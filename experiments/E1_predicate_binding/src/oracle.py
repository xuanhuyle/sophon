"""E1 independent oracle (frozen with the protocol; written before the evaluator).

Computes the expected yearly amount for a set of *required predicate ids* directly from the raw landing CSVs with
the Python standard library (csv, decimal). It never reads DuckDB, dbt, MetricFlow or any native output.

Supported predicates, each implemented from the LAB-REV-1 clause text:
  P_LINE_AMOUNT         quantity * unit_price per order line (lines whose order and product exist, as fact_sales joins)
  P_STATUS_COMPLETED    lower(strip(order status)) == "completed"
  P_YEAR_BY_ORDER_DATE  group by the year of the order's order_date
  P_UNIT_PRICE_GE_100   Decimal(unit_price) >= Decimal("100.00")
Any other required predicate (for example P_SETTLEMENT_CONFIRMED) makes the expectation NOT_COMPUTABLE: the raw
estate holds no field the oracle could use, and the oracle never substitutes a proxy.
For exactly {P_LINE_AMOUNT, P_STATUS_COMPLETED, P_YEAR_BY_ORDER_DATE} it delegates to E0's crosscheck.compute
(reused, unmodified) and also recomputes with its own loop; the two must agree.
"""
from __future__ import annotations

import csv
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "E0_native_adapter" / "src"))
import crosscheck as e0_crosscheck  # noqa: E402

SUPPORTED = {"P_LINE_AMOUNT", "P_STATUS_COMPLETED", "P_YEAR_BY_ORDER_DATE", "P_UNIT_PRICE_GE_100"}
A_SET = {"P_LINE_AMOUNT", "P_STATUS_COMPLETED", "P_YEAR_BY_ORDER_DATE"}
CENT = Decimal("0.01")


def _own(raw: Path, preds: set[str]) -> dict[str, str]:
    with (raw / "orders.csv").open(newline="", encoding="utf-8") as f:
        orders = {r["order_id"]: r for r in csv.DictReader(f)}
    with (raw / "products.csv").open(newline="", encoding="utf-8") as f:
        products = {r["product_id"] for r in csv.DictReader(f)}
    out: dict[str, Decimal] = {}
    with (raw / "order_items.csv").open(newline="", encoding="utf-8") as f:
        for it in csv.DictReader(f):
            o = orders.get(it["order_id"])
            if o is None or it["product_id"] not in products:
                continue
            if "P_STATUS_COMPLETED" in preds and o["status"].strip().lower() != "completed":
                continue
            if "P_UNIT_PRICE_GE_100" in preds and Decimal(it["unit_price"]) < Decimal("100.00"):
                continue
            key = o["order_date"][:4] if "P_YEAR_BY_ORDER_DATE" in preds else "all"
            out[key] = out.get(key, Decimal("0")) + int(it["quantity"]) * Decimal(it["unit_price"])
    return {k: str(v.quantize(CENT)) for k, v in sorted(out.items())}


def expected(raw: str | Path, required: list[str] | set[str]) -> dict:
    raw = Path(raw)
    preds = set(required)
    if "P_LINE_AMOUNT" not in preds or not preds <= SUPPORTED:
        return {"computable": False, "reason": f"unsupported or unobservable required predicates: {sorted(preds - SUPPORTED) or ['P_LINE_AMOUNT missing']}"}
    own = _own(raw, preds)
    res = {"computable": True, "by_year": own, "method": "own stdlib loop over raw CSVs"}
    if preds == A_SET:
        e0 = e0_crosscheck.compute(raw)["by_year"]
        res["e0_crosscheck_by_year"] = e0
        res["own_equals_e0_crosscheck"] = e0 == own
        if e0 != own:
            res["computable"] = False
            res["reason"] = "oracle self-disagreement (own loop vs E0 crosscheck)"
    return res


def compare(native_by_year: dict[str, str], oracle_by_year: dict[str, str]) -> dict:
    """Exact per-year equality to the cent. Returns the counterexamples when they differ."""
    n = {k: str(Decimal(v).quantize(CENT)) for k, v in native_by_year.items()}
    o = {k: str(Decimal(v).quantize(CENT)) for k, v in oracle_by_year.items()}
    diffs = [{"year": y, "native": n.get(y), "oracle": o.get(y)} for y in sorted(set(n) | set(o)) if n.get(y) != o.get(y)]
    return {"equal": not diffs, "counterexamples": diffs}
