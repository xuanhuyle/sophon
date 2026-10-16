#!/usr/bin/env python3
"""Six-call COLD Jev screen of MS1-MS3 (tasks/2026-10-16_approved_microsoft_cold_screen.md).

Reuses probe.py's questions, transport, parser and key loading; probe.py's frozen
20-call plan is not touched. Offline by default. Only the three definitive Microsoft
LIBRARY_UPDATE decisions are sent; Oracle HOLDOUT and UNRESOLVED texts never are.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe

MODEL = "jev-1.13.0"
CASES = ("MS1", "MS2", "MS3")
REPEATS = 2
FROZEN = {"MS1": ("OBLIGATION", "YES"), "MS2": ("PROHIBITION", "YES"), "MS3": ("PROHIBITION", "NO")}
RECORDING = HERE / "live_runs" / "ms_cold_20261016_approved_001.json"
SOURCE_ID_CONTEXT = ("Document: Service Level Agreement for Microsoft Online Services "
                     "(Volume Licensing), version July 1, 2021. Excerpt quoted verbatim.")


def plan() -> dict:
    data = json.loads((HERE / "discriminating_candidates_v0.json").read_text(encoding="utf-8"))
    by_id = {d["decision_id"]: d for d in data["decisions"]}
    wording = {**probe.FUNCTIONS, **probe.MODIFIERS}
    requests = []
    for cid in CASES:
        d = by_id[cid]
        if d["split"] != "LIBRARY_UPDATE" or d["source_id"] != "MS-OSSLA-2021-07":
            raise ValueError(f"{cid}: not a Microsoft update decision")
        if (d["function"], d["label"]) != FROZEN[cid] or d["function_wording"] != wording[d["function"]]:
            raise ValueError(f"{cid}: frozen label or wording drifted")
        if hashlib.sha256(d["context"].encode("utf-8")).hexdigest() != d["context_sha256"]:
            raise ValueError(f"{cid}: context hash mismatch")
        req = {"model": MODEL,
               "state": {"clause": d["context"], "context": SOURCE_ID_CONTEXT,
                         "prior_provision_skeletons": []},
               "questions": probe.questions()}
        for repeat in range(1, REPEATS + 1):
            requests.append({"case_id": cid, "repeat": repeat, "scored_function": d["function"],
                             "request": req, "request_sha256": probe.digest(req)})
    return {"model_requested": MODEL, "questions_sha256": probe.digest(probe.questions()),
            "requests": requests}


def score(p: dict, recording: dict) -> dict:
    records = recording.get("records", [])
    if recording.get("plan_sha256") != probe.digest(p):
        raise ValueError("recording belongs to another plan")
    rows = {}
    for rec, planned in zip(records, p["requests"]):
        if (rec["case_id"], rec["repeat"], rec["request_sha256"]) != (
                planned["case_id"], planned["repeat"], planned["request_sha256"]):
            raise ValueError("record order or request hash mismatch")
        model, values = probe.parse_jev(rec["raw_response"], list(probe.questions()))
        if model != MODEL:
            raise ValueError(f"provider reported {model}, not {MODEL}")
        rows.setdefault(rec["case_id"], []).append(values)
    out = []
    for cid in CASES:
        fn, label = FROZEN[cid]
        reps = rows.get(cid, [])
        ps = [r[fn] for r in reps]
        agree = [(v >= 0.5) == (label == "YES") for v in ps]
        if len(ps) < REPEATS:
            verdict = "INCOMPLETE"
        elif not any(agree):
            verdict = "CANDIDATE_REPRODUCIBLE_DISAGREEMENT"
        elif all(agree):
            verdict = "AGREES_BOTH_REPEATS"
        else:
            verdict = "INSTABILITY_NOT_ERROR"
        out.append({"case_id": cid, "function": fn, "frozen_label": label,
                    "yes_probabilities": ps, "verdict": verdict,
                    "all_label_probabilities": reps})
    disagreements = [r["case_id"] for r in out if r["verdict"] == "CANDIDATE_REPRODUCIBLE_DISAGREEMENT"]
    complete = len(records) == len(p["requests"])
    decision = ("INCOMPLETE" if not complete else
                "CANDIDATE_ERROR_REQUIRES_INDEPENDENT_SOURCE_ADJUDICATION" if disagreements else
                "STOP_DATASET_AT_CEILING")
    return {"evaluation": "ENGINEERING_PRELABELS_NOT_LEGAL_GOLD", "model": MODEL,
            "calls_recorded": len(records), "candidate_reproducible_disagreements": disagreements,
            "decision": decision, "per_case": out}


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("mode", choices=("preflight", "live", "score"))
    cli.add_argument("--confirm-paid-calls", default="")
    args = cli.parse_args()
    p = plan()
    if args.mode == "preflight":
        hashes = [r["request_sha256"] for r in p["requests"]]
        print(json.dumps({"status": "READY_NO_CALLS_MADE", "model": MODEL, "planned_calls": len(hashes),
                          "plan_sha256": probe.digest(p), "questions_sha256": p["questions_sha256"],
                          "request_sha256": hashes, "recording_exists": RECORDING.exists(),
                          "key_present": bool(probe.resolve_typesafe_key())}, indent=2))
        return 0
    if args.mode == "score":
        print(json.dumps(score(p, json.loads(RECORDING.read_text(encoding="utf-8"))), indent=2))
        return 0
    if args.confirm_paid_calls != "YES":
        cli.error("paid calls require --confirm-paid-calls YES")
    if RECORDING.exists():
        cli.error("recording already exists; never rerun billed requests")
    key = probe.resolve_typesafe_key()
    if not key:
        cli.error("TYPESAFE_API_KEY not available")
    if len(p["requests"]) > 6:
        raise RuntimeError("call budget exceeded")
    RECORDING.parent.mkdir(parents=True, exist_ok=True)
    rec = {"plan_sha256": probe.digest(p), "started_at_utc": datetime.now(timezone.utc).isoformat(),
           "status": "INCOMPLETE", "attempts": 0, "records": []}
    RECORDING.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    try:
        for planned in p["requests"]:
            rec["attempts"] += 1  # counted before sending: a failed attempt is never repeated
            RECORDING.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
            t0 = time.monotonic()
            raw = probe.call_jev(planned["request"], key)
            if raw.get("model") != MODEL:
                raise RuntimeError(f"provider reported {raw.get('model')!r}, not {MODEL}; stopping")
            rec["records"].append({"case_id": planned["case_id"], "repeat": planned["repeat"],
                                   "request_sha256": planned["request_sha256"],
                                   "provenance": "ACTUAL_PROVIDER",
                                   "latency_ms": round((time.monotonic() - t0) * 1000),
                                   "raw_response": raw})
            RECORDING.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        rec["status"] = "COMPLETE"
    except Exception as exc:  # stop at first failure; record only the error class, never secrets
        rec["error"] = type(exc).__name__
        raise
    finally:
        rec["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        RECORDING.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(score(p, rec), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
