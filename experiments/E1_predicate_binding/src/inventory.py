#!/usr/bin/env python3
"""Bounded-estate inventory snapshot for E1 (read-only).

    .upstream/.venv/bin/python src/inventory.py --upstream .upstream --out evidence/inventory_snapshot.json

The bounded inspected estate is exactly: the five raw landing CSVs written by the upstream generator (headers),
every relation in the DuckDB warehouse built by the upstream pipeline (information_schema columns; bronze, silver,
gold), every dbt node and source in target/manifest.json, every semantic model / metric in
target/semantic_manifest.json, and the native MetricFlow dimension list for the target metric
(`mf list dimensions --metrics <metric>` through the E0 adapter). Nothing else is inspected; absence from this
estate is not absence from the world.

`estate_fingerprint` is the sha256 of the canonical JSON of the raw headers, warehouse columns and dbt
node/source list; the E1 evaluator recomputes it live and refuses NOT_FOUND claims if it differs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "E0_native_adapter" / "src"))
import mf_adapter as mfa  # noqa: E402  (E0 adapter, imported unmodified)


def canon_sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def estate(p: mfa.Project) -> dict:
    import duckdb
    raw = p.upstream / "data" / "raw"
    headers = {}
    for f in sorted(raw.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            headers[f.name] = next(csv.reader(fh))
    con = duckdb.connect(str(p.warehouse), read_only=True)
    cols = [list(r) for r in con.execute(
        "select table_schema, table_name, column_name, data_type from information_schema.columns "
        "order by table_schema, table_name, ordinal_position").fetchall()]
    con.close()
    man = json.loads(p.dbt_manifest.read_text(encoding="utf-8"))
    nodes = sorted([k, v.get("original_file_path"), v.get("resource_type")] for k, v in {**man["nodes"], **man["sources"]}.items()
                   if v.get("resource_type") in ("model", "source", "seed", "snapshot"))
    return {"raw_csv_headers": headers, "warehouse_columns": cols, "dbt_nodes": nodes}


def semantic_catalog(p: mfa.Project) -> dict:
    sm = json.loads(p.semantic_manifest.read_text(encoding="utf-8"))
    models = []
    for m in sm["semantic_models"]:
        models.append({
            "name": m["name"], "relation": (m.get("node_relation") or {}).get("alias"),
            "primary_entity": next((e["name"] for e in m.get("entities") or [] if e.get("type") == "primary"), None),
            "entities": [[e["name"], e.get("type"), e.get("expr")] for e in m.get("entities") or []],
            "dimensions": [[d["name"], d.get("type"), d.get("expr")] for d in m.get("dimensions") or []],
            "measures": [[x["name"], x.get("agg"), x.get("expr")] for x in m.get("measures") or []],
            "agg_time_dimension": (m.get("defaults") or {}).get("agg_time_dimension"),
        })
    metrics = [{"name": m["name"], "type": m.get("type"), "measure": ((m.get("type_params") or {}).get("measure") or {}).get("name"),
                "filters": [w.get("where_sql_template") for w in ((m.get("filter") or {}).get("where_filters") or [])]}
               for m in sm["metrics"]]
    return {"semantic_models": models, "metrics": sorted(metrics, key=lambda x: x["name"])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--metric", default="completed_revenue")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    p = mfa.open_project(a.upstream)
    est = estate(p)
    dims = mfa.list_dimensions(p, a.metric)
    snap = {
        "upstream_commit": __import__("subprocess").run(["git", "-C", str(p.upstream), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "estate": est, "estate_fingerprint": canon_sha(est),
        "semantic_catalog": semantic_catalog(p),
        "native_dimensions_for_metric": {"metric": a.metric, "dimensions": dims["dimensions"], "exit_code": dims["receipt"]["exit_code"],
                                         "stdout_sha256": dims["receipt"]["stdout_sha256"]},
        "fingerprints": mfa.fingerprints(p),
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"estate_fingerprint": snap["estate_fingerprint"], "relations": len({(c[0], c[1]) for c in est["warehouse_columns"]}),
                      "columns": len(est["warehouse_columns"]), "dbt_nodes": len(est["dbt_nodes"]), "dims": dims["dimensions"],
                      "semantic_manifest": snap["fingerprints"]["semantic_manifest_sha256"]}, indent=1))


if __name__ == "__main__":
    main()
