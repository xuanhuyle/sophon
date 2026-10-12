"""Normalized semantic claim of an E5 requirement version and its meaning hash (PROTOCOL.md §2.3).

An approval of a requirement version is bound to: the governing document's content sha256, the clause id and
version, and this normalized claim's sha256. Changing any atom's operator, value, unit, fact kind, grain, period or
aggregation, the effective window or the supersession changes the hash. Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation

ATOM_KEYS = ("atom_id", "kind", "fact_kind", "op", "value", "unit", "aggregation", "period", "grain")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canon_value(v):
    """Numeric strings in canonical plain decimal form (\"100.00\" -> \"100\"); other values unchanged."""
    if isinstance(v, str):
        try:
            d = Decimal(v)
        except InvalidOperation:
            return v
        if d.is_finite():
            return format(d.normalize(), "f")
    return v


def normalized_claim(ir: dict) -> dict:
    gs = ir["governing_source"]
    atoms = []
    for a in sorted(ir["requirement"]["atoms"], key=lambda a: a["atom_id"]):
        x = {k: a.get(k) for k in ATOM_KEYS if a.get(k) is not None}
        if "value" in x:
            x["value"] = canon_value(x["value"])
        atoms.append(x)
    sup = ir.get("supersedes")
    return {"series": ir["series"], "clause_id": gs["clause_id"], "clause_version": gs["clause_version"],
            "effective_from": gs["effective_from"], "effective_to": gs.get("effective_to"),
            "supersedes": None if sup is None else {"version_id": sup["version_id"], "for_order_dates_from": sup["for_order_dates_from"]},
            "atoms": atoms}


def meaning_sha(ir: dict) -> str:
    return sha_text(canon(normalized_claim(ir)))
