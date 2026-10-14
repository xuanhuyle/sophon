"""Regression checks for native project state and guard, with no network or model calls."""
from __future__ import annotations

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


class ResearchAlignmentGuard(unittest.TestCase):
    """Regression: the old V4 regex proxy must not masquerade as library-assisted classification."""

    def state(self):
        return json.loads((ROOT / "PROJECT_STATE.json").read_text(encoding="utf-8"))

    def declaration(self, **changes):
        fields = {
            "relation": "DIRECT_GOAL_TEST",
            "goal_id": cg.ACTIVE_GOAL,
            "implementation_ref": "PR #17 b9d698c",
            "single_delta": "Use earlier source-anchored skeletons to challenge later classifications",
            "measured_target": cg.ACTIVE_TARGET,
            "library_comparison": cg.ACTIVE_COMPARISON,
            "stage": "PLANNED",
            "claim_limit": "NO_RESULT_YET",
        }
        fields.update(changes)
        return fields

    def test_classification_plus_cumulative_library_is_the_active_goal(self):
        state, errors = cg.read_and_check(ROOT)
        self.assertEqual(errors, [])
        with patch.object(cg, "git_output", return_value="feature"):
            context = cg.context(state)
        self.assertIn("NON-NEGOTIABLE RESEARCH TARGET", context)
        self.assertIn("reduce future classification errors", context)
        self.assertIn("regex/heading-only predictor DOES NOT test this goal", context)

    def test_v4_regex_proxy_cannot_claim_to_test_classification_learning(self):
        false_v4 = self.declaration(
            measured_target="REGEX_TEXT_FEATURE_BRIER",
            library_comparison="CUMULATIVE_COUNTS_VS_SEED")
        errors = cg.check_experiment_alignment(false_v4, self.state())
        self.assertTrue(any("CLASSIFICATION ERRORS" in e for e in errors), errors)
        self.assertTrue(any("frozen/cold" in e for e in errors), errors)

    def test_v4_separate_hypothesis_is_not_classification_evidence(self):
        separate = self.declaration(
            relation="SEPARATE_HYPOTHESIS",
            measured_target="REGEX_TEXT_FEATURE_BRIER",
            library_comparison="CUMULATIVE_COUNTS_VS_SEED",
            claim_limit="NOT_EVIDENCE_FOR_ACTIVE_GOAL")
        self.assertEqual(cg.check_experiment_alignment(separate, self.state()), [])

    def test_planned_one_delta_classification_library_comparison_is_allowed(self):
        self.assertEqual(cg.check_experiment_alignment(self.declaration(), self.state()), [])
        component = self.declaration(
            relation="COMPONENT_ONLY", measured_target="PROVISION_SKELETON_ANCHORING",
            claim_limit="COMPONENT_ONLY_NOT_END_TO_END")
        self.assertEqual(cg.check_experiment_alignment(component, self.state()), [])

    def test_missing_alignment_is_rejected_for_new_experiment_directory(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(cg, "changed_files_since",
                             return_value=["prototype/v5/predict.py", "prototype/v5/PROTOCOL.md"]), \
                patch.object(cg.subprocess, "run", return_value=type("Result", (), {"returncode": 1})()):
            root = Path(tmp)
            (root / "prototype/v5").mkdir(parents=True)
            errors = cg.check_pr_experiment_alignment("base", self.state(), root)
        self.assertTrue(any("must include valid EXPERIMENT_ALIGNMENT.json" in e for e in errors), errors)

    def test_new_experiment_with_false_claim_fails_before_run(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(cg, "changed_files_since",
                             return_value=["prototype/v5/PROTOCOL.md"]), \
                patch.object(cg.subprocess, "run", return_value=type("Result", (), {"returncode": 1})()):
            root = Path(tmp)
            folder = root / "prototype/v5"
            folder.mkdir(parents=True)
            false_v4 = self.declaration(measured_target="REGEX_TEXT_FEATURE_BRIER")
            (folder / "EXPERIMENT_ALIGNMENT.json").write_text(json.dumps(false_v4), encoding="utf-8")
            errors = cg.check_pr_experiment_alignment("base", self.state(), root)
        self.assertTrue(any("CLASSIFICATION ERRORS" in e for e in errors), errors)

    def test_goal_cannot_change_with_experiment_in_same_pr(self):
        before = self.state()
        after = json.loads(json.dumps(before))
        after["research_contract"]["learning_claim"] = "silently changed goal"
        with patch.object(cg, "changed_files_since",
                          return_value=["PROJECT_STATE.json", "prototype/v5/PROTOCOL.md"]), \
                patch.object(cg.subprocess, "run",
                             return_value=type("Result", (), {
                                 "returncode": 0, "stdout": json.dumps(before)})()):
            errors = cg.check_pr_goal_drift("base", after)
        self.assertTrue(any("SAME PR" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
