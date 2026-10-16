#!/usr/bin/env python3
"""CROSS-CHECK (not semantic execution): completed revenue per year recomputed from the raw CSV landing files with
the Python standard library only (csv, decimal). It does not read DuckDB, dbt or MetricFlow output.

Rule, written from the upstream source code before execution (PROTOCOL.md S10): for every order line whose order
has lower(strip(status)) == "completed" and whose product_id exists in products.csv (fact_sales inner-joins
products), add quantity * unit_price; group by the year of order_date.

    python src/crosscheck.py --raw .upstream/data/raw
"""
from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path


def compute(raw: Path) -> dict:
    with (raw / "orders.csv").open(newline="", encoding="utf-8") as f:
        orders = {r["order_id"]: r for r in csv.DictReader(f)}
    with (raw / "products.csv").open(newline="", encoding="utf-8") as f:
        products = {r["product_id"] for r in csv.DictReader(f)}
    by_year: dict[str, Decimal] = {}
    lines = {"total": 0, "completed": 0, "orphan_order": 0, "orphan_product": 0}
    with (raw / "order_items.csv").open(newline="", encoding="utf-8") as f:
        for it in csv.DictReader(f):
            lines["total"] += 1
            o = orders.get(it["order_id"])
            if o is None:
                lines["orphan_order"] += 1
                continue
            if it["product_id"] not in products:
                lines["orphan_product"] += 1
                continue
            if o["status"].strip().lower() != "completed":
                continue
            lines["completed"] += 1
            year = o["order_date"][:4]
            by_year[year] = by_year.get(year, Decimal("0")) + int(it["quantity"]) * Decimal(it["unit_price"])
    return {"by_year": {y: str(v.quantize(Decimal("0.01"))) for y, v in sorted(by_year.items())},
            "total": str(sum(by_year.values(), Decimal("0")).quantize(Decimal("0.01"))), "lines": lines}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    print(json.dumps(compute(Path(ap.parse_args().raw)), indent=1))


if __name__ == "__main__":
    main()
