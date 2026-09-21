"""Run everything in the lab that does not need the sandbox owner.

  python -B -m lab.run_lab          (from the repository root)

1. The real ledger (lab/ledger/owner_acts.json). It is empty until the owner adopts, so all 48 cases must be REQUEST_AUTHORITY.
2. A conditional preview: what the bright lines alone would decide IF the draft were adopted unchanged. Not an adopted result.
3. Differential sweep: both architectures over a grid of possible owner settlements, all 48 cases. Any disagreement is reported.
4. How many held-out cases any settlement in the grid can decide (the ceiling on the protocol's "reuse" metric).
5. Adversarial probes against the ledger, the first-pass baseline, the baseline with each convention, and with all of them.
6. Mutation test of the probe suite itself against seeded faults in the ledger arm.

Steps 2-6 use fixture authority held in memory. Nothing here is the owner's adoption or settlement.
"""
from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

from . import probes
from .baseline_arm import CONVENTIONS, BaselineArm
from .ledger_arm import LedgerArm
from .model import ROOT, load_cases, policy_hash

OUT = ROOT / "results" / "lab_results.json"
OWNER_ACTS = ROOT / "lab" / "ledger" / "owner_acts.json"
T0, T_SETTLE = "2026-09-30T09:00:00", "2026-10-24T18:{:02d}:00"
FAULTS = ["proposal_has_force", "skip_power_check", "ignore_delegation_bounds", "allow_self_dealing", "allow_retroactive",
          "untyped_payloads", "ignore_expiry", "ignore_revocation", "ignore_supersession", "ignore_amendment_suspension",
          "ignore_version_timing", "unknown_category_clears", "nan_passes", "exception_matches_any_case", "ignore_amount_cap",
          "no_consumption", "practice_becomes_permission",
          # added after the first mutation run showed five probes detecting nothing (results/mutation_first_run.json)
          "adoption_not_required", "ignore_effective_from", "blank_receipt_passes", "exception_overrides_block"]


def real_ledger(cases):
    state = json.loads(OWNER_ACTS.read_text(encoding="utf-8"))
    arm = LedgerArm(state.get("owner") or "UNSET")
    if state.get("adoption"):
        a = state["adoption"]
        arm.adopt(a["issuer"], a["effective_from"], a["policy_version"], a.get("closure", "ALL_CLAUSES_SATISFIED"))
    refused = [(x, r.reason) for x in state.get("acts", []) if not (r := arm.record(x)).accepted]
    return {"adopted": bool(arm.adoption), "acts_recorded": len(arm.acts), "acts_refused": refused,
            "outcomes": dict(Counter(arm.decide(c).outcome for c in cases))}


def settlements(paris, lyon, meal, deminimis, scope):
    v, acts, n = policy_hash(), [], itertools.count()
    def add(kind, payload):
        acts.append({"type": kind, "issuer": probes.OWNER, "recorded_at": T_SETTLE.format(next(n)), "policy_version": v, "payload": payload})
    rules = [{"where": {"destination": d}, "max_amount": c} for d, c in (("Paris", paris), ("Lyon", lyon)) if c is not None]
    if rules:
        add("INTERPRET_OPEN_STANDARD", {"term": "hotel.reasonable", "rules": rules})
    if meal is not None:
        add("INTERPRET_OPEN_STANDARD", {"term": "meal.modest", "rules": [{"where": {}, "max_amount": meal}]})
    if deminimis is not None:
        add("RELAX_CONSTRAINT", {"constraint": "equipment_deminimis", "value": deminimis})
    if scope is not None:
        add("INTERPRET_OPEN_STANDARD", {"term": "approval.scope", "value": scope})
    return acts


GRID = list(itertools.product([None, 260, 300, 330, 360, 400], [None, 200, 250, 420], [None, 40, 60, 120, 180],
                              [None, 100, 400, 900], [None, "ALL", "TRAVEL_ONLY"]))


def sweep(cases):
    makers = {"ledger": lambda: LedgerArm(probes.OWNER), "baseline": lambda: BaselineArm(probes.OWNER),
              "baseline+all": lambda: BaselineArm(probes.OWNER, CONVENTIONS)}
    holdout = [c for c in cases if c.sequence >= 25]
    disagreements, reuse, varies = [], [], {c.case_id: set() for c in holdout}
    zero = None
    for cfg in GRID:
        outcomes = {}
        for name, make in makers.items():
            arm = make()
            arm.adopt(probes.OWNER, T0, policy_hash())
            for a in settlements(*cfg):
                assert arm.record(a).accepted, (name, a)
            outcomes[name] = {c.case_id: arm.decide(c).outcome for c in cases}
        for other in ("baseline", "baseline+all"):
            for c in cases:
                if outcomes["ledger"][c.case_id] != outcomes[other][c.case_id]:
                    disagreements.append({"settlement": cfg, "case": c.case_id, "ledger": outcomes["ledger"][c.case_id], other: outcomes[other][c.case_id]})
        led = outcomes["ledger"]
        if cfg == (None,) * 5:
            zero = led
        for c in holdout:
            varies[c.case_id].add(led[c.case_id])
        reuse.append((cfg, led))
    early_changed = sum(1 for cfg, led in reuse for c in cases if c.sequence < 25 and led[c.case_id] != zero[c.case_id])
    family = {c.case_id: c.category for c in cases}
    best, by_family = (0, None), Counter()
    for cfg, led in reuse:
        newly = [cid for cid in varies if led[cid] == "CLEAR" and zero[cid] != "CLEAR"]
        if len(newly) > best[0]:
            best = (len(newly), cfg)
        for fam, k in Counter(family[cid] for cid in newly).items():
            by_family[fam] = max(by_family[fam], k)
    dependent = sorted(cid for cid, seen in varies.items() if len(seen) > 1)
    return {"settlement_grid_size": len(GRID), "decisions_compared": len(GRID) * len(cases) * 2, "disagreements": disagreements[:20],
            "disagreement_count": len(disagreements),
            "settlement_period_outcomes_changed_by_later_settlements": early_changed,
            "holdout_cases": len(holdout), "holdout_outcome_independent_of_any_settlement": len(holdout) - len(dependent),
            "holdout_cases_a_settlement_can_move": dependent,
            "max_holdout_cases_newly_cleared_by_settlements": best[0], "achieved_by(paris,lyon,meal,deminimis,scope)": best[1],
            "max_newly_cleared_by_family": dict(by_family),
            "holdout_clear_with_zero_settlements": sum(1 for cid in varies if zero[cid] == "CLEAR")}


def run_probes():
    arms = {"ledger": lambda: LedgerArm(probes.OWNER), "baseline (first pass)": lambda: BaselineArm(probes.OWNER)}
    for c in sorted(CONVENTIONS):
        arms[f"baseline + {c}"] = (lambda c=c: BaselineArm(probes.OWNER, frozenset({c})))
    arms["baseline + all five"] = lambda: BaselineArm(probes.OWNER, CONVENTIONS)
    table, detail = {}, {}
    for name, make in arms.items():
        table[name] = {}
        for p in probes.PROBES:
            try:
                ok, note = p(make)
            except Exception as exc:                                  # a crash is a failure, and is reported as one
                ok, note = False, f"{type(exc).__name__}: {exc}"
            table[name][p.__name__] = ok
            detail.setdefault(p.__name__, {})[name] = note
    fixed_by = {}
    for p in probes.PROBES:
        n = p.__name__
        if not table["baseline (first pass)"][n]:
            fixed_by[n] = [c for c in sorted(CONVENTIONS) if table[f"baseline + {c}"][n]]
    return table, detail, fixed_by


def mutation():
    kills = {f: [] for f in FAULTS}
    for f in FAULTS:
        for p in probes.PROBES:
            try:
                ok, _ = p(lambda f=f: LedgerArm(probes.OWNER, frozenset({f})))
            except Exception:
                ok = False
            if not ok:
                kills[f].append(p.__name__[:3])
    detects = {p.__name__: [f for f in FAULTS if p.__name__[:3] in kills[f]] for p in probes.PROBES}
    return {"faults_each_probe_detects": detects, "probes_detecting_each_fault": kills,
            "surviving_faults": [f for f, k in kills.items() if not k], "probes_detecting_nothing": [p for p, d in detects.items() if not d]}


def loc(path: Path) -> int:
    """Logical lines: not blank, not a comment, not inside a docstring."""
    import ast
    src = path.read_text(encoding="utf-8")
    doc_lines: set[int] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and ast.get_docstring(node, clean=False) is not None:
            d = node.body[0]
            doc_lines.update(range(d.lineno, d.end_lineno + 1))
    return sum(1 for n, raw in enumerate(src.splitlines(), 1)
               if n not in doc_lines and raw.strip() and not raw.strip().startswith("#"))


def main():
    cases = load_cases()
    preview = LedgerArm(probes.OWNER)
    preview.adopt(probes.OWNER, T0, policy_hash())
    table, detail, fixed_by = run_probes()
    result = {
        "1_real_ledger": real_ledger(cases),
        "2_conditional_preview_NOT_ADOPTED": {"label": "IF the draft were adopted unchanged with zero settlements, under lab/READING.md",
                                               "outcomes": dict(Counter(preview.decide(c).outcome for c in cases)),
                                               "by_case": {c.case_id: [preview.decide(c).outcome] + preview.decide(c).reasons() for c in cases}},
        "3_4_differential_sweep": sweep(cases),
        "5_probes": {"passed": {a: f"{sum(r.values())}/{len(r)}" for a, r in table.items()}, "table": table,
                     "first_pass_baseline_failures_fixed_by": fixed_by, "detail": detail, "source_of_each_probe": probes.SOURCE},
        "6_mutation_test_of_probes": mutation(),
        "code_size_logical_lines": {"ledger_arm.py": loc(ROOT / "lab" / "ledger_arm.py"), "baseline_arm.py (all conventions included)": loc(ROOT / "lab" / "baseline_arm.py")},
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")

    print("1. real ledger:", result["1_real_ledger"])
    print("2. conditional preview (NOT adopted):", result["2_conditional_preview_NOT_ADOPTED"]["outcomes"])
    s = result["3_4_differential_sweep"]
    print(f"3. sweep: {s['settlement_grid_size']} settlements x 48 cases, disagreements between arms: {s['disagreement_count']}; "
          f"settlement-period outcomes changed by later settlements: {s['settlement_period_outcomes_changed_by_later_settlements']}")
    print(f"4. held-out: {s['holdout_outcome_independent_of_any_settlement']}/{s['holdout_cases']} never move; "
          f"max newly cleared = {s['max_holdout_cases_newly_cleared_by_settlements']} {s['max_newly_cleared_by_family']}")
    print("5. probes passed:")
    for a, v in result["5_probes"]["passed"].items():
        failed = [p[:3] for p, ok in table[a].items() if not ok]
        print(f"     {a:38s} {v:6s} failed: {' '.join(failed) or '-'}")
    print("   first-pass failures fixed by:", {k[:3]: v for k, v in fixed_by.items()})
    m = result["6_mutation_test_of_probes"]
    print("6. surviving faults:", m["surviving_faults"] or "none", "| probes detecting nothing:", [p[:3] for p in m["probes_detecting_nothing"]] or "none")
    print("   code size:", result["code_size_logical_lines"])


if __name__ == "__main__":
    main()
