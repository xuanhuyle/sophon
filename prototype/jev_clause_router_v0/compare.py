"""Per-clause A/B/C/D comparison against the PROVISIONAL review matrix.

Mechanical only. It counts missed required modifiers, unsupported modifiers, holds and candidates,
and gives AUTO_HINTs when an arm quotes text overlapping a material-condition anchor. Whether an arm
really understood a condition needs human adjudication. Never extrapolates rates from 5-10 clauses.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prototype as p  # noqa: E402

ARM_LABELS = {"A_jev_only": "A Jev", "B_jev_adversarial": "B Jev+adv", "C_jev_adversarial_backward": "C Jev+adv+back",
              "D_blind_llm": "D blind LLM"}


def _overlaps(quote: str, anchor: str) -> bool:
    q, a = p._norm(quote), p._norm(anchor)
    return bool(q) and (a in q or (len(q) >= 8 and q in a))


def score_arm(arm: dict, entry: dict) -> dict:
    if arm["status"] != "RUN" or "proposed_primary" not in arm:
        return {"status": arm["status"], "disposition": arm["disposition"], "provenance": arm["provenance"],
                "reasons": arm["reasons"]}
    detected = set(arm["detected_modifiers"])
    required, contestable = set(entry["required_modifiers"]), set(entry["contestable_modifiers"])
    quotes = arm.get("evidence_quotes", []) + arm.get("unresolved_refs", [])
    hints = None
    if quotes:
        hints = {mc["id"]: any(_overlaps(q, mc["anchor"]) for q in quotes) for mc in entry["material_conditions"]}
    return {"status": "RUN", "provenance": arm["provenance"], "disposition": arm["disposition"],
            "primary": arm["proposed_primary"], "primary_acceptable": arm["proposed_primary"] in entry["acceptable_primary"],
            "missed_required": sorted(required - detected), "unsupported": sorted(detected - required - contestable),
            "condition_anchor_hints": hints, "unresolved_refs": arm.get("unresolved_refs"),
            "reasons": arm["reasons"], "human_adjudication": "PENDING"}


def unique_reviewer_findings(arm_c: dict) -> dict:
    ch = arm_c.get("reviewer_challenges") or {}
    adv, back = set(ch.get("adversarial", [])), set(ch.get("backward", []))
    return {"adversarial_only": sorted(adv - back), "backward_only": sorted(back - adv), "both": sorted(adv & back)}


def overhead(results: dict) -> dict:
    totals: dict = {}
    for rec in results.get("records", []):
        for name, step in rec["steps"].items():
            t = totals.setdefault(name, {"calls_attempted": 0, "calls_ok": 0, "input_tokens": 0, "output_tokens": 0,
                                         "latency_ms": 0, "reported_cost_usd": 0.0, "models_reported": set()})
            t["calls_attempted"] += 1
            if step.get("provenance") != "ACTUAL_PROVIDER":
                continue
            t["calls_ok"] += 1
            meta = step.get("meta", {})
            usage = meta.get("usage") or (step.get("raw_response") or {}).get("usage") or {}
            t["input_tokens"] += int(usage.get("input_tokens") or 0)
            t["output_tokens"] += int(usage.get("output_tokens") or 0)
            t["latency_ms"] += int(meta.get("latency_ms") or 0)
            t["reported_cost_usd"] += float(meta.get("total_cost_usd") or 0)
            for m in [meta.get("model_reported")] + list(meta.get("models_reported") or []):
                if m:
                    t["models_reported"].add(m)
    for t in totals.values():
        t["models_reported"] = sorted(t["models_reported"])
    return totals


def compare(results: dict, matrix: dict) -> dict:
    rows, totals = [], {arm: {"run": 0, "candidate": 0, "hold": 0, "not_run": 0, "primary_acceptable": 0,
                              "missed_required": 0, "unsupported": 0,
                              "candidate_with_missed_required": 0, "hold_with_no_missed_required": 0}
                        for arm in p.ARMS}
    for ev in results["evaluation"]:
        entry = matrix["clauses"][ev["clause_id"]]
        scored = {arm: score_arm(ev["arms"][arm], entry) for arm in p.ARMS}
        for arm, s in scored.items():
            t = totals[arm]
            if s["status"] != "RUN" or "primary" not in s:
                t["not_run" if s["status"] != "RUN" else "hold"] += 1
                continue
            t["run"] += 1
            t["primary_acceptable"] += s["primary_acceptable"]
            t["missed_required"] += len(s["missed_required"])
            t["unsupported"] += len(s["unsupported"])
            if s["disposition"] == "CANDIDATE_FOR_HUMAN_REVIEW":
                t["candidate"] += 1
                t["candidate_with_missed_required"] += bool(s["missed_required"])
            else:
                t["hold"] += 1
                t["hold_with_no_missed_required"] += not s["missed_required"]
        rows.append({"clause_id": ev["clause_id"], "provenance": ev["provenance"], "arms": scored,
                     "reviewer_unique_findings": unique_reviewer_findings(ev["arms"]["C_jev_adversarial_backward"])})
    live = any(prov in ("ACTUAL_PROVIDER", "RECORDED_ACTUAL") for r in rows for prov in r["provenance"].values())
    return {"corpus_id": results["corpus_id"], "mode": results["mode"], "matrix_status": matrix["status"],
            "has_actual_provider_outputs": live, "per_clause": rows, "per_arm_totals": totals,
            "overhead": overhead(results),
            "caution": "5 clauses per corpus: report counts, not rates. Matrix is provisional and not independent."}


def to_markdown(report: dict) -> str:
    out = [f"### {report['corpus_id']} ({report['mode']})", "",
           f"Actual provider outputs present: **{report['has_actual_provider_outputs']}**. {report['caution']}", "",
           "| Clause | Arm | Provenance | Disposition | Primary (ok?) | Missed required | Unsupported | Anchor hints |",
           "|---|---|---|---|---|---|---|---|"]
    for row in report["per_clause"]:
        for arm, s in row["arms"].items():
            if "primary" not in s:
                out.append(f"| {row['clause_id']} | {ARM_LABELS[arm]} | {s['provenance']} | {s['disposition']} | - | - | - | - |")
                continue
            hints = "n/a" if s["condition_anchor_hints"] is None else ", ".join(
                f"{k.split('.')[-1]}{'+' if v else '-'}" for k, v in s["condition_anchor_hints"].items())
            out.append(f"| {row['clause_id']} | {ARM_LABELS[arm]} | {s['provenance']} | {s['disposition']} | "
                       f"{s['primary']} ({'yes' if s['primary_acceptable'] else 'NO'}) | {', '.join(s['missed_required']) or '-'} | "
                       f"{', '.join(s['unsupported']) or '-'} | {hints} |")
    out += ["", "| Arm | run | candidate | hold | not run | primary ok | missed req. | unsupported | candidate w/ missed req. | hold w/o missed req. |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for arm, t in report["per_arm_totals"].items():
        out.append(f"| {ARM_LABELS[arm]} | {t['run']} | {t['candidate']} | {t['hold']} | {t['not_run']} | {t['primary_acceptable']} | "
                   f"{t['missed_required']} | {t['unsupported']} | {t['candidate_with_missed_required']} | {t['hold_with_no_missed_required']} |")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results", nargs="+", help="live or replay result files")
    ap.add_argument("--matrix", default=str(HERE / "review_matrix.json"))
    ap.add_argument("--json-out")
    args = ap.parse_args(argv)
    matrix = p.read_json(args.matrix)
    reports = [compare(p.read_json(f), matrix) for f in args.results]
    for r in reports:
        print(to_markdown(r))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(reports, indent=2) + "\n", encoding="utf8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
