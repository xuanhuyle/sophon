"""Write E5's frozen LAB inputs (run once before the freeze): versioned requirement IR P1_v1 / P1_v2, the
LAB_SIMULATED v2 approval bound to source hash + clause version + normalized-claim hash, the fixed native binding,
the native baseline candidate (E4 M6B + E4 M2) and the hand-written negative-control candidates.

    python3 src/build_inputs.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
EXP = E5.parent
REPO = EXP.parent
sys.path.insert(0, str(HERE))
import claim  # noqa: E402

E3 = EXP / "E3_formal_ir"
E4 = EXP / "E4_independent_verification"
MET = "dbt/retail_dwh/models/marts/semantic/_metrics.yml"
V1_SRC = E3 / "cases" / "sources" / "LAB_REVENUE_POLICY.md"
V2_SRC = E5 / "sources" / "LAB_REVENUE_POLICY_AMENDMENT_1.md"


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def rel(p: Path) -> str:
    return str(p.resolve().relative_to(REPO))


def ir_v1() -> dict:
    s1 = json.loads((E3 / "cases" / "records" / "S1.json").read_text())
    trusted = json.loads((EXP / "E3_1_integrity" / "cases" / "TRUSTED_MANIFEST.json").read_text())
    atoms = []
    for a in s1["requirement"]["atoms"]:
        atoms.append({k: v for k, v in a.items()})
    gs = s1["governing_source"]
    return {"ir_version": "E5-IR-0.1", "version_id": "P1_v1", "policy": "P1", "series": "LAB-REV-POLICY/S1",
            "provenance": "LAB_AUTHORED restatement of E3 record S1 (requirement atoms copied verbatim)",
            "derived_from_e3": {"record": rel(E3 / "cases" / "records" / "S1.json"), "record_sha256": sha_file(E3 / "cases" / "records" / "S1.json"),
                                "reading_id": "R_SINGLE", "reading_meaning_sha256": trusted["approved_reading_meaning_sha256"]["S1/R_SINGLE"]},
            "governing_source": {"source_id": gs["source_id"], "document_id": "LAB-REV-POLICY", "path": rel(V1_SRC),
                                 "content_sha256": gs["content_sha256"], "clause_id": "S1", "clause_version": 1,
                                 "observed_at": gs["observed_at"], "effective_from": gs["effective_from"], "effective_to": gs["effective_to"]},
            "supersedes": None,
            "requirement": {"text": s1["requirement"]["text"], "atoms": atoms, "population": s1["requirement"]["population"]},
            "approval_ids": ["AP_S1_READ"]}


def ir_v2(v1: dict) -> dict:
    text = "Report, for each calendar year of order date, the revenue from completed orders, counting only order lines whose charged unit price is at least 120."
    atoms = copy.deepcopy(v1["requirement"]["atoms"])
    for a in atoms:
        a["span"] = list(a["span"])
        a["text"] = text[a["span"][0]:a["span"][1]]
        if a["atom_id"] == "unit_price_threshold":
            a["value"] = "120"
    return {"ir_version": "E5-IR-0.1", "version_id": "P1_v2", "policy": "P1", "series": "LAB-REV-POLICY/S1",
            "provenance": "LAB_AUTHORED (E5 amendment; hypothetical retroactive amendment, not historical law)",
            "derived_from_e3": None,
            "governing_source": {"source_id": "LAB-REV-POLICY", "document_id": "LAB-REV-POLICY-AMD-1", "path": rel(V2_SRC),
                                 "content_sha256": sha_file(V2_SRC), "clause_id": "S1", "clause_version": 2,
                                 "observed_at": "2026-10-09T09:00:00Z", "effective_from": "2025-01-01", "effective_to": None},
            "supersedes": {"version_id": "P1_v1", "ir_sha256": claim.sha_text(claim.canon(v1)), "for_order_dates_from": "2025-01-01"},
            "requirement": {"text": text, "atoms": atoms, "population": v1["requirement"]["population"]},
            "approval_ids": ["AP_S1_V2"]}


def approval_v2(v2: dict) -> dict:
    gs = v2["governing_source"]
    return {"approval_id": "AP_S1_V2", "provenance": "LAB_SIMULATED", "approver_role": "LAB_REVENUE_POLICY_OWNER",
            "claim": {"kind": "INTERPRETATION_CHOICE", "series": v2["series"], "version_id": v2["version_id"],
                      "normalized_claim_sha256": claim.meaning_sha(v2), "normalized_claim": claim.normalized_claim(v2)},
            "scope": {"source_id": gs["source_id"], "document_id": gs["document_id"], "source_sha256": gs["content_sha256"],
                      "clause_id": gs["clause_id"], "clause_version": gs["clause_version"]},
            "known_at": "2026-10-10T10:00:00Z", "effective_from": "2025-01-01", "effective_to": None,
            "authorizes": "the LAB meaning of [S1 v2] only; NOT a deployment authorization and NOT an implementation approval",
            "note": "simulated role approval; no real person, signature or identity verification"}


def binding() -> dict:
    return {"binding_id": "NB_E5_1",
            "provenance": "LAB_AUTHORED from E4 candidates M6B (NO_MATERIAL_DRIFT_FOR_CHECKS) and M2 (VERIFIED_FOR_LAB_CHECKS); "
                          "fixed before E5; not a separate LAB approval; not a fresh or blind mapping",
            "metrics": {
                "premium_completed_revenue": {"implements_series": "LAB-REV-POLICY/S1", "file": MET,
                                              "predicate_atoms": ["completed", "unit_price_threshold"],
                                              "description_template": "Completed revenue on lines with unit price at least {unit_price_threshold}."},
                "french_market_revenue": {"implements_series": "LAB-REV-POLICY/S2", "reading_id": "R_CUSTOMER_COUNTRY", "file": MET,
                                          "predicate_fact_kinds": ["order_status_label", "customer_country"]}},
            "measure": {"order_line_amount": "revenue"},
            "fact_kind_dimension": {"order_status_label": "sales__status", "order_line_charged_unit_price": "sales__unit_price",
                                    "customer_country": "customer__country"},
            "dimension_unit": {"sales__unit_price": "CURRENCY_PER_UNIT"},
            "literal_style": {"order_status_label": "QUOTED_STRING", "order_line_charged_unit_price": "PLAIN_DECIMAL"},
            "operator_sql": {"EQ": "=", "GE": ">=", "GT": ">", "LE": "<=", "LT": "<"},
            "predicate_template": "{{ Dimension('<dimension>') }} <operator> <literal>",
            "conjunction": " AND ",
            "supported_delta_kinds": ["PREDICATE_VALUE_CHANGE"]}


def candidates() -> dict:
    m6b = json.loads((E4 / "candidates" / "M6B.json").read_text())
    m2 = json.loads((E4 / "candidates" / "M2.json").read_text())
    base_patch = m6b["patch"] + m2["patch"]
    q1 = {"metric": "premium_completed_revenue", "group_by": ["metric_time__year"], "where": []}
    p1_filter = "    filter: \"{{ Dimension('sales__status') }} = 'completed' AND {{ Dimension('sales__unit_price') }} >= 100\"\n"
    p2_filter = "    filter: \"{{ Dimension('sales__status') }} = 'completed' AND {{ Dimension('customer__country') }} = 'France'\"\n"
    out = {"BASELINE": {"candidate_id": "BASELINE", "revision_id": "REV_P1_V1_BASELINE", "compose": [], "patch": base_patch, "query": q1,
                        "provenance": "E4 candidates M6B (patch ops 1-2) + M2 (patch op 1), applied in that order to pinned upstream 312e97ad. "
                                      "Lab-added native metrics; not an organically maintained enterprise metric."}}
    wrong = {"N2A_GE119": p1_filter.replace(">= 100", ">= 119"),
             "N2B_GT120": p1_filter.replace(">= 100", "> 120"),
             "N2C_NONCANCELLED": p1_filter.replace("= 'completed'", "!= 'cancelled'").replace(">= 100", ">= 120")}
    for cid, new in wrong.items():
        out[cid] = {"candidate_id": cid, "revision_id": None, "compose": ["BASELINE"], "patch": [{"op": "replace", "file": MET, "old": p1_filter, "new": new}],
                    "query": q1, "provenance": "hand-written negative control (wrong P1 v2 implementation), applied on top of BASELINE"}
    out["N3_P2_COLLATERAL"] = {"candidate_id": "N3_P2_COLLATERAL", "revision_id": None, "compose": ["BASELINE", "GENERATED"],
                               "patch": [{"op": "replace", "file": MET, "old": p2_filter,
                                          "new": p2_filter.replace("= 'France'", "= 'France' AND {{ Dimension('sales__unit_price') }} >= 120")}],
                               "query": {"metric": "french_market_revenue", "group_by": ["metric_time__year"], "where": []},
                               "provenance": "hand-written negative control: the generated proposal plus a collateral edit of the P2 metric "
                                             "(the amended threshold leaks into french_market_revenue)"}
    return out


def main() -> int:
    v1 = ir_v1()
    v2 = ir_v2(v1)
    dump(E5 / "ir" / "P1_v1.json", v1)
    dump(E5 / "ir" / "P1_v2.json", v2)
    dump(E5 / "approvals" / "AP_S1_V2.json", approval_v2(v2))
    dump(E5 / "ir" / "NATIVE_BINDING.json", binding())
    for cid, c in candidates().items():
        dump(E5 / "candidates" / f"{cid}.json", c)
    print(json.dumps({"P1_v1_meaning": claim.meaning_sha(v1), "P1_v2_meaning": claim.meaning_sha(v2),
                      "v2_source_sha256": v2["governing_source"]["content_sha256"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
