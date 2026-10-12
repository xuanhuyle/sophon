"""E5 runner (written after the freeze). Generates the proposal with the isolated transposer, builds and executes
every native revision, and evaluates every scenario. It strips `expected` from SCENARIOS.json and never reads it.

    .upstream/.venv/bin/python src/run_e5.py --upstream .upstream --out evidence/run
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import time
from decimal import Decimal
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
E5 = HERE.parent
EXP = E5.parent
sys.path.insert(0, str(HERE))
import authority as authmod  # noqa: E402
import claim  # noqa: E402
import e4_adapter  # noqa: E402
import lifecycle  # noqa: E402
import run_transposer  # noqa: E402

oracle = e4_adapter.oracle  # E5 src/oracle.py, loaded by path

MET = "dbt/retail_dwh/models/marts/semantic/_metrics.yml"
CENT = Decimal("0.01")


def j(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


def sha(o) -> str:
    return hashlib.sha256(canon(o).encode()).hexdigest()


def strip_expected(o):
    if isinstance(o, dict):
        return {k: strip_expected(v) for k, v in o.items() if k != "expected"}
    if isinstance(o, list):
        return [strip_expected(x) for x in o]
    return o


def get_in(o, path):
    for p in path:
        o = o[p]
    return o


def mutate(packet: dict, ctl: dict) -> dict:
    pk = copy.deepcopy(packet)
    for op in ctl["ops"]:
        parent, last = get_in(pk, op["path"][:-1]), op["path"][-1]
        if op["op"] == "set":
            parent[last] = op["value"]
        elif op["op"] == "delete":
            del parent[last]
        elif op["op"] == "replace_in_text":
            assert parent[last].count(op["old"]) == 1
            parent[last] = parent[last].replace(op["old"], op["new"])
    if ctl.get("rehash_v2_approval") and "AP_S1_V2" in pk["approvals"]:
        v2 = pk["requirement_versions"]["P1_v2"]
        pk["approvals"]["AP_S1_V2"]["claim"]["normalized_claim"] = claim.normalized_claim(v2)
        pk["approvals"]["AP_S1_V2"]["claim"]["normalized_claim_sha256"] = claim.meaning_sha(v2)
    if ctl.get("rehash_baseline_file"):
        pk["native_baseline"]["file_sha256"][MET] = claim.sha_text(pk["native_baseline"]["files"][MET])
    return pk


def threshold_variant(packet: dict, value: str, text_value: str | None) -> dict:
    """Non-scored sensitivity packet: the v2 threshold set to `value`; if text_value is given, the amendment source and
    clause text say `text_value` and every hash/approval is recomputed so the variant is internally authorized."""
    pk = copy.deepcopy(packet)
    v2 = pk["requirement_versions"]["P1_v2"]
    if text_value is not None:
        doc = pk["source_documents"][v2["governing_source"]["document_id"]]
        old_clause = v2["requirement"]["text"]
        new_clause = old_clause.replace("at least 120.", f"at least {text_value}.")
        doc["text"] = doc["text"].replace(old_clause, new_clause)
        doc["sha256"] = claim.sha_text(doc["text"])
        v2["requirement"]["text"] = new_clause
        for a in v2["requirement"]["atoms"]:
            a["span"][1] = a["span"][1] + (len(new_clause) - len(old_clause)) if a["atom_id"] == "unit_price_threshold" else a["span"][1]
            a["text"] = new_clause[a["span"][0]:a["span"][1]]
        v2["governing_source"]["content_sha256"] = doc["sha256"]
        pk["approvals"]["AP_S1_V2"]["scope"]["source_sha256"] = doc["sha256"]
    for a in v2["requirement"]["atoms"]:
        if a["atom_id"] == "unit_price_threshold":
            a["value"] = value
    pk["approvals"]["AP_S1_V2"]["claim"]["normalized_claim"] = claim.normalized_claim(v2)
    pk["approvals"]["AP_S1_V2"]["claim"]["normalized_claim_sha256"] = claim.meaning_sha(v2)
    return pk


def compose(cands: dict, cid: str, generated_patch: list | None) -> dict:
    c = cands[cid]
    patch = []
    for part in c["compose"]:
        patch += generated_patch if part == "GENERATED" else cands[part]["patch"]
    return {"candidate_id": cid, "patch": patch + c["patch"], "query": c["query"]}


def metric_yaml(stack: dict, name: str) -> dict | None:
    doc = yaml.safe_load((Path(stack["upstream"]) / MET).read_text(encoding="utf-8"))
    return next((m for m in doc.get("metrics", []) if m.get("name") == name), None)


def manifest(stack: dict) -> dict:
    return j(Path(stack["upstream"]) / "dbt" / "retail_dwh" / "target" / "semantic_manifest.json")


def manifest_metric(stack: dict, name: str) -> dict | None:
    m = next((x for x in manifest(stack)["metrics"] if x["name"] == name), None)
    return None if m is None else {k: v for k, v in m.items() if k != "metadata"}


def lines_of(st: dict, metric: str) -> dict:
    return {str(r["sales"]): str(Decimal(r[metric]).quantize(CENT)) for r in st["exec_line"]["rows"]}


def years_of(st: dict, metric: str) -> dict:
    return {r["metric_time__year"][:4]: str(Decimal(r[metric]).quantize(CENT)) for r in st["exec_year"]["rows"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cost = {"paid_calls": 0, "model_calls": 0, "phases_seconds": {}}
    t0 = time.time()

    def lap(name):
        nonlocal t0
        cost["phases_seconds"][name] = round(time.time() - t0, 1)
        t0 = time.time()

    sc = strip_expected(j(E5 / "SCENARIOS.json"))  # the runner never sees `expected`
    ctx, windows = sc["contexts"], sc["windows"]
    scen = {s["id"]: s for s in sc["scenarios"]}
    ref = j(E5 / "REFERENCE.json")
    packet_path = E5 / "TRANSPOSE_PACKET.json"
    packet = j(packet_path)
    cands = {p.stem: j(p) for p in sorted((E5 / "candidates").glob("*.json"))}
    R = {"packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest()}

    # ---------------------------------------------------------------- F3 (generation) and N1 (refusals): isolated transposer
    main_run = run_transposer.run(packet_path, out / "transposer" / "main")
    prop = main_run["proposal"]
    R["transposer"] = {"invocation": main_run["invocation"], "proposal": prop}
    n1 = {}
    for ctl in j(E5 / "controls" / "N1_PACKET_MUTATIONS.json")["controls"]:
        r = run_transposer.run(mutate(packet, ctl), out / "transposer" / "N1" / ctl["control_id"])
        p = r["proposal"] or {}
        n1[ctl["control_id"]] = {"status": p.get("status"), "reasons": sorted({x for f in p.get("refusals", []) for x in f["reasons"]}),
                                 "patch": p.get("patch"), "exit_code": r["invocation"]["exit_code"],
                                 "no_repository_file_opened": r["invocation"]["no_repository_file_opened"]}
    R["N1"] = n1
    sens = {}
    for name, (val, txt) in {"threshold_135_reapproved": ("135", "135"), "threshold_120.00_same_text": ("120.00", None),
                             "threshold_99.5_reapproved": ("99.5", "99.5")}.items():
        r = run_transposer.run(threshold_variant(packet, val, txt), out / "transposer" / "sensitivity" / name)
        p = r["proposal"] or {}
        sens[name] = {"ir_value": val, "status": p.get("status"), "emitted_filter": (p.get("rendered") or {}).get("after", {}).get("filter"),
                      "reasons": sorted({x for f in p.get("refusals", []) for x in f["reasons"]})}
    R["sensitivity_non_scored"] = sens
    lap("transposer")

    # ---------------------------------------------------------------- native stacks
    chk = e4_adapter.E5Checker(Path(a.upstream), E5 / "runs" / f"e5_{out.name}", ref)
    R["snapshots_match_frozen"] = chk.snapshots_match_frozen
    gen_patch = (prop or {}).get("patch") or []
    C = {cid: compose(cands, cid, gen_patch) for cid in cands}
    C["GENERATED"] = {"candidate_id": "GENERATED", "patch": cands["BASELINE"]["patch"] + gen_patch, "query": cands["BASELINE"]["query"]}
    p2q = {"metric": "french_market_revenue", "group_by": ["metric_time__year"], "where": []}
    S = ["PINNED", "BOUNDARY120"]
    for s in S:  # sanity: no order dates before the earliest effective date (segment windows starting there are open-start)
        assert min(f["order_date"] for f in oracle.order_lines(chk.snap_dir / s).values()) >= authmod.DATA_START
    base_p1 = chk.run_query(C["BASELINE"], "PINNED", C["BASELINE"]["query"])
    base_p2 = chk.run_query(C["BASELINE"], "PINNED", p2q)
    R["G0_baseline"] = {"build_ok": base_p1["ok"], "semantic_manifest_sha256": base_p1.get("semantic_manifest_sha256"),
                        "p1_ok": bool(base_p1.get("exec_year", {}).get("ok")), "p2_ok": bool(base_p2.get("exec_year", {}).get("ok")),
                        "p1_by_year": years_of(base_p1, "premium_completed_revenue") if base_p1["ok"] else None,
                        "p2_by_year": years_of(base_p2, "french_market_revenue") if base_p1["ok"] else None}
    lap("baseline")

    # ---------------------------------------------------------------- authority (F1, F1B, F2 state parts)
    auth = authmod.Authority()
    states = {}
    for sid in ("F1", "F1B", "F2"):
        K = ctx[scen[sid]["knowledge_at"]]
        states[sid] = {"knowledge_at": K, "version_state": {v: auth.version_state(v, K)["state"] for v in authmod.VERSIONS},
                       "governing": {d: auth.governing(d, K)["version"] for d in scen[sid]["probe_dates"]}}
    R["authority"] = states

    # ---------------------------------------------------------------- native checks (F1, F1B, F2, F4, N2)
    checks = {}
    for sid in ("F1", "F1B", "F2", "F4", "N2"):
        for c in scen[sid]["checks"]:
            cc = {**c, "window": windows[c["window"]]}
            checks[c["check_id"]] = chk.evaluate_check(cc, C[c["candidate"]], auth, ctx[c["knowledge_at"]])
    R["checks"] = checks
    lap("checks")

    # ---------------------------------------------------------------- F2 lifecycle before proposal
    R["F2_lifecycle_before_proposal"] = lifecycle.state(None, auth.roster)

    # ---------------------------------------------------------------- F3 native facts of the generated revision
    gen = {s: chk.run_query(C["GENERATED"], s, C["GENERATED"]["query"]) for s in S}
    base = {s: chk.run_query(C["BASELINE"], s, C["BASELINE"]["query"]) for s in S}
    frozen_patches = {cid: c["patch"] for cid, c in cands.items()}
    R["F3"] = {"status": (prop or {}).get("status"), "modified_metrics": (prop or {}).get("modified_metrics"),
               "not_affected": [x["metric"] for x in (prop or {}).get("not_affected", [])], "delta": [
                   {k: d[k] for k in ("atom_id", "fact_kind", "op", "from", "to", "unit")} for d in (prop or {}).get("delta", [])],
               "patch_files": sorted({p["file"] for p in gen_patch}), "patch_ops": len(gen_patch),
               "generated_stack_builds": all(gen[s]["ok"] for s in S),
               "generated_compiled_sql": gen["PINNED"].get("exec_year", {}).get("compiled_sql"),
               "generated_semantic_manifest_sha256": {s: gen[s].get("semantic_manifest_sha256") for s in S},
               "baseline_semantic_manifest_sha256": {s: base[s].get("semantic_manifest_sha256") for s in S},
               "metric_name_set_unchanged": all(sorted(m["name"] for m in manifest(gen[s])["metrics"]) == sorted(m["name"] for m in manifest(base[s])["metrics"]) for s in S),
               "p2_block_unchanged_by_patch": all(metric_yaml(gen[s], "french_market_revenue") == metric_yaml(base[s], "french_market_revenue") for s in S),
               "p1_yaml_before": metric_yaml(base["PINNED"], "premium_completed_revenue"),
               "p1_yaml_after": metric_yaml(gen["PINNED"], "premium_completed_revenue"),
               "patch_differs_from_every_frozen_candidate": all(gen_patch != fp for fp in frozen_patches.values()),
               "patch_sha256": sha(gen_patch), "diffs": gen["PINNED"].get("diffs", [])[len(cands["BASELINE"]["patch"]):],
               "no_repository_file_opened_by_transposer": main_run["invocation"]["no_repository_file_opened"]}
    R["F3"]["compiled_sql_contains_threshold_120"] = "sales__unit_price >= 120" in (R["F3"]["generated_compiled_sql"] or "")
    lap("generated")

    # ---------------------------------------------------------------- F5 historical version routing
    routings = {}
    registry_cands = {"BASELINE": C["BASELINE"], "GENERATED": C["GENERATED"]}
    for rt in scen["F5"]["routings"]:
        K = ctx[rt["knowledge_at"]]
        segs = auth.routing(K)
        res_segs, comb_lines, comb_year = [], {s: {} for s in S}, {s: {} for s in S}
        for i, sg in enumerate(segs):
            w = [None if sg["window"][0] == authmod.DATA_START else sg["window"][0], sg["window"][1]]
            rev = rt["revision_registry"].get(sg["version"])
            r = chk.evaluate_check({"check_id": f"{rt['routing_id']}.seg{i}", "requested_version": sg["version"], "window": w, "snapshots": S},
                                   registry_cands[rev], auth, K)
            for s in S:
                st = chk.run_query(registry_cands[rev], s, r["query"])
                for k, v in lines_of(st, "premium_completed_revenue").items():
                    comb_lines[s][k] = v
                for y, v in years_of(st, "premium_completed_revenue").items():
                    comb_year[s][y] = str((Decimal(comb_year[s].get(y, "0")) + Decimal(v)).quantize(CENT))
            res_segs.append({"window": sg["window"], "native_window": w, "version": sg["version"], "revision": rev,
                             "status": "CONFORMS" if r["status"] == "VERIFIED_FOR_LAB_CHECKS" else r["status"], "check": r})
        key = f"ROUTED@{rt['knowledge_at']}"
        comb = {s: {"by_year": dict(sorted(comb_year[s].items())), "lines_sha256": sha(dict(sorted(comb_lines[s].items(), key=lambda kv: int(kv[0])))),
                    "line_count": len(comb_lines[s])} for s in S}
        eq = {s: comb[s]["by_year"] == ref["reference_results"][f"{key}@{s}"]["by_year"]
              and comb[s]["lines_sha256"] == ref["reference_results"][f"{key}@{s}"]["lines_sha256"] for s in S}
        routings[rt["routing_id"]] = {"knowledge_at": K, "label": "HISTORICAL_VERSION_ROUTING (explicit selection of preserved native revisions; "
                                      "not a native bitemporal capability)", "segments": res_segs, "combined": comb,
                                      "combined_equals_reference": {"reference": key, "per_snapshot": eq}}
    naive = {}
    for s in S:
        st = chk.run_query(C["GENERATED"], s, C["GENERATED"]["query"])
        naive[s] = {"generated_all_dates_by_year": years_of(st, "premium_completed_revenue"),
                    "routed_by_year": ref["reference_results"][f"ROUTED@K_POST@{s}"]["by_year"]}
        naive[s]["differs_in_2024"] = naive[s]["generated_all_dates_by_year"].get("2024") != naive[s]["routed_by_year"].get("2024")
    R["F5"] = {"routings": routings, "naive_single_revision": naive}
    lap("routing")

    # ---------------------------------------------------------------- F6 / N3 P2 control
    def p2_control(sid: str) -> dict:
        s_ = scen[sid]
        before, after = C[s_["before"]], C[s_["after"]]
        q = {"metric": s_["metric"], "group_by": ["metric_time__year"], "where": []}
        per = {}
        for s in s_["snapshots"]:
            bst, ast = chk.run_query(before, s, q), chk.run_query(after, s, q)
            ev = chk.snapshot_eval({**after, "query": q}, "P2|ALL", s)  # E4 algorithm vs independent P2 oracle
            per[s] = {"yaml_block_identical": metric_yaml(bst, s_["metric"]) == metric_yaml(ast, s_["metric"]),
                      "yaml_after": metric_yaml(ast, s_["metric"]),
                      "manifest_node_identical": manifest_metric(bst, s_["metric"]) == manifest_metric(ast, s_["metric"]),
                      # order-insensitive: `mf` returns rows without ORDER BY
                      "native_identical": years_of(bst, s_["metric"]) == years_of(ast, s_["metric"])
                      and lines_of(bst, s_["metric"]) == lines_of(ast, s_["metric"]),
                      "before_by_year": years_of(bst, s_["metric"]), "after_by_year": years_of(ast, s_["metric"]),
                      "after_vs_P2_oracle": {k: ev.get(k) for k in ("status", "reasons", "membership", "candidate_by_year", "reference_by_year")},
                      "counterexamples": ev.get("counterexamples", [])}
        ok = all(p["yaml_block_identical"] and p["manifest_node_identical"] and p["native_identical"] and p["after_vs_P2_oracle"]["status"] == "CONFORMS"
                 for p in per.values())
        return {"status": "P2_UNCHANGED_VERIFIED" if ok else "P2_CHANGED_DETECTED", "per_snapshot": per,
                "yaml_block_identical": all(p["yaml_block_identical"] for p in per.values()),
                "manifest_node_identical": all(p["manifest_node_identical"] for p in per.values()),
                "native_identical": all(p["native_identical"] for p in per.values()),
                "after_conforms_to_P2_oracle": all(p["after_vs_P2_oracle"]["status"] == "CONFORMS" for p in per.values()),
                "has_row_counterexample": any(p["counterexamples"] for p in per.values())}
    R["F6"] = p2_control("F6")
    R["N3"] = p2_control("N3")
    lap("p2_control")

    # ---------------------------------------------------------------- F7 / N4 lifecycle
    approvals = {"AP_S1_V2": j(E5 / "approvals" / "AP_S1_V2.json")}
    f4 = checks["F4.generated_vs_governing"]
    lc = lifecycle.state(prop, auth.roster, verification=f4)
    R["F7"] = {"proposal_id": (prop or {}).get("proposal_id"), "state": lc["state"], "reasons": lc["reasons"], "deployed": lc["deployed"],
               "deployment_authorization": None, "reviewer_decision": ((prop or {}).get("reviewer") or {}).get("decision"),
               "proposal_review_status": (prop or {}).get("review_status"),
               "original_semantic_manifest_sha256": R["F3"]["baseline_semantic_manifest_sha256"]["PINNED"],
               "proposed_semantic_manifest_sha256": R["F3"]["generated_semantic_manifest_sha256"]["PINNED"],
               "receipts": {"transposer_invocation": "transposer/main/invocation.json", "native_generated": "candidate_stacks.json#GENERATED__*",
                            "verification": "checks.F4.generated_vs_governing", "authority": "authority.F2",
                            "approval_of_meaning": "AP_S1_V2 (LAB_SIMULATED; not a deployment authorization)"}}
    n4 = {}
    for case in scen["N4"]["cases"]:
        i = case["inputs"]
        n4[case["case_id"]] = lifecycle.state(prop if i["proposal"] else None, auth.roster,
                                              verification=checks["F4.generated_vs_governing"] if i["verification"] == "F4" else None,
                                              forged_claimed_state=i["forged_claimed_state"], deployment_authorization=i["deployment_authorization"],
                                              approvals=approvals)
    R["N4"] = n4
    lap("lifecycle")
    R["cost"] = cost

    # ---------------------------------------------------------------- write
    stacks = {f"{k[0]}__{k[1]}__q{sha(k[2])[:8]}": {kk: vv for kk, vv in st.items() if kk not in ("exec_year", "exec_line")}
              | {"query": json.loads(k[2]),
                 "exec_year": {x: st.get("exec_year", {}).get(x) for x in ("ok", "exit_code", "argv", "compiled_sql", "mf_identity", "rows_sha256", "stdout_tail", "error")},
                 "exec_line": {x: st.get("exec_line", {}).get(x) for x in ("ok", "exit_code", "argv", "rows_sha256")}}
              for k, st in chk.stacks.items()}
    (out / "results.json").write_text(json.dumps(R, indent=1, default=str) + "\n", encoding="utf-8")
    (out / "candidate_stacks.json").write_text(json.dumps(stacks, indent=1, default=str) + "\n", encoding="utf-8")
    (out / "normalized.json").write_text(json.dumps(normalized(R), indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    (out / "cost_log.json").write_text(json.dumps(cost, indent=1) + "\n", encoding="utf-8")
    for cid, r in checks.items():
        print(f"{cid:34s} {r['status']:30s} {','.join(r['reasons'])[:70]:70s} " + " ".join(f"{s['snapshot']}={s['status']}" for s in r["snapshots"]))
    print("F3", R["F3"]["status"], R["F3"]["compiled_sql_contains_threshold_120"], "F6", R["F6"]["status"], "N3", R["N3"]["status"], "F7", R["F7"]["state"])
    print("N1", {k: (v["status"], v["reasons"]) for k, v in n1.items()})
    print("routing", {k: [(s["version"], s["status"]) for s in v["segments"]] for k, v in routings.items()}, "sens", {k: v["emitted_filter"] for k, v in sens.items()})
    return 0


def normalized(R: dict) -> dict:
    p = R["transposer"]["proposal"] or {}
    return {
        "packet_sha256": R["packet_sha256"],
        "proposal": {k: p.get(k) for k in ("status", "modified_metrics", "delta", "patch", "rendered", "review_status", "deployment")},
        "N1": {k: {x: v[x] for x in ("status", "reasons", "patch")} for k, v in R["N1"].items()},
        "sensitivity": R["sensitivity_non_scored"],
        "G0": R["G0_baseline"], "authority": R["authority"],
        "checks": {k: {"status": v["status"], "reasons": v["reasons"],
                       "snapshots": [{x: s.get(x) for x in ("snapshot", "status", "reasons", "candidate_by_year", "reference_by_year", "candidate_line_count",
                                                            "membership", "native_executed_ok")}
                                     | {"counterexample_ids": [c["order_item_id"] for c in s.get("counterexamples", [])]} for s in v["snapshots"]]}
                   for k, v in R["checks"].items()},
        "F3": {k: v for k, v in R["F3"].items() if k not in ("diffs",)},
        "F5": {"routings": {k: {"segments": [{x: s[x] for x in ("window", "version", "revision", "status")} for s in v["segments"]],
                                "combined": v["combined"], "equals": v["combined_equals_reference"]} for k, v in R["F5"]["routings"].items()},
               "naive": R["F5"]["naive_single_revision"]},
        "F6": {k: v for k, v in R["F6"].items() if k != "per_snapshot"}, "N3": {k: v for k, v in R["N3"].items() if k != "per_snapshot"},
        "N3_counterexample_ids": {s: [c["order_item_id"] for c in v["counterexamples"]] for s, v in R["N3"]["per_snapshot"].items()},
        "F7": {k: v for k, v in R["F7"].items() if k != "receipts"}, "N4": R["N4"]}


if __name__ == "__main__":
    raise SystemExit(main())
