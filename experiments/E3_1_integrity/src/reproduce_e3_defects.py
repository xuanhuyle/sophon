"""Reproduce E3's two post-scoring defects with the UNMODIFIED E3 validator and E3's committed receipts (in memory only),
and record the old E3 status of every frozen E3.1 case. Run BEFORE the corrected verifier exists.

    python3 src/reproduce_e3_defects.py --out evidence/reproduction
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candidates as cand  # noqa: E402

E31 = HERE.parent
VERIFIED_OLD = "VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    ctx = cand.e3_context()
    cases = {c["case_id"]: c for c in cand.load(E31 / "cases" / "CASES.json")["cases"]}
    e3_head = subprocess.run(["git", "-C", str(E31), "log", "-1", "--format=%H", "--", str(cand.E3)], capture_output=True, text=True).stdout.strip()
    e3_code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((cand.E3 / "src").glob("*.py"))}

    def old(cid):
        res = cand.old_e3(cases[cid], ctx)
        return {"status": res["status"], "reasons": res["reasons"], "selected_reading": res["meaning"].get("selected_reading"),
                "evidence": res.get("evidence", {})}

    # F-TIME
    ft = old("T1_START_AFTER_EVAL_DATE")
    # F-FORGE (+ anti-vacuity: the forged pair is plausible, self-consistent, and not what the approved reading computes)
    ff = old("V5_FORGED_PAIR_STORE_READING")
    _, _, _, fctx = cand.candidate(cases["V5_FORGED_PAIR_STORE_READING"], ctx)
    forged_native = {r["metric_time__year"][:4]: r["revenue"] for r in fctx.native["NR_S2_CUSTOMER"]["rows"]}
    forged_oracle = fctx.oracle["OR_S2_CUSTOMER"]["by_year"]
    genuine_customer_native = {r["metric_time__year"][:4]: r["revenue"] for r in ctx.native["NR_S2_CUSTOMER"]["rows"]}
    trusted_customer = cand.load(cand.E3 / "cases" / "ORACLE_EXPECTED.json")["oracles"]["OR_S2_CUSTOMER"]["by_year"]
    d_eq = lambda a, b: set(a) == set(b) and all(Decimal(a[k]) == Decimal(b[k]) for k in a)  # noqa: E731
    anti = {"forged_native_by_year": forged_native, "forged_oracle_by_year": forged_oracle,
            "forged_pair_self_consistent": d_eq(forged_native, forged_oracle),
            "forged_receipt_internal_hash_valid": fctx.native["NR_S2_CUSTOMER"]["rows_sha256"] ==
            cand.e3val.sha_text(cand.e3val.canon(fctx.native["NR_S2_CUSTOMER"]["rows"])),
            "forged_receipt_claims_customer_query": fctx.native["NR_S2_CUSTOMER"]["query"] == ctx.native["NR_S2_CUSTOMER"]["query"],
            "forged_differs_from_frozen_trusted_customer_oracle": not d_eq(forged_oracle, trusted_customer),
            "forged_differs_from_E3_genuine_customer_native_run": not d_eq(forged_native, genuine_customer_native),
            "forged_values_are_the_store_reading": d_eq(forged_oracle, ctx.oracle["OR_S2_STORE"]["by_year"])}
    repro = {
        "label": "Retrospective reproduction of E3 post-scoring defects with the UNMODIFIED E3 validator (experiments/E3_formal_ir/src) and E3's committed receipts, altered in memory only.",
        "e3_last_commit_touching_dir": e3_head, "e3_src_sha256": e3_code,
        "F_TIME": {"case": "T1_START_AFTER_EVAL_DATE", "config": cases["T1_START_AFTER_EVAL_DATE"], "old_e3": ft,
                   "reproduced": ft["status"] == VERIFIED_OLD},
        "F_FORGE": {"case": "V5_FORGED_PAIR_STORE_READING", "config": cases["V5_FORGED_PAIR_STORE_READING"], "old_e3": ff,
                    "anti_vacuity": anti, "reproduced": ff["status"] == VERIFIED_OLD and all(anti[k] for k in anti if isinstance(anti[k], bool))},
    }
    (out / "e3_defect_reproduction.json").write_text(json.dumps(repro, indent=1) + "\n", encoding="utf-8")
    table = {cid: {k: v for k, v in old(cid).items() if k != "evidence"} | {"old_expected_by_protocol": c["old_e3_expected_status"]}
             for cid, c in cases.items()}
    (out / "old_e3_on_all_cases.json").write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"F_TIME_reproduced": repro["F_TIME"]["reproduced"], "F_TIME_old": ft["status"],
                      "F_FORGE_reproduced": repro["F_FORGE"]["reproduced"], "F_FORGE_old": ff["status"], "anti_vacuity": anti}, indent=1))
    for cid, v in table.items():
        print(f"{cid:50s} old={v['status'][:28]:28s} {','.join(v['reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
