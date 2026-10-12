"""E3 minimal typed governance IR (E3-IR-0.1), PROTOCOL.md §2. Plain Pydantic v2 models, extra fields forbidden.

The models only check shape and types. Every cross-object rule (source identity, catalog resolution, approvals,
evidence) lives in validator.py, and the status is computed there; it has no input field here.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


Unit = Optional[Literal["CURRENCY", "CURRENCY_PER_UNIT", "UNIT", "COUNT"]]


class GoverningSource(_M):
    source_id: str
    path: str
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    clause_id: str
    clause_version: int = Field(ge=1)
    observed_at: datetime
    effective_from: date
    effective_to: Optional[date]
    provenance: Literal["LAB_AUTHORED"]


class Atom(_M):
    atom_id: str
    span: tuple[int, int]
    text: str
    kind: Literal["MEASURE", "PREDICATE", "GROUP_BY"]
    fact_kind: Optional[str]
    op: Optional[Literal["EQ", "GE", "IS_TRUE"]] = None
    value: Optional[str] = None
    unit: Unit = None
    aggregation: Optional[Literal["SUM", "COUNT_DISTINCT"]] = None
    period: Optional[Literal["CALENDAR_YEAR"]] = None
    grain: Optional[Literal["ORDER_LINE"]] = None


class Requirement(_M):
    text: str
    atoms: list[Atom] = Field(min_length=1)
    population: str
    exceptions: list[str]


class SemanticObject(_M):
    type: Literal["metric", "dimension", "time_dimension"]
    name: str


class Derivation(_M):
    pattern: Literal["LINE_GRAIN_RATIO_THRESHOLD"]
    numerator_metric: str
    denominator_metric: str
    line_entity: str
    threshold: str
    guards_declared: list[str]
    guard_receipt_id: Optional[str]


class Equivalence(_M):
    field: str
    fact_kind: str
    statement: str
    claimed_approval_id: Optional[str]


class Binding(_M):
    kind: Literal["DIRECT", "DERIVED", "CANDIDATE_EQUIVALENCE", "MISSING"]
    semantic_object: Optional[SemanticObject]
    physical_lineage: list[str]
    value_override: Optional[str] = None
    derivation: Optional[Derivation] = None
    equivalence: Optional[Equivalence] = None
    missing_fact: Optional[str] = None


class NativeQuery(_M):
    metric: str
    group_by: list[str]
    where: list[str]


class Reading(_M):
    reading_id: str
    statement: str
    atom_fact_kinds: dict[str, str] = Field(default_factory=dict)
    bindings: dict[str, Binding]
    native_query: Optional[NativeQuery]
    native_receipt_id: Optional[str]
    oracle_id: Optional[str]


class Interpretation(_M):
    claimed_state: Literal["PROPOSED", "UNRESOLVED_INTERPRETATION", "LAB_APPROVED"]
    claimed_approval_ids: list[str]
    readings: list[Reading] = Field(min_length=1)
    open_questions: list[str]


class VerificationRequest(_M):
    semantic_manifest_sha256: str
    raw_csv_sha256: dict[str, str]


class Record(_M):
    ir_version: Literal["E3-IR-0.1"]
    record_id: str
    proposed_by_role: str
    governing_source: GoverningSource
    requirement: Requirement
    interpretation: Interpretation
    lab_assumptions: list[str]
    verification_request: VerificationRequest


class ApprovalScope(_M):
    source_id: str
    source_sha256: str
    clause_id: str
    clause_version: int


class Claim(_M):
    kind: Literal["INTERPRETATION_CHOICE", "SEMANTIC_EQUIVALENCE"]
    record_id: str
    reading_id: Optional[str] = None
    fact_kind: Optional[str] = None
    field: Optional[str] = None
    statement: Optional[str] = None


class Approval(_M):
    approval_id: str
    provenance: Literal["LAB_SIMULATED"]
    approver_role: str
    claim: Claim
    scope: ApprovalScope
    known_at: datetime
    effective_from: date
    effective_to: Optional[date]


class Revocation(_M):
    revocation_id: str
    provenance: Literal["LAB_SIMULATED"]
    revokes: str
    approver_role: str
    known_at: datetime


STATUS_KEYS = {"status", "verified", "verification_status"}
STATUSES = ("STRUCTURALLY_INVALID", "MISSING_REQUIRED_FACT", "MEANING_UNRESOLVED", "NOT_VERIFIED",
            "VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS")
