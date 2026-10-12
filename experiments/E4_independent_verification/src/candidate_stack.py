"""Instantiate and execute a CANDIDATE native implementation in its own disposable stack (PROTOCOL.md §4).

build(candidate, snapshot_dir, work) copies the pinned upstream project (without .git/.venv/warehouse/target),
symlinks the locked virtualenv, installs the snapshot's raw CSVs, applies the candidate's text patch to the
semantic YAML / dbt SQL (each `old` must occur exactly once), then runs the upstream loader, `dbt build` and
`dbt parse` against the candidate's own DuckDB file. execute(stack, query) runs genuine `mf` (E1 wrapper over the
unmodified E0 adapter) on that stack and returns rows plus compiled SQL. Nothing here decides conformance.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E4 = HERE.parent
EXP = E4.parent
sys.path.insert(0, str(EXP / "E1_expressibility_erratum" / "src"))
import run_erratum as rr  # noqa: E402  (unmodified: E1 wrapper, E0 adapter, explain, guards)

mfa = rr.mfa
SKIP = {".git", ".venv", "target", "logs", "dbt_packages", "__pycache__", ".pytest_cache"}


def sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _copytree(src: Path, dst: Path) -> None:
    def ignore(d, names):
        out = {n for n in names if n in SKIP or n.endswith((".duckdb", ".duckdb.wal"))}
        if Path(d) == src / "data":
            out.add("raw")
        return out
    shutil.copytree(src, dst, ignore=ignore, symlinks=True)


def apply_patch(root: Path, patch: list[dict]) -> list[dict]:
    diffs = []
    for op in patch:
        f = root / op["file"]
        before = f.read_text(encoding="utf-8")
        if op["op"] == "replace":
            n = before.count(op["old"])
            if n != 1:
                raise ValueError(f"patch anchor occurs {n} times in {op['file']}")
            after = before.replace(op["old"], op["new"])
        elif op["op"] == "append":
            after = before + op["text"]
        else:
            raise ValueError(op)
        f.write_text(after, encoding="utf-8")
        diffs.append({"file": op["file"], "unified_diff": "".join(difflib.unified_diff(
            before.splitlines(True), after.splitlines(True), f"pristine/{op['file']}", f"candidate/{op['file']}"))})
    return diffs


def build(stack_id: str, patch: list[dict], snapshot_dir: Path, pristine: Path, work: Path) -> dict:
    root = work / stack_id
    if root.exists():
        shutil.rmtree(root)
    up = root / "upstream"
    _copytree(pristine, up)
    (up / ".venv").symlink_to(pristine / ".venv")
    (up / "data" / "raw").mkdir(parents=True, exist_ok=True)
    for f in sorted(Path(snapshot_dir).glob("*.csv")):
        shutil.copy(f, up / "data" / "raw" / f.name)
    rec = {"stack_id": stack_id, "upstream": str(up), "patch_ops": len(patch), "ok": False}
    try:
        rec["diffs"] = apply_patch(up, patch)
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"PATCH_FAILED: {e}"
        return rec
    p = mfa.open_project(up)
    env = {**os.environ, **p.env()}
    py, dbt = str(p.python), str(p.python.parent / "dbt")
    proj = ["--project-dir", str(p.dbt_dir), "--profiles-dir", str(p.dbt_dir)]
    steps = {}
    for name, argv in (("load_bronze", [py, "-m", "scripts.load_bronze"]), ("dbt_build", [dbt, "build", *proj]),
                       ("dbt_parse", [dbt, "parse", *proj])):
        r = subprocess.run(argv, cwd=str(up), env=env, capture_output=True, text=True)
        steps[name] = {"exit_code": r.returncode, "tail": (r.stdout + r.stderr)[-1200:]}
        if r.returncode != 0:
            break
    rec["steps"] = steps
    rec["raw_csv_sha256"] = {f.name: sha_file(f) for f in sorted((up / "data" / "raw").glob("*.csv"))}
    rec["semantic_manifest_sha256"] = sha_file(p.semantic_manifest) if p.semantic_manifest.exists() else None
    rec["warehouse"] = str(p.warehouse)
    rec["ok"] = all(s["exit_code"] == 0 for s in steps.values()) and len(steps) == 3 and rec["semantic_manifest_sha256"] is not None
    if not rec["ok"]:
        rec["error"] = "BUILD_FAILED: " + next((k for k, s in steps.items() if s["exit_code"] != 0), "semantic manifest missing")
    return rec


def execute(stack: dict, query: dict) -> dict:
    """Genuine `mf query` on the candidate's own stack; also the compiled SQL via --explain."""
    p = mfa.open_project(Path(stack["upstream"]))
    out = {"query": query}
    try:
        r = rr.e1.native_query_with_where(p, query["metric"], query["group_by"], query["where"])
        out.update(ok=r["ok"], exit_code=r["receipt"]["exit_code"], argv=r["receipt"]["argv"], rows=r["rows"],
                   rows_sha256=sha_text(json.dumps(r["rows"], sort_keys=True)), mf_identity=r["receipt"].get("mf_identity"),
                   stdout_tail=None if r["ok"] else (r["receipt"].get("stdout") or "")[-900:])
        if r["ok"]:
            args = ["query", "--metrics", query["metric"], "--group-by", ",".join(query["group_by"])]
            if query["where"]:
                args += ["--where", " AND ".join(query["where"])]
            ex = mfa._run(p, [*args, "--explain"])  # noqa: SLF001
            text = mfa._ANSI.sub("", ex["stdout"] or "")  # noqa: SLF001
            import re
            m = re.search(r"^(WITH|SELECT)\b", text, flags=re.M)
            out["compiled_sql"] = text[m.start():].strip() if ex["exit_code"] == 0 and m else None
    except Exception as e:  # noqa: BLE001
        out.update(ok=False, error=f"{type(e).__name__}: {e}"[:600])
    return out


def guards(stack: dict, query: dict, raw_dir: Path) -> dict:
    """The erratum's guard checks (unmodified) on the candidate's own warehouse."""
    wh = Path(stack["warehouse"])
    p = mfa.open_project(Path(stack["upstream"]))
    ex = rr.explain_with_where(p, query["metric"], query["group_by"], " AND ".join(query["where"]))
    prices = rr.csv_prices(raw_dir)
    g = rr.guards(rr.warehouse_lines(wh), prices, len(prices), ex["sql"])
    names = ("quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison")
    return {"ok": all(g[n]["ok"] for n in names), "guards": {n: g[n]["ok"] for n in names},
            "min_quantity": g["quantity_positive"]["min_quantity"]}
