#!/usr/bin/env python3
"""Condense stage-1 workflow outputs into digest.md plus one JSON file per cluster."""
import json, sys, os, glob

SP = '/tmp/claude-0/-home-user-sophon/03144a04-0e98-54e7-9d2c-78cb7b16e172'
OUT = f'{SP}/scratchpad/market'
task_files = sys.argv[1:]
clusters = []
for tf in task_files:
    d = json.load(open(tf))
    res = d.get('result') or {}
    for c in res.get('clusters', []):
        clusters.append(c)

os.makedirs(f'{OUT}/clusters', exist_ok=True)
lines = ['# Digest of stage-1 domain sweeps (adversarially verified)', '',
         'Each cluster below has a full JSON file with the finder result and the verifier result. Read those for detail.', '']
for c in clusters:
    key = c['key']; f = c['found']; v = c['verification']
    path = f'{OUT}/clusters/{key}.json'
    json.dump(c, open(path, 'w'), indent=1)
    lines.append(f'## {key}  (full file: {path})')
    lines.append('')
    lines.append(f"**Finder assessment.** {f.get('domain_assessment','')}")
    lines.append('')
    lines.append(f"**Verifier overall.** {v.get('overall','')}")
    lines.append('')
    corrected = {x['name']: x for x in v.get('corrected_workflow_verdicts', [])}
    lines.append('| Workflow | Geography | Finder verdict / quality | Verifier corrected verdict / quality | Volume | Review rate | Why humans review (A to H) | Settlement loop | Existing solutions |')
    lines.append('|---|---|---|---|---|---|---|---|---|')
    for w in f.get('workflows', []):
        cv = corrected.get(w['name'])
        cvs = f"{cv['verdict']} / {cv['evidence_quality']}: {cv['why'][:160]}" if cv else 'no correction'
        loops = '; '.join(f"{s['description'][:90]} [{s['prospective']}]" for s in w.get('settlement_loop_evidence', [])[:3]) or 'none found'
        row = [w['name'], w.get('geography',''), f"{w['verdict']} / {w['evidence_quality']}", cvs, w.get('decision_volume','')[:160], w.get('human_review_rate','')[:120], w.get('why_humans_review','')[:220], loops[:260], w.get('existing_solutions','')[:200]]
        lines.append('| ' + ' | '.join(x.replace('|','/').replace('\n',' ') for x in row) + ' |')
    lines.append('')
    if v.get('refuted'):
        lines.append('**Refuted by verifier:** ' + ' // '.join(f"{r['claim'][:100]} => {r['why'][:140]}" for r in v['refuted'][:5]))
    if v.get('manual_review_conflated_with_repeatable_ambiguity'):
        lines.append('**Manual review conflated with H:** ' + ' // '.join(x[:160] for x in v['manual_review_conflated_with_repeatable_ambiguity'][:4]))
    if f.get('evidence_against_thesis'):
        lines.append('**Evidence against the thesis:** ' + ' // '.join(x[:160] for x in f['evidence_against_thesis'][:5]))
    lines.append('')
open(f'{OUT}/digest.md', 'w').write('\n'.join(lines))
print('clusters:', len(clusters), '| digest chars:', len('\n'.join(lines)))
for c in clusters:
    print(' -', c['key'], '| workflows:', len(c['found'].get('workflows', [])), '| refuted:', len(c['verification'].get('refuted', [])))
