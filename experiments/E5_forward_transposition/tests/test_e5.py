"""E5 unit tests (no native builds): transposition from the IR, refusals, authority/time, lifecycle, oracle boundaries.

    .upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

E5 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E5 / "src"))
import authority  # noqa: E402
import claim  # noqa: E402
import lifecycle  # noqa: E402
import run_e5  # noqa: E402
import snapshots  # noqa: E402
import transposer  # noqa: E402

oracle = run_e5.oracle
PACKET = json.loads((E5 / "TRANSPOSE_PACKET.json").read_text())
MET = "dbt/retail_dwh/models/marts/semantic/_metrics.yml"
K_PRE, K_MID, K_POST = "2026-10-06T00:00:00Z", "2026-10-09T12:00:00Z", "2026-10-11T00:00:00Z"


def v2_threshold(pk: dict) -> str:
    return next(a["value"] for a in pk["requirement_versions"]["P1_v2"]["requirement"]["atoms"] if a["atom_id"] == "unit_price_threshold")


def test_meaning_hash_is_the_same_definition_in_transposer_and_authority():
    for v in ("P1_v1", "P1_v2"):
        ir = PACKET["requirement_versions"][v]
        assert transposer.meaning(ir) == claim.meaning_sha(ir)
    assert PACKET["approvals"]["AP_S1_V2"]["claim"]["normalized_claim_sha256"] == claim.meaning_sha(PACKET["requirement_versions"]["P1_v2"])


def test_transposer_edits_the_existing_p1_metric_in_place_and_leaves_p2():
    p = transposer.transpose(copy.deepcopy(PACKET))
    assert p["status"] == p["review_status"] == "PROPOSED_NOT_DEPLOYED" and p["deployment"] is None
    assert p["modified_metrics"] == ["premium_completed_revenue"] and len(p["patch"]) == 1 and p["patch"][0]["op"] == "replace"
    base = PACKET["native_baseline"]["files"][MET]
    new = base.replace(p["patch"][0]["old"], p["patch"][0]["new"])
    before, after = transposer.metric_blocks(base), transposer.metric_blocks(new)
    assert sorted(before) == sorted(after)
    assert all(before[m] == after[m] for m in before if m != "premium_completed_revenue")
    assert f">= {v2_threshold(PACKET)}\"" in after["premium_completed_revenue"]
    assert [x["metric"] for x in p["not_affected"]] == ["french_market_revenue"]


@pytest.mark.parametrize("value,text", [("135", "135"), ("99.5", "99.5"), ("120.00", None), ("1000", "1000")])
def test_emitted_threshold_follows_the_ir(value, text):
    p = transposer.transpose(run_e5.threshold_variant(PACKET, value, text))
    assert p["status"] == "PROPOSED_NOT_DEPLOYED"
    assert p["rendered"]["after"]["filter"].endswith(">= " + claim.canon_value(value))


def test_every_n1_mutation_is_refused_without_a_patch():
    for ctl in json.loads((E5 / "controls" / "N1_PACKET_MUTATIONS.json").read_text())["controls"]:
        with pytest.raises(transposer.Refusal) as ex:
            transposer.transpose(run_e5.mutate(PACKET, ctl))
        assert ex.value.status in ("BLOCKED", "UNRESOLVED"), ctl["control_id"]


def test_transposer_source_holds_no_answer_and_names_no_hidden_file():
    src = (E5 / "src" / "transposer.py").read_text()
    assert not re.search(r"(?<![\d.])120(?![\d])", src)
    assert not re.search(r"REFERENCE|SCENARIOS|oracle", src)
    assert "open(" in src and src.count("open(") == 2  # the packet in, the proposal out


def test_packet_carries_no_reference_or_expected_data():
    txt = (E5 / "TRANSPOSE_PACKET.json").read_text()
    for k in ("reference_results", '"expected"', "by_year", "lines_sha256", "discriminating_rows"):
        assert k not in txt


def test_runner_strips_expected():
    assert '"expected"' not in json.dumps(run_e5.strip_expected(json.loads((E5 / "SCENARIOS.json").read_text())))


def test_authority_states_governing_versions_and_no_future_leak():
    A = authority.Authority()
    assert {v: A.version_state(v, K_PRE)["state"] for v in authority.VERSIONS} == {"P1_v1": "LAB_APPROVED", "P1_v2": "NOT_KNOWN"}
    assert A.version_state("P1_v2", K_MID)["state"] == "NOT_APPROVED"
    assert A.version_state("P1_v2", K_POST)["state"] == "LAB_APPROVED"
    assert A.version_state("P1_v2", "2026-10-10T10:00:00Z")["state"] == "LAB_APPROVED"  # approval known exactly then
    assert A.version_state("P1_v2", "2026-10-10T09:59:59Z")["state"] == "NOT_APPROVED"
    for K in (K_PRE, K_MID):
        assert A.routing(K) == [{"window": ["2024-01-01", None], "version": "P1_v1"}]
    assert A.routing(K_POST) == [{"window": ["2024-01-01", "2025-01-01"], "version": "P1_v1"}, {"window": ["2025-01-01", None], "version": "P1_v2"}]
    assert A.governing("2024-12-31", K_POST)["version"] == "P1_v1" and A.governing("2025-01-01", K_POST)["version"] == "P1_v2"
    assert A.governing_window(None, None, K_POST)["reason"] == "WINDOW_SPANS_VERSIONS"


def test_authority_rejects_a_v2_approval_bound_to_another_meaning():
    aps = {"AP_S1_READ": json.loads((E5.parent / "E3_formal_ir" / "cases" / "approvals" / "AP_S1_READ.json").read_text()),
           "AP_S1_V2": copy.deepcopy(PACKET["approvals"]["AP_S1_V2"])}
    aps["AP_S1_V2"]["claim"]["normalized_claim_sha256"] = "0" * 64
    A = authority.Authority(approvals=aps)
    s = A.version_state("P1_v2", K_POST)
    assert s["state"] == "APPROVAL_INVALID" and "APPROVAL_MEANING_MISMATCH" in s["reasons"]
    assert A.governing("2025-06-01", K_POST)["version"] == "P1_v1"


def test_lifecycle_never_reaches_deployed():
    roster = json.loads((E5.parent / "E3_formal_ir" / "cases" / "roster.json").read_text())
    p = transposer.transpose(copy.deepcopy(PACKET))
    for ver in (None, {"status": "VERIFIED_FOR_LAB_CHECKS"}, {"status": "NONCONFORMING_IMPLEMENTATION"}):
        for forged in (None, "DEPLOYED", "IMPLEMENTED"):
            for dep in (None, {"approval_id": "AP_S1_V2"}):
                s = lifecycle.state(p, roster, verification=ver, forged_claimed_state=forged, deployment_authorization=dep,
                                    approvals={"AP_S1_V2": PACKET["approvals"]["AP_S1_V2"]})
                assert s["state"] in lifecycle.STATES and s["deployed"] is False
    assert lifecycle.state(None, roster)["state"] == "CHANGE_REQUIRED_NOT_PROPOSED"


def test_oracle_boundary_rows(tmp_path):
    snapshots.build(E5 / ".upstream" / "data" / "raw", tmp_path)
    L = oracle.order_lines(tmp_path / "BOUNDARY120")
    v1 = {k for k, f in L.items() if oracle.is_eligible("P1v1", f)}
    v2 = {k for k, f in L.items() if oracle.is_eligible("P1v2", f)}
    assert L["22"]["unit_price"] == "120.00" and "22" in v2
    assert L["21"]["unit_price"] == "119.99" and "21" in v1 and "21" not in v2
    assert L["15"]["unit_price"] == "100.00" and "15" in v1 and "15" not in v2
    assert L["2"]["unit_price"] == "99.99" and "2" not in v1
    assert L["19"]["status"] == "returned" and "19" not in v2 and L["11"]["status"] == "cancelled" and "11" not in v2
    assert L["58"]["order_date"] < "2025-01-01" and "58" in v1 and "58" not in v2
