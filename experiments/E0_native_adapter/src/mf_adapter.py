"""Thin read-only adapter over a dbt project's native MetricFlow interface (E0).

It never computes a metric itself and never returns a value that the native `mf` CLI did not write. Every call
returns a receipt (argv, cwd, environment keys used, exit code, elapsed time, stdout/stderr sha256, and the
sha256 of the `mf` entry point, the semantic manifest, the dbt manifest and the warehouse file) so that a fresh
process can re-check what ran.

Public functions:
    open_project(upstream_dir, warehouse=None, mf=None) -> Project
    mf_identity(project)                    -> verifies `mf` is the entry point installed by dbt-metricflow
    list_metrics(project)                   -> names from `mf list metrics` and from the semantic manifest
    list_dimensions(project, metric)        -> `mf list dimensions --metrics <metric>`
    inspect_metric(project, name)           -> native identity + lineage from target/semantic_manifest.json
                                               and target/manifest.json
    identity_mismatches(identity, expected) -> [] when the native definition matches the expected one
    query(project, metrics, group_by, order)-> rows parsed from the CSV that `mf query --csv` wrote, + receipt
    explain(project, ...)                   -> compiled SQL from `mf query --explain`
    fingerprints(project)                   -> file sha256 values (manifests, warehouse)
Errors: NativeQueryError carries the receipt of the failed native call.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

ENV_KEYS = ("DBT_PROFILES_DIR", "WAREHOUSE_DB")


class NativeQueryError(RuntimeError):
    def __init__(self, message: str, receipt: dict):
        super().__init__(message)
        self.receipt = receipt


class IdentityError(RuntimeError):
    pass


@dataclass(frozen=True)
class Project:
    upstream: Path      # pinned upstream checkout
    dbt_dir: Path       # dbt project directory (cwd for mf)
    warehouse: Path     # DuckDB file the dbt profile points to
    mf: Path            # native MetricFlow CLI entry point
    python: Path        # interpreter of the locked environment

    @property
    def semantic_manifest(self) -> Path:
        return self.dbt_dir / "target" / "semantic_manifest.json"

    @property
    def dbt_manifest(self) -> Path:
        return self.dbt_dir / "target" / "manifest.json"

    def env(self) -> dict[str, str]:
        return {**os.environ, "DBT_PROFILES_DIR": str(self.dbt_dir), "WAREHOUSE_DB": str(self.warehouse)}


def sha256_file(p: Path) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def open_project(upstream: str | Path, warehouse: str | Path | None = None, mf: str | Path | None = None) -> Project:
    up = Path(upstream).resolve()
    venv_bin = up / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    mf_path = Path(mf).resolve() if mf else venv_bin / ("mf.exe" if os.name == "nt" else "mf")
    py = venv_bin / ("python.exe" if os.name == "nt" else "python")
    wh = Path(warehouse).resolve() if warehouse else up / "data" / "warehouse.duckdb"
    return Project(upstream=up, dbt_dir=up / "dbt" / "retail_dwh", warehouse=wh, mf=mf_path, python=py)


def fingerprints(p: Project) -> dict:
    return {
        "semantic_manifest_sha256": sha256_file(p.semantic_manifest),
        "dbt_manifest_sha256": sha256_file(p.dbt_manifest),
        "warehouse_sha256": sha256_file(p.warehouse),
        "warehouse_bytes": p.warehouse.stat().st_size if p.warehouse.exists() else None,
    }


def mf_identity(p: Project) -> dict:
    """The `mf` entry point must be the file the installed dbt-metricflow distribution recorded (RECORD hash).
    Raises IdentityError otherwise (for example a stub executable that prints canned results)."""
    site = subprocess.run([str(p.python), "-c", "import sysconfig;print(sysconfig.get_paths()['purelib'])"],
                          capture_output=True, text=True, check=True).stdout.strip()
    dists = sorted(Path(site).glob("dbt_metricflow-*.dist-info"))
    if len(dists) != 1:
        raise IdentityError(f"expected one dbt_metricflow distribution in {site}, found {len(dists)}")
    record = (dists[0] / "RECORD").read_text(encoding="utf-8")
    entry = None
    for line in record.splitlines():
        path, _, rest = line.partition(",")
        rel = Path(path.replace("\\", "/"))
        if rel.name in ("mf", "mf.exe") and rel.parent.name in ("bin", "Scripts"):
            entry = (path, rest.split(",")[0])
            break
    if entry is None:
        raise IdentityError("dbt_metricflow RECORD lists no mf entry point")
    rec_path, rec_hash = entry
    expected_file = (dists[0].parent / rec_path).resolve()
    if p.mf.resolve() != expected_file:
        raise IdentityError(f"mf path {p.mf} is not the entry point installed by dbt-metricflow ({expected_file})")
    digest = base64.urlsafe_b64encode(hashlib.sha256(p.mf.read_bytes()).digest()).rstrip(b"=").decode()
    if f"sha256={digest}" != rec_hash:
        raise IdentityError(f"mf entry point hash {digest} differs from its RECORD entry {rec_hash}")
    versions = subprocess.run(
        [str(p.python), "-c", "import importlib.metadata as m,json;print(json.dumps({k:m.version(k) for k in "
         "['dbt-metricflow','metricflow','dbt-core','dbt-duckdb','dbt-semantic-interfaces','duckdb']}))"],
        capture_output=True, text=True, check=True).stdout
    return {"mf_path": str(p.mf), "mf_sha256": sha256_file(p.mf), "record_entry": rec_path, "record_hash": rec_hash,
            "distribution": dists[0].name, "versions": json.loads(versions)}


def _run(p: Project, args: list[str], timeout: int = 300) -> dict:
    argv = [str(p.mf), *args]
    t0 = time.monotonic()
    proc = subprocess.run(argv, cwd=str(p.dbt_dir), env=p.env(), capture_output=True, text=True, timeout=timeout)
    return {
        "argv": ["mf", *args],
        "cwd": str(p.dbt_dir),
        "env": {k: p.env()[k] for k in ENV_KEYS},
        "exit_code": proc.returncode,
        "elapsed_s": round(time.monotonic() - t0, 3),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "stdout_sha256": sha256_text(proc.stdout),
        "stderr_sha256": sha256_text(proc.stderr),
    }


_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def list_metrics(p: Project) -> dict:
    r = _run(p, ["list", "metrics"])
    if r["exit_code"] != 0:
        raise NativeQueryError("mf list metrics failed", r)
    text = _ANSI.sub("", r["stdout"])
    cli_names = sorted(set(re.findall(r"^\s*[•\-*]\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", text, flags=re.M)))
    manifest_names = sorted(m["name"] for m in json.loads(p.semantic_manifest.read_text(encoding="utf-8"))["metrics"])
    return {"cli_metric_names": cli_names, "manifest_metric_names": manifest_names, "receipt": r}


def list_dimensions(p: Project, metric: str) -> dict:
    r = _run(p, ["list", "dimensions", "--metrics", metric])
    if r["exit_code"] != 0:
        raise NativeQueryError(f"mf list dimensions --metrics {metric} failed", r)
    text = _ANSI.sub("", r["stdout"])
    return {"dimensions": sorted(set(re.findall(r"^\s*[•\-*]\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", text, flags=re.M))), "receipt": r}


def inspect_metric(p: Project, name: str) -> dict:
    """Native identity of one metric from the semantic manifest written by `dbt parse`, traced to its dbt node."""
    sm = json.loads(p.semantic_manifest.read_text(encoding="utf-8"))
    metric = next((m for m in sm["metrics"] if m["name"] == name), None)
    if metric is None:
        raise IdentityError(f"metric {name!r} is not in {p.semantic_manifest}")
    tp = metric.get("type_params") or {}
    measure_ref = (tp.get("measure") or {}).get("name")
    flt = metric.get("filter") or {}
    filters = [w.get("where_sql_template") for w in (flt.get("where_filters") or [])]
    owner = None
    measure = None
    for model in sm["semantic_models"]:
        for ms in model.get("measures") or []:
            if ms["name"] == measure_ref:
                owner, measure = model, ms
    node_relation = (owner or {}).get("node_relation") or {}
    dbt_node = None
    lineage = []
    if owner and p.dbt_manifest.exists():
        man = json.loads(p.dbt_manifest.read_text(encoding="utf-8"))
        target = node_relation.get("alias")
        dbt_node = next((k for k, v in man["nodes"].items() if v.get("resource_type") == "model" and v.get("alias") == target), None)
        seen, todo = set(), [dbt_node] if dbt_node else []
        while todo:
            k = todo.pop()
            if k in seen:
                continue
            seen.add(k)
            node = man["nodes"].get(k) or man["sources"].get(k) or {}
            lineage.append({"unique_id": k, "path": node.get("original_file_path"),
                            "checksum": (node.get("checksum") or {}).get("checksum"),
                            "depends_on": (node.get("depends_on") or {}).get("nodes", [])})
            todo.extend((node.get("depends_on") or {}).get("nodes", []))
    return {
        "metric": name,
        "type": metric.get("type"),
        "label": metric.get("label"),
        "description": metric.get("description"),
        "measure": measure_ref,
        "filters": filters,
        "semantic_model": (owner or {}).get("name"),
        "measure_agg": (measure or {}).get("agg"),
        "measure_expr": (measure or {}).get("expr"),
        "agg_time_dimension": ((owner or {}).get("defaults") or {}).get("agg_time_dimension"),
        "node_relation": node_relation,
        "dbt_node": dbt_node,
        "lineage": sorted(lineage, key=lambda x: x["unique_id"]),
        "metric_definition_sha256": sha256_text(json.dumps(metric, sort_keys=True)),
        "semantic_model_definition_sha256": sha256_text(json.dumps(owner, sort_keys=True)) if owner else None,
    }


def identity_mismatches(identity: dict, expected: dict) -> list[str]:
    out = []
    for k, v in expected.items():
        if identity.get(k) != v:
            out.append(f"{k}: expected {v!r}, native manifest has {identity.get(k)!r}")
    return out


def _query_args(metrics: list[str], group_by: list[str] | None, order: list[str] | None) -> list[str]:
    args = ["query", "--metrics", ",".join(metrics)]
    if group_by:
        args += ["--group-by", ",".join(group_by)]
    if order:
        args += ["--order", ",".join(order)]
    return args


def query(p: Project, metrics: list[str], group_by: list[str] | None = None, order: list[str] | None = None) -> dict:
    """Run `mf query ... --csv`; return the rows MetricFlow wrote. Raises IdentityError before running anything if
    the executable is not the installed MetricFlow entry point, and NativeQueryError on any native failure."""
    identity = mf_identity(p)
    before = fingerprints(p)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "result.csv"
        r = _run(p, [*_query_args(metrics, group_by, order), "--csv", str(out)])
        r["argv"] = [a if a != str(out) else "<csv>" for a in r["argv"]]
        r["csv_written"] = out.exists()
        csv_text = out.read_text(encoding="utf-8") if out.exists() else None
    r["csv_sha256"] = sha256_text(csv_text) if csv_text is not None else None
    r["fingerprints_before"] = before
    r["fingerprints_after"] = fingerprints(p)
    r["mf_identity"] = identity
    if r["exit_code"] != 0 or csv_text is None:
        raise NativeQueryError(f"mf query failed (exit {r['exit_code']}, csv written: {r['csv_written']})", r)
    rows = list(csv.DictReader(csv_text.splitlines()))
    return {"rows": rows, "csv": csv_text, "receipt": r}


def explain(p: Project, metrics: list[str], group_by: list[str] | None = None, order: list[str] | None = None) -> dict:
    mf_identity(p)
    r = _run(p, [*_query_args(metrics, group_by, order), "--explain"])
    if r["exit_code"] != 0:
        raise NativeQueryError("mf query --explain failed", r)
    text = _ANSI.sub("", r["stdout"])
    idx = text.find("SELECT")
    return {"sql": text[idx:].strip() if idx != -1 else None, "receipt": r}
