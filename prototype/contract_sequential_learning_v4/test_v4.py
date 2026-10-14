"""Offline plumbing tests for V4. All fixtures are SYNTHETIC (generated below); they test masking,
sealing, append-only learning, replay and that the decision rule can both pass and fail.
They are never evidence about real contractual learning.

    python -m unittest test_v4 -v
"""
from __future__ import annotations

import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path

import v4_corpus as C
import v4_sequential as S

ARTS = [("DEFINITIONS", ["Defined Terms", "Accounting Terms"]),
        ("CONDITIONS PRECEDENT", ["Effective Date", "Each Credit Event"]),
        ("AFFIRMATIVE COVENANTS", ["Financial Statements", "Insurance", "Books and Records; Inspection", "Use of Proceeds"]),
        ("NEGATIVE COVENANTS", ["Liens", "Fundamental Changes", "Indebtedness", "Transactions with Affiliates"]),
        ("EVENTS OF DEFAULT", ["Events of Default"]),
        ("MISCELLANEOUS", ["Notices", "Governing Law", "Counterparts"])]


def body_for(heading: str, rng: random.Random, learnable: bool, step: int) -> str:
    """Synthetic body. If `learnable`, Liens/Indebtedness carry exceptions, thresholds and cross-references that
    seeds (step<=2) do NOT show; random otherwise."""
    words = "The Borrower will maintain such records as are customary for its business."
    if learnable:
        if heading in ("Liens", "Indebtedness") and step > 2:
            return f'{words} except Permitted Liens up to $50,000,000 as set forth in Section 6.02 (the "Basket").'
        return words
    parts = [words]
    if rng.random() < 0.5:
        parts.append("except as otherwise agreed")
    if rng.random() < 0.5:
        parts.append("provided that no Default exists")
    if rng.random() < 0.5:
        parts.append("not to exceed $10,000,000")
    if rng.random() < 0.5:
        parts.append("subject to Section 6.01")
    return "; ".join(parts) + "."


def synthetic_html(doc: int, learnable: bool, seed: int) -> bytes:
    rng = random.Random(seed * 100 + doc)
    toc, bodytxt = ["<p>SYNTHETIC CREDIT AGREEMENT (test fixture)</p>"], []
    for a, (art, secs) in enumerate(ARTS, start=1):
        toc.append(f"<p>ARTICLE {a} {art}</p>")
        bodytxt.append(f"<p>ARTICLE {a} {art}</p>")
        for s, head in enumerate(secs, start=1):
            toc.append(f"<p>Section {a}.{s:02d} {head}</p>")
            bodytxt.append(f"<p>Section {a}.{s:02d} {head}. {body_for(head, rng, learnable, doc)}</p>")
            if art == "MISCELLANEOUS" and head == "Governing Law":
                bodytxt.append("<p>This Agreement shall be governed by, and construed in accordance with, the law of the State of New York.</p>")
    return ("<html><body>" + "".join(toc + bodytxt) + "</body></html>").encode()


def build_fixture(root: Path, learnable: bool, seed: int = 1) -> tuple[Path, Path]:
    views, hidden = root / "views", root / "hidden"
    views.mkdir(parents=True)
    hidden.mkdir()
    for k in range(1, 9):
        raw = synthetic_html(k, learnable, seed)
        src = {"doc_id": f"SYN-{k:02d}", "sha256": hashlib.sha256(raw).hexdigest(), "role": "SEED" if k <= 2 else "EVAL",
               "sequence_index": k, "file_date": f"2024-01-{k:02d}", "adsh": f"SYNTHETIC-{k}"}
        v, h = C.build_record(src, raw)
        (views / f"{src['doc_id']}.json").write_text(json.dumps(v))
        (hidden / f"{src['doc_id']}.json").write_text(json.dumps(h))
    return views, hidden


class TestCorpus(unittest.TestCase):
    def test_toc_and_bodies(self):
        s = C.structure(synthetic_html(3, False, 1))
        self.assertEqual(len(s["toc"]["units"]), 6)
        self.assertEqual(len(s["bodies"]), len(s["keys"]))
        self.assertTrue(s["bodies"]["4.01"].startswith("Section 4.01 Liens"))

    def test_eligibility_screens(self):
        ok, why, _ = C.eligibility(synthetic_html(3, False, 1), [])
        self.assertFalse(ok)
        self.assertIn("size", why)
        amend = b"<p>FIRST AMENDMENT TO CREDIT AGREEMENT</p>" + b"<p>x</p>" * 40000
        ok, why, _ = C.eligibility(amend, [])
        self.assertFalse(ok)
        self.assertIn("amendment", why)

    def test_hash_mismatch_refused(self):
        with self.assertRaises(ValueError):
            C.build_record({"doc_id": "X", "sha256": "0" * 64, "role": "SEED", "sequence_index": 1, "file_date": "", "adsh": ""},
                           synthetic_html(1, False, 1))


class TestSequential(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_mask_hides_target(self):
        views, _ = build_fixture(self.root, False)
        v = json.loads((views / "SYN-03.json").read_text())
        for t in S.targets(v):
            ctx = json.dumps(S.masked_context(v, t))
            p = next(p for _, _, p in S.subunits(v) if p["path"] == t["path"])
            self.assertNotIn(p["heading"], ctx)
            self.assertNotIn(t["path"], ctx)

    def test_hidden_requires_seal(self):
        _, hidden = build_fixture(self.root, False)
        h = S.Hidden(hidden)
        with self.assertRaises(PermissionError):
            h.get("SYN-03", "EVAL")
        h.seal("SYN-03")
        self.assertIn("bodies", h.get("SYN-03", "EVAL"))

    def test_run_order_frozen_and_growing(self):
        views, hidden = build_fixture(self.root, False)
        res = S.run(views, hidden, self.root / "out")
        self.assertEqual(res["provider_calls"], 0)
        frozen = {json.loads((self.root / "out" / "predictions" / f"{d}.json").read_text())["library_digest"]["FROZEN_SEED"] for d in res["sequence"]}
        self.assertEqual(len(frozen), 1, "frozen library must never change")
        versions = [json.loads((self.root / "out" / "predictions" / f"{d}.json").read_text())["library_version"]["CUMULATIVE"] for d in res["sequence"]]
        self.assertEqual(versions, list(range(2, 8)), "growing library must contain exactly the earlier agreements")
        self.assertEqual(res["hidden_access_order"], [f"SYN-{k:02d}" for k in range(1, 9)])
        packet = (self.root / "out" / "review_packet.csv").read_text().splitlines()
        self.assertEqual(len(packet), 1 + sum(d["n_targets"] for d in res["per_doc"]))
        self.assertNotIn("CUMULATIVE", packet[0])
        for k, c in enumerate(res["chain"][1:], start=1):
            self.assertEqual(c["prev"], res["chain"][k - 1]["entry_sha256"])

    def test_replay_identical(self):
        views, hidden = build_fixture(self.root, False)
        a = S.run(views, hidden, self.root / "a")
        b = S.run(views, hidden, self.root / "b")
        self.assertEqual([c["predictions_sha256"] for c in a["chain"]], [c["predictions_sha256"] for c in b["chain"]])

    def test_decision_can_pass_on_learnable_fixture(self):
        views, hidden = build_fixture(self.root, True)
        res = S.run(views, hidden, self.root / "out")
        self.assertEqual(res["decision"]["verdict"].split(":")[0], "KEEP", res["decision"])
        self.assertIn("PRECEDENT_COPY_EQUIVALENT_OR_BETTER", res["decision"]["qualifiers"])   # templated fixture
        self.assertGreater(res["decision"]["checks"]["gain_vs_frozen"], 0)
        self.assertTrue(any(l["new_dependency_edges"] for l in res["learned_after_each_agreement"]))

    def test_decision_can_fail_on_random_fixture(self):
        views, hidden = build_fixture(self.root, False, seed=7)
        res = S.run(views, hidden, self.root / "out")
        self.assertNotEqual(res["decision"]["verdict"].split(":")[0], "KEEP", res["decision"])


if __name__ == "__main__":
    unittest.main()
