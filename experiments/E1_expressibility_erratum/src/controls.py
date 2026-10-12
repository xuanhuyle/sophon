"""G7 negative controls (PROTOCOL.md §5) on DISPOSABLE warehouse copies under runs/controls/ (ignored).

Each control copies the pinned warehouse (file name kept as warehouse.duckdb so the manifest's catalog name still
resolves), rewrites a few gold.fact_sales rows consistently (revenue = quantity * unit_price), reruns the SAME
native derived filter through `mf`, and compares it with the truth, i.e. B1 applied in Python Decimal to the copy's
own rows (`unit_price >= 100`, status completed, amount = revenue). The pinned warehouse is never written.
    .upstream/.venv/bin/python src/controls.py --upstream .upstream --out evidence/controls
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_erratum as rr  # noqa: E402  (same native helpers, guards and constants as the reproduction)

cap, mfa = rr.cap, rr.mfa
T = Decimal("100")


def truth(rows) -> dict:
    """rows: (sales_id, order_id, quantity, unit_price, revenue, status, order_date)."""
    by_year, lines, orders = {}, {}, {}
    for sid, oid, q, u, rev, st, od in rows:
        if st != "completed" or Decimal(u) < T:
            continue
        y = str(od)[:4]
        by_year[y] = by_year.get(y, Decimal(0)) + Decimal(rev)
        lines[str(sid)] = str(Decimal(rev).quantize(rr.CENT))
        orders.setdefault(y, set()).add(oid)
    return {"by_year": {y: str(v.quantize(rr.CENT)) for y, v in sorted(by_year.items())}, "lines": lines,
            "orders_by_year": {y: len(v) for y, v in sorted(orders.items())}}


def make_copy(src: Path, name: str, root: Path, updates: list[tuple[int, int, Decimal]]) -> Path:
    import duckdb
    d = root / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    wh = d / "warehouse.duckdb"
    shutil.copy(src, wh)
    con = duckdb.connect(str(wh))
    try:
        for sid, q, u in updates:
            con.execute("update gold.fact_sales set quantity = ?, unit_price = ?, "
                        "revenue = cast(? * ? as decimal(12,2)) where sales_id = ?", [q, u, q, u, sid])
            assert con.execute("select count(*) from gold.fact_sales where sales_id = ?", [sid]).fetchone()[0] == 1
        con.execute("checkpoint")
    finally:
        con.close()
    return wh


def run_control(p0, name: str, root: Path, updates, extra_orders: bool = False) -> dict:
    wh = make_copy(p0.warehouse, name, root, updates)
    p = mfa.open_project(p0.upstream, warehouse=wh)
    before_pinned = mfa.sha256_file(p0.warehouse)
    nw = rr.nq(p, "revenue", ["metric_time__year"], rr.W)
    nl = rr.nq(p, "revenue", ["sales"], rr.W)
    no = rr.nq(p, "orders", ["metric_time__year"], rr.W) if extra_orders else None
    explain = rr.explain_with_where(p, "revenue", ["metric_time__year"], rr.W)
    whl = rr.warehouse_lines(wh)
    tr = truth(whl["rows"])
    # the control simulates an estate whose source carries the rewritten values: source = the copy's own rows
    src_prices = {str(r[0]): str(r[3]) for r in whl["rows"]}
    g = rr.guards(whl, src_prices, len(whl["rows"]), explain["sql"])
    nat_y, nat_l = rr.yearly(nw, "revenue"), rr.line_rows(nl)
    ev = {"source_column_present": True, "direct_dimension_present": False, "native_witness_accepted": nw["ok"],
          "native_equals_oracle_yearly": nat_y == tr["by_year"], "native_equals_oracle_lines": nat_l == tr["lines"],
          "guards": {k: g[k]["ok"] for k in cap.GUARDS}}
    touched = [str(s) for s, _, _ in updates]
    out = {"control": name, "updates": [{"sales_id": s, "quantity": q, "unit_price": str(u)} for s, q, u in updates],
           "native_ok": nw["ok"] and nl["ok"], "native_yearly": nat_y, "truth_yearly": tr["by_year"],
           "yearly_equal": nat_y == tr["by_year"], "lines_equal": nat_l == tr["lines"],
           "touched_lines": {s: {"in_native_derived": s in (nat_l or {}), "in_truth": s in tr["lines"],
                                 "native_amount": (nat_l or {}).get(s), "truth_amount": tr["lines"].get(s)}
                             for s in touched},
           "guards": {k: g[k]["ok"] for k in cap.GUARDS}, "guard_detail_quantity": g["quantity_positive"],
           "capability": cap.classify(ev),
           "pinned_warehouse_unchanged": before_pinned == mfa.sha256_file(p0.warehouse),
           "receipts": {"NW": nw["receipt"], "NL_exit": nl["receipt"]["exit_code"], "NL_rows": len(nl["rows"])}}
    if no is not None:
        out["native_orders_yearly"] = rr.yearly(no, "orders") if no["ok"] else None
        out["native_orders_yearly"] = ({y: str(int(Decimal(v))) for y, v in out["native_orders_yearly"].items()}
                                       if out["native_orders_yearly"] else None)
        out["truth_orders_yearly"] = {y: str(v) for y, v in tr["orders_by_year"].items()}
        out["orders_equal"] = out["native_orders_yearly"] == out["truth_orders_yearly"]
        out["receipts"]["NO"] = no["receipt"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default=str(HERE.parent / "runs" / "controls"))
    a = ap.parse_args()
    out, work = Path(a.out), Path(a.work)
    p0 = mfa.open_project(a.upstream)
    rows = rr.warehouse_lines(p0.warehouse)["rows"]
    comp = sorted((r for r in rows if r[5] == "completed"), key=lambda r: r[0])
    hi = next(r for r in comp if Decimal(r[3]) > T)                      # strictly above threshold
    lo = next(r for r in comp if Decimal(r[3]) < T)
    # zero control: a below-threshold completed line whose order has NO line >= threshold (so order counts move)
    orders_hi = {r[1] for r in comp if Decimal(r[3]) >= T}
    lo_alone = next(r for r in comp if Decimal(r[3]) < T and r[1] not in orders_hi)
    # near-threshold: three completed lines from three different orders that have no other line >= threshold
    near = []
    for r in comp:
        if r[1] not in orders_hi and r[1] not in {x[1] for x in near} and r[0] != lo_alone[0]:
            near.append(r)
        if len(near) == 3:
            break
    picks = {"hi": hi[:4], "lo": lo[:4], "lo_alone": lo_alone[:4], "near": [x[:4] for x in near]}

    res = {
        "selection": {k: ([list(map(str, x)) for x in v] if k == "near" else list(map(str, v))) for k, v in picks.items()},
        "neg_quantity": run_control(p0, "neg_quantity", work,
                                    [(hi[0], -1, Decimal(hi[3])), (lo[0], -1, Decimal(lo[3]))]),
        "zero_quantity": run_control(p0, "zero_quantity", work, [(lo_alone[0], 0, Decimal(lo_alone[3]))],
                                     extra_orders=True),
        "near_threshold": run_control(p0, "near_threshold", work,
                                      [(near[0][0], 3, Decimal("99.99")), (near[1][0], 3, Decimal("100.00")),
                                       (near[2][0], 3, Decimal("100.01"))], extra_orders=True),
    }
    neg, zero, nt = res["neg_quantity"], res["zero_quantity"], res["near_threshold"]
    hi_id, lo_id, la_id = str(hi[0]), str(lo[0]), str(lo_alone[0])
    nt_ids = [str(x[0]) for x in near]
    res["G7"] = {
        "a_negative_diverges": neg["native_ok"] and not neg["yearly_equal"] and not neg["lines_equal"]
        and neg["touched_lines"][lo_id]["in_native_derived"] and not neg["touched_lines"][lo_id]["in_truth"]
        and not neg["touched_lines"][hi_id]["in_native_derived"] and neg["touched_lines"][hi_id]["in_truth"],
        "a_capability_refuses": neg["capability"]["classification"] == cap.UNSUPPORTED
        and "quantity_positive" in neg["capability"]["failed"],
        "b_zero_line_admitted_wrongly": zero["native_ok"] and zero["touched_lines"][la_id]["in_native_derived"]
        and not zero["touched_lines"][la_id]["in_truth"],
        "b_orders_diverge": zero.get("orders_equal") is False,
        "b_revenue_sum_unaffected_observed": zero["yearly_equal"],
        "b_capability_refuses": zero["capability"]["classification"] == cap.UNSUPPORTED
        and "quantity_positive" in zero["capability"]["failed"],
        "c_boundary_exact": nt["native_ok"] and nt["yearly_equal"] and nt["lines_equal"] and nt.get("orders_equal") is True
        and [nt["touched_lines"][i]["in_native_derived"] for i in nt_ids] == [False, True, True],
        "c_capability_derivable": nt["capability"]["classification"] == cap.DERIVABLE,
        "pinned_warehouse_unchanged": all(x["pinned_warehouse_unchanged"] for x in (neg, zero, nt)),
    }
    gate_keys = [k for k in res["G7"] if k != "b_revenue_sum_unaffected_observed"]
    res["G7"]["ok"] = all(res["G7"][k] for k in gate_keys)
    rr.dump(out / "controls.json", res)
    print(json.dumps(res["G7"], indent=1))
    print(json.dumps({k: {kk: res[k][kk] for kk in ("native_yearly", "truth_yearly", "touched_lines", "capability")
                          if kk in res[k]} | ({"native_orders_yearly": res[k].get("native_orders_yearly"),
                                               "truth_orders_yearly": res[k].get("truth_orders_yearly")})
                      for k in ("neg_quantity", "zero_quantity", "near_threshold")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
