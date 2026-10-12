"""Independent scorer and mechanical E5 verdict (PROTOCOL.md §7). Reads the runner's output and the FROZEN
expectations in SCENARIOS.json (the runner never reads them).

    python3 src/gate.py --evidence evidence
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

E5 = Path(__file__).resolve().parents[1]
EXP = E5.parent
BASE = "d6fe13d182e0053831c0024314ac0afc484f681a"
PRIOR_DIRS = ["experiments/E0_native_adapter", "experiments/E1_predicate_binding", "experiments/E2_blind_discovery",
              "experiments/E1_expressibility_erratum", "experiments/E3_formal_ir", "experiments/E3_1_integrity",
              "experiments/E4_independent_verification"]


def j(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def walk_states(o, bad: set, path="") -> list[str]:
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("state", "status", "review_status") and isinstance(v, str) and v in bad:
                hits.append(f"{path}.{k}={v}")
            hits += walk_states(v, bad, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            hits += walk_states(v, bad, f"{path}[{i}]")
    return hits


def score_check(r: dict, e: dict) -> list[str]:
    f = []
    if r["status"] != e["status"]:
        f.append(f"status {r['status']} != {e['status']}")
    miss = [x for x in e.get("reasons_include", []) if x not in r["reasons"]]
    if miss:
        f.append(f"missing reasons {miss}")
    snaps = {s["snapshot"]: s for s in r["snapshots"]}
    if e.get("native_executed_ok") and not all(s.get("native_executed_ok") for s in r["snapshots"]):
        f.append("native execution did not succeed on every snapshot")
    if "governing_version" in e and r["authority"].get("version") != e["governing_version"]:
        f.append(f"governing version {r['authority'].get('version')} != {e['governing_version']}")
    if e.get("every_snapshot_mismatch") and not all(s["status"] == "MISMATCH" for s in r["snapshots"]):
        f.append("not every snapshot mismatches")
    if "counterexample_band" in e:
        lo, hi = (Decimal(x) for x in e["counterexample_band"])
        for s in r["snapshots"]:
            ok = any(not c["expected_included"] and c["actual_native_included"] and lo <= Decimal(c["unit_price_raw"]) < hi
                     for c in s.get("counterexamples", []))
            if not ok:
                f.append(f"{s['snapshot']}: no counterexample priced in [{lo},{hi}) included by the candidate but not expected")
    if "counterexample_status" in e:
        for s in r["snapshots"]:
            if not any(c.get("status") == e["counterexample_status"] for c in s.get("counterexamples", [])):
                f.append(f"{s['snapshot']}: no counterexample with status {e['counterexample_status']}")
    for sn, st in e.get("snapshot_status", {}).items():
        if snaps[sn]["status"] != st:
            f.append(f"{sn}: {snaps[sn]['status']} != {st}")
    for sn, ids in e.get("counterexample_ids_include", {}).items():
        got = [c["order_item_id"] for c in snaps[sn].get("counterexamples", [])]
        if not all(i in got for i in ids):
            f.append(f"{sn}: counterexamples {got} lack {ids}")
    return f


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ev = Path(ap.parse_args().evidence)
    R = j(ev / "run" / "results.json")
    SC = j(E5 / "SCENARIOS.json")
    scen = {s["id"]: s for s in SC["scenarios"]}
    ref = j(E5 / "REFERENCE.json")
    bad = set(SC["forbidden_state_values"])
    fails: dict[str, list[str]] = {}

    def need(sid: str, cond: bool, msg: str) -> None:
        if not cond:
            fails.setdefault(sid, []).append(msg)

    # ---- authority states (F1, F1B, F2)
    for sid in ("F1", "F1B", "F2"):
        e, a = scen[sid]["expected"], R["authority"][sid]
        need(sid, a["version_state"] == e["version_state"], f"version_state {a['version_state']}")
        need(sid, a["governing"] == e["governing"], f"governing {a['governing']}")
    need("F2", R["F2_lifecycle_before_proposal"]["state"] == scen["F2"]["expected"]["lifecycle_before_proposal"], "lifecycle before proposal")
    # ---- native checks (F1, F1B, F2, F4, N2)
    for sid in ("F1", "F1B", "F2", "F4", "N2"):
        for c in scen[sid]["checks"]:
            for m in score_check(R["checks"][c["check_id"]], c["expected"]):
                fails.setdefault(sid, []).append(f"{c['check_id']}: {m}")
    # ---- F3
    e, f3 = scen["F3"]["expected"], R["F3"]
    for k in ("status", "modified_metrics", "delta", "patch_files", "generated_stack_builds", "metric_name_set_unchanged",
              "p2_block_unchanged_by_patch", "no_repository_file_opened_by_transposer", "patch_differs_from_every_frozen_candidate"):
        need("F3", f3.get(k) == e[k], f"{k}: {f3.get(k)!r} != {e[k]!r}")
    need("F3", all(x in f3["not_affected"] for x in e["not_affected_includes"]), "not_affected")
    need("F3", e["compiled_sql_contains"] in (f3.get("generated_compiled_sql") or ""), "compiled SQL lacks the amended predicate")
    # ---- F5
    e = scen["F5"]["expected"]
    for rid in ("F5.K_POST", "F5.K_PRE"):
        got = R["F5"]["routings"][rid]
        segs = [{k: s[k] for k in ("window", "version", "revision", "status")} for s in got["segments"]]
        need("F5", segs == e[rid]["segments"], f"{rid} segments {segs}")
        need("F5", got["combined_equals_reference"]["reference"] == e[rid]["combined_equals_reference"]
             and all(got["combined_equals_reference"]["per_snapshot"].values()), f"{rid} combined != reference")
    need("F5", R["F5"]["routings"]["F5.K_POST"]["combined"]["PINNED"]["by_year"].get("2024") == e["F5.K_POST"]["pinned_2024_total"], "2024 total")
    need("F5", not any(s["version"] == "P1_v2" for s in R["F5"]["routings"]["F5.K_PRE"]["segments"]), "v2 leaked into K_PRE")
    need("F5", all(v["differs_in_2024"] for v in R["F5"]["naive_single_revision"].values()) == e["naive_single_revision_rewrites_2024"], "naive")
    # ---- F6 / N3
    for sid in ("F6", "N3"):
        for k, v in scen[sid]["expected"].items():
            need(sid, R[sid].get(k) == v, f"{k}: {R[sid].get(k)!r} != {v!r}")
    # ---- F7 / N4 / forbidden states
    e, f7 = scen["F7"]["expected"], R["F7"]
    for k in ("state", "deployed", "deployment_authorization", "reviewer_decision"):
        need("F7", f7.get(k) == e[k], f"{k}: {f7.get(k)!r}")
    need("F7", bool(f7["original_semantic_manifest_sha256"]) and bool(f7["proposed_semantic_manifest_sha256"])
         and f7["original_semantic_manifest_sha256"] != f7["proposed_semantic_manifest_sha256"], "manifest shas")
    forbidden_hits = walk_states(R, bad)
    need("F7", not forbidden_hits, f"forbidden states {forbidden_hits[:5]}")
    for case in scen["N4"]["cases"]:
        got = R["N4"][case["case_id"]]
        need("N4", got["state"] == case["expected"]["state"] and all(x in got["reasons"] for x in case["expected"].get("reasons_include", [])),
             f"{case['case_id']}: {got}")
    # ---- N1
    for ctl in scen["N1"]["controls"]:
        got = R["N1"][ctl["control_id"]]
        need("N1", got["status"] == ctl["expected"]["status"] and all(x in got["reasons"] for x in ctl["expected"]["reasons_include"])
             and got["patch"] is None and got["no_repository_file_opened"], f"{ctl['control_id']}: {got['status']} {got['reasons']}")
    # ---- F8 replay
    rp = j(ev / "replay" / "replay_record.json")
    need("F8", rp["exit_code"] == scen["F8"]["expected"]["exit_code"] and rp["normalized_identical"] == scen["F8"]["expected"]["normalized_identical"], "replay")

    # ---- integrity, isolation, prerequisites
    e4 = j(EXP / "E4_independent_verification" / "evidence" / "gate.json")
    g0b = R["G0_baseline"]
    baseline_ok = bool(g0b["build_ok"] and g0b["p1_ok"] and g0b["p2_ok"])
    ref_ok = all(s.get("reference_equals_frozen", True) for c in R["checks"].values() for s in c["snapshots"]) and \
        all(s.get("reference_equals_frozen", True) for rt in R["F5"]["routings"].values() for sg in rt["segments"] for s in sg["check"]["snapshots"]) and \
        R["snapshots_match_frozen"] and all(ref["cross_check_with_e4_frozen_reference"].values())
    packet_ok = R["packet_sha256"] == ref["transpose_packet_sha256"] == hashlib.sha256((E5 / "TRANSPOSE_PACKET.json").read_bytes()).hexdigest()
    isolation_ok = bool(R["transposer"]["invocation"]["no_repository_file_opened"])
    tsrc = (E5 / "src" / "transposer.py").read_text(encoding="utf-8")
    src_clean = not re.search(r"(?<![\d.])120(?![\d])", tsrc) and not re.search(r"REFERENCE|SCENARIOS|oracle", tsrc)
    sens = R["sensitivity_non_scored"]
    sens_ok = (sens["threshold_135_reapproved"]["emitted_filter"] or "").endswith(">= 135") and \
        (sens["threshold_120.00_same_text"]["emitted_filter"] or "").endswith(">= 120") and \
        (sens["threshold_99.5_reapproved"]["emitted_filter"] or "").endswith(">= 99.5")
    mism = []
    for line in (E5 / "FREEZE_MANIFEST.txt").read_text().splitlines()[2:]:
        h, name = line.split(maxsplit=1)
        if name != "PROTOCOL.md" and hashlib.sha256((E5 / name).read_bytes()).hexdigest() != h:
            mism.append(name)
    d = subprocess.run(["git", "-C", str(E5), "diff", "--stat", BASE, "--", *PRIOR_DIRS], capture_output=True, text=True)
    outside = subprocess.run(["git", "-C", str(E5), "diff", "--name-only", BASE], capture_output=True, text=True).stdout.split()
    outside = [x for x in outside if not x.startswith("experiments/E5_forward_transposition/")]
    log = (ev / "pytest.log").read_text()
    prop = R["transposer"]["proposal"] or {}
    frozen_patches = [j(p)["patch"] for p in (E5 / "candidates").glob("*.json")]

    crit = {
        "G0": e4["verdict"] == "PASS_INDEPENDENT_VERIFICATION_SIGNAL" and baseline_ok and ref_ok,
        "G1": "F3" not in fails and isolation_ok and packet_ok and src_clean and sens_ok,
        "G2": not any(s in fails for s in ("F1", "F1B", "F2")),
        "G3": not any(s in fails for s in ("F4", "N2")),
        "G4": "F5" not in fails,
        "G5": not any(s in fails for s in ("F6", "N3")),
        "G6": not any(s in fails for s in ("F7", "N4")),
        "G7": "N1" not in fails,
        "G8": "F8" not in fails,
        "G9": not mism and d.returncode == 0 and d.stdout.strip() == "" and not outside,
        "G10": " passed" in log and "failed" not in log and " error" not in log,
        "G11": (ev / "run" / "cost_log.json").exists() and R["cost"]["paid_calls"] == 0,
    }
    routing_post = R["F5"]["routings"]["F5.K_POST"]["segments"]
    unsafe = {
        "baseline_verified_for_v2": R["checks"]["F2.baseline_vs_governing"]["status"] == "VERIFIED_FOR_LAB_CHECKS",
        "wrong_patch_verified": [c for c in ("N2A", "N2B", "N2C") if R["checks"][c]["status"] == "VERIFIED_FOR_LAB_CHECKS"],
        "p2_collateral_undetected": R["N3"]["status"] != "P2_CHANGED_DETECTED",
        "n1_produced_patch": [k for k, v in R["N1"].items() if v["patch"] is not None or v["status"] == "PROPOSED_NOT_DEPLOYED"],
        "v2_verified_before_authority": [c for c in ("F1.generated_vs_requested_v2", "F1B.generated_vs_requested_v2")
                                         if R["checks"][c]["status"] == "VERIFIED_FOR_LAB_CHECKS"],
        "future_leak_k_pre": any(s["version"] == "P1_v2" for s in R["F5"]["routings"]["F5.K_PRE"]["segments"]),
        "v2_applied_to_2024": any(s["version"] == "P1_v2" and s["window"][0] < "2025-01-01" for s in routing_post),
        "forbidden_states": forbidden_hits,
    }
    unsafe_any = any(bool(v) for v in unsafe.values())
    no_transposition = prop.get("status") != "PROPOSED_NOT_DEPLOYED" or not prop.get("patch") or \
        any(prop.get("patch") == fp for fp in frozen_patches) or not sens_ok
    if unsafe_any:
        verdict = "FAIL_UNSAFE_TRANSPOSITION"
    elif mism or not ref_ok or not packet_ok or not isolation_ok:
        verdict = "INCONCLUSIVE"
    elif e4["verdict"] != "PASS_INDEPENDENT_VERIFICATION_SIGNAL" or not baseline_ok:
        verdict = "BLOCKED"
    elif no_transposition:
        verdict = "FAIL_NO_TRANSPOSITION"
    elif all(crit.values()):
        verdict = "PASS_FORWARD_TRANSPOSITION_SIGNAL"
    else:
        verdict = "PARTIAL_FORWARD_TRANSPOSITION_SIGNAL"
    out = {"verdict": verdict, "criteria": crit, "scenario_failures": fails, "unsafe_conditions": unsafe,
           "integrity": {"freeze_hash_mismatch": mism, "prior_dirs_unchanged": d.stdout.strip() == "", "files_changed_outside_e5": outside,
                         "packet_sha_matches_frozen": packet_ok, "reference_equals_frozen": ref_ok,
                         "transposer_opened_no_repository_file": isolation_ok, "transposer_source_has_no_answer_literal_or_reference_names": src_clean},
           "sensitivity_non_scored": {k: v["emitted_filter"] for k, v in sens.items()}, "sensitivity_ok": sens_ok,
           "pytest_tail": log.strip().splitlines()[-1] if log.strip() else ""}
    (ev / "gate.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
