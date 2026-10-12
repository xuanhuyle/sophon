#!/usr/bin/env python3
"""Build the sanitized solver packet from the pinned upstream only (PROTOCOL.md section 4).

    .upstream/.venv/bin/python src/build_packet.py --upstream .upstream --out packet

Inputs: upstream semantic YAML, dbt models/macros/project file, raw-data generator and loaders, native MetricFlow
listings (`mf list metrics|dimensions|entities` via the E0 adapter's runner), warehouse information_schema and the
observed values of every VARCHAR/BOOLEAN column with at most 12 distinct values (mechanical rule, not hand-picked),
raw CSV headers, the task text and CASES.json clauses. Never reads E0/E1 experiment files other than importing the
E0 adapter code. Writes packet/solver_input.txt (the exact bytes sent to the solver) and packet/PACKET_MANIFEST.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E2 = HERE.parent
sys.path.insert(0, str(E2.parent / "E0_native_adapter" / "src"))
import mf_adapter as mfa  # noqa: E402

UPSTREAM_FILES = [
    "dbt/retail_dwh/models/marts/semantic/_semantic_models.yml",
    "dbt/retail_dwh/models/marts/semantic/_metrics.yml",
    "dbt/retail_dwh/models/streaming/_semantic_live.yml",
    "dbt/retail_dwh/dbt_project.yml",
    "dbt/retail_dwh/models/staging/_sources.yml",
    "dbt/retail_dwh/models/staging/_staging.yml",
    "dbt/retail_dwh/models/staging/stg_customers.sql",
    "dbt/retail_dwh/models/staging/stg_orders.sql",
    "dbt/retail_dwh/models/staging/stg_order_items.sql",
    "dbt/retail_dwh/models/staging/stg_products.sql",
    "dbt/retail_dwh/models/staging/stg_stores.sql",
    "dbt/retail_dwh/models/marts/_marts.yml",
    "dbt/retail_dwh/models/marts/facts/fact_sales.sql",
    "dbt/retail_dwh/models/marts/facts/fact_customer_orders.sql",
    "dbt/retail_dwh/models/marts/dimensions/dim_customers.sql",
    "dbt/retail_dwh/models/marts/dimensions/dim_products.sql",
    "dbt/retail_dwh/models/marts/dimensions/dim_stores.sql",
    "dbt/retail_dwh/models/marts/dimensions/dim_dates.sql",
    "dbt/retail_dwh/models/streaming/_streaming.yml",
    "dbt/retail_dwh/models/streaming/stg_order_events.sql",
    "dbt/retail_dwh/models/streaming/fact_sales_live.sql",
    "dbt/retail_dwh/models/streaming/rt_freshness.sql",
    "dbt/retail_dwh/models/_exposures.yml",
    "dbt/retail_dwh/macros/portability.sql",
    "scripts/generate_raw_data.py",
    "scripts/load_bronze.py",
    "governed_analytics_agent/streaming.py",
]
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def clean(text: str, up: Path) -> str:
    text = ANSI.sub("", text).replace(str(up), "<upstream>")
    keep = [l for l in text.splitlines() if not re.search(r"new version of the MetricFlow CLI|pip install --upgrade|Please update to version|Looking for all available", l)]
    return "\n".join(keep).strip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    up = Path(a.upstream).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = mfa.open_project(up)
    files: dict[str, str] = {}

    clauses = json.loads((E2 / "CASES.json").read_text(encoding="utf-8"))
    files["00_TASK.md"] = (HERE / "task_text.md").read_text(encoding="utf-8")
    files["01_CLAUSES.md"] = "# Clauses (LAB_AUTHORED)\n\nProvenance: " + clauses["provenance"] + "\n\n" + "".join(
        f"- **{cid}**: {txt}\n" for cid, txt in clauses["clauses"].items())
    for f in UPSTREAM_FILES:
        files["10_upstream/" + f] = (up / f).read_text(encoding="utf-8")

    sm = json.loads(p.semantic_manifest.read_text(encoding="utf-8"))
    metrics = sorted(m["name"] for m in sm["metrics"])
    cat = ["# Native MetricFlow catalog listings (MetricFlow 0.211.0 via dbt-metricflow 0.13.0, `mf` CLI)\n"]
    r = mfa._run(p, ["list", "metrics"])  # noqa: SLF001
    cat += ["## $ mf list metrics", "```", clean(r["stdout"], up), "```"]
    for m in metrics:
        r = mfa._run(p, ["list", "dimensions", "--metrics", m])  # noqa: SLF001
        cat += [f"## $ mf list dimensions --metrics {m}", "```", clean(r["stdout"], up), "```"]
        r = mfa._run(p, ["list", "entities", "--metrics", m])  # noqa: SLF001
        cat += [f"## $ mf list entities --metrics {m}", "```", clean(r["stdout"], up), "```"]
    files["20_native_catalog.md"] = "\n".join(cat) + "\n"

    import duckdb
    con = duckdb.connect(str(p.warehouse), read_only=True)
    cols = con.execute("select table_schema, table_name, column_name, data_type from information_schema.columns "
                       "order by table_schema, table_name, ordinal_position").fetchall()
    types = dict(con.execute("select table_schema||'.'||table_name, table_type from information_schema.tables").fetchall())
    lines = ["# Warehouse schema (DuckDB file built by the upstream pipeline; every relation and column)\n"]
    cur = None
    for s, t, c, d in cols:
        if (s, t) != cur:
            cur = (s, t)
            lines.append(f"\n## {s}.{t} ({types.get(s + '.' + t)})")
        lines.append(f"- {c}: {d}")
    lines.append("\n# Observed values of every VARCHAR or BOOLEAN column with at most 12 distinct values (row counts)\n")
    for s, t, c, d in cols:
        if d in ("VARCHAR", "BOOLEAN"):
            n = con.execute(f'select count(distinct "{c}") from "{s}"."{t}"').fetchone()[0]
            if 0 < n <= 12:
                vals = con.execute(f'select "{c}", count(*) from "{s}"."{t}" group by 1 order by 1').fetchall()
                lines.append(f"- {s}.{t}.{c}: " + ", ".join(f"{v!r}={k}" for v, k in vals))
    counts = [f"- {s}.{t}: {con.execute(f'select count(*) from {s}.{t}').fetchone()[0]} rows" for s, t in sorted({(c[0], c[1]) for c in cols})]
    con.close()
    lines.append("\n# Row counts\n")
    lines += counts
    files["30_warehouse_schema.md"] = "\n".join(lines) + "\n"

    raw = up / "data" / "raw"
    hdr = ["# Raw landing files (CSV headers; written by scripts/generate_raw_data.py, loaded into schema bronze)\n"]
    for f in sorted(raw.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            hdr.append(f"- data/raw/{f.name}: " + ", ".join(next(csv.reader(fh))))
    files["40_raw_headers.md"] = "\n".join(hdr) + "\n"

    manifest = {"files": {}, "solver_input_sha256": None}
    parts = []
    for name in sorted(files):
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[name], encoding="utf-8")
        manifest["files"][name] = hashlib.sha256(files[name].encode("utf-8")).hexdigest()
        parts.append(f"\n\n===== FILE: {name} =====\n\n{files[name]}")
    solver_input = files["00_TASK.md"] + "\n\n# EVIDENCE PACKET\n" + "".join(parts[1:])
    (out / "solver_input.txt").write_text(solver_input, encoding="utf-8")
    manifest["solver_input_sha256"] = hashlib.sha256(solver_input.encode("utf-8")).hexdigest()
    manifest["solver_input_bytes"] = len(solver_input.encode("utf-8"))
    (out / "PACKET_MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "solver_input_bytes": manifest["solver_input_bytes"], "sha256": manifest["solver_input_sha256"]}))


if __name__ == "__main__":
    main()
