"""Write the frozen E4 candidates and variant list (run before the freeze).

  candidates/<ID>.json   the implementation under inspection: policy, predecessor (change_of), text patch to the
                         pinned dbt/MetricFlow project, and the native query that implements the policy
  VARIANTS.json          variant -> candidate, snapshots, authority/time context, optional candidate claim, and the
                         FROZEN EXPECTED classification (read only by the independent scorer, never by the checker)

    python3 src/build_variants.py
"""
from __future__ import annotations

import json
from pathlib import Path

E4 = Path(__file__).resolve().parents[1]
SEM = "dbt/retail_dwh/models/marts/semantic/_semantic_models.yml"
MET = "dbt/retail_dwh/models/marts/semantic/_metrics.yml"
FACT = "dbt/retail_dwh/models/marts/facts/fact_sales.sql"
STG_C = "dbt/retail_dwh/models/staging/stg_customers.sql"
STATUS = "{{ Dimension('sales__status') }} = 'completed'"
DERIVED = "{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }}"
YEAR = ["metric_time__year"]

EXPOSE_UNIT_PRICE = {"op": "replace", "file": SEM,
                     "old": "      - name: status\n        type: categorical\n    measures:\n      - name: revenue\n        description: \"Quantity x price charged.\"\n",
                     "new": "      - name: status\n        type: categorical\n      - name: unit_price\n        type: categorical\n        expr: unit_price\n"
                            "    measures:\n      - name: revenue\n        description: \"Quantity x price charged.\"\n"}


def metric(name: str, flt: str, label: str, desc: str) -> dict:
    return {"op": "append", "file": MET, "text": f"\n  - name: {name}\n    description: \"{desc}\"\n    label: \"{label}\"\n"
                                                 f"    type: simple\n    type_params:\n      measure: revenue\n    filter: \"{flt}\"\n"}


def cand(cid, policy, change_of, patch, q_metric, where, note):
    return {"candidate_id": cid, "policy": policy, "change_of": change_of, "patch": patch,
            "query": {"metric": q_metric, "group_by": YEAR, "where": where}, "note": note}


P1M, P2M = "premium_completed_revenue", "french_market_revenue"
CANDIDATES = [
    cand("M1", "P1", None, [], "revenue", [STATUS, DERIVED],
         "approved line-grain derivation on the pristine semantic layer (E3 S1 native query)"),
    cand("M6B", "P1", "M1", [EXPOSE_UNIT_PRICE, metric(P1M, f"{STATUS} AND {{{{ Dimension('sales__unit_price') }}}} >= 100",
                                                       "Premium completed revenue", "Completed revenue on lines with unit price at least 100.")],
         P1M, [], "harmless alternative: expose unit_price as a dimension and define a metric with >= 100"),
    cand("M3", "P1", "M6B", [EXPOSE_UNIT_PRICE, metric(P1M, f"{STATUS} AND {{{{ Dimension('sales__unit_price') }}}} > 100",
                                                       "Premium completed revenue", "Completed revenue on lines with unit price above 100.")],
         P1M, [], "WRONG boundary: > 100 instead of >= 100 (native semantic YAML mutation)"),
    cand("M4", "P1", "M6B", [EXPOSE_UNIT_PRICE, metric(P1M, "{{ Dimension('sales__status') }} != 'cancelled' AND {{ Dimension('sales__unit_price') }} >= 100",
                                                       "Premium completed revenue", "Non-cancelled revenue on lines with unit price at least 100.")],
         P1M, [], "WRONG status filter: != 'cancelled' instead of = 'completed' (native semantic YAML mutation)"),
    cand("M2", "P2", None, [metric(P2M, f"{STATUS} AND {{{{ Dimension('customer__country') }}}} = 'France'",
                                   "French market revenue", "Completed revenue of customers in France.")],
         P2M, [], "baseline native metric for the approved customer-country reading"),
    cand("M5", "P2", "M2", [metric(P2M, f"{STATUS} AND {{{{ Dimension('store__store_country') }}}} = 'France'",
                                   "French market revenue", "Completed revenue of stores in France.")],
         P2M, [], "WRONG binding: store country instead of customer country (native semantic YAML mutation)"),
    cand("M5B", "P2", "M2", [metric(P2M, f"{STATUS} AND {{{{ Dimension('customer__country') }}}} = 'France'",
                                    "French market revenue", "Completed revenue of customers in France."),
                             {"op": "replace", "file": STG_C, "old": "        when 'FR'          then 'France'\n        when 'FRA'         then 'France'\n", "new": ""}],
         P2M, [], "WRONG dbt model: stg_customers drops the FR/FRA country aliases (dbt SQL mutation; metric unchanged)"),
    cand("M6", "P2", "M2", [metric(P2M, "{{ Dimension('customer__country') }} IN ('France') AND {{ Dimension('sales__status') }} IN ('completed')",
                                   "French market revenue (customer country)", "Refactored: revenue of completed orders whose customer country is France."),
                            {"op": "replace", "file": FACT, "old": "-- Gold fact: one row per order line (the grain).",
                             "new": "-- Gold fact: one row per order line (the grain).\n-- (E4 M6: comment-only refactor; no behaviour change intended)"}],
         P2M, [], "harmless refactor of M2: reordered IN-filters, new label/description, comment-only dbt model edit"),
    cand("C4", "P2", "M2", [metric(P2M, f"{STATUS} AND {{{{ Dimension('customer__residence_country') }}}} = 'France'",
                                   "French market revenue", "Refers to a dimension that does not exist.")],
         P2M, [], "broken candidate: filter references a nonexistent dimension"),
]

OK = {"P1": {"approvals": ["AP_S1_READ"], "record": "S1"}, "P2": {"approvals": ["AP_S2_CUSTOMER"], "record": "S2"}}
DEFAULT_CTX = {"eval_known_at": "2026-10-06T00:00:00Z", "eval_effective_at": "2026-06-30", "record_patch": []}
SNAPS = {"P1": ["PINNED", "BOUNDARY"], "P2": ["PINNED"]}


def variant(vid, cid, expected, snapshots=None, ctx=None, claim=None, kind="", must=None, extra=None):
    c = next(x for x in CANDIDATES if x["candidate_id"] == cid)
    context = {**DEFAULT_CTX, **OK[c["policy"]], **(ctx or {})}
    return {"variant_id": vid, "candidate": cid, "policy": c["policy"], "snapshots": snapshots or SNAPS[c["policy"]],
            "context": context, "candidate_claim": claim, "kind": kind,
            "expected": {"status": expected, "reasons_include": must or [], **(extra or {})}}


def variants() -> list[dict]:
    V, ND, NC, NV, NA = ("VERIFIED_FOR_LAB_CHECKS", "NO_MATERIAL_DRIFT_FOR_CHECKS", "NONCONFORMING_IMPLEMENTATION",
                         "NOT_VERIFIED", "NOT_APPLICABLE")
    return [
        variant("M1", "M1", V, kind="correct baseline P1 (derived)"),
        variant("M2", "M2", V, kind="correct baseline P2 (native metric)"),
        variant("M6B", "M6B", ND, kind="harmless alternative P1 (semantic YAML change)"),
        variant("M6", "M6", ND, kind="harmless refactor P2 (YAML + dbt comment)"),
        variant("M3", "M3", NC, kind="wrong boundary, accidental agreement on PINNED", must=["MEMBERSHIP_MISMATCH"],
                extra={"counterexample_ids": ["2"], "agrees_on_snapshot": "PINNED", "differs_on_snapshot": "BOUNDARY", "native_mutation": True}),
        variant("M4", "M4", NC, kind="wrong status filter", must=["MEMBERSHIP_MISMATCH"], extra={"native_mutation": True}),
        variant("M5", "M5", NC, kind="wrong customer/store binding", must=["MEMBERSHIP_MISMATCH"], extra={"native_mutation": True}),
        variant("M5B", "M5B", NC, kind="wrong dbt staging model", must=["MEMBERSHIP_MISMATCH"], extra={"native_mutation": True}),
        variant("C1", "M2", NV, snapshots=["STALE"], kind="unregistered/stale source snapshot", must=["SOURCE_SNAPSHOT_UNREGISTERED"]),
        variant("C2A", "M2", NV, ctx={"approvals": []}, kind="approval absent; correct implementation", must=["APPROVAL_MISSING"]),
        variant("C2B", "M2", NA, ctx={"record_patch": [{"op": "set", "path": ["governing_source", "effective_from"], "value": "2027-01-01"}]},
                kind="requirement not in force at the evaluated date", must=["REQUIREMENT_NOT_IN_FORCE"]),
        variant("C3", "M5", NC, claim={"by_year": {"2024": "310780.14", "2025": "261972.06", "2026": "155221.02"},
                                       "status": "VERIFIED", "note": "forged candidate receipt claiming the approved customer values"},
                kind="poisoned candidate claim on a wrong implementation", must=["MEMBERSHIP_MISMATCH", "CANDIDATE_CLAIM_CONTRADICTED"]),
        variant("C4", "C4", NV, kind="candidate fails to execute natively", must=["EXECUTION_FAILURE"]),
        variant("C5", "M1", NV, snapshots=["NEGQTY"], kind="derived implementation on data violating its guard", must=["DATA_GUARD_FAILURE"]),
    ]


def main() -> int:
    (E4 / "candidates").mkdir(exist_ok=True)
    for c in CANDIDATES:
        (E4 / "candidates" / f"{c['candidate_id']}.json").write_text(json.dumps(c, indent=1) + "\n", encoding="utf-8")
    vs = variants()
    (E4 / "VARIANTS.json").write_text(json.dumps({"variants": vs}, indent=1) + "\n", encoding="utf-8")
    print(len(CANDIDATES), "candidates,", len(vs), "variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
