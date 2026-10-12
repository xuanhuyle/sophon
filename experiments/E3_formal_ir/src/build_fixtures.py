"""Build the frozen E3 fixtures (run once, BEFORE the validator exists; output committed in the freeze commit).

    .upstream/.venv/bin/python src/build_fixtures.py --upstream .upstream

Writes cases/: the LAB_AUTHORED governing source, the LAB_SIMULATED roster, the lab fact registry, four IR records
(S1-S4), approval/revocation objects, SCENARIOS.json (inputs + frozen expected outcomes), RECEIPT_PLAN.json (native
queries to execute after the freeze), ORACLE_EXPECTED.json (independent raw-CSV oracles, reused unmodified from the
erratum and E2) and UNTYPED_BASELINE.json. Nothing here executes MetricFlow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

E3 = Path(__file__).resolve().parents[1]
EXP = E3.parent
CASES = E3 / "cases"

SOURCE_ID = "LAB-REV-POLICY"
SOURCE_PATH = "cases/sources/LAB_REVENUE_POLICY.md"
CLAUSES = {
    "S1": "Report, for each calendar year of order date, the revenue from completed orders, counting only order lines "
          "whose charged unit price is at least 100.",
    "S2": "Report, for each calendar year of order date, the revenue from completed orders that is attributable to the "
          "French market.",
    "S3": "Report, for each calendar year of order date, the number of distinct orders placed through the online "
          "channel by customers whose country of residence is France, regardless of order status.",
    "S4": "Report, for each calendar year of order date, the revenue from completed orders whose payment has been "
          "independently confirmed as settled by a payment processor.",
}
OBSERVED_AT = "2026-10-01T09:00:00Z"
EFFECTIVE_FROM = "2024-01-01"
# lab clock (LAB_SIMULATED times)
T_PRE_SOURCE, T1, TA, T3, TR, T5 = ("2026-09-30T00:00:00Z", "2026-10-03T00:00:00Z", "2026-10-05T10:00:00Z",
                                     "2026-10-06T00:00:00Z", "2026-10-08T10:00:00Z", "2026-10-09T00:00:00Z")
EFF = "2026-06-30"

DERIVED_WHERE = ("{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }}")
STATUS = "{{ Dimension('sales__status') }} = 'completed'"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def dump(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def source_text() -> str:
    head = ("# LAB revenue reporting policy (LAB_AUTHORED for Sophon E3; not a real policy)\n\n"
            "Each clause is identified as [clause_id vVERSION]. Provenance: LAB_AUTHORED by the E3 orchestrator.\n\n")
    return head + "".join(f"[{cid} v1] {txt}\n\n" for cid, txt in CLAUSES.items())


def span(text: str, sub: str) -> list[int]:
    i = text.index(sub)
    return [i, i + len(sub)]


def atom(cid: str, atom_id: str, sub: str, **kw) -> dict:
    return {"atom_id": atom_id, "span": span(CLAUSES[cid], sub), "text": sub, **kw}


YEAR = lambda cid: atom(cid, "year", "calendar year of order date", kind="GROUP_BY", fact_kind="order_date",  # noqa: E731
                        period="CALENDAR_YEAR")
AMOUNT = lambda cid: atom(cid, "amount", "revenue", kind="MEASURE", fact_kind="order_line_amount",  # noqa: E731
                          aggregation="SUM", unit="CURRENCY")
COMPLETED = lambda cid: atom(cid, "completed", "completed orders", kind="PREDICATE", fact_kind="order_status_label",  # noqa: E731
                             op="EQ", value="completed", unit=None)

B_YEAR = {"kind": "DIRECT", "semantic_object": {"type": "time_dimension", "name": "metric_time__year"},
          "physical_lineage": ["gold.fact_sales.order_date", "silver.stg_orders.order_date", "bronze.orders.order_date"]}
B_AMOUNT = {"kind": "DIRECT", "semantic_object": {"type": "metric", "name": "revenue"},
            "physical_lineage": ["gold.fact_sales.revenue", "silver.stg_order_items.quantity", "silver.stg_order_items.unit_price"]}
B_STATUS = {"kind": "DIRECT", "semantic_object": {"type": "dimension", "name": "sales__status"},
            "physical_lineage": ["gold.fact_sales.status", "silver.stg_orders.status", "bronze.orders.status"]}


def governing(cid: str, src_sha: str) -> dict:
    return {"source_id": SOURCE_ID, "path": SOURCE_PATH, "content_sha256": src_sha, "clause_id": cid,
            "clause_version": 1, "observed_at": OBSERVED_AT, "effective_from": EFFECTIVE_FROM, "effective_to": None,
            "provenance": "LAB_AUTHORED"}


def record(cid: str, src_sha: str, revision: dict, atoms: list, readings: list, open_questions: list,
           claimed_state: str, lab_assumptions: list) -> dict:
    return {
        "ir_version": "E3-IR-0.1", "record_id": cid, "proposed_by_role": "LLM_PROPOSER",
        "governing_source": governing(cid, src_sha),
        "requirement": {"text": CLAUSES[cid], "atoms": atoms, "population": "order lines of the pinned estate",
                        "exceptions": []},
        "interpretation": {"claimed_state": claimed_state, "claimed_approval_ids": [], "readings": readings,
                           "open_questions": open_questions},
        "lab_assumptions": lab_assumptions,
        "verification_request": revision,
    }


def build(upstream: Path) -> None:
    src = source_text()
    (CASES / "sources").mkdir(parents=True, exist_ok=True)
    (E3 / SOURCE_PATH).write_text(src, encoding="utf-8")
    src_sha = sha(src.encode("utf-8"))

    rb = json.loads((E3 / "runs" / "e0_rebuild" / "run_receipt.json").read_text())
    revision = {"semantic_manifest_sha256": rb["fingerprints_final"]["semantic_manifest_sha256"],
                "raw_csv_sha256": {k: v["sha256"] for k, v in sorted(rb["S1_csv"].items())}}
    currency = "Currency is not declared anywhere in the pinned estate; all amounts are taken as one unspecified currency (ASSUMED)."

    roster = {"provenance": "LAB_SIMULATED", "note": "Roles only; no real people, signatures or identity verification.",
              "roles": {
                  "LAB_REVENUE_POLICY_OWNER": {"may_approve": ["INTERPRETATION_CHOICE"], "source_ids": [SOURCE_ID]},
                  "LAB_CUSTOMER_DATA_STEWARD": {"may_approve": ["SEMANTIC_EQUIVALENCE"], "field_prefixes": ["gold.dim_customers."]},
                  "LAB_ORDER_DATA_STEWARD": {"may_approve": ["SEMANTIC_EQUIVALENCE"], "field_prefixes": ["gold.fact_sales."]}},
              "never_approvers": ["LLM_PROPOSER"]}
    dump(CASES / "roster.json", roster)

    registry = {
        "provenance": "LAB designation from reading the pinned upstream generator, loader and dbt models (extends E1 FROZEN_CASES authority_registry)",
        "field_origins": {
            "gold.fact_sales.revenue": "ORDER_LINE", "gold.fact_sales.quantity": "ORDER_LINE", "gold.fact_sales.unit_price": "ORDER_LINE",
            "gold.fact_sales.status": "ORDER_SYSTEM", "gold.fact_sales.order_date": "ORDER_SYSTEM", "gold.fact_sales.channel": "ORDER_SYSTEM",
            "gold.fact_sales.order_id": "ORDER_SYSTEM",
            "gold.dim_customers.country": "CUSTOMER_MASTER", "gold.dim_customers.email": "CUSTOMER_MASTER",
            "gold.dim_stores.country": "STORE_MASTER"},
        "fact_kinds": {
            "order_line_amount": {"required_origin": "ORDER_LINE", "designated_fields": ["gold.fact_sales.revenue"]},
            "order_line_charged_unit_price": {"required_origin": "ORDER_LINE", "designated_fields": ["gold.fact_sales.unit_price"]},
            "order_status_label": {"required_origin": "ORDER_SYSTEM", "designated_fields": ["gold.fact_sales.status"]},
            "order_date": {"required_origin": "ORDER_SYSTEM", "designated_fields": ["gold.fact_sales.order_date"]},
            "sales_channel": {"required_origin": "ORDER_SYSTEM", "designated_fields": ["gold.fact_sales.channel"]},
            "distinct_order": {"required_origin": "ORDER_SYSTEM", "designated_fields": ["gold.fact_sales.order_id"]},
            "customer_country_attribute": {"required_origin": "CUSTOMER_MASTER", "designated_fields": ["gold.dim_customers.country"]},
            "store_country_attribute": {"required_origin": "STORE_MASTER", "designated_fields": ["gold.dim_stores.country"]},
            "customer_residence_country": {"required_origin": "CUSTOMER_MASTER", "designated_fields": [],
                                           "note": "upstream column is just `country`; residence meaning not documented"},
            "payment_settlement_confirmation": {"required_origin": "EXTERNAL_PAYMENT_PROCESSOR", "designated_fields": []}},
        "metric_units": {"revenue": "CURRENCY", "quantity_sold": "UNIT", "orders": "COUNT", "completed_revenue": "CURRENCY"},
        "derivation_patterns": {
            "LINE_GRAIN_RATIO_THRESHOLD": {
                "where_template": "{{ Metric('<numerator>', group_by=['<line_entity>']) }} >= <threshold> * {{ Metric('<denominator>', group_by=['<line_entity>']) }}",
                "required_guards": ["quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison"],
                "line_entity_rule": "primary entity of the semantic model that defines both measures",
                "proof": "experiments/E1_expressibility_erratum/ERRATUM.md section 2"}},
    }
    dump(CASES / "fact_registry.json", registry)

    # ---------------------------------------------------------------- records
    s1 = record("S1", src_sha, revision, [YEAR("S1"), AMOUNT("S1"), COMPLETED("S1"),
                atom("S1", "unit_price_threshold", "charged unit price is at least 100", kind="PREDICATE",
                     fact_kind="order_line_charged_unit_price", op="GE", value="100", unit="CURRENCY_PER_UNIT", grain="ORDER_LINE")],
                [{"reading_id": "R_SINGLE", "statement": "Sum of line revenue for completed orders over lines with charged unit price >= 100, by calendar year of order date.",
                  "bindings": {"year": B_YEAR, "amount": B_AMOUNT, "completed": B_STATUS,
                               "unit_price_threshold": {"kind": "DERIVED", "semantic_object": None,
                                                        "physical_lineage": ["gold.fact_sales.unit_price", "silver.stg_order_items.unit_price", "bronze.order_items.unit_price"],
                                                        "derivation": {"pattern": "LINE_GRAIN_RATIO_THRESHOLD", "numerator_metric": "revenue",
                                                                       "denominator_metric": "quantity_sold", "line_entity": "sales", "threshold": "100",
                                                                       "guards_declared": ["quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison"],
                                                                       "guard_receipt_id": "GR_S1"}}},
                  "native_query": {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, DERIVED_WHERE]},
                  "native_receipt_id": "NR_S1", "oracle_id": "OR_S1"}],
                [], "PROPOSED", [currency, "unit_price derivation valid only while every line has quantity > 0 (data guard, not enforced by the semantic layer)"])
    s2_readings = []
    for rid, dim, field, fk, oracle in (("R_CUSTOMER_COUNTRY", "customer__country", "gold.dim_customers.country", "customer_country_attribute", "OR_S2_CUSTOMER"),
                                        ("R_STORE_COUNTRY", "store__store_country", "gold.dim_stores.country", "store_country_attribute", "OR_S2_STORE")):
        where = f"{{{{ Dimension('{dim}') }}}} = 'France'"
        s2_readings.append({"reading_id": rid, "statement": f"French market = {dim} is France",
                            "atom_fact_kinds": {"french_market": fk},
                            "bindings": {"year": B_YEAR, "amount": B_AMOUNT, "completed": B_STATUS,
                                         "french_market": {"kind": "DIRECT", "semantic_object": {"type": "dimension", "name": dim},
                                                           "physical_lineage": [field]}},
                            "native_query": {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, where]},
                            "native_receipt_id": "NR_S2_CUSTOMER" if rid == "R_CUSTOMER_COUNTRY" else "NR_S2_STORE",
                            "oracle_id": oracle})
    s2 = record("S2", src_sha, revision, [YEAR("S2"), AMOUNT("S2"), COMPLETED("S2"),
                atom("S2", "french_market", "attributable to the French market", kind="PREDICATE", fact_kind=None,
                     op="EQ", value="France", unit=None)],
                s2_readings, ["Does 'French market' mean the customer's country or the country of the store the order is booked to?"],
                "UNRESOLVED_INTERPRETATION", [currency])
    s3 = record("S3", src_sha, revision, [YEAR("S3"),
                atom("S3", "distinct_orders", "number of distinct orders", kind="MEASURE", fact_kind="distinct_order", aggregation="COUNT_DISTINCT", unit="COUNT"),
                atom("S3", "online", "online channel", kind="PREDICATE", fact_kind="sales_channel", op="EQ", value="online", unit=None),
                atom("S3", "residence_france", "country of residence is France", kind="PREDICATE", fact_kind="customer_residence_country", op="EQ", value="France", unit=None)],
                [{"reading_id": "R_SINGLE", "statement": "Distinct online orders whose customer's residence country is France, any status, by year.",
                  "bindings": {"year": B_YEAR,
                               "distinct_orders": {"kind": "DIRECT", "semantic_object": {"type": "metric", "name": "orders"},
                                                   "physical_lineage": ["gold.fact_sales.order_id"]},
                               "online": {"kind": "DIRECT", "semantic_object": {"type": "dimension", "name": "sales__channel"},
                                          "physical_lineage": ["gold.fact_sales.channel", "silver.stg_orders.channel", "bronze.orders.channel"]},
                               "residence_france": {"kind": "CANDIDATE_EQUIVALENCE", "semantic_object": {"type": "dimension", "name": "customer__country"},
                                                    "physical_lineage": ["gold.dim_customers.country", "silver.stg_customers.country", "bronze.customers.country"],
                                                    "equivalence": {"field": "gold.dim_customers.country", "fact_kind": "customer_residence_country",
                                                                    "statement": "customers.country denotes the customer's country of residence",
                                                                    "claimed_approval_id": None}}},
                  "native_query": {"metric": "orders", "group_by": ["metric_time__year"],
                                   "where": ["{{ Dimension('sales__channel') }} = 'online'", "{{ Dimension('customer__country') }} = 'France'"]},
                  "native_receipt_id": "NR_S3", "oracle_id": "OR_S3"}],
                ["Is customers.country the country of residence?"], "PROPOSED", [])
    s4 = record("S4", src_sha, revision, [YEAR("S4"), AMOUNT("S4"), COMPLETED("S4"),
                atom("S4", "settled_by_processor", "independently confirmed as settled by a payment processor", kind="PREDICATE",
                     fact_kind="payment_settlement_confirmation", op="IS_TRUE", value=None, unit=None)],
                [{"reading_id": "R_SINGLE", "statement": "Completed-order revenue restricted to orders with an independent payment-processor settlement record.",
                  "bindings": {"year": B_YEAR, "amount": B_AMOUNT, "completed": B_STATUS,
                               "settled_by_processor": {"kind": "MISSING", "semantic_object": None, "physical_lineage": [],
                                                        "missing_fact": "payment_settlement_confirmation"}},
                  "native_query": None, "native_receipt_id": None, "oracle_id": None}],
                [], "PROPOSED", [currency])
    for r in (s1, s2, s3, s4):
        dump(CASES / "records" / f"{r['record_id']}.json", r)

    # ---------------------------------------------------------------- approvals and revocations (all LAB_SIMULATED)
    def ap(aid, role, claim, clause, known=TA, version=1, src=src_sha, eff_from="2024-01-01", eff_to=None):
        return {"approval_id": aid, "provenance": "LAB_SIMULATED", "approver_role": role, "claim": claim,
                "scope": {"source_id": SOURCE_ID, "source_sha256": src, "clause_id": clause, "clause_version": version},
                "known_at": known, "effective_from": eff_from, "effective_to": eff_to}
    choice = lambda rec, rid: {"kind": "INTERPRETATION_CHOICE", "record_id": rec, "reading_id": rid}  # noqa: E731
    eq_res = {"kind": "SEMANTIC_EQUIVALENCE", "record_id": "S3", "fact_kind": "customer_residence_country",
              "field": "gold.dim_customers.country", "statement": "customers.country denotes the customer's country of residence"}
    eq_proxy = {"kind": "SEMANTIC_EQUIVALENCE", "record_id": "S4", "fact_kind": "payment_settlement_confirmation",
                "field": "gold.fact_sales.status", "statement": "status = 'completed' means settled by a payment processor"}
    OWNER, CUST, ORD = "LAB_REVENUE_POLICY_OWNER", "LAB_CUSTOMER_DATA_STEWARD", "LAB_ORDER_DATA_STEWARD"
    altered = sha((src + " ").encode())
    approvals = [
        ap("AP_S1_READ", OWNER, choice("S1", "R_SINGLE"), "S1"),
        ap("AP_S2_CUSTOMER", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S2"),
        ap("AP_S2_STORE", OWNER, choice("S2", "R_STORE_COUNTRY"), "S2"),
        ap("AP_S3_READ", OWNER, choice("S3", "R_SINGLE"), "S3"),
        ap("AP_S3_EQ", CUST, eq_res, "S3"),
        ap("AP_S3_EQ_WRONG_STEWARD", ORD, eq_res, "S3"),
        ap("AP_S4_READ", OWNER, choice("S4", "R_SINGLE"), "S4"),
        ap("AP_S4_PROXY_EQ", ORD, eq_proxy, "S4"),
        ap("AP_S2_WRONG_CLAUSE", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S3"),
        ap("AP_S2_WRONG_VERSION", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S2", version=2),
        ap("AP_S2_WRONG_HASH", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S2", src=altered),
        ap("AP_S2_BAD_READING", OWNER, choice("S2", "R_EUROZONE"), "S2"),
        ap("AP_S2_ROLE_UNKNOWN", "LAB_INTERN", choice("S2", "R_CUSTOMER_COUNTRY"), "S2"),
        ap("AP_S2_ROLE_UNAUTHORIZED", CUST, choice("S2", "R_CUSTOMER_COUNTRY"), "S2"),
        ap("AP_S2_SELF", "LLM_PROPOSER", choice("S2", "R_CUSTOMER_COUNTRY"), "S2"),
        ap("AP_S2_FUTURE", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S2", known="2026-10-20T10:00:00Z"),
        ap("AP_S2_BEFORE_SOURCE", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S2", known="2026-09-20T10:00:00Z"),
        ap("AP_S2_NOT_EFFECTIVE", OWNER, choice("S2", "R_CUSTOMER_COUNTRY"), "S2", eff_from="2027-01-01"),
    ]
    for a in approvals:
        dump(CASES / "approvals" / f"{a['approval_id']}.json", a)
    dump(CASES / "approvals" / "RV_S3_EQ.json", {"revocation_id": "RV_S3_EQ", "provenance": "LAB_SIMULATED", "revokes": "AP_S3_EQ",
                                                "approver_role": CUST, "known_at": TR})

    # ---------------------------------------------------------------- scenarios with frozen expectations
    def sc(sid, test, rec, approvals=(), at=T3, revocations=(), patch=(), tamper=None, expect=None, note=""):
        return {"scenario_id": sid, "test": test, "record": rec, "approvals": list(approvals), "revocations": list(revocations),
                "eval_known_at": at, "eval_effective_at": EFF, "record_patch": list(patch), "receipt_tamper": tamper,
                "expected": expect, "note": note}
    V, U, NV, MISS, INV = ("VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS", "MEANING_UNRESOLVED", "NOT_VERIFIED",
                           "MISSING_REQUIRED_FACT", "STRUCTURALLY_INVALID")
    E = lambda status, *reasons, **kw: {"status": status, "reasons_include": list(reasons), **kw}  # noqa: E731
    R0 = ["interpretation", "readings", 0]
    D = R0 + ["bindings", "unit_price_threshold", "derivation"]
    S2C = ["interpretation", "readings", 0]  # R_CUSTOMER_COUNTRY
    scen = [
        # 1-2: S1
        sc("S1_T1_POSITIVE", 1, "S1", ["AP_S1_READ"], expect=E(V, selected_reading="R_SINGLE")),
        sc("S1_T1_NO_INTERPRETATION_APPROVAL", 1, "S1", [], expect=E(U, "INTERPRETATION_NOT_APPROVED", technically_executable=True)),
        sc("S1_T2_NO_GUARD_RECEIPT", 2, "S1", ["AP_S1_READ"], patch=[{"op": "set", "path": D + ["guard_receipt_id"], "value": None}],
           expect=E(NV, "GUARD_NOT_EVIDENCED")),
        sc("S1_T2_GUARD_UNDECLARED", 2, "S1", ["AP_S1_READ"],
           patch=[{"op": "set", "path": D + ["guards_declared"], "value": ["revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison"]}],
           expect=E(INV, "REQUIRED_GUARD_UNDECLARED")),
        sc("S1_T2_GRAIN_ORDER", 2, "S1", ["AP_S1_READ"],
           patch=[{"op": "set", "path": D + ["line_entity"], "value": "order"},
                  {"op": "set", "path": R0 + ["native_query", "where"], "value": [STATUS, DERIVED_WHERE.replace("['sales']", "['order']")]},
                  {"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S1_GRAIN_ORDER"}],
           expect=E(INV, "DERIVATION_GRAIN_INVALID")),
        sc("S1_T2_EXPRESSION_WITHOUT_QUANTITY", 2, "S1", ["AP_S1_READ"],
           patch=[{"op": "set", "path": R0 + ["native_query", "where"], "value": [STATUS, "{{ Metric('revenue', group_by=['sales']) }} >= 100"]},
                  {"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S1_NO_QTY"}],
           expect=E(INV, "DERIVATION_QUERY_MISMATCH")),
        sc("S1_T2_NEGATIVE_QUANTITY_SNAPSHOT", 2, "S1", ["AP_S1_READ"],
           patch=[{"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S1_NEGQTY"},
                  {"op": "set", "path": D + ["guard_receipt_id"], "value": "GR_S1_NEGQTY"}],
           expect=E(NV, "GUARD_FAILED"), note="disposable copy with two completed lines at quantity -1"),
        sc("S1_T2_GUARD_FROM_OTHER_SNAPSHOT", 2, "S1", ["AP_S1_READ"],
           patch=[{"op": "set", "path": D + ["guard_receipt_id"], "value": "GR_S1_NEGQTY"}],
           expect=E(NV, "GUARD_SNAPSHOT_MISMATCH")),
        # 3-5: S2
        sc("S2_T3_NO_APPROVAL", 3, "S2", [], expect=E(U, "INTERPRETATION_UNRESOLVED", technically_executable=True,
                                                     readings_native_equals_oracle={"R_CUSTOMER_COUNTRY": True, "R_STORE_COUNTRY": True})),
        sc("S2_T4_APPROVED_CUSTOMER", 4, "S2", ["AP_S2_CUSTOMER"],
           expect=E(V, selected_reading="R_CUSTOMER_COUNTRY", alternatives={"R_STORE_COUNTRY": "NOT_SELECTED"})),
        sc("S2_T5_WRONG_CLAUSE", 5, "S2", ["AP_S2_WRONG_CLAUSE"], expect=E(U, "APPROVAL_SCOPE_MISMATCH")),
        sc("S2_T5_WRONG_VERSION", 5, "S2", ["AP_S2_WRONG_VERSION"], expect=E(U, "APPROVAL_SCOPE_MISMATCH")),
        sc("S2_T5_WRONG_SOURCE_HASH", 5, "S2", ["AP_S2_WRONG_HASH"], expect=E(U, "APPROVAL_SCOPE_MISMATCH")),
        sc("S2_T5_NONEXISTENT_READING", 5, "S2", ["AP_S2_BAD_READING"], expect=E(U, "APPROVAL_SCOPE_MISMATCH")),
        sc("S2_T5_CONFLICTING_CHOICES", 5, "S2", ["AP_S2_CUSTOMER", "AP_S2_STORE"], expect=E(U, "CONFLICTING_APPROVALS")),
        sc("S2_T5_APPROVER_NOT_IN_ROSTER", 5, "S2", ["AP_S2_ROLE_UNKNOWN"], expect=E(U, "APPROVER_NOT_IN_ROSTER")),
        sc("S2_T5_APPROVER_NOT_AUTHORIZED", 5, "S2", ["AP_S2_ROLE_UNAUTHORIZED"], expect=E(U, "APPROVER_NOT_AUTHORIZED_FOR_CLAIM")),
        sc("S2_T5_SELF_APPROVAL", 5, "S2", ["AP_S2_SELF"], expect=E(U, "SELF_APPROVAL")),
        sc("S2_T5_APPROVAL_BEFORE_SOURCE_OBSERVED", 5, "S2", ["AP_S2_BEFORE_SOURCE"], expect=E(U, "APPROVAL_BEFORE_SOURCE_OBSERVED")),
        sc("S2_T5_APPROVAL_NOT_EFFECTIVE", 5, "S2", ["AP_S2_NOT_EFFECTIVE"], expect=E(U, "APPROVAL_NOT_EFFECTIVE")),
        sc("S2_T5_FUTURE_APPROVAL_UNCLAIMED", 5, "S2", ["AP_S2_FUTURE"], expect=E(U, "INTERPRETATION_UNRESOLVED", must_not_mention=["AP_S2_FUTURE"])),
        sc("S2_T5_FUTURE_APPROVAL_CLAIMED", 5, "S2", ["AP_S2_FUTURE"],
           patch=[{"op": "set", "path": ["interpretation", "claimed_state"], "value": "LAB_APPROVED"},
                  {"op": "set", "path": ["interpretation", "claimed_approval_ids"], "value": ["AP_S2_FUTURE"]}],
           expect=E(INV, "APPROVAL_CLAIM_WITHOUT_EVIDENCE")),
        # 6-7: S3
        sc("S3_T6_NO_EQUIVALENCE_APPROVAL", 6, "S3", ["AP_S3_READ"],
           expect=E(U, "EQUIVALENCE_UNAPPROVED", technically_executable=True, readings_native_equals_oracle={"R_SINGLE": True})),
        sc("S3_T7_EQUIVALENCE_APPROVED", 7, "S3", ["AP_S3_READ", "AP_S3_EQ"], expect=E(V, selected_reading="R_SINGLE")),
        sc("S3_T7_BEFORE_REVOCATION_KNOWN", 7, "S3", ["AP_S3_READ", "AP_S3_EQ"], revocations=["RV_S3_EQ"], at=T3,
           expect=E(V, must_not_mention=["RV_S3_EQ"])),
        sc("S3_T7_REVOKED", 7, "S3", ["AP_S3_READ", "AP_S3_EQ"], revocations=["RV_S3_EQ"], at=T5, expect=E(U, "APPROVAL_REVOKED")),
        sc("S3_T7_APPROVAL_REMOVED", 7, "S3", ["AP_S3_READ"], at=T5, expect=E(U, "EQUIVALENCE_UNAPPROVED")),
        sc("S3_T7_FLAG_FLIPPED_WITHOUT_APPROVAL", 7, "S3", ["AP_S3_READ"],
           patch=[{"op": "set", "path": R0 + ["bindings", "residence_france", "equivalence", "claimed_approval_id"], "value": "AP_S3_EQ_FAKE"}],
           expect=E(INV, "APPROVAL_CLAIM_WITHOUT_EVIDENCE")),
        sc("S3_T7_WRONG_STEWARD", 7, "S3", ["AP_S3_READ", "AP_S3_EQ_WRONG_STEWARD"], expect=E(U, "APPROVER_NOT_AUTHORIZED_FOR_CLAIM")),
        # 8: S4
        sc("S4_T8_MISSING_SETTLEMENT", 8, "S4", ["AP_S4_READ"], expect=E(MISS, "REQUIRED_FACT_ABSENT", uncovered=["settled_by_processor"])),
        sc("S4_T8_STATUS_PROXY_DIRECT", 8, "S4", ["AP_S4_READ"],
           patch=[{"op": "set", "path": R0 + ["bindings", "settled_by_processor"],
                   "value": {"kind": "DIRECT", "semantic_object": {"type": "dimension", "name": "sales__status"},
                             "physical_lineage": ["gold.fact_sales.status"], "value_override": "completed"}},
                  {"op": "set", "path": R0 + ["native_query"], "value": {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, STATUS]}},
                  {"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S4_PROXY"},
                  {"op": "set", "path": R0 + ["oracle_id"], "value": "OR_S4_PROXY"}],
           expect=E(MISS, "NOT_DESIGNATED_FOR_FACT", uncovered=["settled_by_processor"], readings_native_equals_oracle={"R_SINGLE": True})),
        sc("S4_T8_PROXY_WITH_SIMULATED_APPROVAL", 8, "S4", ["AP_S4_READ", "AP_S4_PROXY_EQ"],
           patch=[{"op": "set", "path": R0 + ["bindings", "settled_by_processor"],
                   "value": {"kind": "CANDIDATE_EQUIVALENCE", "semantic_object": {"type": "dimension", "name": "sales__status"},
                             "physical_lineage": ["gold.fact_sales.status"], "value_override": "completed",
                             "equivalence": {"field": "gold.fact_sales.status", "fact_kind": "payment_settlement_confirmation",
                                             "statement": "status = 'completed' means settled by a payment processor", "claimed_approval_id": "AP_S4_PROXY_EQ"}}},
                  {"op": "set", "path": R0 + ["native_query"], "value": {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, STATUS]}},
                  {"op": "set", "path": R0 + ["native_receipt_id"], "value": "NR_S4_PROXY"},
                  {"op": "set", "path": R0 + ["oracle_id"], "value": "OR_S4_PROXY"}],
           expect=E(MISS, "APPROVAL_CANNOT_CREATE_SOURCE", uncovered=["settled_by_processor"])),
        sc("S4_T8_STATUS_FIELD_SET_VERIFIED", 8, "S4", ["AP_S4_READ"], patch=[{"op": "set", "path": ["status"], "value": "VERIFIED"}],
           expect=E(INV, "STATUS_FIELD_FORBIDDEN")),
        # 9: structural negatives (otherwise-valid S1/S2 with their valid approvals)
        sc("S1_T9_UNIT_MISMATCH", 9, "S1", ["AP_S1_READ"],
           patch=[{"op": "set", "path": ["requirement", "atoms", 3, "unit"], "value": "UNIT"}], expect=E(INV, "UNIT_MISMATCH")),
        sc("S2_T9_UNKNOWN_SEMANTIC_OBJECT", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["bindings", "french_market", "semantic_object", "name"], "value": "customer__residence_country"}],
           expect=E(INV, "UNKNOWN_SEMANTIC_OBJECT")),
        sc("S2_T9_UNKNOWN_PHYSICAL_FIELD", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["bindings", "french_market", "physical_lineage"], "value": ["gold.dim_customers.residence"]}],
           expect=E(INV, "UNKNOWN_PHYSICAL_FIELD")),
        sc("S2_T9_SEMANTIC_PHYSICAL_MISMATCH", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["bindings", "french_market", "physical_lineage"], "value": ["gold.dim_stores.country"]}],
           expect=E(INV, "SEMANTIC_PHYSICAL_MISMATCH")),
        sc("S2_T9_UNDEFINED_PREDICATE", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["bindings", "discount"], "value": B_STATUS}], expect=E(INV, "UNDEFINED_PREDICATE")),
        sc("S2_T9_ATOM_UNBOUND", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "delete", "path": S2C + ["bindings", "completed"]}], expect=E(INV, "ATOM_UNBOUND")),
        sc("S2_T9_EFFECTIVE_ORDER", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": ["governing_source", "effective_to"], "value": "2023-12-31"}], expect=E(INV, "TEMPORAL_ORDER_INVALID")),
        sc("S2_T9_SOURCE_NOT_YET_KNOWN", 9, "S2", ["AP_S2_CUSTOMER"], at=T_PRE_SOURCE, expect=E(INV, "SOURCE_NOT_YET_KNOWN")),
        sc("S2_T9_SOURCE_HASH_ALTERED", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": ["governing_source", "content_sha256"], "value": altered}], expect=E(INV, "SOURCE_HASH_MISMATCH")),
        sc("S2_T9_SOURCE_VERSION_UNKNOWN", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": ["governing_source", "clause_version"], "value": 2}], expect=E(INV, "SOURCE_CLAUSE_MISMATCH")),
        sc("S2_T9_SPAN_TEXT_MISMATCH", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": ["requirement", "atoms", 3, "span"], "value": [10, 40]}], expect=E(INV, "SPAN_TEXT_MISMATCH")),
        sc("S2_T9_APPROVED_CLAIM_WITHOUT_IDS", 9, "S2", [],
           patch=[{"op": "set", "path": ["interpretation", "claimed_state"], "value": "LAB_APPROVED"}], expect=E(INV, "APPROVAL_CLAIM_WITHOUT_EVIDENCE")),
        sc("S2_T9_SCHEMA_INVALID_STATE", 9, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": ["interpretation", "claimed_state"], "value": "MAYBE"}], expect=E(INV, "SCHEMA_INVALID")),
        # 10: native / oracle negative controls (S2 customer reading, validly approved)
        sc("S2_T10_RECEIPT_VALUE_CHANGED_REHASHED", 10, "S2", ["AP_S2_CUSTOMER"],
           tamper={"receipt_id": "NR_S2_CUSTOMER", "mode": "ADD_ONE_CENT_FIRST_ROW_REHASH"}, expect=E(NV, "NATIVE_ORACLE_MISMATCH")),
        sc("S2_T10_RECEIPT_VALUE_CHANGED_NOT_REHASHED", 10, "S2", ["AP_S2_CUSTOMER"],
           tamper={"receipt_id": "NR_S2_CUSTOMER", "mode": "ADD_ONE_CENT_FIRST_ROW"}, expect=E(NV, "RECEIPT_INTEGRITY_FAILED")),
        sc("S2_T10_UNDERLYING_VALUE_CHANGED", 10, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["native_receipt_id"], "value": "NR_S2_CUSTOMER_VALUE_CHANGED"}],
           expect=E(NV, "NATIVE_ORACLE_MISMATCH"), note="disposable copy: one completed French-customer line's revenue +100.00"),
        sc("S2_T10_RECEIPT_FOR_OTHER_QUERY", 10, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["native_receipt_id"], "value": "NR_S2_STORE"}], expect=E(NV, "RECEIPT_QUERY_MISMATCH")),
        sc("S2_T10_ORACLE_FOR_OTHER_READING", 10, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": S2C + ["oracle_id"], "value": "OR_S2_STORE"}], expect=E(NV, "ORACLE_READING_MISMATCH")),
        sc("S2_T10_WRONG_SEMANTIC_REVISION", 10, "S2", ["AP_S2_CUSTOMER"],
           patch=[{"op": "set", "path": ["verification_request", "semantic_manifest_sha256"], "value": "0" * 64}],
           expect=E(NV, "RECEIPT_REVISION_MISMATCH")),
        # 11: no history rewriting / as-of
        sc("S2_T11_AS_OF_BEFORE_APPROVAL", 11, "S2", ["AP_S2_CUSTOMER"], at=T1,
           expect=E(U, "INTERPRETATION_UNRESOLVED", must_not_mention=["AP_S2_CUSTOMER"])),
        sc("S2_T11_AS_OF_AFTER_APPROVAL", 11, "S2", ["AP_S2_CUSTOMER"], at=T3,
           expect=E(V, selected_reading="R_CUSTOMER_COUNTRY", alternatives={"R_STORE_COUNTRY": "NOT_SELECTED"})),
    ]
    dump(CASES / "SCENARIOS.json", {"lab_clock": {"T_PRE_SOURCE": T_PRE_SOURCE, "T1": T1, "TA_approvals_known": TA, "T3": T3,
                                                  "TR_revocation_known": TR, "T5": T5, "eval_effective_at": EFF},
                                    "scenarios": scen})

    # ---------------------------------------------------------------- native receipts to collect after the freeze
    plan = {
        "NR_S1": {"snapshot": "PINNED", "query": s1["interpretation"]["readings"][0]["native_query"]},
        "NR_S1_GRAIN_ORDER": {"snapshot": "PINNED", "query": {"metric": "revenue", "group_by": ["metric_time__year"],
                                                               "where": [STATUS, DERIVED_WHERE.replace("['sales']", "['order']")]}},
        "NR_S1_NO_QTY": {"snapshot": "PINNED", "query": {"metric": "revenue", "group_by": ["metric_time__year"],
                                                          "where": [STATUS, "{{ Metric('revenue', group_by=['sales']) }} >= 100"]}},
        "NR_S1_NEGQTY": {"snapshot": "COPY_NEGATIVE_QUANTITY", "query": s1["interpretation"]["readings"][0]["native_query"]},
        "NR_S2_CUSTOMER": {"snapshot": "PINNED", "query": s2_readings[0]["native_query"]},
        "NR_S2_STORE": {"snapshot": "PINNED", "query": s2_readings[1]["native_query"]},
        "NR_S2_CUSTOMER_VALUE_CHANGED": {"snapshot": "COPY_VALUE_CHANGED", "query": s2_readings[0]["native_query"]},
        "NR_S3": {"snapshot": "PINNED", "query": s3["interpretation"]["readings"][0]["native_query"]},
        "NR_S4_PROXY": {"snapshot": "PINNED", "query": {"metric": "revenue", "group_by": ["metric_time__year"], "where": [STATUS, STATUS]}},
        "NR_PROBE_UNIT_PRICE_DIMENSION": {"snapshot": "PINNED", "expect_rejected": True,
                                          "query": {"metric": "revenue", "group_by": ["metric_time__year"],
                                                    "where": ["{{ Dimension('sales__unit_price') }} >= 100"]}},
    }
    guards = {"GR_S1": {"snapshot": "PINNED"}, "GR_S1_NEGQTY": {"snapshot": "COPY_NEGATIVE_QUANTITY"}}
    snapshots = {
        "PINNED": "the rebuilt pinned warehouse, unmodified",
        "COPY_NEGATIVE_QUANTITY": "disposable copy; the lowest-id completed line with unit_price > 100 and the lowest-id completed line with unit_price < 100 set to quantity -1, revenue = quantity * unit_price",
        "COPY_VALUE_CHANGED": "disposable copy; revenue of the lowest-id completed line of a French customer (customer__country = 'France') increased by 100.00",
    }
    dump(CASES / "RECEIPT_PLAN.json", {"native": plan, "guards": guards, "snapshots": snapshots})

    # ---------------------------------------------------------------- independent oracles (raw CSVs only; reused unmodified)
    sys.path.insert(0, str(EXP / "E1_expressibility_erratum" / "src"))
    sys.path.insert(0, str(EXP / "E2_blind_discovery" / "src"))
    import e2_oracle  # noqa: E402
    import oracle_b1  # noqa: E402
    raw = upstream / "data" / "raw"
    oracle = {
        "OR_S1": {"computes": {"record_id": "S1", "reading_id": "R_SINGLE"}, "by_year": oracle_b1.compute(raw)["by_year"],
                  "code": "experiments/E1_expressibility_erratum/src/oracle_b1.py"},
        "OR_S2_CUSTOMER": {"computes": {"record_id": "S2", "reading_id": "R_CUSTOMER_COUNTRY"},
                           "by_year": e2_oracle.DIAGNOSTICS["H3_reading_customer_country"](raw), "code": "experiments/E2_blind_discovery/src/e2_oracle.py"},
        "OR_S2_STORE": {"computes": {"record_id": "S2", "reading_id": "R_STORE_COUNTRY"},
                        "by_year": e2_oracle.DIAGNOSTICS["H3_reading_store_country"](raw), "code": "experiments/E2_blind_discovery/src/e2_oracle.py"},
        "OR_S3": {"computes": {"record_id": "S3", "reading_id": "R_SINGLE"}, "by_year": e2_oracle.h6(raw),
                  "code": "experiments/E2_blind_discovery/src/e2_oracle.py"},
        "OR_S4_PROXY": {"computes": {"record_id": "S4", "reading_id": "R_SINGLE"}, "binding_variant": "STATUS_PROXY_ONLY",
                        "by_year": e2_oracle.DIAGNOSTICS["H1_rejected_status_proxy"](raw), "code": "experiments/E2_blind_discovery/src/e2_oracle.py"},
    }
    code_sha = {p: sha((EXP.parent / p).read_bytes()) for p in sorted({o["code"] for o in oracle.values()})}
    dump(CASES / "ORACLE_EXPECTED.json", {"label": "INDEPENDENT ORACLE: stdlib Decimal over the pinned raw CSVs; no warehouse, no MetricFlow",
                                          "raw_csv_sha256": revision["raw_csv_sha256"], "code_sha256": code_sha, "oracles": oracle})

    # ---------------------------------------------------------------- untyped baseline (states a plain JSON store accepts)
    dump(CASES / "UNTYPED_BASELINE.json", {
        "rule": "A plain JSON note store (json.loads only) read naively: a stored status field is taken as the status; otherwise a requirement is 'verified' when its recorded native query executed and its recorded numbers match a recorded expected value.",
        "cases": [
            {"id": "U1", "e3_scenario": "S2_T3_NO_APPROVAL", "false_state": "metric executed => requirement verified (both French-market readings execute and match their oracles)"},
            {"id": "U2", "e3_scenario": "S3_T7_FLAG_FLIPPED_WITHOUT_APPROVAL", "false_state": "approval flag set without an approval object => equivalence approved"},
            {"id": "U3", "e3_scenario": "S2_T10_WRONG_SEMANTIC_REVISION", "false_state": "receipt from a different semantic revision => verified"},
            {"id": "U4", "e3_scenario": "S4_T8_STATUS_PROXY_DIRECT", "false_state": "status proxy executes and matches its own oracle => settlement verified"},
            {"id": "U5", "e3_scenario": "S2_T5_WRONG_VERSION", "false_state": "approval of another clause version => approved"},
            {"id": "U6", "e3_scenario": "S1_T2_NEGATIVE_QUANTITY_SNAPSHOT", "false_state": "derived expression executes => unit-price threshold verified despite quantity <= 0 rows"},
            {"id": "U7", "e3_scenario": "S4_T8_STATUS_FIELD_SET_VERIFIED", "false_state": "status: VERIFIED written into the record => verified"},
        ]})
    print("fixtures written; source sha256", src_sha)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    build(Path(ap.parse_args().upstream).resolve())
