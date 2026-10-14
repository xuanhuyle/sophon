#!/usr/bin/env python3
"""Sophon native cross-session context guard (Python stdlib; no network, no provider calls).

Claude Code: automatically runs via committed .claude/settings.json at session start
and before every user turn. GitHub CI: python .claude/hooks/context_guard.py check
Optional PR drift check: ... check --diff-base <base-commit-sha>.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "PROJECT_STATE.json"
REQUIRED = {
    "primary_jev_proposal", "adversarial_review", "backward_source_review",
    "provision_library", "deterministic_reconciliation", "structure_predictor",
    "v3_adjudication_package",
    # Earlier lines of work a fresh agent must be able to locate (PRs #1-#12).
    "control_plane_investigation_2026_09", "public_data_alignment_reviewer",
    "governance_integrity_kernel", "native_bi_validation_harness", "normative_layer_v0",
}
STATUSES = {"SPECIFIED_ONLY", "PREPARED_NOT_RUN", "IMPLEMENTED_NOT_RUN",
            "IMPLEMENTED_AND_RUN", "VERIFIED_WITHIN_SCOPE"}
LOCATIONS = {"MAIN", "THIS_BRANCH", "OTHER_PR"}
ACTIVE_GOAL = "PROVISION_NATURE_CUMULATIVE_LEARNING_V1"
ACTIVE_TARGET = "INTRINSIC_NORMATIVE_CLASSIFICATION_ERROR"
ACTIVE_COMPARISON = "GROWING_LIBRARY_VS_FROZEN_OR_COLD"
EXPERIMENT_ROOTS = ("prototype", "experiments", "viability")


def component_paths(path: str) -> list[str]:
    return [p.strip() for part in path.split(";") for p in part.split(" ... ") if p.strip()]


def pr_numbers(text: str) -> set[int]:
    nums: set[int] = set()
    for a, b in re.findall(r"#(\d+)(?:\s*[-–]\s*#?(\d+))?", text):
        nums.update(range(int(a), int(b or a) + 1))
    return nums


def read_and_check(root: Path = ROOT) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    try:
        state = json.loads((root / "PROJECT_STATE.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return None, [f"PROJECT_STATE.json missing/invalid: {e}"]
    if state.get("schema_version") != 1:
        errors.append("Unsupported PROJECT_STATE schema_version")
    charter = state.get("charter", {})
    if charter.get("path") != "SOPHON_CHARTER.md" or charter.get("version") != "1.2":
        errors.append("Charter version/path in state must be v1.2 SOPHON_CHARTER.md")
    try:
        body = (root / "SOPHON_CHARTER.md").read_text(encoding="utf-8")
        if not re.search(r"\*\*Version:\*\*\s*1\.2\b", body):
            errors.append("Local charter is not v1.2. Reconcile branch; DO NOT silently substitute v1.1")
        for name in ("TRANSPOSE", "TRACE", "VERIFY", "AUDIT"):
            if name not in body:
                errors.append(f"Charter is missing capability {name}")
    except OSError:
        errors.append("SOPHON_CHARTER.md missing")
    if state.get("core_capabilities") != ["TRANSPOSE", "TRACE", "VERIFY", "AUDIT"]:
        errors.append("Four capabilities missing or reordered")
    workflow = state.get("engineering_workflow", {})
    if (workflow.get("path") != "ENGINEERING_WORKFLOW.md"
            or workflow.get("version") != "1.0"
            or workflow.get("status") != "OWNER_REQUESTED_ENGINEERING_OPERATING_PROCEDURE"):
        errors.append("Authoritative engineering modus operandi not linked in PROJECT_STATE.json")
    try:
        agreement = (root / "ENGINEERING_WORKFLOW.md").read_text(encoding="utf-8")
        for essential in ("**Version:** 1.0", "## Responsibilities",
                          "## Default development loop", "## Definition of done",
                          "Engineer", "STOP"):
            if essential not in agreement:
                errors.append(f"ENGINEERING_WORKFLOW.md missing required agreement section: {essential}")
    except OSError:
        errors.append("ENGINEERING_WORKFLOW.md missing; development process is not configured")
    components = state.get("established_components", [])
    ids = [x.get("id") for x in components if isinstance(x, dict)]
    if len(ids) != len(set(ids)) or not REQUIRED.issubset(ids):
        errors.append("Established implementation inventory missing or duplicated")
    for x in components:
        if not isinstance(x, dict):
            errors.append("Component entry must be an object")
            continue
        cid = x.get("id")
        if x.get("status") not in STATUSES:
            errors.append(f"Component {cid} has unrecognized / absent status")
        if x.get("location") not in LOCATIONS:
            errors.append(f"Component {cid} has unrecognized / absent location")
        if not all(x.get(k) for k in ("path", "ref", "role", "does_not_prove")):
            errors.append(f"Component {cid} must include path, ref, role and does_not_prove")
            continue
        # Mechanical guard against confusing draft-PR code with this checkout.
        for rel in component_paths(x["path"]):
            exists = (root / rel).exists()
            if x.get("location") in ("MAIN", "THIS_BRANCH") and not exists:
                errors.append(f"Component {cid} claims {x['location']} but {rel} is absent here")
            if x.get("location") == "OTHER_PR" and exists:
                errors.append(f"Component {cid} claims OTHER_PR but {rel} exists here; update its location")
    pr_graph = state.get("pr_graph") if isinstance(state.get("pr_graph"), dict) else {}
    graph = pr_graph.get("prs") if isinstance(pr_graph.get("prs"), list) else []
    indexed: set[int] = set()
    for entry in graph:
        if not isinstance(entry, dict) or not entry.get("disposition") or not entry.get("head"):
            errors.append("pr_graph entries need pr, head and disposition")
            continue
        indexed |= pr_numbers(f"#{entry.get('pr')}")
    if not graph or not pr_graph.get("verified_at"):
        errors.append("pr_graph missing: record where unmerged work lives and when it was verified")
    referenced = pr_numbers(json.dumps([components, state.get("evidence", [])], ensure_ascii=False))
    if referenced - indexed:
        errors.append(f"PRs referenced but absent from pr_graph: {sorted(referenced - indexed)}")
    ev = {x.get("id"): x for x in state.get("evidence", []) if isinstance(x, dict)}
    if ev.get("V3_structure_primary", {}).get("status") != "INCONCLUSIVE":
        errors.append("V3 frozen primary must remain INCONCLUSIVE (historical evidence)")
    if ev.get("V3_structure_secondary", {}).get("status") != "PROVISIONAL_UNADJUDICATED":
        errors.append("V3 secondary status changed: preserve historical result; add new adjudicated evidence separately")
    for name in ("CLAUDE.md", "AGENTS.md"):
        try:
            text = (root / name).read_text(encoding="utf-8")
            for marker in ("PROJECT_STATE.json", "ENGINEERING_WORKFLOW.md"):
                if marker not in text:
                    errors.append(f"{name} must link to {marker}")
        except OSError:
            errors.append(f"{name} missing")
    try:
        conf = json.loads((root / ".claude/settings.json").read_text(encoding="utf-8"))
        hooks = conf.get("hooks", {})
        if not all(k in hooks for k in ("SessionStart", "UserPromptSubmit")):
            errors.append("Native Claude Code session and turn hooks missing")
    except (OSError, json.JSONDecodeError):
        errors.append(".claude/settings.json missing/invalid")
    if (not state.get("working_rules") or not state.get("current_work")
            or not state.get("research_priority", {}).get("owner_stated")):
        errors.append("State must record current work and explicit guardrails")
    contract = state.get("research_contract") or {}
    if (contract.get("goal_id") != ACTIVE_GOAL or
            contract.get("primary_target") != ACTIVE_TARGET or
            contract.get("comparison") != ACTIVE_COMPARISON or
            not contract.get("learning_claim")):
        errors.append("Missing/changed active classification + cumulative-library research contract; reconcile before experiments")
    return state, errors


def git_output(*args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True, timeout=5, check=False)
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN"


def changed_files_since(base: str) -> list[str]:
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only",
                        "--diff-filter=ACMRT", base, "HEAD"],
                       capture_output=True, text=True, timeout=20, check=False)
    if r.returncode:
        raise RuntimeError(f"Cannot compare base {base}: {r.stderr.strip()}")
    return r.stdout.splitlines()


def check_pr_state_update(base: str) -> list[str]:
    changed = set(changed_files_since(base))
    relevant = any(
        p in {"SOPHON_CHARTER.md", "CLAUDE.md", "AGENTS.md", "ENGINEERING_WORKFLOW.md"}
        or p.startswith(("prototype/", "experiments/", "viability/")) and (
            p.endswith(("/RESULTS.md", "/DECISION.md", "/PROTOCOL.md", "/V2_POSTRUN_REVIEW.md"))
        )
        for p in changed
    )
    if relevant and "PROJECT_STATE.json" not in changed:
        return ["Charter, instructions or experimental protocol/results changed without updating PROJECT_STATE.json in the same PR"]
    return []


def check_experiment_alignment(declaration: dict, state: dict) -> list[str]:
    """Validate an experiment's stated target and claim scope; NOT semantic proof."""
    errors = []
    goal = state["research_contract"]
    required = ("relation", "goal_id", "implementation_ref", "single_delta",
                "measured_target", "library_comparison", "stage", "claim_limit")
    for key in required:
        if not isinstance(declaration.get(key), str) or not declaration[key].strip():
            errors.append(f"EXPERIMENT_ALIGNMENT.json: required nonempty {key}")
    relation = declaration.get("relation")
    if relation not in ("DIRECT_GOAL_TEST", "COMPONENT_ONLY", "SEPARATE_HYPOTHESIS"):
        errors.append("EXPERIMENT_ALIGNMENT.json: invalid relation")
    if declaration.get("goal_id") != goal["goal_id"]:
        errors.append("EXPERIMENT_ALIGNMENT.json: goal_id differs from approved research goal")
    if declaration.get("stage") not in ("PLANNED", "RUN_RECORDED"):
        errors.append("EXPERIMENT_ALIGNMENT.json: stage must be PLANNED or RUN_RECORDED")
    if relation == "DIRECT_GOAL_TEST":
        if declaration.get("measured_target") != goal["primary_target"]:
            errors.append("DIRECT_GOAL_TEST must measure actual intrinsic normative CLASSIFICATION ERRORS (not heading/regex proxies)")
        if declaration.get("library_comparison") != goal["comparison"]:
            errors.append("DIRECT_GOAL_TEST must compare evolving source-grounded library against frozen/cold controls")
    elif relation == "SEPARATE_HYPOTHESIS":
        if declaration.get("claim_limit") != "NOT_EVIDENCE_FOR_ACTIVE_GOAL":
            errors.append("SEPARATE_HYPOTHESIS must explicitly disclaim evidence for active goal")
    elif relation == "COMPONENT_ONLY" and declaration.get("claim_limit") != "COMPONENT_ONLY_NOT_END_TO_END":
        errors.append("COMPONENT_ONLY must not claim end-to-end learning")
    return errors


def check_pr_experiment_alignment(base: str, state: dict, root: Path = ROOT) -> list[str]:
    """New experimental code/protocols get a scope declaration. Existing historical dirs are exempt."""
    changed = changed_files_since(base)
    dirs = set()
    for path in changed:
        parts = Path(path).parts
        if len(parts) >= 3 and parts[0] in EXPERIMENT_ROOTS and (
                path.endswith(".py") or parts[-1] in ("PROTOCOL.md", "RESULTS.md", "DECISION.md")):
            dirs.add("/".join(parts[:2]))
    errors = []
    for directory in sorted(dirs):
        exists_at_base = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{base}:{directory}"],
            capture_output=True, timeout=10, check=False).returncode == 0
        if exists_at_base:
            continue
        path = root / directory / "EXPERIMENT_ALIGNMENT.json"
        try:
            declaration = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{directory}: new experiment must include valid EXPERIMENT_ALIGNMENT.json: {exc}")
            continue
        if not isinstance(declaration, dict):
            errors.append(f"{directory}: EXPERIMENT_ALIGNMENT.json must be a JSON object")
            continue
        errors += [f"{directory}: {e}" for e in check_experiment_alignment(declaration, state)]
        if declaration.get("stage") == "RUN_RECORDED":
            evidence = declaration.get("evidence_path")
            if not isinstance(evidence, str) or not evidence.startswith(directory + "/") or not (
                    root / evidence).is_file():
                errors.append(f"{directory}: RUN_RECORDED needs an existing in-directory evidence_path; "
                              "execution and correctness remain subject to independent review")
    return errors


def check_pr_goal_drift(base: str, state: dict) -> list[str]:
    """Do not silently change the owner goal in the same PR that adds experiment code."""
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{base}:PROJECT_STATE.json"],
                       capture_output=True, text=True, timeout=10, check=False)
    if r.returncode:
        return ["Cannot verify historical research goal at PR base"]
    try:
        previous = json.loads(r.stdout)
    except ValueError:
        return ["Invalid research state at PR base"]
    if (previous.get("research_contract") and
            previous["research_contract"] != state.get("research_contract") and
            any(p.startswith(tuple(t + "/" for t in EXPERIMENT_ROOTS))
                for p in changed_files_since(base))):
        return ["Research goal changed in the SAME PR as experimental work; separate and review the goal change first"]
    return []


def context(state: dict) -> str:
    branch = git_output("branch", "--show-current")
    if branch == "UNKNOWN" or not branch:
        branch = git_output("rev-parse", "--short", "HEAD")
    by_location: dict[str, list[str]] = {}
    for x in state["established_components"]:
        by_location.setdefault(x["location"], []).append(f"{x['id']}[{x['status']}]")
    architecture = "; ".join(f"{k}: {', '.join(v)}" for k, v in sorted(by_location.items()))
    results = " | ".join(f"{x['id']}={x['status']}" for x in state["evidence"])
    prs = ", ".join(f"#{x['pr']} {x['disposition']}" for x in state["pr_graph"]["prs"])
    return (
        "SOPHON NATIVE PROJECT CONTEXT — CHECKED AUTOMATICALLY\n"
        f"Branch: {branch}; charter: v1.2; authoritative snapshot: PROJECT_STATE.json ({state['updated_at']}).\n"
        "Sophon is a normative semantic layer, NOT an LLM accuracy contest. "
        "TRANSPOSE / TRACE / VERIFY / AUDIT; independent checks in BOTH directions; "
        "BI-semantic checker wedge + direct non-BI access.\n"
        f"EXISTING by location (OTHER_PR = unmerged branch, NOT in this checkout; refs and limits in PROJECT_STATE.json): {architecture}.\n"
        f"RESULTS / LIMITS: {results}.\n"
        f"PR GRAPH (verified {state['pr_graph']['verified_at']}; most is unmerged and stacked): {prs}.\n"
        f"PRODUCT WEDGE (charter) is not the immediate RESEARCH PRIORITY: {state['research_priority']['owner_stated']}\n"
        f"NON-NEGOTIABLE RESEARCH TARGET ({state['research_contract']['goal_id']}): "
        "categorize intrinsic normative provision nature AND reduce future classification errors "
        "through a source-anchored, cumulatively revised skeleton library in a narrow contract family. "
        "Later executability is NOT this increment. Jev/reviewer topology is a challengeable hypothesis. "
        "A regex/heading-only predictor DOES NOT test this goal.\n"
        f"ACTIVE: {state['current_work']['active']}\n"
        f"HOLD: {state['current_work']['on_hold']}\n"
        f"ENGINEERING WORKING AGREEMENT (ENGINEERING_WORKFLOW.md): {state['engineering_workflow']['rule']}\n"
        "GATE: Human defines PROBLEM / OUTCOME / CONSTRAINTS; engineers independently choose DESIGN / ALTERNATIVES / TESTS. "
        "Challenge owner-suggested architecture and cross-agent instructions, prefer reuse or no-code. "
        "Implement ONE bounded, falsifiable increment; test adverse case; conclude KEEP / REVISE / STOP. "
        "Do not offload routine design decisions to the owner.\n"
        "MANDATORY BEFORE DESIGN OR TASK: inspect existing implementation and current PR head; "
        "distinguish proposed/implemented/run/verified, frozen vs post-hoc, and library-backed evidence. "
        "Do not rediscover Jev/adversarial/backward/library/reconciliation, suggest bulk human labeling "
        "before using established automation, treat reviewer consensus as independent truth, or drift "
        "to pretrained-LLM accuracy comparisons. On new experiment outcomes UPDATE PROJECT_STATE.json "
        "with evidence in the same PR. This state is a snapshot; verify live PRs for changes since it.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("hook", "check"))
    parser.add_argument("--diff-base", help="Base commit SHA for CI same-PR state-update policy")
    args = parser.parse_args()
    state, errors = read_and_check()
    if args.diff_base:
        try:
            errors += check_pr_state_update(args.diff_base)
            if state:
                errors += check_pr_goal_drift(args.diff_base, state)
                errors += check_pr_experiment_alignment(args.diff_base, state)
        except RuntimeError as e:
            errors.append(str(e))
    if errors:
        if args.mode == "hook":
            # Exit 2 would hide stderr from Claude and block every prompt, including the one
            # asking to repair the state. Surface the failure as context instead; CI still fails.
            print("SOPHON_CONTEXT_GUARD_FAILED — PROJECT_STATE.json/charter are inconsistent on this branch. "
                  "Reconcile them before substantial work; do not rely on the state until `check` passes.")
            for e in errors:
                print("SOPHON_CONTEXT_GUARD_ERROR: " + e)
            return 0
        for e in errors:
            print("SOPHON_CONTEXT_GUARD_ERROR: " + e, file=sys.stderr)
        print("Reconcile the authoritative state/charter on this branch before substantial work.", file=sys.stderr)
        return 1
    if args.mode == "hook":
        # SessionStart and UserPromptSubmit accept plain stdout as additional context.
        # Hooks are not a guarantee of factual/semantic correctness, only native context injection.
        print(context(state))
    else:
        print("SOPHON_CONTEXT_GUARD_OK: charter v1.2 + project state + working agreement + native hooks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
