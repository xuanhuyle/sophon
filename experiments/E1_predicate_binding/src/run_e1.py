#!/usr/bin/env python3
"""Run E1 once: scored cases A, B1, B2 and the frozen adversarial variants (PROTOCOL.md section 4).

    .upstream/.venv/bin/python src/run_e1.py --upstream .upstream --out evidence/run

Each case and variant gets its own LiveContext, so no native result is shared through a cache. Writes
case_results.json (scored) and adversarial_results.json, each entry with its full recorded transcript.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluator as ev  # noqa: E402
import oracle as oracle_mod  # noqa: E402

E1 = HERE.parent


def load_frozen() -> dict:
    return json.loads((E1 / "FROZEN_CASES.json").read_text(encoding="utf-8"))


def live(p, raw=None):
    return ev.LiveContext(p, raw)


def summarize(r: dict) -> dict:
    return {"case_status": r["case_status"], "verified_for_recorded_checks": r["verified_for_recorded_checks"],
            "predicates": {k: v["status"] for k, v in r["predicates"].items()}, "uncovered": r["uncovered"],
            "metric_consistency_problems": r["metric_consistency_problems"]}


def run_all(upstream: Path, scratch: Path) -> dict:
    frozen = load_frozen()
    p = ev.mfa.open_project(upstream)
    out = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "scored": {}, "adversarial": {}}
    out["live_semantic_manifest_sha256"] = ev.mfa.fingerprints(p)["semantic_manifest_sha256"]

    for cid, case in frozen["cases"].items():
        ctx = live(p)
        r = ev.evaluate_case(case, frozen, ctx)
        out["scored"][cid] = {"result": r, "summary": summarize(r), "transcript": ctx.transcript}

    a_native = out["scored"]["A"]["result"]["native"]["by_year"]
    a_oracle = out["scored"]["A"]["result"]["oracle"]["by_year"]
    for vid, var in frozen["adversarial"].items():
        entry: dict = {}
        if "disposable_manifest_edit" in var:  # M7
            edit = var["disposable_manifest_edit"]
            dst = scratch / vid / "dbt" / "retail_dwh"
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(p.dbt_dir, dst, ignore=shutil.ignore_patterns("logs"))
            smp = dst / "target" / "semantic_manifest.json"
            sm = json.loads(smp.read_text(encoding="utf-8"))
            n = 0
            for m in sm["metrics"]:
                if m["name"] == edit["metric"]:
                    for w in m["filter"]["where_filters"]:
                        if w["where_sql_template"] == edit["filter_from"]:
                            w["where_sql_template"] = edit["filter_to"]
                            n += 1
            smp.write_text(json.dumps(sm), encoding="utf-8")
            dp = ev.mfa.Project(upstream=p.upstream, dbt_dir=dst, warehouse=p.warehouse, mf=p.mf, python=p.python)
            ctx = live(dp, p.upstream / "data" / "raw")
            r = ev.evaluate_case(ev.apply_variant(frozen, var), frozen, ctx)
            drifted = ev.native_query_with_where(dp, frozen["target"]["metric"], ["metric_time__year"], [])
            entry = {"edits_applied": n, "result": r, "summary": summarize(r), "transcript": ctx.transcript,
                     "drifted_native_by_year": ev.native_by_year(drifted["rows"], frozen["target"]["metric"]) if drifted["ok"] else None,
                     "drifted_native_exit": drifted["receipt"]["exit_code"],
                     "stale_recorded_A_native_by_year": a_native}
            entry["drifted_native_differs_from_A_native"] = entry["drifted_native_by_year"] != a_native
        elif "alter_native_value" in var:  # M8a
            alt = dict(a_native)
            y = var["alter_native_value"]["year"]
            alt[y] = str((Decimal(alt[y]) + Decimal(var["alter_native_value"]["delta"])).quantize(ev.CENT))
            cmp = oracle_mod.compare(alt, a_oracle)
            entry = {"altered_native": alt, "oracle": a_oracle, "comparison": cmp, "comparison_rejects": not cmp["equal"]}
        elif "alter_raw_copy" in var:  # M8b
            src = p.upstream / "data" / "raw"
            dst = scratch / vid / "raw"
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            with (dst / "orders.csv").open(newline="", encoding="utf-8") as f:
                completed = {r["order_id"] for r in csv.DictReader(f) if r["status"].strip().lower() == "completed"}
            with (dst / "order_items.csv").open(newline="", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                fields, items = rdr.fieldnames, list(rdr)
            target = min((it for it in items if it["order_id"] in completed), key=lambda it: int(it["order_item_id"]))
            target["quantity"] = str(int(target["quantity"]) + 1)
            with (dst / "order_items.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(items)
            with (dst / "orders.csv").open(newline="", encoding="utf-8") as f:
                year = next(r["order_date"][:4] for r in csv.DictReader(f) if r["order_id"] == target["order_id"])
            orc = oracle_mod.expected(dst, list(frozen["cases"]["A"]["required"]))
            cmp = oracle_mod.compare(a_native, orc["by_year"])
            delta = Decimal(orc["by_year"][year]) - Decimal(a_native[year])
            entry = {"mutated_line": target, "year": year, "oracle_on_mutated_copy": orc["by_year"], "native": a_native,
                     "comparison": cmp, "comparison_rejects": not cmp["equal"],
                     "oracle_delta": str(delta), "oracle_delta_equals_line_unit_price": delta == Decimal(target["unit_price"]).quantize(ev.CENT)}
        else:  # M4a-d, M5, M6, D10
            ctx = live(p)
            r = ev.evaluate_case(ev.apply_variant(frozen, var), frozen, ctx, var.get("frozen_fingerprint_override"))
            entry = {"result": r, "summary": summarize(r), "transcript": ctx.transcript}
            if vid.startswith("M5"):
                cov = (r.get("covered_subset_native") or {}).get("by_year")
                entry["covered_native_by_year"] = cov
                entry["covered_native_equals_A_native"] = cov == a_native
        entry["variant"] = var
        out["adversarial"][vid] = entry
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    up = Path(a.upstream).resolve()
    outdir = Path(a.out)
    res = run_all(up, E1 / "runs" / "scratch")
    outdir.mkdir(parents=True, exist_ok=True)
    meta = {k: res[k] for k in ("started_utc", "finished_utc", "live_semantic_manifest_sha256")}
    txt = lambda o: json.dumps(o, indent=1, ensure_ascii=False, default=str).replace(str(up), "<upstream>").replace(str(E1), "<e1>") + "\n"  # noqa: E731
    (outdir / "case_results.json").write_text(txt({**meta, "scored": res["scored"]}), encoding="utf-8")
    (outdir / "adversarial_results.json").write_text(txt({**meta, "adversarial": res["adversarial"]}), encoding="utf-8")
    brief = {"scored": {k: v["summary"] for k, v in res["scored"].items()},
             "A_native": res["scored"]["A"]["result"].get("native", {}).get("by_year"),
             "A_oracle": res["scored"]["A"]["result"].get("oracle", {}).get("by_year"),
             "A_comparison": res["scored"]["A"]["result"].get("comparison"),
             "B1_probe": res["scored"]["B1"]["result"]["predicates"]["P_UNIT_PRICE_GE_100"].get("native_exposure_probe"),
             "B1_covered_native": (res["scored"]["B1"]["result"].get("covered_subset_native") or {}).get("by_year"),
             "adversarial": {k: (v.get("summary") or {kk: v[kk] for kk in v if kk.endswith(("rejects", "equals_line_unit_price"))})
                             for k, v in res["adversarial"].items()},
             "M5_covered_equals_A": res["adversarial"]["M5_settlement_predicate_added_to_A"].get("covered_native_equals_A_native"),
             "M7": {k: res["adversarial"]["M7_native_identity_drift"].get(k) for k in ("edits_applied", "drifted_native_by_year", "drifted_native_differs_from_A_native")}}
    (outdir / "summary.json").write_text(txt(brief), encoding="utf-8")
    print(txt(brief))


if __name__ == "__main__":
    main()
