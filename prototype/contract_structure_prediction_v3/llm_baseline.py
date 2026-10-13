"""OPTIONAL STRONG_LLM_CONTEXT baseline for the V3 masked-structure pilot. NOT RUN.

One logical call per heldout case (8 cases in the secondary repaired set -> at most 8 calls). The model sees
exactly what the frequency arms see: family, evidenced law (or UNKNOWN), the visible labels, the section
function (provision task) and the candidate label list with one-line category names. It never sees source
text, headings of masked units, URLs, issuers or target labels.

    python llm_baseline.py --mode preflight                     # no network; prompts, hashes, cap, estimate
    python llm_baseline.py --mode live --allow-external-calls --output live_runs/llm_<stamp>.json   # operator only
    python llm_baseline.py --mode score --recorded live_runs/llm_<stamp>.json                      # offline
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "jev_clause_router_v0"))
import predict  # noqa: E402

PROMPT_VERSION = "v3-llm-structure-prior-1"
MODEL = "claude-opus-5-5"
MAX_CALLS = 8
# Repo price table (prototype.PRICES, USD per MTok in/out); V2 observed ~4,076 output tokens per call incl. thinking.
PRICE_IN, PRICE_OUT, OUT_PER_CALL = 4.0, 20.0, 4100


def cases() -> list[dict]:
    res = json.loads((HERE / "results" / "secondary_repaired_run.json").read_text(encoding="utf-8"))
    return [row["case"] for row in res["cases"]]


def prompt_for(c: dict) -> str:
    if c["task"] == "SECTION":
        q = ("Some top-level sections of this agreement are hidden. Estimate, for EACH candidate section function, the probability "
             "that it is present among the hidden sections (multi-label; several or none may be present).")
        ctx = {"contract_family": c["family"], "evidenced_governing_law": c["law"], "visible_section_functions": c["observed"]}
    else:
        q = ("Some subsections of one article are hidden. Estimate, for EACH candidate provision type, the probability that it is "
             "present among the hidden subsections of THIS article (multi-label).")
        ctx = {"contract_family": c["family"], "evidenced_governing_law": c["law"], "article_function": c["section_function"],
               "visible_provision_types_in_this_article": c["observed"]}
    return (f"{q}\nAbsence is normal (negotiated omission or different placement). Do not infer legal defects.\n"
            f"CONTEXT (labels only; no source text is available): {json.dumps(ctx)}\n"
            f"CANDIDATES: {json.dumps(c['candidates'])}\n"
            'Return ONLY JSON: {"probabilities": {"<candidate>": <0..1>, ...}} with every candidate exactly once.')


def preflight() -> dict:
    cs = cases()
    prompts = {c["case_id"]: prompt_for(c) for c in cs}
    chars = sum(len(p) for p in prompts.values())
    usd = round(chars / 4 / 1e6 * PRICE_IN + len(cs) * OUT_PER_CALL / 1e6 * PRICE_OUT, 2)
    return {"prompt_version": PROMPT_VERSION, "model": MODEL, "planned_logical_calls": len(cs), "cap": MAX_CALLS,
            "ready": len(cs) <= MAX_CALLS, "inside_claude_code_session": bool(os.getenv("CLAUDECODE")),
            "credentials_present": bool(os.getenv("ANTHROPIC_API_KEY")),
            "prompt_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in prompts.items()},
            "cost_estimate_usd": usd, "cost_note": "chars/4 input + 4,100 output tokens/call (V2 observed mean incl. thinking) at repo price table; estimate only, no enforceable cap"}


def live(output: Path) -> None:
    if os.getenv("CLAUDECODE"):
        raise SystemExit("inside Claude Code: refusing paid calls")
    import prototype  # V1 adapter: call_anthropic, no model fallback
    rec = {"prompt_version": PROMPT_VERSION, "model": MODEL, "calls": []}
    for c in cases()[:MAX_CALLS]:
        p = prompt_for(c)
        try:
            r = prototype.call_anthropic(p, MODEL, effort="medium")
            rec["calls"].append({"case_id": c["case_id"], "prompt_sha256": hashlib.sha256(p.encode()).hexdigest(), **r})
        except Exception as e:  # keep partial evidence; never retry silently beyond the adapter's own bounded retries
            rec["calls"].append({"case_id": c["case_id"], "error": repr(e)})
        output.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")


def score(recorded: Path) -> dict:
    rec = json.loads(recorded.read_text(encoding="utf-8"))
    by = {c["case_id"]: c for c in cases()}
    rows = []
    for call in rec["calls"]:
        c = by[call["case_id"]]
        try:
            probs = json.loads(call["raw_text"].strip().strip("`").removeprefix("json"))["probabilities"]
            ok = set(probs) == set(c["candidates"])
        except Exception:
            probs, ok = {}, False
        pr = {cand: {"p": float(probs.get(cand, 0.5))} for cand in c["candidates"]}
        pred = {"ranked": sorted(c["candidates"], key=lambda x: (-pr[x]["p"], x)), "probs": pr}
        rows.append({"case_id": c["case_id"], "valid_output": ok, "score": predict.score_case(c, pred)})
    return {"arm": "STRONG_LLM_CONTEXT", "rows": rows,
            "hit3": sum(r["score"]["hit3"] for r in rows), "false_expectations_top3": sum(r["score"]["false_expectations_top3"] for r in rows),
            "brier_mean": round(sum(r["score"]["brier"] for r in rows) / max(1, len(rows)), 4)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preflight", "live", "score"], required=True)
    ap.add_argument("--allow-external-calls", action="store_true")
    ap.add_argument("--output")
    ap.add_argument("--recorded")
    a = ap.parse_args()
    if a.mode == "preflight":
        r = preflight()
        print(json.dumps(r, indent=1))
        sys.exit(0 if r["ready"] else 2)
    if a.mode == "live":
        if not a.allow_external_calls:
            raise SystemExit("--allow-external-calls required")
        live(Path(a.output))
    else:
        print(json.dumps(score(Path(a.recorded)), indent=1))


if __name__ == "__main__":
    main()
