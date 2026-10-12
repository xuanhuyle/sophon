"""Scorer negative controls: run before the solver; must pass. They exercise native re-execution on a disposable
warehouse copy.   .upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_scorer_controls.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

E2 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E2 / "src"))
import controls  # noqa: E402
import score  # noqa: E402

REF = json.loads((E2 / "REFERENCE.json").read_text(encoding="utf-8"))
UP = E2 / ".upstream"
MUT = controls.mutations(REF)
OUT = E2 / "evidence" / "scorer_controls"


@pytest.mark.parametrize("name", list(controls.EXPECTATIONS))
def test_control(name):
    rep = score.score(REF, MUT[name], UP, isolation_ok=True, controls_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps({"gate": rep["gate"], "confusion": rep["confusion"], "error_counts": rep["error_counts"],
                                                  "format_failure": rep["format_failure"]}, indent=1, sort_keys=True) + "\n")
    e = controls.EXPECTATIONS[name]
    if "gate" in e:
        assert rep["gate"]["verdict"] == e["gate"], rep["gate"]
    if "gate_not" in e:
        assert rep["gate"]["verdict"] != e["gate_not"]
    if "correct" in e:
        assert rep["gate"]["cases_correct"] == e["correct"], rep["confusion"]
    for cid in e.get("incorrect", []):
        assert rep["cases"][cid]["correct"] is False
    for k in e.get("errors_include", []):
        assert any(x.startswith(k) for c in rep["cases"].values() for x in c["errors"] + c["severe"]), (k, rep["error_counts"])
    if e.get("format_failure"):
        assert rep["format_failure"]
