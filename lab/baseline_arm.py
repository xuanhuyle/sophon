"""Arm B: the best practical alternative - policy-as-code, settings in a reviewed repository, a stateless decision
function. Rules live in code, thresholds and exceptions live in data files, every change is a commit approved by a
CODEOWNER, and history is the commit log.

With no conventions switched on this is how a competent team would build it on a first pass. Each convention is one
discipline such a team could add. lab/run_lab.py switches them on one at a time to see which probe each one fixes.
"""
from __future__ import annotations

import copy

from .model import Case, Decision, Receipt, ts

CONVENTIONS = frozenset({
    "effective_dating",   # settings carry effective_from/expires_at distinct from commit time; never backdated
    "typed_ownership",    # who may change what is checked per kind of change, with bounded delegation
    "version_pinning",    # nothing is live until a policy version is adopted; settings are pinned to the version they were made for
    "exact_one_shot",     # the payment step remembers what it executed and uses an exception once
    "closed_surface",     # anything the rules do not recognise goes to a person
})
DEFAULTS = {"finance_threshold": 1000.0, "cfo_threshold": 5000.0, "equipment_deminimis": None}
TERMS = ("hotel.reasonable", "meal.modest", "equipment.necessity", "approval.scope")


class BaselineArm:
    def __init__(self, owner: str, conventions: frozenset[str] = frozenset()):
        assert conventions <= CONVENTIONS
        self.name = "baseline" + ("+all" if conventions == CONVENTIONS else "+" + ",".join(sorted(conventions)) if conventions else "")
        self.owner, self.on = owner, conventions
        self.adopted: dict | None = None
        self.commits: list[dict] = []     # linear history of full snapshots, like a main branch
        self.branches: list[dict] = []    # unmerged proposals
        self.paid: list[str] = []
        self.used: dict[str, str] = {}

    # ------------------------------------------------------------------ repository
    def _head(self, known_at: str | None = None) -> dict:
        snap = {"settings": {}, "exceptions": [], "codeowners": {self.owner}, "delegations": [], "policy_version": None}
        for c in self.commits:
            if known_at is None or ts(c["time"]) <= ts(known_at):
                snap = c["snapshot"]
        return snap

    def adopt(self, issuer: str, at: str, policy_version: str, closure: str = "ALL_CLAUSES_SATISFIED") -> Receipt:
        if issuer != self.owner:
            return Receipt(False, "not a codeowner")
        self.adopted = {"time": at, "policy_version": policy_version, "closure": closure}
        snap = copy.deepcopy(self._head())
        snap["policy_version"] = policy_version
        self.commits.append({"time": at, "author": issuer, "snapshot": snap})
        return Receipt(True, act_id="C0")

    def propose(self, proposal: dict) -> Receipt:
        self.branches.append(proposal)
        return Receipt(True, "open pull request; not merged")

    def record(self, act: dict) -> Receipt:
        """A pull request that the repository's review rules either merge or refuse."""
        t, who, kind, p = act["recorded_at"], act["issuer"], act["type"], act.get("payload", {})
        if self.commits and ts(t) < ts(self.commits[-1]["time"]):
            return Receipt(False, "history is linear")
        head = self._head()
        eff = act.get("effective_from") or t
        if "effective_dating" in self.on and ts(eff) < ts(t):
            return Receipt(False, "backdated effective date")
        if "version_pinning" in self.on:
            if not self.adopted or ts(t) < ts(self.adopted["time"]):
                return Receipt(False, "no adopted policy")
            if act.get("policy_version") != head["policy_version"]:
                return Receipt(False, "pinned to a policy version that is not current")
        refusal = self._review(head, act, t) if "typed_ownership" in self.on else (None if who in head["codeowners"] else "not a codeowner")
        if refusal:
            return Receipt(False, refusal)

        snap = copy.deepcopy(head)
        entry_id = f"C{len(self.commits)}"
        entry = {"id": entry_id, "author": who, "payload": p, "effective_from": eff, "expires_at": act.get("expires_at"),
                 "policy_version": act.get("policy_version"), "suspended": False}
        def put(key, e):   # with effective dating the file keeps dated entries; otherwise a new value overwrites the old
            snap["settings"][key] = snap["settings"].get(key, []) + [e] if "effective_dating" in self.on else [e]
        if kind == "INTERPRET_OPEN_STANDARD":
            put(p["term"], entry)
            if "constraint" in p and "typed_ownership" not in self.on:   # the label on a pull request binds nothing
                put(p["constraint"], {**entry, "payload": {"constraint": p["constraint"], "value": p["value"]}})
        elif kind in ("ADD_CONSTRAINT", "RELAX_CONSTRAINT"):
            put(p["constraint"], entry)
        elif kind == "CASE_EXCEPTION":
            snap["exceptions"].append(entry)
        elif kind == "DELEGATE":
            if "typed_ownership" in self.on:
                snap["delegations"].append(entry)
            else:
                snap["codeowners"].add(p["delegate"])      # CODEOWNERS has no amounts, categories or expiry
        elif kind == "AMEND_SOURCE":
            snap["policy_version"] = p["new_policy_version"]
            if "version_pinning" in self.on:
                for e in [x for v in snap["settings"].values() for x in v] + snap["exceptions"]:
                    if e["id"] not in p.get("survivors", []):
                        e["suspended_from"] = eff
        elif kind == "REVOKE":
            if "effective_dating" in self.on:      # end-date the entry; do not rewrite what was in force before
                for e in [x for v in snap["settings"].values() for x in v] + snap["exceptions"]:
                    if e["id"] == p["target"]:
                        e["expires_at"] = eff
            else:
                snap["settings"] = {k: [e for e in v if e["id"] != p["target"]] for k, v in snap["settings"].items()}
                snap["exceptions"] = [e for e in snap["exceptions"] if e["id"] != p["target"]]
        self.commits.append({"time": t, "author": who, "snapshot": snap})
        return Receipt(True, act_id=entry_id)

    def _review(self, head: dict, act: dict, t: str) -> str | None:
        who, kind, p = act["issuer"], act["type"], act.get("payload", {})
        if kind == "INTERPRET_OPEN_STANDARD" and (p.get("term") not in TERMS or set(p) - {"term", "rules", "value", "outside"}):
            return "interpretations/ may only hold declared open terms"
        if kind == "CASE_EXCEPTION" and p.get("claimant") == who:
            return "author is the beneficiary"
        if who == self.owner:
            return None
        if kind not in ("CASE_EXCEPTION", "INTERPRET_OPEN_STANDARD", "REVOKE"):
            return "owner-only path"
        for d in head["delegations"]:
            g = d["payload"]
            live = ts(d["effective_from"]) <= ts(t) and (not d["expires_at"] or ts(t) < ts(d["expires_at"]))
            if g["delegate"] != who or not live or kind not in g.get("act_types", []):
                continue
            if kind == "CASE_EXCEPTION" and (p.get("category") not in g.get("categories", []) or not p.get("max_amount", 1e18) <= g.get("max_amount", 0)):
                continue
            if kind == "INTERPRET_OPEN_STANDARD" and p.get("term") not in g.get("terms", []):
                continue
            return None
        return "no delegation covers this change"

    # ------------------------------------------------------------------ rules
    def _usable(self, e: dict, case: Case, at: str) -> str:
        """'yes', 'no', or 'timing' (in force now, but not when the expense was incurred)."""
        if "effective_dating" not in self.on:
            return "yes"
        def live(t):
            ok = ts(e["effective_from"]) <= ts(t) and (not e["expires_at"] or ts(t) < ts(e["expires_at"]))
            return ok and not ("suspended_from" in e and ts(t) >= ts(e["suspended_from"]))
        if not live(at):
            return "no"
        return "yes" if live(case.decision_time) else "timing"

    def decide(self, case: Case, at: str | None = None, known_at: str | None = None) -> Decision:
        at = at or case.decision_time
        head = self._head(known_at or at)
        if "version_pinning" in self.on and (not self.adopted or ts(self.adopted["time"]) > ts(at)):
            return Decision.of([("REQUEST_AUTHORITY", "no adopted policy")], [], None)
        out: list[tuple[str, str]] = []
        used: list[str] = []

        def setting(key):
            entries = head["settings"].get(key) or []
            if "effective_dating" in self.on:      # the newest entry already effective wins, and an ended one never revives an older one
                entries = sorted((e for e in entries if ts(e["effective_from"]) <= ts(at)), key=lambda e: ts(e["effective_from"]))
            if not entries:
                return None, "missing"
            e = entries[-1]
            if "version_pinning" in self.on and "suspended_from" in e and ts(at) >= ts(e["suspended_from"]):
                return None, "missing"
            state = self._usable(e, case, at)
            if state == "yes":
                used.append(e["id"])
                return e["payload"], "ok"
            return None, "timing" if state == "timing" else "missing"

        limits = dict(DEFAULTS)
        for key in DEFAULTS:
            p, state = setting(key)
            if state == "ok":
                limits[key] = p["value"]
            elif state == "timing":
                out.append(("SEMANTIC_REVIEW", "limit changed after the expense"))

        if case.category not in ("hotel", "meal", "equipment", "travel") and "closed_surface" in self.on:
            return Decision.of([("REQUEST_AUTHORITY", "unrecognised category")], used, head["policy_version"])

        if not case.purpose.strip():
            out.append(("REQUEST_FACT", "no purpose"))
        if case.receipt_present != "yes":
            out.append(("REQUEST_FACT", "no receipt"))
        if case.approver == case.claimant:
            out.append(("BLOCK", "self-approved"))
        amount = case.amount
        if amount is None:
            out.append(("REQUEST_FACT", "bad amount"))
            amount = 0.0
        if amount > limits["finance_threshold"] and case.finance_approved != "yes":
            out.append(("REQUEST_AUTHORITY", "needs Finance"))
        if amount > limits["cfo_threshold"] and case.cfo_approved != "yes":
            out.append(("REQUEST_AUTHORITY", "needs CFO"))

        def matching_exceptions() -> list[dict]:
            found = []
            for e in head["exceptions"]:
                p = e["payload"]
                if p["case_id"] != case.case_id or p["claimant"] != case.claimant or p["category"] != case.category:
                    continue
                if amount > p["max_amount"]:
                    continue
                if e["expires_at"] and ts(at) >= ts(e["expires_at"]):      # a competent team gives exceptions an end date
                    continue
                if "effective_dating" in self.on and self._usable(e, case, at) != "yes":
                    continue
                if "version_pinning" in self.on and "suspended_from" in e and ts(at) >= ts(e["suspended_from"]):
                    continue
                if "exact_one_shot" in self.on and self.used.get(e["id"]) not in (None, case.action_hash()):
                    continue
                used.append(e["id"])
                found.append(e)
            return found

        exceptions = matching_exceptions()

        def capped(key: str) -> None:
            if any(key in e["payload"].get("waives", []) for e in exceptions):
                return
            p, state = setting(key)
            if state == "timing":
                out.append(("SEMANTIC_REVIEW", f"{key} settled after the expense"))
            elif state == "missing":
                out.append(("SEMANTIC_REVIEW", f"{key} not set"))
            else:
                for r in p.get("rules", []):
                    if all(getattr(case, k) == v for k, v in r.get("where", {}).items()):
                        if amount > r["max_amount"]:
                            out.append(("BLOCK" if p.get("outside") == "BLOCK" else "SEMANTIC_REVIEW", f"over {key}"))
                        return
                out.append(("SEMANTIC_REVIEW", f"{key} does not cover this case"))

        if case.manager_approved != "yes":
            if case.category in ("hotel", "travel"):
                out.append(("REQUEST_AUTHORITY", "needs manager"))
            elif case.category in ("meal", "equipment"):
                p, state = setting("approval.scope")
                if state != "ok":
                    out.append(("SEMANTIC_REVIEW", "approval.scope not set"))
                elif p.get("value") == "ALL":
                    out.append(("REQUEST_AUTHORITY", "needs manager"))
        if case.category == "hotel":
            capped("hotel.reasonable")
        elif case.category == "meal":
            if float(case.alcohol_gbp or 0) > 0 or float(case.tip_gbp or 0) > 0:
                out.append(("BLOCK", "alcohol or tip"))
            if case.purpose == "Team celebration":
                if not exceptions:
                    out.append(("REQUEST_AUTHORITY", "celebration needs owner approval"))
            else:
                capped("meal.modest")
        elif case.category == "equipment":
            if case.catalog_available == "no":
                if case.catalog_unavailability_documented != "yes":
                    out.append(("REQUEST_FACT", "unavailability not documented"))
            elif limits["equipment_deminimis"] is None or amount > limits["equipment_deminimis"]:
                capped("equipment.necessity")
        if case.requested_exception == "yes" and case.purpose != "Team celebration" and not exceptions:
            out.append(("REQUEST_AUTHORITY", "exception requested"))
        if not out and self.adopted and self.adopted["closure"] != "ALL_CLAUSES_SATISFIED":
            out.append(("REQUEST_AUTHORITY", "no sufficiency grant"))
        return Decision.of(out, used, head["policy_version"])

    # ------------------------------------------------------------------ payment step
    def execute(self, case: Case, at: str) -> tuple[bool, str]:
        h = case.action_hash()
        if "exact_one_shot" in self.on and h in self.paid:
            return False, "already paid"
        d = self.decide(case, at=at, known_at=at)
        if d.outcome != "CLEAR":
            return False, d.outcome
        if "exact_one_shot" in self.on:
            head = self._head(at)
            for e in head["exceptions"]:
                if e["id"] in d.relied_on:
                    self.used[e["id"]] = h
        self.paid.append(h)
        return True, "paid"
