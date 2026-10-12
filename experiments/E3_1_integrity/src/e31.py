"""E3.1 wrapper and runner (PROTOCOL.md §3-§4). E3's validator is called unmodified; this file adds
(1) applicability on the effective-time axis and (2) fresh verification of would-be promotions.

    .upstream/.venv/bin/python src/e31.py --upstream .upstream --out evidence/run
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_cases  # noqa: E402  (frozen: reading_meaning, canon)
import candidates as cand  # noqa: E402  (frozen harness; imports the unmodified E3 validator)
from fresh_verifier import FreshVerifier, dec_equal  # noqa: E402

E31 = HERE.parent
E3_VERIFIED = "VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS"
V = "VERIFIED_FOR_LAB_ASSUMPTIONS_AND_FRESH_CHECKS"
TRUST_BOUNDARY = ("Trusted: cases/TRUSTED_MANIFEST.json (anchors from E0's committed regen receipt and E3's frozen fixtures), "
                  "the pinned upstream rebuilt by this verifier process, and code files whose sha256 match the manifest. "
                  "Untrusted: the record's verification_request and every candidate receipt. Not covered: an adversary "
                  "controlling the manifest, verifier/reference code, the pinned source or generator; genuineness of the "
                  "raw data or of LAB_SIMULATED approvals.")


def in_force(effective_from: str, effective_to: str | None, eval_effective_at: str) -> bool:
    """Inclusive on both ends; a null effective_to means no declared end."""
    d = date.fromisoformat(str(eval_effective_at))
    return date.fromisoformat(str(effective_from)) <= d and (effective_to is None or d <= date.fromisoformat(str(effective_to)))


def meaning_sha(reading: dict) -> str:
    return build_cases.sha_bytes(build_cases.canon(build_cases.reading_meaning(reading)).encode())


def trusted_reading(record_id: str, reading_id: str) -> dict | None:
    rec = cand.load(cand.E3 / "cases" / "records" / f"{record_id}.json")
    return next((r for r in rec["interpretation"]["readings"] if r["reading_id"] == reading_id), None)


def fresh_check(case: dict, rec: dict, ctx, old: dict, fv: FreshVerifier | None, m: dict) -> tuple[set, dict]:
    reasons: set[str] = set()
    sel = old["meaning"]["selected_reading"]
    key = f"{rec['record_id']}/{sel}"
    reading = next(r for r in rec["interpretation"]["readings"] if r["reading_id"] == sel)
    fc = case["fresh_conditions"]
    detail = {"reading_key": key, "estate": fc["estate"]}
    # V-b anchors (candidate claims vs trusted manifest)
    vr = rec["verification_request"]
    nr = ctx.native.get(reading.get("native_receipt_id") or "") or {}
    orc = ctx.oracle.get(reading.get("oracle_id") or "") or {}
    fp = nr.get("fingerprint") or {}
    anchors = {"request_semantic_manifest": vr["semantic_manifest_sha256"] == m["semantic_manifest_sha256"],
               "request_raw_csv": vr["raw_csv_sha256"] == m["raw_csv_sha256"],
               "receipt_semantic_manifest": fp.get("semantic_manifest_sha256") == m["semantic_manifest_sha256"],
               "receipt_raw_csv": fp.get("raw_csv_sha256") == m["raw_csv_sha256"],
               "oracle_raw_csv": orc.get("raw_csv_sha256") == m["raw_csv_sha256"],
               "governing_source": rec["governing_source"]["content_sha256"] == m["governing_source"]["sha256"]}
    detail["anchor_checks"] = anchors
    if not all(anchors.values()):
        reasons.add("TRUST_ANCHOR_MISMATCH")
    trusted = trusted_reading(rec["record_id"], sel)
    t_sha = m["approved_reading_meaning_sha256"].get(key)
    detail["reading_meaning"] = {"candidate": meaning_sha(reading), "trusted": t_sha,
                                 "fixture_matches_manifest": trusted is not None and meaning_sha(trusted) == t_sha}
    if t_sha is None or meaning_sha(reading) != t_sha or not detail["reading_meaning"]["fixture_matches_manifest"]:
        reasons.add("UNTRUSTED_READING_CONTENT")
    if fv is None or not fv.build["ok"]:
        reasons.add("FRESH_BUILD_ANCHOR_MISMATCH" if fv is not None else "FRESH_RUNTIME_UNAVAILABLE")
        return reasons, detail
    if trusted is None or trusted.get("native_query") is None:
        reasons.add("UNTRUSTED_READING_CONTENT")
        return reasons, detail
    q = trusted["native_query"]  # the query comes from the trusted reading, never from the candidate
    nat = fv.native(q, fc["estate"], fc["runtime"])
    ref = fv.reference(key, fc["reference_code"])
    detail["fresh_native"] = {k: nat.get(k) for k in ("ok", "exit_code", "by_period", "error", "semantic_manifest_sha256")}
    detail["fresh_reference"] = {k: ref.get(k) for k in ("ok", "by_period", "error", "code_sha256")}
    if not nat["ok"]:
        reasons.add("FRESH_RUNTIME_UNAVAILABLE")
    if not ref["ok"]:
        reasons.add("FRESH_REFERENCE_UNAVAILABLE")
    if nat["ok"] and ref["ok"] and not dec_equal(nat["by_period"], ref["by_period"]):
        reasons.add("FRESH_NATIVE_REFERENCE_MISMATCH")
    cand_native = None
    if nr.get("rows"):
        try:
            cand_native = {r["metric_time__year"][:4]: r[nr["query"]["metric"]] for r in nr["rows"]}
        except Exception:  # noqa: BLE001
            cand_native = None
    detail["candidate_native_by_period"] = cand_native
    detail["candidate_reference_by_period"] = orc.get("by_year")
    if nat["ok"] and not dec_equal(cand_native, nat["by_period"]):
        reasons.add("CANDIDATE_NATIVE_DISAGREES_WITH_FRESH")
    if ref["ok"] and not dec_equal(orc.get("by_year"), ref["by_period"]):
        reasons.add("CANDIDATE_REFERENCE_DISAGREES_WITH_FRESH")
    if any(b.get("kind") == "DERIVED" for b in trusted["bindings"].values()):
        g = fv.guards(q, fc["estate"])
        detail["fresh_guards"] = g
        if not g["ok"]:
            reasons.add("FRESH_GUARD_FAILED")
    return reasons, detail


def evaluate(case: dict, e3ctx, fv: FreshVerifier | None, m: dict) -> dict:
    rec, aps, rvs, ctx = cand.candidate(case, e3ctx)
    old = cand.e3val.validate(rec, aps, rvs, ctx, case["eval_known_at"], case["eval_effective_at"])
    structural = {e["code"] for e in old["structural_errors"]}
    known = "SOURCE_NOT_YET_KNOWN" not in structural
    gs = rec.get("governing_source", {})
    try:
        applicable = in_force(gs["effective_from"], gs.get("effective_to"), case["eval_effective_at"])
    except Exception:  # noqa: BLE001  (malformed dates are already a structural error)
        applicable = None
    reasons = set(old["reasons"])
    fresh_detail, promoted = None, False
    if structural - {"SOURCE_NOT_YET_KNOWN"}:
        status = "STRUCTURALLY_INVALID"
    elif not known:
        status = "NOT_KNOWN_AT_EVALUATION_TIME"
    elif applicable is not True:
        status = "REQUIREMENT_NOT_IN_FORCE"
        reasons.add("REQUIREMENT_NOT_IN_FORCE")
    elif old["status"] == E3_VERIFIED:
        fr, fresh_detail = fresh_check(case, rec, ctx, old, fv, m)
        reasons |= fr
        promoted = not fr
        status = V if promoted else "NOT_VERIFIED"
    else:
        status = old["status"]
    sel = old["meaning"].get("selected_reading") if old.get("meaning") else None
    eqs = (old.get("meaning") or {}).get("equivalences", {})
    states = {
        "known_at_eval_time": known,
        "applicable_at_effective_date": applicable,
        "approved_lab_meaning": bool(sel) and "EQUIVALENCE_UNAPPROVED" not in old["reasons"] and
        all(v["state"] == "LAB_APPROVED" for k, v in eqs.items() if k.startswith(f"{sel}/")),
        "lab_simulated_equivalence_used": any(v["state"] == "LAB_APPROVED" for k, v in eqs.items() if sel and k.startswith(f"{sel}/")),
        "technically_executable_candidate": old.get("technically_executable"),
        "fresh_reexecution_succeeded": None if fresh_detail is None else bool((fresh_detail.get("fresh_native") or {}).get("ok")),
        "fresh_reference_agreement": None if fresh_detail is None else (
            "FRESH_NATIVE_REFERENCE_MISMATCH" not in reasons and bool((fresh_detail.get("fresh_reference") or {}).get("ok"))
            and bool((fresh_detail.get("fresh_native") or {}).get("ok"))),
        "candidate_agrees_with_fresh": None if fresh_detail is None else not (
            {"CANDIDATE_NATIVE_DISAGREES_WITH_FRESH", "CANDIDATE_REFERENCE_DISAGREES_WITH_FRESH"} & reasons),
    }
    return {"case_id": case["case_id"], "group": case["group"], "status": status, "reasons": sorted(reasons),
            "selected_reading": sel, "uncovered": old.get("uncovered", []), "states": states,
            "e3_old": {"status": old["status"], "reasons": old["reasons"]}, "fresh": fresh_detail,
            "trust_boundary": TRUST_BOUNDARY}


def check(case: dict, res: dict, m: dict) -> list[str]:
    exp, f = case["expected"], []
    if res["status"] != exp["status"]:
        f.append(f"status {res['status']} != {exp['status']}")
    miss = [r for r in exp.get("reasons_include", []) if r not in res["reasons"]]
    if miss:
        f.append(f"missing reasons {miss}")
    if "uncovered" in exp and res["uncovered"] != exp["uncovered"]:
        f.append(f"uncovered {res['uncovered']}")
    blob = json.dumps({k: v for k, v in res.items() if k != "trust_boundary"})
    for t in exp.get("must_not_mention", []):
        if t in blob:
            f.append(f"mentions {t}")
    if exp.get("fresh_values"):
        fn = ((res.get("fresh") or {}).get("fresh_native") or {}).get("by_period")
        if not dec_equal(fn, m["expected_reference_values"][exp["fresh_values"]]):
            f.append(f"fresh native {fn} != trusted expected {exp['fresh_values']}")
    return f


def normalized(results: list[dict]) -> list[dict]:
    """Projection compared across independent verifier processes (no run ids, timestamps or warehouse hashes)."""
    out = []
    for r in results:
        fr = r.get("fresh") or {}
        out.append({"case_id": r["case_id"], "status": r["status"], "reasons": r["reasons"], "states": r["states"],
                    "fresh_native": (fr.get("fresh_native") or {}).get("by_period"),
                    "fresh_reference": (fr.get("fresh_reference") or {}).get("by_period"),
                    "fresh_guards": (fr.get("fresh_guards") or {}).get("guards")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    m = cand.load(E31 / "cases" / "TRUSTED_MANIFEST.json")
    cases = cand.load(E31 / "cases" / "CASES.json")["cases"]
    fv = FreshVerifier(Path(a.upstream), m, E31 / "runs" / f"verifier_{out.name}")
    e3ctx = cand.e3_context()
    results = []
    for c in cases:
        r = evaluate(c, e3ctx, fv, m)
        r["check_failures"] = check(c, r, m)
        r["passed"] = not r["check_failures"]
        r["expected_status"] = c["expected"]["status"]
        results.append(r)
    build = {k: v for k, v in fv.build.items()}
    build["control_mutation"] = getattr(fv, "control_mutation", None)
    build["run_id"] = fv.run_id
    (out / "fresh_build.json").write_text(json.dumps(build, indent=1) + "\n", encoding="utf-8")
    fresh_receipts = {"native": [{"query": json.loads(k[0]), "estate": k[1], "runtime": k[2],
                                  **{x: v.get(x) for x in ("ok", "exit_code", "error", "by_period", "argv", "mf_identity",
                                                           "semantic_manifest_sha256", "warehouse_sha256", "compiled_sql")}}
                                 for k, v in fv._native.items()],  # noqa: SLF001
                      "reference": [{"reading": k[0], "code_mode": k[1], **v} for k, v in fv._ref.items()],  # noqa: SLF001
                      "guards": [{"query": json.loads(k[0]), "estate": k[1], **v} for k, v in fv._guards.items()]}  # noqa: SLF001
    (out / "fresh_receipts.json").write_text(json.dumps(fresh_receipts, indent=1, default=str) + "\n", encoding="utf-8")
    (out / "case_results.json").write_text(json.dumps(results, indent=1, default=str) + "\n", encoding="utf-8")
    (out / "normalized.json").write_text(json.dumps(normalized(results), indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    bad = [r for r in results if not r["passed"]]
    print(f"build_ok={fv.build['ok']} {len(results) - len(bad)}/{len(results)} cases as frozen")
    for r in results:
        print(f"{r['case_id']:50s} {r['status'][:32]:32s} old={r['e3_old']['status'][:14]:14s} {','.join(r['reasons'])[:120]}")
    for r in bad:
        print(" FAIL", r["case_id"], r["check_failures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
