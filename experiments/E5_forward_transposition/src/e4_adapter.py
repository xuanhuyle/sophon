"""E5 adapter around the E4 checker (PROTOCOL.md §5; written after the freeze). E4 files are NOT edited.

Reused unmodified from E4 (imported from experiments/E4_independent_verification/src):
  - checker.Checker.snapshot_eval: native year + order-line results vs reference, TOTAL/MEMBERSHIP/AMOUNT_MISMATCH,
    counterexamples with source facts and lineage (inherited, not overridden);
  - candidate_stack.build / execute: disposable copy of the pinned project, patch, loader, dbt build/parse, genuine `mf`.
Replaced here (E4 hardcodes P1 >= 100, the E3 v1 approval and its own REFERENCE/snapshots):
  - __init__ / registered: E5 snapshots and E5 REFERENCE.json;
  - reference: the E5 oracle by "policy|window", checked against the frozen E5 reference;
  - stack: one build per (candidate, snapshot), one `mf` execution per distinct query (E4 cached one query per stack);
  - evaluate_check: E5 versioned authority (src/authority.py) instead of E4's step A.
So E4's comparison algorithm runs as written; the E4 checker as a whole did NOT run unchanged.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
EXP = E5.parent
sys.path.insert(0, str(EXP / "E4_independent_verification" / "src"))
import candidate_stack as cs  # noqa: E402  (E4, unmodified)
import checker as e4c  # noqa: E402  (E4, unmodified)

sys.path.insert(0, str(HERE))
import snapshots  # noqa: E402


def _load_by_path(name: str):
    """E1's src also has an `oracle` module (pulled in by E4 -> E1 erratum imports); load E5's by file path."""
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location(f"e5_{name}", HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"e5_{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


oracle = _load_by_path("oracle")  # E5 independent oracle (src/oracle.py)

ORACLE_POLICY = {"P1_v1": "P1v1", "P1_v2": "P1v2", "P2": "P2"}


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def window_key(a: str | None, b: str | None) -> str:
    if a is None and b is None:
        return "ALL"
    if a is None:
        return f"<{b}"
    if b is None:
        return f">={a}"
    return f"[{a},{b})"


def parse_key(key: str) -> tuple[str, str | None, str | None]:
    pol, w = key.split("|")
    if w == "ALL":
        return pol, None, None
    if w.startswith("<"):
        return pol, None, w[1:]
    if w.startswith(">="):
        return pol, w[2:], None
    a, b = w[1:-1].split(",")
    return pol, a, b


class E5Checker(e4c.Checker):
    def __init__(self, upstream: Path, work: Path, reference: dict):  # noqa: D107  (does not call E4's __init__)
        self.up = Path(upstream).resolve()
        self.work = Path(work)
        self.ref = reference
        pinned = self.up / "data" / "raw"
        reg = self.ref["registered_snapshots"]
        if {f: snapshots.sha(pinned / f) for f in snapshots.FILES} != reg["PINNED"]["csv_sha256"]:
            raise RuntimeError("pinned raw CSVs differ from the frozen PINNED anchors")
        self.snap_dir = self.work / "snapshots"
        built = snapshots.build(pinned, self.snap_dir)
        self.snapshots_match_frozen = all(built[k]["csv_sha256"] == reg[k]["csv_sha256"] for k in reg)
        self.stacks, self.refs, self.builds, self.facts = {}, {}, {}, {}

    def registered(self, policy: str, hashes: dict) -> str | None:
        return next((n for n, s in self.ref["registered_snapshots"].items() if s["csv_sha256"] == hashes), None)

    def reference(self, policy: str, snap: str) -> dict:
        key = (policy, snap)
        if key not in self.refs:
            pol, a, b = parse_key(policy)
            if snap not in self.facts:
                self.facts[snap] = oracle.order_lines(self.snap_dir / snap)
            r = oracle.evaluate(self.snap_dir / snap, pol, a, b, self.facts[snap])
            frozen = self.ref["reference_results"].get(f"{policy}@{snap}")
            r["equals_frozen"] = frozen is not None and r["by_year"] == frozen["by_year"] and \
                hashlib.sha256(canon(r["lines"]).encode()).hexdigest() == frozen["lines_sha256"]
            r["facts"] = self.facts[snap]
            self.refs[key] = r
        return self.refs[key]

    def build(self, c: dict, snap: str) -> dict:
        key = (c["candidate_id"], snap)
        if key not in self.builds:
            self.builds[key] = cs.build(f"{c['candidate_id']}__{snap}", c["patch"], self.snap_dir / snap, self.up, self.work / "stacks")
        return self.builds[key]

    def run_query(self, c: dict, snap: str, query: dict) -> dict:
        b = self.build(c, snap)
        key = (c["candidate_id"], snap, canon(query))
        if key not in self.stacks:
            st = dict(b)
            if b["ok"]:
                st["exec_year"] = cs.execute(b, query)
                st["exec_line"] = cs.execute(b, {**query, "group_by": ["sales"]})
            self.stacks[key] = st
        return self.stacks[key]

    def stack(self, c: dict, snap: str) -> dict:  # used by the inherited E4 snapshot_eval
        return self.run_query(c, snap, c["query"])

    # ------------------------------------------------------------------ one E5 check
    def evaluate_check(self, check: dict, cand: dict, auth, K: str) -> dict:
        a, b = check["window"]
        detail = {"requested_version": check["requested_version"], "knowledge_at": K, "window": [a, b]}
        if check["requested_version"] == "GOVERNING":
            g = auth.governing_window(a, b, K)
            detail["governing"] = g
            version = g["version"]
        else:
            version = check["requested_version"]
        a_status, a_reasons = None, []
        if version is None:
            a_status, a_reasons = "NOT_VERIFIED", [detail["governing"]["reason"]]
        else:
            vs = auth.version_state(version, K)
            detail["version_state"] = {"state": vs["state"], "reasons": vs["reasons"]}
            if vs["state"] != "LAB_APPROVED":
                a_status, a_reasons = "NOT_VERIFIED", vs["reasons"]
            elif check["requested_version"] != "GOVERNING":
                g = auth.governing_window(a, b, K)
                detail["governing"] = g
                if g["version"] != version:
                    a_status, a_reasons = "NOT_APPLICABLE", ["VERSION_NOT_GOVERNING_FOR_WINDOW"]
        detail["version"] = version
        policy_key = f"{ORACLE_POLICY.get(version, 'P1v1' if version is None else version)}|{window_key(a, b)}"
        q = dict(cand["query"])
        q["where"] = list(q.get("where", [])) + time_where(a, b)
        c = {**cand, "query": q}
        snaps = []
        for s in check["snapshots"]:
            r = self.snapshot_eval(c, policy_key, s)  # E4's algorithm (inherited, unmodified)
            r["native_executed_ok"] = bool(self.stack(c, s).get("exec_year", {}).get("ok"))
            snaps.append(r)
        reasons = set(a_reasons)
        for s in snaps:
            reasons |= set(s["reasons"])
        if a_status:
            status = a_status
        elif any(s["status"] == "MISMATCH" for s in snaps):
            status = "NONCONFORMING_IMPLEMENTATION"
        elif any(s["status"] == "NOT_VERIFIED" for s in snaps):
            status = "NOT_VERIFIED"
        else:
            status = "VERIFIED_FOR_LAB_CHECKS"
        return {"check_id": check["check_id"], "candidate": cand["candidate_id"], "status": status, "reasons": sorted(reasons),
                "authority": detail, "reference_key": policy_key, "query": q, "snapshots": snaps,
                "scope": "bounded LAB checks: registered snapshots, order-line grain, LAB_SIMULATED approvals; not legal compliance"}


def time_where(a: str | None, b: str | None) -> list[str]:
    td = "{{ TimeDimension('metric_time', 'day') }}"
    w = []
    if a is not None:
        w.append(f"{td} >= '{a}'")
    if b is not None:
        w.append(f"{td} < '{b}'")
    return w
