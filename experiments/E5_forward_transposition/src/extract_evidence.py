"""Write readable evidence files from a run: the generated patch and diff, compiled SQL per stack/query,
counterexamples per check, P2 before/after and the routing table.

    python3 src/extract_evidence.py --run evidence/run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    run = Path(ap.parse_args().run)
    R = json.loads((run / "results.json").read_text())
    st = json.loads((run / "candidate_stacks.json").read_text())
    (run / "generated").mkdir(exist_ok=True)
    p = R["transposer"]["proposal"]
    (run / "generated" / "proposed_patch.json").write_text(json.dumps(p["patch"], indent=1) + "\n")
    (run / "generated" / "proposed_edit.diff").write_text("".join(d["unified_diff"] for d in R["F3"]["diffs"]))
    (run / "compiled_sql").mkdir(exist_ok=True)
    for k, s in sorted(st.items()):
        sql = (s.get("exec_year") or {}).get("compiled_sql")
        if sql:
            q = s["query"]
            (run / "compiled_sql" / f"{k}.sql").write_text(f"-- stack {k}\n-- query {json.dumps(q)}\n-- semantic manifest {s.get('semantic_manifest_sha256')}\n{sql}\n")
    ces = {cid: {s["snapshot"]: s.get("counterexamples", []) for s in c["snapshots"]} for cid, c in R["checks"].items()}
    ces["N3_P2_COLLATERAL"] = {s: v["counterexamples"] for s, v in R["N3"]["per_snapshot"].items()}
    (run / "counterexamples.json").write_text(json.dumps(ces, indent=1) + "\n")
    (run / "p2_before_after.json").write_text(json.dumps({"F6": R["F6"], "N3": R["N3"]}, indent=1) + "\n")
    (run / "routing.json").write_text(json.dumps(R["F5"], indent=1) + "\n")
    print("ok", len(list((run / "compiled_sql").glob("*.sql"))), "sql files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
