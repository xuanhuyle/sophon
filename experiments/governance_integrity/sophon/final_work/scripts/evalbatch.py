#!/usr/bin/env python3
"""Run a batch of publicodes evaluations and print a compact table.
usage: python3 work/scripts/evalbatch.py <cases.json> <rules_dir> <out.jsonl>
cases.json: [{"id": "...", "situation": {...}, "rules": ["rule a", "rule b"]}, ...]
"""
import json, subprocess, sys, os
cases = json.load(open(sys.argv[1])); rules_dir = sys.argv[2]; out = sys.argv[3]
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open(out, "a") as fo:
    for c in cases:
        cmd = ["node", os.path.join(root, "src/publicodes_eval.mjs"), "evaluate", "--rules", rules_dir,
               "--situation", json.dumps(c["situation"], ensure_ascii=False)]
        for r in c["rules"]: cmd += ["--rule", r]
        p = subprocess.run(cmd, capture_output=True, text=True)
        rec = {"id": c["id"], "situation": c["situation"], "rules": c["rules"], "rc": p.returncode,
               "stdout": p.stdout, "stderr": p.stderr[-2000:]}
        fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"### {c['id']}  date={c['situation'].get('date')}  rc={p.returncode}")
        try:
            j = json.loads(p.stdout)
            res = j.get("results") or j.get("evaluations") or j
            if isinstance(res, dict):
                for k, v in res.items():
                    if k in ("command", "rules_dirs", "situation", "date", "raw_rule_count", "parsed_rule_count"): continue
                    print(f"   {k} => {json.dumps(v, ensure_ascii=False)[:300]}")
            elif isinstance(res, list):
                for v in res: print(f"   {json.dumps(v, ensure_ascii=False)[:300]}")
        except Exception as e:
            print("   RAW:", p.stdout[:1500]); print("   ERR:", p.stderr[-800:])
