"""Offline checks for cold_screen.py: bounds, pair parity, empty library, no answer or holdout leakage."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cold_screen
import probe

DATA = json.loads((HERE / "discriminating_candidates_v0.json").read_text(encoding="utf-8"))


class ColdScreenTests(unittest.TestCase):
    def setUp(self):
        self.plan = cold_screen.plan()
        self.reqs = self.plan["requests"]

    def test_six_requests_identical_pairs_exact_model_empty_library(self):
        self.assertEqual([(r["case_id"], r["repeat"]) for r in self.reqs],
                         [("MS1", 1), ("MS1", 2), ("MS2", 1), ("MS2", 2), ("MS3", 1), ("MS3", 2)])
        for a, b in zip(self.reqs[::2], self.reqs[1::2]):
            self.assertEqual(a["request"], b["request"])
            self.assertEqual(a["request_sha256"], b["request_sha256"])
        for r in self.reqs:
            self.assertEqual(r["request"]["model"], "jev-1.13.0")
            self.assertEqual(r["request"]["state"]["prior_provision_skeletons"], [])
            self.assertEqual(r["request"]["questions"], probe.questions())

    def test_no_label_evidence_or_holdout_text_reaches_provider(self):
        # Questions are the frozen probe.py wording (asserted above); check everything else sent.
        sent = json.dumps([r["request"]["state"] for r in self.reqs] + [r["request"]["model"] for r in self.reqs],
                          ensure_ascii=False)
        for word in ("YES", "UNRESOLVED", "HOLDOUT", "LIBRARY_UPDATE", "evidence", "label"):
            self.assertNotIn(word, sent)
        for d in DATA["decisions"]:
            if d["decision_id"] not in cold_screen.CASES:
                self.assertNotIn(d["quote"], sent, d["decision_id"])

    def test_live_refuses_without_confirmation(self):
        with patch.object(sys, "argv", ["cold_screen.py", "live"]), \
             patch.object(probe, "call_jev", side_effect=AssertionError("must not call")):
            with self.assertRaises(SystemExit):
                cold_screen.main()

    def test_score_flags_disagreement_only_when_both_repeats_disagree(self):
        def fake(p_ms1, p_ms3):
            base = {k: 0.1 for k in probe.questions()}
            recs = []
            for r, p in zip(self.reqs, p_ms1 + [0.9, 0.9] + p_ms3):
                fn = r["scored_function"]
                recs.append({"case_id": r["case_id"], "repeat": r["repeat"],
                             "request_sha256": r["request_sha256"],
                             "raw_response": {"model": "jev-1.13.0", "answers": {
                                 k: {"type": "noul", "noul": (p if k == fn else v)} for k, v in base.items()}}})
            return {"plan_sha256": probe.digest(self.plan), "records": recs}
        out = cold_screen.score(self.plan, fake([0.2, 0.3], [0.1, 0.2]))
        self.assertEqual(out["candidate_reproducible_disagreements"], ["MS1"])
        out = cold_screen.score(self.plan, fake([0.2, 0.7], [0.6, 0.2]))
        self.assertEqual(out["candidate_reproducible_disagreements"], [])
        self.assertEqual({r["case_id"]: r["verdict"] for r in out["per_case"]}["MS3"], "INSTABILITY_NOT_ERROR")
        self.assertEqual(out["decision"], "STOP_DATASET_AT_CEILING")


if __name__ == "__main__":
    unittest.main()
