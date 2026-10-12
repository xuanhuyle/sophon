"""E1 tests (PROTOCOL.md section 4, E1 prompt section 6). They re-execute everything live (native MetricFlow via the
E0 adapter, DuckDB read-only, oracle on raw CSVs) independently of the recorded evidence, and compare behaviour to
EXPECTED.json. Run after the warehouse is built:

    .upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e1_binding.py
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

E1 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E1 / "src"))
import evaluator as ev  # noqa: E402
import run_e1  # noqa: E402

UP = E1 / ".upstream"
EXPECTED = json.loads((E1 / "EXPECTED.json").read_text(encoding="utf-8"))
FROZEN = json.loads((E1 / "FROZEN_CASES.json").read_text(encoding="utf-8"))
pytestmark = pytest.mark.skipif(not (UP / "dbt/retail_dwh/target/semantic_manifest.json").exists(), reason="build the warehouse first")


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    return run_e1.run_all(UP, tmp_path_factory.mktemp("scratch"))


def statuses(r):
    return {k: v["status"] for k, v in r["predicates"].items()}


# 1 A positive
def test_1_case_A_fully_observable_and_native_equals_oracle(run):
    r = run["scored"]["A"]["result"]
    e = EXPECTED["cases"]["A"]
    assert r["case_status"] == e["case_status"] and r["verified_for_recorded_checks"] is True
    assert statuses(r) == e["predicates"]
    assert r["comparison"]["equal"] and r["oracle"]["own_equals_e0_crosscheck"]
    assert r["native"]["ok"] and r["native"]["exit_code"] == 0


# 2 B1 present in source, not exposed
def test_2_case_B1_present_not_exposed_with_native_probe_rejected(run):
    r = run["scored"]["B1"]["result"]
    p = r["predicates"]["P_UNIT_PRICE_GE_100"]
    assert r["case_status"] == "PRESENT_IN_SOURCE_NOT_EXPOSED" and r["verified_for_recorded_checks"] is False
    assert statuses(r) == EXPECTED["cases"]["B1"]["predicates"]
    assert p["physical_present"] and p["in_native_dimension_list"] is False and p["catalog_scan_exposing_physical_column"] == []
    assert p["native_exposure_probe"]["accepted"] is False and p["native_exposure_probe"]["exit_code"] != 0
    assert r["uncovered"] == ["P_UNIT_PRICE_GE_100"]


# 3 B2 not found in bounded estate
def test_3_case_B2_not_found_in_bounded_estate(run):
    r = run["scored"]["B2"]["result"]
    p = r["predicates"]["P_SETTLEMENT_CONFIRMED"]
    assert r["case_status"] == "NOT_FOUND_IN_BOUNDED_ESTATE" and not r["verified_for_recorded_checks"]
    assert p["designated_fields"] == [] and "not a claim of absence elsewhere" in p["reason"]
    assert r["estate_fingerprint"]["equal"]


# 4-7 adversarial variants: none reaches full observability; each matches its frozen expectation
@pytest.mark.parametrize("vid", [k for k, v in EXPECTED["adversarial"].items() if "case_status" in v])
def test_4_to_7_adversarial_variants(run, vid):
    e = EXPECTED["adversarial"][vid]
    r = run["adversarial"][vid]["result"]
    assert r["verified_for_recorded_checks"] is False
    assert r["case_status"] != "FULLY_OBSERVABLE_FOR_THIS_CALCULATION"
    assert r["case_status"] == e["case_status"]
    if "predicate" in e:
        assert r["predicates"][e["predicate"][0]]["status"] == e["predicate"][1]


def test_5_predicate_addition_keeps_same_native_number_but_withdraws_verification(run):
    a = run["adversarial"]["M5_settlement_predicate_added_to_A"]
    assert a["covered_native_equals_A_native"] is True
    assert a["result"]["case_status"] != "FULLY_OBSERVABLE_FOR_THIS_CALCULATION"


def test_7_identity_drift_changes_native_result_and_invalidates_binding(run):
    a = run["adversarial"]["M7_native_identity_drift"]
    assert a["edits_applied"] == 1 and a["drifted_native_differs_from_A_native"] is True
    assert a["result"]["case_status"] == "INVALID_BINDING"


# 8 oracle sanity
def test_8_oracle_rejects_altered_native_and_altered_input(run):
    assert run["adversarial"]["M8a_altered_native_amount"]["comparison_rejects"] is True
    m = run["adversarial"]["M8b_altered_oracle_input"]
    assert m["comparison_rejects"] is True and m["oracle_delta_equals_line_unit_price"] is True


# diagnostic: the authority registry, not the case, drives the result
def test_registry_drives_classification(run):
    fz = copy.deepcopy(FROZEN)
    fz["authority_registry"]["order_status_label"] = []
    r = ev.evaluate_case(FROZEN["cases"]["A"], fz, ev.LiveContext(ev.mfa.open_project(UP)))
    assert r["predicates"]["P_STATUS_COMPLETED"]["status"] == "NOT_AUTHORITATIVE_FOR_FACT"
    assert r["verified_for_recorded_checks"] is False


# 9 fresh-process replay of the committed evidence
def test_9_fresh_process_replay_of_committed_evidence(tmp_path):
    out = tmp_path / "replay.json"
    proc = subprocess.run([sys.executable, str(E1 / "src" / "replay.py"), "--evidence", str(E1 / "evidence" / "run"),
                           "--out", str(out), "--raw", str(UP / "data" / "raw")], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    rep = json.loads(out.read_text())
    assert rep["all_equal"] and all(rep["oracle_recomputed"].values())
