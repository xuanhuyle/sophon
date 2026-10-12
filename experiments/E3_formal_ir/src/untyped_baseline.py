"""Comparison with untyped recording (PROTOCOL.md §6). A plain JSON note store keeps the same documents (json.loads only:
no schema, no approvals logic) and is read naively:
  - a stored `status` field is taken as the status;
  - otherwise a requirement is 'VERIFIED' when one of its readings has a recorded native receipt with exit 0 whose
    numbers equal the recorded expected (oracle) numbers. Approvals, revisions, guards and provenance are not consulted.
The same documents are then given to the E3 validator (results from evidence/validation_results.json).

    python3 src/untyped_baseline.py --results evidence/validation_results.json --out evidence/untyped_baseline.json
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E3 = HERE.parent
sys.path.insert(0, str(HERE))
import run_scenarios as rs  # noqa: E402


def naive_status(doc: dict, native: dict, oracle: dict) -> str:
    if "status" in doc:
        return str(doc["status"])
    for r in (doc.get("interpretation") or {}).get("readings") or []:
        nr, orc = native.get(r.get("native_receipt_id") or ""), oracle.get(r.get("oracle_id") or "")
        if not nr or not orc or nr.get("exit_code") != 0:
            continue
        metric = nr["query"]["metric"]
        nat = {row["metric_time__year"][:4]: Decimal(row[metric]) for row in nr["rows"]}
        if nat == {k: Decimal(v) for k, v in orc["by_year"].items()}:
            return "VERIFIED"
    return "NOT_VERIFIED"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    base = rs.load(E3 / "cases" / "UNTYPED_BASELINE.json")
    scen = {s["scenario_id"]: s for s in rs.load(E3 / "cases" / "SCENARIOS.json")["scenarios"]}
    results = {r["scenario_id"]: r for r in rs.load(Path(a.results))}
    ctx = rs.context()
    rows = []
    for u in base["cases"]:
        s = scen[u["e3_scenario"]]
        doc = json.loads(json.dumps(rs.apply_patch(rs.load(E3 / "cases" / "records" / f"{s['record']}.json"), s["record_patch"])))
        native = rs.tamper(ctx.native, s["receipt_tamper"])
        naive = naive_status(doc, native, ctx.oracle)
        e3 = results[u["e3_scenario"]]["result"]
        rows.append({"id": u["id"], "e3_scenario": u["e3_scenario"], "false_state": u["false_state"],
                     "plain_json_store_accepts": True, "naive_status": naive, "naive_promotes": naive.upper().startswith("VERIFIED"),
                     "e3_status": e3["status"], "e3_rejects": not e3["status"].startswith("VERIFIED"),
                     "e3_reasons": e3["reasons"]})
    summary = {"promoted_by_naive_and_rejected_by_e3": [r["id"] for r in rows if r["naive_promotes"] and r["e3_rejects"]],
               "not_promoted_by_naive": [r["id"] for r in rows if not r["naive_promotes"]]}
    Path(a.out).write_text(json.dumps({"rule": base["rule"], "cases": rows, "summary": summary}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
