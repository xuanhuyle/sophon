#!/usr/bin/env python3
"""Minimal real-input Jev memory probe. Offline by default. No reviewer LLM.

One provider request per case and arm, identical questions. Only state.library differs.
Source corpus and source-grounded library are read from immutable historical PR #17.
Scoring is a narrow predeclared text-anchored probe, NOT independent legal truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REF = "b9d698c78c4e7390555e2d73c2568cabe9be0b67"
V1 = "prototype/jev_clause_router_v0"
V2 = "prototype/jev_library_transfer_v2"
JEV_URL = "https://api.typesafe.ai/v1/systemone"
FUNCTIONS = {
    "OBLIGATION": "An explicit affirmative duty or service commitment imposed by this clause.",
    "PROHIBITION": "An action this clause expressly forbids. Do not infer prohibitions from mere definitions or exclusions.",
    "PERMISSION_RIGHT": "An explicit entitlement, permission or claim held by a party, including a conditional remedy.",
    "DEFINITION": "This clause expressly defines a term, metric, procedure or calculation.",
    "AUTHORITY": "This clause expressly grants a party approval or decision-making authority.",
}
MODIFIERS = {
    "CONDITION": "An explicit prerequisite or contingency governing applicability or exercise of a right/duty.",
    "EXCLUSION": "An explicit carve-out or exclusion from scope.",
    "THRESHOLD": "An explicit numerical or quantitative limit, threshold or cap.",
    "DEADLINE": "An explicit time limit for taking an action (not merely any measurement period).",
    "CROSS_REFERENCE": "An explicit reference needed to interpret this clause outside this excerpt.",
}
# Exact source-bounded passages, NOT invented or modified contractual text.
# Positive probes only: absence of another function is NOT a legal oracle.
CASES = (
    ("B1a", "B1", '"Back-off Requirements" means', "\n\n",
     (("DEFINITION", '"Back-off Requirements" means'),
      ("OBLIGATION", "Application is responsible for waiting"))),
    ("B1b", "B1", '"Error Rate" means', "\n\n",
     (("DEFINITION", '"Error Rate" means'),)),
    ("B1c", "B1", '"Monthly Uptime Percentage" means', "\n\n",
     (("DEFINITION", '"Monthly Uptime Percentage" means'),)),
    ("B2a", "B2", "During the Term of the agreement", "\n\n",
     (("OBLIGATION", "the Covered Service will provide a Monthly Uptime Percentage"),)),
    ("B2b", "B2", '"Financial Credit" means the following for the Standard storage class in a multi-region', "\n\n",
     (("DEFINITION", '"Financial Credit" means'),)),
    ("B3a", "B3", "In order to receive any of the Financial Credits described above", "\n\n",
     (("OBLIGATION", "Customer must notify Google technical support"),
      ("DEADLINE", "within 30 days"))),
    ("B3b", "B3", "The aggregate maximum number of Financial Credits to be issued by Google", "\n\n",
     (("THRESHOLD", "will not exceed 50%"),)),
    ("B3c", "B3", "The SLA does not apply to any", "",
     (("EXCLUSION", "The SLA does not apply to any"),)),
    # Full multi-function packets are the headroom-targeted probes, not just easy atomics.
    ("B2whole", "B2", "During the Term of the agreement", "",
     (("OBLIGATION", "the Covered Service will provide a Monthly Uptime Percentage"),
      ("DEFINITION", '"Financial Credit" means'))),
    ("B3whole", "B3", "In order to receive any of the Financial Credits described above", "",
     (("OBLIGATION", "Customer must notify Google technical support"),
      ("DEADLINE", "within 30 days"),
      ("THRESHOLD", "will not exceed 50%"),
      ("EXCLUSION", "The SLA does not apply to any"))),
)
ARMS = ("COLD", "LEARNED")


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def history(path: str) -> dict:
    result = subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{path}"],
                            text=True, capture_output=True, check=False, timeout=20)
    if result.returncode:
        raise RuntimeError(f"Cannot read historical PR #17 at {REF[:8]} ({path}). "
                           "Fetch the PR's history; do not replace it with newly invented data.")
    return json.loads(result.stdout)


def questions() -> dict:
    result = {}
    for name, meaning in {**FUNCTIONS, **MODIFIERS}.items():
        result[name] = {
            "type": "noul",
            "instructions": (f"Does the SOURCE clause itself express {meaning} "
                             "Return the probability of YES. Decide from SOURCE clause/context, "
                             "not from an earlier contract example. Multiple functions may coexist. "
                             "Prior library structures are provisional patterns only; never import "
                             "their numbers, deadlines, parties or entitlements."),
        }
    return result


def cases_and_memory() -> tuple[list, list]:
    corpus = history(f"{V2}/google_storage_sla_20210624.json")
    library = history(f"{V2}/library_v1.json")
    original = history(f"{V1}/external_github_sla_2021.json")
    by_id = {c["id"]: c for c in corpus["clauses"]}
    previous = {c["id"]: c for c in original["clauses"]}
    examples = []
    for key, template in sorted(library["templates"].items()):
        if not template.get("learned_from_source"):
            continue
        if template.get("status") != "PROVISIONAL" or len(template["positive_examples"]) != 1:
            raise ValueError(f"{key}: expected one explicitly provisional historical example")
        ex = template["positive_examples"][0]
        source = previous[ex["packet_id"]]
        if source["excerpt_sha256"] != ex["excerpt_sha256"]:
            raise ValueError(f"{key}: A-document evidence digest mismatch")
        evidence_quotes = [q for q in ex["quotes"] if q in source["text"]]
        if not evidence_quotes:
            raise ValueError(f"{key}: no source-verifiable example quote")
        examples.append({
            "archetype": key,
            "provisional": True,
            "source_id": ex["document_id"],
            "source_sha256": ex["excerpt_sha256"],
            "source_quotes": evidence_quotes[:2],
            "normative_functions_hypothesized": template["category_readings"],
            "structural_rules_provisional": template["structural_rules"][:3],
        })
    if len(examples) != 3:
        raise ValueError("expected three source-linked V2 learned patterns, not a new library")
    selected = []
    for name, packet_id, begin, end, probes in CASES:
        packet = by_id[packet_id]
        if hashlib.sha256(packet["text"].encode("utf-8")).hexdigest() != packet["excerpt_sha256"]:
            raise ValueError(f"{packet_id}: frozen source excerpt mismatch")
        if hashlib.sha256(packet["context"].encode("utf-8")).hexdigest() != packet["context_sha256"]:
            raise ValueError(f"{packet_id}: frozen context mismatch")
        if packet["source_id"] != "GCS-SLA-20210624":
            raise ValueError("Unexpected target contract")
        start = packet["text"].find(begin)
        if start < 0 or packet["text"].count(begin) != 1:
            raise ValueError(f"{name}: ambiguous source start marker")
        finish = packet["text"].find(end, start) if end else len(packet["text"])
        if finish < 0:
            raise ValueError(f"{name}: missing end delimiter")
        excerpt = packet["text"][start:finish].strip()
        for label, anchor in probes:
            if label not in FUNCTIONS and label not in MODIFIERS:
                raise ValueError(f"{name}: unknown function or modifier {label}")
            if anchor not in excerpt:
                raise ValueError(f"{name}: unsupported pre-registered anchor {anchor}")
        selected.append({"id": name, "document_id": packet["source_id"],
                         "source_packet_id": packet_id, "source_packet_sha256": packet["excerpt_sha256"],
                         "clause": excerpt, "context": packet["context"],
                         "probes": [{"name": name_, "verbatim_quote": q} for name_, q in probes]})
    if len({x["id"] for x in selected}) != len(selected):
        raise ValueError("duplicate probe case IDs")
    return selected, examples


def request(case: dict, library: list, arm: str, model: str) -> dict:
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    return {
        "model": model,
        "state": {
            "clause": case["clause"],
            "context": case["context"],
            # Same field exists in BOTH arms; only accumulated knowledge changes.
            "prior_provision_skeletons": [] if arm == "COLD" else library,
        },
        "questions": questions(),
    }


def validate_pair(cold: dict, warm: dict) -> None:
    if cold["model"] != warm["model"] or cold["questions"] != warm["questions"]:
        raise ValueError("Model/question drift between COLD and LEARNED")
    if set(cold["state"]) != set(warm["state"]):
        raise ValueError("Different state schema")
    for name in ("clause", "context"):
        if cold["state"][name] != warm["state"][name]:
            raise ValueError("Target text/context drift")
    if cold["state"]["prior_provision_skeletons"] != []:
        raise ValueError("Cold arm received prior knowledge")
    if not warm["state"]["prior_provision_skeletons"]:
        raise ValueError("Warm arm lacks prior knowledge")


def build(model: str = "jev-latest") -> dict:
    cs, memory = cases_and_memory()
    pairs = []
    for case in cs:
        cold = request(case, memory, "COLD", model)
        warm = request(case, memory, "LEARNED", model)
        validate_pair(cold, warm)
        pairs.append({"case": case, "requests": {"COLD": cold, "LEARNED": warm},
                      "request_hashes": {"COLD": digest(cold), "LEARNED": digest(warm)}})
    return {"research_goal": "PROVISION_NATURE_CUMULATIVE_LEARNING_V1",
            "scope": "FIRST_CROSS_AGREEMENT_MEMORY_EFFECT_ONLY",
            "unit_of_analysis": "MANUALLY_CURATED_SOURCE_EXCERPTS_NOT_AUTOMATIC_SUBPROVISION_SEGMENTATION",
            "reference_commit": REF, "library_sha256": digest(memory),
            "questions_sha256": digest(questions()), "model_requested": model,
            "pairs": pairs, "source_linked_library": memory,
            "frozen_positive_probes_count": sum(len(x["case"]["probes"]) for x in pairs)}


def parse_jev(raw: dict, question_names: list) -> tuple[str, dict]:
    if not isinstance(raw, dict) or not isinstance(raw.get("model"), str):
        raise ValueError("Missing actual reported model")
    reported = raw["model"]
    answers = raw.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("Missing typed answers")
    values = {}
    for name in question_names:
        a = answers.get(name)
        if not isinstance(a, dict) or a.get("type") != "noul":
            raise ValueError(f"Missing noul answer for {name}")
        p = a.get("noul")
        if isinstance(p, bool) or not isinstance(p, (float, int)) or not 0 <= p <= 1:
            raise ValueError(f"Bad probability for {name}")
        values[name] = float(p)
    return reported, values


def score(plan: dict, recording: dict) -> dict:
    if recording.get("plan_sha256") != digest(plan):
        raise ValueError("Recording belongs to another frozen plan")
    records = recording.get("records")
    if not isinstance(records, list) or len(records) != len(plan["pairs"]) * 2:
        raise ValueError("Incomplete/inconsistent number of actual provider calls")
    indexed = {(r["case_id"], r["arm"]): r for r in records}
    if len(indexed) != len(records):
        raise ValueError("Duplicate case/arm records")
    newly_passed, newly_lost, stable_hit = [], [], []
    models = set()
    report = []
    for pair in plan["pairs"]:
        case = pair["case"]
        scores = {}
        for arm in ARMS:
            entry = indexed.get((case["id"], arm))
            if not entry or entry.get("provenance") != "ACTUAL_PROVIDER":
                raise ValueError(f"{case['id']} {arm}: no actual provider output")
            if entry.get("request_sha256") != pair["request_hashes"][arm]:
                raise ValueError(f"{case['id']} {arm}: request mismatch")
            model, output = parse_jev(entry["raw_response"], list(questions()))
            models.add(model)
            scores[arm] = output
        passed = {}
        for probe in case["probes"]:
            name = probe["name"]
            cold = scores["COLD"][name] >= 0.5
            warm = scores["LEARNED"][name] >= 0.5
            row = {"label": name, "verbatim_quote": probe["verbatim_quote"],
                   "cold_yes_probability": scores["COLD"][name],
                   "learned_yes_probability": scores["LEARNED"][name],
                   "cold_probe_pass": cold, "learned_probe_pass": warm}
            passed.setdefault(name, []).append(row)
            marker = f"{case['id']}:{name}"
            if warm and not cold:
                newly_passed.append(marker)
            elif cold and not warm:
                newly_lost.append(marker)
            elif warm and cold:
                stable_hit.append(marker)
        report.append({"id": case["id"], "source_packet_id": case["source_packet_id"],
                       "source_packet_sha256": case["source_packet_sha256"], "positive_probes": passed,
                       "all_label_probabilities": scores})
    if len(models) != 1:
        raise ValueError("Model version changed between arms")
    return {"evaluation": "LIMITED_PREDECLARED_POSITIVE_SOURCE_QUOTES_NOT_LEGAL_GOLD",
            "automatic_subprovision_segmentation": False,
            "span_to_function_localization": False,
            "reported_model": next(iter(models)), "total_cases": len(report),
            "number_of_positive_probes": plan["frozen_positive_probes_count"],
            "newly_passed_positive_probes": newly_passed,
            "lost_positive_probes": newly_lost,
            "passed_in_both": stable_hit,
            "warning": "Manually curated excerpts with whole-excerpt multi-label decisions, NOT automatic sub-provision identification or span-to-function mapping. Unannotated labels are not negatives. Probe changes are not independent legal-accuracy gains.",
            "per_case": report}


def resolve_typesafe_key() -> str | None:
    """Read an existing local .env without exporting or printing any secrets.

    Only two explicit project-relative locations are eligible; a Claude cloud
    checkout cannot access a file that exists solely on the user's Windows PC.
    A process environment variable always takes priority. No new dependency.
    """
    existing = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if existing:
        return existing
    for env_file in (ROOT / ".env", HERE / ".env"):
        if not env_file.is_file():
            continue
        # Read only the specifically approved provider credential.
        # Do not report file contents or any parsed key in logs/errors.
        try:
            lines = env_file.read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            raise RuntimeError(f"Could not read {env_file.name}; check local file permissions") from None
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("export "):
                stripped = stripped[7:].lstrip()
            name, sep, rhs = stripped.partition("=")
            if not sep or name.strip() != "TYPESAFE_API_KEY":
                continue
            value = rhs.strip()
            if not value:
                continue
            if value[0] in ("'", '"'):
                end = value.find(value[0], 1)
                if end == -1 or value[end + 1:].strip() not in ("",) and not value[end + 1:].strip().startswith("#"):
                    raise RuntimeError(f"Malformed TYPESAFE_API_KEY assignment in {env_file.name}")
                value = value[1:end]
            else:
                value = value.split(" #", 1)[0].rstrip()
            if value:
                return value
    return None


def call_jev(req: dict, key: str) -> dict:
    data = json.dumps(req, ensure_ascii=False).encode("utf-8")
    http = urllib.request.Request(JEV_URL, data=data, method="POST",
                                  headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    # A single attempt. No silent retries, model substitution or provider fallback.
    with urllib.request.urlopen(http, timeout=45) as response:
        if getattr(response, "status", 200) != 200:
            raise RuntimeError("Provider did not return HTTP 200")
        raw = json.load(response)
    parse_jev(raw, list(questions()))
    return raw


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("mode", choices=("preflight", "live", "score"))
    cli.add_argument("--model", default="jev-latest")
    cli.add_argument("--output", type=Path)
    cli.add_argument("--recorded", type=Path)
    cli.add_argument("--confirm-paid-calls", default="")
    args = cli.parse_args()
    plan = build(args.model)
    if args.mode == "preflight":
        print(json.dumps({"status": "READY_FOR_OPTIONAL_PROVIDER_RUN_NOT_LEGAL_ORACLE",
                          "cases": len(plan["pairs"]), "planned_calls": len(plan["pairs"]) * 2,
                          "positive_probes": plan["frozen_positive_probes_count"],
                          "model": args.model, "plan_sha256": digest(plan),
                          "questions_sha256": plan["questions_sha256"],
                          "library_sha256": plan["library_sha256"]}, indent=2))
        return 0
    if args.mode == "score":
        if not args.recorded:
            cli.error("--recorded is required for score")
        output = score(plan, json.loads(args.recorded.read_text(encoding="utf-8")))
        print(json.dumps(output, indent=2))
        if args.output:
            args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        return 0
    if args.confirm_paid_calls != "YES":
        cli.error("Provider calls require explicit --confirm-paid-calls YES")
    key = resolve_typesafe_key()
    if not key:
        cli.error("TYPESAFE_API_KEY not found in this process or the project .env. "
                  "A local Windows .env is not visible in a separate Claude cloud container. "
                  "Use your local checkout or configure the cloud environment secret.")
    if len(plan["pairs"]) * 2 > 20:
        raise RuntimeError("Call budget exceeded")
    if not args.output:
        cli.error("--output under ignored live_runs/ is required for live mode")
    args.output = args.output.resolve()  # relative paths must pass the live_runs/ guard below
    if args.output.exists():
        cli.error("Refusing to overwrite a provider recording")
    if HERE / "live_runs" not in args.output.parents:
        cli.error("Live output must be in prototype/jev_memory_causal_probe_v0/live_runs/")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    recording = {"plan_sha256": digest(plan), "started_at_utc": datetime.now(timezone.utc).isoformat(),
                 "status": "INCOMPLETE", "records": []}
    try:
        for pair in plan["pairs"]:
            for arm in ARMS:
                req = pair["requests"][arm]
                result = call_jev(req, key)
                recording["records"].append({"case_id": pair["case"]["id"], "arm": arm,
                    "request_sha256": pair["request_hashes"][arm], "provenance": "ACTUAL_PROVIDER",
                    "raw_response": result})
                args.output.write_text(json.dumps(recording, indent=2) + "\n", encoding="utf-8")
        recording["status"] = "COMPLETE"
    finally:
        args.output.write_text(json.dumps(recording, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(score(plan, recording), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
