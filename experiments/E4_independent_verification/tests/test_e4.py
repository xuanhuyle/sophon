"""E4 unit tests (Q7). No candidate stacks are built here; native execution is exercised by src/checker.py."""
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import candidate_stack as cs  # noqa: E402
import checker  # noqa: E402
import reference as ref  # noqa: E402


def facts(status="completed", price="100.00", country="FR"):
    return {"status": status, "unit_price": price, "customer_country": ref.COUNTRY.get(country.strip().upper(), "Other")}


def test_p1_boundary_is_inclusive_and_status_exact():
    assert ref.eligible("P1", facts(price="100.00"))
    assert not ref.eligible("P1", facts(price="99.99"))
    assert ref.eligible("P1", facts(price="100.01"))
    assert not ref.eligible("P1", facts(status="returned", price="500"))


def test_p2_uses_customer_country_with_pinned_aliases():
    for raw in ("France", " france ", "FR", "FRA"):
        assert ref.eligible("P2", facts(country=raw))
    assert not ref.eligible("P2", facts(country="Belgique"))
    assert not ref.eligible("P2", facts(status="cancelled", country="France"))


def test_patch_anchor_must_be_unique(tmp_path):
    f = tmp_path / "a.yml"
    f.write_text("x\nx\n")
    with pytest.raises(ValueError):
        cs.apply_patch(tmp_path, [{"op": "replace", "file": "a.yml", "old": "x\n", "new": "y\n"}])
    f.write_text("x\n")
    d = cs.apply_patch(tmp_path, [{"op": "replace", "file": "a.yml", "old": "x\n", "new": "y\n"}])
    assert f.read_text() == "y\n" and d[0]["unified_diff"]


def test_authority_controls_without_execution():
    trusted = checker.json.loads((checker.EXP / "E3_1_integrity" / "cases" / "TRUSTED_MANIFEST.json").read_text())
    base = {"eval_known_at": "2026-10-06T00:00:00Z", "eval_effective_at": "2026-06-30", "record_patch": []}
    assert checker.authority("P2", {**base, "approvals": ["AP_S2_CUSTOMER"]}, trusted)[0] is None
    assert checker.authority("P2", {**base, "approvals": []}, trusted)[:2] == ("NOT_VERIFIED", ["APPROVAL_MISSING"])
    assert checker.authority("P2", {**base, "approvals": ["AP_S2_STORE"]}, trusted)[:2] == ("NOT_VERIFIED", ["APPROVAL_MISSING"])
    nif = {**base, "approvals": ["AP_S2_CUSTOMER"], "record_patch": [{"op": "set", "path": ["governing_source", "effective_from"], "value": "2027-01-01"}]}
    assert checker.authority("P2", nif, trusted)[:2] == ("NOT_APPLICABLE", ["REQUIREMENT_NOT_IN_FORCE"])


def test_checker_never_reads_expected():
    src = (Path(checker.__file__)).read_text()
    body = src.split("def main", 1)[0]
    assert '"expected"' not in body and "'expected'" not in body
