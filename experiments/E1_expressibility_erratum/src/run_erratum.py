"""E1 expressibility erratum: the frozen reproduction (PROTOCOL.md §3-§7) on the pinned estate.

Run with the locked interpreter of the pinned upstream (it has duckdb), from the erratum directory:
    .upstream/.venv/bin/python src/run_erratum.py --upstream .upstream --out evidence
Native results only come from `mf` via the unmodified E0 adapter / E1 wrapper. The oracle reads raw CSVs only.
Guards read the warehouse read-only and compare in Python Decimal. Negative controls are in src/controls.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ERR = HERE.parent
EXP = ERR.parent
sys.path.insert(0, str(EXP / "E1_predicate_binding" / "src"))
import evaluator as e1  # noqa: E402  (E1 wrapper, unmodified; it imports the unmodified E0 adapter)

mfa = e1.mfa
sys.path.insert(0, str(HERE))
import capability as cap  # noqa: E402
import oracle_b1  # noqa: E402

R = "{{ Metric('revenue', group_by=['sales']) }}"
Q = "{{ Metric('quantity_sold', group_by=['sales']) }}"
S = "{{ Dimension('sales__status') }} = 'completed'"
W = f"{R} >= 100 * {Q} AND {S}"
W_E2 = ("{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }} "
        "AND {{ Dimension('sales__status') }} = 'completed'")
assert W == W_E2  # exact E2 PRIOR.md text
ND_WHERE = "{{ Dimension('sales__unit_price') }} >= 100"
CENT = Decimal("0.01")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=False, default=str) + "\n", encoding="utf-8")


def nq(p, metric: str, group_by: list[str], where: str | None) -> dict:
    return e1.native_query_with_where(p, metric, group_by, [where] if where else [])


def yearly(res: dict, metric: str) -> dict[str, str] | None:
    if not res["ok"]:
        return None
    return {r["metric_time__year"][:4]: str(Decimal(r[metric]).quantize(CENT)) for r in res["rows"]}


def line_rows(res: dict, metric: str = "revenue") -> dict[str, str] | None:
    if not res["ok"]:
        return None
    key = next(k for k in res["rows"][0] if k != metric) if res["rows"] else "sales"
    return {str(r[key]): str(Decimal(r[metric]).quantize(CENT)) for r in res["rows"]}


def explain_with_where(p, metric: str, group_by: list[str], where: str) -> dict:
    """`mf query ... --where ... --explain` through the adapter's own _run (adapter.explain has no --where)."""
    identity = mfa.mf_identity(p)
    r = mfa._run(p, ["query", "--metrics", metric, "--group-by", ",".join(group_by), "--where", where, "--explain"])  # noqa: SLF001
    text = mfa._ANSI.sub("", r["stdout"] or "")  # noqa: SLF001
    # Start at the first line that begins the statement; a CTE-based plan starts with WITH, not SELECT.
    m = re.search(r"^(WITH|SELECT)\b", text, flags=re.M)
    idx = m.start() if m else -1
    r["mf_identity"] = identity
    return {"sql": text[idx:].strip() if r["exit_code"] == 0 and idx != -1 else None, "receipt": r}


def warehouse_lines(wh: Path) -> dict:
    import duckdb  # locked environment of the pinned upstream
    con = duckdb.connect(str(wh), read_only=True)
    try:
        rows = con.execute("select sales_id, order_id, quantity, unit_price, revenue, status, order_date "
                           "from gold.fact_sales").fetchall()
        types = {c[0]: c[1] for c in con.execute("describe gold.fact_sales").fetchall()}
        agg_types = con.execute("select typeof(sum(revenue)), typeof(100 * sum(quantity)), "
                                "typeof(sum(revenue) >= 100 * sum(quantity)) from gold.fact_sales").fetchone()
    finally:
        con.close()
    return {"rows": rows, "types": types, "agg_types": list(agg_types)}


def guards(wh_lines: dict, source_price: dict[str, str], source_item_count: int, compiled_sql: str | None) -> dict:
    rows = wh_lines["rows"]
    ids = [str(r[0]) for r in rows]
    q_min = min(r[2] for r in rows)
    nonpos = [str(r[0]) for r in rows if r[2] is None or r[2] <= 0]
    rev_bad = [str(r[0]) for r in rows if Decimal(r[4]) != Decimal(r[2]) * Decimal(r[3])]
    price_bad = [str(r[0]) for r in rows if source_price.get(str(r[0])) is None
                 or Decimal(source_price[str(r[0])]) != Decimal(r[3])]
    max_dec = max(len(v.split(".", 1)[1]) if "." in v else 0 for v in source_price.values())
    float_tokens = sorted(set(re.findall(r"\b(FLOAT|DOUBLE|REAL|FLOAT4|FLOAT8)\b", (compiled_sql or "").upper())))
    t = wh_lines["types"]
    exact_types = (t.get("quantity", "").upper() == "INTEGER" and t.get("unit_price", "").upper().startswith("DECIMAL")
                   and t.get("revenue", "").upper().startswith("DECIMAL")
                   and not any(x in " ".join(wh_lines["agg_types"][:2]).upper() for x in ("FLOAT", "DOUBLE")))
    return {
        "quantity_positive": {"ok": not nonpos, "min_quantity": q_min, "nonpositive_ids": nonpos[:20],
                              "nonpositive_count": len(nonpos)},
        "revenue_exact": {"ok": not rev_bad, "mismatch_ids": rev_bad[:20], "mismatch_count": len(rev_bad),
                          "rule": "Decimal(revenue) == quantity * Decimal(unit_price) for every fact_sales row"},
        "price_source_exact": {"ok": not price_bad and max_dec <= 2, "mismatch_ids": price_bad[:20],
                               "mismatch_count": len(price_bad), "source_max_decimals": max_dec},
        "line_entity_unique": {"ok": len(ids) == len(set(ids)) == source_item_count, "fact_rows": len(ids),
                               "distinct_sales_id": len(set(ids)), "source_order_items": source_item_count},
        "exact_comparison": {"ok": bool(compiled_sql) and not float_tokens and exact_types,
                             "float_tokens_in_compiled_sql": float_tokens, "column_types": t,
                             "duckdb_types_sum_revenue__100x_sum_quantity__comparison": wh_lines["agg_types"]},
    }


def csv_prices(raw: Path) -> dict[str, str]:
    with (raw / "order_items.csv").open(newline="", encoding="utf-8") as f:
        return {r["order_item_id"]: r["unit_price"] for r in csv.DictReader(f)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rebuild-receipt", default=str(ERR / "runs" / "e0_rebuild" / "run_receipt.json"))
    a = ap.parse_args()
    out = Path(a.out)
    p = mfa.open_project(a.upstream)
    raw = p.upstream / "data" / "raw"
    started = now()

    # ---------------- G1 source identity
    e0 = json.loads((EXP / "E0_native_adapter" / "evidence" / "regen" / "run_receipt.json").read_text())
    rb = json.loads(Path(a.rebuild_receipt).read_text())
    freeze = subprocess.run(["uv", "pip", "freeze", "--python", str(p.python)], capture_output=True, text=True).stdout
    e0_freeze = (EXP / "E0_native_adapter" / "evidence" / "env_freeze.txt").read_text()
    fp = mfa.fingerprints(p)
    n0 = nq(p, "completed_revenue", ["metric_time__year"], None)
    e0_n0 = {r["metric_time__year"][:4]: str(Decimal(r["completed_revenue"]).quantize(CENT)) for r in e0["S7_query"]["rows"]}
    csv_now = {k: v["sha256"] for k, v in rb["S1_csv"].items()}
    csv_e0 = {k: v["sha256"] for k, v in e0["S1_csv"].items()}
    g1 = {
        "upstream_commit": rb["upstream_commit"], "upstream_commit_ok": rb["upstream_commit"] == e0["upstream_commit"],
        "env_freeze_sha256": mfa.sha256_text(freeze), "env_freeze_ok": freeze == e0_freeze,
        "semantic_manifest_sha256": fp["semantic_manifest_sha256"],
        "semantic_manifest_ok": fp["semantic_manifest_sha256"] == e0["fingerprints_final"]["semantic_manifest_sha256"],
        "csv_sha256": csv_now, "csv_ok": csv_now == csv_e0,
        "N0_completed_revenue": yearly(n0, "completed_revenue"), "N0_e0": e0_n0,
    }
    g1["N0_ok"] = g1["N0_completed_revenue"] == e0_n0
    g1["ok"] = all(g1[k] for k in ("upstream_commit_ok", "env_freeze_ok", "semantic_manifest_ok", "csv_ok", "N0_ok"))
    dump(out / "identity.json", {**g1, "fingerprints": fp, "N0_receipt": n0["receipt"]})

    # ---------------- native queries
    n1 = nq(p, "revenue", ["metric_time__year"], None)
    n2 = nq(p, "revenue", ["metric_time__year"], S)
    nw = nq(p, "revenue", ["metric_time__year"], W)
    nw_sql = explain_with_where(p, "revenue", ["metric_time__year"], W)
    nl = nq(p, "revenue", ["sales"], W)
    nv = nq(p, "completed_revenue", ["metric_time__year"], f"{R} >= 100 * {Q}")
    nd = nq(p, "revenue", [], ND_WHERE)
    ld = mfa.list_dimensions(p, "revenue")
    native = {"N1": n1, "N2": n2, "NW": nw, "NL": nl, "NV": nv, "ND": nd}
    for k, v in native.items():
        dump(out / "native" / f"{k}.json", {"ok": v["ok"], "row_count": len(v["rows"]), "rows": v["rows"],
                                            "receipt": v["receipt"]})
    (out / "native" / "NW_compiled.sql").write_text((nw_sql["sql"] or "") + "\n", encoding="utf-8")
    dump(out / "native" / "NW_explain_receipt.json", {**nw_sql["receipt"], "stdout": "(see NW_compiled.sql)"})
    dump(out / "native" / "LD.json", ld)

    nat = {"N1": yearly(n1, "revenue"), "N2": yearly(n2, "revenue"), "NW": yearly(nw, "revenue"),
           "NV": yearly(nv, "completed_revenue")}
    nl_lines = line_rows(nl)

    # ---------------- oracle (raw CSVs only)
    orc = oracle_b1.compute(raw)
    dump(out / "oracle_b1.json", orc)

    sql = nw_sql["sql"] or ""
    sql_u = sql.upper()
    g2 = {"NW_exit_code": nw["receipt"]["exit_code"], "NW_argv": nw["receipt"]["argv"],
          "where_text_equals_E2": nw["receipt"]["argv"][nw["receipt"]["argv"].index("--where") + 1] == W_E2,
          "explain_exit_code": nw_sql["receipt"]["exit_code"],
          "sql_groups_metric_subqueries_by_sales_id": sql_u.count("GROUP BY") >= 3 and "SALES_ID" in sql_u
          and "SUM(" in sql_u and "QUANTITY" in sql_u,
          "sql_has_threshold_comparison": bool(re.search(r">=\s*100\s*\*", sql))}
    g2["ok"] = (nw["ok"] and g2["where_text_equals_E2"] and g2["explain_exit_code"] == 0
                and g2["sql_groups_metric_subqueries_by_sales_id"] and g2["sql_has_threshold_comparison"])
    g3 = {"native_NW": nat["NW"], "oracle": orc["by_year"], "ok": nat["NW"] == orc["by_year"]}
    g4 = {"native_line_count": len(nl_lines or {}), "oracle_line_count": orc["line_count"],
          "ids_equal": nl_lines is not None and set(nl_lines) == set(orc["lines"]),
          "amounts_equal": nl_lines == orc["lines"],
          "only_native": sorted(set(nl_lines or {}) - set(orc["lines"]), key=int)[:20],
          "only_oracle": sorted(set(orc["lines"]) - set(nl_lines or {}), key=int)[:20]}
    g4["ok"] = g4["ids_equal"] and g4["amounts_equal"]

    # ---------------- G5 guards (warehouse read-only; Python Decimal)
    wh = warehouse_lines(p.warehouse)
    prices = csv_prices(raw)
    g5 = guards(wh, prices, orc["csv_facts"]["order_items"], nw_sql["sql"])
    g5["csv_facts"] = orc["csv_facts"]
    g5["csv_quantity_positive"] = orc["csv_facts"]["min_quantity"] is not None and orc["csv_facts"]["min_quantity"] >= 1
    g5["ok"] = all(g5[k]["ok"] for k in cap.GUARDS) and g5["csv_quantity_positive"]
    dump(out / "guards.json", g5)

    # ---------------- G6 anti-vacuity
    with (raw / "orders.csv").open(newline="", encoding="utf-8") as f:
        status = {r["order_id"]: r["status"] for r in csv.DictReader(f)}
    with (raw / "order_items.csv").open(newline="", encoding="utf-8") as f:
        completed = [r for r in csv.DictReader(f) if status.get(r["order_id"]) == "completed"]
    below = min((r for r in completed if Decimal(r["unit_price"]) < 100), key=lambda r: int(r["order_item_id"]))
    above = min((r for r in completed if Decimal(r["unit_price"]) >= 100), key=lambda r: int(r["order_item_id"]))
    strict = all(nat["NW"] and nat["N2"] and nat["N1"] and Decimal(nat["NW"][y]) < Decimal(nat["N2"][y]) < Decimal(nat["N1"][y])
                 for y in (nat["NW"] or {}))
    g6 = {"NW": nat["NW"], "N2_status_only": nat["N2"], "N1_unfiltered": nat["N1"], "strict_NW_lt_N2_lt_N1": strict,
          "below_threshold_line": {"order_item_id": below["order_item_id"], "unit_price": below["unit_price"],
                                   "quantity": below["quantity"], "in_native_NL": below["order_item_id"] in (nl_lines or {})},
          "above_threshold_line": {"order_item_id": above["order_item_id"], "unit_price": above["unit_price"],
                                   "quantity": above["quantity"], "in_native_NL": above["order_item_id"] in (nl_lines or {})},
          "ND_direct_dimension_probe": {"where": ND_WHERE, "accepted": nd["ok"], "exit_code": nd["receipt"]["exit_code"],
                                        "stderr_tail": (nd["receipt"].get("stderr") or "")[-600:],
                                        "stdout_tail": (nd["receipt"].get("stdout") or "")[-600:]},
          "NW_accepted": nw["ok"],
          "LD_unit_price_dimensions": [d for d in ld["dimensions"] if "unit_price" in d],
          "LD_dimension_count": len(ld["dimensions"])}
    g6["ok"] = (strict and not g6["below_threshold_line"]["in_native_NL"] and g6["above_threshold_line"]["in_native_NL"]
                and not nd["ok"] and nd["receipt"]["exit_code"] != 0 and nw["ok"] and not g6["LD_unit_price_dimensions"])
    dump(out / "anti_vacuity.json", g6)

    # ---------------- capability on the pinned evidence
    sm = json.loads(p.semantic_manifest.read_text())
    src_col = "unit_price" in wh["types"]
    direct = any(d["name"] == "unit_price" or (d.get("expr") or d["name"]) == "unit_price"
                 for m in sm["semantic_models"] for d in m.get("dimensions") or []) or bool(g6["LD_unit_price_dimensions"])
    evidence = {"source_column_present": src_col, "direct_dimension_present": direct, "native_witness_accepted": nw["ok"],
                "native_equals_oracle_yearly": g3["ok"], "native_equals_oracle_lines": g4["ok"],
                "guards": {k: g5[k]["ok"] for k in cap.GUARDS}}
    capres = {"evidence": evidence, "result": cap.classify(evidence)}
    dump(out / "capability.json", capres)

    summary = {"started_utc": started, "finished_utc": now(), "G1": g1["ok"], "G2": g2, "G3": g3, "G4": g4,
               "G5": {k: g5[k]["ok"] for k in cap.GUARDS} | {"csv_quantity_positive": g5["csv_quantity_positive"],
                                                              "ok": g5["ok"]},
               "G6": g6["ok"], "native_yearly": nat, "capability": capres["result"],
               "fingerprints_after": mfa.fingerprints(p)}
    dump(out / "reproduction_summary.json", summary)
    print(json.dumps({k: (v["ok"] if isinstance(v, dict) and "ok" in v else v) for k, v in summary.items()
                      if k.startswith("G")} | {"NW": nat["NW"], "oracle": orc["by_year"], "NV": nat["NV"],
                                               "capability": capres["result"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
