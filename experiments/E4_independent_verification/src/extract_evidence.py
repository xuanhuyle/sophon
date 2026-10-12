"""Write human-readable evidence from evidence/run: compiled SQL and patch diffs per candidate stack, and one
counterexample file per wrong variant.  python3 src/extract_evidence.py --run evidence/run"""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
run = Path(ap.parse_args().run)
stacks = json.loads((run / "candidate_stacks.json").read_text())
(run / "compiled_sql").mkdir(exist_ok=True)
(run / "diffs").mkdir(exist_ok=True)
for k, st in stacks.items():
    sql = (st.get("exec_year") or {}).get("compiled_sql")
    if sql:
        (run / "compiled_sql" / f"{k}.sql").write_text(sql + "\n", encoding="utf-8")
    d = "".join(x["unified_diff"] for x in st.get("diffs", []))
    if d:
        (run / "diffs" / f"{k.split('__')[0]}.diff").write_text(d, encoding="utf-8")
res = json.loads((run / "variant_results.json").read_text())
ce = {}
for r in res:
    if r["status"] == "NONCONFORMING_IMPLEMENTATION" or r["variant_id"] == "C5":
        ce[r["variant_id"]] = [{"snapshot": s["snapshot"], "status": s["status"], "candidate_by_year": s.get("candidate_by_year"),
                                "reference_by_year": s.get("reference_by_year"), "membership": s.get("membership"),
                                "counterexamples": [{k: v for k, v in c.items() if k != "lineage"} for c in s.get("counterexamples", [])],
                                "lineage": (s.get("counterexamples") or [{}])[0].get("lineage")} for s in r["snapshots"]]
(run / "counterexamples.json").write_text(json.dumps(ce, indent=1) + "\n", encoding="utf-8")
print(sorted(ce), len(list((run / "compiled_sql").iterdir())), "sql files")
