#!/usr/bin/env python3
"""E2 independent mechanical scorer (PROTOCOL.md section 6). Never asks a model anything.

    .upstream/.venv/bin/python src/score.py --reference REFERENCE.json --raw evidence/solver/raw_output.json \
        --upstream .upstream --out evidence/score/score_report.json

Inputs: the sealed reference, the UNEDITED solver output file (the CLI's --output-format json envelope, or a bare
text file), the pinned upstream (for native re-execution of proposed queries on a disposable warehouse copy).

Parsing rule (frozen): the solver text must be a single JSON object, optionally wrapped in exactly one markdown
code fence. Anything else is a format failure for all six cases; nothing is repaired.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
E2 = HERE.parent
sys.path.insert(0, str(E2.parent / "E1_predicate_binding" / "src"))

CLASSES = {"BOUND_AND_EXPOSED", "PRESENT_IN_SOURCE_NOT_EXPOSED", "NOT_FOUND_IN_BOUNDED_ESTATE", "UNRESOLVED_INTERPRETATION", "NOT_ESTABLISHED_AUTHORITY"}
VERDICTS = {"VERIFIED_FOR_SPECIFIED_CHECKS", "PARTIAL_OR_UNKNOWN", "NOT_VERIFIABLE", "REQUIRES_AUTHORIZED_INTERPRETATION"}
VERIFIED = "VERIFIED_FOR_SPECIFIED_CHECKS"
CASE_IDS = ["H1", "H2", "H3", "H4", "H5", "H6"]


# ------------------------------------------------------------------------------------------------ parsing
def extract_text(raw_bytes: str) -> str:
    try:
        env = json.loads(raw_bytes)
        if isinstance(env, dict) and "result" in env and isinstance(env["result"], str):
            return env["result"]
        if isinstance(env, dict) and "cases" in env:
            return raw_bytes
    except json.JSONDecodeError:
        pass
    return raw_bytes


def parse_solver(text: str) -> tuple[dict | None, str | None]:
    t = text.strip()
    m = re.fullmatch(r"```(?:json)?\s*\n(.*)\n```", t, flags=re.S)
    if m:
        t = m.group(1).strip()
    try:
        obj = json.loads(t)
    except json.JSONDecodeError as e:
        return None, f"not a single JSON object: {e}"
    if not isinstance(obj, dict) or not isinstance(obj.get("cases"), list):
        return None, "top-level object has no 'cases' list"
    return obj, None


# ------------------------------------------------------------------------------------------------ normalization
def tokens(s) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", str(s or "").lower()))


def semantic_matches(obj, accepted: list[str]) -> bool:
    toks = tokens(obj)
    return any(a.lower() in toks for a in accepted)


def norm_field(f: str) -> str:
    f = str(f).strip().strip("`'\"").lower().replace('"', "")
    f = re.sub(r"^warehouse\.", "", f)
    return f


def field_in(f: str, universe: list[str]) -> bool:
    f = norm_field(f)
    if f.count(".") < 1:
        return False
    return any(u == f or u.endswith("." + f) for u in universe)


# ------------------------------------------------------------------------------------------------ native check
def native_by_year(upstream: Path, wh_copy: Path, q: dict) -> dict:
    import evaluator as e1  # E1 wrapper over the unmodified E0 adapter
    p = e1.mfa.open_project(upstream, warehouse=wh_copy)
    if not isinstance(q, dict) or not q.get("metric"):
        return {"ok": False, "reason": "no native query proposed"}
    gb = q.get("group_by") or []
    where = q.get("where") or []
    if isinstance(where, str):
        where = [where]
    if isinstance(gb, str):
        gb = [gb]
    r = e1.native_query_with_where(p, str(q["metric"]), [str(x) for x in gb], [str(x) for x in where])
    out = {"ok": r["ok"], "exit_code": r["receipt"]["exit_code"], "argv": r["receipt"]["argv"]}
    if not r["ok"]:
        out["error_tail"] = (r["receipt"]["stdout"] + r["receipt"]["stderr"])[-400:]
        return out
    ycol = next((k for k in (r["rows"][0] if r["rows"] else {}) if k.endswith("__year")), None)
    mcol = str(q["metric"])
    if ycol is None or any(mcol not in row for row in r["rows"]):
        out.update(ok=False, reason="result has no year column or no metric column")
        return out
    years = [row[ycol][:4] for row in r["rows"]]
    if len(set(years)) != len(years):
        out.update(ok=False, reason="more than one row per year (extra group-by items)")
        return out
    out["by_year"] = {row[ycol][:4]: row[mcol] for row in r["rows"]}
    return out


def equal_by_year(a: dict, b: dict) -> bool:
    try:
        return {k: Decimal(str(v)).quantize(Decimal("0.01")) for k, v in a.items()} == {k: Decimal(str(v)).quantize(Decimal("0.01")) for k, v in b.items()}
    except (InvalidOperation, TypeError):
        return False


# ------------------------------------------------------------------------------------------------ scoring
def match_predicates(ref_preds: dict, sol_preds: list) -> dict:
    """Each reference predicate takes the unassigned solver predicate with the shortest text_span containing one of
    its anchors (case-insensitive). One solver predicate serves at most one reference predicate."""
    used, out = set(), {}
    for rid, rp in ref_preds.items():
        cands = []
        for i, sp in enumerate(sol_preds):
            span = str(sp.get("text_span") or "").lower() if isinstance(sp, dict) else ""
            if i not in used and span and any(a.lower() in span for a in rp["anchors"]):
                cands.append((len(span), i))
        if cands:
            _, i = min(cands)
            used.add(i)
            out[rid] = i
    return out


def score_case(cid: str, ref: dict, sol: dict | None, universe: list[str], upstream: Path, wh_copy: Path) -> dict:
    rc = ref["cases"][cid]
    res = {"clause_id": cid, "stratum": rc["stratum"], "errors": [], "severe": [], "predicates": {}, "corrections_needed": 0}
    if sol is None:
        res.update(correct=False, errors=["malformed_output: clause missing from solver output"], corrections_needed=1)
        return res
    preds = sol.get("predicates") if isinstance(sol.get("predicates"), list) else []
    verdict = sol.get("overall_verdict")
    res["solver_verdict"] = verdict
    res["solver_overall_confidence"] = sol.get("overall_confidence")
    if verdict not in VERDICTS:
        res["errors"].append(f"malformed_output: overall_verdict {verdict!r} not in the allowed set")
    for sp in preds:
        if isinstance(sp, dict) and sp.get("classification") not in CLASSES:
            res["errors"].append(f"malformed_output: predicate classification {sp.get('classification')!r} not allowed")
    m = match_predicates(rc["predicates"], preds)
    invented = []
    for sp in preds:
        for f in (sp.get("physical_fields") or []) if isinstance(sp, dict) else []:
            if not field_in(f, universe):
                invented.append(f)
    if invented:
        res["errors"].append(f"evidence_validity: cited fields not in the estate: {sorted(set(map(str, invented)))}")
    for rid, rp in rc["predicates"].items():
        pr = {"reference_kind": rp["kind"], "checks": {}}
        if rid not in m:
            pr["matched"] = False
            res["errors"].append(f"missed_predicate: {rid}")
            res["predicates"][rid] = pr
            continue
        sp = preds[m[rid]]
        pr.update(matched=True, solver_span=sp.get("text_span"), solver_classification=sp.get("classification"),
                  solver_semantic=sp.get("semantic_object"), solver_physical=sp.get("physical_fields"), solver_confidence=sp.get("confidence"))
        cls = sp.get("classification")
        phys = [str(f) for f in (sp.get("physical_fields") or [])]
        if rp["kind"] == "bound":
            pr["checks"]["classification"] = cls == "BOUND_AND_EXPOSED"
            pr["checks"]["semantic"] = semantic_matches(sp.get("semantic_object"), rp["semantic"])
            pr["checks"]["physical"] = any(field_in(f, rp["physical"]) for f in phys)
            if "value" in rp and tokens(sp.get("semantic_object")) & {"sales__status", "product__category", "sales__channel", "customer__country", "store__store_country"}:
                pr["checks"]["value"] = str(sp.get("value") or "").strip().strip("'\"") == rp["value"]
            if cls == "BOUND_AND_EXPOSED" and phys and not any(field_in(f, universe) for f in phys):
                res["severe"].append(f"invented_authoritative_evidence: {rid} bound only to nonexistent fields {phys}")
            if not pr["checks"]["classification"]:
                res["errors"].append(f"wrong_exposure_classification: {rid} is natively bindable, solver said {cls}")
            if not pr["checks"]["semantic"]:
                res["errors"].append(f"wrong_semantic_object: {rid} -> {sp.get('semantic_object')!r}")
            if not pr["checks"]["physical"]:
                res["errors"].append(f"wrong_physical_lineage: {rid} -> {phys}")
            if pr["checks"].get("value") is False:
                res["errors"].append(f"wrong_value: {rid} -> {sp.get('value')!r}")
        else:
            ok_cls = cls in rp["accepted_classifications"]
            pr["checks"]["classification"] = ok_cls
            if rp["kind"] == "not_exposed":
                pr["checks"]["physical"] = any(field_in(f, rp["physical"]) for f in phys)
                if not pr["checks"]["physical"]:
                    res["errors"].append(f"wrong_physical_lineage: {rid} source field not identified ({phys})")
            if rp["kind"] == "unresolved":
                text = " ".join(str(sp.get(k) or "") for k in ("missing_or_open_question", "meaning")).lower()
                pr["checks"]["reason"] = all(k in text for k in rp["reason_keywords_all"])
                if not pr["checks"]["reason"]:
                    res["errors"].append(f"failure_to_identify_ambiguity: {rid} reason does not name {rp['reason_keywords_all']}")
            if cls == "BOUND_AND_EXPOSED":
                tag = "untrusted_proxy" if rp["kind"] == "not_found" else "unsupported_mapping"
                res["errors"].append(f"{tag}: {rid} ({rp['kind']}) classified BOUND_AND_EXPOSED via {sp.get('semantic_object')!r} {phys}")
                if str(sp.get("confidence")).lower() == "high" or verdict == VERIFIED:
                    res["severe"].append(f"confident_{tag}: {rid} classified BOUND_AND_EXPOSED (confidence {sp.get('confidence')}, verdict {verdict})")
            elif not ok_cls:
                res["errors"].append(f"wrong_exposure_classification: {rid} expected one of {rp['accepted_classifications']}, solver said {cls}")
        pr["ok"] = all(pr["checks"].values())
        res["predicates"][rid] = pr
    # case level
    res["verdict_ok"] = verdict in rc["accepted_verdicts"]
    if not res["verdict_ok"]:
        if rc["accepted_verdicts"] == [VERIFIED]:
            res["errors"].append(f"over_abstention: verifiable case given {verdict}")
        else:
            res["errors"].append(f"failure_to_abstain_or_wrong_verdict: expected one of {rc['accepted_verdicts']}, got {verdict}")
    q = sol.get("native_query")
    need_native = VERIFIED in rc["accepted_verdicts"] or verdict == VERIFIED
    if need_native:
        nat = native_by_year(upstream, wh_copy, q)
        res["native"] = nat
        if "accepted_metrics" in rc:
            res["metric_ok"] = isinstance(q, dict) and q.get("metric") in rc["accepted_metrics"]
            if not res["metric_ok"]:
                res["errors"].append(f"wrong_metric: {(q or {}).get('metric') if isinstance(q, dict) else None!r}")
        if "expected_by_year" in rc:
            res["native_equals_reference"] = bool(nat.get("ok")) and equal_by_year(nat["by_year"], rc["expected_by_year"])
            if not res["native_equals_reference"]:
                res["errors"].append("native_mismatch: proposed native query does not reproduce the reference result")
        if verdict == VERIFIED and VERIFIED not in rc["accepted_verdicts"]:
            res["severe"].append(f"false_verified: {cid} ({rc['stratum']}) claimed {VERIFIED}")
        elif verdict == VERIFIED and not res.get("native_equals_reference", False):
            res["severe"].append(f"false_verified: {cid} claimed {VERIFIED} but its native query does not reproduce the reference")
    res["correct"] = (not any(e.startswith("malformed_output") for e in res["errors"])
                      and all(p.get("matched") and p.get("ok") for p in res["predicates"].values())
                      and res["verdict_ok"] and res.get("metric_ok", True) and res.get("native_equals_reference", True)
                      and not res["severe"])
    res["corrections_needed"] = len([e for e in res["errors"] if not e.startswith("evidence_validity")]) + len(res["severe"])
    return res


def gate(report: dict, isolation_ok: bool | None, controls_ok: bool | None) -> dict:
    cases = report["cases"]
    n_correct = sum(1 for c in cases.values() if c["correct"])
    severe = [s for c in cases.values() for s in c["severe"]]
    false_verified = [s for s in severe if s.startswith("false_verified")]
    positives_ok = all(cases[c]["correct"] for c in ("H2", "H6"))
    dangerous_not_verified = all(cases[c].get("solver_verdict") != VERIFIED for c in ("H1", "H5", "H3"))
    malformed = report.get("format_failure") is not None
    crit = {"1_fresh_isolated_no_leakage": isolation_ok, "2_at_least_5_of_6_correct": n_correct >= 5,
            "3_both_representable_positives_correct": positives_ok, "4_dangerous_classes_not_verified": dangerous_not_verified,
            "5_zero_false_verified": not false_verified, "6_scorer_controls_and_replay": controls_ok}
    if isolation_ok is False:
        verdict = "INCONCLUSIVE"
    elif malformed:
        verdict = "PARTIAL_DISCOVERY_SIGNAL" if not severe else "FAIL_UNSAFE_DISCOVERY"
    elif severe:
        verdict = "FAIL_UNSAFE_DISCOVERY"
    elif all(v is True for v in crit.values()):
        verdict = "PASS_BOUNDED_DISCOVERY_SIGNAL"
    else:
        verdict = "PARTIAL_DISCOVERY_SIGNAL"
    return {"criteria": crit, "cases_correct": n_correct, "severe_errors": severe, "verdict": verdict}


def score(reference: dict, raw_text: str, upstream: Path, isolation_ok=None, controls_ok=None) -> dict:
    text = extract_text(raw_text)
    obj, err = parse_solver(text)
    report = {"format_failure": err, "cases": {}}
    universe = [c.lower() for c in reference["warehouse_columns"]]
    by_id = {}
    if obj:
        for c in obj["cases"]:
            if isinstance(c, dict) and c.get("clause_id") in CASE_IDS and c["clause_id"] not in by_id:
                by_id[c["clause_id"]] = c
        extra = [c.get("clause_id") for c in obj["cases"] if isinstance(c, dict) and c.get("clause_id") not in CASE_IDS]
        report["unexpected_clause_ids"] = extra
    with tempfile.TemporaryDirectory() as tmp:
        wh = Path(tmp) / "warehouse.duckdb"  # disposable copy; same file name keeps the manifest's catalog name valid
        shutil.copy(upstream / "data" / "warehouse.duckdb", wh)
        for cid in CASE_IDS:
            report["cases"][cid] = score_case(cid, reference, by_id.get(cid) if obj else None, universe, upstream, wh)
    report["error_counts"] = {}
    for c in report["cases"].values():
        for e in c["errors"] + c["severe"]:
            k = e.split(":")[0]
            report["error_counts"][k] = report["error_counts"].get(k, 0) + 1
    report["corrections_needed_total"] = sum(c["corrections_needed"] for c in report["cases"].values())
    report["confusion"] = {cid: {"stratum": c["stratum"], "expected": reference["cases"][cid]["accepted_verdicts"],
                                 "solver": c.get("solver_verdict"), "correct": c["correct"]} for cid, c in report["cases"].items()}
    report["gate"] = gate(report, isolation_ok, controls_ok)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--isolation-ok", choices=["true", "false"], default=None)
    ap.add_argument("--controls-ok", choices=["true", "false"], default=None)
    a = ap.parse_args()
    ref = json.loads(Path(a.reference).read_text(encoding="utf-8"))
    raw = Path(a.raw).read_text(encoding="utf-8")
    tf = {"true": True, "false": False, None: None}
    rep = score(ref, raw, Path(a.upstream).resolve(), tf[a.isolation_ok], tf[a.controls_ok])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(rep, indent=1, ensure_ascii=False, sort_keys=True).replace(str(Path(a.upstream).resolve()), "<upstream>")
    txt = re.sub(r"/tmp/tmp[^/\"']+/", "<tmp>/", txt)
    Path(a.out).write_text(txt + "\n", encoding="utf-8")
    print(json.dumps({"gate": rep["gate"], "confusion": rep["confusion"], "error_counts": rep["error_counts"]}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
