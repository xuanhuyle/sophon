"""E5 versioned authority and temporal check (PROTOCOL.md §3; written after the freeze).

version_state(version_id, K)      -> NOT_KNOWN | NOT_APPROVED | APPROVAL_INVALID | LAB_APPROVED (+ reasons, detail)
governing(D, K)                   -> the version that governs order date D as known at K
governing_window(a, b, K)         -> the single governing version over [a, b), or a refusal
routing(K)                        -> HISTORICAL_VERSION_ROUTING segments [(from, to, version)]

The approval of P1_v2 is bound to source sha256 + clause version + normalized-claim hash (claim.py). P1_v1 keeps its
E3 approval (AP_S1_READ, bound to a reading id); it is additionally checked through E4's unmodified step A (E3
validator + E3.1 in_force / trusted reading meaning) and by comparing its atoms with E3 record S1.
This is a LAB check of simulated roles, not identity authentication.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
EXP = E5.parent
REPO = EXP.parent
sys.path.insert(0, str(HERE))
import claim  # noqa: E402

VERSIONS = ("P1_v1", "P1_v2")
DATA_START = "2024-01-01"


def t(x: str) -> datetime:
    return datetime.fromisoformat(str(x).replace("Z", "+00:00"))


def j(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _e4_step_a():
    sys.path.insert(0, str(EXP / "E4_independent_verification" / "src"))
    import checker as e4c  # noqa: PLC0415  (E4, unmodified)
    return e4c


class Authority:
    def __init__(self, ir_dir: Path | None = None, approvals: dict | None = None):
        ir_dir = Path(ir_dir or E5 / "ir")
        self.ir = {v: j(ir_dir / f"{v}.json") for v in VERSIONS}
        self.approvals = approvals if approvals is not None else {
            "AP_S1_READ": j(EXP / "E3_formal_ir" / "cases" / "approvals" / "AP_S1_READ.json"),
            "AP_S1_V2": j(E5 / "approvals" / "AP_S1_V2.json")}
        self.roster = j(EXP / "E3_formal_ir" / "cases" / "roster.json")
        self.trusted = j(EXP / "E3_1_integrity" / "cases" / "TRUSTED_MANIFEST.json")
        self.e3_s1 = j(EXP / "E3_formal_ir" / "cases" / "records" / "S1.json")

    # ------------------------------------------------------------------ approvals
    def _approval_failures(self, ap: dict, ir: dict, src_sha: str | None) -> list[str]:
        gs, sc, f = ir["governing_source"], ap["scope"], []
        spec = self.roster["roles"].get(ap["approver_role"])
        if ap["approver_role"] in self.roster["never_approvers"] or spec is None or ap["claim"]["kind"] not in spec.get("may_approve", []) \
                or sc["source_id"] not in spec.get("source_ids", []):
            f.append("APPROVER_NOT_AUTHORIZED")
        if (sc["source_id"] != gs["source_id"] or sc["source_sha256"] != gs["content_sha256"] or sc["source_sha256"] != src_sha
                or sc["clause_id"] != gs["clause_id"] or sc["clause_version"] != gs["clause_version"]
                or sc.get("document_id", gs["document_id"]) != gs["document_id"]):
            f.append("APPROVAL_SCOPE_MISMATCH")
        if "normalized_claim_sha256" in ap["claim"]:
            if ap["claim"]["normalized_claim_sha256"] != claim.meaning_sha(ir):
                f.append("APPROVAL_MEANING_MISMATCH")
        elif ap["claim"].get("reading_id") != (ir.get("derived_from_e3") or {}).get("reading_id"):
            f.append("APPROVAL_MEANING_MISMATCH")
        if t(ap["known_at"]) < t(gs["observed_at"]):
            f.append("APPROVAL_BEFORE_SOURCE_OBSERVED")
        return f

    def version_state(self, vid: str, K: str) -> dict:
        ir = self.ir[vid]
        gs = ir["governing_source"]
        detail = {"version_id": vid, "document_id": gs["document_id"], "clause": f"{gs['clause_id']} v{gs['clause_version']}",
                  "observed_at": gs["observed_at"], "effective_from": gs["effective_from"], "effective_to": gs.get("effective_to"),
                  "knowledge_at": K}
        if t(gs["observed_at"]) > t(K):
            return {"state": "NOT_KNOWN", "reasons": ["REQUIREMENT_VERSION_NOT_KNOWN"], "detail": detail}
        src = REPO / gs["path"]
        text = src.read_text(encoding="utf-8") if src.is_file() else None
        src_sha = hashlib.sha256(text.encode("utf-8")).hexdigest() if text is not None else None
        detail["source_sha256_recomputed"] = src_sha
        reasons = []
        if src_sha != gs["content_sha256"]:
            reasons.append("SOURCE_HASH_MISMATCH")
        if text is None or f"[{gs['clause_id']} v{gs['clause_version']}] {ir['requirement']['text']}" not in text:
            reasons.append("CLAUSE_NOT_IN_SOURCE")
        visible = [self.approvals[a] for a in ir["approval_ids"] if a in self.approvals and t(self.approvals[a]["known_at"]) <= t(K)]
        detail["visible_approvals"] = [a["approval_id"] for a in visible]
        if not visible:
            return {"state": "NOT_APPROVED", "reasons": ["REQUIREMENT_VERSION_NOT_APPROVED"] + reasons, "detail": detail}
        valid = []
        for ap in visible:
            fails = self._approval_failures(ap, ir, src_sha)
            detail.setdefault("approval_checks", {})[ap["approval_id"]] = fails or "VALID"
            if not fails:
                valid.append(ap)
            reasons += fails
        if vid == "P1_v1":
            e4c = _e4_step_a()
            st, rs, d = e4c.authority("P1", {"approvals": ["AP_S1_READ"], "eval_known_at": K, "eval_effective_at": gs["effective_from"]}, self.trusted)
            detail["e4_step_a"] = {"refusal": st, "reasons": rs, "selected_reading": d.get("selected_reading"),
                                   "reading_meaning_matches_trusted": d.get("reading_meaning_matches_trusted")}
            same_atoms = ir["requirement"]["atoms"] == self.e3_s1["requirement"]["atoms"] and ir["requirement"]["text"] == self.e3_s1["requirement"]["text"]
            detail["atoms_equal_e3_s1"] = same_atoms
            if st is not None:
                reasons += [f"E4_STEP_A_{r}" for r in rs]
                valid = []
            if not same_atoms:
                reasons.append("V1_ATOMS_DIFFER_FROM_E3")
                valid = []
        if reasons or not valid:
            return {"state": "APPROVAL_INVALID", "reasons": sorted(set(reasons)) or ["APPROVAL_INVALID"], "detail": detail}
        detail["approval_effective"] = {a["approval_id"]: [a["effective_from"], a.get("effective_to")] for a in valid}
        return {"state": "LAB_APPROVED", "reasons": [], "detail": detail, "approvals": valid}

    # ------------------------------------------------------------------ selection
    @staticmethod
    def _covers(a_from: str, a_to: str | None, d: str) -> bool:
        return a_from <= d and (a_to is None or d <= a_to)

    def governing(self, d: str, K: str) -> dict:
        cands = []
        for vid in VERSIONS:
            s = self.version_state(vid, K)
            if s["state"] != "LAB_APPROVED":
                continue
            gs = self.ir[vid]["governing_source"]
            if not self._covers(gs["effective_from"], gs.get("effective_to"), d):
                continue
            if not any(self._covers(a["effective_from"], a.get("effective_to"), d) for a in s["approvals"]):
                continue
            cands.append(vid)
        superseded = set()
        for vid in cands:
            sup = self.ir[vid].get("supersedes")
            if sup and sup["version_id"] in cands and sup["for_order_dates_from"] <= d:
                superseded.add(sup["version_id"])
        left = [v for v in cands if v not in superseded]
        if len(left) == 1:
            return {"version": left[0], "candidates": cands, "superseded": sorted(superseded)}
        return {"version": None, "reason": "NO_GOVERNING_VERSION" if not left else "AMBIGUOUS", "candidates": cands}

    def _breakpoints(self, K: str) -> list[str]:
        pts = set()
        for vid in VERSIONS:
            if self.version_state(vid, K)["state"] != "LAB_APPROVED":
                continue
            gs = self.ir[vid]["governing_source"]
            pts.add(gs["effective_from"])
            if gs.get("effective_to"):
                pts.add((date.fromisoformat(gs["effective_to"]) + timedelta(days=1)).isoformat())
            if self.ir[vid].get("supersedes"):
                pts.add(self.ir[vid]["supersedes"]["for_order_dates_from"])
        return sorted(pts)

    def governing_window(self, a: str | None, b: str | None, K: str) -> dict:
        start = a or DATA_START
        probes = [start] + [p for p in self._breakpoints(K) if p > start and (b is None or p < b)]
        found = {p: self.governing(p, K)["version"] for p in probes}
        vs = set(found.values())
        if len(vs) == 1 and None not in vs:
            return {"version": vs.pop(), "probes": found}
        return {"version": None, "reason": "WINDOW_SPANS_VERSIONS" if None not in vs else "NO_GOVERNING_VERSION", "probes": found}

    def routing(self, K: str) -> list[dict]:
        pts = [p for p in self._breakpoints(K)]
        if not pts:
            return []
        segs = []
        for i, p in enumerate(pts):
            nxt = pts[i + 1] if i + 1 < len(pts) else None
            v = self.governing(p, K)["version"]
            if segs and segs[-1]["version"] == v:
                segs[-1]["window"][1] = nxt
            else:
                segs.append({"window": [p, nxt], "version": v})
        return segs
