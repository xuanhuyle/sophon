"""V1 adapter, replay and comparison tests. All offline: every provider response here is a
LAB_FIXTURE shaped like the official schema, used only to exercise code paths."""
import contextlib
import copy
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("prototype", HERE / "prototype.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
sys.modules["prototype"] = p
import compare  # noqa: E402

PROBS = {"OBLIGATION": 0.05, "PROHIBITION": 0.02, "PERMISSION_RIGHT": 0.85, "DEFINITION": 0.04,
         "AUTHORITY": 0.02, "OTHER": 0.02}


def jev_body(primary="PERMISSION_RIGHT", probs=None, mods=None, model="jev-1.13.0", reversed_choice=None,
             usage=True):
    probs = probs or PROBS
    mods = mods or {"THRESHOLD": 0.9, "EXCLUSION": 0.1, "CONDITION": 0.8, "DEADLINE": 0.2, "CROSS_REFERENCE": 0.1}
    answers = {"primary": {"type": "choice", "choice": primary, "probabilities": probs, "confidence": 0.7}}
    rev_probs = probs if not reversed_choice else {k: (0.9 if k == reversed_choice else 0.02) for k in probs}
    answers["primary_reversed"] = {"type": "choice", "choice": reversed_choice or primary, "probabilities": rev_probs,
                                   "confidence": 0.7}
    answers.update({k: {"type": "noul", "noul": v} for k, v in mods.items()})
    body = {"answers": answers}
    if model:
        body["model"] = model
    if usage:
        body["usage"] = {"input_tokens": 400, "output_tokens": 30}
    return body


def review_text(verdict="SUPPORTED", missing=(), quotes=("may claim a service credit",), issues=(), refs=()):
    return json.dumps({"verdict": verdict, "missing_modifiers": list(missing), "evidence_quotes": list(quotes),
                       "issues": list(issues), "missing_source_refs": list(refs)})


def baseline_text(types=("PERMISSION_RIGHT",), mods=("THRESHOLD", "CONDITION", "DEADLINE"),
                  quotes=("within 30 days after month-end",), refs=(), complete=True):
    return json.dumps({"primary_types": list(types), "modifiers": list(mods), "evidence_quotes": list(quotes),
                       "issues": ["written claim needed within 30 days"], "unresolved_refs": list(refs),
                       "complete_from_packet": complete})


class FakeResponse:
    def __init__(self, body, status=200, headers=None):
        self._raw = json.dumps(body).encode() if not isinstance(body, bytes) else body
        self.status, self.headers = status, headers or {}

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def http_error(code, body=b"{}", headers=None):
    return urllib.error.HTTPError("https://x", code, "err", headers or {}, io.BytesIO(body))


class JevSchemaTests(unittest.TestCase):
    def test_official_shape_parses_and_records_versioned_model(self):
        r = p.parse_jev_response(jev_body())
        self.assertTrue(r["valid"])
        self.assertEqual(r["model_id"], "jev-1.13.0")
        self.assertEqual(r["proposal"]["primary"], "PERMISSION_RIGHT")
        self.assertEqual(r["flags"], [])

    def test_missing_model_id_is_invalid_not_replaced_by_alias(self):
        # V0 fell back to the requested alias 'jev-latest'; the response's model field is required.
        r = p.parse_jev_response(jev_body(model=None))
        self.assertFalse(r["valid"])
        self.assertIn("response missing the versioned model ID", r["errors"])

    def test_missing_usage_is_invalid(self):
        self.assertFalse(p.parse_jev_response(jev_body(usage=False))["valid"])

    def test_near_tie_inconsistency_keeps_provider_label_and_flags_it(self):
        probs = dict(PROBS, PERMISSION_RIGHT=0.445, OBLIGATION=0.455, DEFINITION=0.04, PROHIBITION=0.02,
                     AUTHORITY=0.02, OTHER=0.02)
        raw = jev_body(primary="PERMISSION_RIGHT", probs=probs)
        untouched = copy.deepcopy(raw)
        r = p.parse_jev_response(raw)
        self.assertTrue(r["valid"])
        self.assertEqual(r["proposal"]["primary"], "PERMISSION_RIGHT")  # not silently swapped
        self.assertEqual(r["proposal"]["probabilities"]["OBLIGATION"], 0.455)  # no invented probability
        self.assertTrue(any(f.startswith("PROVIDER_CHOICE_PROBABILITY_INCONSISTENT_NEAR_TIE") for f in r["flags"]))
        self.assertEqual(raw, untouched)

    def test_large_choice_contradiction_is_invalid(self):
        r = p.parse_jev_response(jev_body(primary="OTHER"))
        self.assertFalse(r["valid"])

    def test_option_order_sensitivity_is_flagged(self):
        r = p.parse_jev_response(jev_body(reversed_choice="OTHER"))
        self.assertTrue(any(f.startswith("JEV_OPTION_ORDER_SENSITIVE") for f in r["flags"]))

    def test_out_of_range_noul_is_invalid(self):
        body = jev_body()
        body["answers"]["DEADLINE"]["noul"] = 1.2
        self.assertFalse(p.parse_jev_response(body)["valid"])

    def test_request_uses_official_fields_and_structured_state(self):
        req = p.jev_request({"text": "T", "context": "C"}, "jev-latest")
        self.assertEqual(set(req), {"model", "state", "questions"})
        self.assertEqual(req["state"], {"clause": "T", "context": "C"})
        self.assertEqual(list(req["questions"]["primary_reversed"]["criteria"]),
                         list(reversed(list(req["questions"]["primary"]["criteria"]))))
        self.assertEqual(p.jev_request({"text": "T"}, "jev-latest")["state"], "T")


class TransportTests(unittest.TestCase):
    def test_429_retried_with_retry_after_then_succeeds(self):
        sleeps = []
        calls = [http_error(429, headers={"retry-after": "2"}), FakeResponse({"ok": 1})]

        def fake(req, timeout):
            item = calls.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        with patch.object(p.urllib.request, "urlopen", side_effect=fake):
            body, meta = p.post_json("https://x", {}, {}, provider="t", sleep=sleeps.append)
        self.assertEqual(body, {"ok": 1})
        self.assertEqual(meta["attempts"], 2)
        self.assertEqual(sleeps, [2.0])

    def test_401_not_retried(self):
        with patch.object(p.urllib.request, "urlopen", side_effect=http_error(401)) as m:
            with self.assertRaises(p.ProviderError) as ctx:
                p.post_json("https://x", {}, {}, provider="t", sleep=lambda s: None)
        self.assertEqual(ctx.exception.status, 401)
        self.assertEqual(m.call_count, 1)

    def test_529_exhausts_bounded_retries(self):
        with patch.object(p.urllib.request, "urlopen", side_effect=lambda *a, **k: (_ for _ in ()).throw(http_error(529))) as m:
            with self.assertRaises(p.ProviderError):
                p.post_json("https://x", {}, {}, provider="t", sleep=lambda s: None)
        self.assertEqual(m.call_count, 3)

    def test_anthropic_request_has_no_temperature_and_refusal_is_error(self):
        sent = {}

        def fake(req, timeout):
            sent.update(json.loads(req.data))
            return FakeResponse({"id": "msg_1", "model": "claude-opus-5-5", "stop_reason": "refusal",
                                 "content": [], "usage": {"input_tokens": 1, "output_tokens": 0}})
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-not-a-key"}):
            with patch.object(p.urllib.request, "urlopen", side_effect=fake):
                with self.assertRaises(p.ProviderError):
                    p.call_anthropic("prompt", p.DEFAULT_LLM_MODEL)
        self.assertNotIn("temperature", sent)
        self.assertEqual(sent["model"], "claude-opus-5-5")

    def test_cli_reviewer_refuses_inside_claude_code_without_spawning(self):
        with patch.dict(os.environ, {"CLAUDECODE": "1"}):
            with patch.object(p.subprocess, "run", side_effect=AssertionError("spawned")):
                with self.assertRaises(p.ReadinessBlocked):
                    p.call_claude_cli("prompt", "opus")

    def test_preflight_reports_blockers_without_network(self):
        corpus = p.read_json(HERE / "clauses.json")
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "", "ANTHROPIC_API_KEY": ""}):
            with patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("network")):
                rep = p.preflight([corpus], "anthropic", p.DEFAULT_LLM_MODEL, 20)
        self.assertFalse(rep["ready"])
        self.assertEqual(rep["plans"]["LAB-SLA-5"]["calls"]["total"], 20)
        self.assertFalse(rep["credentials_present"]["TYPESAFE_API_KEY"])

    def test_live_cli_refuses_without_allow_flag(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            p.main(["--mode", "live", "--output", os.devnull])


class DecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = p.read_json(HERE / "clauses.json")
        cls.c3 = cls.corpus["clauses"][2]

    def record(self, jev, adv, back, blind):
        steps = {"jev": {"provenance": "LAB_FIXTURE", "raw_response": jev}}
        for name, text in (("adversarial", adv), ("backward", back), ("blind", blind)):
            steps[name] = {"provenance": "LAB_FIXTURE", "raw_text": text}
        return {"clause_id": "C3", "source_sha256": p.sha256_text(p.anchor_source(self.c3)), "steps": steps}

    def test_reviewer_condition_kept_when_jev_scores_below_threshold(self):
        rec = self.record(jev_body(), review_text("DISPUTED", ["DEADLINE"], ["within 30 days after month-end"], ["claim window"]),
                          review_text(), baseline_text())
        arms = p.evaluate_record(rec, self.corpus)["arms"]
        self.assertEqual(arms["A_jev_only"]["disposition"], "CANDIDATE_FOR_HUMAN_REVIEW")
        self.assertNotIn("DEADLINE", arms["A_jev_only"]["detected_modifiers"])
        c = arms["C_jev_adversarial_backward"]
        self.assertIn("DEADLINE", c["detected_modifiers"])
        self.assertEqual(c["disposition"], "HOLD_UNRESOLVED")
        self.assertIn("REVIEWERS_INCOMPATIBLE", c["reasons"])
        self.assertEqual(c["suggested_transposition"]["route"], "ENTITLEMENT_WITH_CLAIM_DEADLINE")
        self.assertEqual(c["approval"], "NOT_AUTHORIZED")

    def test_unanchored_live_review_holds_instead_of_crashing(self):
        rec = self.record(jev_body(), review_text(quotes=["NOT IN THE CLAUSE"]), review_text(), baseline_text())
        b = p.evaluate_record(rec, self.corpus)["arms"]["B_jev_adversarial"]
        self.assertEqual(b["disposition"], "HOLD_UNRESOLVED")
        self.assertTrue(any(r.startswith("REVIEW_INVALID_ADVERSARIAL") for r in b["reasons"]))

    def test_invalid_jev_means_abc_not_run_but_blind_still_scored(self):
        rec = self.record(jev_body(model=None), review_text(), review_text(), baseline_text())
        arms = p.evaluate_record(rec, self.corpus)["arms"]
        for arm in ("A_jev_only", "B_jev_adversarial", "C_jev_adversarial_backward"):
            self.assertEqual(arms[arm]["disposition"], "NOT_RUN")
        self.assertEqual(arms["D_blind_llm"]["status"], "RUN")

    def test_near_tie_holds_every_jev_arm(self):
        probs = dict(PROBS, PERMISSION_RIGHT=0.445, OBLIGATION=0.455)
        rec = self.record(jev_body(probs=probs), review_text(), review_text(), baseline_text())
        arms = p.evaluate_record(rec, self.corpus)["arms"]
        for arm in ("A_jev_only", "B_jev_adversarial", "C_jev_adversarial_backward"):
            self.assertEqual(arms[arm]["disposition"], "HOLD_UNRESOLVED")

    def test_curly_quotes_anchor_against_straight_quotes(self):
        self.assertTrue(p.anchored('"Downtime" is a period', "“Downtime” is a period of time"))
        self.assertFalse(p.anchored("Uptime is a period", "“Downtime” is a period of time"))

    def test_record_from_edited_source_is_refused(self):
        rec = self.record(jev_body(), review_text(), review_text(), baseline_text())
        rec["source_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            p.evaluate_record(rec, self.corpus)


class LiveReplayCompareTests(unittest.TestCase):
    """Exercises run_live -> replay -> compare with mocked transport. Not evidence of anything."""

    def test_live_then_replay_then_compare(self):
        corpus = p.read_json(HERE / "clauses.json")
        texts = {c["text"]: c["id"] for c in corpus["clauses"]}

        def fake(req, timeout):
            body = json.loads(req.data)
            if req.full_url == p.JEV_URL:
                cid = texts[body["state"]]
                prim = {"C1": "OBLIGATION", "C2": "DEFINITION", "C3": "PERMISSION_RIGHT", "C4": "PROHIBITION",
                        "C5": "AUTHORITY"}[cid]
                probs = {k: (0.9 if k == prim else 0.02) for k in p.PRIMARIES}
                return FakeResponse(jev_body(prim, probs))
            prompt = body["messages"][0]["content"]
            text = next(t for t in texts if t in prompt)
            quote = text.split()[0] + " " + text.split()[1]
            if "contractual-structure analyst" in prompt:
                out = baseline_text(quotes=[quote])
            else:
                out = review_text(quotes=[quote])
            return FakeResponse({"id": "msg_x", "model": "claude-opus-5-5", "stop_reason": "end_turn",
                                 "content": [{"type": "text", "text": out}],
                                 "usage": {"input_tokens": 900, "output_tokens": 200}})
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "live.json"
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test", "ANTHROPIC_API_KEY": "test"}):
                with patch.object(p.urllib.request, "urlopen", side_effect=fake) as m:
                    live = p.run_live(corpus, output=out, jev_model="jev-latest", engine="anthropic",
                                      adversarial_model=p.DEFAULT_LLM_MODEL, backward_model=p.DEFAULT_LLM_MODEL,
                                      baseline_model=p.DEFAULT_LLM_MODEL, effort="medium", order_check=True,
                                      max_calls=20)
            self.assertEqual(m.call_count, 20)
            recorded = p.read_json(out)
            with patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("network in replay")):
                replayed = p.replay(recorded, corpus)
            for a, b in zip(live["evaluation"], replayed["evaluation"]):
                self.assertEqual({k: v["disposition"] for k, v in a["arms"].items()},
                                 {k: v["disposition"] for k, v in b["arms"].items()})
                self.assertEqual(b["provenance"]["jev"], "RECORDED_ACTUAL")
            edited = copy.deepcopy(corpus)
            edited["clauses"][0]["text"] += " (edited)"
            with self.assertRaises(ValueError):
                p.replay(recorded, edited)
            report = compare.compare(replayed, p.read_json(HERE / "review_matrix.json"))
            totals = report["per_arm_totals"]["A_jev_only"]
            self.assertEqual(totals["run"], 5)
            # Jev-alone scored candidates despite missing required modifiers (e.g. C3 DEADLINE): the key error kind.
            self.assertGreater(totals["candidate_with_missed_required"], 0)
            self.assertEqual(report["overhead"]["jev"]["calls_ok"], 5)

    def test_call_cap_enforced_before_any_call(self):
        corpus = p.read_json(HERE / "clauses.json")
        with patch.object(p.urllib.request, "urlopen", side_effect=AssertionError("network")):
            with self.assertRaises(p.ReadinessBlocked):
                p.run_live(corpus, output=Path(os.devnull), jev_model="j", engine="anthropic", adversarial_model="m",
                           backward_model="m", baseline_model="m", effort=None, order_check=True, max_calls=19)


class FrozenSourceTests(unittest.TestCase):
    def test_external_corpus_hashes_and_matrix_anchors(self):
        ext = p.read_json(HERE / "external_github_sla_2021.json")
        p.check_clause_file(ext)  # verifies every excerpt_sha256
        lab = p.read_json(HERE / "clauses.json")
        texts = {c["id"]: c["text"] for c in lab["clauses"] + ext["clauses"]}
        matrix = p.read_json(HERE / "review_matrix.json")
        self.assertEqual(set(matrix["clauses"]), set(texts))
        for cid, entry in matrix["clauses"].items():
            for mc in entry["material_conditions"]:
                self.assertIn(mc["anchor"], texts[cid], mc["id"])

    def test_edited_external_excerpt_is_detected(self):
        ext = p.read_json(HERE / "external_github_sla_2021.json")
        ext["clauses"][3]["text"] = ext["clauses"][3]["text"].replace("thirty (30)", "sixty (60)")
        with self.assertRaises(ValueError):
            p.check_clause_file(ext)


if __name__ == "__main__":
    unittest.main()
