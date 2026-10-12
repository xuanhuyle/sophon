"""E3.1 unit tests (G6): applicability boundaries and wrapper precedence. No MetricFlow needed: fresh verification is
exercised by src/e31.py on genuine native runs; here the verifier is absent, so no case may be promoted."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import candidates as cand  # noqa: E402
import e31  # noqa: E402

M = cand.load(e31.E31 / "cases" / "TRUSTED_MANIFEST.json")
CASES = {c["case_id"]: c for c in cand.load(e31.E31 / "cases" / "CASES.json")["cases"]}
CTX = cand.e3_context()


def test_in_force_inclusive_boundaries():
    assert e31.in_force("2026-06-30", None, "2026-06-30")
    assert not e31.in_force("2026-07-01", None, "2026-06-30")
    assert e31.in_force("2024-01-01", "2026-06-30", "2026-06-30")
    assert not e31.in_force("2024-01-01", "2026-06-29", "2026-06-30")
    assert e31.in_force("2024-01-01", None, "2099-12-31")


def test_no_promotion_without_fresh_verifier():
    for c in CASES.values():
        assert e31.evaluate(c, CTX, None, M)["status"] != e31.V, c["case_id"]


def test_precedence_without_fresh():
    want = {"T1_START_AFTER_EVAL_DATE": "REQUIREMENT_NOT_IN_FORCE", "T5_SOURCE_NOT_YET_KNOWN": "NOT_KNOWN_AT_EVALUATION_TIME",
            "T10_CORRUPT_SOURCE_AND_NOT_IN_FORCE": "STRUCTURALLY_INVALID", "T11_MISSING_FACT_NOT_IN_FORCE": "REQUIREMENT_NOT_IN_FORCE",
            "T9_IN_FORCE_UNAUTHORIZED": "MEANING_UNRESOLVED", "V4_S4_STATUS_PROXY": "MISSING_REQUIRED_FACT"}
    for cid, s in want.items():
        assert e31.evaluate(CASES[cid], CTX, None, M)["status"] == s, cid


def test_reading_meaning_hash_ignores_evidence_pointers_only():
    rec = cand.load(cand.E3 / "cases" / "records" / "S1.json")
    r = rec["interpretation"]["readings"][0]
    base = e31.meaning_sha(r)
    r2 = {**r, "native_receipt_id": "OTHER", "oracle_id": "OTHER"}
    assert e31.meaning_sha(r2) == base == M["approved_reading_meaning_sha256"]["S1/R_SINGLE"]
    r3 = {**r, "native_query": {**r["native_query"], "where": r["native_query"]["where"][:1]}}
    assert e31.meaning_sha(r3) != base
