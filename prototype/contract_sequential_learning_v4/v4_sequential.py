"""V4 prequential run: predict -> seal -> reveal -> score -> learn, one agreement at a time.

    python v4_sequential.py run    [--hidden-dir local_hidden] [--out results]
    python v4_sequential.py replay [--hidden-dir local_hidden] [--out results]   # fresh rerun, compares sealed hashes

Standard library only; no network; no provider calls. Reuses the V3 provision-type predictor
(`predict.predict`, V3 label rules) unchanged except V3's CONTEXT_CONFLICT backoff, which is disabled
(V3 RESULTS: it misread sparse support as conflict). Frozen parameters are in PROTOCOL.md.

Arms (identical current-agreement view, identical targets):
  FROZEN_SEED   library fixed after the 2 seed agreements
  CUMULATIVE    same predictor; library grows after each agreement is sealed and revealed
  SIMPLE_COUNTS same growing history; feature base rates per article function, V3 FAMILY type frequency
  PRECEDENT     same growing history; copies the most recent prior provision at the same article function/position
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "contract_structure_prediction_v3"))
import labels   # noqa: E402  (V3, unchanged)
import predict  # noqa: E402  (V3, unchanged)

predict.CONFLICT = 0.0          # V4 frozen deviation from V3: no context-conflict backoff
SALT = "sophon-v4-sequential-targets-2026-10-14"
MODEL_VERSION = "v4-seq-1"
TARGETS_PER_DOC = 4
TYPE_TOP = 3                     # types mixed for feature expectations (V3 hit@3 shortlist)
M = 1.0                          # pseudo-count mass of the next-coarser estimate
SUBSTANTIVE = {"AFFIRMATIVE_COVENANTS", "NEGATIVE_COVENANTS", "COVENANTS_COMBINED", "FINANCIAL_COVENANTS",
               "EVENTS_OF_DEFAULT", "CONDITIONS_PRECEDENT", "REPRESENTATIONS"}
ARMS = ["FROZEN_SEED", "CUMULATIVE", "SIMPLE_COUNTS", "PRECEDENT"]
FEATURES = {   # mechanical, source-text checks on the revealed provision body (heading prefix removed)
    "EXCEPTION": re.compile(r"(?i)\b(except|other than|excluding|unless|notwithstanding)\b"),
    "PROVISO": re.compile(r"(?i)\bprovided\s*,?\s*(however|further|that)\b"),
    "QUANT_THRESHOLD": re.compile(r"\$\s?\d|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s?(?:to|:)\s?1(?:\.0+)?\b|\bpercent\b"),
    "CROSS_REFERENCE": None,     # computed: a reference to another Section of the same agreement
    "INLINE_DEFINITION": re.compile(r'"[A-Z][^"]{1,60}"\s*(?:means|shall mean|has the meaning|shall have the meaning)'
                                    r'|\(\s*(?:the|each|such|any|a|an)?\s*"[A-Z][^"]{1,60}"\s*\)'),
}
XREF = re.compile(r"\bSections?\s+(\d+)\.(\d+)")
EXCLUDE = predict.EXCLUDE


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def hkey(*parts: str) -> str:
    return hashlib.sha256("|".join((SALT,) + parts).encode()).hexdigest()


# ------------------------------------------------------------------ observation (after reveal only)
def subunits(view: dict):
    for sec in view["sections"]:
        for k, p in enumerate(sec["subunits"]):
            yield sec, k, p


def type_of(view: dict) -> dict[str, str]:
    return {p["num"]: p["provision_type"] for _, _, p in subunits(view)}


def strip_prefix(text: str, num: str, heading: str) -> str:
    t = re.sub(r"^(?:SECTION|Section|§)\s+" + re.escape(num.split(".")[0]) + r"\.0*" + re.escape(num.split(".")[1].lstrip("0") or "0")
               + r"\.?\s*", "", text)
    return t[len(heading):].lstrip(" .:-") if heading and t.startswith(heading) else t


def observe(view: dict, hidden: dict, sec: dict, k: int, p: dict) -> dict:
    body = hidden["bodies"][p["num"]]
    text = strip_prefix(body["text"], p["num"], p["heading"])
    feats = {}
    types = type_of(view)
    xrefs = {}
    for m in XREF.finditer(text):
        ref = f"{int(m.group(1))}.{int(m.group(2)):02d}"
        if ref != p["num"] and ref in types:
            xrefs.setdefault(types[ref], {"ref": f"Section {ref}", "start": m.start(), "end": m.end()})
    for f, rx in FEATURES.items():
        if f == "CROSS_REFERENCE":
            first = min(xrefs.values(), key=lambda a: a["start"]) if xrefs else None
            feats[f] = {"present": bool(first), "anchor": first and {"start": first["start"], "end": first["end"]}}
        else:
            m = rx.search(text)
            feats[f] = {"present": bool(m), "anchor": m and {"start": m.start(), "end": m.end(),
                                                              "match_sha256": hashlib.sha256(m.group(0).encode()).hexdigest()}}
    return {"doc_id": view["doc_id"], "accession": view["accession"], "path": p["path"], "num": p["num"],
            "article_function": sec["functions"][0], "ordinal": k, "provision_type": p["provision_type"],
            "body_sha256": body["sha256"], "features": feats, "xref_types": xrefs}


# ------------------------------------------------------------------ library = prior views + append-only events
def new_library(name: str) -> dict:
    return {"name": name, "version": 0, "records": [], "events": []}


def learn(lib: dict, view: dict, hidden: dict, step: int) -> list[dict]:
    """Append OBSERVE events for every located provision of a fully revealed agreement."""
    added = []
    for sec, k, p in subunits(view):
        if p.get("body_located") and p["num"] in hidden["bodies"]:
            ev = {"event": "OBSERVE", "id": f"{view['doc_id']}:{p['path']}", "known_at_step": step, **observe(view, hidden, sec, k, p)}
            lib["events"].append(ev)
            added.append(ev)
    lib["records"].append(view)
    lib["version"] += 1
    return added


def obs(lib: dict) -> list[dict]:
    return [e for e in lib["events"] if e["event"] == "OBSERVE"]


def rate(evs: list[dict], f: str, prior: float) -> tuple[float, int, list[str]]:
    n = len(evs)
    n1 = sum(e["features"][f]["present"] for e in evs)
    return (n1 + M * prior) / (n + M), n, [e["id"] for e in evs if e["features"][f]["present"]][:5]


def feature_probs_by_type(lib: dict, type_dist: dict[str, float], func: str) -> tuple[dict, dict]:
    ev = obs(lib)
    probs, support = {}, {}
    for f in FEATURES:
        g, _, _ = rate(ev, f, 0.5)
        p_total, best = 0.0, None
        for t, pt in type_dist.items():
            et = [e for e in ev if e["provision_type"] == t]
            pt_t, _, _ = rate(et, f, g)
            etf = [e for e in et if e["article_function"] == func]
            p_tf, n, ids = rate(etf, f, pt_t)
            p_total += pt * p_tf
            if best is None or pt > best[0]:
                best = (pt, t, n, ids)
        probs[f] = round(p_total, 4)
        support[f] = {"top_type": best[1], "n_type_function": best[2], "supporting_events": best[3]} if best else {}
    return probs, support


def xref_probs(lib: dict, type_dist: dict[str, float]) -> dict[str, float]:
    ev = obs(lib)
    tgt = sorted({t for e in ev for t in e["xref_types"]})
    out = {}
    for x in tgt:
        g = (sum(x in e["xref_types"] for e in ev) + 0.5) / (len(ev) + 1)
        p = 0.0
        for t, pt in type_dist.items():
            et = [e for e in ev if e["provision_type"] == t]
            p += pt * (sum(x in e["xref_types"] for e in et) + M * g) / (len(et) + M)
        out[x] = round(p, 4)
    return out


# ------------------------------------------------------------------ targets and the masked view
def targets(view: dict) -> list[dict]:
    """Content-blind positions: located subsections in substantive articles, not [Reserved], salted-hash order."""
    pool = [(sec, k, p) for sec, k, p in subunits(view)
            if sec["functions"][0] in SUBSTANTIVE and p.get("body_located") and p["provision_type"] != "RESERVED"]
    pool.sort(key=lambda x: hkey(view["doc_id"], x[2]["path"]))
    return [{"path": p["path"], "num": p["num"], "article_path": sec["path"], "article_function": sec["functions"][0],
             "ordinal": k} for sec, k, p in pool[:TARGETS_PER_DOC]]


def masked_context(view: dict, tgt: dict) -> dict:
    """What every arm may see: family, law, the target's article function/position and the rule types of the
    OTHER provisions in that article. Never the target heading, type, body, or any body text."""
    sec = next(s for s in view["sections"] if s["path"] == tgt["article_path"])
    observed = sorted({p["provision_type"] for p in sec["subunits"] if p["path"] != tgt["path"]} - EXCLUDE)
    return {"family": view["family"], "law": view["governing_law"]["value"], "section_function": tgt["article_function"],
            "ordinal": tgt["ordinal"], "observed": observed,
            "candidates": sorted(set(labels.PROVISION_VOCAB) - set(observed) - EXCLUDE)}   # V3 convention


# ------------------------------------------------------------------ arms
def predict_arm(arm: str, lib: dict, ctx: dict) -> dict:
    if arm == "PRECEDENT":
        same = [e for e in obs(lib) if e["article_function"] == ctx["section_function"]]
        if not same:
            return {"features": {f: 0.5 for f in FEATURES}, "type_ranked": [], "xref": {}, "precedent": None}
        latest = max(e["known_at_step"] for e in same)
        cands = [e for e in same if e["known_at_step"] == latest]
        e = min(cands, key=lambda e: (abs(e["ordinal"] - ctx["ordinal"]), e["ordinal"]))
        return {"features": {f: 0.9 if e["features"][f]["present"] else 0.1 for f in FEATURES},
                "type_ranked": [e["provision_type"]], "xref": {x: 0.9 for x in e["xref_types"]}, "precedent": e["id"]}
    v3_arm = "FAMILY" if arm == "SIMPLE_COUNTS" else "FAMILY_SECTION"
    tp = predict.predict("PROVISION", ctx, lib["records"], v3_arm)
    # V3 scores are per-type presence probabilities, not a distribution over the masked slot: mix over
    # V3's top-TYPE_TOP review shortlist only, renormalized (frozen V4 parameter).
    dist = {c: tp["probs"][c]["p"] for c in tp["ranked"][:TYPE_TOP]}
    z = sum(dist.values()) or 1.0
    dist = {c: p / z for c, p in dist.items()}
    if arm == "SIMPLE_COUNTS":
        ev = [e for e in obs(lib) if e["article_function"] == ctx["section_function"]]
        feats = {}
        for f in FEATURES:
            g, _, _ = rate(obs(lib), f, 0.5)
            feats[f] = round(rate(ev, f, g)[0], 4)
        return {"features": feats, "type_ranked": tp["ranked"][:5], "xref": {}, "support": {"n_function": len(ev)}}
    feats, support = feature_probs_by_type(lib, dist, ctx["section_function"])
    return {"features": feats, "type_ranked": tp["ranked"][:5], "xref": xref_probs(lib, dist), "support": support,
            "type_fallback_path": tp["fallback_path"]}


# ------------------------------------------------------------------ scoring
def score(pred: dict, truth: dict) -> dict:
    fb = {f: (pred["features"][f] - (1.0 if truth["features"][f]["present"] else 0.0)) ** 2 for f in FEATURES}
    true_x = set(truth["xref_types"])
    top3 = [x for x, _ in sorted(pred["xref"].items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
    return {"feature_brier": fb, "brier": round(sum(fb.values()) / len(fb), 4),
            "type_hit3": truth["provision_type"] in pred["type_ranked"][:3] if truth["provision_type"] not in EXCLUDE else None,
            "xref_recall3": round(len(true_x & set(top3)) / len(true_x), 3) if true_x else None,
            "xref_false3": len(set(top3) - true_x)}


class Hidden:
    """Hidden bodies, readable only for an agreement whose predictions are already sealed."""
    def __init__(self, hidden_dir: Path):
        self.dir, self.sealed, self.log = hidden_dir, set(), []

    def seal(self, doc_id: str):
        self.sealed.add(doc_id)

    def get(self, doc_id: str, role: str) -> dict:
        if role == "EVAL" and doc_id not in self.sealed:
            raise PermissionError(f"hidden bodies of {doc_id} requested before its predictions were sealed")
        self.log.append(doc_id)
        return json.loads((self.dir / f"{doc_id}.json").read_text(encoding="utf-8"))


def lib_digest(lib: dict) -> str:
    return sha({"records": [r["doc_id"] for r in lib["records"]], "events": lib["events"]})


def run(views_dir: Path, hidden_dir: Path, out: Path) -> dict:
    views = sorted((json.loads(p.read_text(encoding="utf-8")) for p in views_dir.glob("*.json")), key=lambda v: v["sequence_index"])
    if len(views) < 3:
        raise SystemExit(f"BLOCKED_SOURCE_ACCESS: {len(views)} agreement views in {views_dir}; run v4_corpus.py fetch/build first")
    seeds = [v for v in views if v["role"] == "SEED"]
    evals = [v for v in views if v["role"] == "EVAL"]
    hidden = Hidden(hidden_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "predictions").mkdir(exist_ok=True)
    frozen, growing = new_library("FROZEN_SEED"), new_library("GROWING")
    for step, v in enumerate(seeds, start=1):
        hb = hidden.get(v["doc_id"], "SEED")
        learn(frozen, v, hb, step)
        learn(growing, v, hb, step)
    chain, prev, per_doc, learned_log, counterexamples = [], "GENESIS", [], [], []
    for step, v in enumerate(evals, start=len(seeds) + 1):
        tg = targets(v)
        libs = {"FROZEN_SEED": frozen, "CUMULATIVE": growing, "SIMPLE_COUNTS": growing, "PRECEDENT": growing}
        preds = {"doc_id": v["doc_id"], "step": step, "model_version": MODEL_VERSION,
                 "library_digest": {a: lib_digest(libs[a]) for a in ARMS},
                 "library_version": {a: libs[a]["version"] for a in ARMS},
                 "targets": [{"target": t, "context": masked_context(v, t),
                              "arms": {a: predict_arm(a, libs[a], masked_context(v, t)) for a in ARMS}} for t in tg]}
        psha = sha(preds)
        (out / "predictions" / f"{v['doc_id']}.json").write_text(json.dumps(preds, indent=1), encoding="utf-8")
        chain.append({"step": step, "doc_id": v["doc_id"], "prev": prev, "predictions_sha256": psha,
                      "entry_sha256": sha([prev, psha])})
        prev = chain[-1]["entry_sha256"]
        hidden.seal(v["doc_id"])                                    # ---- reveal only after sealing
        hb = hidden.get(v["doc_id"], "EVAL")
        rows = []
        for t in preds["targets"]:
            sec = next(s for s in v["sections"] if s["path"] == t["target"]["article_path"])
            p = sec["subunits"][t["target"]["ordinal"]]
            truth = observe(v, hb, sec, t["target"]["ordinal"], p)
            row = {"target": t["target"]["path"], "true_type": truth["provision_type"],
                   "true_features": {f: truth["features"][f]["present"] for f in FEATURES},
                   "true_xref_types": sorted(truth["xref_types"]), "anchors": {f: truth["features"][f]["anchor"] for f in FEATURES},
                   "body_sha256": truth["body_sha256"], "scores": {a: score(t["arms"][a], truth) for a in ARMS}}
            if truth["provision_type"] not in {e["provision_type"] for e in obs(growing)}:
                row["NOVEL_TYPE"] = truth["provision_type"]
            for f in FEATURES:                                       # confident CUMULATIVE errors -> counterexamples
                pf, present = t["arms"]["CUMULATIVE"]["features"][f], truth["features"][f]["present"]
                if (pf >= 0.8 and not present) or (pf <= 0.2 and present):
                    ce = {"event": "COUNTEREXAMPLE", "id": f"{v['doc_id']}:{p['path']}:{f}", "known_at_step": step,
                          "feature": f, "predicted_p": pf, "observed": present, "provision_type": truth["provision_type"],
                          "article_function": truth["article_function"], "anchor": truth["features"][f]["anchor"],
                          "body_sha256": truth["body_sha256"]}
                    growing["events"].append(ce)
                    counterexamples.append(ce)
            rows.append(row)
        types_before = {e["provision_type"] for e in obs(growing)}
        edges_before = {(e["provision_type"], x) for e in obs(growing) for x in e["xref_types"]}
        added = learn(growing, v, hb, step)                          # ---- learn for FUTURE agreements only
        learned_log.append({"after_doc": v["doc_id"], "step": step, "observe_events_added": len(added),
                            "new_provision_types": sorted({e["provision_type"] for e in added} - types_before),
                            "new_dependency_edges": sorted({f"{e['provision_type']}->{x}" for e in added for x in e["xref_types"]} - {f"{a}->{b}" for a, b in edges_before}),
                            "counterexamples_logged": sum(1 for c in counterexamples if c["known_at_step"] == step),
                            "library_version": growing["version"], "library_digest": lib_digest(growing)})
        per_doc.append({"doc_id": v["doc_id"], "step": step, "n_targets": len(rows), "rows": rows,
                        "mean_brier": {a: round(sum(r["scores"][a]["brier"] for r in rows) / len(rows), 4) if rows else None for a in ARMS}})
    res = {"model_version": MODEL_VERSION, "provider_calls": 0, "seeds": [s["doc_id"] for s in seeds],
           "sequence": [e["doc_id"] for e in evals], "chain": chain, "hidden_access_order": hidden.log,
           "per_doc": per_doc, "learned_after_each_agreement": learned_log, "counterexamples": counterexamples}
    res["summary"] = summarize(per_doc)
    res["decision"] = decide(res["summary"], per_doc)
    (out / "run.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (out / "library_final_events.json").write_text(json.dumps(growing["events"], indent=1), encoding="utf-8")
    write_review_packet(per_doc, views, out / "review_packet.csv")
    return res


def write_review_packet(per_doc: list[dict], views: list[dict], path: Path) -> None:
    """Small blind packet: one row per scored target, rule labels shown, reviewer columns empty.
    Arms' predictions are deliberately omitted so the reviewer cannot be anchored by them."""
    acc = {v["doc_id"]: v["accession"] for v in views}
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["doc_id", "accession", "section", "rule_provision_type", *[f"rule_{f}" for f in FEATURES], "rule_xref_types",
                    "reviewer_type_ok(Y/N)", *[f"reviewer_{f}_ok(Y/N)" for f in FEATURES], "reviewer_note"])
        for d in per_doc:
            for r in d["rows"]:
                w.writerow([d["doc_id"], acc.get(d["doc_id"]), r["target"], r["true_type"], *[int(r["true_features"][f]) for f in FEATURES],
                            ";".join(r["true_xref_types"]), "", *["" for _ in FEATURES], ""])


def verify_freeze() -> None:
    rec = json.loads((HERE / "frozen" / "freeze_receipt.json").read_text(encoding="utf-8"))
    bad = []
    for rel, h in rec["files_lf_normalized_sha256"].items():
        data = (HERE / rel).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(data).hexdigest() != h:
            bad.append(rel)
    if bad:
        raise SystemExit(f"FROZEN FILES CHANGED, refusing to run: {bad}")


def summarize(per_doc: list[dict]) -> dict:
    rows = [r for d in per_doc for r in d["rows"]]
    s = {"n_docs": len(per_doc), "n_targets": len(rows), "arms": {}}
    rate_obs = {f: (sum(r["true_features"][f] for r in rows) / len(rows)) if rows else None for f in FEATURES}
    s["observed_feature_rates"] = {f: round(v, 3) if v is not None else None for f, v in rate_obs.items()}
    s["ceiling_features"] = sorted(f for f, v in rate_obs.items() if v is not None and (v >= 0.95 or v <= 0.05))
    live = [f for f in FEATURES if f not in s["ceiling_features"]]
    s["primary_features"] = live
    for a in ARMS:
        th = [r["scores"][a]["type_hit3"] for r in rows if r["scores"][a]["type_hit3"] is not None]
        xr = [r["scores"][a]["xref_recall3"] for r in rows if r["scores"][a]["xref_recall3"] is not None]
        s["arms"][a] = {
            "mean_brier_all_features": round(sum(r["scores"][a]["brier"] for r in rows) / len(rows), 4) if rows else None,
            "mean_brier_primary": round(sum(sum(r["scores"][a]["feature_brier"][f] for f in live) / len(live) for r in rows) / len(rows), 4) if rows and live else None,
            "per_feature_brier": {f: round(sum(r["scores"][a]["feature_brier"][f] for r in rows) / len(rows), 4) for f in FEATURES} if rows else {},
            "type_hit3": f"{sum(th)}/{len(th)}" if th else "n/a", "xref_recall3_mean": round(sum(xr) / len(xr), 3) if xr else None}
    return s


def doc_primary(d: dict, a: str, live: list[str]) -> float:
    return sum(sum(r["scores"][a]["feature_brier"][f] for f in live) / len(live) for r in d["rows"]) / len(d["rows"])


def decide(s: dict, per_doc: list[dict]) -> dict:
    """Pre-registered (PROTOCOL.md section 6). Lower Brier is better."""
    live = s["primary_features"]
    docs = [d for d in per_doc if d["rows"]]
    if len(docs) < 4 or not live:
        return {"verdict": "INCONCLUSIVE", "reason": f"{len(docs)} scorable agreements; primary features {live}"}
    wins = lambda a, b: sum(doc_primary(d, a, live) < doc_primary(d, b, live) for d in docs)
    gap = lambda a, b: s["arms"][b]["mean_brier_primary"] - s["arms"][a]["mean_brier_primary"]
    chk = {"cum_beats_frozen_docs": wins("CUMULATIVE", "FROZEN_SEED"), "cum_beats_simple_docs": wins("CUMULATIVE", "SIMPLE_COUNTS"),
           "cum_beats_precedent_docs": wins("CUMULATIVE", "PRECEDENT"), "simple_beats_frozen_docs": wins("SIMPLE_COUNTS", "FROZEN_SEED"),
           "gain_vs_frozen": round(gap("CUMULATIVE", "FROZEN_SEED"), 4), "gain_vs_simple": round(gap("CUMULATIVE", "SIMPLE_COUNTS"), 4),
           "n_docs": len(docs), "need_docs": 4 if len(docs) >= 6 else len(docs) - 1}
    need = chk["need_docs"]
    if chk["cum_beats_frozen_docs"] >= need and chk["gain_vs_frozen"] >= 0.01:
        if chk["cum_beats_simple_docs"] >= need and chk["gain_vs_simple"] >= 0.01:
            v = "KEEP: CUMULATIVE_SIGNAL_PROVISIONAL"
        else:
            v = "REVISE: EXPERIENCE_GAIN_EXPLAINED_BY_SIMPLE_COUNTS"
    else:
        v = "STOP: NO_OBSERVED_CUMULATIVE_GAIN"
    q = []
    if chk["cum_beats_precedent_docs"] < need or gap("CUMULATIVE", "PRECEDENT") <= 0:
        q.append("PRECEDENT_COPY_EQUIVALENT_OR_BETTER")   # gain may be explained by copying earlier clauses
    return {"verdict": v, "qualifiers": q, "checks": chk}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "replay"])
    ap.add_argument("--views-dir", default=str(HERE / "data" / "views"))
    ap.add_argument("--hidden-dir", default=str(HERE / "local_hidden"))
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args()
    verify_freeze()
    if a.cmd == "run":
        res = run(Path(a.views_dir), Path(a.hidden_dir), Path(a.out))
        print(json.dumps({"decision": res["decision"], "summary": res["summary"]["arms"]}, indent=1))
    else:
        first = json.loads((Path(a.out) / "run.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as t:
            again = run(Path(a.views_dir), Path(a.hidden_dir), Path(t))
        same = [x["predictions_sha256"] for x in first["chain"]] == [x["predictions_sha256"] for x in again["chain"]]
        print(json.dumps({"replay_identical_sealed_predictions": same, "chain_head": first["chain"][-1]["entry_sha256"] if first["chain"] else None}))
        if not same:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
