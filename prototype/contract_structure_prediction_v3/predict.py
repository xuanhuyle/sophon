"""V3 masked contract-structure prediction: transparent conditional frequencies with soft backoff.

Standard library only; no network; no provider calls. Every probability carries its numerator,
denominator, conditioning key, training document weights and fallback path.

    python predict.py --mode dev       # leave-one-out on TRAIN only (ceiling / discrimination check)
    python predict.py --mode heldout   # frozen heldout run -> results/heldout_run.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import labels

HERE = Path(__file__).resolve().parent
MODEL_VERSION = "csp-v3-freq-1"
SALT = "sophon-v3-masked-structure-targets-2026-10-13"
EPS = 0.5          # per-mismatch weight of a training doc lacking an observed label (soft, never 0)
M_BACKOFF = 1.0    # pseudo-count mass given to the next-coarser estimate
CONFLICT = 0.5     # if < 50% of observed labels have support under the declared context -> back off
K = 3
ARMS = ["GLOBAL_FREQ", "FAMILY", "FAMILY_SECTION", "EVIDENCED_LAW_FAMILY_SECTION"]
WRONG_SECTION = {"REPRESENTATIONS": "COVENANTS_COMBINED", "COVENANTS_COMBINED": "REPRESENTATIONS",
                 "MISCELLANEOUS": "AGENCY", "AGENCY": "MISCELLANEOUS", "CREDIT_FACILITIES": "YIELD_PROTECTION_TAXES",
                 "YIELD_PROTECTION_TAXES": "CREDIT_FACILITIES", "AFFIRMATIVE_COVENANTS": "REPRESENTATIONS"}
OTHER_FAMILY = {"CREDIT_AGREEMENT": "VENDOR_SLA", "VENDOR_SLA": "CREDIT_AGREEMENT"}
EXCLUDE = {"OTHER", "RESERVED"}


def h(*parts: str) -> str:
    return hashlib.sha256("|".join((SALT,) + parts).encode()).hexdigest()


# ---------------------------------------------------------------- training statistics
def doc_sections(rec: dict) -> set[str]:
    return {f for s in rec["sections"] for f in s["functions"]} - EXCLUDE


def section_provisions(rec: dict, func: str) -> set[str]:
    return {p["provision_type"] for s in rec["sections"] if func in s["functions"] for p in s["subunits"]} - EXCLUDE


def all_provisions(rec: dict) -> set[str]:
    return {p["provision_type"] for s in rec["sections"] for p in s["subunits"]} - EXCLUDE


def weight(observed: set[str], doc_labels: set[str]) -> float:
    return EPS ** len(observed - doc_labels)


def est(cands, docs, label_sets, observed, prior, key, use_weights=True):
    """p(c) = (sum_d w_d * 1[c in d] + M * prior(c)) / (sum_d w_d + M)."""
    ws = {d["doc_id"]: (weight(observed, label_sets[d["doc_id"]]) if use_weights else 1.0) for d in docs}
    den = sum(ws.values())
    out = {}
    for c in cands:
        num = sum(w for did, w in ws.items() if c in label_sets[did])
        out[c] = {"p": (num + M_BACKOFF * prior[c]) / (den + M_BACKOFF), "numerator": round(num, 4), "denominator": round(den, 4),
                  "conditioning_key": key, "backoff_prior": round(prior[c], 4)}
    return out, {k: round(v, 4) for k, v in ws.items()}


def global_prior(cands, docs, label_sets):
    n = len(docs)
    return {c: (sum(c in label_sets[d["doc_id"]] for d in docs) + 0.5) / (n + 1) for c in cands}


def predict(task: str, ctx: dict, train: list[dict], arm: str) -> dict:
    """ctx: family, law, observed labels, section_function (provision task), candidates."""
    cands = sorted(ctx["candidates"])
    if task == "SECTION":
        sets = {d["doc_id"]: doc_sections(d) for d in train}
    else:
        sets = {d["doc_id"]: all_provisions(d) for d in train}
    g = global_prior(cands, train, sets)
    path, flags, weights = [], [], {}
    if arm == "GLOBAL_FREQ":
        probs = {c: {"p": g[c], "numerator": sum(c in sets[d["doc_id"]] for d in train) + 0.5, "denominator": len(train) + 1,
                     "conditioning_key": "ALL_TRAINING_DOCS"} for c in cands}
        path = ["GLOBAL"]
    else:
        fam_docs = [d for d in train if d["family"] == ctx["family"]]
        fam, _ = est(cands, fam_docs, sets, set(), g, f"family={ctx['family']}", use_weights=False)
        pf = {c: fam[c]["p"] for c in cands}
        probs, path = fam, ["GLOBAL", "FAMILY"]
        if arm in ("FAMILY_SECTION", "EVIDENCED_LAW_FAMILY_SECTION"):
            obs = set(ctx["observed"])
            if task == "SECTION":
                support = [o for o in obs if any(o in sets[d["doc_id"]] for d in fam_docs)]
                pool, prior, key = fam_docs, pf, f"family={ctx['family']}+observed_sections"
                lsets = sets
            else:
                sec = ctx["section_function"]
                pool = [d for d in fam_docs if sec in doc_sections(d)]
                lsets = {d["doc_id"]: section_provisions(d, sec) for d in train}
                support = [o for o in obs if any(o in lsets[d["doc_id"]] for d in pool)]
                prior, key = pf, f"family={ctx['family']}+section={sec}+observed_provisions"
                if not pool:
                    flags.append("UNSEEN_SECTION_FUNCTION_BACKOFF_TO_FAMILY")
            consistency = len(support) / len(obs) if obs else 1.0
            if pool and consistency < CONFLICT:
                flags.append(f"CONTEXT_CONFLICT(consistency={consistency:.2f})_BACKOFF")
                if task == "SECTION":      # let the observed structure speak across all families
                    pool, prior, key, lsets = train, g, "ALL_FAMILIES+observed_sections", sets
                else:                      # drop the section condition; provisions anywhere in family
                    pool, prior, key, lsets = fam_docs, g, f"family={ctx['family']}+observed_provisions_anywhere", sets
            if pool:
                if arm == "EVIDENCED_LAW_FAMILY_SECTION":
                    laws = {d["governing_law"]["value"] for d in pool} - {"UNKNOWN"}
                    if ctx["law"] == "UNKNOWN" or len(laws) < 2:
                        flags.append("LAW_EFFECT_UNTESTABLE(heldout_law=%s; training_laws=%s)" % (ctx["law"], sorted(laws) or ["UNKNOWN"]))
                    else:
                        pool = [d for d in pool if d["governing_law"]["value"] == ctx["law"]] or pool
                        key += f"+law={ctx['law']}"
                probs, weights = est(cands, pool, lsets, obs, prior, key)
                path.append("FAMILY_SECTION" if "CONTEXT_CONFLICT" not in " ".join(flags) else "CONFLICT_BACKOFF")
    ranked = sorted(cands, key=lambda c: (-probs[c]["p"], c))
    return {"arm": arm, "model_version": MODEL_VERSION, "ranked": ranked, "top_k": ranked[:K],
            "probs": {c: {**probs[c], "p": round(probs[c]["p"], 4)} for c in cands}, "fallback_path": path, "flags": flags,
            "train_doc_weights": weights, "uncertainty": f"tiny sample: {len(train)} training docs; probabilities are smoothed frequencies, not calibrated"}


# ---------------------------------------------------------------- frozen target selection and masking
def section_cases(rec: dict) -> list[dict]:
    present = sorted(doc_sections(rec))
    chosen = sorted(present, key=lambda f: h(rec["doc_id"], "SECTION", f))[:2]
    masked_paths = [s["path"] for s in rec["sections"] if set(s["functions"]) & set(chosen)]
    visible = [s for s in rec["sections"] if s["path"] not in masked_paths]
    vis_labels = {f for s in visible for f in s["functions"]} - EXCLUDE
    hidden = sorted(set(present) - vis_labels)
    law = rec["governing_law"]["value"]
    if set(rec["governing_law"]["evidence_section_paths"]) & set(masked_paths):
        law = "UNKNOWN"   # the choice-of-law evidence sits inside a masked unit
    return [{"case_id": f"{rec['doc_id']}:SECTION", "task": "SECTION", "doc_id": rec["doc_id"], "family": rec["family"], "law": law,
             "chosen_targets": chosen, "positives": hidden, "collateral_positives": sorted(set(hidden) - set(chosen)),
             "masked_paths": masked_paths, "observed": sorted(vis_labels), "observed_order": [s["functions"][0] for s in visible],
             "candidates": sorted(set(labels.SECTION_VOCAB) - vis_labels - EXCLUDE),
             "negatives": sorted(set(labels.SECTION_VOCAB) - set(present) - EXCLUDE),
             "target_positions": [i for i, s in enumerate(rec["sections"]) if s["path"] in masked_paths]}]


def provision_cases(rec: dict) -> list[dict]:
    if rec["family"] != "CREDIT_AGREEMENT":
        return []
    out = []
    elig = [s for s in rec["sections"] if len({p["provision_type"] for p in s["subunits"]} - EXCLUDE) >= 4]
    for sec in sorted(elig, key=lambda s: h(rec["doc_id"], "PSECTION", s["path"]))[:2]:
        func = sec["functions"][0]
        here = {p["provision_type"] for p in sec["subunits"]} - EXCLUDE
        elsewhere = {p["provision_type"] for s in rec["sections"] if s is not sec for p in s["subunits"]}
        pool = sorted(here - elsewhere)          # leak guard: same type visible in another section is not a target
        chosen = sorted(pool, key=lambda t: h(rec["doc_id"], sec["path"], t))[:2]
        visible = here - set(chosen)
        out.append({"case_id": f"{rec['doc_id']}:{sec['path']}", "task": "PROVISION", "doc_id": rec["doc_id"], "family": rec["family"],
                    "law": rec["governing_law"]["value"], "section_path": sec["path"], "section_heading": sec["heading"], "section_function": func,
                    "chosen_targets": chosen, "positives": chosen, "collateral_positives": [],
                    "masked_paths": [p["path"] for p in sec["subunits"] if p["provision_type"] in chosen],
                    "observed": sorted(visible), "candidates": sorted(set(labels.PROVISION_VOCAB) - visible - EXCLUDE),
                    "negatives": sorted(set(labels.PROVISION_VOCAB) - here - EXCLUDE)})
    return out


def sequence_diag(case: dict, rec: dict, train: list[dict]) -> dict:
    if rec["family"] != "CREDIT_AGREEMENT":
        return {"status": "NOT_TESTED", "reason": "SLA units are multi-label and unordered enough that next-unit prediction is ill-defined here"}
    fam = [d for d in train if d["family"] == rec["family"]]
    order = [s["functions"][0] for s in rec["sections"]]
    res = []
    for pos in case["target_positions"]:
        prev = next((order[i] for i in range(pos - 1, -1, -1) if i not in case["target_positions"]), "START")
        cands = case["candidates"]
        big = {c: 0 for c in cands}
        n = 0
        for d in fam:
            seq = ["START"] + [s["functions"][0] for s in d["sections"]]
            for a, b in zip(seq, seq[1:]):
                if a == prev:
                    n += 1
                    if b in big:
                        big[b] += 1
        fr = {c: sum(c in doc_sections(d) for d in fam) / len(fam) for c in cands}
        p = {c: (big[c] + M_BACKOFF * fr[c]) / (n + M_BACKOFF) for c in cands}
        ranked = sorted(cands, key=lambda c: (-p[c], c))
        res.append({"position": pos, "previous_visible": prev, "true": order[pos], "rank": ranked.index(order[pos]) + 1 if order[pos] in ranked else None,
                    "top3": ranked[:3], "bigram_denominator": n})
    return {"status": "RUN", "per_position": res}


# ---------------------------------------------------------------- scoring
def p_in_top(pred: dict, c: str, k: int) -> float:
    """Tie-aware: probability that c lands in the top-k if ties are broken uniformly at random."""
    pc = pred["probs"][c]["p"]
    above = sum(1 for x in pred["ranked"] if pred["probs"][x]["p"] > pc)
    tied = sum(1 for x in pred["ranked"] if pred["probs"][x]["p"] == pc)
    return max(0.0, min(1.0, (k - above) / tied))


def score_case(case: dict, pred: dict) -> dict:
    pos, neg = set(case["positives"]), set(case["negatives"])
    ranked = pred["ranked"]
    rank = {c: ranked.index(c) + 1 for c in pos if c in ranked}
    brier = sum((pred["probs"][c]["p"] - (1.0 if c in pos else 0.0)) ** 2 for c in ranked) / len(ranked)
    ll = -sum(math.log(max(1e-6, pred["probs"][c]["p"] if c in pos else 1 - pred["probs"][c]["p"])) for c in ranked) / len(ranked)
    return {"ranks_display_order": rank, "hit1": round(sum(p_in_top(pred, c, 1) for c in pos if c in ranked), 3),
            "hit3": round(sum(p_in_top(pred, c, K) for c in pos if c in ranked), 3), "n_pos": len(pos),
            "false_expectations_top3": round(sum(p_in_top(pred, c, K) for c in neg if c in ranked), 3),
            "false_expectations_in_display_top3": sorted(c for c in ranked[:K] if c in neg), "brier": round(brier, 4), "log_loss": round(ll, 4)}


def run(train: list[dict], test: list[dict]) -> dict:
    cases = [c for r in test for c in section_cases(r) + provision_cases(r)]
    by_doc = {r["doc_id"]: r for r in test}
    out = []
    for c in cases:
        row = {"case": c, "arms": {}}
        for arm in ARMS:
            p = predict(c["task"], c, train, arm)
            row["arms"][arm] = {"prediction": p, "score": score_case(c, p)}
        if c["task"] == "SECTION":
            row["sequence_diagnostic"] = sequence_diag(c, by_doc[c["doc_id"]], train)
        out.append(row)
    # negative controls (fixed subset, fixed before any heldout outcome)
    controls = []
    first = {}
    for c in cases:
        first.setdefault((c["family"], c["task"]), c)
    for (fam, task), c in sorted(first.items()):
        bad = dict(c)
        if task == "SECTION":
            bad["family"] = OTHER_FAMILY[fam]
            what = f"family {fam} -> {bad['family']}"
        else:
            bad["section_function"] = WRONG_SECTION.get(c["section_function"], "REPRESENTATIONS")
            what = f"section {c['section_function']} -> {bad['section_function']}"
        res = {}
        for arm in ("FAMILY", "FAMILY_SECTION"):
            p = predict(task, bad, train, arm)
            res[arm] = {"score": score_case(c, p), "flags": p["flags"], "top_k": p["top_k"]}
        controls.append({"case_id": c["case_id"], "perturbation": what, "results": res})
    return {"model_version": MODEL_VERSION, "label_rules": labels.VERSION, "cases": out, "negative_controls": controls,
            "summary": summarize(out)}


def summarize(rows: list[dict]) -> dict:
    s = {}
    for arm in ARMS:
        agg = {"targets": 0, "hit1": 0, "hit3": 0, "false_expectations_top3": 0, "brier_mean": 0.0, "log_loss_mean": 0.0, "by_task": {}, "hit3_docs": {}}
        for r in rows:
            sc = r["arms"][arm]["score"]
            t = r["case"]["task"]
            bt = agg["by_task"].setdefault(t, {"targets": 0, "hit1": 0, "hit3": 0, "false_expectations_top3": 0})
            for k_ in ("hit1", "hit3"):
                agg[k_] += sc[k_]
                bt[k_] += sc[k_]
            agg["targets"] += sc["n_pos"]
            bt["targets"] += sc["n_pos"]
            agg["false_expectations_top3"] += sc["false_expectations_top3"]
            bt["false_expectations_top3"] += sc["false_expectations_top3"]
            agg["brier_mean"] += sc["brier"] / len(rows)
            agg["log_loss_mean"] += sc["log_loss"] / len(rows)
            agg["hit3_docs"][r["case"]["doc_id"]] = round(agg["hit3_docs"].get(r["case"]["doc_id"], 0) + sc["hit3"], 3)
        agg["brier_mean"], agg["log_loss_mean"] = round(agg["brier_mean"], 4), round(agg["log_loss_mean"], 4)
        s[arm] = agg
    return s


def decide(res: dict) -> dict:
    """Pre-registered decision rule (PROTOCOL.md section 6), applied mechanically."""
    S = res["summary"]
    g, f, fs = S["GLOBAL_FREQ"], S["FAMILY"], S["FAMILY_SECTION"]
    if g["targets"] == 0:
        return {"decision": "BLOCKED", "reason": "no scorable heldout targets"}
    ceiling = g["hit3"] / g["targets"] >= 0.9
    gain_docs = [d for d in fs["hit3_docs"] if fs["hit3_docs"][d] > g["hit3_docs"].get(d, 0)]
    backoffs = [c for c in res["negative_controls"] if any("BACKOFF" in fl for fl in c["results"]["FAMILY_SECTION"]["flags"])]
    checks = {"global_top3_rate": round(g["hit3"] / g["targets"], 3), "ceiling_effect": ceiling,
              "fs_minus_global_hit3": fs["hit3"] - g["hit3"], "fs_gain_docs": gain_docs,
              "fs_false_exp_not_worse_than_global": fs["false_expectations_top3"] <= g["false_expectations_top3"],
              "observable_backoff_in_negative_controls": len(backoffs),
              "fs_minus_family_hit3": fs["hit3"] - f["hit3"], "fs_minus_family_brier": round(fs["brier_mean"] - f["brier_mean"], 4),
              "fs_minus_global_brier": round(fs["brier_mean"] - g["brier_mean"], 4)}
    hurdle = checks["fs_minus_global_hit3"] >= 3 and len(gain_docs) >= 2 and checks["fs_false_exp_not_worse_than_global"] and len(backoffs) >= 1
    if ceiling:
        d = "CEILING_EFFECT_UNINFORMATIVE"
    elif hurdle and (checks["fs_minus_family_hit3"] > 0 or checks["fs_minus_family_brier"] < 0):
        d = "PREDICTIVE_SIGNAL_PROVISIONAL"
    elif hurdle or (fs["hit3"] > g["hit3"] or fs["brier_mean"] < g["brier_mean"]):
        d = "GLOBAL_OR_FAMILY_AS_GOOD" if checks["fs_minus_family_hit3"] <= 0 and checks["fs_minus_family_brier"] >= 0 else "INCONCLUSIVE"
    else:
        d = "NO_INCREMENTAL_SECTION_SIGNAL"
    return {"decision": d, "hurdle_met": hurdle, "checks": checks}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dev", "heldout"], required=True)
    a = ap.parse_args()
    train = json.loads((HERE / "data" / "records_train.json").read_text(encoding="utf-8"))["records"]
    (HERE / "results").mkdir(exist_ok=True)
    if a.mode == "dev":
        rows, ctrls = [], []
        for d in train:
            r = run([t for t in train if t["doc_id"] != d["doc_id"]], [d])
            rows += r["cases"]
            ctrls += r["negative_controls"]
        res = {"mode": "DEV_LEAVE_ONE_OUT_TRAIN_ONLY", "cases": rows, "negative_controls": ctrls, "summary": summarize(rows)}
        res["decision_if_this_were_heldout"] = decide(res)
        path = HERE / "results" / "dev_loo.json"
    else:
        rec = HERE / "frozen" / "freeze_receipt.json"
        if not rec.exists():
            raise SystemExit("no freeze receipt; refusing heldout run")
        receipt = json.loads(rec.read_text(encoding="utf-8"))
        for name, digest in receipt["files"].items():
            if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
                raise SystemExit(f"{name} changed after freeze; refusing heldout run")
        test = json.loads((HERE / "data" / "records_heldout.json").read_text(encoding="utf-8"))["records"]
        res = run(train, test)
        res["mode"] = "HELDOUT_FROZEN"
        res["freeze_receipt"] = receipt
        res["decision"] = decide(res)
        path = HERE / "results" / "heldout_run.json"
    path.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    S = res["summary"]
    for arm in ARMS:
        x = S[arm]
        print(f"{arm:30s} targets={x['targets']:3d} hit@1={x['hit1']:6.2f} hit@3={x['hit3']:6.2f} falseExp@3={x['false_expectations_top3']:6.2f} "
              f"brier={x['brier_mean']:.4f} logloss={x['log_loss_mean']:.4f} by_task={json.dumps(x['by_task'])}")
    print(json.dumps(res.get("decision") or res.get("decision_if_this_were_heldout"), indent=1))


if __name__ == "__main__":
    main()
