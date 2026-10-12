"""Test harness (frozen before the corrected verifier): build the *candidate* inputs of an E3.1 case.

A candidate = the IR record (an E3 fixture plus E3 patch ops), the supplied approvals/revocations, and the candidate
receipts (E3's committed native/guard/oracle receipts, then in-memory tamper ops). Nothing here decides a status and
nothing is written to E3's directory.
"""
from __future__ import annotations

import copy
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E31 = HERE.parent
EXP = E31.parent
E3 = EXP / "E3_formal_ir"
sys.path.insert(0, str(E3 / "src"))
import run_scenarios as e3rs  # noqa: E402  (unmodified E3 harness: apply_patch, load, load_dir)
import validator as e3val  # noqa: E402  (unmodified E3 validator)


def load(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def e3_context() -> "e3val.Context":
    """E3's own validation context from E3's committed files (catalog + receipts)."""
    return e3rs.context()


def rehash(rc: dict) -> None:
    rc["rows_sha256"] = e3val.sha_text(e3val.canon(rc["rows"]))


def apply_candidate_ops(ctx: "e3val.Context", ops: list[dict]) -> "e3val.Context":
    native, oracle, guards = copy.deepcopy(ctx.native), copy.deepcopy(ctx.oracle), copy.deepcopy(ctx.guards)
    for op in ops:
        k = op["op"]
        if k == "replace_native_rows":          # copy another receipt's rows, keep this receipt's query/identity
            native[op["receipt"]]["rows"] = copy.deepcopy(native[op["from_receipt"]]["rows"])
            if op.get("rehash"):
                rehash(native[op["receipt"]])
        elif k == "set_native_query":
            native[op["receipt"]]["query"] = copy.deepcopy(op["value"])
        elif k == "add_cent_native":            # +0.01 on every row
            rc = native[op["receipt"]]
            m = rc["query"]["metric"]
            for r in rc["rows"]:
                r[m] = str(Decimal(r[m]) + Decimal("0.01"))
            if op.get("rehash"):
                rehash(rc)
        elif k == "replace_oracle_values":
            oracle[op["oracle"]]["by_year"] = copy.deepcopy(oracle[op["from_oracle"]]["by_year"])
        elif k == "add_cent_oracle":
            oracle[op["oracle"]]["by_year"] = {y: str(Decimal(v) + Decimal("0.01")) for y, v in oracle[op["oracle"]]["by_year"].items()}
        elif k == "set_native_fingerprint":
            native[op["receipt"]]["fingerprint"][op["field"]] = copy.deepcopy(op["value"])
        elif k == "set_native_raw_csv_hash":
            native[op["receipt"]]["fingerprint"]["raw_csv_sha256"][op["file"]] = op["value"]
        elif k == "set_oracle_raw_csv_hash":
            oracle[op["oracle"]]["raw_csv_sha256"][op["file"]] = op["value"]
        elif k == "force_guards_true":
            for g in guards[op["guard"]]["guards"]:
                guards[op["guard"]]["guards"][g] = True
        else:
            raise ValueError(op)
    return e3val.Context(**{**ctx.__dict__, "native": native, "oracle": oracle, "guards": guards})


def candidate(case: dict, ctx: "e3val.Context"):
    rec = e3rs.apply_patch(load(E3 / "cases" / "records" / f"{case['record']}.json"), case.get("record_patch", []))
    approvals = e3rs.load_dir(E3 / "cases" / "approvals")
    aps = [approvals[a] for a in case.get("approvals", [])]
    rvs = [approvals[r] for r in case.get("revocations", [])]
    return rec, aps, rvs, apply_candidate_ops(ctx, case.get("candidate_ops", []))


def old_e3(case: dict, ctx: "e3val.Context") -> dict:
    rec, aps, rvs, c = candidate(case, ctx)
    return e3val.validate(rec, aps, rvs, c, case["eval_known_at"], case["eval_effective_at"])
