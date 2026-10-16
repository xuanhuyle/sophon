"""Local context-event replay using actual dbt lineage and explicit review binding."""
import hashlib
import json
from pathlib import Path

ROOT = Path('viability/runs/public_nyc')
OUT = Path('viability/public_nyc/evidence')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def ancestors(nodes, target):
    seen, pending = set(), [target]
    while pending:
        node = pending.pop()
        if node in seen:
            continue
        if node not in nodes:
            raise ValueError('Unknown dependency: ' + node)
        seen.add(node)
        pending.extend(nodes[node].get('depends_on', {}).get('nodes', []))
    return sorted(seen)


def context(consumer, nodes, requirements):
    dependencies = ancestors(nodes, consumer['target'])
    applicable = [rule for rule in requirements if rule['source_node'] in dependencies]
    body = {'consumer': consumer['id'], 'target': consumer['target'],
            'dependency_code_sha256': fingerprint({n: nodes[n].get('raw_code', '') for n in dependencies}),
            'scope': 'yellow service only', 'governing_context': applicable,
            'alignment_status': 'REVIEW_REQUIRED' if applicable else 'OUTSIDE_REVIEW_SCOPE'}
    return {**body, 'context_id': fingerprint(body)}


def accept_context(cached, current):
    if cached['context_id'] != current['context_id']:
        raise ValueError('STALE_CONTEXT')
    return current['alignment_status']


def main():
    manifest = json.loads((ROOT / 'project/target/manifest.json').read_text())
    nodes = {**manifest['nodes'], **manifest['sources']}
    project = 'nyc_taxi_databricks_dbt'
    source_node = f'source.{project}.staging.yellow_tripdata_raw'
    provenance = json.loads((OUT / 'provenance.json').read_text())
    consumers = [{'id': 'monthly_bi_consumer', 'target': f'model.{project}.dm_monthly_zone_revenue'},
                 {'id': 'trip_review_consumer', 'target': f'model.{project}.fact_trips'},
                 {'id': 'zone_reference_consumer', 'target': f'model.{project}.dim_zones'}]
    initial_rule = {
        'id': 'tlc.record_semantics', 'source_node': source_node,
        'source': provenance['inputs']['yellow_dictionary.pdf'],
        'interpretation': 'Provider identity is not trip identity; recorded totals exclude cash tips.',
        'review_findings': ['Unsupported deduplication key discards distinct records.',
                            'Cash-tip completeness must not be inferred.'],
        'binding_origin': 'conversational_reviewer; not machine-certified authority',
    }
    arrived_rule = {
        'id': 'tlc.cbd_rate', 'source_node': source_node,
        'field': 'cbd_congestion_fee',
        'source': provenance['inputs']['congestion_program.html'],
        'effective_date_source': provenance['inputs']['yellow_dictionary.pdf'],
        'interpretation': 'For eligible yellow-taxi per-trip charges, the stated rate is USD 0.75. The dictionary dates this fee to 2025-01-05. A trip may straddle the start time; pickup date alone cannot determine applicability.',
        'review_findings': ['Bare numeric has zero scale on documented Databricks semantics; fractional fee representation requires review.'],
        'applicability_limits': 'No complete route, enrollment, exemption or correction evidence; no row-level legal clearance.',
        'binding_origin': 'conversational_reviewer; explicitly supplied to propagation mechanism',
    }
    before = {c['id']: context(c, nodes, [initial_rule]) for c in consumers}
    after = {c['id']: context(c, nodes, [initial_rule, arrived_rule]) for c in consumers}
    replay = {c['id']: context(c, nodes, [initial_rule, arrived_rule]) for c in consumers}
    receipts = []
    for c in consumers:
        ident = c['id']
        try:
            accept_context(before[ident], after[ident])
            stale = False
        except ValueError as error:
            if str(error) != 'STALE_CONTEXT':
                raise
            stale = True
        status = accept_context(after[ident], replay[ident])
        receipts.append({'consumer': ident, 'old_context_rejected_as_stale': stale,
                         'replacement_context_current': True, 'alignment_status': status})
    checks = {
        'both_dependent_contexts_invalidated': all(r['old_context_rejected_as_stale'] for r in receipts[:2]),
        'unrelated_context_unchanged': not receipts[2]['old_context_rejected_as_stale'],
        'repeat_event_idempotent': after == replay,
        'fresh_contexts_retain_unresolved_findings': all(r['alignment_status'] == 'REVIEW_REQUIRED' for r in receipts[:2]),
    }
    if not all(checks.values()):
        raise RuntimeError('Context-delivery check failed')
    result = {'mode': 'local_consumer_simulation_with_explicit_semantic_binding',
              'protocol_sha256': hashlib.sha256(Path('viability/public_nyc/CONTEXT_PROTOCOL.md').read_bytes()).hexdigest(),
              'event': arrived_rule, 'before': before, 'after': after,
              'receipts': receipts, 'checks': checks,
              'limits': 'No actual downstream agent, BI integration, unattended watcher or independent semantic extraction test.'}
    (OUT / 'context_event.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'receipts': receipts, 'checks': checks}, indent=2))


if __name__ == '__main__':
    main()
