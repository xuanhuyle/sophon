"""Collect E3 behavioural evidence after the freeze (PROTOCOL.md §4). The only E3 code that runs MetricFlow.

    .upstream/.venv/bin/python src/collect_evidence.py --upstream .upstream --out evidence

Writes: evidence/identity.json, evidence/catalog.json, evidence/receipts/native/*.json (genuine `mf` through E1's
wrapper over the unmodified E0 adapter), evidence/receipts/guards/*.json (the erratum's guard functions, unmodified),
evidence/receipts/oracle/*.json (the erratum/E2 raw-CSV oracles, unmodified; must equal cases/ORACLE_EXPECTED.json).
Disposable warehouse copies live under runs/snapshots/ (ignored); the pinned warehouse is never written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E3 = HERE.parent
EXP = E3.parent
sys.path.insert(0, str(EXP / "E1_expressibility_erratum" / "src"))
sys.path.insert(0, str(EXP / "E2_blind_discovery" / "src"))
import e2_oracle  # noqa: E402  (E2 oracle, unmodified)
import oracle_b1  # noqa: E402  (erratum oracle, unmodified)
import run_erratum as rr  # noqa: E402  (erratum helpers, unmodified; imports E1 wrapper + E0 adapter)

mfa = rr.mfa


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def dump(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def raw_csv_hashes(raw: Path) -> dict[str, str]:
    return {f.name: mfa.sha256_file(f) for f in sorted(raw.glob("*.csv"))}


def relation(model: dict) -> str:
    return ".".join(model["node_relation"]["relation_name"].replace('"', "").split(".")[1:]).lower()


def catalog(p, wh: Path) -> dict:
    import duckdb
    sm = json.loads(p.semantic_manifest.read_text())
    con = duckdb.connect(str(wh), read_only=True)
    try:
        cols = sorted(f"{s}.{t}.{c}".lower() for s, t, c in con.execute(
            "select table_schema, table_name, column_name from information_schema.columns "
            "where table_schema in ('bronze','silver','gold')").fetchall())
    finally:
        con.close()
    measures, dims, primary = {}, {}, {}
    for m in sm["semantic_models"]:
        rel = relation(m)
        prim = next((e["name"] for e in m.get("entities") or [] if e["type"] == "primary"), None)
        primary[m["name"]] = prim
        for x in m.get("measures") or []:
            measures[x["name"]] = {"model": m["name"], "field": f"{rel}.{(x.get('expr') or x['name']).lower()}", "agg": x["agg"]}
        for d in m.get("dimensions") or []:
            dims[f"{prim}__{d['name']}"] = {"field": f"{rel}.{(d.get('expr') or d['name']).lower()}", "type": d["type"].lower()}
        agg_time = (m.get("defaults") or {}).get("agg_time_dimension")
        if agg_time:
            d = next(d for d in m["dimensions"] if d["name"] == agg_time)
            primary_time = f"{rel}.{(d.get('expr') or d['name']).lower()}"
            dims.setdefault(f"metric_time__year@{m['name']}", {"field": primary_time, "type": "time"})
    metrics = {}
    for mt in sm["metrics"]:
        tp = mt.get("type_params") or {}
        meas = (tp.get("measure") or {}).get("name") if isinstance(tp.get("measure"), dict) else tp.get("measure")
        entry = {"type": mt["type"], "measure": meas, "filter": mt.get("filter")}
        if meas and meas in measures:
            entry.update(model=measures[meas]["model"], field=measures[meas]["field"],
                         primary_entity=primary[measures[meas]["model"]])
        metrics[mt["name"]] = entry
    return {"semantic_manifest_sha256": mfa.sha256_file(p.semantic_manifest), "metrics": metrics, "measures": measures,
            "dimensions": dims, "primary_entities": primary, "warehouse_columns": cols}


def make_copy(src: Path, name: str, mutate) -> Path:
    import duckdb
    d = E3 / "runs" / "snapshots" / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    wh = d / "warehouse.duckdb"  # same file name keeps the manifest's catalog name valid
    shutil.copy(src, wh)
    con = duckdb.connect(str(wh))
    try:
        detail = mutate(con)
        con.execute("checkpoint")
    finally:
        con.close()
    return wh, detail


def mutate_negative_quantity(con):
    rows = con.execute("select sales_id, unit_price from gold.fact_sales where status = 'completed' order by sales_id").fetchall()
    hi = next(r for r in rows if r[1] > 100)
    lo = next(r for r in rows if r[1] < 100)
    for sid, _ in (hi, lo):
        con.execute("update gold.fact_sales set quantity = -1, revenue = cast(-1 * unit_price as decimal(12,2)) where sales_id = ?", [sid])
    return {"set_quantity_minus_1": [{"sales_id": hi[0], "unit_price": str(hi[1])}, {"sales_id": lo[0], "unit_price": str(lo[1])}]}


def mutate_value_changed(con):
    sid, rev = con.execute("select f.sales_id, f.revenue from gold.fact_sales f join gold.dim_customers c using (customer_id) "
                           "where f.status = 'completed' and c.country = 'France' order by f.sales_id limit 1").fetchone()
    con.execute("update gold.fact_sales set revenue = revenue + 100.00 where sales_id = ?", [sid])
    return {"revenue_plus_100": {"sales_id": sid, "old_revenue": str(rev)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    p0 = mfa.open_project(a.upstream)
    raw = p0.upstream / "data" / "raw"
    plan = json.loads((E3 / "cases" / "RECEIPT_PLAN.json").read_text())
    expected_oracle = json.loads((E3 / "cases" / "ORACLE_EXPECTED.json").read_text())

    # identity (C0)
    e0 = json.loads((EXP / "E0_native_adapter" / "evidence" / "regen" / "run_receipt.json").read_text())
    rb = json.loads((E3 / "runs" / "e0_rebuild" / "run_receipt.json").read_text())
    freeze = subprocess.run(["uv", "pip", "freeze", "--python", str(p0.python)], capture_output=True, text=True).stdout
    csv_now = raw_csv_hashes(raw)
    identity = {"upstream_commit": rb["upstream_commit"], "upstream_commit_ok": rb["upstream_commit"] == e0["upstream_commit"],
                "env_freeze_sha256": sha_text(freeze),
                "env_freeze_ok": freeze == (EXP / "E0_native_adapter" / "evidence" / "env_freeze.txt").read_text(),
                "semantic_manifest_sha256": mfa.sha256_file(p0.semantic_manifest),
                "semantic_manifest_ok": mfa.sha256_file(p0.semantic_manifest) == e0["fingerprints_final"]["semantic_manifest_sha256"],
                "raw_csv_sha256": csv_now, "raw_csv_ok": csv_now == {k: v["sha256"] for k, v in e0["S1_csv"].items()},
                "mf_identity": mfa.mf_identity(p0)}
    identity["ok"] = all(identity[k] for k in ("upstream_commit_ok", "env_freeze_ok", "semantic_manifest_ok", "raw_csv_ok"))
    dump(out / "identity.json", identity)
    dump(out / "catalog.json", catalog(p0, p0.warehouse))

    # snapshots
    snaps = {"PINNED": (p0.warehouse, {"unmodified": True})}
    snaps["COPY_NEGATIVE_QUANTITY"] = make_copy(p0.warehouse, "COPY_NEGATIVE_QUANTITY", mutate_negative_quantity)
    snaps["COPY_VALUE_CHANGED"] = make_copy(p0.warehouse, "COPY_VALUE_CHANGED", mutate_value_changed)
    pinned_sha_before = mfa.sha256_file(p0.warehouse)
    snap_meta = {k: {"warehouse_sha256": mfa.sha256_file(v[0]), "mutation": v[1]} for k, v in snaps.items()}
    dump(out / "snapshots.json", snap_meta)

    # native receipts
    for rid, spec in plan["native"].items():
        wh = snaps[spec["snapshot"]][0]
        p = mfa.open_project(a.upstream, warehouse=wh)
        q = spec["query"]
        res = rr.e1.native_query_with_where(p, q["metric"], q["group_by"], q["where"])
        rows = res["rows"]
        dump(out / "receipts" / "native" / f"{rid}.json", {
            "receipt_id": rid, "kind": "NATIVE_METRICFLOW", "snapshot": spec["snapshot"], "query": q,
            "exit_code": res["receipt"]["exit_code"], "ok": res["ok"], "rows": rows, "rows_sha256": sha_text(canon(rows)),
            "mf_csv_sha256": res["receipt"].get("csv_sha256"), "argv": res["receipt"]["argv"],
            "mf_identity": res["receipt"].get("mf_identity"),
            "stdout_tail": (res["receipt"].get("stdout") or "")[-800:] if not res["ok"] else None,
            "fingerprint": {"semantic_manifest_sha256": mfa.sha256_file(p.semantic_manifest), "raw_csv_sha256": raw_csv_hashes(raw),
                            "warehouse_sha256": mfa.sha256_file(wh)}})

    # guard receipts (erratum guard code, unmodified), against the snapshot the S1 native receipt ran on
    s1q = plan["native"]["NR_S1"]["query"]
    prices = rr.csv_prices(raw)
    n_items = len(prices)
    for gid, spec in plan["guards"].items():
        wh = snaps[spec["snapshot"]][0]
        p = mfa.open_project(a.upstream, warehouse=wh)
        ex = rr.explain_with_where(p, s1q["metric"], s1q["group_by"], " AND ".join(s1q["where"]))
        g = rr.guards(rr.warehouse_lines(wh), prices, n_items, ex["sql"])
        names = ("quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison")
        dump(out / "receipts" / "guards" / f"{gid}.json", {
            "receipt_id": gid, "kind": "GUARD", "snapshot": spec["snapshot"], "warehouse_sha256": mfa.sha256_file(wh),
            "guards": {n: g[n]["ok"] for n in names}, "detail": {n: g[n] for n in names},
            "compiled_sql_sha256": sha_text(ex["sql"] or ""), "compiled_sql": ex["sql"]})

    # oracle receipts (raw CSVs only)
    funcs = {"OR_S1": lambda: oracle_b1.compute(raw)["by_year"],
             "OR_S2_CUSTOMER": lambda: e2_oracle.DIAGNOSTICS["H3_reading_customer_country"](raw),
             "OR_S2_STORE": lambda: e2_oracle.DIAGNOSTICS["H3_reading_store_country"](raw),
             "OR_S3": lambda: e2_oracle.h6(raw),
             "OR_S4_PROXY": lambda: e2_oracle.DIAGNOSTICS["H1_rejected_status_proxy"](raw)}
    oracle_ok = True
    for oid, fn in funcs.items():
        exp = expected_oracle["oracles"][oid]
        by_year = fn()
        oracle_ok &= by_year == exp["by_year"]
        dump(out / "receipts" / "oracle" / f"{oid}.json", {
            "receipt_id": oid, "kind": "INDEPENDENT_ORACLE", "computes": exp["computes"], "by_year": by_year,
            "equals_frozen_expectation": by_year == exp["by_year"], "raw_csv_sha256": raw_csv_hashes(raw),
            "code": exp["code"], "code_sha256": mfa.sha256_file(EXP.parent / exp["code"])})
    summary = {"identity_ok": identity["ok"], "oracle_equals_frozen": oracle_ok,
               "pinned_warehouse_unchanged": pinned_sha_before == mfa.sha256_file(p0.warehouse),
               "native": {rid: json.loads((out / "receipts" / "native" / f"{rid}.json").read_text())["exit_code"] for rid in plan["native"]}}
    dump(out / "collection_summary.json", summary)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
