"""Reference probes and optional live-model check generation; keep their results separate."""
import json
import os
from pathlib import Path
import urllib.request

from alignment.agent import obj, arr, validate_shape
from viability.warehouse import fingerprint


def clauses(version):
    result = {
        'G1': 'At the order grain, amounts are expressed in AUD. Raw payment amounts are integer Australian cents; 100 cents equals AUD 1. Every payment contribution is counted once.',
        'G2': 'Include credit card, bank transfer, gift card and coupon payments across all order statuses. Aggregate by order date, without inferring settlement or cash collection.',
        'G3': 'Every raw payment needs a non-null amount, a unique payment ID and a valid order link. Missing amounts must not be treated as zero.',
        'G4': 'Order 2 has an agreed gross payment ceiling of AUD 20.00. Actual recorded payments exceeding it violate this limit even when their sum is calculated correctly.',
        'G5': 'Reporting scope is orders dated from 2018-01-01 through 2018-04-30 inclusive.'}
    if version == 2:
        result['G2'] += ' Amendment: exclude coupon payments for orders dated on or after 2018-02-01. Earlier orders retain their original treatment. Only this inclusion rule changes.'
    return result


def schema():
    string = {'type': 'string'}
    return obj({'snapshot_id': string,
                'checks': arr(obj({'id': string, 'requirement_id': string, 'source_quote': string,
                                   'node_ids': arr(string), 'rationale': string, 'sql': string,
                                   'failure_kind': {'type': 'string', 'enum': ['DEFINITION_MISMATCH', 'DATA_VIOLATION', 'MISSING_EVIDENCE']}})),
                'coverage': arr(obj({'requirement_id': string,
                                     'status': {'type': 'string', 'enum': ['CHECKED', 'UNVERIFIABLE']},
                                     'check_ids': arr(string), 'rationale': string})),
                'limitations': arr(string)})


def validate_plan(packet, plan):
    if packet['snapshot_id'] != fingerprint({k: v for k, v in packet.items() if k != 'snapshot_id'}):
        raise ValueError('Tampered packet')
    validate_shape(plan, schema())
    if plan['snapshot_id'] != packet['snapshot_id']:
        raise ValueError('Plan belongs to another snapshot')
    if len(plan['checks']) > 12:
        raise ValueError('Check budget exceeded')
    by_id = {c['id']: c for c in plan['checks']}
    if len(by_id) != len(plan['checks']):
        raise ValueError('Duplicate checks')
    nodes = {n['id'] for n in packet['nodes']}
    for check in plan['checks']:
        source = packet['governing_clauses'].get(check['requirement_id'])
        if not source or check['source_quote'] not in source or not check['node_ids'] or not set(check['node_ids']) <= nodes:
            raise ValueError('Ungrounded check')
    coverage_ids = [c['requirement_id'] for c in plan['coverage']]
    if len(set(coverage_ids)) != len(coverage_ids) or set(coverage_ids) != set(packet['governing_clauses']):
        raise ValueError('Every requirement needs one disposition')
    referenced = set()
    for entry in plan['coverage']:
        if not set(entry['check_ids']) <= set(by_id):
            raise ValueError('Unknown check reference')
        if entry['status'] == 'CHECKED' and not entry['check_ids']:
            raise ValueError('A checked requirement needs a query')
        referenced.update(entry['check_ids'])
    if referenced != set(by_id):
        raise ValueError('Orphaned check')


def execute(packet, plan, warehouse):
    validate_plan(packet, plan)
    receipts = []
    for check in plan['checks']:
        receipts.append({**check, 'result': warehouse.query(check['sql'])})
    issues = sorted({c['failure_kind'] for c in receipts if c['result']['has_counterexamples']})
    if any(x['status'] == 'UNVERIFIABLE' for x in plan['coverage']):
        issues.append('UNVERIFIABLE')
    priority = ['MISSING_EVIDENCE', 'UNVERIFIABLE', 'DATA_VIOLATION', 'DEFINITION_MISMATCH']
    return {'status': next((x for x in priority if x in issues), 'NO_ISSUE_DETECTED'),
            'issues': issues, 'receipts': receipts}


def reference_plan(packet, version):
    """Explicitly authored comparator. NOT the agent and NOT semantic discovery."""
    included = "case when o.order_date >= DATE '2018-02-01' and p.payment_method = 'coupon' then 0 else p.amount end" if version == 2 else 'p.amount'
    checks = []

    def add(ident, requirement, failure, sql):
        checks.append({'id': ident, 'requirement_id': requirement,
                       'source_quote': packet['governing_clauses'][requirement],
                       'node_ids': [n['id'] for n in packet['nodes']],
                       'rationale': 'Manually authored reference probe for the frozen integration test.',
                       'failure_kind': failure, 'sql': sql})

    add('units', 'G1', 'DEFINITION_MISMATCH', '''select s.payment_id, s.amount observed_aud, r.amount / 100.0 expected_aud
from stg_payments s join raw_payments r on s.payment_id = r.id
where r.amount is not null and (s.amount is null or abs(s.amount - r.amount / 100.0) > 0.000001)''')
    add('definition', 'G2', 'DEFINITION_MISMATCH', f'''with expected as (
select o.id order_id, sum({included}) / 100.0 expected_aud
from raw_orders o left join raw_payments p on p.order_id = o.id
where o.order_date between DATE '2018-01-01' and DATE '2018-04-30' group by o.id)
select e.order_id, e.expected_aud, a.amount observed_aud
from expected e left join orders a on e.order_id = a.order_id
where a.order_id is null or (e.expected_aud is not null and (a.amount is null or abs(a.amount-e.expected_aud) > 0.000001))''')
    add('grain', 'G1', 'DEFINITION_MISMATCH', 'select order_id, count(*) rows_per_order from orders group by order_id having count(*) <> 1')
    add('evidence', 'G3', 'MISSING_EVIDENCE', '''select p.id payment_id, p.order_id, p.amount,
case when p.amount is null then 'missing_amount' when o.id is null then 'missing_order' else 'duplicate_payment_id' end problem
from raw_payments p left join raw_orders o on p.order_id=o.id
where p.amount is null or o.id is null or p.id in (select id from raw_payments group by id having count(*) > 1)''')
    add('ceiling', 'G4', 'DATA_VIOLATION', '''select order_id, sum(amount)/100.0 observed_aud, 20.0 agreed_ceiling_aud,
sum(amount)/100.0 - 20.0 excess_aud from raw_payments where order_id=2 group by order_id having sum(amount)>2000''')
    return {'snapshot_id': packet['snapshot_id'], 'checks': checks,
            'coverage': [{'requirement_id': rid, 'status': 'CHECKED',
                          'check_ids': [c['id'] for c in checks if c['requirement_id'] == rid] if rid != 'G5' else ['definition'],
                          'rationale': 'Reporting cohort is embedded in the definition query.' if rid == 'G5' else 'Explicit reference query.'}
                         for rid in packet['governing_clauses']],
            'limitations': ['Reference probes are manually encoded; passing them does not demonstrate automatic interpretation or query discovery.']}


def live_plan(packet, model):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise ValueError('No OPENAI_API_KEY; autonomous agent gate must remain NOT_RUN')
    body = {'model': model, 'store': False, 'max_output_tokens': 14000,
            'input': [{'role': 'developer', 'content': Path(__file__).with_name('reviewer.md').read_text()},
                      {'role': 'user', 'content': json.dumps(packet)}],
            'text': {'format': {'type': 'json_schema', 'strict': True, 'name': 'warehouse_alignment_plan', 'schema': schema()}}}
    request = urllib.request.Request('https://api.openai.com/v1/responses', data=json.dumps(body).encode(),
                                    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
    with urllib.request.urlopen(request, timeout=120) as result:
        raw = json.load(result)
    if raw.get('status') != 'completed':
        raise ValueError('Incomplete model response')
    output = ''.join(p['text'] for item in raw.get('output', []) if item.get('type') == 'message'
                     for p in item.get('content', []) if p.get('type') == 'output_text')
    if not output:
        raise ValueError('No model plan, possibly a refusal')
    return json.loads(output), {'model': raw.get('model'), 'response_id': raw.get('id'), 'usage': raw.get('usage')}
