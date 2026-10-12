"""E3 read-only validator (PROTOCOL.md §3). Pure function of its inputs; computes the status, never reads one.

validate(record, approvals, revocations, ctx, eval_known_at, eval_effective_at) -> dict
ctx: Context(root, roster, registry, catalog, native, guards, oracle) - all plain dicts loaded from committed files.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from pydantic import ValidationError

import models as M

V, U, NV, MISS, INV = M.STATUSES[4], M.STATUSES[2], M.STATUSES[3], M.STATUSES[1], M.STATUSES[0]


@dataclass(frozen=True)
class Context:
    root: Path
    roster: dict
    registry: dict
    catalog: dict
    native: dict
    guards: dict
    oracle: dict


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _dt(x) -> datetime:
    return x if isinstance(x, datetime) else datetime.fromisoformat(str(x).replace("Z", "+00:00"))


def _d(x) -> date:
    return x if isinstance(x, date) else date.fromisoformat(str(x))


def dim_where(name: str, value: str) -> str:
    return f"{{{{ Dimension('{name}') }}}} = '{value}'"


def validate(record: dict, approvals: list[dict], revocations: list[dict], ctx: Context,
             eval_known_at, eval_effective_at) -> dict:
    t_known, t_eff = _dt(eval_known_at), _d(eval_effective_at)
    errors: list[dict] = []
    reasons: set[str] = set()

    def err(code: str, path: str, detail: str = "") -> None:
        errors.append({"code": code, "path": path, "detail": detail})

    out = {"record_id": record.get("record_id"), "record_sha256": sha_text(canon(record)),
           "eval_known_at": str(eval_known_at), "eval_effective_at": str(eval_effective_at)}

    # ---------------------------------------------------------------- I1 status is computed, never input
    raw = dict(record)
    for k in sorted(M.STATUS_KEYS & set(raw)):
        err("STATUS_FIELD_FORBIDDEN", k, "status is an output of the validator, not an input")
        raw.pop(k)
    try:
        rec = M.Record.model_validate(raw)
    except ValidationError as e:
        for x in e.errors():
            err("SCHEMA_INVALID", ".".join(map(str, x["loc"])), x["msg"])
        return _finish(out, errors, reasons, None, {}, {}, [], [], False)

    # ---------------------------------------------------------------- I5 as-of visibility (before anything else)
    vis_app, vis_rev = [], []
    for a in approvals:
        try:
            ap = M.Approval.model_validate(a)
        except ValidationError:
            continue  # malformed approvals never count; they are also never echoed
        if ap.known_at <= t_known:
            vis_app.append(ap)
    for r in revocations:
        try:
            rv = M.Revocation.model_validate(r)
        except ValidationError:
            continue
        if rv.known_at <= t_known:
            vis_rev.append(rv)

    gs, req, interp = rec.governing_source, rec.requirement, rec.interpretation

    # ---------------------------------------------------------------- I2 source identity and time
    src_path = (ctx.root / gs.path).resolve()
    src_text = src_path.read_text(encoding="utf-8") if src_path.is_file() and ctx.root.resolve() in src_path.parents else None
    actual_sha = sha_text(src_text) if src_text is not None else None
    if actual_sha != gs.content_sha256:
        err("SOURCE_HASH_MISMATCH", "governing_source.content_sha256", "declared hash differs from the source file")
    if src_text is None or f"[{gs.clause_id} v{gs.clause_version}] {req.text}" not in src_text:
        err("SOURCE_CLAUSE_MISMATCH", "governing_source", "clause id/version/text not found in the source")
    if gs.effective_to is not None and gs.effective_to < gs.effective_from:
        err("TEMPORAL_ORDER_INVALID", "governing_source.effective_to", "effective_to precedes effective_from")
    if gs.observed_at > t_known:
        err("SOURCE_NOT_YET_KNOWN", "governing_source.observed_at", "source observed after the evaluation knowledge time")
    atoms = {a.atom_id: a for a in req.atoms}
    if len(atoms) != len(req.atoms):
        err("SCHEMA_INVALID", "requirement.atoms", "duplicate atom_id")
    for i, a in enumerate(req.atoms):
        s, e = a.span
        if not (0 <= s < e <= len(req.text)) or req.text[s:e] != a.text:
            err("SPAN_TEXT_MISMATCH", f"requirement.atoms.{i}.span", f"text[{s}:{e}] != atom text")

    # ---------------------------------------------------------------- I4 approval validity
    reg, roster, cat = ctx.registry, ctx.roster, ctx.catalog
    readings = {r.reading_id: r for r in interp.readings}
    equiv_targets = {(b.equivalence.fact_kind, b.equivalence.field)
                     for r in interp.readings for b in r.bindings.values()
                     if b.kind == "CANDIDATE_EQUIVALENCE" and b.equivalence is not None}

    def role_covers(role: str, claim: M.Claim, source_id: str) -> bool:
        spec = roster["roles"].get(role)
        if spec is None or claim.kind not in spec.get("may_approve", []):
            return False
        if claim.kind == "INTERPRETATION_CHOICE":
            return source_id in spec.get("source_ids", [])
        return any((claim.field or "").startswith(p) for p in spec.get("field_prefixes", []))

    app_report, valid_app = [], []
    for ap in sorted(vis_app, key=lambda x: x.approval_id):
        if ap.claim.record_id != rec.record_id:
            continue  # belongs to another record
        fails = []
        if ap.approver_role in roster.get("never_approvers", []) or ap.approver_role == rec.proposed_by_role:
            fails.append("SELF_APPROVAL")
        elif ap.approver_role not in roster["roles"]:
            fails.append("APPROVER_NOT_IN_ROSTER")
        elif not role_covers(ap.approver_role, ap.claim, ap.scope.source_id):
            fails.append("APPROVER_NOT_AUTHORIZED_FOR_CLAIM")
        sc = ap.scope
        if (sc.source_id != gs.source_id or sc.source_sha256 != gs.content_sha256 or sc.source_sha256 != actual_sha
                or sc.clause_id != gs.clause_id or sc.clause_version != gs.clause_version):
            fails.append("APPROVAL_SCOPE_MISMATCH")
        elif ap.claim.kind == "INTERPRETATION_CHOICE" and ap.claim.reading_id not in readings:
            fails.append("APPROVAL_SCOPE_MISMATCH")
        elif ap.claim.kind == "SEMANTIC_EQUIVALENCE" and (ap.claim.fact_kind, ap.claim.field) not in equiv_targets:
            fails.append("APPROVAL_SCOPE_MISMATCH")
        if ap.known_at < gs.observed_at:
            fails.append("APPROVAL_BEFORE_SOURCE_OBSERVED")
        if not (ap.effective_from <= t_eff and (ap.effective_to is None or t_eff <= ap.effective_to)):
            fails.append("APPROVAL_NOT_EFFECTIVE")
        for rv in vis_rev:
            if rv.revokes == ap.approval_id and role_covers(rv.approver_role, ap.claim, ap.scope.source_id):
                fails.append("APPROVAL_REVOKED")
        app_report.append({"approval_id": ap.approval_id, "claim_kind": ap.claim.kind, "valid": not fails, "failures": fails})
        reasons.update(fails)
        if not fails:
            valid_app.append(ap)
    valid_ids = {a.approval_id for a in valid_app}

    # I1 (claims): a record may only claim what visible, valid approvals give it
    claimed = list(interp.claimed_approval_ids)
    if interp.claimed_state == "LAB_APPROVED" and not claimed:
        err("APPROVAL_CLAIM_WITHOUT_EVIDENCE", "interpretation.claimed_state", "LAB_APPROVED claimed without approval ids")
    for cid in claimed:
        ok = any(a.approval_id == cid and a.claim.kind == "INTERPRETATION_CHOICE" for a in valid_app)
        if not ok:
            err("APPROVAL_CLAIM_WITHOUT_EVIDENCE", "interpretation.claimed_approval_ids", f"{cid} is not a visible valid interpretation approval")

    # ---------------------------------------------------------------- I3 bindings vs catalog / registry / query
    metrics, dims, cols = cat["metrics"], cat["dimensions"], set(cat["warehouse_columns"])
    units = reg["metric_units"]
    patterns = reg["derivation_patterns"]

    def resolve(obj: M.SemanticObject, measure_model: str | None):
        if obj.type == "metric":
            m = metrics.get(obj.name)
            return (m or {}).get("field") if m else None, m is not None
        if obj.type == "time_dimension":
            d = dims.get(f"{obj.name}@{measure_model}") if obj.name.startswith("metric_time__") else dims.get(obj.name)
            return (d or {}).get("field"), d is not None
        d = dims.get(obj.name)
        return (d or {}).get("field"), d is not None

    def fact_kind(reading: M.Reading, a: M.Atom):
        return a.fact_kind or reading.atom_fact_kinds.get(a.atom_id)

    rendered_derived: dict[str, str] = {}
    for r in interp.readings:
        base = f"interpretation.readings.{r.reading_id}"
        for aid in r.bindings:
            if aid not in atoms:
                err("UNDEFINED_PREDICATE", f"{base}.bindings.{aid}", "binding for an atom the requirement does not define")
        for aid in atoms:
            if aid not in r.bindings:
                err("ATOM_UNBOUND", f"{base}.bindings.{aid}", "atom has no binding (use kind MISSING to declare absence)")
        measure_atoms = [a for a in req.atoms if a.kind == "MEASURE"]
        mmetric = r.bindings[measure_atoms[0].atom_id].semantic_object.name if measure_atoms and measure_atoms[0].atom_id in r.bindings \
            and r.bindings[measure_atoms[0].atom_id].semantic_object else None
        mmodel = metrics.get(mmetric or "", {}).get("model")
        for aid, b in r.bindings.items():
            p = f"{base}.bindings.{aid}"
            a = atoms.get(aid)
            if a is not None and fact_kind(r, a) is None:
                err("FACT_KIND_UNDECLARED", p, "atom fact kind not declared by the requirement or the reading")
            for f in b.physical_lineage:
                if f.lower() not in cols:
                    err("UNKNOWN_PHYSICAL_FIELD", p, f)
            if b.kind in ("DIRECT", "CANDIDATE_EQUIVALENCE") and b.semantic_object is None:
                err("SCHEMA_INVALID", p, f"{b.kind} binding needs a semantic object")
            if b.semantic_object is not None:
                field, known = resolve(b.semantic_object, mmodel)
                if not known:
                    err("UNKNOWN_SEMANTIC_OBJECT", p, b.semantic_object.name)
                elif not b.physical_lineage or field != b.physical_lineage[0].lower():
                    err("SEMANTIC_PHYSICAL_MISMATCH", p, f"{b.semantic_object.name} resolves to {field}")
            if a is not None and a.kind == "MEASURE" and b.semantic_object is not None:
                if a.unit != units.get(b.semantic_object.name):
                    err("UNIT_MISMATCH", p, f"atom unit {a.unit} vs metric unit {units.get(b.semantic_object.name)}")
            if b.kind == "CANDIDATE_EQUIVALENCE":
                if b.equivalence is None or not b.physical_lineage or b.equivalence.field != b.physical_lineage[0]:
                    err("SCHEMA_INVALID", p, "candidate equivalence must name the bound field")
                elif b.equivalence.claimed_approval_id is not None and not any(
                        x.approval_id == b.equivalence.claimed_approval_id and x.claim.kind == "SEMANTIC_EQUIVALENCE"
                        and (x.claim.fact_kind, x.claim.field) == (b.equivalence.fact_kind, b.equivalence.field) for x in valid_app):
                    err("APPROVAL_CLAIM_WITHOUT_EVIDENCE", p, f"{b.equivalence.claimed_approval_id} is not a visible valid equivalence approval")
            if b.kind == "DERIVED":
                d = b.derivation
                pat = patterns.get(d.pattern) if d else None
                if d is None or pat is None:
                    err("SCHEMA_INVALID", p, "DERIVED binding needs a known derivation pattern")
                    continue
                num, den = metrics.get(d.numerator_metric), metrics.get(d.denominator_metric)
                if num is None or den is None:
                    err("UNKNOWN_SEMANTIC_OBJECT", p, f"{d.numerator_metric}/{d.denominator_metric}")
                    continue
                if num.get("model") != den.get("model") or d.line_entity != num.get("primary_entity"):
                    err("DERIVATION_GRAIN_INVALID", p, f"line_entity {d.line_entity} is not the primary entity "
                                                       f"{num.get('primary_entity')} of the model defining both measures")
                missing_g = [g for g in pat["required_guards"] if g not in d.guards_declared]
                if missing_g:
                    err("REQUIRED_GUARD_UNDECLARED", p, ",".join(missing_g))
                derived_unit = f"{units.get(d.numerator_metric)}_PER_{units.get(d.denominator_metric)}"
                if a is not None and a.unit != derived_unit:
                    err("UNIT_MISMATCH", p, f"threshold unit {a.unit} vs derived unit {derived_unit}")
                rendered_derived[r.reading_id + "/" + aid] = (pat["where_template"].replace("<numerator>", d.numerator_metric)
                                                              .replace("<denominator>", d.denominator_metric)
                                                              .replace("<line_entity>", d.line_entity).replace("<threshold>", d.threshold))
        # native query must be exactly what the bindings say
        if r.native_query is not None:
            exp_where, derived_ok = [], True
            for a in req.atoms:
                b = r.bindings.get(a.atom_id)
                if b is None or a.kind != "PREDICATE" or b.kind == "MISSING":
                    continue
                if b.kind == "DERIVED":
                    w = rendered_derived.get(r.reading_id + "/" + a.atom_id)
                    if w is None or w not in r.native_query.where:
                        derived_ok = False
                        err("DERIVATION_QUERY_MISMATCH", f"{base}.native_query.where", "rendered derivation template not in the query")
                    exp_where.append(w)
                elif b.semantic_object is not None:
                    exp_where.append(dim_where(b.semantic_object.name, b.value_override or a.value))
            exp_group = [r.bindings[a.atom_id].semantic_object.name for a in req.atoms
                         if a.kind == "GROUP_BY" and a.atom_id in r.bindings and r.bindings[a.atom_id].semantic_object]
            if derived_ok and (r.native_query.metric != mmetric or r.native_query.group_by != exp_group
                               or Counter(r.native_query.where) != Counter(exp_where)):
                err("QUERY_BINDING_MISMATCH", f"{base}.native_query", "query is not the conjunction rendered from the bindings")

    # ---------------------------------------------------------------- I6 meaning
    choices = sorted({a.claim.reading_id for a in valid_app if a.claim.kind == "INTERPRETATION_CHOICE"})
    selected = choices[0] if len(choices) == 1 else None
    if len(choices) > 1:
        reasons.add("CONFLICTING_APPROVALS")
    elif not choices:
        reasons.add("INTERPRETATION_UNRESOLVED" if len(readings) > 1 else "INTERPRETATION_NOT_APPROVED")
    meaning = {"interpretation": "LAB_APPROVED" if selected else ("UNRESOLVED_INTERPRETATION" if len(readings) > 1 else "PROPOSED_NOT_APPROVED"),
               "selected_reading": selected,
               "selecting_approvals": sorted(a.approval_id for a in valid_app
                                             if a.claim.kind == "INTERPRETATION_CHOICE" and a.claim.reading_id == selected) if selected else [],
               "alternatives": {rid: ("NOT_SELECTED" if selected else "CANDIDATE") for rid in readings if rid != selected},
               "open_questions": list(interp.open_questions) if not selected else [],
               "equivalences": {}}
    meaning_ok = selected is not None
    for r in interp.readings:
        for aid, b in r.bindings.items():
            if b.kind != "CANDIDATE_EQUIVALENCE" or b.equivalence is None:
                continue
            ok = [a.approval_id for a in valid_app if a.claim.kind == "SEMANTIC_EQUIVALENCE"
                  and (a.claim.fact_kind, a.claim.field) == (b.equivalence.fact_kind, b.equivalence.field)]
            origin_ok = (reg["field_origins"].get(b.equivalence.field)
                         == reg["fact_kinds"].get(b.equivalence.fact_kind, {}).get("required_origin"))
            state = ("REFUSED_SOURCE_ORIGIN_MISMATCH" if not origin_ok else
                     "LAB_APPROVED" if ok else "NOT_ESTABLISHED_SEMANTIC_EQUIVALENCE")
            meaning["equivalences"][f"{r.reading_id}/{aid}"] = {"field": b.equivalence.field, "fact_kind": b.equivalence.fact_kind,
                                                               "state": state, "approvals": sorted(ok)}
            ok = ok if origin_ok else []
            if not ok and (selected is None or r.reading_id == selected):
                reasons.add("EQUIVALENCE_UNAPPROVED")
                if r.reading_id == selected:
                    meaning_ok = False

    # ---------------------------------------------------------------- I7 coverage: provenance cannot be approved into existence
    origins_present = set(reg["field_origins"].values())
    coverage: dict[str, list[str]] = {}
    cov_reasons: dict[str, set] = {}
    for r in interp.readings:
        unc, rs = [], set()
        for aid, b in r.bindings.items():
            a = atoms.get(aid)
            fk = fact_kind(r, a) if a else None
            spec = reg["fact_kinds"].get(fk or "", {})
            field = b.physical_lineage[0] if b.physical_lineage else None
            bad = None
            if b.kind == "MISSING":
                bad = "MISSING"
            elif b.kind in ("DIRECT", "DERIVED") and field not in spec.get("designated_fields", []):
                bad = "NOT_DESIGNATED_FOR_FACT"
            elif b.kind == "CANDIDATE_EQUIVALENCE" and reg["field_origins"].get(field) != spec.get("required_origin"):
                bad = "SOURCE_ORIGIN_MISMATCH"
                if any(a2.claim.kind == "SEMANTIC_EQUIVALENCE" and a2.claim.field == field and a2.claim.fact_kind == fk
                       for a2 in vis_app if a2.claim.record_id == rec.record_id):
                    rs.add("APPROVAL_CANNOT_CREATE_SOURCE")
            if bad:
                unc.append(aid)
                if bad != "MISSING":
                    rs.add(bad)
                if spec.get("required_origin") not in origins_present:
                    rs.add("REQUIRED_FACT_ABSENT")
        coverage[r.reading_id] = sorted(unc)
        cov_reasons[r.reading_id] = rs
    scope_readings = [selected] if selected else list(readings)
    uncovered = sorted({x for rid in scope_readings for x in coverage[rid]})
    for rid in scope_readings:
        reasons.update(cov_reasons[rid])

    # ---------------------------------------------------------------- I8 behavioural evidence
    evidence, computability = {}, {}
    for r in interp.readings:
        ev_r, rs = _evidence(r, rec, ctx)
        evidence[r.reading_id] = {**ev_r, "reasons": sorted(rs)}
        computability[r.reading_id] = {"native_receipt_id": r.native_receipt_id, "executed": ev_r["executed"]}
        if r.reading_id == selected:
            reasons.update(rs)
    technically_executable = any(c["executed"] for c in computability.values())

    out.update(meaning=meaning, computability=computability, evidence=evidence, approvals=app_report)
    status_inputs = {"uncovered": uncovered, "meaning_ok": meaning_ok,
                     "evidence_ok": bool(selected) and not evidence.get(selected, {}).get("reasons")
                     and evidence.get(selected, {}).get("native_equals_oracle") is True}
    return _finish(out, errors, reasons, status_inputs, meaning, computability, uncovered, app_report, technically_executable)


def _evidence(r: M.Reading, rec: M.Record, ctx: Context):
    rs: set[str] = set()
    ev = {"executed": False, "native_equals_oracle": None, "native_by_period": None, "oracle_by_period": None, "guards": None}
    if r.native_query is None:
        return ev, rs
    nr = ctx.native.get(r.native_receipt_id or "")
    req = rec.verification_request
    if nr is None:
        rs.add("NATIVE_RECEIPT_MISSING")
        return ev, rs
    if sha_text(canon(nr.get("rows"))) != nr.get("rows_sha256"):
        rs.add("RECEIPT_INTEGRITY_FAILED")
    if nr.get("exit_code") != 0:
        rs.add("NATIVE_QUERY_FAILED")
    if nr.get("query") != r.native_query.model_dump():
        rs.add("RECEIPT_QUERY_MISMATCH")
    fp = nr.get("fingerprint") or {}
    if fp.get("semantic_manifest_sha256") != req.semantic_manifest_sha256 or fp.get("raw_csv_sha256") != req.raw_csv_sha256:
        rs.add("RECEIPT_REVISION_MISMATCH")
    ev["executed"] = nr.get("exit_code") == 0 and "RECEIPT_INTEGRITY_FAILED" not in rs and "RECEIPT_QUERY_MISMATCH" not in rs
    metric = r.native_query.metric
    try:
        nat = {row["metric_time__year"][:4]: str(Decimal(row[metric])) for row in nr.get("rows") or []}
    except Exception:  # noqa: BLE001
        nat = None
    ev["native_by_period"] = nat
    orc = ctx.oracle.get(r.oracle_id or "")
    if orc is None:
        rs.add("ORACLE_MISSING")
    else:
        if orc.get("computes") != {"record_id": rec.record_id, "reading_id": r.reading_id}:
            rs.add("ORACLE_READING_MISMATCH")
        if orc.get("raw_csv_sha256") != req.raw_csv_sha256:
            rs.add("ORACLE_REVISION_MISMATCH")
        ob = orc.get("by_year") or {}
        ev["oracle_by_period"] = ob
        eq = nat is not None and set(nat) == set(ob) and all(Decimal(nat[k]) == Decimal(ob[k]) for k in ob)
        ev["native_equals_oracle"] = eq
        if not eq:
            rs.add("NATIVE_ORACLE_MISMATCH")
    # guards of derived bindings, tied to the native receipt's snapshot
    for aid, b in r.bindings.items():
        if b.kind != "DERIVED" or b.derivation is None:
            continue
        pat = ctx.registry["derivation_patterns"].get(b.derivation.pattern, {})
        gr = ctx.guards.get(b.derivation.guard_receipt_id or "")
        if gr is None:
            rs.add("GUARD_NOT_EVIDENCED")
            ev["guards"] = {"receipt": None}
            continue
        failed = [g for g in pat.get("required_guards", []) if (gr.get("guards") or {}).get(g) is not True]
        if failed:
            rs.add("GUARD_FAILED")
        if gr.get("warehouse_sha256") != fp.get("warehouse_sha256"):
            rs.add("GUARD_SNAPSHOT_MISMATCH")
        ev["guards"] = {"receipt": gr.get("receipt_id"), "failed": failed,
                        "same_snapshot_as_native": gr.get("warehouse_sha256") == fp.get("warehouse_sha256")}
    return ev, rs


def _finish(out, errors, reasons, si, meaning, computability, uncovered, app_report, executable) -> dict:
    for e in errors:
        reasons.add(e["code"])
    if errors or si is None:
        status = INV
    elif si["uncovered"]:
        status = MISS
    elif not si["meaning_ok"]:
        status = U
    elif not si["evidence_ok"]:
        status = NV
    else:
        status = V
    out.update(structural_errors=sorted(errors, key=lambda e: (e["code"], e["path"], e["detail"])),
               uncovered=uncovered, technically_executable=executable, reasons=sorted(reasons), status=status)
    out.setdefault("meaning", meaning)
    out.setdefault("computability", computability)
    out.setdefault("approvals", app_report)
    return out
