"""Mechanical E3 verdict (PROTOCOL.md §7) from the recorded evidence.

    python3 src/gate.py --evidence evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

E3 = Path(__file__).resolve().parents[1]
POSITIVES = ["S1_T1_POSITIVE", "S2_T4_APPROVED_CUSTOMER", "S3_T7_EQUIVALENCE_APPROVED"]
# PROTOCOL.md §6 frozen classification of each untyped-baseline case: is the rejecting invariant new in E3?
NEW_OR_PARTLY = {"U1": "No", "U2": "No", "U3": "Partly", "U4": "Yes", "U5": "No", "U6": "Partly", "U7": "No"}
VERIFIED = "VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"


def j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ev = Path(ap.parse_args().evidence)

    manifest = (E3 / "FREEZE_MANIFEST.txt").read_text().splitlines()
    fixture_mismatch = []
    for line in manifest[2:]:
        h, name = line.split(maxsplit=1)
        if name == "PROTOCOL.md":
            continue  # amendments may be appended after the freeze; the frozen bytes stay in git at the freeze commit
        if hashlib.sha256((E3 / name).read_bytes()).hexdigest() != h:
            fixture_mismatch.append(name)

    ident, coll = j(ev / "identity.json"), j(ev / "collection_summary.json")
    must_run = ["NR_S1", "NR_S2_CUSTOMER", "NR_S2_STORE", "NR_S3", "NR_S4_PROXY"]
    runtime_ok = all(coll["native"].get(k) == 0 for k in must_run) and coll["native"].get("NR_PROBE_UNIT_PRICE_DIMENSION") != 0
    c0 = ident["ok"] and coll["oracle_equals_frozen"] and coll["pinned_warehouse_unchanged"] and not fixture_mismatch

    res = j(ev / "validation_results.json")
    by = {r["scenario_id"]: r for r in res}
    c1 = all(r["passed"] for r in res) and len(res) == 54
    false_verified = [r["scenario_id"] for r in res if r["status"] == VERIFIED and r["expected_status"] != VERIFIED]
    c2 = not false_verified
    c3_detail = {}
    for sid in POSITIVES:
        x = by[sid]["result"]
        sel = x["meaning"]["selected_reading"]
        rid = x["computability"][sel]["native_receipt_id"]
        rc = j(ev / "receipts" / "native" / f"{rid}.json")
        c3_detail[sid] = {"status": x["status"], "receipt": rid, "snapshot": rc["snapshot"], "exit": rc["exit_code"],
                          "native_equals_oracle": x["evidence"][sel]["native_equals_oracle"]}
    c3 = all(d["status"] == VERIFIED and d["snapshot"] == "PINNED" and d["exit"] == 0 and d["native_equals_oracle"] is True
             for d in c3_detail.values())
    ub = j(ev / "untyped_baseline.json")
    rejected = ub["summary"]["promoted_by_naive_and_rejected_by_e3"]
    rejected_new = [u for u in rejected if NEW_OR_PARTLY[u] in ("No", "Partly")]
    c4 = len(rejected) >= 3 and len(rejected_new) >= 3
    rp = j(ev / "replay" / "replay_record.json")
    c5 = rp["exit_code"] == 0 and rp["byte_identical"]
    log = (ev / "pytest.log").read_text()
    c6 = " passed" in log and "failed" not in log and " error" not in log

    crit = {"C0": c0, "C0_runtime": runtime_ok, "C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6}
    if not runtime_ok:
        verdict = "BLOCKED"
    elif not c0:
        verdict = "INCONCLUSIVE"
    elif not c2:
        verdict = "FAIL_UNSAFE_IR"
    elif not c4:
        verdict = "FAIL_NO_INCREMENTAL_VALUE"
    elif all(crit.values()):
        verdict = "PASS_IR_GUARD_VALUE"
    else:
        verdict = "PARTIAL_IR_GUARD_VALUE"
    out = {"criteria": crit, "verdict": verdict, "false_verified": false_verified, "fixture_hash_mismatch": fixture_mismatch,
           "failing_scenarios": [r["scenario_id"] for r in res if not r["passed"]], "positives": c3_detail,
           "untyped_rejected": rejected, "untyped_rejected_new_or_partly": rejected_new,
           "pytest_tail": log.strip().splitlines()[-1], "replay_sha256": rp["replay_sha256"]}
    (ev / "gate.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
