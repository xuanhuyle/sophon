"""Mechanical E3.1 verdict (PROTOCOL.md §6).

    python3 src/gate.py --evidence evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from decimal import Decimal
from pathlib import Path

E31 = Path(__file__).resolve().parents[1]
V = "VERIFIED_FOR_LAB_ASSUMPTIONS_AND_FRESH_CHECKS"
PRIOR_DIRS = ["experiments/E0_native_adapter", "experiments/E1_predicate_binding", "experiments/E2_blind_discovery",
              "experiments/E1_expressibility_erratum", "experiments/E3_formal_ir"]


def j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ev = Path(ap.parse_args().evidence)
    mismatch = []
    for line in (E31 / "FREEZE_MANIFEST.txt").read_text().splitlines()[2:]:
        h, name = line.split(maxsplit=1)
        if name != "PROTOCOL.md" and hashlib.sha256((E31 / name).read_bytes()).hexdigest() != h:
            mismatch.append(name)
    rep = j(ev / "reproduction" / "e3_defect_reproduction.json")
    g0 = rep["F_TIME"]["reproduced"] and rep["F_FORGE"]["reproduced"]
    res = j(ev / "run" / "case_results.json")
    by = {r["case_id"]: r for r in res}
    g1 = len(res) == 28 and all(r["passed"] for r in res)
    v5 = by["V5_FORGED_PAIR_STORE_READING"]["fresh"]
    forged = rep["F_FORGE"]["anti_vacuity"]["forged_oracle_by_year"]
    fresh_c = v5["fresh_native"]["by_period"]
    v5_anti = fresh_c is not None and any(Decimal(fresh_c[k]) != Decimal(forged[k]) for k in forged)
    g1 = g1 and v5_anti
    false_promotions = [r["case_id"] for r in res if r["status"] == V and r["expected_status"] != V]
    g2 = not false_promotions
    build = j(ev / "run" / "fresh_build.json")
    verified = [r for r in res if r["status"] == V]
    g3 = build["ok"] and all(r["fresh"]["fresh_native"]["ok"] and r["fresh"]["fresh_native"]["exit_code"] == 0
                             and r["fresh"]["fresh_reference"]["ok"] for r in verified)
    rp = j(ev / "replay" / "replay_record.json")
    g4 = rp["exit_code"] == 0 and rp["normalized_identical"] and rp["independent_rebuild"]["replay_build_ok"]
    diff = subprocess.run(["git", "-C", str(E31), "diff", "--stat", "5130518f2fa86281a8cd615bf7135d1dce5058e1", "--", *PRIOR_DIRS],
                          capture_output=True, text=True, cwd=str(E31))
    g5 = diff.returncode == 0 and diff.stdout.strip() == ""
    log = (ev / "pytest.log").read_text()
    g6 = " passed" in log and "failed" not in log and " error" not in log
    crit = {"G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6}
    if not g0 or not build["ok"]:
        verdict = "BLOCKED" if not g0 else "INCONCLUSIVE"
    elif mismatch:
        verdict = "INCONCLUSIVE"
    elif not g2:
        verdict = "FAIL_UNSAFE_INTEGRITY"
    elif all(crit.values()):
        verdict = "PASS_INTEGRITY_HARDENING"
    else:
        verdict = "PARTIAL_INTEGRITY_HARDENING"
    out = {"criteria": crit, "verdict": verdict, "false_promotions": false_promotions, "freeze_hash_mismatch": mismatch,
           "failing_cases": [r["case_id"] for r in res if not r["passed"]], "v5_fresh_customer_differs_from_forged": v5_anti,
           "verified_cases": [r["case_id"] for r in verified],
           "old_e3_false_promotions_now_blocked": sorted(r["case_id"] for r in res if r["e3_old"]["status"].startswith("VERIFIED")
                                                        and r["expected_status"] != V and r["status"] != V),
           "pytest_tail": log.strip().splitlines()[-1]}
    (ev / "gate.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
