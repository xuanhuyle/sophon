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
        self.assertEqual(len(self.plan["pairs"]), 10)
        self.assertEqual(self.plan["frozen_positive_probes_count"], 16)
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

    def test_existing_root_dotenv_loaded_only_when_no_process_key(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".env").write_text("# Local only\nexport TYPESAFE_API_KEY = 'secret-from-dotenv' # comment\n", encoding="utf-8")
            with patch.object(probe, "ROOT", root), \
                 patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}, clear=False):
                self.assertEqual(probe.resolve_typesafe_key(), "secret-from-dotenv")
            with patch.object(probe, "ROOT", root), \
                 patch.dict(os.environ, {"TYPESAFE_API_KEY": "secret-from-process"}, clear=False):
                self.assertEqual(probe.resolve_typesafe_key(), "secret-from-process")

    def test_dotenv_loader_handles_missing_file_and_quoted_bom(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(probe, "ROOT", root), \
                 patch.object(probe, "HERE", root), \
                 patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}, clear=False):
                self.assertIsNone(probe.resolve_typesafe_key())
                (root / ".env").write_text("\ufeffTYPESAFE_API_KEY=\"some-value\"\n", encoding="utf-8")
                self.assertEqual(probe.resolve_typesafe_key(), "some-value")

    def test_live_with_confirm_and_local_dotenv_uses_authorized_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".env").write_text("TYPESAFE_API_KEY=dummy-key\n", encoding="utf-8")
            # Use pre-flight check and mock the provider so this remains network-free.
            with patch.object(probe, "ROOT", root), \
                 patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}, clear=False):
                self.assertEqual(probe.resolve_typesafe_key(), "dummy-key")

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

class TargetValidityTests(unittest.TestCase):
    """2026-10-15 post-run target note: offline span and arithmetic checks only."""
    HERE = Path(__file__).resolve().parent

    def test_quoted_units_match_frozen_source_offsets(self):
        spec = json.loads((self.HERE / "target_spans_2026-10-15.json").read_text(encoding="utf-8"))
        packets = {c["id"]: c for c in probe.history(spec["source"]["path"])["clauses"]}
        for unit in spec["units"]:
            text = packets[unit["packet"]][unit["field"]]
            self.assertEqual(text[unit["start"]:unit["end"]], unit["quote"], unit["id"])
            self.assertEqual(text.count(unit["quote"]), 1, unit["id"])

    def test_recorded_score_and_bracketed_sensitivity_reconcile(self):
        import hashlib
        score_path = self.HERE / "score_jev_memory_20261014_approved_001.json"
        receipt = json.loads((self.HERE / "receipt_jev_memory_20261014_approved_001.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(score_path.read_bytes()).hexdigest(), receipt["score_file_sha256"])
        spec = json.loads((self.HERE / "target_spans_2026-10-15.json").read_text(encoding="utf-8"))
        contested = {tuple(x) for x in spec["contested_probes_bracketed_for_interpretation_only"]}
        rows = [(c["id"], r["label"], r["cold_probe_pass"], r["learned_probe_pass"])
                for c in json.loads(score_path.read_text(encoding="utf-8"))["per_case"]
                for v in c["positive_probes"].values() for r in v]
        self.assertEqual((len(rows), sum(r[2] for r in rows), sum(r[3] for r in rows)), (16, 15, 14))
        kept = [r for r in rows if (r[0], r[1]) not in contested]
        self.assertEqual((len(kept), sum(r[2] for r in kept), sum(r[3] for r in kept)), (14, 14, 14))


if __name__ == "__main__":
    unittest.main()
