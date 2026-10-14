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
