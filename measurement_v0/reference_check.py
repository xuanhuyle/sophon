"""Measurement V0 reference check (oracle instrument, not a Sophon component).

Runs the native PolicyEngine-US model from a pinned checkout and compares the
monthly SNAP allotment with the arithmetic required by 7 CFR 273.10(e)(2)(ii)(A)
(CFR 2025 edition): allotment = max allotment - 30% of net income, where under
either State rounding option the result is max allotment - ceil(0.3 * N) for a
whole-dollar max allotment.

Scope guards (see PROTOCOL.md): whole-dollar net income N supplied directly (so
the State-optional net-income rounding of 273.10(e)(1)(ii) is moot), household of
3 (no minimum benefit), Texas, non-initial month 2026-01. The max allotment M is
read from the model itself and is NOT part of the checked claim.

Usage: python -I reference_check.py <policyengine-us checkout> <out.json>
"""
import json
import math
import sys

CHECKOUT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, CHECKOUT)

from policyengine_us import Simulation  # noqa: E402

PERIOD, STATE, SIZE = "2026-01", "TX", 3
NET_INCOMES = [501, 1000, 1234, 1391, 1999]  # frozen; 1000 is a zero-cents control
VARS = ["snap_max_allotment", "snap_expected_contribution",
        "snap_min_allotment", "snap_normal_allotment", "is_snap_eligible", "snap"]

rows = []
for n in NET_INCOMES:
    people = {f"p{i}": {"age": {2026: 35 if i == 0 else 10}} for i in range(SIZE)}
    members = list(people)
    situation = {
        "people": people,
        "spm_units": {"u": {"members": members, "snap_net_income": {PERIOD: n}}},
        "households": {"h": {"members": members, "state_code": {2026: STATE}}},
        "tax_units": {"t": {"members": members}},
        "families": {"f": {"members": members}},
    }
    sim = Simulation(situation=situation)
    out = {v: sim.calculate(v, PERIOD).tolist()[0] for v in VARS}
    m = out["snap_max_allotment"]
    # Exact decimal 30%: n is an integer, so 3n/10 avoids float noise.
    expected = m - math.ceil(3 * n / 10)
    observed = round(out["snap"], 2)
    rows.append({"net_income": n, "observed": out, "observed_snap_cents": observed,
                 "reference_allotment": expected,
                 "conforms": abs(observed - expected) < 0.005})

json.dump({"checkout": CHECKOUT, "period": PERIOD, "state": STATE, "size": SIZE,
           "rows": rows, "all_conform": all(r["conforms"] for r in rows)},
          open(OUT, "w"), indent=2)
for r in rows:
    print(r["net_income"], r["observed_snap_cents"], r["reference_allotment"], r["conforms"])
