"""E5 raw-data snapshots (frozen construction, run before the freeze). Each snapshot is a directory of the five
pinned landing CSVs.

  PINNED       trusted generator output (hashes = E0 anchors)
  BOUNDARY120  control fixture made from PINNED by the exact edits below (all chosen by a fixed rule):
               - 2025 completed, quantity > 0 lines get unit_price 99.99 / 100.00 / 119.99 / 120.00 / 120.01
               - 2024 completed, quantity > 0 lines get unit_price 100.00 / 119.99   (history: v1 still governs 2024)
               - 2025 returned line -> 120.00, 2025 cancelled line -> 120.01, 2024 returned line -> 100.00
               The edited lines are the lowest order_item_id lines of the required (year, status) whose pinned
               unit price is below 90, so no edit lands on an existing near-boundary price.

    python3 src/snapshots.py --pinned .upstream/data/raw --out runs/snapshots
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from decimal import Decimal
from pathlib import Path

FILES = ("customers.csv", "order_items.csv", "orders.csv", "products.csv", "stores.csv")
PLAN = [("2025", "completed", "99.99"), ("2025", "completed", "100.00"), ("2025", "completed", "119.99"),
        ("2025", "completed", "120.00"), ("2025", "completed", "120.01"), ("2024", "completed", "100.00"),
        ("2024", "completed", "119.99"), ("2025", "returned", "120.00"), ("2025", "cancelled", "120.01"),
        ("2024", "returned", "100.00")]


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _read(p: Path):
    with p.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def _write(p: Path, header, rows) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    p.write_text(buf.getvalue(), encoding="utf-8")


def build(pinned: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    for name in ("PINNED", "BOUNDARY120"):
        d = out / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        for f in FILES:
            shutil.copy(Path(pinned) / f, d / f)
    d = out / "BOUNDARY120"
    _, orders = _read(d / "orders.csv")
    odate = {o["order_id"]: (o["order_date"][:4], o["status"].strip().lower()) for o in orders}
    h, items = _read(d / "order_items.csv")
    used, edits = set(), []
    for year, status, price in PLAN:
        it = min((i for i in items if odate.get(i["order_id"]) == (year, status) and int(i["quantity"]) > 0
                  and Decimal(i["unit_price"]) < 90 and i["order_item_id"] not in used), key=lambda i: int(i["order_item_id"]))
        used.add(it["order_item_id"])
        edits.append({"file": "order_items.csv", "order_item_id": it["order_item_id"], "order_id": it["order_id"], "year": year,
                      "status": status, "field": "unit_price", "old": it["unit_price"], "new": price})
        it["unit_price"] = price
    _write(d / "order_items.csv", h, items)
    return {name: {"csv_sha256": {f: sha(out / name / f) for f in FILES}, "edits": edits if name == "BOUNDARY120" else []}
            for name in ("PINNED", "BOUNDARY120")}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pinned", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print(json.dumps(build(Path(a.pinned), Path(a.out)), indent=1))
