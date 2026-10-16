#!/usr/bin/env python3
"""Run a batch of publicodes evaluations against one OR SEVERAL rules directories (multi-package trees
such as modele-ti + modele-commun) and print a compact table.
usage: python3 -I work/scripts/evalbatch2.py <cases.json> <out.jsonl> --rules DIR [--rules DIR2 ...] [--only-ids a,b]
cases.json: [{"id": "...", "situation": {...}, "rules": ["rule a", ...], "rules_before": [...], "rules_after": [...]}, ...]
  "rules" are evaluated always; add --side before|after to also evaluate "rules_before"/"rules_after" (tree-specific names).
Output: one JSON line per case appended to out.jsonl (same shape as evalbatch.py, readable by grid_evals.py /
summarize_evals.py): {id, situation, rules, rc, stdout, stderr}.
"""
import json, subprocess, sys, os
args = sys.argv[1:]
cases_path, out = args[0], args[1]
rules_dirs, side, only = [], None, None
i = 2
while i < len(args):
    if args[i] == '--rules': rules_dirs.append(args[i + 1]); i += 2
    elif args[i] == '--side': side = args[i + 1]; i += 2
    elif args[i] == '--only-ids': only = set(args[i + 1].split(',')); i += 2
    else: raise SystemExit(f'unknown arg {args[i]}')
assert rules_dirs, '--rules DIR required'
cases = json.load(open(cases_path))
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open(out, 'a') as fo:
    for c in cases:
        if only and c['id'] not in only: continue
        rules = list(c['rules']) + (list(c.get(f'rules_{side}', [])) if side else [])
        cmd = ['node', os.path.join(root, 'src/publicodes_eval.mjs'), 'evaluate']
        for d in rules_dirs: cmd += ['--rules', d]
        cmd += ['--situation', json.dumps(c['situation'], ensure_ascii=False)]
        for r in rules: cmd += ['--rule', r]
        p = subprocess.run(cmd, capture_output=True, text=True)
        rec = {'id': c['id'], 'situation': c['situation'], 'rules': rules, 'rc': p.returncode,
               'stdout': p.stdout, 'stderr': p.stderr[-2000:]}
        fo.write(json.dumps(rec, ensure_ascii=False) + '\n')
        print(f"### {c['id']}  date={c['situation'].get('date')}  rc={p.returncode}")
        try:
            ev = json.loads(p.stdout)['evaluations']
            se = json.loads(p.stdout).get('situation_error')
            if se: print('   SITUATION_ERROR (whole situation ignored by the engine):', se[:300])
            for k, v in ev.items():
                if 'error' in v: print(f'   {k} => ERR {v["error"][:120]}'); continue
                nv = v.get('nodeValue'); nv = round(nv, 4) if isinstance(nv, float) else nv
                miss = v.get('missing_variables') or []
                print(f"   {k} => {nv} {v.get('unit') or ''}" + (f"  MISSING {miss[:4]}" if miss else ''))
        except Exception:
            print('   RAW:', p.stdout[:800]); print('   ERR:', p.stderr[-600:])
