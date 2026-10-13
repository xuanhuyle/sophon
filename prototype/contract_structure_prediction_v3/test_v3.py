"""Offline tests for the V3 masked-structure pilot. No network, no provider calls.
Fixtures below are SYNTHETIC structural records (not real documents); they test plumbing only and are
not evidence of predictive value."""
import json
import unittest
from pathlib import Path

import extract
import labels
import predict

HERE = Path(__file__).resolve().parent


def ca(doc_id, arts, law="STATE_OF_NEW_YORK", split="TRAIN"):
    secs = []
    for i, (func, provs) in enumerate(arts, 1):
        secs.append({"path": f"Article {i}", "heading": func, "functions": [func],
                     "subunits": [{"path": f"Section {i}.{j:02d}", "heading": p, "provision_type": p} for j, p in enumerate(provs, 1)]})
    return {"doc_id": doc_id, "family": "CREDIT_AGREEMENT", "split": split, "sections": secs,
            "governing_law": {"value": law, "evidence_section_paths": [s["path"] for s in secs if any(p["provision_type"] == "GOVERNING_LAW_JURISDICTION" for p in s["subunits"])]}}


def sla(doc_id, units, split="TRAIN"):
    return {"doc_id": doc_id, "family": "VENDOR_SLA", "split": split, "governing_law": {"value": "UNKNOWN", "evidence_section_paths": []},
            "sections": [{"path": f"Unit {i}", "heading": "h", "functions": f, "subunits": []} for i, f in enumerate(units, 1)]}


REPS = ["LITIGATION", "TAXES", "ERISA", "INVESTMENT_COMPANY", "FULL_DISCLOSURE"]
COV = ["FINANCIAL_REPORTING", "LIENS", "FUNDAMENTAL_CHANGES", "USE_OF_PROCEEDS", "MAINTENANCE_INSURANCE"]
MISC = ["NOTICES_COMMUNICATIONS", "GOVERNING_LAW_JURISDICTION", "JURY_TRIAL_WAIVER", "SEVERABILITY"]
TRAIN = [ca(f"T{i}", [("DEFINITIONS", ["DEFINED_TERMS"]), ("REPRESENTATIONS", REPS), ("COVENANTS_COMBINED", COV), ("MISCELLANEOUS", MISC)]) for i in range(3)] + \
        [sla(f"S{i}", [["SERVICE_COMMITMENT"], ["CREDIT_SCHEDULE"], ["CLAIM_PROCEDURE"], ["EXCLUSIONS"], ["DEFINITIONS"]]) for i in range(3)]


class Extraction(unittest.TestCase):
    def test_roman(self):
        self.assertEqual([extract.roman(x) for x in ["I", "IV", "IX", "XII", "Q"]], [1, 4, 9, 12, None])

    def test_toc_parse_stops_at_body(self):
        html = "<p>ARTICLE I</p><p>DEFINITIONS</p><p>SECTION 1.01</p><p>Defined Terms</p><p>ARTICLE II</p><p>THE CREDITS</p>" \
               "<p>SECTION 2.01</p><p>Loans and Borrowings</p><p>ARTICLE I</p><p>DEFINITIONS</p><p>SECTION 1.01 Defined Terms. body</p>"
        st = extract.credit_agreement_structure(html)
        self.assertEqual([(u["num"], u["heading"]) for u in st["units"]], [(1, "DEFINITIONS"), (2, "THE CREDITS")])
        self.assertEqual(st["units"][1]["subunits"][0]["heading"], "Loans and Borrowings")

    def test_sla_units_skip_table_headers(self):
        html = "<h1>Example SLA</h1><p>Provider will provide a Monthly Uptime Percentage of 99.9%.</p><p><b>Uptime</b></p><p><b>Credit</b></p>" \
               "<p>Less than 99.9% 10%</p><h2>Exclusions</h2><p>The SLA does not apply to beta features.</p><h2>Learn</h2><p>Blog</p>"
        st = extract.sla_structure(html)
        self.assertEqual([u["heading"] for u in st["units"]], ["HEADING_ABSENT", "Exclusions"])


class Labels(unittest.TestCase):
    def test_ca_rules(self):
        self.assertEqual(labels.ca_section_function("Negative Covenants"), "NEGATIVE_COVENANTS")
        self.assertEqual(labels.ca_section_function("COVENANTS OF THE COMPANY"), "COVENANTS_COMBINED")
        self.assertEqual(labels.ca_section_function("[RESERVED]"), "RESERVED")
        self.assertEqual(labels.ca_provision_type("WAIVER OF JURY TRIAL"), "JURY_TRIAL_WAIVER")
        self.assertEqual(labels.ca_provision_type("Indemnification"), "EXPENSES_INDEMNITY")
        self.assertEqual(labels.ca_provision_type("Something Novel"), "OTHER")

    def test_law_requires_explicit_clause(self):
        self.assertEqual(labels.evidenced_governing_law("Lender is based in New York.")["law"], "UNKNOWN")
        t = "This Agreement shall be construed in accordance with and governed by the law of the State of New York."
        self.assertEqual(labels.evidenced_governing_law(t)["law"], "STATE_OF_NEW_YORK")

    def test_sla_multilabel(self):
        f = labels.sla_unit_functions("Credit terms", "Requests for credits must be made within 30 days. The maximum amount of any credit is the invoice.")
        self.assertIn("CLAIM_PROCEDURE", f)
        self.assertIn("CREDIT_CAP", f)


class Prediction(unittest.TestCase):
    def test_soft_prior_never_zero(self):
        ctx = {"family": "CREDIT_AGREEMENT", "law": "UNKNOWN", "observed": ["DEFINITIONS"],
               "candidates": [c for c in labels.SECTION_VOCAB if c != "DEFINITIONS"]}
        p = predict.predict("SECTION", ctx, TRAIN, "FAMILY_SECTION")
        self.assertTrue(all(v["p"] > 0 for v in p["probs"].values()))
        self.assertGreater(p["probs"]["REPRESENTATIONS"]["p"], p["probs"]["CREDIT_SCHEDULE"]["p"])
        self.assertEqual(predict.p_in_top(p, "REPRESENTATIONS", 3), 1.0)

    def test_masking_hides_target_and_law(self):
        held = ca("H", [("DEFINITIONS", ["DEFINED_TERMS"]), ("REPRESENTATIONS", REPS), ("COVENANTS_COMBINED", COV), ("MISCELLANEOUS", MISC)], split="HELDOUT")
        c = predict.section_cases(held)[0]
        for t in c["positives"]:
            self.assertNotIn(t, c["observed"])
            self.assertIn(t, c["candidates"])
        if "MISCELLANEOUS" in c["positives"]:
            self.assertEqual(c["law"], "UNKNOWN")

    def test_provision_leak_guard(self):
        held = ca("H", [("REPRESENTATIONS", REPS), ("COVENANTS_COMBINED", COV + ["TAXES"])], split="HELDOUT")
        for c in predict.provision_cases(held):
            self.assertNotIn("TAXES", c["positives"])   # TAXES also visible in the other article

    def test_section_conditioning_beats_family_on_synthetic(self):
        held = ca("H", [("REPRESENTATIONS", REPS), ("COVENANTS_COMBINED", COV), ("MISCELLANEOUS", MISC)], split="HELDOUT")
        res = predict.run(TRAIN, [held])
        self.assertGreaterEqual(res["summary"]["FAMILY_SECTION"]["by_task"]["PROVISION"]["hit3"],
                                res["summary"]["FAMILY"]["by_task"]["PROVISION"]["hit3"])

    def test_conflicting_family_backs_off(self):
        ctx = {"family": "VENDOR_SLA", "law": "UNKNOWN", "observed": ["REPRESENTATIONS", "COVENANTS_COMBINED", "MISCELLANEOUS"],
               "candidates": sorted(set(labels.SECTION_VOCAB) - {"REPRESENTATIONS", "COVENANTS_COMBINED", "MISCELLANEOUS"})}
        p = predict.predict("SECTION", ctx, TRAIN, "FAMILY_SECTION")
        self.assertTrue(any("CONTEXT_CONFLICT" in f for f in p["flags"]))
        self.assertEqual(p["top_k"][0], "DEFINITIONS")

    def test_law_untestable_when_single_law(self):
        ctx = {"family": "CREDIT_AGREEMENT", "law": "STATE_OF_NEW_YORK", "observed": ["DEFINITIONS"], "candidates": labels.SECTION_VOCAB}
        p = predict.predict("SECTION", ctx, TRAIN, "EVIDENCED_LAW_FAMILY_SECTION")
        self.assertTrue(any(f.startswith("LAW_EFFECT_UNTESTABLE") for f in p["flags"]))

    def test_tie_aware_topk(self):
        pred = {"ranked": ["a", "b", "c", "d"], "probs": {k: {"p": 0.5} for k in "abcd"}}
        self.assertAlmostEqual(predict.p_in_top(pred, "d", 3), 0.75)


class Freeze(unittest.TestCase):
    def test_receipt_matches_files_if_present(self):
        rec = HERE / "frozen" / "freeze_receipt.json"
        if not rec.exists():
            self.skipTest("not frozen yet")
        import hashlib
        for name, digest in json.loads(rec.read_text(encoding="utf-8"))["files"].items():
            self.assertEqual(hashlib.sha256((HERE / name).read_bytes()).hexdigest(), digest, name)


if __name__ == "__main__":
    unittest.main()
