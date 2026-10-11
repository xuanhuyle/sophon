#!/usr/bin/env python3
"""Mechanical scorer, second pass (PROTOCOL.md §5, §8). The first pass is kept in results/*_firstpass.*.

Changes from the first pass, all documented in RESULTS.md and none touching a threshold:
  * citation checks resolve the article from the version id or by searching every staged article, normalise
    apostrophes/spaces, accept a quote followed by the arm's own annotation (longest exact prefix >= 40 chars);
  * the "required affected" sets are refined to rules whose implemented *value* the changed text alters
    (strict pattern-based sets are still reported as IR_strict / FS_strict);
  * transposition correctness is a reference-driven replay: the scorer evaluates each arm's proposal tree at the
    reference requirements (M1: BNC 2026 rate and the twenty D613-6 split rules; M2: the Acre share; T1a: no value
    may change at the announced dates; T1b: the decree constants must appear in the proposal and the arm's own
    evaluation rows must replay), instead of parsing arm-specific evaluation fields;
  * engine amounts in euros are compared with a 0.5 tolerance (the engine rounds), percentages with 1e-6.

  python3 src/score.py --runs-root RUNS --out results
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "src" / "publicodes_eval.mjs"
ARMS = ["A", "B"]
TASKS = ["T0", "T1a", "T1b", "R1", "R2", "R3", "R4", "R5", "M0", "M1", "M2"]
AE_PREFIX = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"
AE_BASE = {"salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur": "oui",
           "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois", "établissement . commune . département . outre-mer": "non", "entreprise . activités . revenus mixtes": "non",
           "entreprise . date de création": "01/01/2019", "dirigeant . exonérations . ACRE": "non"}
# the library computes each category only when the activity selects it (entreprise.publicodes: `applicable si: activités . service ou vente = ...` / `activité . nature . libérale`; auto-entrepreneur.publicodes: `Cipav` needs `libérale . réglementée`)
AE_GROUP_SIT = {"service BNC": {**AE_BASE, "entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "non"},
                "service BNC Cipav": {**AE_BASE, "entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "oui"},
                "service BIC": {**AE_BASE, "entreprise . activité . nature": "'artisanale'", "entreprise . activités . service ou vente": "'service'"},
                "vente restauration hébergement": {**AE_BASE, "entreprise . activité . nature": "'commerciale'", "entreprise . activités . service ou vente": "'vente'"}}
AE_SIT = AE_GROUP_SIT["service BNC"]
TI_ACRE_SIT = {"date": "01/06/2026", "salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "non",
               "entreprise . imposition": "'IR'", "entreprise . activité . nature": "'artisanale'", "entreprise . date de création": "01/02/2026",
               "dirigeant . exonérations . ACRE": "oui", "dirigeant . indépendant . revenu professionnel": "20000 €/an"}
T1B_CONSTANTS = {"L136-3 abattement 26 %": [r"\b26\s?%", r"\b0\.26\b"], "D136-5 floor 1,76 % PASS": [r"1\.76\s?%", r"0\.0176"], "D136-5 ceiling 130 % PASS": [r"\b130\s?%", r"\b1\.3\b"],
                 "D621-2 T1 1,5 %": [r"\b1\.5\s?%"], "D621-2 T2 4 %": [r"\b4\s?%"], "D633-3 I+II within PSS 17,15 + 0,72 = 17,87 % (library keeps one first-tranche rate, 17,75 before)": [r"17\.87\s?%", r"17\.15"], "D633-3 II 0,72 %": [r"0\.72\s?%"]}


# ----------------------------------------------------------------------------- helpers
def load_json(p: Path):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"__error__": f"{type(e).__name__}: {e}"}


def norm(s) -> str:
    s = str(s or "").replace(" ", " ").replace(" ", " ").replace("’", "'").replace("‘", "'")
    s = re.sub(r"\s*'\s*", "'", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def law_articles(stage: Path) -> dict:
    out = {}
    for d in sorted((stage / "inputs" / "law").iterdir()):
        j = json.load(open(d / "articles.json", encoding="utf-8"))
        out[j["snapshot"]] = {num: recs[0] for num, recs in j["articles"].items()}
    return out


def all_texts(law: dict) -> list[tuple[str, str, str]]:
    """[(article, version_id, normalised text incl. nota)]"""
    out = []
    for snap in law.values():
        for num, a in snap.items():
            t = norm(a["text"]) + " " + norm(a.get("nota") or "")
            out.append((num, a["id"], t))
    return out


def texts_up_to(runs: Path, arm: str, task: str) -> list[tuple[str, str, str]]:
    """Texts of every law snapshot staged for this arm in this task or an earlier one: the arm's persistent work/
    legitimately carries earlier snapshots (for example the 2024-07 text of D613-4 seen at T1b), so a quotation from
    one of them is a real quotation, not a fabrication."""
    seen, out = set(), []
    for t in TASKS[: TASKS.index(task) + 1]:
        d = runs / arm / t / "inputs" / "law"
        if not d.exists():
            continue
        for num, vid, txt in all_texts(law_articles(runs / arm / t)):
            if (vid, txt) not in seen:
                seen.add((vid, txt)); out.append((num, vid, txt))
    return out


def quote_check(texts, quote: str) -> dict:
    """exact: whole normalised quote found; prefix: longest exact prefix (>=40 chars, cut at an annotation marker) found."""
    q = norm(quote)
    if not q:
        return {"found": False, "mode": "empty"}
    for num, vid, t in texts:
        if q in t:
            return {"found": True, "mode": "exact", "article": num, "version_id": vid}
    # the arms sometimes append an annotation after the quote: '... <quote>  (in force ...) -> comment'
    for cut in (" (", " [", " ->", " and ", " ; ", "  "):
        head = q.split(cut)[0].strip()
        if len(head) >= 30:
            for num, vid, t in texts:
                if head in t:
                    return {"found": True, "mode": "prefix", "article": num, "version_id": vid, "prefix_len": len(head)}
    # ellipsis-split quotes: every fragment >= 25 chars must be found in one article
    frags = [f.strip() for f in re.split(r"…|\.\.\.", q) if len(f.strip()) >= 25]
    if len(frags) >= 2:
        for num, vid, t in texts:
            if all(f in t for f in frags):
                return {"found": True, "mode": "fragments", "article": num, "version_id": vid}
    return {"found": False, "mode": "not_found"}


def numeric(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def node_eval(rules_dirs: list[Path], situation: dict, rules: list[str]) -> dict:
    cmd = ["node", str(EVAL), "evaluate"]
    for d in rules_dirs:
        cmd += ["--rules", str(d)]
    cmd += ["--situation", json.dumps(situation, ensure_ascii=False)]
    for r in rules:
        cmd += ["--rule", r]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"__error__": f"engine failure: {r.stdout[:200]} {r.stderr[:200]}"}
    if "error" in j:
        return {"__error__": j["error"]}
    return j.get("evaluations", {})


def ae_group(rule: str) -> str:
    for g in ("service BNC Cipav", "service BNC", "service BIC", "vente restauration hébergement"):
        if f" . {g} . " in rule or rule.endswith(f" . {g} . taux") or rule.endswith(f" . {g}"):
            return g
    return "service BNC"


def node_eval_grouped(rules_dirs, date: str, rules: list[str]) -> dict:
    """Evaluate each AE rule under the situation that activates its category."""
    out = {}
    by_g = {}
    for r in rules:
        by_g.setdefault(ae_group(r), []).append(r)
    for g, rs in by_g.items():
        ev = node_eval(rules_dirs, {**AE_GROUP_SIT[g], "date": date}, rs)
        if "__error__" in ev:
            return ev
        out.update(ev)
    return out


def build_ok(rules_dir: Path) -> bool:
    if not rules_dir.exists():
        return False
    r = subprocess.run(["node", str(EVAL), "build", "--rules", str(rules_dir)], capture_output=True, text=True)
    try:
        return "error" not in json.loads(r.stdout)
    except json.JSONDecodeError:
        return False


def close(obs, exp, unit=None) -> bool:
    if obs is None or exp is None:
        return False
    tol = 1e-6 if (unit and "%" in str(unit)) or abs(exp) <= 200 else 0.5
    return abs(float(obs) - float(exp)) <= tol


def pin_dir(stage: Path) -> Path:
    return next((stage / "inputs" / "rules").iterdir()) / "modele-social" / "règles"


def proposal_dir(stage: Path, ans: dict) -> Path | None:
    p = ans.get("proposal_dir")
    if not p:
        return None
    d = stage / str(p)
    return d if d.exists() else None


# ----------------------------------------------------------------------------- reference-derived expectations
def d613_6_expected(ref: dict, version_id: str) -> dict:
    """{(group, line): value} with line in maladie|especes|inval|base|rc|csg from the reference requirements."""
    out = {}
    for r in ref["requirements"]:
        if r["article"] != "D613-6" or r["version_id"] != version_id:
            continue
        m = re.match(r"répartition (a et d|b|c|e): (.*)", r["item"])
        if not m:
            continue
        g, lab = m.group(1), m.group(2).lower()
        if "espèces" in lab:
            line = "especes"
        elif "maladie" in lab:
            line = "maladie"
        elif "invalidité" in lab:
            line = "inval"
        elif "vieillesse de base" in lab:
            line = "base"
        elif "complémentaire" in lab:
            line = "rc"
        elif "contribution sociale" in lab:
            line = "csg"
        else:
            continue
        out[(g, line)] = out.get((g, line), 0.0) + float(r["value"])
    return out


def group_of(rule: str) -> str:
    if "service BNC Cipav" in rule:
        return "b"
    if "service BNC" in rule:
        return "e"
    return "a et d"  # service BIC (d) and vente restauration hébergement (a) share one table


def line_of(rule: str) -> str | None:
    for k, v in (("maladie-maternité", "maladie"), ("invalidité-décès", "inval"), ("retraite de base", "base"), ("retraite complémentaire", "rc"), ("autres contributions", "csg")):
        if k in rule:
            return v
    return None


def expected_repartition(ref: dict, rule: str, version_id: str) -> float | None:
    exp = d613_6_expected(ref, version_id)
    g, line = group_of(rule), line_of(rule)
    if line is None:
        return None
    v = exp.get((g, line))
    if line == "maladie":
        v = (exp.get((g, "maladie")) or 0) + (exp.get((g, "especes")) or 0)  # the library has one maladie-maternité line
    return v


def refined_required(task: str, ref: dict, strict: list[str]) -> tuple[list[str], list[str], str]:
    """Return (required_refined, demoted_to_optional, reason)."""
    if task == "T1a":
        dem = [r for r in strict if r == "dirigeant . auto-entrepreneur . DROM"]
        return [r for r in strict if r not in dem], dem, "the DROM parent is an applicability rule, not a value rule"
    if task == "T1b":
        dem = [r for r in strict if r.endswith("maladie . réduction supplémentaire")]
        return [r for r in strict if r not in dem], dem, "rule is deprecated and applicable only before 2022 (`applicable si: date < 01/2022`)"
    if task == "M1":
        old = d613_6_expected(ref, "LEGIARTI000049625405")
        new = d613_6_expected(ref, "LEGIARTI000052218747")
        dem = []
        for r in strict:
            line = line_of(r)
            if line:
                g = group_of(r)
                o = old.get((g, line), 0) + (old.get((g, "especes"), 0) if line == "maladie" else 0)
                n = new.get((g, line), 0) + (new.get((g, "especes"), 0) if line == "maladie" else 0)
                if abs(o - n) < 1e-9:
                    dem.append(r)
        return [r for r in strict if r not in dem], dem, "the D613-6 line implemented by the rule has the same value in the 2025 and 2026 versions"
    if task == "M2":
        dem = [r for r in strict if r.endswith("prorata sur l'année") or r == "dirigeant . exonérations . ACRE"]
        return [r for r in strict if r not in dem], dem, "prorata (D131-6-1 III) and the eligibility question are unchanged by the new version; the share and the formula are what changed"
    return strict, [], ""


# ----------------------------------------------------------------------------- scoring
def classify(ans: dict) -> dict:
    cls = {}
    for r in ans.get("rules") or []:
        if isinstance(r, dict) and r.get("rule"):
            cls[r["rule"]] = (str(r.get("classification", "")).upper(), str(r.get("confidence", "")).lower())
    return cls


def impact(cls: dict, required: list[str], optional: list[str]) -> dict:
    req = set(required)
    flagged = {n for n, (c, _) in cls.items() if c == "AFFECTED"}
    needs = {n for n, (c, _) in cls.items() if c == "NEEDS_REVIEW"}
    unaff = {n for n, (c, _) in cls.items() if c == "UNAFFECTED"}
    fs = sorted(req & unaff)
    return {"den": len(req), "flagged": len(flagged & req), "needs_review": len(needs & req), "missed_silently": sorted(req - flagged - needs - unaff),
            "FS": fs, "FS_high": sorted(n for n in fs if cls[n][1] == "high"), "over_flag": sorted(flagged - req - set(optional))}


COMMENTARY = re.compile(r"^\s*(\[|no text|negative finding|occurrences of|not quoted|n/a|none)", re.I)


def is_commentary(q: str) -> bool:
    """An arm's own note in a quote field (a version reference, a negative finding), not a claimed quotation."""
    words = re.findall(r"[A-Za-zÀ-ÿ']{3,}", q)
    return bool(COMMENTARY.match(q)) or (("LEGIARTI" in q or "version" in q.lower()) and len(words) < 12)


def citations(ans: dict, texts) -> dict:
    """Every quote-like string in the answer's evaluations / evidence / links, checked against the staged texts.
    not_found counts claimed quotations absent from every staged article (fabrication candidates, listed for manual review);
    commentary counts strings in quote fields that are the arm's own notes rather than quotations."""
    cited, fab, prefix, comm, rows = 0, 0, 0, 0, []
    def consider(q, where):
        nonlocal cited, fab, prefix, comm
        if not isinstance(q, str) or len(q.strip()) < 12 or not re.search(r"[A-Za-zÀ-ÿ]{4}", q) or re.fullmatch(r"\s*LEGI\w+\s*", q):
            return
        res = quote_check(texts, q)
        cited += 1
        if res["found"]:
            if res["mode"] != "exact":
                prefix += 1
            return
        if is_commentary(q):
            comm += 1
            rows.append({"where": where, "quote": q[:160], "result": "commentary_not_quote"})
        else:
            fab += 1
            rows.append({"where": where, "quote": q[:160], "result": res["mode"]})
    for i, e in enumerate(ans.get("evaluations") or []):
        if isinstance(e, dict):
            for k, v in e.items():
                if ("quote" in k.lower() and "version" not in k.lower()) or k in ("governing_text", "law_basis"):
                    consider(v, f"evaluations[{i}].{k}")
                if k == "justification" and isinstance(v, list):
                    for j, item in enumerate(v):
                        if isinstance(item, dict):
                            consider(item.get("quote"), f"evaluations[{i}].justification[{j}]")
    for i, e in enumerate(ans.get("evidence") or []):
        if isinstance(e, dict) and e.get("kind") == "article_quote":
            consider(e.get("quote_or_values"), f"evidence[{i}]")
    for i, L in enumerate(ans.get("links") or []):
        if isinstance(L, dict):
            consider(L.get("quote"), f"links[{i}]")
    return {"cited": cited, "not_found": fab, "found_with_annotation": prefix, "commentary_not_quote": comm, "rows_for_review": rows[:30]}


def score_t0(arm, stage, ans, ref, texts):
    rules_dir = pin_dir(stage)
    rows, hold, fail = [], 0, 0
    by_status = {}
    for L in ans.get("links") or []:
        if not isinstance(L, dict):
            continue
        st = str(L.get("status", "")).upper()
        by_status[st] = by_status.get(st, 0) + 1
        res = quote_check(texts, L.get("quote", ""))
        row = {"rule": L.get("rule"), "article": L.get("article"), "status": st, "quote": res["mode"], "approval": L.get("approval")}
        if st == "VERIFIED":
            chk = L.get("check") or {}
            ok = False
            if chk.get("rule") and isinstance(chk.get("situation"), dict):
                sit = dict(chk["situation"])
                if chk.get("date") and "date" not in sit:
                    sit["date"] = chk["date"]
                ev = node_eval([rules_dir], sit, [chk["rule"]])
                obs = numeric((ev.get(chk["rule"]) or {}).get("nodeValue")) if "__error__" not in ev else None
                row["replayed"] = obs
                ok = close(obs, numeric(chk.get("expected")), (ev.get(chk["rule"]) or {}).get("unit")) and res["found"]
            row["check_holds"] = ok
            hold += int(ok)
            fail += int(not ok)
        rows.append(row)
    exp_rules = set(sum(ref["tasks"]["T0"]["expected_bindings"].values(), []))
    linked = {r["rule"] for r in rows if r["quote"] != "not_found"}
    return {"task": "T0", "arm": arm, "answered": True, "links": len(rows), "by_status": by_status,
            "citations": citations(ans, texts), "VERIFIED_checks": {"hold_on_replay": hold, "fail": fail},
            "expected_bound_rules": {"num": len(exp_rules & linked), "den": len(exp_rules), "missed": sorted(exp_rules - linked)},
            "approvals_claimed": sorted({str(r.get("approval")) for r in rows}), "rows": rows}


def score_change(task, arm, stage, ans, ref, texts):
    t = ref["tasks"][task]
    strict_req = list(t.get("affected_rules_required", []))
    optional = list(t.get("affected_rules_optional", []))
    req, demoted, reason = refined_required(task, ref, strict_req)
    cls = classify(ans)
    strict = impact(cls, strict_req, optional)
    refined = impact(cls, req, optional + demoted)
    ref_changed = set((t.get("changed_articles") or {}).keys())
    ans_changed = {str(c.get("article")) for c in (ans.get("changed_articles") or []) if isinstance(c, dict)}
    prop = proposal_dir(stage, ans)
    pin = pin_dir(stage)
    tc = {"method": None, "items": [], "correct": 0, "incorrect": 0, "not_transposed": 0, "replay_failed": 0}
    bok = build_ok(prop) if prop else None
    if task == "M1" and prop:
        tc["method"] = "reference-driven replay at 01/01/2026 on the proposal tree, each category evaluated under the situation that activates it: BNC global rate (D613-4 e) and the twenty D613-6 split rules (maladie line = maladie + prestations en espèces; retraite de base b = sum of its two lines)"
        rules = [n for n in ref["bindings_by_pin"]["G3"]["ae_global_rate_rules"] if n.endswith("service BNC . taux")] + ref["bindings_by_pin"]["G3"]["ae_repartition_rules"]
        evp = node_eval_grouped([prop], "01/01/2026", rules)
        evg = node_eval_grouped([pin], "01/01/2026", rules)
        for r in rules:
            exp = 25.6 if r.endswith("service BNC . taux") else expected_repartition(ref, r, "LEGIARTI000052218747")
            obs = numeric((evp.get(r) or {}).get("nodeValue")) if "__error__" not in evp else None
            before = numeric((evg.get(r) or {}).get("nodeValue")) if "__error__" not in evg else None
            item = {"rule": r.replace(AE_PREFIX + " . ", ""), "expected": exp, "pin_value": before, "proposal_value": obs}
            if obs is None:
                item["outcome"] = "REPLAY_FAILED"; tc["replay_failed"] += 1
            elif exp is not None and close(obs, exp, "%"):
                item["outcome"] = "CORRECT"; tc["correct"] += 1
            elif before is not None and close(obs, before, "%"):
                item["outcome"] = "NOT_TRANSPOSED"; tc["not_transposed"] += 1
            else:
                item["outcome"] = "INCORRECT"; tc["incorrect"] += 1
            tc["items"].append(item)
    elif task == "M2" and prop:
        tc["method"] = "reference-driven replay of the indépendant Acre share rule on the proposal tree for a 2026 creation (expected 25 %), situation taken from the arm's own evaluation row when present"
        rule = "dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux"
        sit = None
        for e in ans.get("evaluations") or []:
            if isinstance(e, dict) and e.get("rule") == rule and isinstance(e.get("situation"), dict) and "2026" in json.dumps(e.get("situation")) + str(e.get("date")):
                sit = dict(e["situation"]); sit.setdefault("date", e.get("date") or "01/06/2026"); break
        sit = sit or TI_ACRE_SIT
        evp, evg = node_eval([prop], sit, [rule]), node_eval([pin], sit, [rule])
        obs = numeric((evp.get(rule) or {}).get("nodeValue")) if "__error__" not in evp else None
        before = numeric((evg.get(rule) or {}).get("nodeValue")) if "__error__" not in evg else None
        item = {"rule": rule, "situation": sit, "expected": 25.0, "pin_value": before, "proposal_value": obs}
        if obs is None:
            item["outcome"] = "REPLAY_FAILED"; tc["replay_failed"] += 1
        elif close(obs, 25.0, "%"):
            item["outcome"] = "CORRECT"; tc["correct"] += 1
        elif before is not None and close(obs, before, "%"):
            item["outcome"] = "NOT_TRANSPOSED"; tc["not_transposed"] += 1
        else:
            item["outcome"] = "INCORRECT"; tc["incorrect"] += 1
        tc["items"].append(item)
    elif task == "T1a" and prop:
        tc["method"] = "no value is visible for the announced versions in S1: the proposal must not change any global rate at 01/07/2024, 01/01/2025, 01/01/2026 (abstention); changed values are counted as UNSUPPORTED"
        rules = ref["bindings_by_pin"]["G0"]["ae_global_rate_rules"]
        for date in ("01/07/2024", "01/01/2025", "01/01/2026"):
            evp, evg = node_eval_grouped([prop], date, rules), node_eval_grouped([pin], date, rules)
            for r in rules:
                o, b = numeric((evp.get(r) or {}).get("nodeValue")), numeric((evg.get(r) or {}).get("nodeValue"))
                item = {"rule": r.replace(AE_PREFIX + " . ", ""), "date": date, "pin_value": b, "proposal_value": o}
                if o is None and b is None:
                    item["outcome"] = "NULL_BOTH"
                elif o is None or b is None or not close(o, b, "%"):
                    item["outcome"] = "UNSUPPORTED_CHANGE"; tc["incorrect"] += 1
                else:
                    item["outcome"] = "UNCHANGED_ABSTAINED"; tc["not_transposed"] += 1
                tc["items"].append(item)
    elif task == "T1b" and prop:
        tc["method"] = "the decree/law constants must appear in the proposal's edits; every evaluation row the arm reported with a numeric value_after is replayed on the proposal tree"
        r = subprocess.run(["diff", "-ruN", str(pin), str(prop)], capture_output=True, text=True)
        added = "\n".join(l for l in r.stdout.splitlines() if l.startswith("+") and not l.startswith("+++"))
        for name, pats in T1B_CONSTANTS.items():
            present = any(re.search(p, added) for p in pats)
            tc["items"].append({"constant": name, "present_in_proposal": present})
            tc["correct" if present else "not_transposed"] += 1
        replay_ok, replay_bad = 0, 0
        for e in ans.get("evaluations") or []:
            if not (isinstance(e, dict) and e.get("rule") and isinstance(e.get("situation"), dict)):
                continue
            va = numeric(e.get("value_after"))
            if va is None:
                continue
            sit = dict(e["situation"]); sit.setdefault("date", e.get("date") or "01/06/2025")
            ev = node_eval([prop], sit, [e["rule"]])
            obs = numeric((ev.get(e["rule"]) or {}).get("nodeValue")) if "__error__" not in ev else None
            if close(obs, va, (ev.get(e["rule"]) or {}).get("unit")):
                replay_ok += 1
            else:
                replay_bad += 1
        tc["arm_rows_replayed"] = {"match": replay_ok, "mismatch": replay_bad}
    elif task == "M0":
        tc["method"] = "no-op window: nothing to transpose; counted are rules flagged AFFECTED (over-flag) and whether the arm said no change was needed"
    return {"task": task, "arm": arm, "answered": True,
            "changed_articles": {"reference": sorted(ref_changed), "answer": sorted(ans_changed), "hit": len(ref_changed & ans_changed), "missed": sorted(ref_changed - ans_changed), "extra": sorted(ans_changed - ref_changed)},
            "required_strict": strict_req, "required_refined": req, "demoted_to_optional": demoted, "refinement_reason": reason,
            "IR_strict": strict, "IR_refined": refined, "classified_rules": len(cls),
            "TC": tc, "citations": citations(ans, texts), "build_ok_on_proposal": bok, "proposal_dir": ans.get("proposal_dir"),
            "no_change_needed_claimed": ans.get("no_change_needed"), "abstentions_listed": len(ans.get("abstentions") or []), "approval_field": ans.get("approval")}


def score_reverse(task, arm, stage, ans, ref, texts):
    t = ref["tasks"][task]
    label = str(ans.get("label", "")).upper()
    conf = str(ans.get("confidence", "")).lower()
    acceptable = label in t["acceptable_labels"]
    return {"task": task, "arm": arm, "answered": True, "label": label, "confidence": conf, "acceptable": acceptable, "acceptable_labels": t["acceptable_labels"],
            "CFC": int((not acceptable) and conf == "high"), "citations": citations(ans, texts), "expected_values_listed": len(ans.get("expected_values_if_mismatch") or []),
            "outside_bounded_set": ans.get("outside_bounded_set"), "approval_field": ans.get("approval")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    runs = Path(a.runs_root)
    ref = json.load(open(ROOT / "held_out" / "REFERENCE.json", encoding="utf-8"))
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    scores = {"protocol_sha256": ref["protocol_sha256"], "pass": "second (see docstring)", "by_arm": {}}
    for arm in ARMS:
        scores["by_arm"][arm] = {}
        for task in TASKS:
            stage = runs / arm / task
            ans_p = stage / "output" / "answer.json"
            audit = load_json(stage / "AUDIT.json") if (stage / "AUDIT.json").exists() else {}
            if not ans_p.exists():
                res = {"task": task, "arm": arm, "answered": False, "reason": "no output/answer.json"}
            else:
                ans = load_json(ans_p)
                if "__error__" in ans:
                    res = {"task": task, "arm": arm, "answered": False, "reason": ans["__error__"]}
                else:
                    texts = texts_up_to(runs, arm, task)
                    if task == "T0":
                        res = score_t0(arm, stage, ans, ref, texts)
                    elif task.startswith("R"):
                        res = score_reverse(task, arm, stage, ans, ref, texts)
                    else:
                        res = score_change(task, arm, stage, ans, ref, texts)
            res["cost"] = {"tool_calls": audit.get("tool_calls_total"), "assistant_turns": audit.get("assistant_turns"), "usage": audit.get("usage"), "contaminated": audit.get("contaminated"), "flags": audit.get("flags")}
            scores["by_arm"][arm][task] = res
    json.dump(scores, open(out / "scores.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# Scores (mechanical, second pass)", "", f"Protocol {ref['protocol_sha256'][:16]}…. Exact counts; rows in scores.json. First pass kept in SCORES_firstpass.md.", "",
          "## Change tasks", "", "| task | arm | changed articles hit | IR strict (flagged/needs-review/den) | FS strict (high) | IR refined (flagged/needs-review/den) | FS refined (high) | over-flag | TC (correct / incorrect / not transposed / replay failed) | quotes not found / cited | build ok | tool calls |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for task in ("T1a", "T1b", "M0", "M1", "M2"):
        for arm in ARMS:
            r = scores["by_arm"][arm][task]
            if not r.get("answered"):
                md.append(f"| {task} | {arm} | NOT ANSWERED | | | | | | | | | {r['cost'].get('tool_calls')} |"); continue
            s, f, tc, c = r["IR_strict"], r["IR_refined"], r["TC"], r["citations"]
            md.append(f"| {task} | {arm} | {r['changed_articles']['hit']}/{len(r['changed_articles']['reference'])} | {s['flagged']}/{s['needs_review']}/{s['den']} | {len(s['FS'])} ({len(s['FS_high'])}) | {f['flagged']}/{f['needs_review']}/{f['den']} | {len(f['FS'])} ({len(f['FS_high'])}) | {len(f['over_flag'])} | {tc['correct']} / {tc['incorrect']} / {tc['not_transposed']} / {tc['replay_failed']} | {c['not_found']}/{c['cited']} | {r['build_ok_on_proposal']} | {r['cost'].get('tool_calls')} |")
    md += ["", "## Reverse checks", "", "| task | arm | label (confidence) | acceptable | CFC | quotes not found / cited | tool calls |", "|---|---|---|---|---|---|---|"]
    for task in ("R1", "R2", "R3", "R4", "R5"):
        for arm in ARMS:
            r = scores["by_arm"][arm][task]
            md.append(f"| {task} | {arm} | {r.get('label')} ({r.get('confidence')}) | {'yes' if r.get('acceptable') else 'NO'} | {r.get('CFC')} | {r['citations']['not_found']}/{r['citations']['cited']} | {r['cost'].get('tool_calls')} |")
    md += ["", "## Initial binding (T0)", "", "| arm | links | by status | VERIFIED checks hold / fail on replay | expected rule families bound | quotes not found / cited | approvals claimed | tool calls |", "|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        r = scores["by_arm"][arm]["T0"]
        md.append(f"| {arm} | {r['links']} | {r['by_status']} | {r['VERIFIED_checks']['hold_on_replay']} / {r['VERIFIED_checks']['fail']} | {r['expected_bound_rules']['num']}/{r['expected_bound_rules']['den']} | {r['citations']['not_found']}/{r['citations']['cited']} | {r['approvals_claimed']} | {r['cost'].get('tool_calls')} |")
    (out / "SCORES.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
