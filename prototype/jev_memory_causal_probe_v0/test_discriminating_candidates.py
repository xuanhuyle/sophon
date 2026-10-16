"""Offline identity/split checks for discriminating_candidates_v0.json. No provider calls.

Passing proves only that quotes, hashes and splits are internally consistent; it does not
validate any label. Set SOPHON_SLA_SOURCE_DIR to a folder holding the two re-downloaded
source files (names in SOURCE_FILES) to also re-verify source hashes and offsets.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe

DATA = json.loads((HERE / "discriminating_candidates_v0.json").read_text(encoding="utf-8"))
SOURCE_FILES = {"MS-OSSLA-2021-07": "ms_sla_jul2021.docx", "ORCL-PILLAR-2026-09": "pillar.pdf"}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized_text(source_id: str, path: Path) -> str:
    """The extraction recorded in each source's `extraction` field."""
    if source_id == "MS-OSSLA-2021-07":
        xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
        paras = ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
                 for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)]
        raw = html.unescape("\n".join(paras))
    else:
        raw = subprocess.run(["pdftotext", str(path), "-"], capture_output=True,
                             text=True, check=True).stdout
    return " ".join(raw.split())


class DiscriminatingCandidateTests(unittest.TestCase):
    def test_labels_wording_and_balance(self):
        wording = {**probe.FUNCTIONS, **probe.MODIFIERS}
        labels = [d["label"] for d in DATA["decisions"]]
        self.assertTrue(8 <= len(labels) <= 12)
        self.assertGreaterEqual(labels.count("YES"), 3)
        self.assertGreaterEqual(labels.count("NO"), 3)
        for d in DATA["decisions"]:
            self.assertIn(d["label"], ("YES", "NO", "UNRESOLVED"))
            self.assertEqual(d["function_wording"], wording[d["function"]], d["decision_id"])
            self.assertTrue(d["evidence_for_positive_reading"] and d["evidence_for_negative_reading"])
        self.assertEqual(len({d["decision_id"] for d in DATA["decisions"]}), len(labels))

    def test_quotes_contexts_and_offsets_are_consistent(self):
        for d in DATA["decisions"]:
            ctx, (cs, ce), (qs, qe) = (d["context"], d["context_offsets_in_normalized_text"],
                                       d["quote_offsets_in_normalized_text"])
            self.assertEqual(sha(ctx), d["context_sha256"], d["decision_id"])
            self.assertEqual(ce - cs, len(ctx))
            self.assertEqual(ctx[qs - cs:qe - cs], d["quote"], d["decision_id"])

    def test_one_holdout_document_never_shared_with_library_or_prior_cases(self):
        splits = {s["source_id"]: s["split"] for s in DATA["sources"]}
        self.assertEqual(sorted(splits.values()), ["HOLDOUT", "LIBRARY_UPDATE"])
        for d in DATA["decisions"]:
            self.assertEqual(d["split"], splits[d["source_id"]])
        holdout = [d for d in DATA["decisions"] if d["split"] == "HOLDOUT"]
        update = [d for d in DATA["decisions"] if d["split"] == "LIBRARY_UPDATE"]
        self.assertTrue(holdout and update)
        cases, memory = probe.cases_and_memory()
        prior = json.dumps([cases, memory], ensure_ascii=False)
        for h in holdout:
            self.assertNotIn(h["quote"], prior, h["decision_id"])
            for u in update:
                self.assertNotIn(h["quote"], u["context"])
                self.assertNotIn(u["quote"], h["context"])

    @unittest.skipUnless(os.environ.get("SOPHON_SLA_SOURCE_DIR"), "source files not supplied")
    def test_reverify_against_downloaded_sources(self):
        folder = Path(os.environ["SOPHON_SLA_SOURCE_DIR"])
        for s in DATA["sources"]:
            path = folder / SOURCE_FILES[s["source_id"]]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), s["sha256"], s["source_id"])
            text = normalized_text(s["source_id"], path)
            self.assertEqual(sha(text), s["normalized_text_sha256"], s["source_id"])
            for d in (d for d in DATA["decisions"] if d["source_id"] == s["source_id"]):
                cs, ce = d["context_offsets_in_normalized_text"]
                self.assertEqual(text[cs:ce], d["context"], d["decision_id"])
                self.assertEqual(text.count(d["quote"]), 1, d["decision_id"])


if __name__ == "__main__":
    unittest.main()
