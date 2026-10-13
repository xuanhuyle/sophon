"""Offline tests for the adjudication package (no network, no provider). Synthetic fixtures test plumbing only;
nothing here is evidence about any label or prediction.

    python -m unittest test_adjudication -v
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
V3 = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V3))

import fetch_local_evidence as fle  # noqa: E402

FROZEN = ["results/heldout_run.json", "results/secondary_repaired_run.json", "results/dev_loo.json",
          "data/records_train.json", "data/records_heldout.json", "data/records_heldout_secondary.json",
          "frozen/freeze_receipt.json", "labels.py", "predict.py", "extract.py", "corpus.py"]


def digest(paths):
    return {p: hashlib.sha256((V3 / p).read_bytes()).hexdigest() for p in paths}


class Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = digest(FROZEN)
        cls.out = subprocess.run([sys.executable, str(HERE / "build_review_package.py")], capture_output=True, text=True, check=True).stdout
        cls.after = digest(FROZEN)

    def test_frozen_files_untouched(self):
        self.assertEqual(self.before, self.after)

    def test_counts_match_frozen_cases(self):
        counts = json.loads(self.out.strip().splitlines()[-1])
        run = json.loads((V3 / "results/secondary_repaired_run.json").read_text(encoding="utf-8"))
        self.assertEqual(counts["positives"], sum(len(i["case"]["positives"]) for i in run["cases"]))
        self.assertEqual(counts["negatives"], sum(len(i["case"]["negatives"]) for i in run["cases"]))
        self.assertEqual(counts["neg_top3"] + counts["neg_brier_only"], counts["negatives"])
        self.assertEqual((counts["positives"], counts["negatives"]), (18, 275))

    def test_every_scored_label_has_a_row_and_tier(self):
        rows = list(csv.DictReader((HERE / "review_labels.csv").read_text(encoding="utf-8").splitlines()))
        run = json.loads((V3 / "results/secondary_repaired_run.json").read_text(encoding="utf-8"))
        want = {(i["case"]["case_id"], l) for i in run["cases"] for l in i["case"]["positives"] + i["case"]["negatives"]}
        self.assertEqual({(r["case_id"], r["label"]) for r in rows}, want)
        self.assertTrue(all(r["tier"] in {"1A", "1B", "2"} for r in rows))
        self.assertTrue(all(r["tier"] == "1A" for r in rows if r["polarity"].startswith("POSITIVE")))

    def test_worksheet_unadjudicated_and_complete(self):
        rows = list(csv.DictReader((HERE / "review_units.csv").read_text(encoding="utf-8").splitlines()))
        self.assertEqual(len(rows), 78)
        self.assertEqual(len({r["unit_id"] for r in rows}), 78)
        for r in rows:
            self.assertEqual(r["label_status"], "PROVISIONAL_AGENT_AUTHORED")
            for k in ("reviewer_labels", "reviewer_verdict", "reviewer_evidence_quote", "reviewer_notes"):
                self.assertEqual(r[k], "", k)
        self.assertEqual(sum(r["role"] == "MASKED_TARGET" for r in rows), 16)

    def test_no_claim_of_validation(self):
        text = (HERE / "REVIEW_PACKAGE.md").read_text(encoding="utf-8")
        self.assertIn("AWAITING_HUMAN_ADJUDICATION", text)
        self.assertNotIn("INDEPENDENT_HUMAN_REVIEWED", text)
        self.assertNotRegex(text, r"(?i)\bvalidated by (claude|the agent)")

    def test_deterministic(self):
        first = digest(["adjudication/REVIEW_PACKAGE.md", "adjudication/review_units.csv", "adjudication/review_labels.csv"])
        subprocess.run([sys.executable, str(HERE / "build_review_package.py")], capture_output=True, check=True)
        self.assertEqual(first, digest(["adjudication/REVIEW_PACKAGE.md", "adjudication/review_units.csv", "adjudication/review_labels.csv"]))


SYNTH_CA = """<html><body>
<p>TABLE OF CONTENTS</p><p>ARTICLE I DEFINITIONS</p><p>Section 1.01 Defined Terms 1</p><p>Section 1.02 Divisions 9</p>
<p>ARTICLE II MISCELLANEOUS</p><p>Section 2.01 Notices 10</p>
<p>ARTICLE I</p><p>DEFINITIONS</p><p>Section 1.01 Defined Terms. "Agent" means the synthetic agent.</p><p>More definition text.</p>
<p>Section 1.02 Divisions. For all purposes a synthetic division rule applies.</p>
<p>ARTICLE II</p><p>MISCELLANEOUS</p><p>Section 2.01 Notices. Notices go to a synthetic address.</p>
</body></html>"""


class LocalRetrievalPlumbing(unittest.TestCase):
    def test_section_body_is_taken_after_toc(self):
        rec = {"sections": [{"path": "Article 1", "heading": "DEFINITIONS", "subunits": [{"path": "Section 1.01", "heading": "Defined Terms"},
                                                                                        {"path": "Section 1.02", "heading": "Divisions"}]},
                            {"path": "Article 2", "heading": "MISCELLANEOUS", "subunits": [{"path": "Section 2.01", "heading": "Notices"}]}]}
        p = fle.ca_passages(SYNTH_CA, rec)
        self.assertEqual(p["Section 1.01"][1], "BODY_AFTER_TOC")
        self.assertIn("synthetic agent", p["Section 1.01"][0])
        self.assertIn("More definition text", p["Section 1.01"][0])
        self.assertNotIn("Divisions", p["Section 1.01"][0])
        self.assertIn("synthetic division rule", p["Section 1.02"][0])
        self.assertIn("synthetic address", p["Section 2.01"][0])

    def test_missing_section_is_reported_not_invented(self):
        rec = {"sections": [{"path": "Article 1", "heading": "DEFINITIONS", "subunits": [{"path": "Section 1.09", "heading": "Rates"}]}]}
        self.assertEqual(fle.ca_passages(SYNTH_CA, rec)["Section 1.09"], ("", "PASSAGE_NOT_LOCATED"))

    def test_structure_comparison_detects_label_drift(self):
        a = {"sections": [{"path": "Unit 1", "heading": "X", "functions": ["DEFINITIONS"], "unit_text_sha256": "h", "subunits": []}]}
        b = json.loads(json.dumps(a))
        self.assertEqual(fle.compare(a, b), [])
        b["sections"][0]["unit_text_sha256"] = "other"
        self.assertEqual(fle.compare(a, b), ["Unit 1.unit_text_sha256"])

    def test_sources_cover_all_secondary_docs_with_hashes(self):
        src = fle.sources()
        self.assertEqual(set(src), set(fle.DOCS))
        self.assertTrue(all(len(s["sha256"]) == 64 and s["url"].startswith("https://") for s in src.values()))


if __name__ == "__main__":
    unittest.main()
