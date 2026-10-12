"""Build the E4 raw-data snapshots (frozen construction; run before the freeze). Each snapshot is a directory of the
five landing CSVs. Only PINNED comes from the pinned generator; the others are controlled disposable fixtures made
from PINNED by the exact edits below, so their discriminating rows are known in advance.

  PINNED      trusted generator output (hashes = E0 anchors)
  BOUNDARY    P1 discriminator: three completed lines with positive quantity get unit_price 100.00 / 99.99 / 100.01
  NEGQTY      guard control: the lowest-id completed line with unit_price >= 100 gets quantity -1
  STALE       unregistered snapshot: one completed order of a French customer is relabelled 'returned'

    python3 src/fixtures.py --pinned .upstream/data/raw --out fixtures
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


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p: Path):
    with p.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(p: Path, header, rows) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    p.write_text(buf.getvalue(), encoding="utf-8")


def completed_lines(d: Path):
    _, orders = read(d / "orders.csv")
    st = {o["order_id"]: o["status"].strip().lower() for o in orders}
    h, items = read(d / "order_items.csv")
    return h, items, [i for i in items if st.get(i["order_id"]) == "completed" and int(i["quantity"]) > 0]


def build(pinned: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    reg = {}
    for name in ("PINNED", "BOUNDARY", "NEGQTY", "STALE"):
        d = out / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        for f in FILES:
            shutil.copy(pinned / f, d / f)
    edits = {"PINNED": []}
    # BOUNDARY
    h, items, comp = completed_lines(out / "BOUNDARY")
    below = sorted((i for i in comp if Decimal(i["unit_price"]) < 100), key=lambda i: int(i["order_item_id"]))[:3]
    e = []
    for i, new in zip(below, ("100.00", "99.99", "100.01")):
        e.append({"file": "order_items.csv", "order_item_id": i["order_item_id"], "field": "unit_price", "old": i["unit_price"], "new": new})
        i["unit_price"] = new
    write(out / "BOUNDARY" / "order_items.csv", h, items)
    edits["BOUNDARY"] = e
    # NEGQTY
    h, items, comp = completed_lines(out / "NEGQTY")
    hi = min((i for i in comp if Decimal(i["unit_price"]) >= 100), key=lambda i: int(i["order_item_id"]))
    edits["NEGQTY"] = [{"file": "order_items.csv", "order_item_id": hi["order_item_id"], "field": "quantity", "old": hi["quantity"], "new": "-1"}]
    hi["quantity"] = "-1"
    write(out / "NEGQTY" / "order_items.csv", h, items)
    # STALE
    _, custs = read(out / "STALE" / "customers.csv")
    fr = {c["customer_id"] for c in custs if c["country"].strip().upper() in ("FRANCE", "FR", "FRA")}
    h, orders = read(out / "STALE" / "orders.csv")
    o = min((o for o in orders if o["status"].strip().lower() == "completed" and o["customer_id"] in fr), key=lambda o: int(o["order_id"]))
    edits["STALE"] = [{"file": "orders.csv", "order_id": o["order_id"], "field": "status", "old": o["status"], "new": "returned"}]
    o["status"] = "returned"
    write(out / "STALE" / "orders.csv", h, orders)
    for name in edits:
        reg[name] = {"csv_sha256": {f: sha(out / name / f) for f in FILES}, "edits": edits[name]}
    return reg


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pinned", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    reg = build(Path(a.pinned), Path(a.out))
    print(json.dumps(reg, indent=1))
