"""Replay checks derived during the interactive review, not a fresh agent run.

The conversational reviewer already knew the fixture scenarios and outcomes.
This demonstrates an inspection workflow; it is not a blinded accuracy test.
No reference_plan or checks.py imports are used.
Run from the repo root after viability.run has built the fixtures:
    python -m viability.interactive_amendment_review
"""
import json
from pathlib import Path

from viability.warehouse import Warehouse, packet


# Establish prerequisites before trusting an aggregate comparison. In particular,
# SQL SUM ignores NULL, and joining duplicate order IDs can inflate payments.
QUALITY = """
select 'missing_payment_amount' as issue, count(*) as affected
from main.raw_payments where amount is null
union all
select 'missing_payment_id', count(*) from main.raw_payments where id is null
union all
select 'duplicate_payment_id', count(*) from
  (select id from main.raw_payments group by id having count(*) > 1)
union all
select 'invalid_order_link', count(*) from main.raw_payments p
where not exists (select 1 from main.raw_orders o where o.id = p.order_id)
union all
select 'invalid_raw_order_key', count(*) from
  (select id from main.raw_orders group by id having id is null or count(*) > 1)
union all
select 'invalid_model_order_key', count(*) from
  (select order_id from main.orders group by order_id
   having order_id is null or count(*) > 1)
union all
select 'missing_raw_order_date', count(*) from main.raw_orders where order_date is null
union all
select 'unrecognized_method', count(*) from main.raw_payments
where payment_method is null or payment_method not in
  ('credit_card', 'bank_transfer', 'gift_card', 'coupon')
"""

# The governing amendment is applied to RAW order date and RAW cents. Reusing
# model.amount to calculate the expected amount would conceal upstream errors.
RECONCILIATION = """
with governed as (
  select o.id as order_id, o.order_date,
    count(p.id) as payment_count,
    sum(case when p.payment_method = 'coupon'
                  and o.order_date >= date '2018-02-01'
             then 0 else p.amount end) as governed_cents,
    sum(p.amount) as original_cents
  from main.raw_orders o
  left join main.raw_payments p on p.order_id = o.id
  where o.order_date between date '2018-01-01' and date '2018-04-30'
  group by o.id, o.order_date
), actual as (
  select order_id, order_date, amount from main.orders
  where order_date between date '2018-01-01' and date '2018-04-30'
)
select coalesce(g.order_id, a.order_id) as order_id,
       g.order_date as governing_order_date, a.order_date as model_order_date,
       g.payment_count,
       cast(a.amount as decimal(18,2)) as reported_aud,
       cast(g.original_cents / 100.0 as decimal(18,2)) as original_aud,
       cast(g.governed_cents / 100.0 as decimal(18,2)) as amended_aud,
       cast(a.amount - g.governed_cents / 100.0 as decimal(18,2)) as difference_aud,
       case when g.order_id is null or a.order_id is null then 'missing_order'
            when g.payment_count = 0 then 'no_payment_evidence'
            when g.order_date is distinct from a.order_date then 'date_mismatch'
            when a.amount is null then 'missing_model_amount'
            when abs(a.amount - g.governed_cents / 100.0) > 0.000001
                 then 'amount_mismatch' else 'aligned' end as disposition
from governed g full outer join actual a on g.order_id = a.order_id
"""


def main():
    project = Path('viability/runs/integration/case_02')
    supplied = json.loads((project / 'review_packet.json').read_text())
    before = packet(project, supplied['governing_clauses'])
    if before['snapshot_id'] != supplied['snapshot_id']:
        raise RuntimeError('Fixture changed since the supplied review packet')
    warehouse = Warehouse(project / 'warehouse.duckdb')
    quality = warehouse.query(QUALITY)
    if any(row[1] for row in quality['rows']):
        raise RuntimeError('Data prerequisites failed; do not clear the aggregate')
    detail = warehouse.query('select * from (' + RECONCILIATION +
                             ") r where disposition <> 'aligned' order by order_id")
    summary = warehouse.query("""select
        case when governing_order_date < date '2018-02-01'
             then 'before_amendment' else 'on_or_after_amendment' end as period,
        count(*) as orders,
        sum(case when disposition <> 'aligned' then 1 else 0 end) as discrepancies,
        sum(reported_aud) as reported_aud, sum(original_aud) as original_aud,
        sum(amended_aud) as amended_aud, sum(difference_aud) as difference_aud
        from (""" + RECONCILIATION + ') r group by 1 order by 1')
    # Aggregate result rows are not themselves counterexamples.
    for receipt in (quality, summary):
        receipt['has_rows'] = receipt.pop('has_counterexamples')
    after = packet(project, supplied['governing_clauses'])
    if before['snapshot_id'] != after['snapshot_id']:
        raise RuntimeError('Inputs changed during review')
    result = {
        'review_mode': 'interactive_conversational_review_of_known_fixture',
        'independent_accuracy_test': False,
        'scope': 'G2 amendment, G1 units/order grain, G3 prerequisites, G5 cohort; G4 ceiling not assessed',
        'governing_clauses': supplied['governing_clauses'],
        'snapshot_id': before['snapshot_id'],
        'derivation': 'The model sums payments before joining order dates, so it has no date-dependent coupon exclusion. Compare its output to raw cents aggregated under G2.',
        'prerequisites': quality, 'discrepancies': detail, 'period_totals': summary,
        'limitations': [
            'Known synthetic agreement and fixtures; previous outcomes visible to reviewer.',
            'This script replays SQL derived in conversation; it does not invoke a model.',
            'No independent accuracy score, production integration, automatic update, or propagation demonstrated.',
        ],
    }
    output = Path('viability/evidence/interactive_amendment_review.json')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
