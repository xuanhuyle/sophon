"""Write REFERENCE.json (run before the freeze): the approved LAB specifications, the registered raw snapshots and
the independent reference results for each, computed by src/reference.py from raw CSVs only.

    python3 src/build_reference.py --snapshots runs/snapshots
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E4 = HERE.parent
EXP = E4.parent
sys.path.insert(0, str(HERE))
import fixtures  # noqa: E402
import reference  # noqa: E402


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshots", required=True)
    a = ap.parse_args()
    snaps = Path(a.snapshots)
    trusted = json.loads((EXP / "E3_1_integrity" / "cases" / "TRUSTED_MANIFEST.json").read_text())
    reg = {name: {"csv_sha256": {f: fixtures.sha(snaps / name / f) for f in fixtures.FILES}} for name in ("PINNED", "BOUNDARY", "NEGQTY")}
    stale = {f: fixtures.sha(snaps / "STALE" / f) for f in fixtures.FILES}
    assert reg["PINNED"]["csv_sha256"] == trusted["raw_csv_sha256"], "PINNED must equal the E0/E3.1 anchors"
    specs = {
        "P1": {"source": {"e3_record": "experiments/E3_formal_ir/cases/records/S1.json", "clause": "S1 v1", "reading": "R_SINGLE",
                          "approved_reading_meaning_sha256": trusted["approved_reading_meaning_sha256"]["S1/R_SINGLE"],
                          "lab_approval": "AP_S1_READ (LAB_SIMULATED)", "governing_source_sha256": trusted["governing_source"]["sha256"]},
               "predicates": [{"field": "order status (normalised lower(trim))", "op": "=", "value": "completed"},
                              {"field": "charged unit price of the order line", "op": ">=", "value": "100", "unit": "currency per unit"}],
               "amount": "sum over eligible order lines of quantity * unit_price", "period": "calendar year of order date",
               "population": "order lines that join to an order and a product (fact_sales inner joins)",
               "row_grain": "order line (order_item_id = sales_id)",
               "derivation_guards_if_derived": ["quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison"]},
        "P2": {"source": {"e3_record": "experiments/E3_formal_ir/cases/records/S2.json", "clause": "S2 v1", "reading": "R_CUSTOMER_COUNTRY",
                          "approved_reading_meaning_sha256": trusted["approved_reading_meaning_sha256"]["S2/R_CUSTOMER_COUNTRY"],
                          "lab_approval": "AP_S2_CUSTOMER (LAB_SIMULATED)", "governing_source_sha256": trusted["governing_source"]["sha256"],
                          "rejected_alternative": "R_STORE_COUNTRY (store country), NOT approved"},
               "predicates": [{"field": "order status (normalised lower(trim))", "op": "=", "value": "completed"},
                              {"field": "customer country (normalised by the pinned stg_customers CASE table, aliases FR/FRA/France)", "op": "=", "value": "France"}],
               "amount": "sum over eligible order lines of quantity * unit_price", "period": "calendar year of order date",
               "population": "order lines that join to an order and a product (fact_sales inner joins)",
               "row_grain": "order line (order_item_id = sales_id)"},
    }
    results = {}
    out_lines = E4 / "fixtures" / "reference_lines"
    out_lines.mkdir(parents=True, exist_ok=True)
    for pol in ("P1", "P2"):
        for snap in ("PINNED", "BOUNDARY", "NEGQTY", "STALE"):
            r = reference.compute(snaps / snap, pol)
            key = f"{pol}@{snap}"
            (out_lines / f"{key.replace('@', '_')}.json").write_text(json.dumps(r["lines"], indent=0) + "\n", encoding="utf-8")
            results[key] = {"by_year": r["by_year"], "line_count": r["line_count"], "lines_sha256": hashlib.sha256(canon(r["lines"]).encode()).hexdigest()}
    for pol, k in (("P1", "S1/R_SINGLE"), ("P2", "S2/R_CUSTOMER_COUNTRY")):
        assert results[f"{pol}@PINNED"]["by_year"] == trusted["expected_reference_values"][k], f"{pol} reference != E3.1 trusted values"
    edits = json.loads((E4 / "runs" / "fixtures_registry.json").read_text())
    doc = {
        "label": "E4 REFERENCE (frozen): approved LAB meaning + independent raw-CSV results. Never derived from any candidate.",
        "approved_specs": specs,
        "registered_snapshots": {
            "verification": {"P1": ["PINNED", "BOUNDARY"], "P2": ["PINNED"]},
            "guard_fixtures": ["NEGQTY"],
            "snapshots": {n: {**reg[n], "edits": edits[n]["edits"], "origin": "pinned generator" if n == "PINNED" else "controlled fixture from PINNED"} for n in reg}},
        "unregistered_example": {"STALE": {"csv_sha256": stale, "edits": edits["STALE"]["edits"], "registered": False}},
        "reference_results": results,
        "pristine_semantic_manifest_sha256": trusted["semantic_manifest_sha256"],
        "reference_code_sha256": {"src/reference.py": fixtures.sha(HERE / "reference.py"), "src/fixtures.py": fixtures.sha(HERE / "fixtures.py")},
        "cross_check": "P1@PINNED and P2@PINNED equal E3.1 TRUSTED_MANIFEST expected_reference_values (erratum oracle_b1 / E2 e2_oracle)",
    }
    (E4 / "REFERENCE.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: (v["by_year"], v["line_count"]) for k, v in results.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
