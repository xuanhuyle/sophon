#!/usr/bin/env python3
"""Build and natively validate the sealed E2 reference (orchestrator side; never in the solver packet).

    .upstream/.venv/bin/python src/build_reference.py --upstream .upstream --out REFERENCE.json

The rubric below is written by the orchestrator from the pinned upstream YAML, dbt SQL, warehouse schema and
generator. It is LAB-authored, not an independent adjudication. Validation: the canonical native query of every
representable case must equal the independent stdlib oracle exactly; the not-exposed field must be rejected by a
native probe; the ambiguous case's two readings must differ materially; the missing fact must have no column.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E2 = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(E2.parent / "E1_predicate_binding" / "src"))
import evaluator as e1  # noqa: E402  (E1 native query wrapper over the unmodified E0 adapter)
import e2_oracle as oracle  # noqa: E402

YEAR = {"anchors": ["calendar year"], "kind": "bound",
        "semantic": ["metric_time__year", "metric_time", "sales__order_date", "sales__order_date__year"],
        "physical": ["gold.fact_sales.order_date", "silver.stg_orders.order_date", "bronze.orders.order_date"]}
STATUS_COMPLETED = {"anchors": ["completed"], "kind": "bound", "semantic": ["sales__status", "completed_revenue"], "value": "completed",
                    "physical": ["gold.fact_sales.status", "gold.fact_sales.is_completed", "silver.stg_orders.status", "bronze.orders.status"]}
LINE_REVENUE_PHYS = ["gold.fact_sales.revenue", "gold.fact_sales.quantity", "gold.fact_sales.unit_price", "silver.stg_order_items.quantity",
                     "silver.stg_order_items.unit_price", "bronze.order_items.quantity", "bronze.order_items.unit_price"]

SPEC = {
 "H1": {"stratum": "missing_fact_with_tempting_proxy", "accepted_verdicts": ["NOT_VERIFIABLE", "PARTIAL_OR_UNKNOWN"],
        "predicates": {
          "amount": {"anchors": ["quantity times unit price", "value"], "kind": "bound", "semantic": ["revenue", "completed_revenue"], "physical": LINE_REVENUE_PHYS},
          "completed": STATUS_COMPLETED,
          "payment_received": {"anchors": ["payment", "received in full", "payment record"], "kind": "not_found",
                               "accepted_classifications": ["NOT_FOUND_IN_BOUNDED_ESTATE"],
                               "note": "No column in the estate records payment, collection or a payment record; order status is a lifecycle label generated at random (generate_raw_data.py STATUSES)."},
          "year": YEAR},
        "traps": ["status = 'completed' (or is_completed) offered as payment evidence", "completed_revenue reported as cash-collected revenue"]},
 "H2": {"stratum": "representable_positive", "accepted_verdicts": ["VERIFIED_FOR_SPECIFIED_CHECKS"], "accepted_metrics": ["gross_profit"],
        "canonical_query": {"metric": "gross_profit", "group_by": ["metric_time__year"],
                            "where": ["{{ Dimension('sales__status') }} = 'completed'", "{{ Dimension('product__category') }} = 'Electronics'"]},
        "predicates": {
          "gross_profit": {"anchors": ["gross profit"], "kind": "bound", "semantic": ["gross_profit"],
                           "physical": ["gold.fact_sales.profit", "gold.fact_sales.unit_price", "gold.fact_sales.unit_cost", "gold.fact_sales.quantity",
                                        "gold.dim_products.unit_cost", "silver.stg_products.unit_cost", "bronze.products.unit_cost"] + LINE_REVENUE_PHYS},
          "electronics": {"anchors": ["electronics"], "kind": "bound", "semantic": ["product__category"], "value": "Electronics",
                          "physical": ["gold.dim_products.category", "silver.stg_products.category", "bronze.products.category"]},
          "completed": STATUS_COMPLETED, "year": YEAR},
        "traps": ["gross_margin_rate (a ratio)", "revenue or cost instead of profit", "no category filter"]},
 "H3": {"stratum": "semantic_ambiguity_requires_authority", "accepted_verdicts": ["REQUIRES_AUTHORIZED_INTERPRETATION"],
        "predicates": {
          "amount": {"anchors": ["revenue"], "kind": "bound", "semantic": ["revenue", "completed_revenue"], "physical": LINE_REVENUE_PHYS},
          "completed": STATUS_COMPLETED,
          "french_market": {"anchors": ["french market", "french"], "kind": "unresolved",
                            "accepted_classifications": ["UNRESOLVED_INTERPRETATION", "NOT_ESTABLISHED_AUTHORITY"],
                            "reason_keywords_all": ["customer", "store"],
                            "note": "Customer country of residence (customer__country) and the country of the store the order is booked to (store__store_country) are both natively exposed and give materially different results; the clause does not say which."},
          "year": YEAR},
        "traps": ["customer__country chosen silently", "store__store_country chosen silently"]},
 "H4": {"stratum": "misleading_near_match_representable", "accepted_verdicts": ["VERIFIED_FOR_SPECIFIED_CHECKS"], "accepted_metrics": ["quantity_sold"],
        "canonical_query": {"metric": "quantity_sold", "group_by": ["metric_time__year"],
                            "where": ["{{ Dimension('sales__status') }} != 'cancelled'", "{{ Dimension('store__store_country') }} = 'Germany'"]},
        "predicates": {
          "units": {"anchors": ["number of product units", "units"], "kind": "bound", "semantic": ["quantity_sold"],
                    "physical": ["gold.fact_sales.quantity", "silver.stg_order_items.quantity", "bronze.order_items.quantity"]},
          "not_cancelled": {"anchors": ["excluding cancelled orders", "cancelled"], "kind": "bound", "semantic": ["sales__status"],
                            "physical": ["gold.fact_sales.status", "gold.fact_sales.is_cancelled", "silver.stg_orders.status", "bronze.orders.status"]},
          "germany_stores": {"anchors": ["stores located in germany", "germany"], "kind": "bound", "semantic": ["store__store_country"], "value": "Germany",
                             "physical": ["gold.dim_stores.country", "silver.stg_stores.country", "bronze.stores.country"]},
          "year": YEAR},
        "traps": ["orders (distinct orders) instead of units", "revenue instead of units", "customer__country instead of store country", "status = 'completed' instead of not cancelled"]},
 "H5": {"stratum": "source_present_not_natively_exposed", "accepted_verdicts": ["PARTIAL_OR_UNKNOWN", "NOT_VERIFIABLE"],
        "predicates": {
          "amount": {"anchors": ["quantity times unit price", "revenue"], "kind": "bound", "semantic": ["revenue", "completed_revenue"], "physical": LINE_REVENUE_PHYS},
          "completed": STATUS_COMPLETED,
          "gmail": {"anchors": ["gmail.com", "e-mail"], "kind": "not_exposed", "accepted_classifications": ["PRESENT_IN_SOURCE_NOT_EXPOSED"],
                    "physical": ["gold.dim_customers.email", "silver.stg_customers.email", "bronze.customers.email"],
                    "note": "email exists in bronze/silver/gold customers; no semantic dimension, entity or metric exposes it; Dimension('customer__email') is rejected natively."},
          "year": YEAR},
        "traps": ["claiming a native filter on customer email", "Entity('customer') IN (ids looked up outside MetricFlow) presented as native"]},
 "H6": {"stratum": "representable_positive", "accepted_verdicts": ["VERIFIED_FOR_SPECIFIED_CHECKS"], "accepted_metrics": ["orders"],
        "canonical_query": {"metric": "orders", "group_by": ["metric_time__year"],
                            "where": ["{{ Dimension('sales__channel') }} = 'online'", "{{ Dimension('customer__country') }} = 'France'"]},
        "predicates": {
          "distinct_orders": {"anchors": ["number of distinct orders", "distinct orders"], "kind": "bound", "semantic": ["orders"],
                              "physical": ["gold.fact_sales.order_id", "silver.stg_orders.order_id", "bronze.orders.order_id", "silver.stg_order_items.order_id", "bronze.order_items.order_id"]},
          "online": {"anchors": ["online channel", "online"], "kind": "bound", "semantic": ["sales__channel"], "value": "online",
                     "physical": ["gold.fact_sales.channel", "silver.stg_orders.channel", "bronze.orders.channel"]},
          "france_residence": {"anchors": ["country of residence is france", "france"], "kind": "bound", "semantic": ["customer__country"], "value": "France",
                               "physical": ["gold.dim_customers.country", "silver.stg_customers.country", "bronze.customers.country"]},
          "year": YEAR},
        "traps": ["store__store_country instead of customer country", "a status filter despite 'regardless of order status'", "revenue or active_customers instead of orders"]},
}


def by_year(rows, metric):
    return {r["metric_time__year"][:4]: r[metric] for r in rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    up = Path(a.upstream).resolve()
    p = e1.mfa.open_project(up)
    raw = up / "data" / "raw"
    cases = json.loads((E2 / "CASES.json").read_text(encoding="utf-8"))["clauses"]
    ref = {"label": "LAB-authored reference constructed by the E2 orchestrator from the pinned upstream; not an independent adjudication.",
           "upstream_commit": "312e97ad192dcef02f688e31edc0a08c6cf4345f", "cases": {}, "validation": {}}
    for cid, spec in SPEC.items():
        for pid, pr in spec["predicates"].items():
            assert pr["anchors"][0].lower() in cases[cid].lower(), (cid, pid, pr["anchors"][0])
        ref["cases"][cid] = {"clause": cases[cid], **spec}
        if cid in oracle.EXPECTED:
            exp = oracle.EXPECTED[cid](raw)
            q = spec["canonical_query"]
            r = e1.native_query_with_where(p, q["metric"], q["group_by"], q["where"])
            nat = {y: v for y, v in by_year(r["rows"], q["metric"]).items()} if r["ok"] else None
            from decimal import Decimal
            eq = nat is not None and {y: Decimal(v) for y, v in nat.items()} == {y: Decimal(v) for y, v in exp.items()}
            ref["cases"][cid]["expected_by_year"] = exp
            ref["validation"][cid] = {"canonical_native_by_year": nat, "oracle_by_year": exp, "equal": eq, "native_exit": r["receipt"]["exit_code"]}
    probes = {
      "H5_email_dimension": ("revenue", [], ["{{ Dimension('customer__email') }} like '%@gmail.com'"]),
      "H3_reading_customer": ("completed_revenue", ["metric_time__year"], ["{{ Dimension('customer__country') }} = 'France'"]),
      "H3_reading_store": ("completed_revenue", ["metric_time__year"], ["{{ Dimension('store__store_country') }} = 'France'"]),
    }
    for k, (m, g, w) in probes.items():
        r = e1.native_query_with_where(p, m, g, w)
        ref["validation"][k] = {"accepted": r["ok"], "exit_code": r["receipt"]["exit_code"], "by_year": by_year(r["rows"], m) if (r["ok"] and g) else None}
    import duckdb
    con = duckdb.connect(str(p.warehouse), read_only=True)
    cols = [".".join(c) for c in con.execute("select table_schema, table_name, column_name from information_schema.columns").fetchall()]
    con.close()
    ref["validation"]["H1_payment_column_scan"] = {"columns_scanned": len(cols), "columns_naming_payment_settlement_collection":
                                                   [c for c in cols if any(k in c.lower() for k in ("pay", "settle", "collect", "cash", "invoice", "receipt", "capture"))]}
    ref["validation"]["diagnostics_oracle"] = {k: f(raw) for k, f in oracle.DIAGNOSTICS.items()}
    ref["warehouse_columns"] = sorted(cols)
    ok = all(ref["validation"][c]["equal"] for c in oracle.EXPECTED) and not ref["validation"]["H5_email_dimension"]["accepted"] \
        and ref["validation"]["H3_reading_customer"]["by_year"] != ref["validation"]["H3_reading_store"]["by_year"] \
        and not ref["validation"]["H1_payment_column_scan"]["columns_naming_payment_settlement_collection"]
    ref["validation"]["all_reference_checks_pass"] = ok
    Path(a.out).write_text(json.dumps(ref, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in ref["validation"].items() if k != "diagnostics_oracle"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
