"""How repetitive is a real stream of governed actions, as a function of how far a settlement may generalize?

Input: the 1,000 real, chronologically ordered IPSA claim rows bundled in the packet (features only, no outcomes).

Model (deliberately generous to the amortization thesis): every time a claim arrives whose *class* has not been
seen before, one human settlement is spent, and that settlement is assumed to cover every later claim of the same
class. "Class" is defined at several granularities. Recurrence at a granularity is NECESSARY for reuse at that
granularity; it is NOT sufficient (a settlement must also be legitimate at that scope, and the facts that decide
real disputes - purpose, evidence, budget state - are not in these rows at all).

Run from the repository root:  python -B analysis/recurrence.py
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "evidence" / "sophon_ipsa" / "results" / "sample_features.json"
OUT = ROOT / "results" / "recurrence.json"


def amount_band(a: str) -> str:
    try:
        v = abs(float(a))
    except ValueError:
        return "?"
    return "0" if v == 0 else f"1e{int(math.floor(math.log10(v)))}"


def norm_details(s: str) -> str:
    s = re.sub(r"\d+", "#", s.casefold())
    return re.sub(r"\s+", " ", s).strip()


GRANULARITIES = {
    "G1 category": lambda f: (f["Category"],),
    "G2 category+cost_type": lambda f: (f["Category"], f["Cost Type"]),
    "G3 +short_description": lambda f: (f["Category"], f["Cost Type"], f["Short Description"]),
    "G4 +amount_order_of_magnitude": lambda f: (f["Category"], f["Cost Type"], f["Short Description"], amount_band(f["Amount Claimed"])),
    "G5 +normalised_details_text": lambda f: (f["Category"], f["Cost Type"], f["Short Description"], norm_details(f["Details"])),
}


def curve(keys: list[tuple]) -> dict:
    seen: set = set()
    settlements = 0
    covered_flags = []
    for k in keys:
        if k in seen:
            covered_flags.append(1)
        else:
            covered_flags.append(0)
            seen.add(k)
            settlements += 1
    n = len(keys)
    half = n // 2
    counts = Counter(keys)
    singletons = sum(1 for c in counts.values() if c == 1)
    # settlements needed (most-frequent-first, i.e. with hindsight) to cover 50/80/90 % of the stream
    ordered = sorted(counts.values(), reverse=True)
    need = {}
    for target in (0.5, 0.8, 0.9):
        acc = 0
        for i, c in enumerate(ordered, 1):
            acc += c
            if acc / n >= target:
                need[f"{int(target * 100)}%"] = i
                break
    return {
        "distinct_classes": len(counts),
        "settlements_spent_online": settlements,
        "covered_overall": round(sum(covered_flags) / n, 3),
        "covered_first_half": round(sum(covered_flags[:half]) / half, 3),
        "covered_second_half": round(sum(covered_flags[half:]) / (n - half), 3),
        "covered_last_100": round(sum(covered_flags[-100:]) / 100, 3),
        "new_classes_in_last_100": 100 - sum(covered_flags[-100:]),
        "classes_seen_exactly_once": singletons,
        "share_of_settlements_never_reused": round(singletons / len(counts), 3),
        "mean_claims_per_settlement": round(n / len(counts), 2),
        "median_claims_per_settlement": sorted(counts.values())[len(counts) // 2],
        "hindsight_settlements_to_cover": need,
    }


def main() -> None:
    rows = json.loads(SAMPLE.read_text(encoding="utf-8"))
    rows.sort(key=lambda r: (r["date"], r["row_index"]))
    result = {"rows": len(rows), "first_date": rows[0]["date"], "last_date": rows[-1]["date"],
              "note": "Upper bound on reuse from recurrence alone. A 1,000-row sample of ~82,787 rows under-states "
                      "recurrence in the full stream (sampling thins repeats), so treat fine-granularity figures as "
                      "pessimistic and the ordering across granularities as the result.",
              "granularities": {}}
    for name, fn in GRANULARITIES.items():
        result["granularities"][name] = curve([fn(r["features"]) for r in rows])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    hdr = f"{'granularity':34s}{'classes':>8s}{'cov.all':>9s}{'cov.2ndH':>10s}{'last100':>9s}{'once-only':>11s}{'median/settl':>13s}"
    print(hdr)
    for name, c in result["granularities"].items():
        print(f"{name:34s}{c['distinct_classes']:8d}{c['covered_overall']:9.3f}{c['covered_second_half']:10.3f}"
              f"{c['covered_last_100']:9.3f}{c['share_of_settlements_never_reused']:11.3f}{c['median_claims_per_settlement']:13d}")


if __name__ == "__main__":
    main()
