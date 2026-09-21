"""Mechanical audit of the evidence packet. Standard library only; never writes inside evidence/.

Run from the repository root:  python -B audit/audit_packet.py
Writes results/audit_packet.json and prints a summary.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import random
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
OUT = ROOT / "results" / "audit_packet.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- 1. frozen hashes
def check_hashes() -> dict:
    ipsa = EVID / "sophon_ipsa"
    freeze = json.loads((ipsa / "results" / "freeze.json").read_text(encoding="utf-8"))
    solo = EVID / "sophon_solo"
    manifest = json.loads((solo / "manifest.json").read_text(encoding="utf-8"))
    checks = {
        "ipsa_decisions": (sha(ipsa / "results" / "decisions.json"), freeze["decisions_sha256"]),
        "ipsa_sample": (sha(ipsa / "results" / "sample_features.json"), freeze["sample_sha256"]),
        "ipsa_policy": (sha(ipsa / "policy_15th.json"), freeze["policy_sha256"]),
        "ipsa_runtime_replay_py": (sha(ipsa / "replay.py"), freeze["runtime_sha256"]),
        "solo_cases": (sha(solo / "cases.csv"), manifest["cases_sha256"]),
        "solo_draft_policy": (sha(solo / "draft_policy.md"), manifest["draft_policy_sha256"]),
    }
    return {k: {"actual": a, "recorded": r, "match": a == r} for k, (a, r) in checks.items()}


# ---------------------------------------------------------------- 2. bundled label counts
def check_labels() -> dict:
    comp = json.loads((EVID / "sophon_ipsa" / "results" / "comparison.json").read_text(encoding="utf-8"))
    return {"rows": len(comp), "published_status": dict(Counter(c["published_status"] for c in comp)),
            "decisions": dict(Counter(c["decision"] for c in comp)),
            "note": "Recount of the bundled 1,000-row join only. The full-file figures (82,787 rows; 18 Not Paid; "
                    "446 Repaid) need the raw CSV, which is not in the packet and was not downloaded."}


# ---------------------------------------------------------------- 3. is decide() a constant?
def audit_decide() -> dict:
    path = EVID / "sophon_ipsa" / "replay.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "decide")
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
    literal_decisions = []
    for r in returns:
        if isinstance(r.value, ast.Dict):
            for k, v in zip(r.value.keys, r.value.values):
                if isinstance(k, ast.Constant) and k.value == "decision":
                    literal_decisions.append(v.value if isinstance(v, ast.Constant) else "<non-literal>")
    fields_read = sorted({n.slice.value for n in ast.walk(fn)
                          if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == "f"
                          and isinstance(n.slice, ast.Constant)})
    all_strings = {n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)}

    sys.path.insert(0, str(path.parent))
    replay = load(path, "packet_replay")
    rng = random.Random(20260921)
    cats = ["Accommodation", "MP Travel", "Staff Travel", "Dependant Travel", "Office Costs", "Staffing",
            "Miscellaneous", "", "Party political donation", "Penalty fine"]
    kinds = ["Hotel", "Taxi", "Mileage", "Rail", "Air", "Vehicle hire", "Subsistence", "Alcohol",
             "Campaign leaflets", "Parking fine", "", "Software & applications"]
    seen = Counter()
    for _ in range(100_000):
        f = {name: "" for name in replay.FEATURES}
        f["Category"], f["Cost Type"] = rng.choice(cats), rng.choice(kinds)
        f["Amount Claimed"] = str(rng.choice([0.01, 5, 210, 211, 10_000, 1e9, -50]))
        f["Details"] = rng.choice(["", "fine for speeding", "donation to party", "hotel London 3 nights"])
        seen[replay.decide(f)["decision"]] += 1

    sample = json.loads((EVID / "sophon_ipsa" / "results" / "sample_features.json").read_text(encoding="utf-8"))
    pairs = {(s["features"]["Category"], s["features"]["Cost Type"]) for s in sample}
    outputs = {json.dumps(replay.decide(s["features"]), sort_keys=True) for s in sample}
    return {
        "return_statements": len(returns),
        "literal_decision_values": literal_decisions,
        "CLEAR_or_BLOCK_string_anywhere_in_decide": bool({"CLEAR", "BLOCK"} & all_strings),
        "feature_fields_read_by_decide": fields_read,
        "feature_fields_available": len(replay.FEATURES),
        "fuzz_100k_decisions": dict(seen),
        "distinct_category_costtype_pairs_in_sample": len(pairs),
        "distinct_outputs_over_1000_rows": len(outputs),
        "finding": "decide() has one return whose decision is the literal 'REQUEST_FACT'. No input can produce CLEAR or "
                   "BLOCK, so '1,000 REQUEST_FACT / 0 CLEAR / 0 BLOCK' is true by construction, not an observation. "
                   "It reads 2 of 17 feature fields; the amount, description, nights, mileage and route never matter.",
    }


# ---------------------------------------------------------------- 4. mutation-test the probe guards
PROBE_MUTANTS = {
    "M0_original": None,
    "M1_always_REQUEST_AUTHORITY": ('    date = dt.date.fromisoformat(service_date)\n',
                                    '    date = dt.date.fromisoformat(service_date)\n'
                                    '    return {"status": "REQUEST_AUTHORITY", "reason": "mutant"}\n'),
    "M2_empty_event_list": ('    events = json.loads((ROOT / "authority_events.json").read_text())\n',
                            '    events = []\n'),
    "M3_no_beneficiary_check": ('if act["beneficiary"] == beneficiary and act["cost_class"] == cost_class:',
                                'if act["cost_class"] == cost_class:'),
    "M4_no_expiry_check": ('<= date <= dt.date.fromisoformat(act["valid_until"]):', '<= date:'),
    "M5_review_outcomes_and_proposals_treated_as_grants": (
        '        if act["type"] != "CASE_SPECIFIC_EXCEPTION_EVIDENCE":\n            continue\n',
        '        act = {**act, "valid_from": act["valid_from"] or "1900-01-01", '
        '"valid_until": act["valid_until"] or "2999-12-31"}\n'),
    "M6_in_window_match_clears_payment": ('"status": "AUTHORITY_EVIDENCE_ONLY"', '"status": "CLEAR"'),
}


def audit_probe_tests() -> dict:
    src_dir = EVID / "sophon_cases"
    original = (src_dir / "authority_probe.py").read_text(encoding="utf-8")
    out = {}
    for name, edit in PROBE_MUTANTS.items():
        code = original
        if edit:
            if edit[0] not in code:
                out[name] = {"error": "mutation anchor not found"}
                continue
            code = code.replace(edit[0], edit[1], 1)
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            (t / "authority_probe.py").write_text(code, encoding="utf-8")
            shutil.copy(src_dir / "test_authority_probe.py", t)
            shutil.copy(src_dir / "authority_events.json", t)
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-v", "test_authority_probe"],
                               cwd=t, capture_output=True, text=True)
            lines = [l for l in r.stderr.splitlines() if " ... " in l]
            failed = sorted(l.split(" ")[0] for l in lines if not l.rstrip().endswith("ok"))
            out[name] = {"tests_run": len(lines), "failed": failed, "mutant_detected": bool(failed)}
    tests = ["test_announcement_does_not_create_general_guidance", "test_expired_exception_does_not_authorize_new_period",
             "test_expressly_non_precedential_half_funding_does_not_spread", "test_in_window_document_does_not_clear_payment",
             "test_named_exception_does_not_transfer_to_another_person", "test_review_decision_does_not_grant_repeat_claim"]
    kills = {t: [m for m, v in out.items() if t in v.get("failed", [])] for t in tests}
    return {"mutants": out, "which_mutants_each_test_detects": kills,
            "finding": "A guard that detects no mutant asserts nothing about the behaviour in its name."}


def main() -> None:
    result = {"hashes": check_hashes(), "bundled_labels": check_labels(), "replay_decide": audit_decide(),
              "probe_guard_mutation": audit_probe_tests()}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("== frozen hashes ==")
    for k, v in result["hashes"].items():
        print(f"  {k:26s} {'MATCH' if v['match'] else 'MISMATCH'}")
    print("== bundled labels ==", result["bundled_labels"]["published_status"], result["bundled_labels"]["decisions"])
    d = result["replay_decide"]
    print("== replay.decide ==")
    print("  literal decision values:", d["literal_decision_values"], "| fuzz:", d["fuzz_100k_decisions"])
    print("  fields read:", d["feature_fields_read_by_decide"], "of", d["feature_fields_available"])
    print("  distinct outputs over 1000 rows:", d["distinct_outputs_over_1000_rows"],
          "| distinct (Category, Cost Type) pairs:", d["distinct_category_costtype_pairs_in_sample"])
    print("== probe guards: mutants each test detects ==")
    for t, ms in result["probe_guard_mutation"]["which_mutants_each_test_detects"].items():
        print(f"  {t:62s} {ms or 'NONE'}")
    for m, v in result["probe_guard_mutation"]["mutants"].items():
        print(f"  {m:52s} detected={v.get('mutant_detected')} failed={v.get('failed')}")


if __name__ == "__main__":
    main()
