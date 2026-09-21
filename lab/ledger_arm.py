"""Arm L: a small authority ledger. Append-only typed acts, checked for issuer power when they are recorded,
evaluated by time when a case is decided, and bound to the exact action when it is executed.

This is the *recommended thin layer*, not the ten-module control plane of the viability report. `faults` exists
only so that lab/probes.py can mutation-test the probe suite against this arm.
"""
from __future__ import annotations

from .model import ACT_TYPES, OPEN_TERMS, Case, Decision, Receipt, ts

CATEGORIES = ("hotel", "meal", "equipment", "travel")
CONSTRAINTS = {"finance_threshold": 1000.0, "cfo_threshold": 5000.0, "equipment_deminimis": None}
ROOT_ONLY = {"AMEND_SOURCE", "DELEGATE", "ADD_CONSTRAINT", "RELAX_CONSTRAINT"}
SUSPENDABLE = {"INTERPRET_OPEN_STANDARD", "ADD_CONSTRAINT", "RELAX_CONSTRAINT", "CASE_EXCEPTION"}


class LedgerArm:
    name = "ledger"

    def __init__(self, root_owner: str, faults: frozenset[str] = frozenset()):
        self.root_owner = root_owner        # trust anchor: set out of band; identities are assumed authenticated
        self.faults = faults
        self.adoption: dict | None = None
        self.acts: list[dict] = []          # accepted acts, append-only
        self.rejected: list[dict] = []      # kept for audit; never evaluated
        self.proposals: list[dict] = []     # model- or human-drafted; never evaluated
        self.consumed: dict[str, str] = {}  # exception act id -> action hash that used it
        self.executed: dict[str, str] = {}  # action hash -> time executed

    # ------------------------------------------------------------------ recording authority
    def adopt(self, issuer: str, at: str, policy_version: str, closure: str = "ALL_CLAUSES_SATISFIED") -> Receipt:
        if issuer != self.root_owner:
            return Receipt(False, "only the designated owner can adopt a policy")
        if self.adoption:
            return Receipt(False, "already adopted; change the policy with AMEND_SOURCE")
        self.adoption = {"id": "ADOPT-1", "issuer": issuer, "recorded_at": at, "effective_from": at,
                         "policy_version": policy_version, "closure": closure}
        return Receipt(True, act_id="ADOPT-1")

    def propose(self, proposal: dict) -> Receipt:
        self.proposals.append(proposal)
        if "proposal_has_force" in self.faults:
            return self.record({**proposal, "issuer": self.root_owner})
        return Receipt(True, "stored as a proposal; it has no effect until an empowered person records an act")

    def record(self, act: dict) -> Receipt:
        act = {"effective_from": act.get("recorded_at"), "expires_at": None, "supersedes": None, **act}
        why = self._why_invalid(act)
        if why:
            self.rejected.append({**act, "rejected_because": why})
            return Receipt(False, why)
        act["id"] = f"ACT-{len(self.acts) + 1}"
        self.acts.append(act)
        return Receipt(True, act_id=act["id"])

    def _why_invalid(self, a: dict) -> str | None:
        f = self.faults
        if a.get("type") not in ACT_TYPES:
            return "unknown act type"
        if (not self.adoption or ts(a["recorded_at"]) < ts(self.adoption["effective_from"])) and "adoption_not_required" not in f:
            return "no adopted policy at the time of recording: there is no normative root"
        if self.acts and ts(a["recorded_at"]) < ts(self.acts[-1]["recorded_at"]):
            return "backdated record: the ledger is append-only in time"
        if ts(a["effective_from"]) < ts(a["recorded_at"]) and "allow_retroactive" not in f:
            return "retroactive effect: effective_from precedes the time of recording"
        if a.get("policy_version") != self.policy_version(a["recorded_at"], a["recorded_at"]):
            return "targets a policy version that is not the one in force"
        p = a.get("payload", {})
        if a["type"] == "INTERPRET_OPEN_STANDARD" and "untyped_payloads" not in f:
            if p.get("term") not in OPEN_TERMS or set(p) - {"term", "rules", "value", "outside"}:
                return "an interpretation may only bind a declared open term; it cannot write a constraint"
        if a["type"] in ("ADD_CONSTRAINT", "RELAX_CONSTRAINT") and p.get("constraint") not in CONSTRAINTS:
            return "unknown constraint"
        if a["type"] == "CASE_EXCEPTION" and p.get("claimant") == a["issuer"] and "allow_self_dealing" not in f:
            return "self-dealing: the issuer is the beneficiary"
        if a["type"] == "REVOKE":
            target = self._by_id(p.get("target"))
            if not target:
                return "revocation of an unknown act"
            if a["issuer"] not in (self.root_owner, target["issuer"]):
                return "only the owner or the original issuer may revoke"
            return None
        if a["supersedes"]:
            old = self._by_id(a["supersedes"])
            if not old or old["type"] != a["type"] or old["payload"].get("term") != p.get("term"):
                return "supersedes nothing comparable"
            if a["issuer"] not in (self.root_owner, old["issuer"]):
                return "only the owner or the original issuer may supersede"
        return None if "skip_power_check" in f else self._power_gap(a)

    def _power_gap(self, a: dict) -> str | None:
        if a["issuer"] == self.root_owner:
            return None
        if a["type"] in ROOT_ONLY:
            return f"{a['type']} is reserved to the owner"
        p = a.get("payload", {})
        for d in self.acts:
            g = d.get("payload", {})
            if d["type"] != "DELEGATE" or g.get("delegate") != a["issuer"]:
                continue
            if not self._in_force(d, a["recorded_at"], a["recorded_at"]):
                continue
            if a["type"] not in g.get("act_types", []):
                continue
            if "ignore_delegation_bounds" in self.faults:
                return None
            if a["type"] == "CASE_EXCEPTION":
                if p.get("category") not in g.get("categories", []):
                    continue
                if not (isinstance(p.get("max_amount"), (int, float)) and p["max_amount"] <= g.get("max_amount", 0)):
                    continue
            if a["type"] == "INTERPRET_OPEN_STANDARD" and p.get("term") not in g.get("terms", []):
                continue
            return None
        return "issuer holds no power, in force when the act was recorded, that covers this act"

    # ------------------------------------------------------------------ time
    def _by_id(self, act_id):
        return next((x for x in self.acts if x["id"] == act_id), None)

    def policy_version(self, t: str, known_at: str) -> str | None:
        if not self.adoption or ts(self.adoption["effective_from"]) > ts(t):
            return None
        v = self.adoption["policy_version"]
        for a in self.acts:
            if a["type"] == "AMEND_SOURCE" and ts(a["recorded_at"]) <= ts(known_at) and ts(a["effective_from"]) <= ts(t):
                v = a["payload"]["new_policy_version"]
        return v

    def _in_force(self, a: dict, t: str, known_at: str) -> bool:
        f = self.faults
        starts = a["recorded_at"] if "ignore_effective_from" in f else a["effective_from"]
        if ts(a["recorded_at"]) > ts(known_at) or ts(starts) > ts(t):
            return False
        if a["expires_at"] and ts(t) >= ts(a["expires_at"]) and "ignore_expiry" not in f:
            return False
        for b in self.acts:
            if ts(b["recorded_at"]) > ts(known_at) or ts(b["effective_from"]) > ts(t):
                continue
            if b["type"] == "REVOKE" and b["payload"]["target"] == a["id"] and "ignore_revocation" not in f:
                return False
            if b["supersedes"] == a["id"] and "ignore_supersession" not in f:
                return False     # fail closed: a superseded act never revives, even if its successor is revoked
            if b["type"] == "AMEND_SOURCE" and a["type"] in SUSPENDABLE and ts(b["effective_from"]) > ts(a["effective_from"]) \
                    and a["id"] not in b["payload"].get("survivors", []) and "ignore_amendment_suspension" not in f:
                return False     # clause 8: an amendment suspends every settlement it does not name as surviving
        return True

    def _live(self, kind: str, case: Case, at: str, known_at: str, want) -> tuple[list[dict], bool]:
        """Acts of `kind` matching `want`, in force when the expense was incurred AND when it is decided.
        Second value: True if something is in force now but was not when the expense was incurred."""
        now = [a for a in self.acts if a["type"] == kind and want(a) and self._in_force(a, at, known_at)]
        if "ignore_version_timing" in self.faults:
            return now, False
        both = [a for a in now if self._in_force(a, case.decision_time, known_at)]
        return both, len(both) < len(now)

    # ------------------------------------------------------------------ deciding
    def decide(self, case: Case, at: str | None = None, known_at: str | None = None) -> Decision:
        at = at or case.decision_time
        known_at = known_at or at
        version = self.policy_version(at, known_at)
        if version is None and "adoption_not_required" not in self.faults:
            return Decision.of([("REQUEST_AUTHORITY", "no adopted policy: there is no normative root")], [], None)
        issues: list[tuple[str, str]] = []
        relied: list[str] = [self.adoption["id"]] if self.adoption else []

        if case.category not in CATEGORIES and "unknown_category_clears" not in self.faults:
            return Decision.of([("REQUEST_AUTHORITY", "action family outside the adopted surface")], relied, version)

        limits = dict(CONSTRAINTS)
        kinds = ("ADD_CONSTRAINT", "RELAX_CONSTRAINT") + (("INTERPRET_OPEN_STANDARD",) if "untyped_payloads" in self.faults else ())
        for kind in kinds:
            acts, timing = self._live(kind, case, at, known_at, lambda a: "constraint" in a["payload"])
            for a in acts:
                limits[a["payload"]["constraint"]] = a["payload"]["value"]
                relied.append(a["id"])
            if timing:
                issues.append(("SEMANTIC_REVIEW", "version_timing: a constraint changed after the expense was incurred"))

        if not case.purpose.strip():
            issues.append(("REQUEST_FACT", "purpose not documented (cl.1)"))
        if case.receipt_present == "no" if "blank_receipt_passes" in self.faults else case.receipt_present != "yes":
            issues.append(("REQUEST_FACT", "supporting evidence not present (cl.1)"))
        if case.approver == case.claimant:
            issues.append(("BLOCK", "self-approval (cl.1)"))
        amount = case.amount
        if amount is None and "nan_passes" not in self.faults:
            issues.append(("REQUEST_FACT", "amount is not a finite positive number"))
        amount = amount if amount is not None else 0.0
        if amount > limits["finance_threshold"] and case.finance_approved != "yes":
            issues.append(("REQUEST_AUTHORITY", "Finance approval required (cl.5)"))
        if amount > limits["cfo_threshold"] and case.cfo_approved != "yes":
            issues.append(("REQUEST_AUTHORITY", "CFO approval required (cl.5)"))

        def matching_exceptions() -> list[dict]:
            def want(a):
                p = a["payload"]
                if "exception_matches_any_case" in self.faults:
                    return p["category"] == case.category
                exact = p["case_id"] == case.case_id and p["claimant"] == case.claimant and p["category"] == case.category
                within = "ignore_amount_cap" in self.faults or amount <= p["max_amount"]
                unused = self.consumed.get(a["id"]) in (None, case.action_hash()) or "no_consumption" in self.faults
                return exact and within and unused
            acts, _ = self._live("CASE_EXCEPTION", case, at, known_at, want)
            relied.extend(a["id"] for a in acts)
            return acts

        exceptions = matching_exceptions()

        def term(name: str, satisfied, outside_issue: tuple[str, str] | None = None) -> None:
            if any(name in a["payload"].get("waives", []) for a in exceptions):
                return      # a case-specific exception may waive a named open term for this exact case only
            if "practice_becomes_permission" in self.faults and len(self.executed) >= 3:
                return
            acts, timing = self._live("INTERPRET_OPEN_STANDARD", case, at, known_at, lambda a: a["payload"]["term"] == name)
            if timing:
                issues.append(("SEMANTIC_REVIEW", f"version_timing: '{name}' was settled after the expense was incurred (cl.8)"))
                return
            if not acts:
                issues.append(("SEMANTIC_REVIEW", f"open term '{name}' has no settlement in force"))
                return
            verdicts = {satisfied(a["payload"]) for a in acts}
            relied.extend(a["id"] for a in acts)
            if len(verdicts) > 1:
                issues.append(("CONFLICT", f"settlements of '{name}' in force disagree on this case"))
            elif verdicts == {"outside"}:
                outside = {a["payload"].get("outside", "SEMANTIC_REVIEW") for a in acts}
                issues.append(outside_issue or ("BLOCK" if outside == {"BLOCK"} else "SEMANTIC_REVIEW",
                                                f"outside the settled meaning of '{name}'"))
            elif verdicts == {"uncovered"}:
                issues.append(("SEMANTIC_REVIEW", f"the settlement of '{name}' does not reach this case"))

        def cap_rule(p: dict) -> str:
            for r in p.get("rules", []):
                if all(getattr(case, k) == v for k, v in r.get("where", {}).items()):
                    return "within" if amount <= r["max_amount"] else "outside"
            return "uncovered"

        if case.category in ("hotel", "travel") and case.manager_approved != "yes":
            issues.append(("REQUEST_AUTHORITY", "manager approval required for travel (cl.2)"))
        if case.category in ("meal", "equipment") and case.manager_approved != "yes":
            term("approval.scope", lambda p: "outside" if p.get("value") == "ALL" else "within",
                 ("REQUEST_AUTHORITY", "manager approval required ('approval.scope' settled as ALL)"))
        if case.category == "hotel":
            term("hotel.reasonable", cap_rule)
        if case.category == "meal":
            if float(case.alcohol_gbp or 0) > 0 or float(case.tip_gbp or 0) > 0:
                issues.append(("BLOCK", "alcohol or tip included in the amount submitted (cl.3)"))
            if case.purpose == "Team celebration":
                if not exceptions:
                    issues.append(("REQUEST_AUTHORITY", "celebration meal needs a case-specific owner approval (cl.3)"))
            else:
                term("meal.modest", cap_rule)
        if case.category == "equipment":
            if case.catalog_available == "no":
                if case.catalog_unavailability_documented != "yes":
                    issues.append(("REQUEST_FACT", "catalogue unavailability not documented (cl.4)"))
            elif limits["equipment_deminimis"] is None or amount > limits["equipment_deminimis"]:
                term("equipment.necessity", cap_rule)
        if case.requested_exception == "yes" and case.purpose != "Team celebration" and not exceptions:
            issues.append(("REQUEST_AUTHORITY", "requested exception needs a case-specific owner approval (cl.6)"))

        if exceptions and "exception_overrides_block" in self.faults:
            issues = [i for i in issues if i[0] != "BLOCK"]
        if not issues and self.adoption and self.adoption["closure"] != "ALL_CLAUSES_SATISFIED":
            issues.append(("REQUEST_AUTHORITY", "policy states necessary conditions only and no sufficiency grant applies"))
        return Decision.of(issues, relied, version)

    # ------------------------------------------------------------------ executing
    def execute(self, case: Case, at: str) -> tuple[bool, str]:
        """Fresh decision at execution time, bound to the exact action; one effect per action."""
        h = case.action_hash()
        if h in self.executed and "no_consumption" not in self.faults:
            return False, "already executed: no second effect"
        d = self.decide(case, at=at, known_at=at)
        if d.outcome != "CLEAR":
            return False, f"not authorized at execution time: {d.outcome}"
        for act_id in d.relied_on:
            a = self._by_id(act_id)
            if a and a["type"] == "CASE_EXCEPTION":
                self.consumed[act_id] = h
        self.executed[h] = at
        return True, "executed"
