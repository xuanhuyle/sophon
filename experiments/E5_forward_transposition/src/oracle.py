"""E5 independent raw-CSV oracle (frozen before the transposer exists). Written anew for E5; it does not import the
E4 reference, the IR, the packet, the transposer or any candidate. Stdlib + Decimal over the five landing CSVs.

Source normalisation re-implemented from the pinned upstream 312e97ad SQL:
  stg_orders       status = lower(trim(status)); order_date = cast(order_date as date)
  stg_order_items  quantity = cast(quantity as integer); unit_price = cast(unit_price as decimal(10,2))
  stg_customers    country = CASE upper(trim(country)) ... ELSE 'Other'
  fact_sales       order_items INNER JOIN orders INNER JOIN products; revenue = cast(quantity*unit_price as decimal(12,2))

Approved LAB meanings encoded here by the reference author from the clause texts:
  P1v1  [S1 v1]  completed AND charged unit price >= 100   (LAB-REV-POLICY)
  P1v2  [S1 v2]  completed AND charged unit price >= 120   (LAB-REV-POLICY-AMD-1)
  P2    [S2 v1, reading R_CUSTOMER_COUNTRY]  completed AND customer country = France
Each result can be restricted to an order-date window [date_from, date_to) (either end open).
"""
from __future__ import annotations

import csv
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

CENT = Decimal("0.01")
CUSTOMER_COUNTRY_CASE = {
    "FRANCE": "France", "FR": "France", "FRA": "France",
    "GERMANY": "Germany", "DE": "Germany", "DEUTSCHLAND": "Germany",
    "SPAIN": "Spain", "ES": "Spain", "ESPAÑA": "Spain",
    "ITALY": "Italy", "IT": "Italy", "ITALIA": "Italy",
    "BELGIUM": "Belgium", "BE": "Belgium", "BELGIQUE": "Belgium",
}
P1_THRESHOLD = {"P1v1": Decimal("100"), "P1v2": Decimal("120")}
POLICIES = ("P1v1", "P1v2", "P2")


def _table(raw: Path, name: str) -> list[dict]:
    with (Path(raw) / f"{name}.csv").open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def order_lines(raw_dir) -> dict[str, dict]:
    """Rows of gold.fact_sales as the pinned dbt models would build them, with the attributes the policies need."""
    orders = {o["order_id"]: o for o in _table(raw_dir, "orders")}
    product_ids = {p["product_id"] for p in _table(raw_dir, "products")}
    customers = {c["customer_id"]: c for c in _table(raw_dir, "customers")}
    stores = {s["store_id"]: s for s in _table(raw_dir, "stores")}
    lines = {}
    for item in _table(raw_dir, "order_items"):
        order = orders.get(item["order_id"])
        if order is None or item["product_id"] not in product_ids:
            continue  # inner joins in fact_sales
        qty = int(item["quantity"])
        price = Decimal(item["unit_price"]).quantize(CENT, rounding=ROUND_HALF_UP)
        cust = customers.get(order["customer_id"]) or {}
        store = stores.get(order["store_id"]) or {}
        lines[item["order_item_id"]] = {
            "order_item_id": item["order_item_id"], "order_id": order["order_id"],
            "order_date": date.fromisoformat(order["order_date"].strip()[:10]).isoformat(),
            "status_raw": order["status"], "status": order["status"].strip().lower(),
            "quantity": qty, "unit_price_raw": item["unit_price"], "unit_price": str(price),
            "amount": str((qty * price).quantize(CENT, rounding=ROUND_HALF_UP)),
            "customer_id": order["customer_id"], "customer_country_raw": cust.get("country"),
            "customer_country": CUSTOMER_COUNTRY_CASE.get((cust.get("country") or "").strip().upper(), "Other"),
            "store_id": order["store_id"], "store_country": (store.get("country") or "").strip()}
    return lines


def is_eligible(policy: str, line: dict) -> bool:
    if line["status"] != "completed":
        return False
    if policy in P1_THRESHOLD:
        return Decimal(line["unit_price"]) >= P1_THRESHOLD[policy]
    if policy == "P2":
        return line["customer_country"] == "France"
    raise KeyError(policy)


def in_window(order_date: str, date_from: str | None, date_to: str | None) -> bool:
    return (date_from is None or order_date >= date_from) and (date_to is None or order_date < date_to)


def evaluate(raw_dir, policy: str, date_from: str | None = None, date_to: str | None = None, lines: dict | None = None) -> dict:
    lines = order_lines(raw_dir) if lines is None else lines
    chosen = {k: v["amount"] for k, v in lines.items() if in_window(v["order_date"], date_from, date_to) and is_eligible(policy, v)}
    totals: dict[str, Decimal] = {}
    for k, amt in chosen.items():
        y = lines[k]["order_date"][:4]
        totals[y] = totals.get(y, Decimal(0)) + Decimal(amt)
    return {"policy": policy, "window": [date_from, date_to],
            "by_year": {y: str(t.quantize(CENT)) for y, t in sorted(totals.items())},
            "lines": dict(sorted(chosen.items(), key=lambda kv: int(kv[0]))), "line_count": len(chosen)}


def routed(raw_dir, segments: list[tuple[str, str | None, str | None]]) -> dict:
    """Union of per-segment results; segments are (policy, date_from, date_to) and must not overlap."""
    lines = order_lines(raw_dir)
    out_lines, totals = {}, {}
    for pol, a, b in segments:
        r = evaluate(raw_dir, pol, a, b, lines)
        for k, v in r["lines"].items():
            if k in out_lines:
                raise ValueError(f"overlapping segments at line {k}")
            out_lines[k] = v
        for y, t in r["by_year"].items():
            totals[y] = totals.get(y, Decimal(0)) + Decimal(t)
    return {"segments": [list(s) for s in segments], "by_year": {y: str(t.quantize(CENT)) for y, t in sorted(totals.items())},
            "lines": dict(sorted(out_lines.items(), key=lambda kv: int(kv[0]))), "line_count": len(out_lines)}
