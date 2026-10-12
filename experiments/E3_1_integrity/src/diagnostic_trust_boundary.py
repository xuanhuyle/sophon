"""NON-SCORED diagnostic (PROTOCOL.md §2): an adversary who controls the verifier code defeats the check.
Here a FreshVerifier whose native() and reference() are replaced (as a compromised verifier would) returns the
forged store-reading values, and V5's forged pair is then promoted. No MetricFlow is run.

    .upstream/.venv/bin/python src/diagnostic_trust_boundary.py --out evidence/diagnostics_nonscored.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cand  # noqa: E402
import e31  # noqa: E402
from fresh_verifier import FreshVerifier  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = cand.load(e31.E31 / "cases" / "TRUSTED_MANIFEST.json")
    case = next(c for c in cand.load(e31.E31 / "cases" / "CASES.json")["cases"] if c["case_id"] == "V5_FORGED_PAIR_STORE_READING")
    store = m["expected_reference_values"]["S2/R_STORE_COUNTRY"]
    fv = FreshVerifier.__new__(FreshVerifier)  # compromised verifier: no rebuild, canned answers
    fv.build = {"ok": True}
    fv.native = lambda q, e, r: {"ok": True, "by_period": store, "exit_code": 0, "error": None}
    fv.reference = lambda k, c: {"ok": True, "by_period": store, "error": None}
    fv.guards = lambda q, e: {"ok": True}
    res = e31.evaluate(case, cand.e3_context(), fv, m)
    out = {"label": "NON-SCORED trust-boundary diagnostic: compromised verifier code (canned native/reference answers)",
           "case": case["case_id"], "status_with_compromised_verifier": res["status"], "reasons": res["reasons"],
           "conclusion": "Defeated, as declared: E3.1 trusts its own verifier/reference code, the trusted manifest and the pinned source."}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
