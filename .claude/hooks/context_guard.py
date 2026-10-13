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
}
REVIEW_STATUSES = {
    "IMPLEMENTED_EXPERIMENTAL_NOT_SEMANTICALLY_VALIDATED",
    "PREPARED_PENDING_SOURCE_RETRIEVAL_AND_INDEPENDENT_REVIEW",
}


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
    components = state.get("established_components", [])
    ids = [x.get("id") for x in components if isinstance(x, dict)]
    if len(ids) != len(set(ids)) or not REQUIRED.issubset(ids):
        errors.append("Established implementation inventory missing or duplicated")
    for x in components:
        if not isinstance(x, dict) or x.get("status") not in REVIEW_STATUSES:
            errors.append("Component has unrecognized / absent implementation status")
        if not x.get("path") or not x.get("ref") or not x.get("role"):
            errors.append("Component inventory must include source path, PR ref and role")
    ev = {x.get("id"): x for x in state.get("evidence", []) if isinstance(x, dict)}
    if ev.get("V3_structure_primary", {}).get("status") != "INCONCLUSIVE":
        errors.append("V3 frozen primary must remain INCONCLUSIVE (historical evidence)")
    if ev.get("V3_structure_secondary", {}).get("status") != "PROVISIONAL_UNADJUDICATED":
        errors.append("V3 secondary status changed: preserve historical result; add new adjudicated evidence separately")
    for name in ("CLAUDE.md", "AGENTS.md"):
        try:
            text = (root / name).read_text(encoding="utf-8")
            if "PROJECT_STATE.json" not in text:
                errors.append(f"{name} must point to authoritative PROJECT_STATE.json")
        except OSError:
            errors.append(f"{name} missing")
    try:
        conf = json.loads((root / ".claude/settings.json").read_text(encoding="utf-8"))
        hooks = conf.get("hooks", {})
        if not all(k in hooks for k in ("SessionStart", "UserPromptSubmit")):
            errors.append("Native Claude Code session and turn hooks missing")
    except (OSError, json.JSONDecodeError):
        errors.append(".claude/settings.json missing/invalid")
    if not state.get("working_rules") or not state.get("current_work"):
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
        p in {"SOPHON_CHARTER.md", "CLAUDE.md", "AGENTS.md"}
        or p.startswith("prototype/") and (
            p.endswith("/RESULTS.md") or p.endswith("/V2_POSTRUN_REVIEW.md")
            or p.endswith("/PROTOCOL.md")
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
    architecture = ", ".join(x["id"] for x in state["established_components"])
    results = " | ".join(f"{x['id']}={x['status']}" for x in state["evidence"])
    return (
        "SOPHON NATIVE PROJECT CONTEXT — CHECKED AUTOMATICALLY\n"
        f"Branch: {branch}; charter: v1.2; authoritative snapshot: PROJECT_STATE.json ({state['updated_at']}).\n"
        "Sophon is a normative semantic layer, NOT an LLM accuracy contest. "
        "TRANSPOSE / TRACE / VERIFY / AUDIT; independent checks in BOTH directions; "
        "BI-semantic checker wedge + direct non-BI access.\n"
        f"EXISTING (experimental; check actual PR/ref before claiming local availability): {architecture}.\n"
        f"RESULTS / LIMITS: {results}.\n"
        f"ACTIVE: {state['current_work']['active']}\n"
        f"HOLD: {state['current_work']['on_hold']}\n"
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
        for e in errors:
            print("SOPHON_CONTEXT_GUARD_ERROR: " + e, file=sys.stderr)
        print("Reconcile the authoritative state/charter on this branch before substantial work.", file=sys.stderr)
        return 2 if args.mode == "hook" else 1
    if args.mode == "hook":
        # SessionStart and UserPromptSubmit accept plain stdout as additional context.
        # Hooks are not a guarantee of factual/semantic correctness, only native context injection.
        print(context(state))
    else:
        print("SOPHON_CONTEXT_GUARD_OK: v1.2 + component inventory + hook configuration + state policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
