"""Pattern-specific expressibility check (PROTOCOL.md §6). Not a planner.

Pattern: a per-line threshold on a charged unit price `u` that is not a declared dimension, derived natively as
    Metric(revenue, group_by=[line entity]) >= T * Metric(quantity, group_by=[line entity]).
This is equivalent to `u >= T` per line only if every guard holds:
    quantity_positive      every line has quantity >= 1 (q = 0 admits every line; q < 0 reverses the inequality)
    revenue_exact          revenue == quantity * unit_price exactly for every line (no rounding)
    price_source_exact     warehouse unit_price == source unit_price, source has <= 2 decimals
    line_entity_unique     the group_by entity is unique per line and no line is lost or duplicated by joins
    exact_comparison       the compiled comparison uses exact numeric types (no FLOAT/DOUBLE)
and the native filter is accepted and reproduces the independent oracle.
"""
from __future__ import annotations

DIRECTLY_EXPOSED = "DIRECTLY_EXPOSED"
DERIVABLE = "NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS"
UNSUPPORTED = "SOURCE_PRESENT_BUT_UNSUPPORTED_BY_NATIVE_SEMANTICS"
NOT_FOUND = "NOT_FOUND_IN_BOUNDED_ESTATE"

GUARDS = ("quantity_positive", "revenue_exact", "price_source_exact", "line_entity_unique", "exact_comparison")


def classify(evidence: dict) -> dict:
    """evidence keys: source_column_present, direct_dimension_present, native_witness_accepted,
    native_equals_oracle_yearly, native_equals_oracle_lines, guards {name: True|False|None}.
    Missing or None counts as not established (refuses the derivation)."""
    if not evidence.get("source_column_present"):
        return {"classification": NOT_FOUND, "failed": ["source_column_present"]}
    if evidence.get("direct_dimension_present"):
        return {"classification": DIRECTLY_EXPOSED, "failed": []}
    guards = evidence.get("guards") or {}
    failed = [g for g in GUARDS if guards.get(g) is not True]
    failed += [k for k in ("native_witness_accepted", "native_equals_oracle_yearly", "native_equals_oracle_lines")
               if evidence.get(k) is not True]
    if failed:
        return {"classification": UNSUPPORTED, "failed": failed}
    return {"classification": DERIVABLE, "failed": []}
