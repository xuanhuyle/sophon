"""E4 checker (PROTOCOL.md §4; written after the freeze). Executes each candidate's own modified dbt/MetricFlow stack
and compares it, at order-line grain, with the frozen independent reference. It never reads a variant's `expected`.

    .upstream/.venv/bin/python src/checker.py --upstream .upstream --out evidence/run
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E4 = HERE.parent
EXP = E4.parent
sys.path.insert(0, str(HERE))
import candidate_stack as cs  # noqa: E402
import fixtures  # noqa: E402
import reference  # noqa: E402

sys.path.append(str(EXP / "E3_1_integrity" / "src"))  # E3.1 helpers (after E4's own src on the path)
import e31  # noqa: E402  (unmodified: in_force, meaning_sha; its candidates module wraps the unmodified E3 validator)

cand3 = e31.cand
POLICY_READING = {"P1": ("S1", "R_SINGLE"), "P2": ("S2", "R_CUSTOMER_COUNTRY")}


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def dec_eq(a: dict, b: dict) -> bool:
    return set(a) == set(b) and all(Decimal(a[k]) == Decimal(b[k]) for k in a)


# --------------------------------------------------------------------------------------------- step A
def authority(policy: str, ctx: dict, trusted: dict) -> tuple[str | None, list[str], dict]:
    rid, reading = POLICY_READING[policy]
    rec = cand3.e3rs.apply_patch(cand3.load(cand3.E3 / "cases" / "records" / f"{rid}.json"), ctx.get("record_patch", []))
    approvals = cand3.e3rs.load_dir(cand3.E3 / "cases" / "approvals")
    res = cand3.e3val.validate(rec, [approvals[a] for a in ctx["approvals"]], [], cand3.e3_context(),
                               ctx["eval_known_at"], ctx["eval_effective_at"])
    structural = {e["code"] for e in res["structural_errors"]}
    sel = (res.get("meaning") or {}).get("selected_reading")
    gs = rec["governing_source"]
    detail = {"approved_record": rid, "selected_reading": sel, "structural": sorted(structural)}
    if structural - {"SOURCE_NOT_YET_KNOWN"}:
        return "NOT_VERIFIED", ["APPROVED_SPEC_INVALID"], detail
    if "SOURCE_NOT_YET_KNOWN" in structural:
        return "NOT_VERIFIED", ["SOURCE_NOT_KNOWN"], detail
    if not e31.in_force(gs["effective_from"], gs.get("effective_to"), ctx["eval_effective_at"]):
        return "NOT_APPLICABLE", ["REQUIREMENT_NOT_IN_FORCE"], detail
    r = next((x for x in rec["interpretation"]["readings"] if x["reading_id"] == reading), None)
    detail["reading_meaning_matches_trusted"] = r is not None and e31.meaning_sha(r) == trusted["approved_reading_meaning_sha256"][f"{rid}/{reading}"]
    if sel != reading or not detail["reading_meaning_matches_trusted"]:
        return "NOT_VERIFIED", ["APPROVAL_MISSING"], detail
    return None, [], detail


# --------------------------------------------------------------------------------------------- the checker
class Checker:
    def __init__(self, upstream: Path, work: Path):
        self.up = Path(upstream).resolve()
        self.work = Path(work)
        self.ref = json.loads((E4 / "REFERENCE.json").read_text())
        self.trusted = json.loads((EXP / "E3_1_integrity" / "cases" / "TRUSTED_MANIFEST.json").read_text())
        pinned = self.up / "data" / "raw"
        if {f: fixtures.sha(pinned / f) for f in fixtures.FILES} != self.ref["registered_snapshots"]["snapshots"]["PINNED"]["csv_sha256"]:
            raise RuntimeError("pinned raw CSVs differ from the frozen PINNED anchors")
        self.snap_dir = self.work / "snapshots"
        fixtures.build(pinned, self.snap_dir)
        self.stacks, self.refs = {}, {}

    def registered(self, policy: str, hashes: dict) -> str | None:
        reg = self.ref["registered_snapshots"]
        for name in reg["verification"][policy] + reg["guard_fixtures"]:
            if reg["snapshots"][name]["csv_sha256"] == hashes:
                return name
        return None

    def reference(self, policy: str, snap: str) -> dict:
        key = (policy, snap)
        if key not in self.refs:
            r = reference.compute(self.snap_dir / snap, policy)
            frozen = self.ref["reference_results"].get(f"{policy}@{snap}")
            r["equals_frozen"] = frozen is not None and r["by_year"] == frozen["by_year"] and \
                hashlib.sha256(canon(r["lines"]).encode()).hexdigest() == frozen["lines_sha256"]
            r["facts"] = reference.line_facts(self.snap_dir / snap)
            self.refs[key] = r
        return self.refs[key]

    def stack(self, c: dict, snap: str) -> dict:
        key = (c["candidate_id"], snap)
        if key not in self.stacks:
            st = cs.build(f"{c['candidate_id']}__{snap}", c["patch"], self.snap_dir / snap, self.up, self.work / "stacks")
            if st["ok"]:
                st["exec_year"] = cs.execute(st, c["query"])
                st["exec_line"] = cs.execute(st, {**c["query"], "group_by": ["sales"]})
            self.stacks[key] = st
        return self.stacks[key]

    def snapshot_eval(self, c: dict, policy: str, snap: str) -> dict:
        st = self.stack(c, snap)
        out = {"snapshot": snap, "stack_raw_csv_registered_as": None, "reasons": []}
        if not st["ok"]:
            out.update(status="NOT_VERIFIED", reasons=["EXECUTION_FAILURE"], error=st.get("error"))
            return out
        out["stack_raw_csv_registered_as"] = self.registered(policy, st["raw_csv_sha256"])
        out["candidate_semantic_manifest_sha256"] = st["semantic_manifest_sha256"]
        out["manifest_differs_from_pristine"] = st["semantic_manifest_sha256"] != self.ref["pristine_semantic_manifest_sha256"]
        out["patch_diff_files"] = [d["file"] for d in st.get("diffs", []) if d["unified_diff"]]
        ey, el = st["exec_year"], st["exec_line"]
        out["native"] = {"year_exit": ey.get("exit_code"), "line_exit": el.get("exit_code"),
                         "compiled_sql_sha256": cs.sha_text(ey["compiled_sql"]) if ey.get("compiled_sql") else None}
        if out["stack_raw_csv_registered_as"] is None:
            out.update(status="NOT_VERIFIED", reasons=["SOURCE_SNAPSHOT_UNREGISTERED"])
            return out
        if not (ey.get("ok") and el.get("ok")):
            out.update(status="NOT_VERIFIED", reasons=["EXECUTION_FAILURE"], error=(ey.get("stdout_tail") or ey.get("error") or "")[-400:])
            return out
        metric = c["query"]["metric"]
        cand_year = {r["metric_time__year"][:4]: str(Decimal(r[metric]).quantize(reference.CENT)) for r in ey["rows"]}
        cand_lines = {str(r["sales"]): str(Decimal(r[metric]).quantize(reference.CENT)) for r in el["rows"]}
        out["candidate_by_year"] = cand_year
        out["candidate_line_count"] = len(cand_lines)
        reasons = []
        if any("Metric(" in w for w in c["query"]["where"]):
            g = cs.guards(st, c["query"], self.snap_dir / snap)
            out["guards"] = g
            if not g["ok"]:
                reasons.append("DATA_GUARD_FAILURE")
        ref = self.reference(policy, snap)
        out["reference_by_year"], out["reference_line_count"], out["reference_equals_frozen"] = ref["by_year"], ref["line_count"], ref["equals_frozen"]
        if not ref["equals_frozen"]:
            out.update(status="NOT_VERIFIED", reasons=reasons + ["REFERENCE_NOT_FROZEN"])
            return out
        mism = []
        if not dec_eq(cand_year, ref["by_year"]):
            mism.append("TOTAL_MISMATCH")
        missing = sorted(set(ref["lines"]) - set(cand_lines), key=int)
        extra = sorted(set(cand_lines) - set(ref["lines"]), key=int)
        diff_amt = sorted((k for k in set(ref["lines"]) & set(cand_lines) if Decimal(ref["lines"][k]) != Decimal(cand_lines[k])), key=int)
        if missing or extra:
            mism.append("MEMBERSHIP_MISMATCH")
        if diff_amt:
            mism.append("AMOUNT_MISMATCH")
        out["membership"] = {"expected_not_in_candidate": len(missing), "candidate_not_expected": len(extra), "amount_differs": len(diff_amt)}
        lineage = {"patch_diff_files": out["patch_diff_files"], "compiled_sql_sha256": out["native"]["compiled_sql_sha256"],
                   "candidate_query": c["query"]}
        def ce(k, exp_in, act_in):
            f = ref["facts"].get(k, {"order_item_id": k, "note": "line not in the raw source join"})
            return {**{x: f.get(x) for x in ("order_item_id", "order_id", "order_date", "status_raw", "status", "quantity", "unit_price_raw",
                                             "customer_id", "customer_country_raw", "customer_country", "store_id", "store_country")},
                    "expected_included": exp_in, "expected_amount": ref["lines"].get(k) if exp_in else None,
                    "actual_native_included": act_in, "actual_native_amount": cand_lines.get(k) if act_in else None, "lineage": lineage}
        out["counterexamples"] = [ce(k, True, False) for k in missing[:5]] + [ce(k, False, True) for k in extra[:5]] + \
                                 [ce(k, True, True) for k in diff_amt[:5]]
        out["mismatch"] = mism
        if "DATA_GUARD_FAILURE" in reasons:
            out.update(status="NOT_VERIFIED", reasons=reasons + mism)
        elif mism:
            out.update(status="MISMATCH", reasons=mism)
        else:
            out.update(status="CONFORMS", reasons=[])
        return out

    def evaluate(self, v: dict) -> dict:
        c = json.loads((E4 / "candidates" / f"{v['candidate']}.json").read_text())
        a_status, a_reasons, a_detail = authority(v["policy"], v["context"], self.trusted)
        snaps = [self.snapshot_eval(c, v["policy"], s) for s in v["snapshots"]]
        reasons = set(a_reasons)
        for s in snaps:
            reasons |= set(s["reasons"])
        claim = None
        if v.get("candidate_claim"):
            actual = snaps[0].get("candidate_by_year")
            contradicted = actual is None or not dec_eq(v["candidate_claim"]["by_year"], actual)
            claim = {"claimed": v["candidate_claim"], "actual_execution_by_year": actual, "contradicted": contradicted}
            if contradicted:
                reasons.add("CANDIDATE_CLAIM_CONTRADICTED")
        if a_status:
            status = a_status
        elif any(s["status"] == "MISMATCH" for s in snaps):
            status = "NONCONFORMING_IMPLEMENTATION"
        elif any(s["status"] == "NOT_VERIFIED" for s in snaps):
            status = "NOT_VERIFIED"
        else:
            status = "VERIFIED_FOR_LAB_CHECKS" if c["change_of"] is None else "NO_MATERIAL_DRIFT_FOR_CHECKS"
        return {"variant_id": v["variant_id"], "candidate": c["candidate_id"], "policy": v["policy"], "change_of": c["change_of"],
                "status": status, "reasons": sorted(reasons), "authority": a_detail, "snapshots": snaps, "candidate_claim": claim,
                "scope": "bounded LAB checks: registered snapshots, order-line grain, approved LAB_SIMULATED meaning; not legal compliance"}


def normalized(results: list[dict]) -> list[dict]:
    out = []
    for r in results:
        out.append({"variant_id": r["variant_id"], "status": r["status"], "reasons": r["reasons"],
                    "snapshots": [{k: s.get(k) for k in ("snapshot", "status", "reasons", "candidate_by_year", "reference_by_year",
                                                         "candidate_line_count", "membership", "manifest_differs_from_pristine")}
                                  | {"counterexample_ids": [x["order_item_id"] for x in s.get("counterexamples", [])]} for s in r["snapshots"]],
                    "claim_contradicted": (r["candidate_claim"] or {}).get("contradicted")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    chk = Checker(Path(a.upstream), E4 / "runs" / f"checker_{out.name}")
    variants = json.loads((E4 / "VARIANTS.json").read_text())["variants"]
    inputs = [{k: v for k, v in x.items() if k != "expected"} for x in variants]  # the checker never sees `expected`
    results = [chk.evaluate(v) for v in inputs]
    stacks = {f"{k[0]}__{k[1]}": {kk: vv for kk, vv in st.items() if kk not in ("exec_year", "exec_line")}
              | {"exec_year": {x: st.get("exec_year", {}).get(x) for x in ("ok", "exit_code", "argv", "compiled_sql", "mf_identity", "rows_sha256", "stdout_tail", "error")},
                 "exec_line": {x: st.get("exec_line", {}).get(x) for x in ("ok", "exit_code", "argv", "rows_sha256")}}
              for k, st in chk.stacks.items()}
    (out / "variant_results.json").write_text(json.dumps(results, indent=1, default=str) + "\n", encoding="utf-8")
    (out / "candidate_stacks.json").write_text(json.dumps(stacks, indent=1, default=str) + "\n", encoding="utf-8")
    (out / "normalized.json").write_text(json.dumps(normalized(results), indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    for r in results:
        print(f"{r['variant_id']:5s} {r['status']:30s} {','.join(r['reasons'])[:90]:90s} " +
              " ".join(f"{s['snapshot']}={s['status']}" for s in r["snapshots"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
