#!/usr/bin/env python3
"""Offline audit of the V1/V2 Jev evidence for a classification-learning headroom test.

Reads the historical V1/V2 artifacts from the PR #17 Git ref (never from the
working tree), makes NO provider calls and needs no network once the ref has
been fetched. It re-derives the facts cited in RESEARCH_PREFLIGHT.md,
"Independent challenge", and exits non-zero if any of them no longer holds.

It does not establish legal truth: the review matrix is agent-authored and no
independent oracle exists. It only measures what the recorded outputs and the
code can support.

Usage:  git fetch origin experiment/jev-v3-context-funnel-2026-10-13
        python3 audit/classification_headroom_2026-10-14/headroom_audit.py
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = "b9d698c78c4e7390555e2d73c2568cabe9be0b67"  # PR #17 head
V1 = "prototype/jev_clause_router_v0"
V2 = "prototype/jev_library_transfer_v2"
RUN = "20261013T094923Z"
MODIFIERS = ("THRESHOLD", "EXCLUSION", "CONDITION", "DEADLINE", "CROSS_REFERENCE")


def show(path: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{path}"],
                          capture_output=True, text=True, check=True).stdout


def load(path: str):
    return json.loads(show(path))


def v1_jev_outputs() -> dict:
    """Recorded Jev outputs for the fixed six-label question (V1, both corpora)."""
    rows = {}
    for corpus in ("EXT", "LAB"):
        run = load(f"{V1}/live_runs/live_{corpus}_{RUN}.json")
        for rec in run["records"]:
            step = rec["steps"]["jev"]
            ans = step["raw_response"]["answers"]
            rows[rec["clause_id"]] = {
                "provenance": step["provenance"],
                "model_reported": step["meta"]["model_reported"],
                "primary": ans["primary"]["choice"],
                "primary_p": ans["primary"]["probabilities"][ans["primary"]["choice"]],
                "reversed": ans["primary_reversed"]["choice"],
                "modifiers_p": {m: ans[m]["noul"] for m in MODIFIERS},
            }
    return rows


def v2_requests() -> dict:
    """Build the V2 Jev requests offline with the historical code and compare arms."""
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", REF, V1, V2],
                             capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        tarfile.open(fileobj=io.BytesIO(archive)).extractall(tmp, filter="data")
        sys.path.insert(0, str(Path(tmp, V2)))
        try:
            import transfer  # historical V2 code at REF
            v2 = Path(tmp, V2)
            lib0 = json.loads((v2 / "library_v0.json").read_text(encoding="utf-8"))
            lib1 = json.loads((v2 / "library_v1.json").read_text(encoding="utf-8"))
            corpus = json.loads((v2 / "google_storage_sla_20210624.json").read_text(encoding="utf-8"))
            out = {}
            for packet in corpus["clauses"]:
                cold = transfer.jev_request_v2(packet, "COLD_B", lib0, lib1, None, "jev-latest")
                warm = transfer.jev_request_v2(packet, "WARM_LIBRARY_B", lib0, lib1, None, "jev-latest")
                warm_text = json.dumps(warm, ensure_ascii=False)
                learned = [t for t in lib1["templates"].values() if t.get("learned_from_source")]
                out[packet["id"]] = {
                    "cold_options": sorted(cold["questions"]["template"]["criteria"]),
                    "warm_options": sorted(warm["questions"]["template"]["criteria"]),
                    "warm_state_keys": sorted(warm["state"]),
                    "warm_contains_any_positive_example_quote": any(
                        q in warm_text for t in learned for ex in t["positive_examples"] for q in ex["quotes"]),
                    "warm_contains_any_structural_rule": any(
                        r in warm_text for t in learned for r in t["structural_rules"]),
                    "warm_contains_any_counterexample_reason": any(
                        c["reason"] in warm_text for t in learned for c in t["counterexamples"]),
                }
            readings = {tid: t["category_readings"] for tid, t in lib1["templates"].items()
                        if t.get("learned_from_source")}
        finally:
            sys.path.pop(0)
            sys.modules.pop("transfer", None)
    return {"per_packet": out, "learned_template_category_readings": readings}


def main() -> int:
    jev = v1_jev_outputs()
    matrix = load(f"{V1}/review_matrix.json")["clauses"]
    ignored = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "--no-index", "-q",
                              f"{V2}/live_runs/live_V2_20261013T130630Z.json"]).returncode == 0
    gitignore_at_ref = f"{V2}/live_runs/" in show(".gitignore")
    v2_raw_in_ref = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{REF}:{V2}/live_runs"],
                                   capture_output=True).returncode == 0
    v2 = v2_requests()

    flips = sorted(c for c, r in jev.items() if r["primary"] != r["reversed"])
    low = sorted(c for c, r in jev.items() if r["primary_p"] < 0.9)
    fired = {m: sum(r["modifiers_p"][m] >= 0.5 for r in jev.values()) for m in MODIFIERS}
    primary_ok = sorted(c for c, r in jev.items() if r["primary"] in matrix[c]["acceptable_primary"])
    multi_accept = sorted(c for c, v in matrix.items() if len(v["acceptable_primary"]) > 1)
    tiered = v2["learned_template_category_readings"]["TIERED_SERVICE_CREDIT_SCHEDULE"]

    report = {
        "ref": REF,
        "provider_calls": 0,
        "v1_fixed_label_jev": {
            "packets": len(jev),
            "all_actual_provider": all(r["provenance"] == "ACTUAL_PROVIDER" for r in jev.values()),
            "models_reported": sorted({r["model_reported"] for r in jev.values()}),
            "primary_in_matrix_acceptable_list": f"{len(primary_ok)}/{len(jev)}",
            "matrix_packets_accepting_more_than_one_primary": multi_accept,
            "option_order_flips": {c: [jev[c]["primary"], jev[c]["reversed"]] for c in flips},
            "primary_probability_below_0_9": {c: jev[c]["primary_p"] for c in low},
            "modifier_yes_at_0_5_of_10": fired,
            "modifier_yes_total": f"{sum(fired.values())}/{len(jev) * len(MODIFIERS)}",
            "per_packet": jev,
        },
        "v2": {
            **v2,
            "tiered_readings_contain_cold_b2_label_DEFINITION": "DEFINITION" in tiered,
            "raw_live_runs_gitignored_at_ref": gitignore_at_ref,
            "raw_live_runs_present_in_ref": v2_raw_in_ref,
            "raw_live_runs_ignored_by_current_checkout": ignored,
        },
    }
    print(json.dumps(report, indent=1, ensure_ascii=False))

    pp = v2["per_packet"].values()
    checks = {
        "V1: 10 recorded Jev answers, all ACTUAL_PROVIDER": report["v1_fixed_label_jev"]["all_actual_provider"] and len(jev) == 10,
        "V1: exactly one option-order flip (G1 PERMISSION_RIGHT vs DEFINITION)": flips == ["G1"],
        "V1: matrix accepts two primaries for G1, G3, C5": multi_accept == ["C5", "G1", "G3"],
        "V1: >= 40/50 modifier answers are yes at 0.5": sum(fired.values()) >= 40,
        "V2: cold and warm Jev option sets differ": all(p["cold_options"] != p["warm_options"] for p in pp),
        "V2: warm Jev request carries no library quote, rule or counterexample": not any(
            p["warm_contains_any_positive_example_quote"] or p["warm_contains_any_structural_rule"]
            or p["warm_contains_any_counterexample_reason"] for p in pp),
        "V2: warm Jev state is only clause+context": all(p["warm_state_keys"] == ["clause", "context"] for p in pp),
        "V2: TIERED template maps to both DEFINITION and PERMISSION_RIGHT": sorted(tiered) == ["DEFINITION", "PERMISSION_RIGHT"],
        "V2: raw live runs git-ignored and absent from ref": gitignore_at_ref and not v2_raw_in_ref,
    }
    failed = [k for k, ok in checks.items() if not ok]
    for k, ok in checks.items():
        print(("PASS " if ok else "FAIL ") + k, file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
