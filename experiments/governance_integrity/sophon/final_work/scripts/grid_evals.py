#!/usr/bin/env python3
"""Compact grid of engine values: python3 -I work/scripts/grid_evals.py before.jsonl after.jsonl
One line per case: rule-suffix => before | after (only nodeValue/unit; errors shown as ERR)."""
import json, sys
def load(p):
    d = {}
    for ln in open(p):
        r = json.loads(ln)
        try: ev = json.loads(r['stdout'])['evaluations']
        except Exception: ev = {'__error__': r.get('stderr', '')[-200:]}
        d[r['id']] = ev
    return d
def val(e):
    if e is None: return '-'
    if 'error' in e: return 'ERR'
    v = e.get('nodeValue'); u = e.get('unit') or ''
    if isinstance(v, float): v = round(v, 4)
    return f"{v}{(' ' + u) if u else ''}"
B = load(sys.argv[1]); A = load(sys.argv[2]) if len(sys.argv) > 2 else {}
for cid in B:
    rules = list(B[cid].keys())
    parts = []
    for r in rules:
        short = r.replace('dirigeant . auto-entrepreneur . cotisations et contributions . cotisations', 'COT').replace('dirigeant . auto-entrepreneur . DROM', 'DROM')
        b = val(B[cid].get(r)); a = val(A.get(cid, {}).get(r)) if A else None
        parts.append(f"{short}={b}" + (f"|{a}" if A else '') + ("  <<CHANGED" if A and a != b else ''))
    print(f"## {cid}"); [print('   ', p) for p in parts]
