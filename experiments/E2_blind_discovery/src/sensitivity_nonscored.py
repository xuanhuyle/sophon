#!/usr/bin/env python3
"""NON-SCORED sensitivity analysis, written AFTER seeing the solver output (RESULTS.md section 5).
It never replaces the frozen score. One relaxation only: a solver predicate whose text_span contains anchors of
several reference predicates may serve all of them (the frozen scorer assigns it to one)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score  # noqa: E402


def lenient(ref_preds, sol_preds):
    out = {}
    for rid, rp in ref_preds.items():
        c = [(len(str(sp.get("text_span") or "")), i) for i, sp in enumerate(sol_preds)
             if isinstance(sp, dict) and any(a.lower() in str(sp.get("text_span") or "").lower() for a in rp["anchors"])]
        if c:
            out[rid] = min(c)[1]
    return out


score.match_predicates = lenient
E2 = HERE.parent
ref = json.loads((E2 / "REFERENCE.json").read_text())
rep = score.score(ref, (E2 / "evidence/solver/raw_output.json").read_text(), E2 / ".upstream", True, True)
res = {"label": "NON-SCORED sensitivity (merged predicates may serve several reference predicates); primary score unchanged",
       "confusion": rep["confusion"], "gate_under_relaxation": rep["gate"], "errors": {k: v["errors"] for k, v in rep["cases"].items() if v["errors"]}}
(E2 / "evidence/score/sensitivity_nonscored.json").write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({"cases_correct": rep["gate"]["cases_correct"], "verdict": rep["gate"]["verdict"], "errors": res["errors"]}, indent=1))
