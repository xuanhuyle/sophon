"""Independent scorer and mechanical E4 verdict (PROTOCOL.md §5). Reads the checker's output and the FROZEN
expectations in VARIANTS.json (the checker never reads them).

    python3 src/gate.py --evidence evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

E4 = Path(__file__).resolve().parents[1]
EXP = E4.parent
OK = {"VERIFIED_FOR_LAB_CHECKS", "NO_MATERIAL_DRIFT_FOR_CHECKS"}
WRONG = ["M3", "M4", "M5", "M5B", "C3"]
CONTROLS = ["C1", "C2A", "C2B", "C4", "C5"]
MUTATION_TOKEN = {"M3": "sales__unit_price > 100", "M4": "!= 'cancelled'", "M5": "store__store_country"}
PRIOR_DIRS = ["experiments/E0_native_adapter", "experiments/E1_predicate_binding", "experiments/E2_blind_discovery",
              "experiments/E1_expressibility_erratum", "experiments/E3_formal_ir", "experiments/E3_1_integrity"]


def j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ev = Path(ap.parse_args().evidence)
    exp = {v["variant_id"]: v for v in j(E4 / "VARIANTS.json")["variants"]}
    res = {r["variant_id"]: r for r in j(ev / "run" / "variant_results.json")}
    stacks = j(ev / "run" / "candidate_stacks.json")
    ref = j(E4 / "REFERENCE.json")

    # per-variant scoring against frozen expectations
    scored = {}
    for vid, v in exp.items():
        r = res[vid]
        f = []
        if r["status"] != v["expected"]["status"]:
            f.append(f"status {r['status']} != {v['expected']['status']}")
        miss = [x for x in v["expected"]["reasons_include"] if x not in r["reasons"]]
        if miss:
            f.append(f"missing reasons {miss}")
        scored[vid] = {"status": r["status"], "expected": v["expected"]["status"], "passed": not f, "failures": f}

    e31 = j(EXP / "E3_1_integrity" / "evidence" / "gate.json")
    runtime_ok = all(stacks.get(k, {}).get("ok") for k in ("M1__PINNED", "M2__PINNED"))
    ref_ok = all(s.get("reference_equals_frozen", True) for r in res.values() for s in r["snapshots"] if "reference_equals_frozen" in s)
    q0 = e31["verdict"] == "PASS_INTEGRITY_HARDENING" and runtime_ok and ref_ok
    q1 = all(scored[x]["passed"] for x in ("M1", "M2", "M6", "M6B"))
    ce_ok = {}
    for x in WRONG:
        ces = [c for s in res[x]["snapshots"] for c in s.get("counterexamples", [])]
        ce_ok[x] = bool(ces) and all(c.get("order_item_id") and "expected_included" in c and "actual_native_included" in c
                                     and c.get("status") is not None for c in ces)
    m3 = {s["snapshot"]: s for s in res["M3"]["snapshots"]}
    m3_ok = m3["PINNED"]["status"] == "CONFORMS" and m3["BOUNDARY"]["status"] == "MISMATCH" and \
        "2" in [c["order_item_id"] for c in m3["BOUNDARY"].get("counterexamples", [])]
    q2 = all(scored[x]["passed"] for x in WRONG) and all(ce_ok.values()) and m3_ok and \
        bool((res["C3"]["candidate_claim"] or {}).get("contradicted"))
    mut = {}
    for x, tok in MUTATION_TOKEN.items():
        st = next(stacks[k] for k in stacks if k.startswith(f"{x}__"))
        mut[x] = bool(st.get("diffs")) and st["semantic_manifest_sha256"] != ref["pristine_semantic_manifest_sha256"] and \
            tok in (st["exec_year"].get("compiled_sql") or "")
    st5b = stacks["M5B__PINNED"]
    mut["M5B"] = any(d["file"].endswith("stg_customers.sql") and d["unified_diff"] for d in st5b.get("diffs", [])) and \
        any(s["status"] == "MISMATCH" for s in res["M5B"]["snapshots"])
    q3 = sum(mut.values()) >= 2
    q4 = all(scored[x]["passed"] for x in CONTROLS) and not any(res[x]["status"] in OK for x in CONTROLS)
    rp = j(ev / "replay" / "replay_record.json")
    q5 = rp["exit_code"] == 0 and rp["normalized_identical"]
    mismatch = []
    for line in (E4 / "FREEZE_MANIFEST.txt").read_text().splitlines()[2:]:
        h, name = line.split(maxsplit=1)
        if name != "PROTOCOL.md" and hashlib.sha256((E4 / name).read_bytes()).hexdigest() != h:
            mismatch.append(name)
    diff = subprocess.run(["git", "-C", str(E4), "diff", "--stat", "9f6e02a90fcc4b06216860de75906a9c4b8b0397", "--", *PRIOR_DIRS],
                          capture_output=True, text=True, cwd=str(E4))
    q6 = not mismatch and diff.returncode == 0 and diff.stdout.strip() == ""
    log = (ev / "pytest.log").read_text()
    q7 = " passed" in log and "failed" not in log and " error" not in log

    false_assurance = [x for x in WRONG + CONTROLS if res[x]["status"] in OK]
    false_alarm = [x for x in ("M6", "M6B") if res[x]["status"] == "NONCONFORMING_IMPLEMENTATION"]
    crit = {"Q0": q0, "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5, "Q6": q6, "Q7": q7}
    if e31["verdict"] != "PASS_INTEGRITY_HARDENING" or not runtime_ok:
        verdict = "BLOCKED"
    elif mismatch or not ref_ok:
        verdict = "INCONCLUSIVE"
    elif false_assurance:
        verdict = "FAIL_FALSE_ASSURANCE"
    elif false_alarm:
        verdict = "FAIL_FALSE_ALARM"
    elif all(crit.values()):
        verdict = "PASS_INDEPENDENT_VERIFICATION_SIGNAL"
    elif any(res[x]["status"] == "NONCONFORMING_IMPLEMENTATION" for x in WRONG):
        verdict = "PARTIAL_INDEPENDENT_VERIFICATION"
    else:
        verdict = "INCONCLUSIVE"
    out = {"criteria": crit, "verdict": verdict, "scored": scored, "false_assurances": false_assurance, "false_alarms": false_alarm,
           "detected_wrong": [x for x in WRONG if res[x]["status"] == "NONCONFORMING_IMPLEMENTATION"],
           "missed_wrong": [x for x in WRONG if res[x]["status"] != "NONCONFORMING_IMPLEMENTATION"],
           "counterexamples_present": ce_ok, "m3_accidental_agreement_then_boundary_detection": m3_ok,
           "native_mutation_evidence": mut, "freeze_hash_mismatch": mismatch, "prior_dirs_unchanged": diff.stdout.strip() == "",
           "pytest_tail": log.strip().splitlines()[-1] if log.strip() else ""}
    (ev / "gate.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
