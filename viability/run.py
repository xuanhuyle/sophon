"""Run the warehouse integration gate; optionally run and score a live model separately."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from viability.checks import clauses, execute, reference_plan, live_plan
from viability.warehouse import Warehouse, packet, fingerprint

HERE = Path(__file__).parent
CASES = [
    ('clean', 1, 'NO_ISSUE_DETECTED'),
    ('amendment_unapplied', 2, 'DEFINITION_MISMATCH'),
    ('wrong_units', 1, 'DEFINITION_MISMATCH'),
    ('duplicate_coupon_contribution', 1, 'DEFINITION_MISMATCH'),
    ('payment_over_ceiling', 1, 'DATA_VIOLATION'),
    ('missing_amount', 1, 'MISSING_EVIDENCE'),
    ('amendment_applied', 2, 'NO_ISSUE_DETECTED'),
    ('equivalent_description', 1, 'NO_ISSUE_DETECTED'),
    ('unrelated_downstream_change', 1, 'NO_ISSUE_DETECTED'),
]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + '\n')


def replace(root, name, before, after):
    path = root / name
    content = path.read_text()
    assert before in content
    path.write_text(content.replace(before, after))


def change_amount(root, payment_id, value):
    path = root / 'seeds/raw_payments.csv'
    rows = list(csv.DictReader(io.StringIO(path.read_text())))
    for row in rows:
        if row['id'] == payment_id:
            row['amount'] = value
    with path.open('w') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def setup(name, target):
    shutil.copytree(HERE / 'vendor/jaffle', target)
    (target / 'profiles.yml').write_text('''config:
  send_anonymous_usage_stats: false
jaffle_shop:
  target: local
  outputs:
    local:
      type: duckdb
      path: warehouse.duckdb
      threads: 1
''')
    if name == 'wrong_units':
        replace(target, 'models/staging/stg_payments.sql', 'amount / 100 as amount', 'amount / 1 as amount')
    elif name == 'duplicate_coupon_contribution':
        replace(target, 'models/orders.sql', 'order_payments.total_amount as amount',
                'order_payments.total_amount + order_payments.coupon_amount as amount')
    elif name == 'payment_over_ceiling':
        change_amount(target, '2', '2500')
    elif name == 'missing_amount':
        change_amount(target, '9', '')
    elif name == 'amendment_applied':
        replace(target, 'models/orders.sql', 'order_payments.total_amount as amount',
                "case when orders.order_date >= DATE '2018-02-01' then order_payments.total_amount - order_payments.coupon_amount else order_payments.total_amount end as amount")
    elif name == 'equivalent_description':
        replace(target, 'models/schema.yml', 'Total amount (AUD) of the order', 'Order value expressed in Australian dollars')
    elif name == 'unrelated_downstream_change':
        replace(target, 'models/customers.sql', 'with customers as (', '-- A documentation-only edit to an unrelated downstream model.\nwith customers as (')


def build(root):
    command = [str(Path(sys.executable).with_name('dbt')), 'build', '--profiles-dir', '.', '--full-refresh', '--no-partial-parse']
    result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                            env={**os.environ, 'DBT_SEND_ANONYMOUS_USAGE_STATS': 'false', 'DO_NOT_TRACK': '1'})
    (root / 'build.log').write_text(result.stdout + result.stderr)
    if not (root / 'target/run_results.json').exists():
        raise RuntimeError('No dbt artifacts: ' + str(root / 'build.log'))
    output = json.loads((root / 'target/run_results.json').read_text())
    return {'exit_code': result.returncode, 'invocation_id': output['metadata']['invocation_id'],
            'statuses': {r['unique_id']: r['status'] for r in output['results']},
            'manifest_sha256': hashlib.sha256((root / 'target/manifest.json').read_bytes()).hexdigest()}


def run(model=None):
    if model and not os.environ.get('OPENAI_API_KEY'):
        raise ValueError('No model credential available. Do not claim an autonomous agent run.')
    provenance = json.loads((HERE / 'vendor/PROVENANCE.json').read_text())
    for path, expected in provenance['files'].items():
        assert hashlib.sha256((HERE / 'vendor/jaffle' / path).read_bytes()).hexdigest() == expected, path
    run_id = 'live' if model else 'integration'
    run_root = HERE / 'runs' / run_id
    if run_root.exists():
        raise ValueError(f'{run_root} already exists; archive it or choose a clean checkout to preserve prior evidence')
    run_root.mkdir(parents=True)
    results = []
    for index, (name, version, expected) in enumerate(CASES):
        root = run_root / f'case_{index + 1:02d}'
        setup(name, root)
        receipt = build(root)
        if receipt['exit_code']:
            raise RuntimeError('Unexpected dbt build failure: ' + str(root / 'build.log'))
        current = packet(root, clauses(version))
        warehouse = Warehouse(root / 'warehouse.duckdb')
        plan = reference_plan(current, version)
        observed = execute(current, plan, warehouse)
        metric = warehouse.query("select sum(amount) total_aud from orders where order_date between DATE '2018-01-01' and DATE '2018-04-30'")
        result = {'case': name, 'expected': expected, 'reference_status': observed['status'],
                  'integration_pass': observed['status'] == expected,
                  'snapshot_id': current['snapshot_id'], 'dependency_fingerprint': fingerprint(current['nodes']),
                  'dependency_nodes': [n['id'] for n in current['nodes']],
                  'dbt': receipt, 'metric_query': metric, 'reference_observation': observed,
                  'agent_gate': 'NOT_RUN'}
        if name == 'payment_over_ceiling':
            over = next(r['result'] for r in observed['receipts'] if r['id'] == 'ceiling')
            assert over['rows'][0][-1] == 5.0
        write(root / 'review_packet.json', current)
        write(root / 'reference_plan.json', plan)
        if model:
            # No case names, expected values, reference SQL or challenge instructions enter this call.
            try:
                generated, provider = live_plan(current, model)
                agent_result = execute(current, generated, warehouse)
                if packet(root, clauses(version))['snapshot_id'] != current['snapshot_id']:
                    raise ValueError('Snapshot changed during model review')
                result.update(agent_gate='RAN', agent_pass=agent_result['status'] == expected,
                              agent_observation=agent_result, provider=provider)
                write(root / 'model_plan.json', generated)
            except Exception as error:
                result.update(agent_gate='FAILED', agent_pass=False, agent_error=type(error).__name__ + ': ' + str(error))
        write(root / 'case_result.json', result)
        results.append(result)
        print(f'{name}: dbt build={receipt["exit_code"]}, reference={observed["status"]}, expected={expected}, agent={result["agent_gate"]}', flush=True)
    assert results[0]['dependency_fingerprint'] == results[-1]['dependency_fingerprint'], 'Unrelated dependency change affected target snapshot'
    total = {'protocol_sha256': hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest(),
             'upstream_commit': provenance['commit'], 'integration_passed': sum(r['integration_pass'] for r in results),
             'cases': len(results), 'autonomous_agent_gate': 'RAN' if model else 'NOT_RUN_NO_MODEL_CREDENTIAL',
             'live_platform_gate': 'NOT_RUN: DuckDB only; no Snowflake, Databricks, Omni or Hex integration',
             'overall_claim': 'Bounded integration feasibility only; autonomous semantic viability not confirmed',
             'results': results}
    if model:
        total['agent_cases_passed'] = sum(r.get('agent_pass', False) for r in results)
    write(HERE / 'evidence' / f'{run_id}_results.json', total)
    assert all(r['integration_pass'] for r in results)
    return total


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', help='Explicit model ID; requires OPENAI_API_KEY. Omit for integration-only reference probes.')
    args = parser.parse_args()
    run(args.model)
