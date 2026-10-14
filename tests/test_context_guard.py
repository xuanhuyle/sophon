"""Regression checks for native project state and guard, with no network or model calls."""
from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
import context_guard as cg


class NativeContextGuard(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        r = Path(temp.name)
        (r / ".claude").mkdir()
        for name in ("PROJECT_STATE.json", "SOPHON_CHARTER.md", "ENGINEERING_WORKFLOW.md",
                     "CLAUDE.md", "AGENTS.md", ".claude/settings.json"):
            dest = r / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        state = json.loads((r / "PROJECT_STATE.json").read_text(encoding="utf-8"))
        for x in state["established_components"]:
            if x["location"] != "OTHER_PR":
                for rel in cg.component_paths(x["path"]):
                    (r / rel).parent.mkdir(parents=True, exist_ok=True)
                    (r / rel).touch()
        self.addCleanup(temp.cleanup)
        return r

    def edit_state(self, r, change):
        p = r / "PROJECT_STATE.json"
        j = json.loads(p.read_text(encoding="utf-8"))
        change(j)
        p.write_text(json.dumps(j), encoding="utf-8")
        _, errors = cg.read_and_check(r)
        return errors

    def run_settings_hook(self, r):
        """Run the exact command committed in .claude/settings.json against a fixture repo."""
        hook_dir = r / ".claude" / "hooks"
        hook_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / ".claude/hooks/context_guard.py", hook_dir / "context_guard.py")
        conf = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        command = conf["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        argv = shlex.split(command.replace("${CLAUDE_PROJECT_DIR}", str(r)))
        self.assertEqual(argv[0], "python")
        argv[0] = sys.executable  # interpreter name resolution is host-specific; see docs
        return subprocess.run(argv, capture_output=True, text=True, timeout=30, check=False)

    def test_repo_configuration_is_valid(self):
        _, errors = cg.read_and_check(ROOT)
        self.assertEqual(errors, [])

    def test_charter_mismatch_detected(self):
        r = self.fixture()
        p = r / "SOPHON_CHARTER.md"
        p.write_text(p.read_text(encoding="utf-8").replace("**Version:** 1.2", "**Version:** 1.1"), encoding="utf-8")
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("not v1.2" in e for e in errors))

    def test_existing_component_cannot_silently_disappear(self):
        r = self.fixture()
        p = r / "PROJECT_STATE.json"
        j = json.loads(p.read_text(encoding="utf-8"))
        j["established_components"] = [
            x for x in j["established_components"] if x["id"] != "backward_source_review"
        ]
        p.write_text(json.dumps(j), encoding="utf-8")
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("implementation inventory" in e for e in errors))

    def test_v3_primary_cannot_be_rewritten_as_success(self):
        r = self.fixture()
        p = r / "PROJECT_STATE.json"
        j = json.loads(p.read_text(encoding="utf-8"))
        next(x for x in j["evidence"] if x["id"] == "V3_structure_primary")["status"] = "PASS"
        p.write_text(json.dumps(j), encoding="utf-8")
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("frozen primary" in e for e in errors))


    def test_missing_engineering_workflow_is_detected(self):
        r = self.fixture()
        (r / "ENGINEERING_WORKFLOW.md").unlink()
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("ENGINEERING_WORKFLOW.md missing" in e for e in errors))

    def test_workflow_state_binding_cannot_disappear(self):
        r = self.fixture()
        p = r / "PROJECT_STATE.json"
        j = json.loads(p.read_text(encoding="utf-8"))
        del j["engineering_workflow"]
        p.write_text(json.dumps(j), encoding="utf-8")
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("modus operandi" in e for e in errors))

    def test_entry_instruction_must_link_to_workflow(self):
        r = self.fixture()
        p = r / "AGENTS.md"
        p.write_text(p.read_text(encoding="utf-8").replace("ENGINEERING_WORKFLOW.md", "SOMETHING_ELSE.md"),
                     encoding="utf-8")
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("AGENTS.md must link to ENGINEERING_WORKFLOW.md" in e for e in errors))

    def test_workflow_change_requires_state_update(self):
        with patch.object(cg, "changed_files_since", return_value=["ENGINEERING_WORKFLOW.md"]):
            self.assertTrue(cg.check_pr_state_update("abc"))
        with patch.object(cg, "changed_files_since",
                          return_value=["ENGINEERING_WORKFLOW.md", "PROJECT_STATE.json"]):
            self.assertFalse(cg.check_pr_state_update("abc"))

    def test_native_hook_is_mandatory(self):
        r = self.fixture()
        p = r / ".claude" / "settings.json"
        j = json.loads(p.read_text(encoding="utf-8"))
        del j["hooks"]["UserPromptSubmit"]
        p.write_text(json.dumps(j), encoding="utf-8")
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("hooks missing" in e for e in errors))

    def test_context_mentions_existing_reviewers_and_hold(self):
        state, errors = cg.read_and_check(ROOT)
        self.assertEqual(errors, [])
        with patch.object(cg, "git_output", return_value="test"):
            result = cg.context(state)
        for token in ("adversarial_review", "backward_source_review", "provision_library",
                      "deterministic_reconciliation", "V3_structure_primary=INCONCLUSIVE",
                      "V4", "NOT an LLM accuracy contest", "Human defines PROBLEM",
                      "ENGINEERING_WORKFLOW.md", "ONE bounded", "KEEP / REVISE / STOP"):
            self.assertIn(token, result)

    def test_ci_result_change_requires_state_update(self):
        with patch.object(cg, "changed_files_since",
                          return_value=["prototype/foo/RESULTS.md"]):
            self.assertTrue(cg.check_pr_state_update("abc"))
        with patch.object(cg, "changed_files_since",
                          return_value=["prototype/foo/RESULTS.md", "PROJECT_STATE.json"]):
            self.assertFalse(cg.check_pr_state_update("abc"))

    def test_ci_regular_code_change_does_not_require_state_update(self):
        with patch.object(cg, "changed_files_since",
                          return_value=["prototype/foo/source.py", "tests/test_foo.py"]):
            self.assertFalse(cg.check_pr_state_update("abc"))

    def test_earlier_work_cannot_silently_disappear(self):
        # The 2026-10-13 state omitted PRs #2, #3, #4-#11 and #12; each is now required.
        for cid in ("normative_layer_v0", "native_bi_validation_harness",
                    "public_data_alignment_reviewer", "governance_integrity_kernel"):
            errors = self.edit_state(self.fixture(), lambda j: j.update(established_components=[
                x for x in j["established_components"] if x["id"] != cid]))
            self.assertTrue(any("implementation inventory" in e for e in errors), cid)

    def test_component_needs_location_and_limits(self):
        def drop(j):
            del j["established_components"][0]["location"]
            del j["established_components"][1]["does_not_prove"]
        errors = self.edit_state(self.fixture(), drop)
        self.assertTrue(any("absent location" in e for e in errors))
        self.assertTrue(any("does_not_prove" in e for e in errors))

    def test_draft_pr_code_is_not_presented_as_local(self):
        r = self.fixture()
        errors = self.edit_state(r, lambda j: next(
            x for x in j["established_components"] if x["id"] == "normative_layer_v0"
        ).update(location="THIS_BRANCH"))
        self.assertTrue(any("normative_layer_v0 claims THIS_BRANCH" in e for e in errors))

    def test_merged_code_forces_location_update(self):
        r = self.fixture()
        (r / "prototype/normative_layer").mkdir(parents=True)
        (r / "prototype/normative_layer/sophon_v0.py").touch()
        _, errors = cg.read_and_check(r)
        self.assertTrue(any("claims OTHER_PR" in e for e in errors))

    def test_referenced_pr_must_be_in_pr_graph(self):
        errors = self.edit_state(self.fixture(), lambda j: j["pr_graph"].update(
            prs=[x for x in j["pr_graph"]["prs"] if x["pr"] != 3]))
        self.assertTrue(any("absent from pr_graph: [3]" in e for e in errors))

    def test_settings_hook_injects_context(self):
        result = self.run_settings_hook(self.fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SOPHON NATIVE PROJECT CONTEXT", result.stdout)
        self.assertIn("OTHER_PR = unmerged branch, NOT in this checkout", result.stdout)
        self.assertIn("RESEARCH PRIORITY", result.stdout)

    def test_hook_failure_reaches_agent_without_blocking_prompts(self):
        r = self.fixture()
        self.edit_state(r, lambda j: j.update(pr_graph={}))
        result = self.run_settings_hook(r)
        self.assertEqual(result.returncode, 0)
        self.assertIn("SOPHON_CONTEXT_GUARD_FAILED", result.stdout)
        self.assertIn("pr_graph missing", result.stdout)
        check = subprocess.run([sys.executable, str(r / ".claude/hooks/context_guard.py"), "check"],
                               capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(check.returncode, 1)

    def test_experiment_decision_change_requires_state_update(self):
        with patch.object(cg, "changed_files_since",
                          return_value=["experiments/E6_reverse/DECISION.md"]):
            self.assertTrue(cg.check_pr_state_update("abc"))


V1 = "prototype/jev_clause_router_v0/prototype.py"
V2 = "prototype/jev_library_transfer_v2/transfer.py"
# Minimal stand-ins for the PR #17 b9d698c call path (same symbol names), so tests stay offline.
PINNED_STUBS = {
    V1: "def call_jev(c):\n    return c\n\ndef jev_live(c):\n    return call_jev(c)\n\n"
        "def reviewer_prompt(role, t):\n    return role\n\ndef verdict_for(*a):\n    return a\n",
    V2: "def call_jev_v2(r):\n    return r\n\ndef reviewer_prompt_v2(role, p):\n    return role\n\n"
        "def reconcile(j, r):\n    return j\n\ndef induce_library(x):\n    return x\n\n"
        # Real transfer.py also has main() -> run_live -> call_jev_v2; an experiment's own main()
        # must not inherit that path by name (bug found running the gate on the real PR #18 code).
        "def run_live(p):\n    return reconcile(call_jev_v2(p), reviewer_prompt_v2('adversarial', p))\n\n"
        "def main():\n    return run_live(None)\n",
}
# Shape of PR #18 v4_sequential.py: regex textual features + conditional counts, no Jev/reviewer path.
V4_RUNNER = '''import re
from collections import Counter
FEATURES = {"EXCEPTION": re.compile(r"(?i)\\b(except|unless|notwithstanding)\\b"),
            "QUANT_THRESHOLD": re.compile(r"\\b\\d+(?:\\.\\d+)?\\s?%")}

def learn(lib, text):
    lib.update(f for f, rx in FEATURES.items() if rx.search(text))

def predict_arm(lib, n):
    return {f: (lib[f] + 1) / (n + 2) for f in FEATURES}

def main(docs):
    lib = Counter()
    for i, d in enumerate(docs):
        predict_arm(lib, i)
        learn(lib, d)
'''
DELTA_RUNNER = '''import transfer
from library_reviewer import library_review

def main(packets):
    for pk in packets:
        j = transfer.call_jev_v2(pk)
        reviews = {r: transfer.reviewer_prompt_v2(r, pk) for r in ("adversarial", "backward")}
        reviews["library"] = library_review(pk, j)
        transfer.reconcile(j, reviews)
'''
EXP = "prototype/jev_library_reviewer_v5"


def continuation(stage="PLANNING", **over):
    status = "PLANNED" if stage == "PLANNING" else "INVOKED"
    decl = {
        "relation": "CONTINUES_ACTIVE_LINEAGE",
        "lineage_id": "jev_source_grounded_provision_skeleton_loop",
        "parent_ref": {"pr": 17, "branch": "experiment/jev-v3-context-funnel-2026-10-13", "head": "b9d698c"},
        "delta_step": "independent_library_based_review",
        "single_delta": "Separate library-skeleton reviewer of each Jev proposal inside the V2 pipeline",
        "preserved_steps": ["jev_classification", "adversarial_challenge", "backward_source_challenge",
                            "evidence_anchored_skeleton_induction", "deterministic_reconciliation",
                            "retain_revise_transfer_to_later_contracts"],
        "runner": f"{EXP}/run.py::main",
        "invoked": {
            "jev_classification": {"status": status, "entry_point": f"{V2}::call_jev_v2"},
            "adversarial_challenge": {"status": status, "entry_point": f"{V2}::reviewer_prompt_v2"},
            "backward_source_challenge": {"status": status, "entry_point": f"{V2}::reviewer_prompt_v2"},
            "deterministic_reconciliation": {"status": status, "entry_point": f"{V2}::reconcile"},
            "independent_library_based_review": {"status": status,
                                                 "entry_point": f"{EXP}/library_reviewer.py::library_review"},
        },
        "stage": stage,
        "provider_calls": 0,
        "delta_receipt_role": "library",
        "claims": "Whether a separate library reviewer raises grounded challenges to Jev proposals",
        "cannot_prove": "Semantic correctness; reviewer agreement is triage, not truth",
    }
    decl.update(over)
    return decl


class MechanismContinuityGate(unittest.TestCase):
    fixture = NativeContextGuard.fixture
    edit_state = NativeContextGuard.edit_state

    def repo(self, pinned_code=True):
        r = self.fixture()
        if pinned_code:
            for rel, text in PINNED_STUBS.items():
                (r / rel).parent.mkdir(parents=True, exist_ok=True)
                (r / rel).write_text(text, encoding="utf-8")
            # A branch that imports the PR #17 code must say so in its inventory (existing guard rule).
            self.edit_state(r, lambda j: [x.update(location="THIS_BRANCH") for x in j["established_components"]
                                          if x["path"] in PINNED_STUBS])
        return r

    def experiment(self, r, decl, files, exp=EXP):
        d = r / exp
        d.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (d / name).parent.mkdir(parents=True, exist_ok=True)
            (d / name).write_text(text, encoding="utf-8")
        if decl is not None:
            (d / "MECHANISM.json").write_text(json.dumps(decl), encoding="utf-8")
        state, errors = cg.read_and_check(r)
        self.assertEqual(errors, [])
        return cg.check_experiments(r, state)

    def delta_files(self, **extra):
        return {"run.py": DELTA_RUNNER,
                "library_reviewer.py": "def library_review(packet, jev):\n    return {}\n", **extra}

    # --- lineage pin ---------------------------------------------------------------------------
    def test_lineage_pin_missing_fails(self):
        errors = self.edit_state(self.fixture(), lambda j: j.pop("active_research_mechanism"))
        self.assertTrue(any("lineage pin missing" in e for e in errors))

    def test_lineage_pin_tampering_fails(self):
        def mark_reviewer_done(j):
            next(s for s in j["active_research_mechanism"]["intended_chain"]
                 if s["step"] == "independent_library_based_review")["state"] = "IMPLEMENTED_RUN"
        def drop_backward(j):
            j["active_research_mechanism"]["intended_chain"] = [
                s for s in j["active_research_mechanism"]["intended_chain"] if s["step"] != "backward_source_challenge"]
        def regex_as_jev(j):
            j["active_research_mechanism"]["intended_chain"][0]["entry_points"] = [
                "prototype/contract_sequential_learning_v4/v4_sequential.py::predict_arm"]
        for change in (mark_reviewer_done, drop_backward, regex_as_jev,
                       lambda j: j["active_research_mechanism"].update(parent_ref="PR #18"),
                       lambda j: j["active_research_mechanism"].update(id="cumulative_regex_learning")):
            errors = self.edit_state(self.fixture(), change)
            self.assertTrue(any("active_research_mechanism changed" in e for e in errors), errors)

    def test_context_shows_exact_lineage_and_missing_reviewer(self):
        state, errors = cg.read_and_check(ROOT)
        self.assertEqual(errors, [])
        with patch.object(cg, "git_output", return_value="test"):
            text = cg.context(state)
        self.assertIn("jev_classification[IMPLEMENTED_RUN] -> adversarial_challenge[IMPLEMENTED_RUN] -> "
                      "backward_source_challenge[IMPLEMENTED_RUN] -> independent_library_based_review"
                      "[NOT_IMPLEMENTED_AS_SEPARATE_REVIEWER] -> evidence_anchored_skeleton_induction", text)
        self.assertIn("deterministic_reconciliation[IMPLEMENTED_RUN]", text)
        self.assertIn("NOT YET IMPLEMENTED: independent_library_based_review", text)
        self.assertIn("PR #17 head b9d698c", text)
        self.assertIn("NOT on main", text)
        self.assertIn("SEPARATE MECHANISMS, NOT tests of this loop", text)
        self.assertIn("V4 predicts regex textual proxies", text)

    def test_checkout_without_state_fails_clearly(self):
        r = self.fixture()
        (r / "PROJECT_STATE.json").unlink()
        state, errors = cg.read_and_check(r)
        self.assertIsNone(state)
        self.assertTrue(any("PROJECT_STATE.json missing" in e for e in errors))

    # --- mandatory acceptance: V4-shaped false continuity --------------------------------------
    def test_v4_regex_experiment_claiming_jev_loop_is_rejected(self):
        false_claim = continuation(
            "RUN", runner=f"{EXP}/v4_sequential.py::main", provider_calls=40,
            execution_verification="RECEIPT_CONSISTENT")
        false_claim["invoked"]["independent_library_based_review"]["entry_point"] = f"{EXP}/v4_sequential.py::learn"
        files = {"v4_sequential.py": V4_RUNNER,
                 "RESULTS.md": "Cumulative Jev learning: Jev + adversarial/backward + provision library improved.\n"}
        for pinned_code in (False, True):  # main-like checkout, and a branch carrying the PR #17 code
            errors = self.experiment(self.repo(pinned_code), false_claim, files)
            self.assertTrue(errors)
            self.assertTrue(any("jev_classification entry" in e for e in errors), errors)
            self.assertTrue(any("claims RECEIPT_CONSISTENT" in e for e in errors), errors)
            if pinned_code:
                self.assertTrue(any("is not reachable from runner" in e for e in errors), errors)

    def test_v4_regex_experiment_mislabel_variants_are_rejected(self):
        files = {"v4_sequential.py": V4_RUNNER, "RESULTS.md": "STOP\n"}
        cases = {
            "no declaration": (None, "MECHANISM.json missing"),
            "planning with results": (continuation(), "PLANNING may not carry results"),
            "fake entry point": (continuation("RUN", runner=f"{EXP}/v4_sequential.py::main", invoked={
                **continuation("RUN")["invoked"],
                "jev_classification": {"status": "INVOKED", "entry_point": f"{EXP}/v4_sequential.py::predict_arm"}}),
                "not a pinned real entry point"),
            "plumbing label hiding a regex runner": (continuation("PLUMBING_ONLY", runner=f"{EXP}/v4_sequential.py::main"),
                                                      "not reachable from runner"),
        }
        for label, (decl, needle) in cases.items():
            errors = self.experiment(self.repo(), decl, files)
            self.assertTrue(any(needle in e for e in errors), (label, errors))

    def test_ci_check_fails_closed_on_v4_false_continuity(self):
        r = self.repo()
        self.experiment(r, continuation("RUN", runner=f"{EXP}/v4_sequential.py::main", provider_calls=40,
                                        execution_verification="RECEIPT_CONSISTENT"),
                        {"v4_sequential.py": V4_RUNNER, "RESULTS.md": "Jev loop gain\n"})
        hook_dir = r / ".claude" / "hooks"
        hook_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / ".claude/hooks/context_guard.py", hook_dir / "context_guard.py")
        result = subprocess.run([sys.executable, str(hook_dir / "context_guard.py"), "check"],
                                capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not reachable from runner", result.stderr)

    # --- separate hypotheses ----------------------------------------------------------------------
    def test_separate_structural_experiment_is_not_the_jev_loop(self):
        separate = {"relation": "SEPARATE_MECHANISM", "hypothesis": "Regex/heading statistics predict masked provisions",
                    "not_a_test_of": "jev_source_grounded_provision_skeleton_loop", "stage": "RUN",
                    "provider_calls": 0, "claims": "Only the regex proxy", "cannot_prove": "Anything about Jev review"}
        honest = {"v4_sequential.py": V4_RUNNER,
                  "RESULTS.md": "SEPARATE_MECHANISM: regex proxy; STOP_NO_OBSERVED_CUMULATIVE_GAIN.\n"}
        self.assertEqual(self.experiment(self.repo(), separate, honest), [])
        errors = self.experiment(self.repo(), separate, {**honest, "RESULTS.md": "Cumulative learning STOP\n"})
        self.assertTrue(any("must state SEPARATE_MECHANISM" in e for e in errors), errors)
        errors = self.experiment(self.repo(), {**separate, "not_a_test_of": None}, honest)
        self.assertTrue(any("not_a_test_of" in e for e in errors), errors)

    # --- legitimate continuation stages --------------------------------------------------------------
    def test_single_delta_planning_passes_without_provider_claims(self):
        for pinned_code in (False, True):
            self.assertEqual(self.experiment(self.repo(pinned_code), continuation(),
                                             {"PROTOCOL.md": "Planned increment.\n"}), [])
        bad = [
            (continuation(provider_calls=3), "PLANNING may not carry"),
            (continuation(delta_step="evidence_anchored_skeleton_induction"), "single delta must be"),
            (continuation(parent_ref={"pr": 18, "head": "30f5b6d"}), "parent_ref must be PR #17"),
            (continuation(invoked={**continuation()["invoked"],
                                   "jev_classification": {"status": "INVOKED", "entry_point": f"{V2}::call_jev_v2"}}),
             "must be PLANNED at stage PLANNING"),
        ]
        for decl, needle in bad:
            errors = self.experiment(self.repo(), decl, {"PROTOCOL.md": "x\n"})
            self.assertTrue(any(needle in e for e in errors), (needle, errors))

    def test_plumbing_only_is_allowed_only_when_labelled(self):
        ok = self.delta_files(**{"RESULTS.md": "PLUMBING_ONLY: wiring test, no Jev/reviewer execution.\n"})
        self.assertEqual(self.experiment(self.repo(), continuation("PLUMBING_ONLY"), ok), [])
        errors = self.experiment(self.repo(), continuation("PLUMBING_ONLY"),
                                 self.delta_files(**{"RESULTS.md": "Library reviewer works.\n"}))
        self.assertTrue(any("must state PLUMBING_ONLY" in e for e in errors), errors)
        errors = self.experiment(self.repo(), continuation("PLUMBING_ONLY", provider_calls=9), ok)
        self.assertTrue(any("0 provider calls" in e for e in errors), errors)

    def test_mock_shadowing_a_pinned_entry_point_is_rejected(self):
        files = self.delta_files(**{"library_reviewer.py": "def library_review(p, j):\n    return {}\n\n"
                                                           "def call_jev_v2(r):\n    return {'mock': True}\n"})
        errors = self.experiment(self.repo(), continuation("PLUMBING_ONLY"), files)
        self.assertTrue(any("shadows a pinned entry point" in e for e in errors), errors)

    def test_run_claim_without_execution_receipts_is_not_verified(self):
        run = continuation("RUN", provider_calls=4, execution_verification="RECEIPT_CONSISTENT")
        claim = {"RESULTS.md": "Jev and reviewers ran.\n"}
        errors = self.experiment(self.repo(), run, self.delta_files(**claim))
        self.assertTrue(any("claims RECEIPT_CONSISTENT" in e and "no run_receipts" in e for e in errors), errors)
        hashes = '{"live.json": "abc"}'
        hash_only = {**run, "run_receipts": [{"path": f"{EXP}/receipts.json",
                                              "sha256": hashlib.sha256(hashes.encode()).hexdigest()}]}
        errors = self.experiment(self.repo(), hash_only, self.delta_files(**claim, **{"receipts.json": hashes}))
        self.assertTrue(any("no record with ACTUAL_PROVIDER" in e for e in errors), errors)
        unverified = {**run, "execution_verification": "UNVERIFIED"}
        errors = self.experiment(self.repo(), unverified, self.delta_files(**claim))
        self.assertTrue(any("must state EXECUTION_UNVERIFIED" in e for e in errors), errors)
        self.assertEqual(self.experiment(self.repo(), unverified, self.delta_files(
            **{"RESULTS.md": "EXECUTION_UNVERIFIED: owner-local run, receipts not committed.\n"})), [])

    def test_run_with_step_receipts_is_receipt_consistent_only(self):
        step = {"provenance": "ACTUAL_PROVIDER", "raw_response": {"x": 1}}
        record = json.dumps({"records": [{"steps": {k: step for k in ("jev", "adversarial", "backward", "library")}}]})
        run = continuation("RUN", provider_calls=4, execution_verification="RECEIPT_CONSISTENT",
                           run_receipts=[{"path": f"{EXP}/live.json",
                                          "sha256": hashlib.sha256(record.encode()).hexdigest()}])
        files = self.delta_files(**{"live.json": record, "RESULTS.md": "Reviewer ran.\n"})
        self.assertEqual(self.experiment(self.repo(), run, files), [])
        no_library = record.replace('"library"', '"other"')
        run["run_receipts"][0]["sha256"] = hashlib.sha256(no_library.encode()).hexdigest()
        errors = self.experiment(self.repo(), run, self.delta_files(**{"live.json": no_library, "RESULTS.md": "x\n"}))
        self.assertTrue(any("no record with ACTUAL_PROVIDER" in e and "library" in e for e in errors), errors)

    # --- PR-level pivot rules -------------------------------------------------------------------------
    def test_pr_cannot_change_lineage_and_experiments_together(self):
        state = json.loads((ROOT / "PROJECT_STATE.json").read_text(encoding="utf-8"))
        moved = json.loads(json.dumps(state))
        moved["active_research_mechanism"]["next_single_delta_step"] = "evidence_anchored_skeleton_induction"
        dirs = [EXP]
        with patch.object(cg, "base_state", return_value=state), \
                patch.object(cg, "changed_files_since", return_value=[f"{EXP}/run.py", "PROJECT_STATE.json"]):
            self.assertEqual(cg.check_lineage_pivot("abc", state, dirs), [])
            self.assertTrue(any("same PR as experiment" in e for e in cg.check_lineage_pivot("abc", moved, dirs)))
        with patch.object(cg, "base_state", return_value=state), \
                patch.object(cg, "changed_files_since", return_value=["PROJECT_STATE.json"]):
            self.assertEqual(cg.check_lineage_pivot("abc", moved, dirs), [])

    def test_new_results_cannot_hide_in_pinned_code_or_new_folders(self):
        state = json.loads((ROOT / "PROJECT_STATE.json").read_text(encoding="utf-8"))
        with patch.object(cg, "base_state", return_value=state), \
                patch.object(cg, "changed_files_since",
                             return_value=["prototype/jev_library_transfer_v2/V5_RESULTS.md"]):
            self.assertTrue(any("historical records only" in e for e in cg.check_lineage_pivot("abc", state, [])))
        with patch.object(cg, "changed_files_since", return_value=["research/v5/RESULTS.md", "docs/notes.md"]):
            self.assertEqual(cg.new_record_dirs("abc"), {"research/v5"})
        r = self.repo()
        (r / "research/v5").mkdir(parents=True)
        (r / "research/v5/RESULTS.md").write_text("Jev loop gain\n", encoding="utf-8")
        state, _ = cg.read_and_check(r)
        errors = cg.check_experiments(r, state, {"research/v5"})
        self.assertTrue(any("research/v5/MECHANISM.json missing" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
