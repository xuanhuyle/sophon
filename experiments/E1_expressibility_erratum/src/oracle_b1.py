"""Independent B1 oracle (PROTOCOL.md §4). Stdlib only, reads the raw CSVs and nothing else: no warehouse, no
MetricFlow output, no E1/E2 code.

B1: completed orders, order lines whose charged unit price is >= 100.00; amount = quantity * unit_price;
year = year of the order date.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

THRESHOLD = Decimal("100")


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute(raw_dir: str | Path, threshold: Decimal = THRESHOLD) -> dict:
    raw = Path(raw_dir)
    orders = {r["order_id"]: r for r in _rows(raw / "orders.csv")}
    products = {r["product_id"] for r in _rows(raw / "products.csv")}
    items = _rows(raw / "order_items.csv")

    by_year: dict[str, Decimal] = {}
    lines: dict[str, str] = {}
    csv_facts = {"order_items": len(items), "min_quantity": None, "max_unit_price_decimals": 0,
                 "items_without_order": 0, "items_without_product": 0, "duplicate_item_ids": 0}
    seen: set[str] = set()
    for it in items:
        q = int(it["quantity"])
        raw_price = it["unit_price"]
        u = Decimal(raw_price)
        decimals = len(raw_price.split(".", 1)[1]) if "." in raw_price else 0
        csv_facts["min_quantity"] = q if csv_facts["min_quantity"] is None else min(csv_facts["min_quantity"], q)
        csv_facts["max_unit_price_decimals"] = max(csv_facts["max_unit_price_decimals"], decimals)
        if it["order_item_id"] in seen:
            csv_facts["duplicate_item_ids"] += 1
        seen.add(it["order_item_id"])
        o = orders.get(it["order_id"])
        if o is None:
            csv_facts["items_without_order"] += 1
            continue
        if it["product_id"] not in products:
            csv_facts["items_without_product"] += 1
            continue
        if o["status"] != "completed" or u < threshold:
            continue
        amount = q * u
        year = o["order_date"][:4]
        by_year[year] = by_year.get(year, Decimal("0")) + amount
        lines[it["order_item_id"]] = str(amount.quantize(Decimal("0.01")))
    return {
        "label": "INDEPENDENT ORACLE: stdlib Decimal over raw CSVs; not native semantic execution",
        "by_year": {y: str(v.quantize(Decimal("0.01"))) for y, v in sorted(by_year.items())},
        "lines": dict(sorted(lines.items(), key=lambda kv: int(kv[0]))),
        "line_count": len(lines),
        "csv_facts": csv_facts,
    }
