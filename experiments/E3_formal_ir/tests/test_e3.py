"""E3 tests (C6). test_frozen_scenarios re-checks the 54 frozen expectations; the other tests are post-freeze
robustness checks (labelled as such in RESULTS.md): purity, schema strictness and fail-closed single mutations of the
three positive scenarios."""
import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import models as M  # noqa: E402
import run_scenarios as rs  # noqa: E402
import validator as val  # noqa: E402

CTX = rs.context()
SC = {s["scenario_id"]: s for s in rs.load(rs.E3 / "cases" / "SCENARIOS.json")["scenarios"]}
APP = rs.load_dir(rs.E3 / "cases" / "approvals")
POSITIVES = ["S1_T1_POSITIVE", "S2_T4_APPROVED_CUSTOMER", "S3_T7_EQUIVALENCE_APPROVED"]


def run(sid, ctx=CTX, approvals=None, record=None, at=None):
    s = SC[sid]
    rec = record if record is not None else rs.apply_patch(rs.load(rs.E3 / "cases" / "records" / f"{s['record']}.json"), s["record_patch"])
    aps = [APP[a] for a in (s["approvals"] if approvals is None else approvals)]
    return val.validate(rec, aps, [APP[r] for r in s["revocations"]], ctx, at or s["eval_known_at"], s["eval_effective_at"])


def test_frozen_scenarios():
    res = rs.run(CTX)
    assert len(res) == 54
    assert [r["scenario_id"] for r in res if not r["passed"]] == []


def test_positive_scenarios_verified():
    for sid in POSITIVES:
        assert run(sid)["status"] == M.STATUSES[4]


def test_validator_is_pure_and_deterministic():
    s = SC["S2_T4_APPROVED_CUSTOMER"]
    rec = rs.load(rs.E3 / "cases" / "records" / "S2.json")
    before = copy.deepcopy(rec)
    a, b = run("S2_T4_APPROVED_CUSTOMER", record=rec), run("S2_T4_APPROVED_CUSTOMER", record=rec)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) and rec == before and s["approvals"] == ["AP_S2_CUSTOMER"]


def test_schema_rejects_unknown_fields_and_exports():
    rec = rs.load(rs.E3 / "cases" / "records" / "S1.json")
    with pytest.raises(Exception):
        M.Record.model_validate({**rec, "extra_note": "x"})
    schema = M.Record.model_json_schema()
    assert "status" not in schema["properties"] and schema.get("additionalProperties") is False


@pytest.mark.parametrize("sid", POSITIVES)
def test_dropping_any_single_approval_fails_closed(sid):
    for a in SC[sid]["approvals"]:
        rest = [x for x in SC[sid]["approvals"] if x != a]
        assert run(sid, approvals=rest)["status"] != M.STATUSES[4], a


@pytest.mark.parametrize("sid", POSITIVES)
def test_missing_receipts_fail_closed(sid):
    for field in ("native", "oracle", "guards"):
        ctx = val.Context(**{**CTX.__dict__, field: {}})
        res = run(sid, ctx=ctx)
        if field == "guards" and sid != "S1_T1_POSITIVE":
            continue  # only S1 has a derived binding
        assert res["status"] == M.STATUSES[3], (sid, field, res["reasons"])


@pytest.mark.parametrize("sid", POSITIVES)
def test_any_binding_replaced_by_missing_is_never_verified(sid):
    base = rs.apply_patch(rs.load(rs.E3 / "cases" / "records" / f"{SC[sid]['record']}.json"), SC[sid]["record_patch"])
    for ri, r in enumerate(base["interpretation"]["readings"]):
        for aid in r["bindings"]:
            rec = copy.deepcopy(base)
            rec["interpretation"]["readings"][ri]["bindings"][aid] = {"kind": "MISSING", "semantic_object": None,
                                                                        "physical_lineage": [], "missing_fact": "x"}
            assert run(sid, record=rec)["status"] != M.STATUSES[4], (sid, aid)


@pytest.mark.parametrize("sid", POSITIVES)
def test_evaluation_before_approvals_known_is_not_verified(sid):
    assert run(sid, at="2026-10-05T09:59:59Z")["status"] == M.STATUSES[2]
