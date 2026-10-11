#!/usr/bin/env python3
"""Mechanical scorer (PROTOCOL.md §5, §8). Reads frozen arm outputs, the sealed inputs and the
scorer-only reference; replays executable claims through the native engine; writes results/.

  python3 src/score.py --runs-root RUNS --out results

Per task and arm it produces exact numerators and denominators for IR, FS, OF, TC, EI, FAB, CFC,
label correctness, abstentions and cost (from AUDIT.json written by audit_transcripts.py). It
never changes a threshold: the decision mapping lives in PROTOCOL.md and is applied in DECISION.md
by reading these numbers.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "src" / "publicodes_eval.mjs"
ARMS = ["A", "B"]
TASKS = ["T0", "T1a", "T1b", "R1", "R2", "R3", "R4", "R5", "M0", "M1", "M2"]


def load_json(p: Path):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"__error__": f"{type(e).__name__}: {e}"}


def law_articles(stage: Path) -> dict:
    """{snapshot: {num: record}} for the snapshots staged for the task."""
    out = {}
    for d in sorted((stage / "inputs" / "law").iterdir()):
        j = json.load(open(d / "articles.json", encoding="utf-8"))
        out[j["snapshot"]] = {num: recs[0] for num, recs in j["articles"].items()}
    return out


def quote_found(law: dict, article: str, quote: str, version_id: str | None):
    """Return (found_in_text, version_matches) across staged snapshots."""
    found, vmatch = False, False
    for snap in law.values():
        a = snap.get(article)
        if not a:
            continue
        if quote and norm(quote) in norm(a["text"]):
            found = True
        if version_id and a.get("id") == version_id:
            vmatch = True
    return found, vmatch


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def replay(rules_dir: Path, situation: dict, rule: str):
    if not rules_dir.exists():
        return {"error": "proposal dir missing"}
    cmd = ["node", str(EVAL), "evaluate", "--rules", str(rules_dir), "--situation", json.dumps(situation, ensure_ascii=False), "--rule", rule]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": f"engine failure: {r.stdout[:200]} {r.stderr[:200]}"}
    if "error" in j:
        return {"error": j["error"]}
    return j.get("evaluations", {}).get(rule, {"error": "rule not evaluated"})


def build_ok(rules_dir: Path) -> bool:
    if not rules_dir.exists():
        return False
    r = subprocess.run(["node", str(EVAL), "build", "--rules", str(rules_dir)], capture_output=True, text=True)
    try:
        return "error" not in json.loads(r.stdout)
    except json.JSONDecodeError:
        return False


def numeric(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def visible_values(ref: dict, article: str, snaps: list[str]) -> dict:
    """{value: [req]} for reference requirements of an article whose text is visible in the staged snapshots."""
    out = {}
    for r in ref["requirements"]:
        if r["article"] != article or r.get("value") is None or not isinstance(r["value"], (int, float)):
            continue
        if set(r.get("visible_in_snapshots", [])) & set(snaps):
            out.setdefault(round(float(r["value"]), 6), []).append(r["req_id"])
    return out


def score_change_task(task: str, arm: str, stage: Path, ans: dict, ref: dict) -> dict:
    t = ref["tasks"][task]
    law = law_articles(stage)
    snaps = list(law)
    required = set(t.get("affected_rules_required", []))
    optional = set(t.get("affected_rules_optional", []))
    rules = ans.get("rules") or []
    cls = {r.get("rule"): (str(r.get("classification", "")).upper(), str(r.get("confidence", "")).lower()) for r in rules if isinstance(r, dict)}
    flagged = {n for n, (c, _) in cls.items() if c == "AFFECTED"}
    unaffected = {n for n, (c, _) in cls.items() if c == "UNAFFECTED"}
    needs = {n for n, (c, _) in cls.items() if c == "NEEDS_REVIEW"}
    ir_num, ir_den = len(flagged & required), len(required)
    fs = sorted(required & unaffected)
    fs_high = sorted(n for n in fs if cls[n][1] == "high")
    of = sorted(flagged - required - optional)
    # changed articles
    ref_changed = set((t.get("changed_articles") or {}).keys())
    ans_changed = {str(c.get("article")) for c in (ans.get("changed_articles") or []) if isinstance(c, dict)}
    # evaluations: citation integrity + replay + value support
    evals = ans.get("evaluations") or []
    prop = stage / str(ans.get("proposal_dir", "work/proposals/x")) if ans.get("proposal_dir") else None
    cited, fab, correct, incorrect, unsupported, replay_fail = 0, 0, 0, 0, 0, 0
    eval_rows = []
    bok = build_ok(prop) if prop else None
    for e in evals:
        if not isinstance(e, dict):
            continue
        row = {"rule": e.get("rule"), "date": e.get("date"), "expected_from_text": e.get("expected_from_text"), "value_after": e.get("value_after")}
        art = str(e.get("article") or guess_article(e, ref)) if (e.get("article") or e.get("quote")) else None
        q_found, v_match = quote_found(law, art, e.get("quote", ""), e.get("article_version_id")) if art else (False, False)
        if e.get("quote"):
            cited += 1
            if not q_found:
                fab += 1
        row["quote_found"] = q_found
        row["version_id_in_snapshot"] = v_match
        exp = numeric(e.get("expected_from_text"))
        if exp is None or str(e.get("expected_from_text")).upper() == "ABSTAIN":
            row["outcome"] = "ABSTAINED"
        else:
            vis = visible_values(ref, art, snaps) if art else {}
            supported = round(exp, 6) in vis or (art == "D756-5")
            # replay on the proposal
            rep = None
            if prop and e.get("rule") and isinstance(e.get("situation"), dict):
                sit = dict(e["situation"])
                if e.get("date") and "date" not in sit:
                    sit["date"] = e["date"]
                rep = replay(prop, sit, e["rule"])
            if rep is None or "error" in rep:
                replay_fail += 1
                row["outcome"] = "REPLAY_FAILED"
                row["replay"] = rep
            else:
                obs = numeric(rep.get("nodeValue"))
                row["replayed_value"] = obs
                if not supported:
                    unsupported += 1
                    row["outcome"] = "UNSUPPORTED_VALUE_NOT_IN_SNAPSHOT_TEXT"
                elif obs is not None and abs(obs - exp) <= 1e-9:
                    correct += 1
                    row["outcome"] = "CORRECT"
                else:
                    incorrect += 1
                    row["outcome"] = "INCORRECT"
        eval_rows.append(row)
    abst = ans.get("abstentions") or []
    cfc = len(fs_high)
    return {"task": task, "arm": arm, "answered": True,
            "changed_articles": {"reference": sorted(ref_changed), "answer": sorted(ans_changed), "hit": len(ref_changed & ans_changed), "missed": sorted(ref_changed - ans_changed), "extra": sorted(ans_changed - ref_changed)},
            "IR": {"num": ir_num, "den": ir_den, "missed": sorted(required - flagged - needs), "needs_review_on_required": sorted(required & needs)},
            "FS": {"count": len(fs), "rules": fs, "high_confidence": fs_high}, "OF": {"count": len(of), "rules": of},
            "classified_rules": len(cls), "flagged_affected": len(flagged),
            "TC": {"correct": correct, "incorrect": incorrect, "abstained": len(abst) + sum(1 for r in eval_rows if r.get("outcome") == "ABSTAINED"), "unsupported_values": unsupported, "replay_failed": replay_fail},
            "EI": {"cited": cited, "fabricated": fab}, "CFC": cfc, "build_ok_on_proposal": bok,
            "no_change_needed_claimed": bool(ans.get("no_change_needed")), "evaluations": eval_rows, "approval_field": ans.get("approval"),
            "self_reported_tool_calls": ans.get("self_reported_tool_calls")}


def guess_article(e: dict, ref: dict) -> str | None:
    q = norm(e.get("quote", ""))
    if not q:
        return None
    for r in ref["requirements"]:
        if r.get("quote") and norm(r["quote"]) and norm(r["quote"]) in q:
            return r["article"]
    return None


def score_t0(arm: str, stage: Path, ans: dict, ref: dict) -> dict:
    law = law_articles(stage)
    links = ans.get("links") or []
    rules_dir = next((stage / "inputs" / "rules").iterdir()) / "modele-social" / "règles"
    rows, cited, fab, verified_ok, verified_bad, ver_mismatch = [], 0, 0, 0, 0, 0
    by_status = {}
    for L in links:
        if not isinstance(L, dict):
            continue
        st = str(L.get("status", "")).upper()
        by_status[st] = by_status.get(st, 0) + 1
        q_found, v_match = quote_found(law, str(L.get("article")), L.get("quote", ""), L.get("article_version_id"))
        cited += 1
        if not q_found:
            fab += 1
        if L.get("article_version_id") and not v_match:
            ver_mismatch += 1
        row = {"rule": L.get("rule"), "article": L.get("article"), "status": st, "quote_found": q_found, "version_ok": v_match, "approval": L.get("approval")}
        if st == "VERIFIED":
            chk = L.get("check") or {}
            if chk.get("rule") and isinstance(chk.get("situation"), dict):
                sit = dict(chk["situation"])
                if chk.get("date") and "date" not in sit:
                    sit["date"] = chk["date"]
                rep = replay(rules_dir, sit, chk["rule"])
                obs = numeric(rep.get("nodeValue")) if "error" not in rep else None
                exp = numeric(chk.get("expected"))
                ok = obs is not None and exp is not None and abs(obs - exp) <= 1e-9 and q_found
                row["replayed"] = obs
                row["check_holds"] = ok
                verified_ok += int(ok)
                verified_bad += int(not ok)
            else:
                row["check_holds"] = False
                verified_bad += 1
        rows.append(row)
    expected = ref["tasks"]["T0"]["expected_bindings"]
    exp_rules = set(sum(expected.values(), []))
    linked_rules = {r["rule"] for r in rows if r.get("quote_found")}
    return {"task": "T0", "arm": arm, "answered": True, "links": len(rows), "by_status": by_status,
            "EI": {"cited": cited, "fabricated": fab, "version_id_mismatch": ver_mismatch},
            "VERIFIED_checks": {"hold_on_replay": verified_ok, "fail_on_replay_or_unverifiable": verified_bad},
            "expected_bound_rules": {"num": len(exp_rules & linked_rules), "den": len(exp_rules), "missed": sorted(exp_rules - linked_rules)},
            "approvals_claimed": sorted({str(r.get("approval")) for r in rows}), "not_observable_listed": len(ans.get("not_observable") or []),
            "outside_bounded_set_listed": len(ans.get("outside_bounded_set") or []), "rows": rows, "self_reported_tool_calls": ans.get("self_reported_tool_calls")}


def score_reverse(task: str, arm: str, stage: Path, ans: dict, ref: dict) -> dict:
    t = ref["tasks"][task]
    law = law_articles(stage)
    label = str(ans.get("label", "")).upper()
    conf = str(ans.get("confidence", "")).lower()
    acceptable = label in t["acceptable_labels"]
    cfc = (not acceptable) and conf == "high"
    cited, fab = 0, 0
    for e in ans.get("evidence") or []:
        if isinstance(e, dict) and e.get("kind") == "article_quote" and e.get("quote_or_values"):
            cited += 1
            f, _ = quote_found(law, str(e.get("article")), str(e.get("quote_or_values")), e.get("article_version_id"))
            fab += int(not f)
    return {"task": task, "arm": arm, "answered": True, "label": label, "confidence": conf, "acceptable": acceptable, "acceptable_labels": t["acceptable_labels"],
            "CFC": int(cfc), "EI": {"cited": cited, "fabricated": fab}, "expected_values_listed": len(ans.get("expected_values_if_mismatch") or []),
            "outside_bounded_set": ans.get("outside_bounded_set"), "approval_field": ans.get("approval"), "self_reported_tool_calls": ans.get("self_reported_tool_calls")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    runs = Path(a.runs_root)
    ref = json.load(open(ROOT / "held_out" / "REFERENCE.json", encoding="utf-8"))
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    scores = {"protocol_sha256": ref["protocol_sha256"], "by_arm": {}}
    for arm in ARMS:
        scores["by_arm"][arm] = {}
        for task in TASKS:
            stage = runs / arm / task
            ans_p = stage / "output" / "answer.json"
            audit = load_json(stage / "AUDIT.json") if (stage / "AUDIT.json").exists() else {}
            if not ans_p.exists():
                res = {"task": task, "arm": arm, "answered": False, "reason": "no output/answer.json"}
            else:
                ans = load_json(ans_p)
                if "__error__" in ans:
                    res = {"task": task, "arm": arm, "answered": False, "reason": ans["__error__"]}
                elif task == "T0":
                    res = score_t0(arm, stage, ans, ref)
                elif task.startswith("R"):
                    res = score_reverse(task, arm, stage, ans, ref)
                else:
                    res = score_change_task(task, arm, stage, ans, ref)
            res["cost"] = {"tool_calls": audit.get("tool_calls_total"), "assistant_turns": audit.get("assistant_turns"), "usage": audit.get("usage"), "contaminated": audit.get("contaminated"), "flags": audit.get("flags")}
            scores["by_arm"][arm][task] = res
    json.dump(scores, open(out / "scores.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # markdown summary
    md = ["# Scores (mechanical)", "", f"Protocol {ref['protocol_sha256'][:16]}…. Exact numerators/denominators; see scores.json for rows.", ""]
    md += ["| task | arm | IR | FS | OF | TC correct/incorrect/abstained/unsupported | EI fabricated/cited | CFC | label | tool calls | contaminated |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for task in TASKS:
        for arm in ARMS:
            r = scores["by_arm"][arm][task]
            if not r.get("answered"):
                md.append(f"| {task} | {arm} | - | - | - | - | - | - | NOT ANSWERED ({r.get('reason')}) | {r['cost'].get('tool_calls')} | {r['cost'].get('contaminated')} |")
                continue
            ir = f"{r['IR']['num']}/{r['IR']['den']}" if "IR" in r else "-"
            fs = r["FS"]["count"] if "FS" in r else "-"
            of = r["OF"]["count"] if "OF" in r else "-"
            tc = f"{r['TC']['correct']}/{r['TC']['incorrect']}/{r['TC']['abstained']}/{r['TC']['unsupported_values']}" if "TC" in r else "-"
            ei = f"{r['EI']['fabricated']}/{r['EI']['cited']}" if "EI" in r else "-"
            cfc = r.get("CFC", "-")
            label = f"{r.get('label')} ({r.get('confidence')}) {'ok' if r.get('acceptable') else 'WRONG'}" if task.startswith("R") else ("-" if task != "T0" else f"links {r['links']} verified-hold {r['VERIFIED_checks']['hold_on_replay']}/{r['VERIFIED_checks']['hold_on_replay'] + r['VERIFIED_checks']['fail_on_replay_or_unverifiable']}")
            md.append(f"| {task} | {arm} | {ir} | {fs} | {of} | {tc} | {ei} | {cfc} | {label} | {r['cost'].get('tool_calls')} | {r['cost'].get('contaminated')} |")
    (out / "SCORES.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
