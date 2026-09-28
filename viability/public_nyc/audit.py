"""Replay the checks derived by the conversational reviewer from public sources.

This is an evidence recorder, not an autonomous model invocation. All queries
are SELECT-only against the locally reproduced warehouse. No injected faults.
"""
import hashlib
import json
from pathlib import Path
import time

import duckdb

ROOT = Path('viability/runs/public_nyc')
OUT = Path('viability/public_nyc/evidence')

QUERIES = {
    'source_scope': """
        select count(*) as raw_records,
               count(*) filter(where VendorID is null) as missing_vendor,
               count(*) filter(where tpep_pickup_datetime >= timestamp '2025-01-01'
                 and tpep_pickup_datetime < timestamp '2025-02-01') as january_pickups,
               min(tpep_pickup_datetime) as earliest_pickup,
               max(tpep_pickup_datetime) as latest_pickup
        from bronze.yellow_tripdata_raw""",
    'key_collision_summary': """
        with buckets as (
          select VendorID, tpep_pickup_datetime, count(*) as records,
            count(distinct struct_pack(dropoff := tpep_dropoff_datetime,
                pickup_zone := PULocationID, dropoff_zone := DOLocationID,
                distance := trip_distance, fare := fare_amount,
                total := total_amount, method := payment_type)) as content_variants
          from bronze.yellow_tripdata_raw where VendorID is not null group by 1,2
        )
        select sum(records) as eligible_records, count(*) as surviving_keys,
               sum(records-1) as records_discarded,
               count(*) filter(where records>1) as colliding_keys,
               count(*) filter(where content_variants>1) as keys_with_different_trip_content,
               sum(content_variants-1) as distinct_content_variants_discarded_at_least,
               max(records) as max_records_per_key
        from buckets""",
    'exact_duplicate_summary': """
        select (select count(*) from bronze.yellow_tripdata_raw) as raw_records,
               count(*) as byte_value_distinct_rows
        from (select distinct * from bronze.yellow_tripdata_raw)""",
    'collision_examples': """
        with collision as (
          select VendorID, tpep_pickup_datetime, count(*) as n
          from bronze.yellow_tripdata_raw
          where VendorID is not null
            and tpep_pickup_datetime >= timestamp '2025-01-05'
            and tpep_pickup_datetime < timestamp '2025-02-01'
          group by 1,2 having count(*) > 1
          order by n desc, VendorID, tpep_pickup_datetime limit 1
        )
        select t.VendorID, t.tpep_pickup_datetime, t.tpep_dropoff_datetime,
               t.PULocationID, t.DOLocationID, t.trip_distance, t.fare_amount,
               t.total_amount, t.payment_type, t.cbd_congestion_fee
        from bronze.yellow_tripdata_raw t join collision c using(VendorID,tpep_pickup_datetime)
        order by tpep_dropoff_datetime, PULocationID, DOLocationID, total_amount limit 10""",
    'cbd_fee_distribution': """
        select case when tpep_pickup_datetime < timestamp '2025-01-05'
                    then 'before_start' else 'on_or_after_start' end as period,
               cbd_congestion_fee, count(*) as records
        from bronze.yellow_tripdata_raw
        where tpep_pickup_datetime >= timestamp '2025-01-01'
          and tpep_pickup_datetime < timestamp '2025-02-01'
        group by 1,2 order by 1,2""",
    # Adaptive follow-up: initial distribution showed charges on pre-start
    # pickups. Inspect drop-off timing before alleging early fee application.
    'pre_start_charge_followup': """
        select count(*) as charged_pre_start_pickups,
               count(*) filter(where tpep_dropoff_datetime >= timestamp '2025-01-05')
                 as dropoffs_on_or_after_start,
               count(*) filter(where tpep_dropoff_datetime < timestamp '2025-01-05')
                 as dropoffs_before_start,
               min(tpep_pickup_datetime) as earliest_pickup,
               max(tpep_dropoff_datetime) as latest_dropoff
        from bronze.yellow_tripdata_raw
        where tpep_pickup_datetime >= timestamp '2025-01-01'
          and tpep_pickup_datetime < timestamp '2025-01-05'
          and cbd_congestion_fee > 0""",
    'numeric_default_contrast': """
        select typeof(cast(0.75 as numeric)) as local_numeric_type,
               cast(0.75 as numeric) as local_result,
               typeof(cast(0.75 as decimal(10,0))) as documented_target_type,
               cast(0.75 as decimal(10,0)) as simulated_target_result""",
    'raw_cbd_precision_exposure': """
        select cbd_congestion_fee, count(*) as records,
               cast(cbd_congestion_fee as decimal(10,0)) as target_type_simulation,
               sum(cast(cbd_congestion_fee as decimal(18,2))) as raw_sum,
               sum(cast(cbd_congestion_fee as decimal(10,0))) as simulated_sum
        from bronze.yellow_tripdata_raw
        group by 1,3 order by 1""",
    'local_model_cardinality': """
        select 'yellow_staging' as relation, count(*) as records from silver.stg_yellow_tripdata
        union all select 'yellow_fact', count(*) from silver.fact_trips where service_type='Yellow'
        union all select 'yellow_mart_represented_trips', sum(total_monthly_trips)
          from gold.dm_monthly_zone_revenue where service_type='Yellow'""",
    'local_fact_cbd_precision_exposure': """
        select cbd_congestion_fee, count(*) as records,
               sum(cbd_congestion_fee) as local_fact_sum,
               sum(cast(cbd_congestion_fee as decimal(10,0))) as simulated_target_sum
        from silver.fact_trips where service_type='Yellow'
        group by 1 order by 1""",
    'cash_tip_observability': """
        select payment_type, count(*) as records,
               count(*) filter(where tip_amount is null) as missing_tip_values,
               sum(cast(tip_amount as decimal(18,2))) as recorded_tip_total
        from bronze.yellow_tripdata_raw group by 1 order by 1""",
    'mart_cbd_reconciliation': """
        select (select sum(cbd_congestion_fee) from silver.fact_trips
                where service_type='Yellow') as fact_cbd,
               (select sum(revenue_monthly_cbd_congestion_fee) from gold.dm_monthly_zone_revenue
                where service_type='Yellow') as mart_cbd,
               (select sum(total_amount) from silver.fact_trips
                where service_type='Yellow') as fact_recorded_charges,
               (select sum(revenue_monthly_total_amount) from gold.dm_monthly_zone_revenue
                where service_type='Yellow') as mart_recorded_charges""",
}


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    project = ROOT / 'project'
    manifest = json.loads((project / 'target/manifest.json').read_text())
    nodes = {ident: {'name': n['name'], 'resource_type': n['resource_type'],
                    'depends_on': n.get('depends_on', {}).get('nodes', []),
                    'original_file_path': n['original_file_path'],
                    'relation_name': n.get('relation_name')}
             for ident, n in manifest['nodes'].items()
             if n['resource_type'] in ('model', 'seed')}
    runs = json.loads((project / 'target/run_results.json').read_text())
    result = {'mode': 'interactive_agent_review_replay', 'engine': 'DuckDB ' + duckdb.__version__,
              'live_databricks': False, 'queries': {}, 'lineage': nodes,
              'dbt_results': [{k: r.get(k) for k in ('unique_id', 'status', 'failures', 'message')}
                              for r in runs['results']]}
    with duckdb.connect(str(ROOT / 'prod.duckdb'), read_only=True,
                        config={'enable_external_access': False, 'memory_limit': '512MB', 'threads': 2}) as con:
        for name, sql in QUERIES.items():
            parsed = con.extract_statements(sql)
            if len(parsed) != 1 or parsed[0].type != duckdb.StatementType.SELECT:
                raise ValueError('Only a single SELECT is allowed')
            started = time.monotonic()
            cursor = con.execute(sql)
            rows = cursor.fetchall()
            columns = [c[0] for c in cursor.description]
            serialized = json.dumps([columns, rows], default=str, sort_keys=True)
            result['queries'][name] = {'sql': sql, 'columns': columns,
                'rows': json.loads(json.dumps(rows, default=str)),
                'seconds': round(time.monotonic()-started, 3),
                'result_sha256': hashlib.sha256(serialized.encode()).hexdigest()}
            (OUT / 'audit_results.json').write_text(json.dumps(result, indent=2) + '\n')
            print(name, json.dumps(rows, default=str), flush=True)


if __name__ == '__main__':
    main()
