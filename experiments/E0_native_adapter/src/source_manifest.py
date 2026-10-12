#!/usr/bin/env python3
"""Write the E0 source/environment manifest (run with the upstream virtualenv's interpreter).

    .upstream/.venv/bin/python src/source_manifest.py --upstream .upstream --out evidence/SOURCE_MANIFEST.json

Records the pinned upstream revision, licence, lock and declaration hashes, the sha256 of every file that
defines the selected metric's lineage, the native runtime versions as installed, the interpreter and the
platform. Reads files only; runs no dbt or MetricFlow command.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import platform
import subprocess
import sys
from pathlib import Path

LINEAGE_FILES = [
    "LICENSE", "pyproject.toml", "uv.lock", "requirements.txt", ".python-version", "Makefile",
    ".github/workflows/ci.yml",
    "scripts/generate_raw_data.py", "scripts/load_bronze.py",
    "dbt/retail_dwh/dbt_project.yml", "dbt/retail_dwh/profiles.yml",
    "dbt/retail_dwh/macros/portability.sql", "dbt/retail_dwh/macros/generate_schema_name.sql",
    "dbt/retail_dwh/models/staging/_sources.yml",
    "dbt/retail_dwh/models/staging/stg_orders.sql", "dbt/retail_dwh/models/staging/stg_order_items.sql",
    "dbt/retail_dwh/models/staging/stg_products.sql",
    "dbt/retail_dwh/models/marts/facts/fact_sales.sql",
    "dbt/retail_dwh/models/marts/_marts.yml",
    "dbt/retail_dwh/models/marts/semantic/_semantic_models.yml",
    "dbt/retail_dwh/models/marts/semantic/_metrics.yml",
    "dbt/retail_dwh/models/streaming/_semantic_live.yml",
    "dbt/retail_dwh/models/_exposures.yml",
    "governed_analytics_agent/semantic_layer.py", "governed_analytics_agent/catalog.py",
    "governed_analytics_agent/reporting.py", "governed_analytics_agent/config.py",
    "streamlit_app.py",
]
PACKAGES = ["dbt-core", "dbt-duckdb", "dbt-adapters", "dbt-metricflow", "metricflow", "dbt-semantic-interfaces",
            "duckdb", "sqlglot", "faker", "pandas"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    up = Path(a.upstream).resolve()
    git = lambda *args: subprocess.run(["git", "-C", str(up), *args], capture_output=True, text=True).stdout.strip()  # noqa: E731
    manifest = {
        "upstream": {
            "url": "https://github.com/behramkorkut/Governed-Analytics-Agent",
            "commit": git("rev-parse", "HEAD"),
            "commit_date": git("log", "-1", "--format=%cI"),
            "commit_author": git("log", "-1", "--format=%an"),
            "commit_subject": git("log", "-1", "--format=%s"),
            "worktree_clean": git("status", "--porcelain") == "",
            "licence_first_line": (up / "LICENSE").read_text().splitlines()[0],
        },
        "files_sha256": {f: sha(up / f) for f in LINEAGE_FILES if (up / f).exists()},
        "files_missing": [f for f in LINEAGE_FILES if not (up / f).exists()],
        "runtime": {
            "python": sys.version.split()[0],
            "executable_relative": str(Path(sys.executable).relative_to(up)) if str(sys.executable).startswith(str(up)) else sys.executable,
            "platform": platform.platform(),
            "packages": {p: md.version(p) for p in PACKAGES},
        },
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"commit": manifest["upstream"]["commit"], "files": len(manifest["files_sha256"]),
                      "missing": manifest["files_missing"], "packages": manifest["runtime"]["packages"]}, indent=1))


if __name__ == "__main__":
    main()
