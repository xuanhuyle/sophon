import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prototype", HERE / "prototype.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class SkeletonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = p.read_json(HERE / "clauses.json")
        cls.fixture = p.read_json(HERE / "mock_evidence.json")

    def test_runs_five_clauses_with_honest_mode(self):
        r = p.run(self.corpus, mode="demo", fixture=self.fixture)
        self.assertEqual(len(r["results"]), 5)
        self.assertEqual(r["mode"], "OFFLINE_HAND_AUTHORED_STUBS")
        self.assertTrue(all(not x["suggested_transposition"]["approval"] == "AUTHORIZED" for x in r["results"]))

    def test_missed_deadline_and_exception_hold(self):
        rows = {r["clause_id"]: r for r in p.run(self.corpus, mode="demo", fixture=self.fixture)["results"]}
        self.assertEqual(rows["C3"]["disposition"], "HOLD_UNRESOLVED")
        self.assertIn("JEV_MODIFIER_OMISSION: DEADLINE", rows["C3"]["reasons"])
        self.assertEqual(rows["C4"]["disposition"], "HOLD_UNRESOLVED")
        self.assertIn("JEV_MODIFIER_OMISSION: EXCLUSION", rows["C4"]["reasons"])
        self.assertIn("MISSING_DOCUMENT_OR_REFERENCE: Schedule A", rows["C4"]["reasons"])

    def test_routes_depend_on_modifiers(self):
        rows = {r["clause_id"]: r for r in p.run(self.corpus, mode="demo", fixture=self.fixture)["results"]}
        self.assertEqual(rows["C2"]["suggested_transposition"]["route"], "SHARED_SEMANTIC_DEFINITION_WITH_EXCLUSIONS")
        self.assertEqual(rows["C5"]["suggested_transposition"]["route"], "THRESHOLD_APPROVAL_GATE")
        # C3 Jev omitted the deadline; it must not be routed as a fully verified deadline workflow.
        self.assertEqual(rows["C3"]["suggested_transposition"]["route"], "CONDITIONAL_ENTITLEMENT_OR_REMEDY_WORKFLOW")
        self.assertEqual(rows["C3"]["disposition"], "HOLD_UNRESOLVED")

    def test_hallucinated_evidence_is_rejected(self):
        bad = copy.deepcopy(self.fixture)
        bad["reviewers"]["C3"]["adversarial"]["evidence_quotes"] = ["THIS IS NOT IN THE CONTRACT"]
        with self.assertRaises(ValueError):
            p.run(self.corpus, mode="demo", fixture=bad)

    def test_review_cannot_claim_supported_with_known_gaps(self):
        review = {"verdict": "SUPPORTED", "missing_modifiers": ["DEADLINE"],
                  "evidence_quotes": ["within 30 days"], "issues": [], "missing_source_refs": []}
        with self.assertRaises(ValueError):
            p.check_review(review, self.corpus["clauses"][2]["text"])

    def test_fake_primary_score_above_one_is_rejected(self):
        bad = copy.deepcopy(self.fixture["jev"]["C1"])
        bad["probabilities"]["OBLIGATION"] = 1.1
        with self.assertRaises(ValueError):
            p.validate_jev_proposal(bad)

    def test_inconsistent_primary_choice_is_rejected(self):
        bad = copy.deepcopy(self.fixture["jev"]["C1"])
        bad["primary"] = "OTHER"
        with self.assertRaises(ValueError):
            p.validate_jev_proposal(bad)

    def test_missing_question_is_rejected(self):
        bad = copy.deepcopy(self.fixture["jev"]["C1"])
        bad["modifiers"].pop("CONDITION")
        with self.assertRaises(ValueError):
            p.validate_jev_proposal(bad)

    def test_modified_corpus_invalidates_evidence_quotes(self):
        bad = copy.deepcopy(self.corpus)
        bad["clauses"][2]["text"] = "Customer may claim a credit."  # incompatible with fixture
        with self.assertRaises(ValueError):
            p.run(bad, mode="demo", fixture=self.fixture)

    def test_fresh_prompts_not_conflated(self):
        pred = p.validate_jev_proposal(self.fixture["jev"]["C1"])
        adv = p.reviewer_prompt("adversarial", self.corpus["clauses"][0]["text"], pred)
        back = p.reviewer_prompt("backward", self.corpus["clauses"][0]["text"], pred)
        self.assertIn("Assume the classifier is WRONG", adv)
        self.assertIn("assume the classifier is RIGHT", back)
        self.assertNotEqual(adv, back)
        self.assertNotIn("C4", adv)

    def test_no_external_calls_in_demo(self):
        with patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("remote network used")):
            with patch.object(p.subprocess, "run", side_effect=AssertionError("Claude spawned")):
                self.assertEqual(len(p.run(self.corpus, mode="demo", fixture=self.fixture)["results"]), 5)

    def test_live_never_silently_falls_back_to_mock(self):
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}):
            with self.assertRaises(RuntimeError):
                p.jev_live("The Supplier shall deliver a report.", model="jev-latest")

    def test_choice_and_noul_payload_shape(self):
        q = p.jev_questions()
        self.assertEqual(q["primary"]["type"], "choice")
        self.assertEqual(q["EXCLUSION"]["type"], "noul")
        self.assertEqual(set(q), {"primary", *p.MODIFIERS})

    def test_backwards_review_does_not_authorize(self):
        rows = p.run(self.corpus, mode="demo", fixture=self.fixture)["results"]
        c1 = rows[0]
        self.assertEqual(c1["disposition"], "CANDIDATE_FOR_HUMAN_REVIEW")
        self.assertEqual(c1["suggested_transposition"]["approval"], "NOT_AUTHORIZED")

    def test_schema_fails_for_missing_clause(self):
        with self.assertRaises(ValueError):
            p.check_clause_file({"corpus_id": "X", "clauses": self.corpus["clauses"][:-1]})


if __name__ == "__main__":
    unittest.main()
