"""E2 independent oracle (orchestrator side; never in the solver packet).

Recomputes the representable cases from the raw landing CSVs with the Python standard library only. Normalizations
are re-implemented from the upstream staging SQL text (stg_orders: lower(trim(status|channel)); stg_customers:
country CASE table; stg_stores: trim(country)). fact_sales inner-joins orders and products, so lines whose order or
product is missing are excluded.

  H2  gross profit = sum(quantity * (unit_price - unit_cost)), completed, category Electronics, by year
  H4  units = sum(quantity), status != cancelled, store country Germany, by year
  H6  distinct orders, channel online, customer country France, any status, by year
Diagnostics (not scored): H3 under each reading, H5 (gmail customers), H1 under the rejected status proxy.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

CENT = Decimal("0.01")
COUNTRY = {"FRANCE": "France", "FR": "France", "FRA": "France", "GERMANY": "Germany", "DE": "Germany", "DEUTSCHLAND": "Germany",
           "SPAIN": "Spain", "ES": "Spain", "ESPAÑA": "Spain", "ITALY": "Italy", "IT": "Italy", "ITALIA": "Italy",
           "BELGIUM": "Belgium", "BE": "Belgium", "BELGIQUE": "Belgium"}


def _read(raw: Path, name: str) -> list[dict]:
    with (raw / f"{name}.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def lines(raw: str | Path):
    raw = Path(raw)
    orders = {r["order_id"]: r for r in _read(raw, "orders")}
    products = {r["product_id"]: r for r in _read(raw, "products")}
    customers = {r["customer_id"]: r for r in _read(raw, "customers")}
    stores = {r["store_id"]: r for r in _read(raw, "stores")}
    for it in _read(raw, "order_items"):
        o, p = orders.get(it["order_id"]), products.get(it["product_id"])
        if o is None or p is None:
            continue
        c, s = customers.get(o["customer_id"], {}), stores.get(o["store_id"], {})
        yield {
            "order_id": o["order_id"], "year": o["order_date"][:4],
            "status": o["status"].strip().lower(), "channel": o["channel"].strip().lower(),
            "qty": int(it["quantity"]), "price": Decimal(it["unit_price"]).quantize(CENT), "cost": Decimal(p["unit_cost"]).quantize(CENT),
            "category": p["category"], "cust_country": COUNTRY.get((c.get("country") or "").strip().upper(), "Other"),
            "store_country": (s.get("country") or "").strip(), "email": (c.get("email") or "").strip().lower(),
        }


def _sum(rows, key):
    out: dict[str, Decimal] = {}
    for r in rows:
        out[r["year"]] = out.get(r["year"], Decimal("0")) + key(r)
    return dict(sorted(out.items()))


def h2(raw):
    return {y: str(v.quantize(CENT)) for y, v in _sum((r for r in lines(raw) if r["status"] == "completed" and r["category"] == "Electronics"),
                                                       lambda r: r["qty"] * (r["price"] - r["cost"])).items()}


def h4(raw):
    return {y: str(int(v)) for y, v in _sum((r for r in lines(raw) if r["status"] != "cancelled" and r["store_country"] == "Germany"),
                                             lambda r: Decimal(r["qty"])).items()}


def h6(raw):
    seen: dict[str, set] = {}
    for r in lines(raw):
        if r["channel"] == "online" and r["cust_country"] == "France":
            seen.setdefault(r["year"], set()).add(r["order_id"])
    return {y: str(len(v)) for y, v in sorted(seen.items())}


def revenue(raw, pred):
    return {y: str(v.quantize(CENT)) for y, v in _sum((r for r in lines(raw) if pred(r)), lambda r: r["qty"] * r["price"]).items()}


EXPECTED = {"H2": h2, "H4": h4, "H6": h6}
DIAGNOSTICS = {
    "H3_reading_customer_country": lambda raw: revenue(raw, lambda r: r["status"] == "completed" and r["cust_country"] == "France"),
    "H3_reading_store_country": lambda raw: revenue(raw, lambda r: r["status"] == "completed" and r["store_country"] == "France"),
    "H5_gmail_completed_revenue": lambda raw: revenue(raw, lambda r: r["status"] == "completed" and r["email"].endswith("@gmail.com")),
    "H1_rejected_status_proxy": lambda raw: revenue(raw, lambda r: r["status"] == "completed"),
}
