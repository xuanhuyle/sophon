"""E5 transposer (PROTOCOL.md §4; written after the freeze). Deterministic, stdlib only, self-contained.

    python3 -I transposer.py PACKET.json OUT.json

Input: ONE file, the transpose packet (approved requirement versions, source texts, approvals, authorized role,
fixed native binding, native baseline text and catalog, patch constraints). It reads nothing else.
Output: a proposal with one in-place patch to the existing metric that implements the amended series, computed by
rendering the metric filter/description from the new IR through the binding — or a refusal (BLOCKED for
provenance/authority, UNRESOLVED for semantics/binding) with no patch. It never deploys anything.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation

ATOM_KEYS = ("atom_id", "kind", "fact_kind", "op", "value", "unit", "aggregation", "period", "grain")


class Refusal(Exception):
    def __init__(self, status: str, reasons: list[str], detail: str):
        super().__init__(detail)
        self.status, self.reasons, self.detail = status, reasons, detail


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def plain_decimal(v: str) -> str | None:
    try:
        d = Decimal(v)
    except (InvalidOperation, TypeError):
        return None
    return format(d.normalize(), "f") if d.is_finite() else None


def meaning(ir: dict) -> str:
    """Normalized claim hash (same definition as PROTOCOL §2.3, independently re-implemented here)."""
    gs = ir["governing_source"]
    atoms = []
    for a in sorted(ir["requirement"]["atoms"], key=lambda a: a["atom_id"]):
        x = {k: a.get(k) for k in ATOM_KEYS if a.get(k) is not None}
        if "value" in x and isinstance(x["value"], str) and plain_decimal(x["value"]) is not None:
            x["value"] = plain_decimal(x["value"])
        atoms.append(x)
    sup = ir.get("supersedes")
    return sha(canon({"series": ir["series"], "clause_id": gs["clause_id"], "clause_version": gs["clause_version"],
                      "effective_from": gs["effective_from"], "effective_to": gs.get("effective_to"),
                      "supersedes": None if sup is None else {"version_id": sup["version_id"], "for_order_dates_from": sup["for_order_dates_from"]},
                      "atoms": atoms}))


# ------------------------------------------------------------------------------------------ provenance / authority
def check_provenance(pk: dict, ir: dict) -> None:
    gs = ir["governing_source"]
    doc = pk["source_documents"].get(gs["document_id"])
    if not gs.get("content_sha256"):
        raise Refusal("BLOCKED", ["SOURCE_HASH_MISSING"], f"{ir['version_id']}: no source hash")
    if doc is None or sha(doc["text"]) != gs["content_sha256"]:
        raise Refusal("BLOCKED", ["SOURCE_HASH_MISMATCH"], f"{ir['version_id']}: declared source hash differs from the source text")
    text = ir["requirement"]["text"]
    if f"[{gs['clause_id']} v{gs['clause_version']}] {text}" not in doc["text"]:
        raise Refusal("BLOCKED", ["CLAUSE_NOT_IN_SOURCE"], f"{ir['version_id']}: clause text not in source")
    for a in ir["requirement"]["atoms"]:
        s, e = a["span"]
        if text[s:e] != a["text"]:
            raise Refusal("BLOCKED", ["SPAN_MISMATCH"], f"{ir['version_id']}/{a['atom_id']}: span text differs")
    apps = [pk["approvals"].get(x) for x in ir.get("approval_ids", [])]
    apps = [a for a in apps if a is not None]
    if not apps:
        raise Refusal("BLOCKED", ["APPROVAL_MISSING"], f"{ir['version_id']}: no approval in the packet")
    roles = pk["authorized_roles"]
    for ap in apps:
        spec = roles.get(ap["approver_role"])
        if ap["approver_role"] in roles.get("never_approvers", []) or not isinstance(spec, dict) \
                or ap["claim"]["kind"] not in spec.get("may_approve", []) or ap["scope"]["source_id"] not in spec.get("source_ids", []):
            raise Refusal("BLOCKED", ["APPROVER_NOT_AUTHORIZED"], f"{ap['approval_id']}: role {ap['approver_role']} may not approve this")
        sc = ap["scope"]
        if (sc["source_id"] != gs["source_id"] or sc["source_sha256"] != gs["content_sha256"] or sc["clause_id"] != gs["clause_id"]
                or sc["clause_version"] != gs["clause_version"] or sc.get("document_id", gs["document_id"]) != gs["document_id"]):
            raise Refusal("BLOCKED", ["APPROVAL_SCOPE_MISMATCH"], f"{ap['approval_id']}: scope differs from the version's source/clause")
        if ap["known_at"] < gs["observed_at"]:
            raise Refusal("BLOCKED", ["APPROVAL_BEFORE_SOURCE_OBSERVED"], ap["approval_id"])
        if "normalized_claim_sha256" in ap["claim"]:
            if ap["claim"]["normalized_claim_sha256"] != meaning(ir):
                raise Refusal("BLOCKED", ["APPROVAL_MEANING_MISMATCH"], f"{ap['approval_id']}: approved claim hash differs from this version's meaning")
        elif ap["claim"].get("reading_id") != (ir.get("derived_from_e3") or {}).get("reading_id"):
            raise Refusal("BLOCKED", ["APPROVAL_MEANING_MISMATCH"], f"{ap['approval_id']}: approved reading differs")


# ------------------------------------------------------------------------------------------ delta
def delta(v1: dict, v2: dict, binding: dict) -> list[dict]:
    a1 = {a["atom_id"]: a for a in v1["requirement"]["atoms"]}
    a2 = {a["atom_id"]: a for a in v2["requirement"]["atoms"]}
    if set(a1) != set(a2):
        raise Refusal("UNRESOLVED", ["UNSUPPORTED_DELTA"], f"atoms added/removed: {sorted(set(a1) ^ set(a2))}")
    out = []
    for k in sorted(a1):
        x, y = a1[k], a2[k]
        diff = sorted(f for f in ATOM_KEYS if f not in ("atom_id",) and x.get(f) != y.get(f))
        if not diff:
            continue
        if y.get("op") is not None and y["op"] not in binding["operator_sql"]:
            raise Refusal("UNRESOLVED", ["UNSUPPORTED_OPERATOR"], f"{k}: operator {y['op']} has no native rendering")
        if "unit" in diff:
            raise Refusal("UNRESOLVED", ["UNIT_CHANGED"], f"{k}: unit {x.get('unit')} -> {y.get('unit')}")
        if diff != ["value"] or x.get("kind") != "PREDICATE":
            raise Refusal("UNRESOLVED", ["UNSUPPORTED_DELTA"], f"{k}: changed fields {diff}")
        if "PREDICATE_VALUE_CHANGE" not in binding["supported_delta_kinds"]:
            raise Refusal("UNRESOLVED", ["UNSUPPORTED_DELTA"], "value changes not supported by the binding")
        out.append({"atom_id": k, "kind": "PREDICATE_VALUE_CHANGE", "fact_kind": y["fact_kind"], "op": y["op"],
                    "from": x["value"], "to": y["value"], "unit": y.get("unit"), "grain": y.get("grain"),
                    "source_span_from": x["text"], "source_span_to": y["text"]})
    if not out:
        raise Refusal("UNRESOLVED", ["NO_SEMANTIC_DELTA"], "the versions have the same atoms")
    return out


def check_grounding(v2: dict, changes: list[dict]) -> None:
    for c in changes:
        lit = c["to"]
        span = c["source_span_to"]
        num = plain_decimal(lit)
        tokens = [t.strip(".,;:()") for t in span.split()]
        grounded = lit in tokens or (num is not None and any(plain_decimal(t) == num for t in tokens))
        if not grounded:
            raise Refusal("BLOCKED", ["VALUE_NOT_GROUNDED_IN_SOURCE"], f"{c['atom_id']}: value {lit} does not occur in its source span '{span}'")


# ------------------------------------------------------------------------------------------ rendering
def literal(binding: dict, fact_kind: str, value: str) -> str:
    style = binding["literal_style"].get(fact_kind)
    if style == "QUOTED_STRING":
        return "'" + value.replace("'", "''") + "'"
    if style == "PLAIN_DECIMAL":
        v = plain_decimal(value)
        if v is None:
            raise Refusal("UNRESOLVED", ["VALUE_NOT_NUMERIC"], f"{fact_kind}: {value}")
        return v
    raise Refusal("UNRESOLVED", ["BINDING_MISSING"], f"no literal style for {fact_kind}")


def render(ir: dict, binding: dict, metric: str, catalog: dict) -> dict:
    spec = binding["metrics"][metric]
    atoms = {a["atom_id"]: a for a in ir["requirement"]["atoms"]}
    parts, values = [], {}
    for aid in spec["predicate_atoms"]:
        a = atoms.get(aid)
        if a is None:
            raise Refusal("UNRESOLVED", ["BINDING_MISSING"], f"binding names atom {aid} absent from {ir['version_id']}")
        dim = binding["fact_kind_dimension"].get(a["fact_kind"])
        if dim is None or dim not in catalog["dimensions"]:
            raise Refusal("UNRESOLVED", ["BINDING_MISSING"], f"{aid}: no native dimension bound for fact kind {a['fact_kind']}")
        if a.get("unit") is not None and binding["dimension_unit"].get(dim) not in (None, a["unit"]):
            raise Refusal("UNRESOLVED", ["BINDING_UNIT_MISMATCH"], f"{aid}: {a['unit']} vs {binding['dimension_unit'][dim]}")
        if a["op"] not in binding["operator_sql"]:
            raise Refusal("UNRESOLVED", ["UNSUPPORTED_OPERATOR"], f"{aid}: {a['op']}")
        lit = literal(binding, a["fact_kind"], a["value"])
        values[aid] = lit
        parts.append(binding["predicate_template"].replace("<dimension>", dim).replace("<operator>", binding["operator_sql"][a["op"]])
                     .replace("<literal>", lit))
    desc = spec["description_template"]
    for aid, lit in values.items():
        desc = desc.replace("{" + aid + "}", lit)
    return {"filter": binding["conjunction"].join(parts), "description": desc}


def metric_blocks(text: str) -> dict[str, str]:
    """Split a MetricFlow `metrics:` YAML file into its top-level metric blocks (text-preserving)."""
    lines = text.splitlines(keepends=True)
    starts = [i for i, l in enumerate(lines) if l.startswith("  - name: ")]
    blocks = {}
    for n, i in enumerate(starts):
        j = starts[n + 1] if n + 1 < len(starts) else len(lines)
        while j > i + 1 and lines[j - 1].strip() == "":
            j -= 1
        if n + 1 < len(starts):
            k = j
            while k > i + 1 and lines[k - 1].lstrip().startswith("#"):
                k -= 1  # section comments belong to the next block's preamble
            j = k
            while j > i + 1 and lines[j - 1].strip() == "":
                j -= 1
        name = lines[i][len("  - name: "):].strip()
        blocks[name] = "".join(lines[i:j])
    return blocks


def field_line(block: str, key: str) -> str | None:
    hits = [l for l in block.splitlines(keepends=True) if l.startswith(f"    {key}: ")]
    return hits[0] if len(hits) == 1 else None


def yaml_dq(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ------------------------------------------------------------------------------------------ main
def transpose(pk: dict) -> dict:
    task = pk["task"]
    v1, v2 = pk["requirement_versions"][task["from_version"]], pk["requirement_versions"][task["to_version"]]
    binding, base, cons = pk["binding"], pk["native_baseline"], pk["patch_constraints"]
    out = {"proposal_id": f"PROP_{task['series']}_{v1['version_id']}_to_{v2['version_id']}".replace("/", "_"),
           "generator": {"name": "E5 deterministic transposer", "model": None, "paid_calls": 0},
           "input_packet_sha256": None, "task": task}
    # provenance and authority of both versions
    for ir in (v1, v2):
        if ir["series"] != task["series"]:
            raise Refusal("BLOCKED", ["SERIES_MISMATCH"], ir["version_id"])
        check_provenance(pk, ir)
    sup = v2.get("supersedes") or {}
    if sup.get("version_id") != v1["version_id"] or sup.get("ir_sha256") != sha(canon(v1)):
        raise Refusal("BLOCKED", ["PREDECESSOR_MISMATCH"], "v2 does not supersede exactly the packet's v1 record")
    changes = delta(v1, v2, binding)
    check_grounding(v2, changes)
    # impacted native objects (through the fixed binding only)
    impacted = sorted(m for m, s in binding["metrics"].items() if s["implements_series"] == task["series"])
    if len(impacted) != 1:
        raise Refusal("UNRESOLVED", ["IMPACT_NOT_UNIQUE"], f"metrics implementing {task['series']}: {impacted}")
    metric = impacted[0]
    spec = binding["metrics"][metric]
    changed_fk = {c["fact_kind"] for c in changes}
    for c in changes:
        if c["fact_kind"] not in binding["fact_kind_dimension"]:
            raise Refusal("UNRESOLVED", ["BINDING_MISSING"], f"no native dimension bound for fact kind {c['fact_kind']}")
    if spec["file"] not in cons["editable_files"]:
        raise Refusal("UNRESOLVED", ["FILE_NOT_EDITABLE"], spec["file"])
    text = base["files"].get(spec["file"])
    if text is None or sha(text) != base["file_sha256"].get(spec["file"]):
        raise Refusal("BLOCKED", ["BASELINE_FILE_HASH_MISMATCH"], spec["file"])
    blocks = metric_blocks(text)
    if metric not in blocks or metric not in base["catalog"]["metrics"]:
        raise Refusal("UNRESOLVED", ["METRIC_NOT_IN_BASELINE"], metric)
    block = blocks[metric]
    old_r, new_r = render(v1, binding, metric, base["catalog"]), render(v2, binding, metric, base["catalog"])
    fl, dl = field_line(block, "filter"), field_line(block, "description")
    if fl is None or dl is None or fl != f"    filter: {yaml_dq(old_r['filter'])}\n" or dl != f"    description: {yaml_dq(old_r['description'])}\n":
        raise Refusal("UNRESOLVED", ["BASELINE_DOES_NOT_IMPLEMENT_PREDECESSOR"],
                      f"{metric}: baseline filter/description differ from the rendering of {v1['version_id']}")
    new_block = block.replace(fl, f"    filter: {yaml_dq(new_r['filter'])}\n").replace(dl, f"    description: {yaml_dq(new_r['description'])}\n")
    if text.count(block) != 1:
        raise Refusal("UNRESOLVED", ["ANCHOR_NOT_UNIQUE"], metric)
    new_text = text.replace(block, new_block)
    new_blocks = metric_blocks(new_text)
    if sorted(new_blocks) != sorted(blocks):
        raise Refusal("UNRESOLVED", ["METRIC_SET_CHANGED"], "the edit would add or remove a metric")
    others_unchanged = all(new_blocks[m] == blocks[m] for m in blocks if m != metric)
    if not others_unchanged:
        raise Refusal("UNRESOLVED", ["COLLATERAL_EDIT"], "an edit outside the impacted metric")
    not_affected = []
    for m, s in sorted(binding["metrics"].items()):
        if m == metric:
            continue
        uses = sorted(set(s.get("predicate_fact_kinds", [])) & changed_fk)
        not_affected.append({"metric": m, "status": "NOT_AFFECTED", "implements_series": s["implements_series"],
                             "rationale": f"implements {s['implements_series']}, not the amended series {task['series']}; "
                                          f"its bound predicates use {sorted(s.get('predicate_fact_kinds', []))}, none of the changed fact kinds "
                                          f"{sorted(changed_fk)}" if not uses else f"shares changed fact kinds {uses}",
                             "block_unchanged_by_patch": new_blocks[m] == blocks[m]})
        if uses:
            raise Refusal("UNRESOLVED", ["SHARED_FACT_KIND_NEEDS_REVIEW"], m)
    patch = [{"op": "replace", "file": spec["file"], "old": block, "new": new_block}]
    out.update({
        "status": "PROPOSED_NOT_DEPLOYED", "refusals": [],
        "impacted_metrics": impacted, "modified_metrics": [metric], "edit_mode": "IN_PLACE_EXISTING_METRIC", "not_affected": not_affected,
        "delta": [{k: c[k] for k in ("atom_id", "kind", "fact_kind", "op", "from", "to", "unit", "grain", "source_span_from", "source_span_to")} for c in changes],
        "rendered": {"before": old_r, "after": new_r},
        "patch": patch,
        "versions": {x["version_id"]: {"ir_sha256": sha(canon(x)), "meaning_sha256": meaning(x), "document_id": x["governing_source"]["document_id"],
                                       "source_sha256": x["governing_source"]["content_sha256"], "clause": f"{x['governing_source']['clause_id']} v{x['governing_source']['clause_version']}",
                                       "observed_at": x["governing_source"]["observed_at"], "effective_from": x["governing_source"]["effective_from"],
                                       "effective_to": x["governing_source"].get("effective_to"),
                                       "approvals": [{k: pk["approvals"][a].get(k) for k in ("approval_id", "provenance", "approver_role", "known_at")}
                                                     for a in x["approval_ids"]]} for x in (v1, v2)},
        "native_revision": {"from": base["revision_id"], "to": "REV_P1_V2_PROPOSED", "file": spec["file"],
                            "file_sha256_before": sha(text), "file_sha256_after": sha(new_text),
                            "semantic_manifest_sha256_before": base["semantic_manifest_sha256"], "semantic_manifest_sha256_after": None},
        "review_status": "PROPOSED_NOT_DEPLOYED", "deployment": None, "reviewer": {"role": "LAB_SEMANTIC_LAYER_OWNER (placeholder)", "decision": "PENDING"},
        "notes": ["Interpretation approval of the amendment is not a deployment authorization.",
                  "History: the proposal does not make the metric version-aware; earlier order dates need the preserved prior revision."]})
    return out


def main(argv: list[str]) -> int:
    src, dst = argv[1], argv[2]
    raw = open(src, "rb").read()
    pk = json.loads(raw.decode("utf-8"))
    try:
        res = transpose(copy.deepcopy(pk))
    except Refusal as r:
        res = {"status": r.status, "refusals": [{"reasons": r.reasons, "detail": r.detail}], "patch": None, "review_status": None, "deployment": None}
    except (KeyError, TypeError, ValueError) as e:
        res = {"status": "UNRESOLVED", "refusals": [{"reasons": ["MALFORMED_PACKET"], "detail": f"{type(e).__name__}: {e}"}], "patch": None,
               "review_status": None, "deployment": None}
    res["input_packet_sha256"] = hashlib.sha256(raw).hexdigest()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"status": res["status"], "reasons": [x for r in res.get("refusals", []) for x in r["reasons"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
