"""E4 independent reference (frozen before any candidate is evaluated). Stdlib + Decimal over raw landing CSVs only.

It encodes the APPROVED LAB meaning of two E3 clauses, using the pinned upstream's own staging normalisations
(stg_orders: lower(trim(status)); stg_customers: the country CASE table; fact_sales: inner joins to orders and
products). It never reads a candidate's YAML, SQL, query or result.

  P1 (E3 S1 / R_SINGLE): completed order lines with charged unit price >= 100; amount = quantity * unit_price;
                         period = calendar year of order date.
  P2 (E3 S2 / R_CUSTOMER_COUNTRY): completed order lines whose CUSTOMER country is France; same amount/period.

compute(raw_dir, policy) -> {"by_year": {...}, "lines": {order_item_id: amount}, "line_facts": {...}}
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

CENT = Decimal("0.01")
# stg_customers.sql CASE upper(trim(country)) ... (pinned upstream 312e97ad)
COUNTRY = {"FRANCE": "France", "FR": "France", "FRA": "France", "GERMANY": "Germany", "DE": "Germany",
           "DEUTSCHLAND": "Germany", "SPAIN": "Spain", "ES": "Spain", "ESPAÑA": "Spain", "ITALY": "Italy",
           "IT": "Italy", "ITALIA": "Italy", "BELGIUM": "Belgium", "BE": "Belgium", "BELGIQUE": "Belgium"}


def _rows(raw: Path, name: str) -> list[dict]:
    with (raw / f"{name}.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def line_facts(raw_dir: str | Path) -> dict[str, dict]:
    """One record per order line that survives fact_sales' inner joins, with the approved-meaning attributes."""
    raw = Path(raw_dir)
    orders = {r["order_id"]: r for r in _rows(raw, "orders")}
    products = {r["product_id"] for r in _rows(raw, "products")}
    customers = {r["customer_id"]: r for r in _rows(raw, "customers")}
    stores = {r["store_id"]: r for r in _rows(raw, "stores")}
    out = {}
    for it in _rows(raw, "order_items"):
        o = orders.get(it["order_id"])
        if o is None or it["product_id"] not in products:
            continue
        c, s = customers.get(o["customer_id"], {}), stores.get(o["store_id"], {})
        q, u = int(it["quantity"]), Decimal(it["unit_price"])
        out[it["order_item_id"]] = {
            "order_item_id": it["order_item_id"], "order_id": o["order_id"], "order_date": o["order_date"],
            "year": o["order_date"][:4], "status_raw": o["status"], "status": o["status"].strip().lower(),
            "quantity": q, "unit_price_raw": it["unit_price"], "unit_price": str(u), "amount": str((q * u).quantize(CENT)),
            "customer_id": o["customer_id"], "customer_country_raw": c.get("country"),
            "customer_country": COUNTRY.get((c.get("country") or "").strip().upper(), "Other"),
            "store_id": o["store_id"], "store_country": (s.get("country") or "").strip()}
    return out


def eligible(policy: str, f: dict) -> bool:
    if policy == "P1":
        return f["status"] == "completed" and Decimal(f["unit_price"]) >= Decimal("100")
    if policy == "P2":
        return f["status"] == "completed" and f["customer_country"] == "France"
    raise ValueError(policy)


def compute(raw_dir: str | Path, policy: str) -> dict:
    facts = line_facts(raw_dir)
    lines = {k: f["amount"] for k, f in facts.items() if eligible(policy, f)}
    by_year: dict[str, Decimal] = {}
    for k in lines:
        by_year[facts[k]["year"]] = by_year.get(facts[k]["year"], Decimal(0)) + Decimal(lines[k])
    return {"policy": policy, "by_year": {y: str(v.quantize(CENT)) for y, v in sorted(by_year.items())},
            "lines": dict(sorted(lines.items(), key=lambda kv: int(kv[0]))), "line_count": len(lines)}
