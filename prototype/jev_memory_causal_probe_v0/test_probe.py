"""Offline regression tests only; fabricated model responses never establish accuracy."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe


class CausalMemoryProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = probe.build("jev-latest")

    def test_source_grounded_real_contract_cases(self):
        self.assertEqual(len(self.plan["pairs"]), 8)
        self.assertEqual(self.plan["frozen_positive_probes_count"], 10)
        self.assertEqual(len(self.plan["source_linked_library"]), 3)
        self.assertEqual({x["case"]["document_id"] for x in self.plan["pairs"]},
                         {"GCS-SLA-20210624"})
        self.assertEqual({x["source_id"] for x in self.plan["source_linked_library"]},
                         {"GH-SLA-2021"})
        for row in self.plan["pairs"]:
            for target in row["case"]["probes"]:
                self.assertIn(target["verbatim_quote"], row["case"]["clause"])

    def test_same_model_and_questions_memory_only_delta(self):
        for row in self.plan["pairs"]:
            cold, learned = row["requests"]["COLD"], row["requests"]["LEARNED"]
            probe.validate_pair(cold, learned)
            self.assertEqual(cold["questions"], learned["questions"])
            self.assertEqual(cold["model"], learned["model"])
            self.assertEqual(set(cold["questions"]), set(probe.FUNCTIONS) | set(probe.MODIFIERS))
            self.assertTrue(all(q["type"] == "noul" for q in cold["questions"].values()))
            self.assertNotIn("source_references", cold["questions"])

    def test_cold_has_no_learned_prior_patterns(self):
        for row in self.plan["pairs"]:
            self.assertEqual(row["requests"]["COLD"]["state"]["prior_provision_skeletons"], [])
            self.assertEqual(
                row["requests"]["LEARNED"]["state"]["prior_provision_skeletons"],
                self.plan["source_linked_library"])

    def test_unanchored_target_or_unsupported_label_rejected(self):
        with patch.object(probe, "CASES",
                          (("fake", "B1", '"Error Rate" means', "\n\n",
                            (("OBLIGATION", "Customer must sign a secret agreement"),)),)):
            with self.assertRaisesRegex(ValueError, "unsupported pre-registered anchor"):
                probe.cases_and_memory()
        with patch.object(probe, "CASES",
                          (("fake", "B1", '"Error Rate" means', "\n\n",
                            (("NEXT_SECTION_PREDICTION", '"Error Rate" means'),)),)):
            with self.assertRaisesRegex(ValueError, "unknown function"):
                probe.cases_and_memory()

    def test_reject_drifts_in_target_or_question(self):
        sample = self.plan["pairs"][0]
        cold = json.loads(json.dumps(sample["requests"]["COLD"]))
        warm = json.loads(json.dumps(sample["requests"]["LEARNED"]))
        warm["questions"]["DEFINITION"]["instructions"] = "No longer identical"
        with self.assertRaisesRegex(ValueError, "drift"):
            probe.validate_pair(cold, warm)
        warm = json.loads(json.dumps(sample["requests"]["LEARNED"]))
        warm["state"]["clause"] += " extra clause"
        with self.assertRaisesRegex(ValueError, "drift"):
            probe.validate_pair(cold, warm)

    def test_score_rejects_invalid_and_lab_only_recordings(self):
        bad = {"plan_sha256": probe.digest(self.plan), "records": []}
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            probe.score(self.plan, bad)
        bad["records"] = []
        for row in self.plan["pairs"]:
            for arm in probe.ARMS:
                bad["records"].append({"case_id": row["case"]["id"], "arm": arm,
                    "provenance": "LAB_FIXTURE", "request_sha256": row["request_hashes"][arm],
                    "raw_response": {"model": "jev-1.13.0",
                        "answers": {n: {"type": "noul", "noul": 1.0} for n in probe.questions()}}})
        with self.assertRaisesRegex(ValueError, "no actual provider output"):
            probe.score(self.plan, bad)

    def test_score_rejects_model_version_change(self):
        mock = {"plan_sha256": probe.digest(self.plan), "records": []}
        for pair in self.plan["pairs"]:
            for arm in probe.ARMS:
                mock["records"].append({"case_id": pair["case"]["id"], "arm": arm,
                    "provenance": "ACTUAL_PROVIDER", "request_sha256": pair["request_hashes"][arm],
                    "raw_response": {"model": "jev-1.13.0" if arm == "COLD" else "jev-1.14.0",
                        "answers": {n: {"type": "noul", "noul": 0.8} for n in probe.questions()}}})
        with self.assertRaisesRegex(ValueError, "Model version changed"):
            probe.score(self.plan, mock)

    def test_default_cli_offline_and_paid_guard(self):
        with patch.object(sys, "argv", ["probe.py", "preflight"]), \
             patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}, clear=False):
            self.assertEqual(probe.main(), 0)
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(sys, "argv", ["probe.py", "live",
               "--output", str(probe.HERE / "live_runs" / "would_never_be_created.json")]), \
             patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}, clear=False), \
             patch.object(probe, "call_jev", side_effect=AssertionError("network touched")):
            with self.assertRaises(SystemExit):
                probe.main()

if __name__ == "__main__":
    unittest.main()
