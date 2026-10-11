#!/usr/bin/env python3
"""Scorer-only reference builder (PROTOCOL.md §5, §9).

Reads the sealed law snapshots and rule pins, extracts every deterministic number the bounded
articles state (rates, thresholds, factors), records in which snapshots each value is *visible*
(legi-data ships only the version in force; future versions are listed by id and date without
text), cross-checks the micro-social rates against OpenFisca-France, derives the per-task
expectations the protocol fixed, and writes held_out/REFERENCE.json and held_out/COVERAGE.json.

It never reads the maintainers' patches. It never reads solver output. Run once, before any
solver run:  python -B src/build_reference.py --out .
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

HERE = Path(__file__).resolve().parent
EVAL = HERE / "publicodes_eval.mjs"

SNAP_ORDER = ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"]
AE_PREFIX = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"
AE_SITUATION = {"salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui",
                "dirigeant . auto-entrepreneur": "oui", "entreprise . activité . nature": "'libérale'", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois"}


def fr(x: str) -> float:
    return float(x.replace(" ", "").replace(" ", "").replace(",", "."))


def load_law(root: Path) -> dict:
    snaps = {}
    for d in sorted((root / "inputs" / "law").iterdir()):
        j = json.load(open(d / "articles.json", encoding="utf-8"))
        snaps[j["snapshot"]] = {"version": j["legi_data_version"], "published": j.get("published"), "dir": str(d.relative_to(root)),
                                "articles": {num: recs[0] for num, recs in j["articles"].items()}}
    return snaps


def parse_d613_4_segments(text: str) -> dict:
    """Return {letter: (global rate, segment text)} from the table text. The last 'x,y %' of each segment is the global rate."""
    segs = re.split(r"(?=\b([a-e])\) Travailleurs? ind)", text)
    out, letter = {}, None
    for s in segs:
        if re.fullmatch(r"[a-e]", s or ""):
            letter = s
            continue
        if letter and s:
            pct = re.findall(r"(\d{1,2},\d) %", s)
            if pct:
                out[letter] = (fr(pct[-1]), s.strip())
            letter = None
    return out


def parse_d613_4(text: str) -> dict:
    return {k: v[0] for k, v in parse_d613_4_segments(text).items()}


def parse_d613_6(text: str) -> dict:
    """Return {group: [(label, pct)]} with groups 'a et d', 'b', 'c', 'e'."""
    out = {}
    parts = re.split(r"-pour les personnes relevant (?:des |du )", text)
    for p in parts[1:]:
        m = re.match(r"([a-e](?: et [a-e])?)\s*:", p)
        if not m:
            continue
        group = m.group(1)
        body = p[m.end():]
        body = re.sub(r"Cotisations et contributions Taux de répartition des montants de cotisations", "", body)
        pairs = re.findall(r"((?:Cotisations? |Contribution )[^%]*?)\s(\d{1,2},\d{2}) %", body)
        out[group] = [(lab.strip(), fr(v)) for lab, v in pairs]
    return out


def roundup_tenth(x: float) -> float:
    return math.ceil(round(x * 10, 9)) / 10


def node_list(rules_dirs: list[str], prefix: str | None = None) -> list[str]:
    cmd = ["node", str(EVAL), "list"]
    for d in rules_dirs:
        cmd += ["--rules", d]
    if prefix:
        cmd += ["--prefix", prefix]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout).get("names", [])


def node_eval(rules_dirs: list[str], situation: dict, rules: list[str]) -> dict:
    cmd = ["node", str(EVAL), "evaluate"]
    for d in rules_dirs:
        cmd += ["--rules", d]
    cmd += ["--situation", json.dumps(situation, ensure_ascii=False)]
    for r in rules:
        cmd += ["--rule", r]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout).get("evaluations", {})


def rule_sets(names: list[str]) -> dict:
    rate_tail = ("taux service BNC", "service BNC . taux", "taux service BIC", "service BIC . taux", "taux vente restauration hébergement",
                 "vente restauration hébergement . taux", "cotisations CIPAV . taux", "service BNC Cipav . taux")
    return {
        "ae_global_rate_rules": sorted(n for n in names if n.startswith(AE_PREFIX) and any(n.endswith(t) for t in rate_tail) and "DROM" not in n and "Acre" not in n and "ACRE" not in n),
        "ae_repartition_rules": sorted(n for n in names if n.startswith(AE_PREFIX) and " . répartition . " in n and n.endswith("taux de répartition")),
        "ae_drom_rules": sorted(n for n in names if n.startswith("dirigeant . auto-entrepreneur . DROM")),
        "ae_acre_rules": sorted(n for n in names if (n.startswith("dirigeant . auto-entrepreneur . Acre") or (n.startswith(AE_PREFIX) and "taux ACRE" in n))),
        "indep_acre_rules": sorted(n for n in names if n.startswith("dirigeant . indépendant . cotisations et contributions . exonérations . ACRE") or n == "dirigeant . exonérations . ACRE"),
        "indep_assiette_rules": sorted(n for n in names if n.startswith("dirigeant . indépendant . cotisations et contributions") and "assiette" in n and "minimale" not in n and "forfaitaire" not in n),
        "indep_maladie_rules": sorted(n for n in names if n.startswith("dirigeant . indépendant . cotisations et contributions . maladie")),
        "indep_retraite_base_rules": sorted(n for n in names if n.startswith("dirigeant . indépendant . cotisations et contributions . retraite de base")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    root = Path(a.out).resolve()
    protocol_sha = (root / "PROTOCOL.sha256").read_text().split()[0]
    law = load_law(root)
    pins = {}
    for d in sorted((root / "inputs" / "rules").iterdir()):
        meta = json.load(open(d / "meta.json", encoding="utf-8"))
        gid = d.name.split("_")[0]
        pins[gid] = {"dir": str(d.relative_to(root)), "rules_dirs": [str(d / "modele-social" / "règles")], **meta}

    requirements = []

    def add(req):
        req["req_id"] = f"REQ{len(requirements) + 1:03d}"
        requirements.append(req)

    # ---------------- D613-4 global rates, per snapshot version
    seen = set()
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("D613-4")
        if not art:
            continue
        rows = parse_d613_4_segments(art["text"])
        key = art["id"]
        if key in seen:
            continue
        seen.add(key)
        visible = [s for s in SNAP_ORDER if law[s]["articles"].get("D613-4", {}).get("id") == key]
        for letter, (rate, seg) in rows.items():
            add({"article": "D613-4", "version_id": key, "etat": art["etat"], "in_force_from": ms(art["dateDebut"]), "in_force_to": ms(art["dateFin"]),
                 "item": f"global rate, category {letter}", "value": rate, "unit": "%", "visible_in_snapshots": visible,
                 "quote": seg[-80:], "status": "DETERMINISTIC"})
    # future versions announced without text (the abstention cases)
    for sid in ("S1", "S2"):
        art = law[sid]["articles"]["D613-4"]
        for v in art.get("articleVersions", []):
            if v.get("etat") == "VIGUEUR_DIFF":
                add({"article": "D613-4", "version_id": v["id"], "etat": "VIGUEUR_DIFF (announced, text not in snapshot)", "in_force_from": ms(v["dateDebut"]), "in_force_to": ms(v["dateFin"]),
                     "item": f"announced future version visible in {sid} by id and date only", "value": None, "unit": None, "visible_in_snapshots": [], "status": "TEXT_NOT_IN_CORPUS_AT_DATE"})
        break

    # ---------------- D613-6 répartition, per version
    seen = set()
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("D613-6")
        if not art or art["id"] in seen:
            continue
        seen.add(art["id"])
        visible = [s for s in SNAP_ORDER if law[s]["articles"].get("D613-6", {}).get("id") == art["id"]]
        groups = parse_d613_6(art["text"])
        for g, pairs in groups.items():
            for lab, v in pairs:
                add({"article": "D613-6", "version_id": art["id"], "etat": art["etat"], "in_force_from": ms(art["dateDebut"]), "in_force_to": ms(art["dateFin"]),
                     "item": f"répartition {g}: {lab}", "value": v, "unit": "%", "visible_in_snapshots": visible, "status": "DETERMINISTIC",
                     "note": "the rule library has one 'maladie-maternité' line; where the law splits maladie-maternité and prestations en espèces, the model line is scored against their sum (INFERRED mapping)"})

    # ---------------- D136-5, L136-3, D621-2, D633-3, D131-6-1
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("D136-5")
        if art:
            vis = [s for s in SNAP_ORDER if law[s]["articles"].get("D136-5", {}).get("id") == art["id"]]
            p, c = re.findall(r"(\d+(?:,\d+)?) %", art["text"])[:2]
            add({"article": "D136-5", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "abattement floor, % of annual PASS", "value": fr(p), "unit": "% PASS", "visible_in_snapshots": vis, "status": "DETERMINISTIC", "quote": "fixé à 1,76 % de la valeur annuelle du plafond"})
            add({"article": "D136-5", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "abattement ceiling, % of annual PASS", "value": fr(c), "unit": "% PASS", "visible_in_snapshots": vis, "status": "DETERMINISTIC", "quote": "fixé à 130 % de la valeur annuelle du plafond"})
            break
    seenL = set()
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("L136-3")
        if art and art["id"] not in seenL:
            seenL.add(art["id"])
            vis = [s for s in SNAP_ORDER if law[s]["articles"].get("L136-3", {}).get("id") == art["id"]]
            m = re.search(r"abattement de (\d+) %", art["text"])
            add({"article": "L136-3", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "III: flat abattement on the base", "value": fr(m.group(1)) if m else None, "unit": "%", "visible_in_snapshots": vis, "status": "DETERMINISTIC" if m else "UNRESOLVED", "quote": m.group(0) if m else None})
    seenM = set()
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("D621-2")
        if art and art["id"] not in seenM:
            seenM.add(art["id"])
            vis = [s for s in SNAP_ORDER if law[s]["articles"].get("D621-2", {}).get("id") == art["id"]]
            for t, v in re.findall(r"T(\d) est égal à (\d+(?:,\d+)?) %", art["text"]):
                add({"article": "D621-2", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": f"maladie reduced-rate constant T{t}", "value": fr(v), "unit": "%", "visible_in_snapshots": vis, "status": "DETERMINISTIC", "quote": f"T{t} est égal à {v} %"})
            thr = sorted({fr(x) for x in re.findall(r"(\d+) % de la valeur annuelle du plafond", art["text"])})
            add({"article": "D621-2", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "maladie reduced-rate thresholds (% PASS)", "value": thr, "unit": "% PASS", "visible_in_snapshots": vis, "status": "DETERMINISTIC"})
    seenR = set()
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("D633-3")
        if art and art["id"] not in seenR:
            seenR.add(art["id"])
            vis = [s for s in SNAP_ORDER if law[s]["articles"].get("D633-3", {}).get("id") == art["id"]]
            pct = re.findall(r"(\d+,\d+) %", art["text"])
            if len(pct) >= 2:
                add({"article": "D633-3", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "retraite de base rate within PASS", "value": fr(pct[0]), "unit": "%", "visible_in_snapshots": vis, "status": "DETERMINISTIC"})
                add({"article": "D633-3", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "retraite de base rate on the whole base", "value": fr(pct[1]), "unit": "%", "visible_in_snapshots": vis, "status": "DETERMINISTIC"})
    seenA = set()
    for sid in SNAP_ORDER:
        art = law[sid]["articles"].get("D131-6-1")
        if art and art["id"] not in seenA:
            seenA.add(art["id"])
            vis = [s for s in SNAP_ORDER if law[s]["articles"].get("D131-6-1", {}).get("id") == art["id"]]
            factor = 0.25 if "quart du montant total" in art["text"] else (1.0 if "correspond au montant total" in art["text"] else None)
            add({"article": "D131-6-1", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": "Acre exemption share of contributions when income <= 3/4 PASS", "value": factor, "unit": "fraction", "visible_in_snapshots": vis, "status": "DETERMINISTIC" if factor is not None else "UNRESOLVED",
                 "quote": "correspond au quart du montant total des cotisations" if factor == 0.25 else "correspond au montant total des cotisations"})
    # ---------------- D756-5 fractions and derived DROM rates (fraction assignment per category is UNRESOLVED: L611-1 is outside the set)
    art = law["S5"]["articles"]["D756-5"]
    base = parse_d613_4(law["S5"]["articles"]["D613-4"]["text"])
    base0 = parse_d613_4(law["S0"]["articles"]["D613-4"]["text"])
    for letter in "abde":
        for period, frac_ad, frac_other in (("1", 1 / 6, 1 / 3), ("2", 1 / 2, 1 / 2), ("3", 2 / 3, 2 / 3)):
            f = frac_ad if letter in "ad" else frac_other
            add({"article": "D756-5", "version_id": art["id"], "in_force_from": ms(art["dateDebut"]), "item": f"DROM rate category {letter}, period {period}: roundup_tenth(fraction x D613-4 rate)",
                 "value": roundup_tenth(f * base[letter]), "value_from_pre_2024_07_base": roundup_tenth(f * base0[letter]), "fraction": round(f, 6), "base_rate_S5": base[letter], "base_rate_S0": base0[letter],
                 "unit": "%", "visible_in_snapshots": ["S3", "S4", "S5"], "status": "UNRESOLVED_FRACTION_ASSIGNMENT" if letter in "be" else "DETERMINISTIC",
                 "note": "D756-5 assigns 1/6 to '2° de l'article L. 611-1' and 1/3 to other cases for period 1; L611-1 is outside the bounded set, so which categories take 1/6 is UNRESOLVED. The direction of change on 2024-07-01 (base 21,1→23,1 for e; 21,2→23,2 for b) is not ambiguous."})

    # ---------------- OpenFisca cross-check
    oracle = {}
    if yaml:
        for f, cat in (("service.yaml", "e"), ("cipav.yaml", "b"), ("vente.yaml", "a"), ("service_bic.yaml", "d")):
            p = root / "held_out" / "oracle" / f
            if p.exists():
                y = yaml.safe_load(p.read_text(encoding="utf-8"))
                oracle[cat] = {d: v.get("value") for d, v in (y.get("values") or {}).items()}
    checks = []
    for r in requirements:
        if r["article"] == "D613-4" and r.get("value") is not None:
            cat = r["item"][-1]
            vals = oracle.get(cat, {})
            d = r["in_force_from"]
            ov = None
            for k in sorted(vals):
                if str(k) <= d:
                    ov = vals[k]
            if ov is not None:
                agree = abs(ov * 100 - r["value"]) < 1e-6
                r["openfisca_value_pct"] = round(ov * 100, 4)
                r["openfisca_agrees"] = agree
                checks.append((r["req_id"], agree))
                if not agree:
                    r["status"] = "UNRESOLVED"

    # ---------------- bindings per pin (names), and pre-change values at the pin
    bindings = {}
    for gid, p in pins.items():
        names = node_list(p["rules_dirs"])
        sets = rule_sets(names)
        vals = {}
        for date in ("01/05/2024", "01/07/2024", "01/01/2025", "01/01/2026"):
            ev = node_eval(p["rules_dirs"], {**AE_SITUATION, "date": date}, sets["ae_global_rate_rules"])
            vals[date] = {k: v.get("nodeValue") for k, v in ev.items()}
        bindings[gid] = {"commit": p["commit"], "committed": p["committed"], **sets, "ae_global_rate_values_at_pin": vals}

    # ---------------- per-task expectations (fixed by PROTOCOL §3, §5)
    def changed(s_from, s_to):
        out = {}
        for num in set(law[s_from]["articles"]) | set(law[s_to]["articles"]):
            a1, a2 = law[s_from]["articles"].get(num), law[s_to]["articles"].get(num)
            if (a1 or {}).get("id") != (a2 or {}).get("id") or (a1 or {}).get("text_sha256") != (a2 or {}).get("text_sha256"):
                out[num] = {"from": (a1 or {}).get("id"), "to": (a2 or {}).get("id"), "to_in_force": ms((a2 or {}).get("dateDebut"))}
        return out

    tasks = {
        "T0": {"law": "S0", "rules": "G0", "expected_bindings": {"ae_global_rate_rules -> D613-4 rows (a vente 12,3; b Cipav 21,2; d BIC 21,2; e BNC 21,1)": bindings["G0"]["ae_global_rate_rules"],
                                                                 "ae_drom_rules -> D756-5": bindings["G0"]["ae_drom_rules"], "ae_acre_rules -> D131-6-1 (AE Acre share is governed outside the set: PARTIALLY)": bindings["G0"]["ae_acre_rules"]},
               "approval_truth": "none recorded anywhere"},
        "T1a": {"law": "S1", "rules": "G0", "changed_articles": changed("S0", "S1"),
                "affected_rules_required": bindings["G0"]["ae_global_rate_rules"] + bindings["G0"]["ae_drom_rules"],
                "affected_rules_optional": bindings["G0"]["ae_acre_rules"],
                "values_visible_in_S1": False, "expected_behaviour": "flag affected rules; ABSTAIN on the new numeric values (new versions are announced by id and date only; their text is not in S1). Any concrete new rate written at T1a is not supported by the sealed corpus.",
                "new_rates_truth_for_scorer_only": {"2024-07-01": {"e": 23.1, "b": 23.2, "a": 12.3, "d": 21.2}, "2025-01-01": {"e": 24.6}, "2026-01-01 (as decreed in 2024, later changed)": {"e": 26.1}}},
        "T1b": {"law": "S3", "rules": "G1", "changed_articles": changed("S2", "S3"),
                "affected_rules_required": bindings["G1"]["indep_assiette_rules"] + bindings["G1"]["indep_maladie_rules"] + bindings["G1"]["indep_retraite_base_rules"],
                "scored_values": {"L136-3 III abattement %": 26, "D136-5 floor % PASS": 1.76, "D136-5 ceiling % PASS": 130, "D621-2 T1 %": 1.5, "D621-2 T2 %": 4, "D633-3 within PASS %": 17.15, "D633-3 whole base %": 0.72, "applicability": "contributions due for periods from 2025-01-01 (D136-5/D621-2/D633-3 in force 2024-07-07; L136-3 in force 2023-12-28)"},
                "note": "T1b is scored on these constants and on explicit abstention; the full reformed base is PARTIALLY_OBSERVABLE."},
        "R1": {"acceptable_labels": ["HARMLESS_REFACTOR"], "wrong_high_confidence": ["MISMATCH"]},
        "R2": {"acceptable_labels": ["HARMLESS_REFACTOR"], "wrong_high_confidence": ["MISMATCH"]},
        "R3": {"acceptable_labels": ["MISMATCH", "UNRESOLVED"], "wrong_high_confidence": ["HARMLESS_REFACTOR", "LEGITIMATE_INDEPENDENT_CHANGE"],
               "material_finding": "post-fix DROM BNC and Cipav values derive from the pre-2024-07-01 base rates (21,1 / 21,2) while D613-4 in force since 2024-07-01 gives 23,1 / 23,2; BIC and vente bases unchanged", "derived_values": [r for r in requirements if r["article"] == "D756-5"]},
        "R4": {"acceptable_labels": ["LEGITIMATE_INDEPENDENT_CHANGE", "UNRESOLVED"], "wrong_high_confidence": ["HARMLESS_REFACTOR", "MISMATCH"]},
        "R5": {"acceptable_labels": ["LEGITIMATE_INDEPENDENT_CHANGE", "UNRESOLVED"], "wrong_high_confidence": ["HARMLESS_REFACTOR", "MISMATCH"]},
        "M0": {"law": ["S6", "S7"], "rules": "G3", "changed_articles": changed("S6", "S7"), "affected_rules_required": [], "expected_behaviour": "nothing changed in the bounded set; no rule to reassess"},
        "M1": {"law": ["S7", "S8"], "rules": "G3", "changed_articles": changed("S7", "S8"),
               "affected_rules_required": [n for n in bindings["G3"]["ae_global_rate_rules"] if "BNC" in n and "Cipav" not in n] + bindings["G3"]["ae_repartition_rules"],
               "affected_rules_optional": [n for n in bindings["G3"]["ae_global_rate_rules"] if not ("BNC" in n and "Cipav" not in n)] + bindings["G3"]["ae_drom_rules"],
               "scored_values_2026_01_01": {"D613-4 e (BNC) global rate": parse_d613_4(law["S8"]["articles"]["D613-4"]["text"]).get("e"),
                                            "D613-4 a/b/d unchanged": {k: v for k, v in parse_d613_4(law["S8"]["articles"]["D613-4"]["text"]).items() if k != "e"},
                                            "D613-6 répartition": parse_d613_6(law["S8"]["articles"]["D613-6"]["text"])}},
        "M2": {"law": ["S8", "S9"], "rules": "G4", "changed_articles": changed("S8", "S9"),
               "affected_rules_required": bindings["G4"]["indep_acre_rules"], "affected_rules_optional": bindings["G4"]["ae_acre_rules"],
               "scored_values": {"D131-6-1 share when income <= 3/4 PASS": 0.25, "previous share": 1.0, "article dateDebut": ms(law["S9"]["articles"]["D131-6-1"]["dateDebut"]), "decree per LEGI link": [m.get("textTitle") for m in law["S9"]["articles"]["D131-6-1"].get("lienModifications", [])]}},
    }
    N = len(requirements)
    t4_index = int(protocol_sha[:8], 16) % N
    ref = {"protocol_sha256": protocol_sha, "built_at_note": "built from inputs/law and inputs/rules only; no maintainer patch and no solver output was read",
           "requirement_count": N, "t4_question1_requirement": requirements[t4_index]["req_id"], "t4_question1_index": t4_index,
           "openfisca_checks": {"count": len(checks), "agree": sum(1 for _, ok in checks if ok), "disagree": [r for r, ok in checks if not ok]},
           "requirements": requirements, "bindings_by_pin": bindings, "tasks": tasks}
    out = root / "held_out" / "REFERENCE.json"
    json.dump(ref, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------------- coverage (PROTOCOL §9): mechanical where a rule value equals the stated number at some pin
    cov = []
    for r in requirements:
        if r.get("value") is None or not isinstance(r["value"], (int, float)):
            cov.append({"req_id": r["req_id"], "article": r["article"], "item": r["item"], "classification": "NOT_OBSERVABLE" if r["article"] in ("D621-2",) else "PARTIALLY_OBSERVABLE", "reason": "formula, list or factor; no single rule value to match"})
            continue
        hit = None
        for gid, b in bindings.items():
            for date, vals in b["ae_global_rate_values_at_pin"].items():
                for name, v in vals.items():
                    if isinstance(v, (int, float)) and abs(v - r["value"]) < 1e-9 and r["article"] in ("D613-4", "D756-5"):
                        hit = (gid, date, name)
        if r["article"] == "D613-4" and hit:
            cls, reason = "FULLY_OBSERVABLE", f"rule {hit[2]} evaluates to the stated value at pin {hit[0]} ({hit[1]})"
        elif r["article"] in ("D613-4", "D613-6", "D756-5"):
            cls, reason = "FULLY_OBSERVABLE", "a bounded auto-entrepreneur rate/répartition/DROM rule implements this family (value differs at the pins because the law version differs)"
        elif r["article"] in ("D136-5", "L136-3", "D633-3", "D131-6-1"):
            cls, reason = "PARTIALLY_OBSERVABLE", "implemented by indépendant rules whose effect is not isolable by a single evaluation at the pins (base reform not yet implemented at G1/G3)"
        else:
            cls, reason = "NOT_OBSERVABLE", "no bounded rule implements it"
        cov.append({"req_id": r["req_id"], "article": r["article"], "item": r["item"], "value": r["value"], "classification": cls, "reason": reason})
    counts = {}
    for c in cov:
        counts[c["classification"]] = counts.get(c["classification"], 0) + 1
    json.dump({"protocol_sha256": protocol_sha, "counts": counts, "items": cov}, open(root / "held_out" / "COVERAGE.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"requirements": N, "t4_question1": requirements[t4_index]["req_id"] + " / " + requirements[t4_index]["item"], "openfisca_checks": ref["openfisca_checks"], "coverage": counts,
                      "M1_required": len(tasks["M1"]["affected_rules_required"]), "M2_required": len(tasks["M2"]["affected_rules_required"]), "T1a_required": len(tasks["T1a"]["affected_rules_required"]), "T1b_required": len(tasks["T1b"]["affected_rules_required"])}, ensure_ascii=False, indent=1))


def ms(x):
    if x is None:
        return None
    try:
        import datetime as dt
        return dt.datetime.fromtimestamp(int(x) / 1000, dt.timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


if __name__ == "__main__":
    main()
