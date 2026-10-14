#!/usr/bin/env python3
"""Sophon native cross-session context guard (Python stdlib; no network, no provider calls).

Claude Code: automatically runs via committed .claude/settings.json at session start
and before every user turn. GitHub CI: python .claude/hooks/context_guard.py check
Optional PR drift check: ... check --diff-base <base-commit-sha>.
Mechanism declaration template for experiment directories: ... template
"""
from __future__ import annotations

import argparse
import ast
import hashlib
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

# sha256 of PROJECT_STATE.json active_research_mechanism (canonical JSON). Change it only in an
# owner-reviewed PR that touches no experiment directory; that PR is the visible pivot record.
LINEAGE_FINGERPRINT = "98b870e915018f0708574e0114a6e617c874d053fdbffa6745616cef84f44992"
EXPERIMENT_TOPS = ("prototype", "experiments", "viability")
RECORD_FILE = re.compile(r"(PROTOCOL|RESULTS|DECISION|POSTRUN_REVIEW)\.md$")
STAGES = ("PLANNING", "PLUMBING_ONLY", "RUN")
MECHANISM_TEMPLATE = {
    "relation": "CONTINUES_ACTIVE_LINEAGE  (or SEPARATE_MECHANISM with hypothesis + not_a_test_of)",
    "lineage_id": "jev_source_grounded_provision_skeleton_loop",
    "parent_ref": {"pr": 17, "branch": "experiment/jev-v3-context-funnel-2026-10-13", "head": "b9d698c"},
    "delta_step": "independent_library_based_review",
    "single_delta": "what new capability this increment adds",
    "preserved_steps": ["every other intended_chain step"],
    "runner": "prototype/<dir>/<file>.py::<function the run starts from>",
    "invoked": {"<required step>": {"status": "PLANNED | INVOKED", "entry_point": "<pinned path::symbol>"}},
    "stage": "PLANNING | PLUMBING_ONLY | RUN",
    "provider_calls": 0,
    "delta_receipt_role": "<steps key the new reviewer writes in run records>",
    "run_receipts": [{"path": "prototype/<dir>/<record>.json", "sha256": "<hex>"}],
    "execution_verification": "RUN only: RECEIPT_CONSISTENT | UNVERIFIED",
    "claims": "what a pass/fail can legitimately support",
    "cannot_prove": "what it cannot show",
}


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
    errors += check_lineage_pin(state, set(ids))
    return state, errors


def lineage_fingerprint(pin) -> str:
    canon = json.dumps(pin, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def check_lineage_pin(state: dict, component_ids: set) -> list[str]:
    pin = state.get("active_research_mechanism")
    if not isinstance(pin, dict):
        return ["active_research_mechanism lineage pin missing/malformed in PROJECT_STATE.json; "
                "do not continue research from memory or an older branch"]
    errors = []
    chain = pin.get("intended_chain") if isinstance(pin.get("intended_chain"), list) else []
    steps = [s.get("step") for s in chain if isinstance(s, dict)]
    ref = pin.get("parent_ref") if isinstance(pin.get("parent_ref"), dict) else {}
    if (not pin.get("id") or len(steps) != len(chain) or len(set(steps)) != len(steps)
            or not set(pin.get("continuation_requires_invoked") or [None]) <= set(steps)
            or pin.get("next_single_delta_step") not in steps
            or not all(ref.get(k) for k in ("pr", "branch", "head"))
            or any(s.get("component") not in component_ids or not isinstance(s.get("entry_points"), list)
                   for s in chain if isinstance(s, dict))):
        errors.append("active_research_mechanism is malformed: needs id, parent_ref{pr,branch,head}, "
                      "unique intended_chain steps with known components and entry_points, "
                      "continuation_requires_invoked and next_single_delta_step")
    fp = lineage_fingerprint(pin)
    if fp != LINEAGE_FINGERPRINT:
        errors.append(f"active_research_mechanism changed (fingerprint {fp[:12]}, guard pins {LINEAGE_FINGERPRINT[:12]}). "
                      "A lineage change needs an owner-reviewed PR touching no experiment directory that also "
                      "updates LINEAGE_FINGERPRINT in .claude/hooks/context_guard.py")
    return errors


def experiment_dirs(root: Path, extra: set[str] = frozenset()) -> list[str]:
    dirs = set(extra)
    for top in EXPERIMENT_TOPS:
        if (root / top).is_dir():
            dirs |= {f"{top}/{d.name}" for d in (root / top).iterdir() if d.is_dir()}
    return sorted(dirs)


def pinned_dirs(pin: dict) -> set[str]:
    """Directories holding the lineage's own pinned implementation (imported parent code, not new experiments)."""
    return {str(Path(e.split("::")[0]).parent) for s in pin.get("intended_chain", []) if isinstance(s, dict)
            for e in s.get("entry_points") or []}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _index(paths: list[Path]) -> tuple[dict, dict]:
    """Function definitions by name, and per-file `from x import name [as alias]` bindings."""
    defs: dict[str, list[tuple[Path, ast.AST]]] = {}
    imports: dict[Path, dict[str, str]] = {}
    for path in paths:
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        imports[path] = {a.asname or a.name: a.name for n in ast.walk(tree)
                         if isinstance(n, ast.ImportFrom) for a in n.names}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs.setdefault(node.name, []).append((path, node))
    return defs, imports


def reachable(defs: dict, imports: dict, start: tuple[Path, str]) -> set[tuple[Path, str]]:
    """Static call closure from one function. Bare calls resolve in the same file or via `from x import`;
    `obj.f()` resolves to any indexed f. Over-approximates; never proof of execution."""
    seen: set[tuple[Path, str]] = set()
    todo = [start]
    while todo:
        key = todo.pop()
        if key in seen:
            continue
        seen.add(key)
        for path, node in defs.get(key[1], []):
            if path != key[0]:
                continue
            for call in ast.walk(node):
                f = getattr(call, "func", None) if isinstance(call, ast.Call) else None
                if isinstance(f, ast.Attribute):
                    todo += [(q, f.attr) for q, _ in defs.get(f.attr, [])]
                elif isinstance(f, ast.Name):
                    local = [(q, f.id) for q, _ in defs.get(f.id, []) if q == path]
                    name = imports.get(path, {}).get(f.id)
                    todo += local or ([(q, name) for q, _ in defs.get(name, [])] if name else [])
    return seen


def _role_steps(obj) -> list[dict]:
    if isinstance(obj, dict):
        out = [obj["steps"]] if isinstance(obj.get("steps"), dict) else []
        return out + [s for v in obj.values() for s in _role_steps(v)]
    if isinstance(obj, list):
        return [s for v in obj for s in _role_steps(v)]
    return []


def receipt_status(root: Path, exp: str, decl: dict, roles: list[str]) -> tuple[str, str]:
    receipts = decl.get("run_receipts")
    if not isinstance(receipts, list) or not receipts:
        return "UNVERIFIED", "no run_receipts declared"
    for r in receipts:
        if not isinstance(r, dict):
            return "UNVERIFIED", "run_receipts entries must be {path, sha256}"
        path = root / str(r.get("path", ""))
        if not str(r.get("path", "")).startswith(exp + "/") or not path.is_file():
            return "UNVERIFIED", f"receipt {r.get('path')} is not committed inside {exp}"
        if hashlib.sha256(path.read_bytes()).hexdigest() != r.get("sha256"):
            return "UNVERIFIED", f"receipt {r.get('path')} sha256 mismatch"
        try:
            record = json.loads(_read(path))
        except json.JSONDecodeError:
            return "UNVERIFIED", f"receipt {r.get('path')} is not a JSON run record (hash-only receipts are not execution evidence)"
        if not any(all((s.get(role) or {}).get("provenance") == "ACTUAL_PROVIDER" and (s.get(role) or {}).get("raw_response")
                       for role in roles) for s in _role_steps(record)):
            return "UNVERIFIED", f"receipt {r.get('path')} has no record with ACTUAL_PROVIDER raw_response for roles {roles}"
    return "RECEIPT_CONSISTENT", ""


def check_mechanism(root: Path, exp: str, pin: dict) -> list[str]:
    """Check one experiment directory's MECHANISM.json against the pin and the actual source."""
    tag = f"{exp}/MECHANISM.json"
    try:
        decl = json.loads((root / tag).read_text(encoding="utf-8"))
    except OSError:
        return [f"{tag} missing: declare CONTINUES_ACTIVE_LINEAGE or SEPARATE_MECHANISM (context_guard.py template)"]
    except json.JSONDecodeError as e:
        return [f"{tag} invalid JSON: {e}"]
    if not isinstance(decl, dict):
        return [f"{tag} must be an object"]
    errors = [f"{tag}: '{k}' required" for k in ("claims", "cannot_prove") if not decl.get(k)]
    stage, calls = decl.get("stage"), decl.get("provider_calls")
    if stage not in STAGES:
        errors.append(f"{tag}: stage must be one of {STAGES}")
    if not isinstance(calls, int) or isinstance(calls, bool) or calls < 0:
        errors.append(f"{tag}: provider_calls must be a non-negative integer")
    records = sorted(p for p in (root / exp).rglob("*.md") if RECORD_FILE.search(p.name))
    results = [p for p in records if not p.name.endswith("PROTOCOL.md")]
    if stage == "PLANNING" and (results or calls or decl.get("run_receipts")):
        errors.append(f"{tag}: PLANNING may not carry results/decisions, provider calls or receipts")
    relation = decl.get("relation")
    if relation == "SEPARATE_MECHANISM":
        if not decl.get("hypothesis") or decl.get("not_a_test_of") != pin.get("id"):
            errors.append(f"{tag}: SEPARATE_MECHANISM needs a hypothesis and not_a_test_of = {pin.get('id')}")
        errors += [f"{p.relative_to(root)} must state SEPARATE_MECHANISM; it is not a test of {pin.get('id')}"
                   for p in records if "SEPARATE_MECHANISM" not in _read(p)]
        return errors
    if relation != "CONTINUES_ACTIVE_LINEAGE":
        return errors + [f"{tag}: relation must be CONTINUES_ACTIVE_LINEAGE or SEPARATE_MECHANISM"]

    chain = {s["step"]: s for s in pin["intended_chain"]}
    delta = pin["next_single_delta_step"]
    ref, parent = pin["parent_ref"], decl.get("parent_ref") if isinstance(decl.get("parent_ref"), dict) else {}
    if decl.get("lineage_id") != pin["id"]:
        errors.append(f"{tag}: lineage_id must be the pinned {pin['id']}")
    if parent.get("pr") != ref["pr"] or str(parent.get("head", ""))[:7] != str(ref["head"])[:7]:
        errors.append(f"{tag}: parent_ref must be PR #{ref['pr']} head {ref['head']} (the pinned implementation, not a prompt)")
    if decl.get("delta_step") != delta or not decl.get("single_delta"):
        errors.append(f"{tag}: the single delta must be the pinned next step '{delta}' with a single_delta description; "
                      "another delta needs an owner-reviewed pin change first")
    if sorted(decl.get("preserved_steps") or []) != sorted(set(chain) - {delta}):
        errors.append(f"{tag}: preserved_steps must list every other pinned step")

    invoked = decl.get("invoked") if isinstance(decl.get("invoked"), dict) else {}
    expected = "PLANNED" if stage == "PLANNING" else "INVOKED"
    exp_py = sorted((root / exp).rglob("*.py"))
    pinned = {e for s in chain.values() for e in s["entry_points"]}
    defs, imports = _index(exp_py + [root / p for p in sorted({e.split("::")[0] for e in pinned}) if (root / p).is_file()])
    errors += [f"{exp}: defines {n}() which shadows a pinned entry point; import the real code instead"
               for n in sorted({e.split("::")[1] for e in pinned})
               if any(path in exp_py for path, _ in defs.get(n, []))]
    seen: set[tuple[Path, str]] = set()
    if stage != "PLANNING":
        rpath, _, rfunc = str(decl.get("runner", "")).partition("::")
        if not rpath.startswith(exp + "/") or not any(p == root / rpath for p, _ in defs.get(rfunc, [])):
            errors.append(f"{tag}: runner {decl.get('runner')!r} is not a function defined in {exp}")
        else:
            seen = reachable(defs, imports, (root / rpath, rfunc))
    for step in pin["continuation_requires_invoked"] + [delta]:
        entry = invoked.get(step) if isinstance(invoked.get(step), dict) else {}
        status, point = entry.get("status"), str(entry.get("entry_point", ""))
        path, _, sym = point.partition("::")
        if status != expected:
            errors.append(f"{tag}: {step} must be {expected} at stage {stage}, declared {status!r}")
            continue
        if step == delta:
            if not path.startswith(exp + "/") or not sym:
                errors.append(f"{tag}: {step} is new code and must live in {exp}")
        elif point not in chain[step]["entry_points"]:
            errors.append(f"{tag}: {step} entry_point {point!r} is not a pinned real entry point "
                          f"{chain[step]['entry_points']}; a name or a mock is not an invocation")
            continue
        if stage == "PLANNING":
            continue
        if not any(p == root / path for p, _ in defs.get(sym, [])):
            errors.append(f"{tag}: {step} entry {point} is not defined in this checkout")
        elif (root / path, sym) not in seen:
            errors.append(f"{tag}: {step} entry {point} is not reachable from runner {decl.get('runner')}")

    if stage == "PLUMBING_ONLY":
        if calls or decl.get("run_receipts"):
            errors.append(f"{tag}: PLUMBING_ONLY must record 0 provider calls and no run receipts")
        errors += [f"{p.relative_to(root)} must state PLUMBING_ONLY (no Jev/reviewer execution shown)"
                   for p in results if "PLUMBING_ONLY" not in _read(p)]
    if stage == "RUN":
        roles = [chain[s]["receipt_role"] for s in pin["continuation_requires_invoked"] if chain[s].get("receipt_role")]
        roles.append(str(decl.get("delta_receipt_role") or "<undeclared delta_receipt_role>"))
        verdict, why = receipt_status(root, exp, decl, roles)
        claimed = decl.get("execution_verification")
        if not calls:
            errors.append(f"{tag}: RUN must record its provider_calls")
        if claimed not in ("RECEIPT_CONSISTENT", "UNVERIFIED"):
            errors.append(f"{tag}: RUN needs execution_verification RECEIPT_CONSISTENT or UNVERIFIED")
        elif claimed == "RECEIPT_CONSISTENT" and verdict != claimed:
            errors.append(f"{tag}: claims RECEIPT_CONSISTENT Jev/reviewer execution but {why}")
        elif claimed == "UNVERIFIED":
            errors += [f"{p.relative_to(root)} must state EXECUTION_UNVERIFIED" for p in results
                       if "EXECUTION_UNVERIFIED" not in _read(p)]
    return errors


def check_experiments(root: Path, state: dict, extra: set[str] = frozenset()) -> list[str]:
    dirs = experiment_dirs(root, extra)
    pin = state.get("active_research_mechanism")
    if not dirs:
        return []
    if check_lineage_pin(state, {x.get("id") for x in state.get("established_components", []) if isinstance(x, dict)}):
        return [f"Experiment directories {dirs} cannot be checked without a valid lineage pin"]
    return [e for d in dirs if d not in pinned_dirs(pin) for e in check_mechanism(root, d, pin)]


def git_output(*args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True, timeout=5, check=False)
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN"


def changed_files_since(base: str, diff_filter: str = "ACMRT") -> list[str]:
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only",
                        f"--diff-filter={diff_filter}", base, "HEAD"],
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


def base_state(base: str) -> dict:
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{base}:PROJECT_STATE.json"],
                       capture_output=True, text=True, timeout=20, check=False)
    try:
        return json.loads(r.stdout) if r.returncode == 0 else {}
    except json.JSONDecodeError:
        return {}


def new_record_dirs(base: str) -> set[str]:
    """Directories of newly added experiment records outside prototype/experiments/viability."""
    return {str(Path(p).parent) for p in changed_files_since(base, "A")
            if RECORD_FILE.search(Path(p).name) and not p.startswith(tuple(t + "/" for t in EXPERIMENT_TOPS))}


def check_lineage_pivot(base: str, state: dict, dirs: list[str]) -> list[str]:
    """A PR may change the pinned lineage/priority OR experiment files, never both (no self-authorized pivot)."""
    old = base_state(base)
    moved = [k for k in ("active_research_mechanism", "research_priority") if old.get(k) != state.get(k)]
    touched = sorted({d for p in changed_files_since(base) for d in dirs if p.startswith(d + "/")})
    errors = []
    if moved and touched:
        errors.append(f"{moved} changed in the same PR as experiment directories {touched}: land the owner-reviewed "
                      "lineage change on main first, then start the experiment on a new branch")
    pin = state.get("active_research_mechanism") if isinstance(state.get("active_research_mechanism"), dict) else {}
    errors += [f"{p}: pinned implementation directories keep historical records only; put new protocol/results in a "
               "new declared experiment directory" for p in changed_files_since(base)
               if RECORD_FILE.search(Path(p).name) and any(p.startswith(d + "/") for d in pinned_dirs(pin))]
    return errors


def lineage_context(pin: dict) -> str:
    ref = pin["parent_ref"]
    chain = " -> ".join(f"{s['step']}[{s['state']}]" for s in pin["intended_chain"])
    missing = ", ".join(s["step"] for s in pin["intended_chain"] if s["state"].startswith("NOT_IMPLEMENTED"))
    return (
        f"ACTIVE RESEARCH LINEAGE {pin['id']} (pinned in PROJECT_STATE.json, fingerprint-checked): {chain}. "
        f"Code: PR #{ref['pr']} head {ref['head']} ({ref['branch']}), NOT on main. "
        f"NOT YET IMPLEMENTED: {missing}. NEXT SINGLE DELTA (not started, no paid run authorized): {pin['next_single_delta']}\n"
        f"SEPARATE MECHANISMS, NOT tests of this loop: {' '.join(pin['separate_hypotheses_not_equivalent'])}\n"
        "MECHANISM GATE: every prototype/, experiments/, viability/ dir needs MECHANISM.json (CONTINUES_ACTIVE_LINEAGE "
        "or SEPARATE_MECHANISM); continuation must reach the real pinned entry points from its runner; naming Jev is "
        "not invoking Jev; PLUMBING_ONLY is not a Jev review; RUN claims without step receipts stay UNVERIFIED.\n"
    )


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
        f"{lineage_context(state['active_research_mechanism'])}"
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
    parser.add_argument("mode", choices=("hook", "check", "template"))
    parser.add_argument("--diff-base", help="Base commit SHA for CI same-PR state-update policy")
    args = parser.parse_args()
    if args.mode == "template":
        print(json.dumps(MECHANISM_TEMPLATE, indent=2))
        return 0
    state, errors = read_and_check()
    extra: set[str] = set()
    if args.diff_base:
        try:
            errors += check_pr_state_update(args.diff_base)
            extra = new_record_dirs(args.diff_base)
            if state:
                errors += check_lineage_pivot(args.diff_base, state, experiment_dirs(ROOT, extra))
        except RuntimeError as e:
            errors.append(str(e))
    if state:
        errors += check_experiments(ROOT, state, extra)
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
        print("SOPHON_CONTEXT_GUARD_OK: charter v1.2 + project state + working agreement + native hooks "
              f"+ lineage pin + {len(set(experiment_dirs(ROOT, extra)) - pinned_dirs(state['active_research_mechanism']))} "
              "experiment mechanism declaration(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
