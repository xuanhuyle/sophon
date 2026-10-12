#!/usr/bin/env python3
"""Run the E0 procedure (PROTOCOL.md S1-S10 and diagnostic D1) once and write a receipt.

Run with the locked upstream interpreter, from experiments/E0_native_adapter:
    .upstream/.venv/bin/python src/run_e0.py --upstream .upstream --out evidence/run
It generates the upstream's synthetic data, loads bronze, runs dbt build and parse, enumerates and inspects the
metric, runs the native query, its repeat, the negative control and the cross-check. It never writes a metric
value that MetricFlow did not produce; the cross-check is stored under its own key.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import crosscheck  # noqa: E402
import mf_adapter as mfa  # noqa: E402

METRIC = "completed_revenue"
GROUP_BY = ["metric_time__year"]
ORDER = ["metric_time__year"]
EXPECTED_IDENTITY = {  # PROTOCOL.md section 2, from the source YAML before execution
    "metric": "completed_revenue", "type": "simple", "measure": "revenue",
    "filters": ["{{ Dimension('sales__status') }} = 'completed'"],
    "semantic_model": "sales", "measure_agg": "sum", "measure_expr": "revenue",
    "dbt_node": "model.retail_dwh.fact_sales",
}
NEGATIVE = {
    "N1_invalid_metric": {"metrics": ["completed_revenue_e0_nonexistent"], "group_by": None, "names": "completed_revenue_e0_nonexistent"},
    "N2_invalid_dimension": {"metrics": [METRIC], "group_by": ["sales__e0_nonexistent_dimension"], "names": "e0_nonexistent_dimension"},
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def step(argv: list[str], cwd: Path, env: dict, log: Path) -> dict:
    t0 = time.monotonic()
    proc = subprocess.run(argv, cwd=str(cwd), env=env, capture_output=True, text=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(f"$ {' '.join(argv)}\n# cwd={cwd}\n# exit={proc.returncode}\n--- stdout\n{proc.stdout}\n--- stderr\n{proc.stderr}", encoding="utf-8")
    return {"argv": argv, "cwd": str(cwd), "exit_code": proc.returncode, "elapsed_s": round(time.monotonic() - t0, 3),
            "log": log.name, "stdout_sha256": mfa.sha256_text(proc.stdout), "stderr_sha256": mfa.sha256_text(proc.stderr)}


def rel(argv: list[str], up: Path) -> list[str]:
    return [a.replace(str(up), "<upstream>") for a in argv]


def strip_receipt(r: dict) -> dict:
    """Keep the receipt small: full stdout/stderr only when short (they are also hashed)."""
    out = dict(r)
    for k in ("stdout", "stderr"):
        if len(out.get(k) or "") > 4000:
            out[k] = out[k][:2000] + "\n...[truncated; sha256 above]...\n" + out[k][-1500:]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--regen", action="store_true", help="S12 clean regeneration: S1-S7 and S10 only (no repeat, no negative control)")
    a = ap.parse_args()
    up = Path(a.upstream).resolve()
    out = Path(a.out).resolve()
    logs = out / "logs"
    p = mfa.open_project(up)
    env = p.env()
    py = str(p.python)
    dbt = str(p.python.parent / "dbt")
    proj = ["--project-dir", str(p.dbt_dir), "--profiles-dir", str(p.dbt_dir)]
    rec: dict = {"mode": "S12_regeneration" if a.regen else "full", "metric": METRIC, "upstream": str(up), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["upstream_commit"] = subprocess.run(["git", "-C", str(up), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec["upstream_clean"] = subprocess.run(["git", "-C", str(up), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.strip() == ""

    # S1 generate, S2 load bronze
    rec["S1_generate"] = step([py, "scripts/generate_raw_data.py"], up, env, logs / "S1_generate.log")
    raw = up / "data" / "raw"
    rec["S1_csv"] = {}
    for f in sorted(raw.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.reader(fh)) - 1
        rec["S1_csv"][f.name] = {"rows": n, "sha256": sha(f)}
    rec["S2_load_bronze"] = step([py, "-m", "scripts.load_bronze"], up, env, logs / "S2_load_bronze.log")
    import duckdb
    con = duckdb.connect(str(p.warehouse), read_only=True)
    rec["S2_bronze_rows"] = {t: con.execute(f"select count(*) from bronze.{t}").fetchone()[0]
                             for t in ["customers", "products", "stores", "orders", "order_items", "order_events"]}
    con.close()

    # S3 dbt build, S4 dbt parse
    rec["S3_dbt_build"] = step([dbt, "build", *proj], up, env, logs / "S3_dbt_build.log")
    rr = p.dbt_dir / "target" / "run_results.json"
    if rr.exists():
        res = json.loads(rr.read_text(encoding="utf-8"))["results"]
        counts: dict[str, int] = {}
        for r in res:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        rec["S3_dbt_build"]["status_counts"] = counts
        rec["S3_dbt_build"]["non_success"] = [{"node": r["unique_id"], "status": r["status"], "message": r.get("message")} for r in res if r["status"] not in ("success", "pass")]
    rec["S4_dbt_parse"] = step([dbt, "parse", *proj], up, env, logs / "S4_dbt_parse.log")
    rec["S4_dbt_parse"]["semantic_manifest_written"] = p.semantic_manifest.exists()
    rec["fingerprints_after_parse"] = mfa.fingerprints(p)
    for k in ("S1_generate", "S2_load_bronze", "S3_dbt_build", "S4_dbt_parse"):
        rec[k]["argv"] = rel(rec[k]["argv"], up)
        rec[k]["cwd"] = rec[k]["cwd"].replace(str(up), "<upstream>")

    # mf entry point identity
    rec["mf_identity"] = mfa.mf_identity(p)

    # S5 enumeration
    lm = mfa.list_metrics(p)
    ld = mfa.list_dimensions(p, METRIC)
    rec["S5_list_metrics"] = {"cli_metric_names": lm["cli_metric_names"], "manifest_metric_names": lm["manifest_metric_names"],
                              "cli_equals_manifest": lm["cli_metric_names"] == lm["manifest_metric_names"],
                              "receipt": strip_receipt(lm["receipt"])}
    rec["S5_list_dimensions"] = {"dimensions": ld["dimensions"], "receipt": strip_receipt(ld["receipt"])}

    # S6 identity
    ident = mfa.inspect_metric(p, METRIC)
    rec["S6_identity"] = ident
    rec["S6_identity_mismatches"] = mfa.identity_mismatches(ident, EXPECTED_IDENTITY)

    # S7 scored query + explain
    ex = mfa.explain(p, [METRIC], GROUP_BY, ORDER)
    rec["S7_explain"] = {"sql": ex["sql"], "receipt": strip_receipt(ex["receipt"])}
    sql_l = (ex["sql"] or "").lower()
    rec["S7_explain"]["reads_fact_sales"] = "fact_sales" in sql_l
    rec["S7_explain"]["applies_completed_filter"] = "= 'completed'" in sql_l
    q1 = mfa.query(p, [METRIC], GROUP_BY, ORDER)
    rec["S7_query"] = {"rows": q1["rows"], "csv": q1["csv"], "receipt": strip_receipt(q1["receipt"])}

    # S8 repeat
    q2 = q1 if a.regen else mfa.query(p, [METRIC], GROUP_BY, ORDER)
    rec["S8_repeat"] = {"rows": q2["rows"], "receipt": strip_receipt(q2["receipt"]),
                        "csv_identical": q1["csv"] == q2["csv"],
                        "warehouse_sha256_unchanged": q1["receipt"]["fingerprints_before"]["warehouse_sha256"] == q2["receipt"]["fingerprints_after"]["warehouse_sha256"]}

    # S9 negative control
    rec["S9_negative"] = {}
    for name, n in ({} if a.regen else NEGATIVE).items():
        try:
            r = mfa.query(p, n["metrics"], n["group_by"], None)
            rec["S9_negative"][name] = {"rejected": False, "rows": r["rows"], "receipt": strip_receipt(r["receipt"])}
        except mfa.NativeQueryError as e:
            msg = (e.receipt.get("stdout") or "") + (e.receipt.get("stderr") or "")
            rec["S9_negative"][name] = {"rejected": True, "adapter_error": str(e), "exit_code": e.receipt["exit_code"],
                                        "csv_written": e.receipt.get("csv_written"), "error_names_invalid_input": n["names"] in msg,
                                        "receipt": strip_receipt(e.receipt)}

    # S10 cross-check
    xc = crosscheck.compute(raw)
    native = {}
    for row in q1["rows"]:
        year = str(row["metric_time__year"])[:4]
        native[year] = str(Decimal(row[METRIC]).quantize(Decimal("0.01")))
    rec["S10_crosscheck"] = {"label": "CROSS-CHECK from raw CSV with Python stdlib; not semantic execution", **xc,
                             "native_by_year": native, "equal_per_year": native == xc["by_year"]}

    # D1 diagnostic: compiled SQL executed directly in DuckDB (read-only)
    try:
        con = duckdb.connect(str(p.warehouse), read_only=True)
        d1 = con.execute(ex["sql"]).fetchall()
        con.close()
        rec["D1_explain_sql_direct"] = {"rows": [[str(c) for c in r] for r in d1],
                                        "equal_to_native": [str(Decimal(str(r[1])).quantize(Decimal('0.01'))) for r in d1] == list(native.values())}
    except Exception as e:  # noqa: BLE001
        rec["D1_explain_sql_direct"] = {"error": f"{type(e).__name__}: {e}"}
    rec["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["fingerprints_final"] = mfa.fingerprints(p)
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_receipt.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False, default=str).replace(str(up), "<upstream>") + "\n", encoding="utf-8")
    (out / "query_result.csv").write_text(q1["csv"], encoding="utf-8")
    if ex["sql"]:
        (out / "compiled_query.sql").write_text(ex["sql"] + "\n", encoding="utf-8")
    shutil_copy = [p.semantic_manifest]
    for f in shutil_copy:
        (out / f.name).write_bytes(f.read_bytes())
    summary = {k: rec[k] for k in ("upstream_commit", "upstream_clean", "S1_csv", "S2_bronze_rows")}
    summary.update({
        "S3_exit": rec["S3_dbt_build"]["exit_code"], "S3_counts": rec["S3_dbt_build"].get("status_counts"),
        "S4_exit": rec["S4_dbt_parse"]["exit_code"], "semantic_manifest": rec["fingerprints_after_parse"]["semantic_manifest_sha256"],
        "S5_cli_equals_manifest": rec["S5_list_metrics"]["cli_equals_manifest"], "S5_n_metrics": len(rec["S5_list_metrics"]["cli_metric_names"]),
        "S6_mismatches": rec["S6_identity_mismatches"],
        "S7_exit": q1["receipt"]["exit_code"], "S7_rows": q1["rows"], "S7_reads_fact_sales": rec["S7_explain"]["reads_fact_sales"],
        "S7_completed_filter": rec["S7_explain"]["applies_completed_filter"],
        "S8_identical": rec["S8_repeat"]["csv_identical"], "S8_warehouse_unchanged": rec["S8_repeat"]["warehouse_sha256_unchanged"],
        "S9": {k: {kk: v.get(kk) for kk in ("rejected", "exit_code", "csv_written", "error_names_invalid_input")} for k, v in rec["S9_negative"].items()},
        "S10_equal": rec["S10_crosscheck"]["equal_per_year"], "S10_crosscheck": xc["by_year"], "D1": rec["D1_explain_sql_direct"].get("equal_to_native", rec["D1_explain_sql_direct"].get("error")),
    })
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
