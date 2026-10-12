"""Mechanical verdict from the recorded evidence (PROTOCOL.md §7). Run after run_erratum.py, controls.py, pytest:
    .upstream/.venv/bin/python -m pytest -q -p no:cacheprovider tests/ | tee evidence/pytest.log
    python3 src/gate.py --evidence evidence
"""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--evidence", required=True)
ev = Path(ap.parse_args().evidence)
s = json.loads((ev / "reproduction_summary.json").read_text())
c = json.loads((ev / "controls" / "controls.json").read_text())
log = (ev / "pytest.log").read_text()
tests_ok = " passed" in log and "failed" not in log and "error" not in log.lower()
g8 = (tests_ok and s["capability"]["classification"] == "NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS"
      and c["G7"]["c_capability_derivable"] and c["G7"]["a_capability_refuses"] and c["G7"]["b_capability_refuses"])
gates = {"G1": s["G1"], "G2": s["G2"]["ok"], "G3": s["G3"]["ok"], "G4": s["G4"]["ok"], "G5": s["G5"]["ok"],
         "G6": s["G6"], "G7": c["G7"]["ok"], "G8": g8}
# precedence: BLOCKED (runtime absent: these files would not exist) > INCONCLUSIVE (G1) > NOT_CONFIRMED (G2-G5)
#             > INCONCLUSIVE (G6-G8) > CONFIRMED
if not gates["G1"]:
    verdict = "INCONCLUSIVE"
elif not all(gates[k] for k in ("G2", "G3", "G4", "G5")):
    verdict = "NOT_CONFIRMED"
elif not all(gates[k] for k in ("G6", "G7", "G8")):
    verdict = "INCONCLUSIVE"
else:
    verdict = "CONFIRMED_E1_ERRATUM"
out = {"gates": gates, "verdict": verdict, "rule": "PROTOCOL.md §7 precedence", "pytest_tail": log.strip().splitlines()[-1]}
(ev / "gate.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out))
