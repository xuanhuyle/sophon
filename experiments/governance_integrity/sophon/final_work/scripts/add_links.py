#!/usr/bin/env python3
"""Record every link of a spec file in the sophon store. usage: add_links.py <spec.json> <law_snap> <rules_snap> <results.jsonl>"""
import json, subprocess, sys
spec, law, rules, out = sys.argv[1:5]
L = json.load(open(spec))
with open(out, "a") as fo:
    for l in L:
        cmd = ["python3", "src/sophon.py", "--store", "work/sophon/store", "link", "add", "--rule", l["rule"], "--rules-snapshot", rules,
               "--article", l["article"], "--law-snapshot", l.get("law", law), "--quote", l["quote"], "--claim", l["claim"]]
        if l.get("check"):
            c = l["check"]; cmd += ["--check-rule", c["rule"], "--check-situation", json.dumps(c["situation"], ensure_ascii=False), "--expect", str(c["expect"]), "--tolerance", str(c.get("tolerance", 1e-9))]
        else:
            cmd += ["--status", l["status"]]
        if l.get("note"): cmd += ["--note", l["note"]]
        p = subprocess.run(cmd, capture_output=True, text=True)
        try: j = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception: j = {"ok": False, "raw": p.stdout[-500:], "err": p.stderr[-500:]}
        j["spec_id"] = l["id"]
        fo.write(json.dumps(j, ensure_ascii=False) + "\n")
        cr = j.get("check_result") or {}
        print(f"{l['id']:<42} ok={j.get('ok')} status={j.get('status')} observed={cr.get('observed')} expected={cr.get('expected')} {('PROBLEMS: '+str(j.get('problems'))) if j.get('problems') else ''} {j.get('err','')[:200]}")
