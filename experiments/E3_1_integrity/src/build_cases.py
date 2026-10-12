"""Write the frozen E3.1 inputs (run BEFORE the corrected verifier exists):
  cases/TRUSTED_MANIFEST.json  independent trust anchors, taken from E0's committed evidence and E3's frozen fixtures,
                               never from a candidate receipt
  cases/CASES.json             12 temporal (T) and 15 evidence (V) cases with frozen expected E3.1 outcomes

    python3 src/build_cases.py
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

E31 = Path(__file__).resolve().parents[1]
EXP = E31.parent
E0, E3 = EXP / "E0_native_adapter", EXP / "E3_formal_ir"


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


POINTERS = ("native_receipt_id", "oracle_id")


def reading_meaning(reading: dict) -> dict:
    """A reading's meaning without evidence pointers (receipt ids are where evidence is, not what was approved)."""
    r = copy.deepcopy(reading)
    for k in POINTERS:
        r.pop(k, None)
    for b in r.get("bindings", {}).values():
        if b.get("derivation"):
            b["derivation"].pop("guard_receipt_id", None)
    return r


def trusted_manifest() -> dict:
    e0 = load(E0 / "evidence" / "regen" / "run_receipt.json")
    readings = {}
    for rid in ("S1", "S2", "S3", "S4"):
        rec = load(E3 / "cases" / "records" / f"{rid}.json")
        for r in rec["interpretation"]["readings"]:
            readings[f"{rid}/{r['reading_id']}"] = sha_bytes(canon(reading_meaning(r)).encode())
    code = {p: sha_bytes((EXP.parent / p).read_bytes()) for p in (
        "experiments/E1_expressibility_erratum/src/oracle_b1.py",
        "experiments/E2_blind_discovery/src/e2_oracle.py",
        "experiments/E1_expressibility_erratum/src/run_erratum.py",
        "experiments/E3_formal_ir/src/validator.py",
        "experiments/E3_formal_ir/src/models.py",
        "experiments/E0_native_adapter/src/mf_adapter.py",
        "experiments/E1_predicate_binding/src/evaluator.py")}
    return {
        "label": "TRUSTED ANCHORS for E3.1 (LAB trust model). Sources: E0 committed regen receipt and env freeze; E3 frozen fixtures; code files on this branch. Never read from candidate receipts.",
        "upstream": {"repo": "behramkorkut/Governed-Analytics-Agent", "commit": e0["upstream_commit"]},
        "env_freeze_sha256": sha_bytes((E0 / "evidence" / "env_freeze.txt").read_bytes()),
        "semantic_manifest_sha256": e0["fingerprints_final"]["semantic_manifest_sha256"],
        "raw_csv_sha256": {k: v["sha256"] for k, v in sorted(e0["S1_csv"].items())},
        "governing_source": {"path": "experiments/E3_formal_ir/cases/sources/LAB_REVENUE_POLICY.md",
                             "sha256": sha_bytes((E3 / "cases" / "sources" / "LAB_REVENUE_POLICY.md").read_bytes())},
        "approved_reading_meaning_sha256": readings,
        "reference_functions": {
            "S1/R_SINGLE": {"code": "experiments/E1_expressibility_erratum/src/oracle_b1.py", "call": "compute(raw)['by_year']"},
            "S2/R_CUSTOMER_COUNTRY": {"code": "experiments/E2_blind_discovery/src/e2_oracle.py", "call": "DIAGNOSTICS['H3_reading_customer_country'](raw)"},
            "S2/R_STORE_COUNTRY": {"code": "experiments/E2_blind_discovery/src/e2_oracle.py", "call": "DIAGNOSTICS['H3_reading_store_country'](raw)"},
            "S3/R_SINGLE": {"code": "experiments/E2_blind_discovery/src/e2_oracle.py", "call": "h6(raw)"}},
        "guard_code": {"code": "experiments/E1_expressibility_erratum/src/run_erratum.py", "call": "guards(warehouse_lines(wh), csv_prices(raw), n, compiled_sql)"},
        "code_sha256": code,
        "expected_reference_values": {k: load(E3 / "cases" / "ORACLE_EXPECTED.json")["oracles"][o]["by_year"]
                                      for k, o in (("S1/R_SINGLE", "OR_S1"), ("S2/R_CUSTOMER_COUNTRY", "OR_S2_CUSTOMER"),
                                                   ("S2/R_STORE_COUNTRY", "OR_S2_STORE"), ("S3/R_SINGLE", "OR_S3"))},
    }


TK, TK_EARLY, EFF = "2026-10-06T00:00:00Z", "2026-09-30T00:00:00Z", "2026-06-30"
V, NIF, NK, MISS, U, NV, INV = ("VERIFIED_FOR_LAB_ASSUMPTIONS_AND_FRESH_CHECKS", "REQUIREMENT_NOT_IN_FORCE",
                                "NOT_KNOWN_AT_EVALUATION_TIME", "MISSING_REQUIRED_FACT", "MEANING_UNRESOLVED",
                                "NOT_VERIFIED", "STRUCTURALLY_INVALID")
STATUS = "{{ Dimension('sales__status') }} = 'completed'"
STORE_FR = "{{ Dimension('store__store_country') }} = 'France'"
GS = ["governing_source"]
R0 = ["interpretation", "readings", 0]


def case(cid, group, rec, approvals, expect, reasons=(), at=TK, eff=EFF, patch=(), ops=(), fresh=None, old=None, note="", **extra):
    return {"case_id": cid, "group": group, "record": rec, "approvals": list(approvals), "revocations": [],
            "eval_known_at": at, "eval_effective_at": eff, "record_patch": list(patch), "candidate_ops": list(ops),
            "fresh_conditions": fresh or {"estate": "TRUSTED_REBUILD", "runtime": "AVAILABLE", "reference_code": "TRUSTED"},
            "expected": {"status": expect, "reasons_include": list(reasons), **extra},
            "old_e3_expected_status": old, "note": note}


def cases() -> list[dict]:
    s2 = ["AP_S2_CUSTOMER"]
    eff = lambda f=None, t=None: ([{"op": "set", "path": GS + ["effective_from"], "value": f}] if f else []) + \
        ([{"op": "set", "path": GS + ["effective_to"], "value": t}] if t else [])  # noqa: E731
    T = [
        case("T1_START_AFTER_EVAL_DATE", "T", "S2", s2, NIF, ["REQUIREMENT_NOT_IN_FORCE"], patch=eff("2027-01-01"),
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS", note="F-TIME configuration"),
        case("T2_START_BOUNDARY_INCLUSIVE", "T", "S2", s2, V, patch=eff("2026-06-30")),
        case("T3_END_BOUNDARY_INCLUSIVE", "T", "S2", s2, V, patch=eff(t="2026-06-30")),
        case("T4_AFTER_END", "T", "S2", s2, NIF, ["REQUIREMENT_NOT_IN_FORCE"], patch=eff(t="2026-06-29")),
        case("T5_SOURCE_NOT_YET_KNOWN", "T", "S2", s2, NK, ["SOURCE_NOT_YET_KNOWN"], at=TK_EARLY),
        case("T6_APPROVAL_KNOWN_LATER", "T", "S2", ["AP_S2_FUTURE"], U, ["INTERPRETATION_UNRESOLVED"], must_not_mention=["AP_S2_FUTURE"]),
        case("T7A_RETROACTIVE_AS_KNOWN_BEFORE_OBSERVATION", "T", "S2", s2, NK, ["SOURCE_NOT_YET_KNOWN"], at=TK_EARLY, eff="2024-06-30"),
        case("T7B_RETROACTIVE_AS_KNOWN_AFTER_OBSERVATION", "T", "S2", s2, V, eff="2024-06-30"),
        case("T8_APPROVAL_IN_FORCE_REQUIREMENT_ENDED", "T", "S2", s2, NIF, ["REQUIREMENT_NOT_IN_FORCE"], patch=eff(t="2025-12-31")),
        case("T9_IN_FORCE_UNAUTHORIZED", "T", "S2", [], U, ["INTERPRETATION_UNRESOLVED"]),
        case("T10_CORRUPT_SOURCE_AND_NOT_IN_FORCE", "T", "S2", s2, INV, ["SOURCE_HASH_MISMATCH"],
             patch=eff("2027-01-01") + [{"op": "set", "path": GS + ["content_sha256"], "value": "0" * 64}]),
        case("T11_MISSING_FACT_NOT_IN_FORCE", "T", "S4", ["AP_S4_READ"], NIF, ["REQUIREMENT_NOT_IN_FORCE"], patch=eff("2027-01-01"),
             uncovered=["settled_by_processor"]),
        case("T12_S3_APPROVED_EQUIVALENCE_NOT_IN_FORCE", "T", "S3", ["AP_S3_READ", "AP_S3_EQ"], NIF, ["REQUIREMENT_NOT_IN_FORCE"], patch=eff("2027-01-01")),
    ]
    proxy = [{"op": "set", "path": R0 + ["bindings", "settled_by_processor"],
              "value": {"kind": "DIRECT", "semantic_object": {"type": "dimension", "name": "sales__status"},
                        "physical_lineage": ["gold.fact_sales.status"], "value_override": "completed"}},
             {"op": "set", "path": R0 + ["native_query"], "value": {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, STATUS]}},
             {"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S4_PROXY"},
             {"op": "set", "path": R0 + ["oracle_id"], "value": "OR_S4_PROXY"}]
    fake_manifest = "f" * 64
    fake_csv = "e" * 64
    D = R0 + ["bindings", "unit_price_threshold", "derivation"]
    negqty_ptrs = [{"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S1_NEGQTY"},
                   {"op": "set", "path": D + ["guard_receipt_id"], "value": "GR_S1_NEGQTY"}]
    store_query = {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, STORE_FR]}
    Vc = [
        case("V1_S1_DERIVED_CLEAN", "V", "S1", ["AP_S1_READ"], V, fresh_values="S1/R_SINGLE"),
        case("V2_S2_CUSTOMER_CLEAN", "V", "S2", s2, V, fresh_values="S2/R_CUSTOMER_COUNTRY"),
        case("V3_S3_EQUIVALENCE_CLEAN", "V", "S3", ["AP_S3_READ", "AP_S3_EQ"], V, fresh_values="S3/R_SINGLE"),
        case("V4_S4_STATUS_PROXY", "V", "S4", ["AP_S4_READ"], MISS, ["NOT_DESIGNATED_FOR_FACT"], patch=proxy, uncovered=["settled_by_processor"]),
        case("V5_FORGED_PAIR_STORE_READING", "V", "S2", s2, NV, ["CANDIDATE_NATIVE_DISAGREES_WITH_FRESH", "CANDIDATE_REFERENCE_DISAGREES_WITH_FRESH"],
             ops=[{"op": "replace_native_rows", "receipt": "NR_S2_CUSTOMER", "from_receipt": "NR_S2_STORE", "rehash": True},
                  {"op": "replace_oracle_values", "oracle": "OR_S2_CUSTOMER", "from_oracle": "OR_S2_STORE"}],
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS", note="F-FORGE configuration (plausible wrong business reading)",
             fresh_values="S2/R_CUSTOMER_COUNTRY"),
        case("V5B_FORGED_PAIR_ONE_CENT", "V", "S2", s2, NV, ["CANDIDATE_NATIVE_DISAGREES_WITH_FRESH", "CANDIDATE_REFERENCE_DISAGREES_WITH_FRESH"],
             ops=[{"op": "add_cent_native", "receipt": "NR_S2_CUSTOMER", "rehash": True}, {"op": "add_cent_oracle", "oracle": "OR_S2_CUSTOMER"}],
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"),
        case("V6_SINGLE_NATIVE_RECEIPT_TAMPERED", "V", "S2", s2, NV, ["NATIVE_ORACLE_MISMATCH"],
             ops=[{"op": "add_cent_native", "receipt": "NR_S2_CUSTOMER", "rehash": True}], old="NOT_VERIFIED"),
        case("V7A_CONSISTENT_WRONG_SEMANTIC_REVISION", "V", "S2", s2, NV, ["TRUST_ANCHOR_MISMATCH"],
             patch=[{"op": "set", "path": ["verification_request", "semantic_manifest_sha256"], "value": fake_manifest}],
             ops=[{"op": "set_native_fingerprint", "receipt": "NR_S2_CUSTOMER", "field": "semantic_manifest_sha256", "value": fake_manifest}],
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"),
        case("V7B_CONSISTENT_WRONG_RAW_DATA_HASH", "V", "S2", s2, NV, ["TRUST_ANCHOR_MISMATCH"],
             patch=[{"op": "set", "path": ["verification_request", "raw_csv_sha256", "orders.csv"], "value": fake_csv}],
             ops=[{"op": "set_native_raw_csv_hash", "receipt": "NR_S2_CUSTOMER", "file": "orders.csv", "value": fake_csv},
                  {"op": "set_oracle_raw_csv_hash", "oracle": "OR_S2_CUSTOMER", "file": "orders.csv", "value": fake_csv}],
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"),
        case("V7C_STALE_RECEIPT_REVISION_ONLY", "V", "S2", s2, NV, ["RECEIPT_REVISION_MISMATCH"],
             ops=[{"op": "set_native_fingerprint", "receipt": "NR_S2_CUSTOMER", "field": "semantic_manifest_sha256", "value": fake_manifest}],
             old="NOT_VERIFIED"),
        case("V8A_FRESH_RUNTIME_UNAVAILABLE", "V", "S2", s2, NV, ["FRESH_RUNTIME_UNAVAILABLE"],
             fresh={"estate": "TRUSTED_REBUILD", "runtime": "UNAVAILABLE", "reference_code": "TRUSTED"},
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"),
        case("V8B_REFERENCE_CODE_UNTRUSTED", "V", "S2", s2, NV, ["FRESH_REFERENCE_UNAVAILABLE"],
             fresh={"estate": "TRUSTED_REBUILD", "runtime": "AVAILABLE", "reference_code": "TAMPERED"},
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"),
        case("V9A_NEGATIVE_QUANTITY_FORGED_GUARDS_AND_AMOUNTS", "V", "S1", ["AP_S1_READ"], NV, ["FRESH_GUARD_FAILED"],
             patch=negqty_ptrs,
             ops=[{"op": "replace_native_rows", "receipt": "NR_S1_NEGQTY", "from_receipt": "NR_S1", "rehash": True},
                  {"op": "force_guards_true", "guard": "GR_S1_NEGQTY"}],
             fresh={"estate": "CONTROL_NEGATIVE_QUANTITY", "runtime": "AVAILABLE", "reference_code": "TRUSTED"},
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS", note="recorded amounts match the oracle; the data snapshot has q = -1 lines"),
        case("V9B_NEGATIVE_QUANTITY_HONEST_RECEIPTS", "V", "S1", ["AP_S1_READ"], NV, ["GUARD_FAILED"], patch=negqty_ptrs,
             fresh={"estate": "CONTROL_NEGATIVE_QUANTITY", "runtime": "AVAILABLE", "reference_code": "TRUSTED"}, old="NOT_VERIFIED"),
        case("V10_APPROVED_READING_CONTENT_SWAPPED", "V", "S2", s2, NV, ["UNTRUSTED_READING_CONTENT"],
             patch=[{"op": "set", "path": R0 + ["atom_fact_kinds", "french_market"], "value": "store_country_attribute"},
                    {"op": "set", "path": R0 + ["bindings", "french_market"],
                     "value": {"kind": "DIRECT", "semantic_object": {"type": "dimension", "name": "store__store_country"},
                               "physical_lineage": ["gold.dim_stores.country"]}},
                    {"op": "set", "path": R0 + ["native_query"], "value": store_query}],
             ops=[{"op": "set_native_query", "receipt": "NR_S2_CUSTOMER", "value": store_query},
                  {"op": "replace_native_rows", "receipt": "NR_S2_CUSTOMER", "from_receipt": "NR_S2_STORE", "rehash": True},
                  {"op": "replace_oracle_values", "oracle": "OR_S2_CUSTOMER", "from_oracle": "OR_S2_STORE"}],
             old="VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS",
             note="approval selects R_CUSTOMER_COUNTRY by id; the reading's content was rewritten to the store reading"),
    ]
    return T + Vc


def main() -> int:
    (E31 / "cases").mkdir(exist_ok=True)
    (E31 / "cases" / "TRUSTED_MANIFEST.json").write_text(json.dumps(trusted_manifest(), indent=1) + "\n", encoding="utf-8")
    cs = cases()
    (E31 / "cases" / "CASES.json").write_text(json.dumps({"eval_known_at_default": TK, "eval_effective_at_default": EFF,
                                                          "cases": cs}, indent=1) + "\n", encoding="utf-8")
    print(len(cs), "cases;", sum(c["group"] == "T" for c in cs), "temporal,", sum(c["group"] == "V" for c in cs), "evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
