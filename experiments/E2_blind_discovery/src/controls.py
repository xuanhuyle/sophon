"""Scorer negative controls (PROTOCOL.md section 6.3). The 'perfect' control is DERIVED FROM THE SEALED REFERENCE to
show the scorer can award full credit; it is never a solver output. Each mutation must lose the stated credit."""
from __future__ import annotations

import copy
import json

KIND_CLASS = {"bound": "BOUND_AND_EXPOSED", "not_found": "NOT_FOUND_IN_BOUNDED_ESTATE",
              "not_exposed": "PRESENT_IN_SOURCE_NOT_EXPOSED", "unresolved": "UNRESOLVED_INTERPRETATION"}


def perfect(ref: dict) -> dict:
    cases = []
    for cid, rc in ref["cases"].items():
        preds = []
        for rid, rp in rc["predicates"].items():
            preds.append({"predicate_id": rid, "text_span": rp["anchors"][0], "meaning": rid,
                          "classification": KIND_CLASS[rp["kind"]],
                          "semantic_object": rp.get("semantic", [None])[0] if rp["kind"] == "bound" else None,
                          "value": rp.get("value"), "physical_fields": rp.get("physical", [])[:1], "evidence": ["control"],
                          "missing_or_open_question": "customer country or store country?" if rp["kind"] == "unresolved" else None,
                          "confidence": "high"})
        cases.append({"clause_id": cid, "predicates": preds, "native_query": rc.get("canonical_query"),
                      "can_establish": "", "cannot_establish": "", "overall_verdict": rc["accepted_verdicts"][0],
                      "overall_confidence": "high", "abstain": False})
    return {"cases": cases}


def _case(p, cid):
    return next(c for c in p["cases"] if c["clause_id"] == cid)


def _pred(c, rid):
    return next(x for x in c["predicates"] if x["predicate_id"] == rid)


def mutations(ref: dict) -> dict[str, str]:
    base = perfect(ref)
    out = {"control_perfect": json.dumps(base), "control_perfect_code_fenced": "```json\n" + json.dumps(base) + "\n```"}

    m = copy.deepcopy(base)  # wrong metric
    c = _case(m, "H2"); c["native_query"]["metric"] = "gross_margin_rate"; _pred(c, "gross_profit")["semantic_object"] = "gross_margin_rate"
    out["mut_wrong_metric_H2"] = json.dumps(m)

    m = copy.deepcopy(base)  # wrong physical column / dimension
    c = _case(m, "H6"); p = _pred(c, "france_residence")
    p["semantic_object"], p["physical_fields"] = "Dimension('store__store_country')", ["gold.dim_stores.country"]
    c["native_query"]["where"] = ["{{ Dimension('sales__channel') }} = 'online'", "{{ Dimension('store__store_country') }} = 'France'"]
    out["mut_wrong_physical_H6"] = json.dumps(m)

    m = copy.deepcopy(base)  # missing mandatory predicate
    c = _case(m, "H4"); c["predicates"] = [x for x in c["predicates"] if x["predicate_id"] != "germany_stores"]
    c["native_query"]["where"] = ["{{ Dimension('sales__status') }} != 'cancelled'"]
    out["mut_missing_predicate_H4"] = json.dumps(m)

    m = copy.deepcopy(base)  # payment proxy
    c = _case(m, "H1"); p = _pred(c, "payment_received")
    p.update(classification="BOUND_AND_EXPOSED", semantic_object="Dimension('sales__status')", value="completed",
             physical_fields=["gold.fact_sales.status"], confidence="high")
    c["overall_verdict"] = "VERIFIED_FOR_SPECIFIED_CHECKS"
    c["native_query"] = {"metric": "completed_revenue", "group_by": ["metric_time__year"], "where": []}
    out["mut_payment_proxy_H1"] = json.dumps(m)

    m = copy.deepcopy(base)  # blanket unknown
    for c in m["cases"]:
        c["overall_verdict"] = "PARTIAL_OR_UNKNOWN"
        c["native_query"] = None
        for p in c["predicates"]:
            p["classification"], p["semantic_object"], p["physical_fields"] = "UNRESOLVED_INTERPRETATION", None, []
    out["mut_blanket_unknown"] = json.dumps(m)

    m = copy.deepcopy(base)  # false verified on the not-exposed case
    c = _case(m, "H5"); p = _pred(c, "gmail")
    p.update(classification="BOUND_AND_EXPOSED", semantic_object="Dimension('customer__email')", confidence="high")
    c["overall_verdict"] = "VERIFIED_FOR_SPECIFIED_CHECKS"
    c["native_query"] = {"metric": "completed_revenue", "group_by": ["metric_time__year"], "where": ["{{ Dimension('customer__email') }} like '%@gmail.com'"]}
    out["mut_false_verified_H5"] = json.dumps(m)

    out["mut_malformed"] = "Here is my analysis: " + json.dumps(base)
    return out


EXPECTATIONS = {
    "control_perfect": {"gate": "PASS_BOUNDED_DISCOVERY_SIGNAL", "correct": 6},
    "control_perfect_code_fenced": {"gate": "PASS_BOUNDED_DISCOVERY_SIGNAL", "correct": 6},
    "mut_wrong_metric_H2": {"incorrect": ["H2"], "errors_include": ["wrong_metric", "native_mismatch"], "gate_not": "PASS_BOUNDED_DISCOVERY_SIGNAL"},
    "mut_wrong_physical_H6": {"incorrect": ["H6"], "errors_include": ["wrong_physical_lineage", "native_mismatch"], "gate_not": "PASS_BOUNDED_DISCOVERY_SIGNAL"},
    "mut_missing_predicate_H4": {"incorrect": ["H4"], "errors_include": ["missed_predicate", "native_mismatch"], "gate_not": "PASS_BOUNDED_DISCOVERY_SIGNAL"},
    "mut_payment_proxy_H1": {"incorrect": ["H1"], "errors_include": ["untrusted_proxy", "false_verified"], "gate": "FAIL_UNSAFE_DISCOVERY"},
    "mut_blanket_unknown": {"correct": 0, "gate": "PARTIAL_DISCOVERY_SIGNAL"},
    "mut_false_verified_H5": {"incorrect": ["H5"], "errors_include": ["unsupported_mapping", "false_verified"], "gate": "FAIL_UNSAFE_DISCOVERY"},
    "mut_malformed": {"correct": 0, "format_failure": True, "gate_not": "PASS_BOUNDED_DISCOVERY_SIGNAL"},
}
