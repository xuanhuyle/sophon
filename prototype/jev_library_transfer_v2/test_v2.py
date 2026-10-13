"""JEV V2 offline tests. Every provider response here is a LAB_FIXTURE shaped like the official schemas;
nothing is evidence of transfer. No network: urlopen is patched to fail wherever a call could occur."""
import copy
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("transfer", HERE / "transfer.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
p = t.p

A_CORPUS = t.read_json(t.FILES["a_corpus"])
B_CORPUS = t.read_json(t.FILES["b_corpus"])
CHECKLIST = t.read_json(t.FILES["checklist"])
LIB0 = t.read_json(t.FILES["lib0"])
CTX = t.load_context(t.FILES["ctx"])
B1 = next(c for c in B_CORPUS["clauses"] if c["id"] == "B1")
B1_SOURCE = p.anchor_source(B1)


def fixture_a_evidence() -> dict:
    """A LAB_FIXTURE Contract-A evidence bundle shaped like load_a_evidence output (not the real recording)."""
    packets = {}
    for c in A_CORPUS["clauses"][:4]:
        quotes = {"G1": ["either (not both)", "less than or equal to 99.9%, but greater than 99.0%", "the amount Customer paid for a Service Feature in a calendar quarter"],
                  "G2": ["“Downtime” is a period of time where either (a)", "the error rate exceeds five percent (5%) in a given minute", "as determined by a combination of GitHub’s internal and external monitoring systems"],
                  "G3": ["Excluded from the Uptime Calculation are Service Feature failures resulting from", "(i) Customer’s acts, omissions, or misuse"],
                  "G4": ["only upon written request to GitHub", "within thirty (30) days of the end of the calendar quarter", "limited to a maximum of ninety (90) days of paid service per calendar quarter", "sole and exclusive remedy"]}[c["id"]]
        prim = {"G1": "PERMISSION_RIGHT", "G2": "DEFINITION", "G3": "DEFINITION", "G4": "PERMISSION_RIGHT"}[c["id"]]
        mods = {"G1": ["THRESHOLD", "CONDITION"], "G2": ["THRESHOLD", "CONDITION"], "G3": ["EXCLUSION", "CROSS_REFERENCE"], "G4": ["CONDITION", "DEADLINE", "THRESHOLD"]}[c["id"]]
        review = {"verdict": "SUPPORTED_WITH_GAPS", "missing_modifiers": [], "evidence_quotes": quotes, "issues": ["x"], "missing_source_refs": []}
        packets[c["id"]] = {"id": c["id"], "text": c["text"], "context": c["context"], "source_sha256": p.sha256_text(p.anchor_source(c)),
                            "excerpt_sha256": c["excerpt_sha256"], "document_id": c["source_id"],
                            "jev": {"primary": prim, "probabilities": {}, "confidence": 0.9, "modifiers": {m: (0.9 if m in mods else 0.1) for m in p.MODIFIERS},
                                    "modifiers_present": mods, "flags": ["JEV_OPTION_ORDER_SENSITIVE: PERMISSION_RIGHT vs reversed DEFINITION"] if c["id"] == "G1" else [],
                                    "model": "jev-fixture", "provenance": "LAB_FIXTURE"},
                            "reviews": {r: {"valid": True, "error": None, "output": review, "model": "fixture", "issues_sha256": "0" * 64} for r in t.ROLES}}
    return {"ok": True, "blockers": [], "packets": packets, "recording": {"path": "fixture", "sha256": "f" * 64, "corpus_sha256": p.digest(A_CORPUS)}}


def review_obj(slots=(), verdict="SUPPORTED_WITH_GAPS", ta="MATCH", omitted=(), refs=(), missing=(), issues=("gap",), risks=(), competing=()):
    return {"verdict": verdict, "template_assessment": ta, "slots": list(slots), "missing_required_slots": list(missing),
            "omitted_conditions": list(omitted), "wrong_transfer_risks": list(risks), "cross_references": list(refs),
            "competing_templates": list(competing), "issues": list(issues)}


class FrozenSourceTests(unittest.TestCase):
    def test_b_packets_hashes_and_checklist_anchors(self):
        t.check_packets(B_CORPUS, 3)
        self.assertEqual(B_CORPUS["sources"][0]["version"].split(" (")[0], "Last modified: June 24, 2021")
        for pid, entry in CHECKLIST["packets"].items():
            src = p.anchor_source(next(c for c in B_CORPUS["clauses"] if c["id"] == pid))
            for el in entry["material_elements"]:
                self.assertTrue(p.anchored(el["anchor"], src), f"{el['id']} anchor not in packet")
                self.assertTrue(set(el["acceptable_slots"]) <= set(t.SLOTS), el["id"])
            self.assertTrue(set(entry["critical_slots"]) <= set(t.SLOTS))

    def test_edited_b_packet_is_detected(self):
        edited = copy.deepcopy(B_CORPUS)
        edited["clauses"][0]["text"] = edited["clauses"][0]["text"].replace("five minute", "one minute")
        with self.assertRaises(ValueError):
            t.check_packets(edited, 3)

    def test_checklist_is_sealed_and_never_in_prompts(self):
        self.assertEqual(CHECKLIST["status"], "PROVISIONAL_NOT_INDEPENDENT_ORACLE")
        self.assertTrue(CHECKLIST["sealed_from_model_prompts"])
        lib1 = t.read_json(t.FILES["lib1"]) if t.FILES["lib1"].exists() else LIB0
        sc = t.section_context(CTX, "B1")
        prompts = [t.blind_prompt_v2(B1, sc)]
        for cond in t.CONDITIONS:
            mem = t.condition_memory(cond, LIB0, lib1, fixture_a_evidence(), next(iter(lib1["templates"])))
            for role in t.ROLES:
                prompts.append(t.reviewer_prompt_v2(role, B1, sc, mem, {"template": "X"}))
        for prompt in prompts:
            self.assertNotIn("material_elements", prompt)
            self.assertNotIn("contamination_markers", prompt)
            self.assertNotIn(CHECKLIST["packets"]["B1"]["material_elements"][0]["description"], prompt)


class SchemaRepairTests(unittest.TestCase):
    def test_v1_blind_object_form_is_diagnosed_field_level(self):
        obj = {"primary_types": ["DEFINITION"], "modifiers": ["THRESHOLD"], "evidence_quotes": {"THRESHOLD": ["five minute period"]},
               "unresolved_refs": [], "issues": [], "complete_from_packet": False}
        d = t.diagnose_v1_baseline(obj, B1_SOURCE)
        self.assertEqual(d["errors"], ["evidence_quotes: expected list, got dict"])
        self.assertIn("evidence_quotes:OBJECT_FORM_NORMALIZED", d["flags"])

    def test_v2_slots_object_form_normalized_and_flagged_not_loosened(self):
        obj = review_obj(slots=[])
        obj["slots"] = {"measurement_period": "during a monthly billing cycle", "threshold": ["NOT IN SOURCE"]}
        r = t.check_review_v2(obj, B1_SOURCE)
        self.assertFalse(r["valid"])
        self.assertIn("slots:OBJECT_FORM_NORMALIZED", r["flags"])
        self.assertTrue(any("slots[1].quote (threshold): not a verbatim substring" in e for e in r["errors"]))

    def test_unanchored_quote_unknown_slot_and_bad_verdict_are_separate_errors(self):
        obj = review_obj(slots=[{"slot": "banana", "value": "x", "quote": "100%, minus the average of Error Rates"},
                                {"slot": "deadline", "value": "x", "quote": "within thirty (30) days"}],
                         verdict="SUPPORTED", omitted=[{"description": "d", "quote": "monthly billing cycle"}])
        r = t.check_review_v2(obj, B1_SOURCE)
        self.assertFalse(r["valid"])
        joined = "\n".join(r["errors"])
        self.assertIn("slots[0].slot: 'banana' is not a known slot name", joined)
        self.assertIn("slots[1].quote (deadline): not a verbatim substring", joined)
        self.assertIn("SUPPORTED cannot coexist", joined)

    def test_valid_review_keeps_only_anchored_slots(self):
        obj = review_obj(slots=[{"slot": "measurement_period", "value": "monthly billing cycle", "quote": "during a monthly billing cycle"}],
                         refs=[{"name": "Documentation", "quote": "conform to the Documentation", "resolved_in_packet": False}])
        r = t.check_review_v2(obj, B1_SOURCE)
        self.assertTrue(r["valid"], r["errors"])
        self.assertEqual(r["output"]["slots"][0]["slot"], "measurement_period")

    def test_blind_claiming_template_is_flagged(self):
        r = t.check_review_v2(review_obj(ta="MATCH"), B1_SOURCE, blind=True)
        self.assertIn("BLIND_CLAIMED_TEMPLATE_ASSESSMENT", r["flags"])


class LibraryValidatorTests(unittest.TestCase):
    def test_bootstrap_library_is_valid(self):
        self.assertEqual(t.validate_library(LIB0), [])

    def test_rejects_approved_status_copied_literal_contradiction_and_supersession_without_evidence(self):
        lib = copy.deepcopy(LIB0)
        tpl = lib["templates"]["DEFINITION"]
        tpl["status"] = "APPROVED"
        tpl["structural_rules"] = ["The band is always 99.9% in a calendar quarter."]
        tpl["optional_slots"].append("normative_action")
        lib["templates"]["OTHER"]["status"] = "SUPERSEDED"
        errors = "\n".join(t.validate_library(lib))
        self.assertIn("APPROVED", errors)
        self.assertIn("vendor-specific literal", errors)
        self.assertIn("contradictory slot definitions", errors)
        self.assertIn("SUPERSEDED without a successor", errors)

    def test_rejects_missing_anchor_and_b_leakage(self):
        lib = copy.deepcopy(LIB0)
        lib["templates"]["LEARNED"] = {**copy.deepcopy(lib["templates"]["DEFINITION"]), "id": "LEARNED", "learned_from_source": True, "positive_examples": [],
                                       "lineage": [{"event": "DISCOVER", "at_utc": "x", "from_version": None, "reason": "r", "evidence": None}]}
        errors = "\n".join(t.validate_library(lib))
        self.assertIn("DISCOVER event without evidence", errors)
        self.assertIn("without a source-anchored positive example", errors)
        lib2 = copy.deepcopy(LIB0)
        lib2["templates"]["DEFINITION"]["known_limits"].append("Watch for Nearline tiers")
        self.assertIn("B_LEAKAGE", "\n".join(t.validate_library(lib2)))

    def test_induction_from_fixture_is_deterministic_sourced_and_b_free(self):
        a = fixture_a_evidence()
        lib1, events = t.induce_library(LIB0, a, created_at="2026-10-13T00:00:00Z")
        lib1b, _ = t.induce_library(LIB0, a, created_at="2026-10-13T00:00:00Z")
        self.assertEqual(lib1, lib1b)
        self.assertEqual(t.validate_library(lib1), [])
        self.assertIn("TIERED_SERVICE_CREDIT_SCHEDULE", lib1["templates"])
        tpl = lib1["templates"]["TIERED_SERVICE_CREDIT_SCHEDULE"]
        self.assertEqual(tpl["category_readings"], ["DEFINITION", "PERMISSION_RIGHT"])  # from the recorded order-sensitivity flag
        self.assertEqual(tpl["lineage"][0]["event"], "DISCOVER")
        self.assertEqual(tpl["positive_examples"][0]["excerpt_sha256"], a["packets"]["G1"]["excerpt_sha256"])
        self.assertTrue(any(c["packet_id"] == "G3" for c in tpl["counterexamples"]))
        kinds = {e["event"] for e in events}
        self.assertTrue({"DISCOVER", "ABSTAIN"} <= kinds)
        self.assertIn("SLA_EXCLUSION_LIST", lib1["templates"])  # the fixture keeps the enumerator "(i)"

    def test_recording_from_other_corpus_or_lab_provenance_is_blocked(self):
        rec = {"corpus_sha256": "0" * 64, "records": []}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "live_EXT_x.json"
            path.write_text(json.dumps(rec), encoding="utf8")
            out = t.load_a_evidence(path, A_CORPUS)
            self.assertFalse(out["ok"])
            self.assertTrue(out["blockers"][0].startswith("BLOCKED_A_RECORDING"))
            rec = {"corpus_sha256": p.digest(A_CORPUS), "records": [{"clause_id": "G1", "source_sha256": p.sha256_text(p.anchor_source(A_CORPUS["clauses"][0])),
                                                                     "steps": {"jev": {"provenance": "LAB_FIXTURE"}, "adversarial": {}, "backward": {}}}]}
            path.write_text(json.dumps(rec), encoding="utf8")
            out = t.load_a_evidence(path, A_CORPUS)
            self.assertTrue(any("without ACTUAL_PROVIDER provenance" in b for b in out["blockers"]))


class ContextValidatorTests(unittest.TestCase):
    def test_frozen_context_is_valid(self):
        self.assertEqual(t.validate_context(CTX, [A_CORPUS, B_CORPUS]), [])

    def test_rejects_unsupported_country_and_law_forum_conflation(self):
        ctx = copy.deepcopy(CTX)
        rec = ctx["legal_context"]["records"]["LC-GCS-SLA-20210624"]
        rec["governing_law"] = {"status": "UNKNOWN", "value": "California", "evidence_anchor": None, "provenance": "vendor is headquartered in California"}
        errors = "\n".join(t.validate_context(ctx, [A_CORPUS, B_CORPUS]))
        self.assertIn("without EVIDENCED status (unsupported inference)", errors)
        self.assertIn("names a jurisdiction without evidence", errors)
        ctx = copy.deepcopy(CTX)
        rec = ctx["legal_context"]["records"]["LC-GCS-SLA-20210624"]
        rec["governing_law"] = {"status": "EVIDENCED", "value": "the Agreement", "evidence_anchor": "have the meaning set forth in the Agreement", "provenance": ""}
        rec["forum"] = dict(rec["governing_law"])
        self.assertIn("conflated", "\n".join(t.validate_context(ctx, [A_CORPUS, B_CORPUS])))
        ctx["legal_context"]["records"]["LC-GH-SLA-2021"]["party_domicile"]["used_as_governing_law_evidence"] = True
        self.assertIn("party domicile used as governing-law evidence", "\n".join(t.validate_context(ctx, [A_CORPUS, B_CORPUS])))

    def test_rejects_invented_heading_false_label_bad_parent_and_lost_inheritance(self):
        ctx = copy.deepcopy(CTX)
        s = ctx["section_registry"]["sections"]["GCS-SLA-20210624/CLAIM"]
        s["heading"] = "Article 7 Claims"
        s["functions"].append("ARBITRATION")
        s["parent"] = "GCS-SLA-20210624/NOPE"
        ctx["provisions"]["provisions"]["B3"]["inherited"]["contract_family_id"] = "FINANCING_AGREEMENT"
        ctx["provisions"]["provisions"]["B1"]["section_ids"] = ["GH-SLA-2021/S1"]
        errors = "\n".join(t.validate_context(ctx, [A_CORPUS, B_CORPUS]))
        self.assertIn("invented heading", errors)
        self.assertIn("unsupported section function labels ['ARBITRATION']", errors)
        self.assertIn("parent 'GCS-SLA-20210624/NOPE' does not exist", errors)
        self.assertIn("inherited contract family lost or changed without an override", errors)
        self.assertIn("wrong section-to-source link", errors)

    def test_rejects_unanchored_cross_section_ref_and_unevidenced_family(self):
        ctx = copy.deepcopy(CTX)
        ctx["provisions"]["provisions"]["B2"]["cross_section_refs"][0]["quote"] = "Section 9 applies"
        ctx["contract_family"]["families"]["SERVICE_LEVEL_AGREEMENT"]["examples"][1]["evidence_anchor"] = "Master Subscription Agreement"
        errors = "\n".join(t.validate_context(ctx, [A_CORPUS, B_CORPUS]))
        self.assertIn("cross-section reference quote not anchored", errors)
        self.assertIn("contract-family assignment without an anchored evidence quote", errors)

    def test_override_requires_anchor_and_scope(self):
        ctx = copy.deepcopy(CTX)
        ctx["provisions"]["provisions"]["B2"]["overrides"] = {"contract_family_id": {"value": "OTHER_UNKNOWN"}}
        ctx["provisions"]["provisions"]["B2"]["inherited"]["contract_family_id"] = "OTHER_UNKNOWN"
        self.assertIn("override of contract_family_id without anchored evidence and scope", "\n".join(t.validate_context(ctx, [A_CORPUS, B_CORPUS])))

    def test_section_context_given_to_arms_is_identical_and_preserves_literal_path(self):
        sc = t.section_context(CTX, "B3")
        self.assertEqual([s["heading"] for s in sc["sections"]], ["Customer Must Request Financial Credit", "Maximum Financial Credit", "SLA Exclusions."])
        self.assertTrue(all(s["numbering"] == "UNNUMBERED" for s in sc["sections"]))
        self.assertEqual(sc["document"]["governing_law_status"], "REFERENCED_SOURCE_UNAVAILABLE")
        self.assertEqual(t.section_context(CTX, "B2")["sections"][0]["heading"], "HEADING_ABSENT")
        prompts = {role: t.reviewer_prompt_v2(role, B1, sc, t.condition_memory("COLD_B", LIB0, None, None, "DEFINITION"), {"template": "DEFINITION"}) for role in t.ROLES}
        for prompt in prompts.values():
            self.assertIn(json.dumps(sc, ensure_ascii=False), prompt)


class LeakageAndMemoryTests(unittest.TestCase):
    def test_cold_and_raw_memory_never_contain_learned_library_and_synthesis_prompt_never_contains_b(self):
        a = fixture_a_evidence()
        lib1, _ = t.induce_library(LIB0, a)
        cold = json.dumps(t.condition_memory("COLD_B", LIB0, lib1, a, "DEFINITION"))
        raw = json.dumps(t.condition_memory("WARM_RAW_A_B", LIB0, lib1, a, "DEFINITION"))
        warm = json.dumps(t.condition_memory("WARM_LIBRARY_B", LIB0, lib1, a, "TIERED_SERVICE_CREDIT_SCHEDULE"))
        learned_rule = lib1["templates"]["TIERED_SERVICE_CREDIT_SCHEDULE"]["structural_rules"][0]
        for mem in (cold, raw):
            self.assertNotIn("TIERED_SERVICE_CREDIT_SCHEDULE", mem)
            self.assertNotIn(learned_rule, mem)
            self.assertNotIn("positive_examples\": [{", mem)
        self.assertNotIn("prior_examples", cold)
        self.assertIn("prior_examples", raw)
        self.assertIn("structural_rules", warm)
        synth = t.synthesis_prompt(a, lib1).lower()
        for tok in t.B_LEAKAGE_TOKENS:
            self.assertNotIn(tok, synth)
        for pk in B_CORPUS["clauses"]:
            self.assertNotIn(pk["text"][:40].lower(), synth)
        self.assertNotIn("material_elements", synth)

    def test_jev_requests_differ_only_in_memory_and_use_official_shape(self):
        a = fixture_a_evidence()
        lib1, _ = t.induce_library(LIB0, a)
        reqs = {c: t.jev_request_v2(B1, c, LIB0, lib1, a, "jev-latest") for c in t.CONDITIONS}
        for r in reqs.values():
            self.assertEqual(set(r), {"model", "state", "questions"})
            self.assertEqual(r["state"]["clause"], B1["text"])
            self.assertIn(t.NO_TEMPLATE, r["questions"]["template"]["criteria"])
            self.assertEqual(set(r["questions"]) - {"template", "template_reversed"}, set(p.MODIFIERS))
        self.assertNotIn("prior_examples", reqs["COLD_B"]["state"])
        self.assertIn("prior_examples", reqs["WARM_RAW_A_B"]["state"])
        self.assertEqual(reqs["COLD_B"]["questions"]["template"]["criteria"].keys(), reqs["WARM_RAW_A_B"]["questions"]["template"]["criteria"].keys())
        self.assertIn("TIERED_SERVICE_CREDIT_SCHEDULE", reqs["WARM_LIBRARY_B"]["questions"]["template"]["criteria"])


class ReconcileAndScoreTests(unittest.TestCase):
    def jev_raw(self, options, choice, model="jev-1.13.0"):
        probs = {k: (0.9 if k == choice else 0.1 / (len(options) - 1)) for k in options}
        answers = {"template": {"type": "choice", "choice": choice, "probabilities": probs, "confidence": 0.8},
                   "template_reversed": {"type": "choice", "choice": choice, "probabilities": probs, "confidence": 0.8}}
        answers.update({m: {"type": "noul", "noul": 0.7} for m in p.MODIFIERS})
        return {"model": model, "usage": {"input_tokens": 10, "output_tokens": 5}, "answers": answers}

    def test_no_template_and_reviewer_conflict_hold(self):
        options = list(LIB0["templates"]) + [t.NO_TEMPLATE]
        jev = t.parse_jev_v2(self.jev_raw(options, t.NO_TEMPLATE), options)
        self.assertTrue(jev["valid"])
        adv = {"ran": True, **t.check_review_v2(review_obj(verdict="DISPUTED", ta="NO_MATCH", issues=["x"]), B1_SOURCE)}
        back = {"ran": True, **t.check_review_v2(review_obj(verdict="SUPPORTED", ta="MATCH", issues=[]), B1_SOURCE)}
        d = t.reconcile(jev, {"adversarial": adv, "backward": back}, t.NO_TEMPLATE)
        self.assertEqual(d["disposition"], "HOLD_UNRESOLVED")
        self.assertIn("UNKNOWN_NO_TEMPLATE", d["reasons"])
        self.assertIn("REVIEWERS_INCOMPATIBLE", d["reasons"])
        self.assertEqual(d["approval"], "NOT_AUTHORIZED")

    def test_invalid_jev_model_id_means_not_run(self):
        options = list(LIB0["templates"]) + [t.NO_TEMPLATE]
        jev = t.parse_jev_v2(self.jev_raw(options, "DEFINITION", model=None), options)
        self.assertFalse(jev["valid"])
        self.assertEqual(t.reconcile(jev, {}, None)["status"], "NOT_RUN")

    def test_scoring_counts_recovered_anchor_only_and_copied_numeric_wrong_transfer(self):
        entry = CHECKLIST["packets"]["B1"]
        slots = [{"slot": "measurement_period", "value": "monthly billing cycle", "quote": "during a monthly billing cycle", "found_by": "adversarial"},
                 {"slot": "deadline", "value": "x", "quote": "100%, minus the average of Error Rates", "found_by": "backward"},
                 {"slot": "threshold", "value": "5% error rate in a given minute (as in GitHub)", "quote": "represented as a percentage", "found_by": "backward"}]
        decision = {"status": "RUN", "disposition": "HOLD_UNRESOLVED", "reasons": ["x"],
                    "extraction": {"template": "X", "slots": slots, "omitted_conditions": [{"description": "d", "quote": "Back-off Requirements", "found_by": "adversarial"}],
                                   "cross_references": [{"name": "Documentation", "quote": "conform to the Documentation", "resolved_in_packet": False}], "wrong_transfer_risks": []}}
        s = t.score_condition(decision, entry)
        self.assertEqual(s["recovered"], ["B1.E3"])
        self.assertEqual(s["anchor_only"], ["B1.E1"])
        self.assertEqual(len(s["critical_wrong_transfers"]), 1)
        self.assertEqual(s["unresolved_refs_found"], ["Documentation"])
        self.assertEqual(s["human_adjudication"], "PENDING")

    def test_decision_rule_requires_all_conditions_and_blocks_otherwise(self):
        rows = [{"packet_id": "B1", "conditions": {c: {"scorable": c != "WARM_RAW_A_B", "recovered": ["B1.E1"]} for c in t.CONDITIONS + (t.BLIND,)}}]
        totals = {c: {"run": 0 if c == "WARM_RAW_A_B" else 1, "recovered": 1, "denominator": 9, "critical_wrong": 0} for c in t.CONDITIONS + (t.BLIND,)}
        self.assertEqual(t.apply_decision_rule(rows, totals)["verdict"], "INCONCLUSIVE_OR_BLOCKED")
        rows = [{"packet_id": "B1", "conditions": {"COLD_B": {"scorable": True, "recovered": ["B1.E1"]}, "WARM_LIBRARY_B": {"scorable": True, "recovered": ["B1.E1", "B1.E2", "B1.E3"]},
                                                   "WARM_RAW_A_B": {"scorable": True, "recovered": ["B1.E1", "B1.E2"]}, t.BLIND: {"scorable": True, "recovered": ["B1.E1"]}}}]
        totals = {"COLD_B": {"run": 1, "recovered": 1, "denominator": 9, "critical_wrong": 0}, "WARM_LIBRARY_B": {"run": 1, "recovered": 3, "denominator": 9, "critical_wrong": 0},
                  "WARM_RAW_A_B": {"run": 1, "recovered": 2, "denominator": 9, "critical_wrong": 0}, t.BLIND: {"run": 1, "recovered": 1, "denominator": 9, "critical_wrong": 0}}
        d = t.apply_decision_rule(rows, totals)
        self.assertEqual(d["verdict"], "PROMISING_TRANSFER_PROVISIONAL")
        self.assertEqual(d["warm_only_vs_raw"], ["B1.E3"])
        totals["WARM_LIBRARY_B"]["critical_wrong"] = 1
        self.assertEqual(t.apply_decision_rule(rows, totals)["verdict"], "NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE")


class LiveReplayPlumbingTests(unittest.TestCase):
    """Mocked transport through run_live -> replay -> score. LAB_FIXTURE: proves plumbing and chronology only."""

    def test_live_replay_score_with_mocked_transport_and_budget(self):
        a = fixture_a_evidence()
        lib1, _ = t.induce_library(LIB0, a, created_at="2026-10-13T00:00:00Z")
        calls = {"jev": 0, "llm": 0}

        class FakeResponse:
            def __init__(self, body):
                self._raw = json.dumps(body).encode()
                self.status, self.headers = 200, {}

            def read(self):
                return self._raw

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake(req, timeout):
            body = json.loads(req.data)
            if req.full_url == p.JEV_URL:
                calls["jev"] += 1
                options = list(body["questions"]["template"]["criteria"])
                choice = "TIERED_SERVICE_CREDIT_SCHEDULE" if "TIERED_SERVICE_CREDIT_SCHEDULE" in options else "DEFINITION"
                return FakeResponse(ReconcileAndScoreTests().jev_raw(options, choice))
            calls["llm"] += 1
            prompt = body["messages"][0]["content"]
            src = next(c for c in B_CORPUS["clauses"] if c["text"] in prompt)
            quote = src["text"].split("\n")[0][:40]
            out = review_obj(slots=[{"slot": "normative_action", "value": "v", "quote": quote}],
                             ta="NO_TEMPLATE_AVAILABLE" if "No template library is available" in prompt else "MATCH")
            return FakeResponse({"id": "m", "model": p.DEFAULT_LLM_MODEL, "stop_reason": "end_turn",
                                 "content": [{"type": "text", "text": json.dumps(out)}], "usage": {"input_tokens": 5, "output_tokens": 5}})

        with tempfile.TemporaryDirectory() as tmp:
            lib1_path = Path(tmp) / "library_v1.json"
            t.write_json(lib1_path, lib1)
            out = Path(tmp) / "live.json"
            args = t.main.__globals__["argparse"].Namespace(a_recording=None, reviewer="anthropic", model=p.DEFAULT_LLM_MODEL, effort="medium",
                                                                library_synthesis=False, jev_model="jev-latest", max_provider_calls=31, max_attempts=93)
            with patch.dict(t.FILES, {"lib1": lib1_path}), patch.object(t, "load_a_evidence", return_value=a), patch.object(t, "find_a_recording", return_value=Path("x")):
                with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test", "ANTHROPIC_API_KEY": "test", "CLAUDECODE": ""}):
                    with patch.object(t, "preflight", return_value={"blockers": [], "hashes": {"a_corpus": p.digest(A_CORPUS), "b_corpus": p.digest(B_CORPUS), "library_v0": p.digest(LIB0), "library_v1": p.digest(lib1)}, "planned_calls": t._planned_calls(False)}):
                        with patch.object(p.urllib.request, "urlopen", side_effect=fake):
                            result = t.run_live(args, out)
            self.assertEqual(calls, {"jev": 9, "llm": 21})
            self.assertEqual(result["budget"]["logical_calls"], 30)
            self.assertLessEqual(result["budget"]["http_attempts"], 93)
            recorded = t.read_json(out)
            with patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("network in replay")):
                replayed = t.replay(recorded, B_CORPUS, LIB0, lib1)
            for ev in replayed["evaluation"]:
                self.assertEqual(ev["conditions"]["COLD_B"]["provenance"]["jev"], "RECORDED_ACTUAL")
                self.assertEqual(ev["conditions"]["WARM_LIBRARY_B"]["decision"]["extraction"]["template"], "TIERED_SERVICE_CREDIT_SCHEDULE")
                self.assertNotEqual(ev["conditions"]["COLD_B"]["decision"]["extraction"]["template"], "TIERED_SERVICE_CREDIT_SCHEDULE")
            edited_lib = copy.deepcopy(lib1)
            edited_lib["templates"]["DEFINITION"]["definition"] += " edited"
            with self.assertRaises(ValueError):
                t.replay(recorded, B_CORPUS, LIB0, edited_lib)
            score = t.score_result(replayed, CHECKLIST)
            self.assertEqual(score["per_condition_totals"]["COLD_B"]["run"], 3)
            self.assertIn(score["decision"]["verdict"], ("NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE", "PROMISING_TRANSFER_PROVISIONAL"))
            self.assertIn("### ", t.score_markdown(score, t.attribution(replayed, score, lib1)))

    def test_budget_stops_before_exceeding_attempt_cap(self):
        b = t.CallBudget(31, 5)
        b.record(3, True)
        with self.assertRaises(t.Blocked):
            b.check()

    def test_preflight_inside_claude_code_without_keys_reports_blockers_and_no_network(self):
        args = t.main.__globals__["argparse"].Namespace(a_recording=None, reviewer="anthropic", model=p.DEFAULT_LLM_MODEL, effort="medium",
                                                            library_synthesis=False, jev_model="jev-latest", max_provider_calls=31, max_attempts=93)
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "", "ANTHROPIC_API_KEY": ""}):
            with patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("network")):
                rep = t.preflight(args)
        self.assertFalse(rep["ready"])
        self.assertTrue(any(b.startswith("NO_TYPESAFE_API_KEY") for b in rep["blockers"]))
        self.assertEqual(rep["planned_calls"]["total_logical"], 30)
        self.assertEqual(rep["caps"]["logical_call_cap"], 31)

    def test_live_refuses_without_allow_flag(self):
        import contextlib
        import io
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            t.main(["--mode", "live", "--output", os.devnull])


if __name__ == "__main__":
    unittest.main()
