"""Regression checks for native project state and guard, with no network or model calls."""
from __future__ import annotations

import json
import shutil
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
        for name in ("PROJECT_STATE.json", "SOPHON_CHARTER.md", "CLAUDE.md", "AGENTS.md",
                     ".claude/settings.json"):
            dest = r / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        self.addCleanup(temp.cleanup)
        return r

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
                      "V4", "NOT an LLM accuracy contest"):
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


if __name__ == "__main__":
    unittest.main()
