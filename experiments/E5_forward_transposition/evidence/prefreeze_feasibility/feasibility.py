"""E5 pre-freeze feasibility (NOT scored). Builds the combined E4 M6B + E4 M2 baseline in a disposable stack and
checks that both lab-added native metrics build and query, the time-window `where` used for version routing and the
line-grain query. Run with the pinned venv python from experiments/E5_forward_transposition."""
import json, sys
from pathlib import Path
E5 = Path(__file__).resolve().parents[1]
E4 = E5.parent / "E4_independent_verification"
sys.path.insert(0, str(E4 / "src"))
import candidate_stack as cs  # unmodified E4 module
m6b = json.loads((E4 / "candidates" / "M6B.json").read_text())
m2 = json.loads((E4 / "candidates" / "M2.json").read_text())
patch = m6b["patch"] + m2["patch"]
up = (E5 / ".upstream").resolve()
st = cs.build("BASELINE__PINNED", patch, up / "data" / "raw", up, E5 / "runs" / "feasibility")
out = {"build": {k: st.get(k) for k in ("ok", "steps", "semantic_manifest_sha256", "raw_csv_sha256", "error")}, "queries": {}}
TW = "{{ TimeDimension('metric_time', 'day') }}"
qs = {
 "p1_year": {"metric": "premium_completed_revenue", "group_by": ["metric_time__year"], "where": []},
 "p2_year": {"metric": "french_market_revenue", "group_by": ["metric_time__year"], "where": []},
 "p1_line": {"metric": "premium_completed_revenue", "group_by": ["sales"], "where": []},
 "p1_year_ge2025": {"metric": "premium_completed_revenue", "group_by": ["metric_time__year"], "where": [f"{TW} >= '2025-01-01'"]},
 "p1_year_lt2025": {"metric": "premium_completed_revenue", "group_by": ["metric_time__year"], "where": [f"{TW} < '2025-01-01'"]},
 "p1_line_ge2025": {"metric": "premium_completed_revenue", "group_by": ["sales"], "where": [f"{TW} >= '2025-01-01'"]},
}
if st["ok"]:
    for k, q in qs.items():
        r = cs.execute(st, q)
        rows = r.get("rows") or []
        out["queries"][k] = {"ok": r.get("ok"), "exit_code": r.get("exit_code"), "n_rows": len(rows),
                             "rows": rows if "year" in k else None,
                             "compiled_sql": r.get("compiled_sql"), "error": r.get("error") or r.get("stdout_tail")}
    import yaml
    sm = json.loads((Path(st["upstream"]) / "dbt/retail_dwh/target/semantic_manifest.json").read_text())
    out["manifest_metrics"] = [m["name"] for m in sm["metrics"]]
    out["manifest_p2_node"] = next(m for m in sm["metrics"] if m["name"] == "french_market_revenue")
    out["metrics_yaml"] = (Path(st["upstream"]) / "dbt/retail_dwh/models/marts/semantic/_metrics.yml").read_text()
print(json.dumps(out, indent=1, default=str))
