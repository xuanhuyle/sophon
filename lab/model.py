"""Shared vocabulary for both arms: cases, decisions, settlement requests. Standard library only."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOLO = ROOT / "evidence" / "sophon_solo"

# Most severe first. A decision's headline is the most severe issue found; every issue is still listed.
ORDER = ["BLOCK", "REQUEST_FACT", "REQUEST_AUTHORITY", "CONFLICT", "SEMANTIC_REVIEW", "CLEAR"]

# The open terms and relaxable bright lines of the draft policy, as read in lab/READING.md.
OPEN_TERMS = ("hotel.reasonable", "meal.modest", "equipment.necessity", "approval.scope")
ACT_TYPES = ("INTERPRET_OPEN_STANDARD", "ADD_CONSTRAINT", "RELAX_CONSTRAINT", "CASE_EXCEPTION", "AMEND_SOURCE",
             "DELEGATE", "REVOKE")


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s)


def policy_hash() -> str:
    return hashlib.sha256((SOLO / "draft_policy.md").read_bytes()).hexdigest()


@dataclass(frozen=True)
class Case:
    case_id: str
    sequence: int
    expense_date: str
    category: str
    amount_raw: str
    claimant: str
    approver: str
    purpose: str
    destination: str
    receipt_present: str
    manager_approved: str
    finance_approved: str
    cfo_approved: str
    catalog_available: str
    catalog_unavailability_documented: str
    alcohol_gbp: str
    tip_gbp: str
    requested_exception: str
    notes: str

    @property
    def amount(self) -> float | None:
        """None when the amount is not a finite, positive number (NaN/inf/negative/blank never pass a threshold)."""
        try:
            v = float(self.amount_raw)
        except (TypeError, ValueError):
            return None
        return v if math.isfinite(v) and v > 0 else None

    @property
    def decision_time(self) -> str:
        return f"{self.expense_date}T12:00:00"

    def action_hash(self) -> str:
        """The exact action an execution permit is bound to: who is paid, how much, for what."""
        body = json.dumps({"case": self.case_id, "claimant": self.claimant, "amount": self.amount_raw,
                           "category": self.category}, sort_keys=True)
        return hashlib.sha256(body.encode()).hexdigest()

    def but(self, **changes) -> "Case":
        d = {**self.__dict__, **changes}
        return Case(**d)


def load_cases() -> list[Case]:
    with (SOLO / "cases.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    names = Case.__dataclass_fields__.keys()
    out = []
    for r in rows:
        r = {**r, "amount_raw": r["amount_gbp"], "sequence": int(r["sequence"])}
        out.append(Case(**{k: r[k] for k in names}))
    return out


@dataclass
class Decision:
    outcome: str
    issues: list[tuple[str, str]] = field(default_factory=list)   # (outcome, reason)
    relied_on: list[str] = field(default_factory=list)            # ids of authority acts the outcome depends on
    policy_version: str | None = None

    @staticmethod
    def of(issues: list[tuple[str, str]], relied_on: list[str], policy_version: str | None) -> "Decision":
        outcome = min((i[0] for i in issues), key=ORDER.index) if issues else "CLEAR"
        return Decision(outcome, sorted(set(issues)), sorted(set(relied_on)), policy_version)

    def reasons(self) -> list[str]:
        return [r for _, r in self.issues]


@dataclass
class Receipt:
    """What an arm says when asked to record an act. `accepted` False means the act has no effect."""
    accepted: bool
    reason: str = ""
    act_id: str | None = None
