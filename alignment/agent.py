"""Prepare, review and validate bounded alignment evidence. Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PROMPT = Path(__file__).with_name('reviewer.md')
KINDS = ['CONTRADICTION', 'MISSING_REQUIREMENT', 'UNSUPPORTED_ASSUMPTION',
         'AMBIGUITY', 'VERSION_UNCERTAINTY', 'UNVERIFIABLE']


def hashed(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def local_path(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Input path must stay within the selected root')
    return path


def prepare(root, manifest_path):
    root = Path(root).resolve()
    manifest = read(manifest_path)
    if not manifest.get('scope') or not manifest.get('documents'):
        raise ValueError('Explicit scope and documents are required')
    documents, segments, ids = [], [], set()
    for spec in manifest['documents']:
        doc_id = spec['id']
        if doc_id in ids or spec['role'] not in ('governing', 'operational'):
            raise ValueError('Unique IDs and explicit document roles required')
        ids.add(doc_id)
        if spec['role'] == 'governing' and spec.get('authority_status') not in ('draft', 'adopted', 'unknown'):
            raise ValueError('Governing document authority must be supplied explicitly')
        raw = local_path(root, spec['path']).read_bytes()
        text = raw.decode('utf-8')
        doc = {**spec, 'sha256': hashlib.sha256(raw).hexdigest()}
        documents.append(doc)
        if spec.get('format', 'text') == 'dbt_manifest':
            nodes = json.loads(text).get('nodes', {})
            selection = spec.get('node_ids')
            if not selection:
                raise ValueError('dbt manifest requires an explicit node_ids selection')
            for node_id in selection:
                node = nodes[node_id]
                payload = {k: node.get(k) for k in ('unique_id', 'resource_type', 'description',
                           'columns', 'meta', 'config', 'depends_on', 'raw_code', 'compiled_code')}
                segments.append({'id': f'{doc_id}:{node_id}', 'document_id': doc_id,
                                 'location': node_id, 'role': spec['role'],
                                 'text': json.dumps(payload, indent=2, ensure_ascii=False)})
        elif spec.get('format', 'text') == 'text':
            for line, body in enumerate(text.splitlines(), 1):
                if body.strip():
                    segments.append({'id': f'{doc_id}:L{line}', 'document_id': doc_id,
                                     'location': f'line {line}', 'role': spec['role'], 'text': body})
        else:
            raise ValueError('Supported inputs: UTF-8 text and selected dbt manifest nodes')
    if {d['role'] for d in documents} != {'governing', 'operational'}:
        raise ValueError('Need both governing and operational inputs')
    if len({s['id'] for s in segments}) != len(segments):
        raise ValueError('Duplicate segment IDs')
    if not segments or len(json.dumps(segments)) > 120_000:
        raise ValueError('Empty or oversized scope; split explicitly, never silently truncate')
    packet = {'schema_version': 1, 'scope': manifest['scope'], 'as_of': manifest.get('as_of'),
              'source_completeness': manifest.get('source_completeness', 'unknown'),
              'documents': documents, 'segments': segments,
              'reviewer_prompt_sha256': hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
              'response_schema_sha256': hashed(response_schema())}
    packet['packet_id'] = hashed(packet)
    return packet


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def arr(items):
    return {'type': 'array', 'items': items}


def response_schema():
    string = {'type': 'string'}
    citation = obj({'segment_id': string, 'quote': string})
    return obj({
        'packet_id': string,
        'findings': arr(obj({'id': string, 'kind': {'type': 'string', 'enum': KINDS},
                             'severity': {'type': 'string', 'enum': ['high', 'medium', 'low']},
                             'title': string, 'explanation': string, 'consequence': string,
                             'suggested_action': string, 'governing_evidence': arr(citation),
                             'operational_evidence': arr(citation)})),
        'coverage': arr(obj({'segment_id': string,
                            'disposition': {'type': 'string', 'enum': ['ASSESSED', 'NON_SUBSTANTIVE', 'UNVERIFIABLE']},
                            'rationale': string, 'finding_ids': arr(string)})),
        'limitations': arr(string),
    })


def validate_shape(value, schema, location='response'):
    kind = schema['type']
    if kind == 'object':
        if not isinstance(value, dict) or set(value) != set(schema['required']):
            raise ValueError(f'{location}: unexpected or missing fields')
        for key, item in value.items():
            validate_shape(item, schema['properties'][key], location + '.' + key)
    elif kind == 'array':
        if not isinstance(value, list):
            raise ValueError(f'{location}: expected list')
        for item in value:
            validate_shape(item, schema['items'], location)
    elif not isinstance(value, str) or not value.strip():
        raise ValueError(f'{location}: expected non-empty string')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{location}: invalid enum')


def validate(packet, response):
    original_id = packet['packet_id']
    if original_id != hashed({k: v for k, v in packet.items() if k != 'packet_id'}):
        raise ValueError('Packet integrity mismatch')
    validate_shape(response, response_schema())
    if response['packet_id'] != original_id:
        raise ValueError('Review belongs to a different snapshot')
    segments = {s['id']: s for s in packet['segments']}
    findings = {f['id']: f for f in response['findings']}
    if len(findings) != len(response['findings']):
        raise ValueError('Duplicate finding IDs')
    covered = [c['segment_id'] for c in response['coverage']]
    if len(covered) != len(set(covered)) or set(covered) != set(segments):
        raise ValueError('Every supplied segment needs exactly one disposition')
    for finding in findings.values():
        gov, op = finding['governing_evidence'], finding['operational_evidence']
        if finding['kind'] in ('CONTRADICTION', 'AMBIGUITY') and (not gov or not op):
            raise ValueError('Contradiction/ambiguity requires evidence from both sides')
        if finding['kind'] == 'MISSING_REQUIREMENT' and not gov:
            raise ValueError('Missing requirement needs its governing source')
        if finding['kind'] == 'UNSUPPORTED_ASSUMPTION' and not op:
            raise ValueError('Unsupported assumption needs its operational source')
        if not gov and not op:
            raise ValueError('Every finding needs evidence')
        for role, refs in (('governing', gov), ('operational', op)):
            for citation in refs:
                segment = segments.get(citation['segment_id'])
                if not segment or segment['role'] != role or citation['quote'] not in segment['text']:
                    raise ValueError('Invalid quotation, segment or evidence role')
    mentioned = set()
    for entry in response['coverage']:
        if not set(entry['finding_ids']) <= set(findings):
            raise ValueError('Coverage refers to an unknown finding')
        mentioned.update(entry['finding_ids'])
    if mentioned != set(findings):
        raise ValueError('Every finding must appear in the coverage account')
    return True


def live_review(packet, model):
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        raise ValueError('OPENAI_API_KEY is not configured; no live model call was made')
    body = {'model': model, 'store': False, 'max_output_tokens': 16000,
            'input': [{'role': 'developer', 'content': PROMPT.read_text()},
                      {'role': 'user', 'content': json.dumps(packet, ensure_ascii=False)}],
            'text': {'format': {'type': 'json_schema', 'name': 'alignment_review',
                                'strict': True, 'schema': response_schema()}}}
    request = urllib.request.Request('https://api.openai.com/v1/responses',
               data=json.dumps(body).encode(), headers={'Content-Type': 'application/json',
                                                        'Authorization': 'Bearer ' + key})
    with urllib.request.urlopen(request, timeout=120) as result:
        raw = json.load(result)
    if raw.get('status') != 'completed':
        raise ValueError('Model response incomplete; cannot publish a review')
    chunks = [part['text'] for item in raw.get('output', []) if item.get('type') == 'message'
              for part in item.get('content', []) if part.get('type') == 'output_text']
    if not chunks:
        raise ValueError('Model refused or returned no structured review')
    return json.loads(''.join(chunks)), {'mode': 'live_api', 'model': raw.get('model', model),
                                        'response_id': raw.get('id'), 'usage': raw.get('usage')}


def report(packet, response, provenance):
    validate(packet, response)
    status = 'REVIEW_REQUIRED' if response['findings'] else 'NO_ISSUES_DETECTED_IN_SUPPLIED_SCOPE'
    if any(c['disposition'] == 'UNVERIFIABLE' for c in response['coverage']):
        status = 'REVIEW_INCOMPLETE'
    return {'status': status,
            'authority': 'DRAFT_OR_UNVERIFIED_REFERENCE' if any(
                d.get('authority_status') != 'adopted' for d in packet['documents'] if d['role'] == 'governing'
            ) else 'CALLER_DECLARED_ADOPTED_NOT_AUTHENTICATED',
            'provenance': provenance, 'packet': packet, 'review': response,
            'validation': 'Evidence locations, quotations, shape and segment accounting checked; semantic correctness not certified'}


def freshness(root, manifest_path, previous):
    validate(previous['packet'], previous['review'])
    current = prepare(root, manifest_path)
    old = previous['packet']
    before = {d['id']: d for d in old['documents']}
    after = {d['id']: d for d in current['documents']}
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    return {'status': 'CURRENT' if current['packet_id'] == old['packet_id'] else 'STALE_REVIEW',
            'changed_documents': changed, 'needs_semantic_review': current['packet_id'] != old['packet_id']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'review', 'import-review', 'check'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'alignment/examples/lab_manifest.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--response', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--model')
    args = parser.parse_args()
    if args.action == 'check':
        if not args.report:
            parser.error('--report required')
        value = freshness(args.root, args.manifest, read(args.report))
    else:
        packet = prepare(args.root, args.manifest)
        if args.action == 'prepare':
            value = packet
        elif args.action == 'review':
            if not args.model:
                parser.error('--model required; choose a model available to your account')
            response, provenance = live_review(packet, args.model)
            value = report(packet, response, provenance)
        else:
            if not args.packet or not args.response:
                parser.error('--packet and --response required')
            saved = read(args.packet)
            if saved['packet_id'] != packet['packet_id']:
                raise ValueError('Inputs changed after packet preparation; review must be refreshed')
            value = report(packet, read(args.response), {'mode': 'imported_review', 'model': 'not_attested'})
    # Re-check after model latency, before publishing results.
    if args.action in ('review', 'import-review') and prepare(args.root, args.manifest)['packet_id'] != packet['packet_id']:
        raise ValueError('Inputs changed during review; result not published')
    if args.output:
        if args.output.resolve() in {local_path(args.root, d['path']) for d in read(args.manifest)['documents']} or args.output.resolve() == args.manifest.resolve():
            raise ValueError('Output must not overwrite a source or manifest')
        write(args.output, value)
    else:
        print(json.dumps(value, indent=2))
    return 2 if value.get('status') == 'STALE_REVIEW' else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(f'Review not published: {exc}', file=sys.stderr)
        sys.exit(1)
