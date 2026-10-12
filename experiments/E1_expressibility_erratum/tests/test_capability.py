import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import capability as cap  # noqa: E402


def ok_evidence(**over):
    ev = {"source_column_present": True, "direct_dimension_present": False, "native_witness_accepted": True,
          "native_equals_oracle_yearly": True, "native_equals_oracle_lines": True,
          "guards": {g: True for g in cap.GUARDS}}
    ev.update(over)
    return ev


def test_all_guards_hold_is_derivable():
    assert cap.classify(ok_evidence()) == {"classification": cap.DERIVABLE, "failed": []}


def test_each_failed_guard_refuses_derivation():
    for g in cap.GUARDS:
        for bad in (False, None):
            r = cap.classify(ok_evidence(guards={**{x: True for x in cap.GUARDS}, g: bad}))
            assert r["classification"] == cap.UNSUPPORTED and r["failed"] == [g]


def test_missing_guard_record_refuses():
    assert cap.classify(ok_evidence(guards={}))["classification"] == cap.UNSUPPORTED


def test_native_rejection_or_mismatch_refuses():
    for k in ("native_witness_accepted", "native_equals_oracle_yearly", "native_equals_oracle_lines"):
        r = cap.classify(ok_evidence(**{k: False}))
        assert r["classification"] == cap.UNSUPPORTED and k in r["failed"]


def test_direct_dimension_wins_and_no_source_is_not_found():
    assert cap.classify(ok_evidence(direct_dimension_present=True))["classification"] == cap.DIRECTLY_EXPOSED
    assert cap.classify(ok_evidence(source_column_present=False))["classification"] == cap.NOT_FOUND
