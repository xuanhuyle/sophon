"""Builds output/answer.json and output/NOTES.md for M1 from the eval jsonl, link results and report files. usage: gen_answer_M1.py <self_calls>"""
import json, os, sys, glob
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else None
def load(f):
    out = {}
    for line in open(f, encoding='utf-8'):
        r = json.loads(line); res = json.loads(r["stdout"])
        for k in ("results", "evaluations", "values"):
            if isinstance(res.get(k), dict): res = res[k]; break
        for k, v in res.items():
            if isinstance(v, dict) and "nodeValue" in v: out[(r["id"], k)] = (v.get("nodeValue"), v.get("unit"), r["situation"])
    return out
B = load("work/evals/M1_G3.jsonl"); A = load("work/evals/M1_proposal.jsonl")
names = [l.rstrip("\n") for l in open("work/evals/list_G3_all.txt", encoding="utf-8")]
spec = {s["id"]: s for s in json.load(open("work/sophon/links_M1.json", encoding="utf-8"))}
LG = {json.loads(l)["spec_id"]: json.loads(l) for l in open("work/sophon/link_results_M1_G3.jsonl", encoding="utf-8")}
LP = {json.loads(l)["spec_id"]: json.loads(l) for l in open("work/sophon/link_results_M1_P.jsonl", encoding="utf-8")}
def LID(l): return l.get("link_id") or l.get("id")
def ev_link(ids):
    out = []
    for i in ids:
        for tag, L in (("G3", LG), ("P_M1", LP)):
            l = L.get(i)
            if l: cr = l.get("check_result") or {}; out.append(f"sophon {i} on {tag} = link {LID(l)}: {l.get('status')} observed={cr.get('observed')} expected={cr.get('expected')}")
    return out
S7 = {a["num"]: a for lst in json.load(open("inputs/law/S7_legi-data-2.469.0/articles.json"))["articles"].values() for a in lst}
S8 = {a["num"]: a for lst in json.load(open("inputs/law/S8_legi-data-2.489.0/articles.json"))["articles"].values() for a in lst}
def Q(SN, art, start, end):
    try: t = SN[art]["text"]; i = t.index(start); j = t.index(end, i) + len(end); return t[i:j]
    except Exception: return None
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"; DR = "dirigeant . auto-entrepreneur . DROM"; AE = "dirigeant . auto-entrepreneur"
V4o, V6o, N4, N6, M4, M6 = "LEGIARTI000049624097", "LEGIARTI000049625405", "LEGIARTI000052218738", "LEGIARTI000052218747", "LEGIARTI000049624125", "LEGIARTI000049625445"
q = {k: spec[i]["quote"] for k, i in [("e", "M1-01"), ("d", "M1-02"), ("a", "M1-03"), ("b", "M1-04"), ("c", "M1-10"), ("6e", "M1-11"), ("6ad", "M1-16"), ("6b", "M1-26"), ("6c", "M1-31"), ("7a", "M1-32"), ("7b", "M1-33"), ("7c", "M1-34")]}
q7 = {"e": Q(S7, "D613-4", "e) Travailleurs", "24,6 %"), "d": Q(S7, "D613-4", "d) Travailleurs", "21,2 %"), "a": Q(S7, "D613-4", "a) Travailleurs", "12,3 %"), "b": Q(S7, "D613-4", "b) Travailleurs", "23,2 %"),
      "6e": Q(S7, "D613-6", "maladie maternité 3,40 %", "32,50 %"), "6ad": Q(S7, "D613-6", "maladie-maternité 8,90 %", "29,70 %"), "6b": Q(S7, "D613-6", "maladie maternité mentionnée au premier alinéa", "34,00 %")}
LAW4 = f"D613-4 {N4} (VIGUEUR 2026-01-01..2999-01-01, v8.0; Décret n°2025-943 du 8 septembre 2025 art. 1, JORF 2025-09-09; nota: periods from 2026-01-01; S8 text sha256 f86c045c3f09f385...)"
LAW6 = f"D613-6 {N6} (VIGUEUR 2026-01-01..2999-01-01, v9.0; same decree; S8 text sha256 d91619e346cf5e9c...)"
LAW4o = f"D613-4 {V4o} (in force 2025-01-01..2026-01-01; S7 text)"; LAW6o = f"D613-6 {V6o} (in force 2025-01-01..2026-01-01; S7 text)"
LAW7 = "D756-5 LEGIARTI000034726710 (in force 2017-05-12; identical in S7 and S8)"
SPLIT = ["maladie-maternité", "invalidité-décès", "retraite de base", "retraite complémentaire", "autres contributions"]
XC = {"BNC": "service BNC", "BIC": "service BIC", "VENTE": "vente restauration hébergement", "CIPAV": "service BNC Cipav"}
R = []; seen = set()
def rule(r, cl, conf, ev):
    if r in seen: return
    seen.add(r); R.append({"rule": r, "classification": cl, "confidence": conf, "evidence": ev})
def vb(case, r): v = B.get((case, r)); return None if v is None else v[0]
def va(case, r): v = A.get((case, r)); return None if v is None else v[0]
def pair(case, r): return f"engine {r.replace(C, 'COT')} [{case}]: G3 = {vb(case, r)}, proposal = {va(case, r)}"
# ---------- AFFECTED: own constant edited
rule(f"{C} . service BNC . taux", "AFFECTED", "high", [
    f"{LAW4} e): \"{q['e']}\" -> 25,6 % from 2026-01-01; G3 carries 26,1 % for date >= 01/2026 (from the mort-ne version {M4}, Décret 2024-484)",
    pair("BNC@01/01/2026", f"{C} . service BNC . taux"), pair("BNC@01/12/2025", f"{C} . service BNC . taux") + f" (2025 control, {LAW4o} e): \"{q7['e']}\")",
    "proposal: variations 'date >= 01/2026' 26.1% -> 25.6%, références pinned to " + N4 + " / " + V4o + ", note"] + ev_link(["M1-01", "M1-05", "M1-06"]))
for i, (s, v, old) in enumerate(zip(SPLIT, [4.1, 3.3, 46.4, 21, 25.2], [3, 3.25, 44.85, 17.7, 31.2])):
    r = f"{C} . service BNC . répartition . {s} . taux de répartition"
    rule(r, "AFFECTED", "high", [f"{LAW6} e): \"{q['6e']}\" -> {s} = {v} %" + (" (2,60 % L621-1 + 1,50 % L621-2 espèces aggregated in the single maladie-maternité rule)" if s == SPLIT[0] else "") + f"; G3 2026 branch = {old} % (mort-ne version {M6})",
        pair("BNC@01/01/2026", r), pair("BNC@01/12/2025", r) + f" (2025 control, {LAW6o} e): \"{q7['6e']}\")", "proposal: 2026 branch value replaced; références/note at 'service BNC . répartition'"] + ev_link([f"M1-{11 + i:02d}"]))
for cat, case, base in [("service BIC", "BIC", 16), ("vente restauration hébergement", "VENTE", 21)]:
    for i, (s, v, old) in enumerate(zip(SPLIT, [10.05, 3.15, 43.45, 19.75, 23.6], [8.9, 3.1, 41.8, 16.5, 29.7])):
        r = f"{C} . {cat} . répartition . {s} . taux de répartition"
        rule(r, "AFFECTED", "high", [f"{LAW6} a/d): \"{q['6ad']}\" -> {s} = {v} % from 2026-01-01" + (" (8,80 % L621-1 + 1,25 % L621-2 aggregated)" if s == SPLIT[0] else "") + f"; G3 has the constant {old} % with no date branch ({LAW6o} a/d: \"{q7['6ad']}\")",
            pair(f"{case}@01/01/2026", r), pair(f"{case}@01/12/2025", r) + " (2025 control unchanged)", "proposal: new variations 'date >= 01/2026' branch, sinon = previous constant; références/note"] + ev_link([f"M1-{base + i:02d}"]))
for i, (s, v, old) in enumerate(zip(SPLIT, [11.4, 1.4, 29.5, 30.7, 27], [10.2, 1.4, 28.8, 25.6, 34])):
    r = f"{C} . service BNC Cipav . répartition . {s} . taux de répartition"
    if s == "invalidité-décès":
        rule(r, "UNAFFECTED", "high", [f"{LAW6} b): \"{q['6b'][:90]}...\" -> invalidité-décès (L644-2) 1,40 %, identical to the 2025 share ({LAW6o} b): 1,40 %); re-examined, no edit", pair("CIPAV@01/01/2026", r)] + ev_link(["M1-27"]))
    else:
        rule(r, "AFFECTED", "high", [f"{LAW6} b): \"{q['6b']}\" -> {s} = {v} %" + (" (10,60 % L621-1 + 0,80 % L621-2 aggregated)" if s == SPLIT[0] else (" (24,30 % 1° D642-3 + 5,20 % 2° D642-3 aggregated)" if s == SPLIT[2] else "")) + f"; G3 = {old} % (2025 share, {LAW6o} b): \"{q7['6b'][:80]}...\")",
            pair("CIPAV@01/01/2026", r), pair("CIPAV@01/12/2025", r) + " (2025 control unchanged)", "proposal: new 'date >= 01/2026' branch; références updated from LEGIARTI000043656780 to " + N6] + ev_link([f"M1-{26 + i:02d}"]))
rule(f"{DR} . taux service BNC", "AFFECTED", "high", [
    f"{LAW7}: \"{q['7a']}\" / \"{q['7b']}\" / \"{q['7c']}\" applied to the 2026 BNC rate 25,6 % ({LAW4} e) -> 4,3 / 12,8 / 17,1 %; G3 2026 branch 4,4 / 13,1 / 17,4 % (fractions of the mort-ne 26,1 %)",
    pair("DROM_BNC_P1@01/01/2026", f"{DR} . taux service BNC"), pair("DROM_BNC_P2@01/01/2026", f"{DR} . taux service BNC"), pair("DROM_BNC_P3@01/01/2026", f"{DR} . taux service BNC"),
    pair("DROM_BNC_P1@01/07/2025", f"{DR} . taux service BNC") + " (2025 control: 1/6 of 24,6 % = 4,1 %)", "proposal: 2026 branch values replaced, note"] + ev_link(["M1-32", "M1-33", "M1-34"]))
rule(f"{DR} . taux CIPAV", "AFFECTED", "high", [
    f"{LAW7} a) 1/3, b) 1/2, c) 2/3 of the CIPAV rate 23,2 % ({LAW4} b): \"{q['b']}\"; also 23,2 % in {LAW4o} b): \"{q7['b']}\") -> 7,8 / 11,6 / 15,5 %; G3 returns 7,1 / 10,6 / 14,2 % (fractions of the superseded 21,2 %) at every date: pre-existing mismatch (open since R3), confirmed by the new version and fixed here for date >= 01/2025",
    pair("DROM_CIPAV_P1@01/01/2026", f"{DR} . taux CIPAV"), pair("DROM_CIPAV_P2@01/01/2026", f"{DR} . taux CIPAV"), pair("DROM_CIPAV_P3@01/01/2026", f"{DR} . taux CIPAV"), pair("DROM_CIPAV_P1@01/07/2025", f"{DR} . taux CIPAV"),
    "ABSTENTION for 07/2024..12/2024: the text of D613-4 v.LEGIARTI000049624068 is not in S7/S8 -> G3 values kept before 01/2025"] + ev_link(["M1-35", "M1-36", "M1-37"]))
# ---------- AFFECTED by propagation (value changes, no own constant)
PROPV = [("BNC@01/01/2026", f"{C} . service BNC"), ("BNC@01/01/2026", C), ("BNC@01/01/2026", f"{AE} . cotisations et contributions")] + [("BNC@01/01/2026", f"{C} . répartition . {s}") for s in SPLIT]
for case, r in PROPV:
    rule(r, "AFFECTED", "medium", ["no own constant: propagates the D613-4 rate / D613-6 shares; value changes with the 2026 text", pair(case, r), pair("BNC@01/12/2025", r) + " (2025 control unchanged)"] + (ev_link(["M1-05", "M1-06"]) if r in (C, f"{C} . service BNC") else []))
for cat in XC.values():
    for r in [f"{C} . {cat} . répartition"] + [f"{C} . {cat} . répartition . {s}" for s in SPLIT]:
        rule(r, "AFFECTED", "medium", [f"amount = {cat} x taux de répartition; the 2026 share changes (see the taux de répartition rules); aggregated engine evidence: {pair('BNC@01/01/2026' if cat == 'service BNC' else ('BIC@01/01/2026' if cat == 'service BIC' else ('VENTE@01/01/2026' if cat.startswith('vente') else 'CIPAV@01/01/2026')), C + ' . répartition . ' + (r.split(' . ')[-1] if r.split(' . ')[-1] in SPLIT else 'retraite de base'))}"])
rule(f"{C} . répartition", "AFFECTED", "medium", ["sum container of the répartition amounts, all of which change in 2026 (see children)"])
rule(f"{C} . répartition . retraite", "AFFECTED", "medium", ["= retraite de base + retraite complémentaire; both change in 2026", pair("BNC@01/01/2026", f"{C} . répartition . retraite de base"), pair("BNC@01/01/2026", f"{C} . répartition . retraite complémentaire")])
for r in [f"{AE} . revenu net", f"{AE} . revenu net . après impôt", f"{AE} . Cipav . retraite complémentaire"]:
    rule(r, "NEEDS_REVIEW", "medium", ["downstream of the cotisations / répartition amounts (BNC total 261 -> 256 €/mois on 1 000 €/mois; Cipav retraite complémentaire share 25,6 -> 30,7 %); not evaluated in M1, no own constant from the bounded articles"])
rule(f"{AE} . Acre . taux service BNC", "NEEDS_REVIEW", "medium", [
    "YAML (G3 exonérations.publicodes l.143-147): 'arrondi: date >= 01/2026 -> 2 décimales' was designed for 50 % x 26,1 % = 13,05 %; with the in-force 25,6 % it yields 12,80 % = 12,8 % (harmless, kept, note added); the AE Acre rate itself (50 %) comes from an article outside the bounded set",
    "engine: 'dirigeant . exonérations . ACRE' and the Acre rules evaluate non applicable (None) in the tested situations (creation 01/09/2025, date 01/01/2026, ACRE oui, durée 122 jours) on G3 and proposal -> no value asserted"] + ev_link(["M1-42"]))
# ---------- UNAFFECTED after re-examination (engine evidence)
for r, k, v, case, ids in [(f"{C} . service BIC . taux", "d", 21.2, "BIC", ["M1-02", "M1-07"]), (f"{C} . vente restauration hébergement . taux", "a", 12.3, "VENTE", ["M1-03", "M1-08"]), (f"{C} . service BNC Cipav . taux", "b", 23.2, "CIPAV", ["M1-04", "M1-09"])]:
    rule(r, "UNAFFECTED", "high", [f"{LAW4} {k}): \"{q[k]}\" -> {v} %, same rate as in {LAW4o} {k}): \"{q7[k]}\" (only the CA / revenue thresholds changed)", pair(f"{case}@01/01/2026", r), "proposal: références/note only (no value change)"] + ev_link(ids))
for r, case, ids, txt in [(f"{DR} . taux service BIC", "DROM_BIC", ["M1-38", "M1-39"], "1/6, 1/2, 2/3 of 21,2 % = 3,6 / 10,6 / 14,2 %"), (f"{DR} . taux vente restauration hébergement", "DROM_VENTE", ["M1-40", "M1-41"], "1/6, 1/2, 2/3 of 12,3 % = 2,1 / 6,2 / 8,2 %")]:
    rule(r, "UNAFFECTED", "high", [f"{LAW7} fractions of a D613-4 rate unchanged in 2026: {txt}", pair(f"{case}_P1@01/01/2026", r), pair(f"{case}_P3@01/01/2026", r)] + ev_link(ids))
for r in [f"{C} . service BIC", f"{C} . vente restauration hébergement", f"{C} . service BNC Cipav"]:
    case = "BIC" if "BIC" in r else ("VENTE" if "vente" in r else "CIPAV")
    rule(r, "UNAFFECTED", "high", ["amount = CA x a rate unchanged in 2026", pair(f"{case}@01/01/2026", r)] + ev_link(["M1-07" if case == "BIC" else ("M1-08" if case == "VENTE" else "M1-09")]))
rule(DR, "UNAFFECTED", "high", [f"applicability (outre-mer, periods) governed by {LAW7}: identical version id, dates and text sha256 in S7 and S8 (work/law/compare_S7_S8.txt)"])
for r in [f"{AE} . Acre", f"{AE} . Acre . taux Acre", f"{AE} . Acre . taux service BIC", f"{AE} . Acre . taux vente restauration hébergement", f"{AE} . Acre . taux CIPAV", f"{AE} . Acre . notification calcul ACRE annuel"]:
    rule(r, "UNAFFECTED", "medium", ["Acre rate article outside the bounded set; inputs from D613-4 (BIC 21,2 / vente 12,3 / CIPAV 23,2 %) unchanged in the 2026 version; engine: non applicable (None) in the tested Acre situations on G3 and proposal"])
rule(f"{C} . répartition . formation professionnelle", "UNAFFECTED", "high", ["= CFP (code du travail, outside the bounded set); no bounded article governing it changed"])
rule("dirigeant . exonérations . ACRE", "UNAFFECTED", "high", ["governed by L613-7 LEGIARTI000048683570 and D131-6-1 LEGIARTI000036475110: identical version id, dates and text sha256 in S7 and S8; engine probe: non applicable in the tested situations (not investigated further)"])
rule("entreprise . imposition . régime . micro-entreprise . revenu abattu", "UNAFFECTED", "high", ["abattement forfaitaire (CGI 50-0/102 ter via L613-7, unchanged S7->S8)"])
reassessed = sorted(seen)
# ---------- everything else bounded -> UNAFFECTED, not re-examined
IND_REASON = ("governed (where a bounded article applies) by L131-6, L136-3, D131-6-1, D136-5, D613-5, D621-2, D632-1, D633-3: all 8 have identical version id, in-force dates and text sha256 in S7 and S8 (work/law/compare_S7_S8.txt: UNCHANGED; store snapshots S7/S8); the S7->S8 changes (D613-4, D613-6: micro-social rates and splits) govern only the auto-entrepreneur rules. "
              "Not re-examined in M1; alignment with G3 itself was last checked on earlier pins (store links L0028-L0055, L0075-L0109: on G3 mostly RULE_FILE_ABSENT/RULE_CHANGED after the 2025-09-19 reorganisation) -> inherited status, stated as such.")
AE_REASON = "auto-entrepreneur rule not governed by D613-4/D613-6 (TFC, CFP, impôt, affiliation, chiffre d'affaires, Cipav adhésion, DROM applicability: texts outside the bounded set or L613-7/D756-5, unchanged S7->S8); no bounded article governing it changed"
not_re = []
bounded = [n for n in names if n.startswith("dirigeant . auto-entrepreneur") or n.startswith("dirigeant . indépendant") or n.startswith("dirigeant . exonérations")] + ["entreprise . imposition . régime . micro-entreprise . revenu abattu"]
for n in bounded:
    if n in seen: continue
    reason = IND_REASON if n.startswith("dirigeant . indépendant") else AE_REASON
    rule(n, "UNAFFECTED", "high" if n.startswith("dirigeant . indépendant") else "medium", [reason]); not_re.append({"rule": n, "reason": reason})
# ---------- evaluations
evals = []
ART = lambda r: "D756-5" if r.startswith(DR) else ("D613-6" if "répartition" in r else "D613-4")
CAT = lambda case: ("CIPAV" if "CIPAV" in case else ("BIC" if "BIC" in case else ("VENTE" if "VENTE" in case else "BNC")))
Qmap = {"D613-4": {"BNC": "e", "BIC": "d", "VENTE": "a", "CIPAV": "b"}, "D613-6": {"BNC": "6e", "BIC": "6ad", "VENTE": "6ad", "CIPAV": "6b"}}
for (case, r), (v0, unit, sit) in B.items():
    v1 = A.get((case, r), (None,))[0]; d = sit["date"]; art = ART(r); cat = CAT(case)
    e = {"rule": r, "date": d, "situation": sit, "value_before_G3": v0, "value_after_proposal": v1, "changed": v0 != v1, "unit": unit, "article": art}
    if d == "01/01/2026":
        if art == "D756-5": e.update({"article_version_id": f"LEGIARTI000034726710 (D756-5) x D613-4 {N4}", "in_force": "2017-05-12.. x 2026-01-01..", "text_available": True, "quote": q["7a"] if "P1" in case else (q["7b"] if "P2" in case else q["7c"]), "rate_quote": q[Qmap["D613-4"][cat]]})
        else: e.update({"article_version_id": N4 if art == "D613-4" else N6, "in_force": "2026-01-01..2999-01-01", "modifying_text": "Décret n°2025-943 du 8 septembre 2025 - art. 1 (JORF 2025-09-09)", "text_available": True, "quote": q[Qmap[art][cat]]})
    else:
        if art == "D756-5": e.update({"article_version_id": f"LEGIARTI000034726710 (D756-5) x D613-4 {V4o}", "in_force": "2017-05-12.. x 2025-01-01..2026-01-01", "text_available": True, "quote": q["7a"] if "P1" in case else (q["7b"] if "P2" in case else q["7c"]), "rate_quote": q7[Qmap["D613-4"][cat]], "law_snapshot": "S7"})
        else: e.update({"article_version_id": V4o if art == "D613-4" else V6o, "in_force": "2025-01-01..2026-01-01", "text_available": True, "quote": q7[Qmap[art][cat]], "law_snapshot": "S7"})
    if r.startswith(DR) and cat == "CIPAV": e["comment"] = "G3 value = fraction of the superseded 21,2 % (pre-existing mismatch); proposal = fraction of 23,2 % (text of both 2025 and 2026 versions)"
    if case.startswith("ACRE") and v0 is None: e["comment"] = "non applicable in this situation (no value asserted)"
    evals.append(e)
abst = [
    {"topic": f"{DR} . taux CIPAV for 07/2024..12/2024", "reason": "the rate 23,2 % applied from 2024-07-01 (D613-4 v.LEGIARTI000049624068) but that version's text is not in S7 or S8 (only current texts are included); the proposal fixes the fractions only from date >= 01/2025 (S7 text) and keeps G3's values before"},
    {"topic": "D613-4 c) meublés de tourisme (6 %, 87 % abattement) and D613-6 c) split", "reason": "no rule for this category exists in G3 (not implemented); no value proposed"},
    {"topic": f"{AE} . Acre . taux * (AE Acre rate 50 %, CIPAV 13,90 %)", "reason": "the micro-social Acre rate article is outside the bounded set; engine non applicable in tested situations; no value asserted"},
    {"topic": "D613-6 separate L621-1 / L621-2 lines", "reason": "the new text splits maladie-maternité into two lines (e.g. 2,60 % + 1,50 % for e); G3 has a single maladie-maternité share rule per category, so the proposal records their SUM (documented in the notes); a finer split would need new rules (design choice, not a legal value)"},
]
ch = [{"article": "D613-4", "old_version_id": V4o, "old_in_force": "2025-01-01..2026-01-01", "old_etat_in_S8": "MODIFIE", "old_text_sha256_prefix": "8c3b3865c4873f63",
       "new_version_id": N4, "new_etat": "VIGUEUR", "new_in_force": "2026-01-01..2999-01-01", "version": "8.0", "new_text_sha256_prefix": "f86c045c3f09f385", "text_available": True,
       "modifying_text": "Décret n°2025-943 du 8 septembre 2025 - art. 1 (JORFTEXT000052211971, JORF 2025-09-09, dateDebutCible 2025-09-10); nota: 'ces dispositions ... s'appliquent au titre des périodes courant à compter du 1 er janvier 2026'",
       "text_changes": "e) BNC 24,6 % -> 25,6 %; thresholds a) 79 828/23 150 -> 89 776/26 035; b) 35 076/23 150 -> 42 586/28 107; c) 29 230/3 800 -> 31 115/4 045; d) 46 300/23 150 -> 52 070/26 035; e) 10 000/6 600 -> 23 609/15 582; rates a) 12,3 b) 23,2 c) 6 d) 21,2 unchanged (work/law/compare_S7_S8.txt)",
       "mort_ne_version": f"{M4} still MODIFIE_MORT_NE (2026-01-01..2025-09-10)"},
      {"article": "D613-6", "old_version_id": V6o, "old_in_force": "2025-01-01..2026-01-01", "old_etat_in_S8": "MODIFIE", "old_text_sha256_prefix": "69b8e1b56c6185a7",
       "new_version_id": N6, "new_etat": "VIGUEUR", "new_in_force": "2026-01-01..2999-01-01", "version": "9.0", "new_text_sha256_prefix": "d91619e346cf5e9c", "text_available": True,
       "modifying_text": "Décret n°2025-943 du 8 septembre 2025 - art. 1 (JORFTEXT000052211971); same nota (periods from 2026-01-01)",
       "text_changes": "new splits with separate L621-1 / L621-2 lines: a/d 8,80+1,25 / 3,15 / 43,45 / 19,75 / 23,60 (was 8,90 / 3,10 / 41,80 / 16,50 / 29,70); b 10,60+0,80 / 1,40 / 24,30+5,20 / 30,70 / 27,00 (was 9,30+0,90 / 1,40 / 23,45+5,35 / 25,60 / 34,00); c 0,00+5,10 / 3,80 / 50,20 / 18,60 / 22,30 (was 4,90 / 3,50 / 48,30 / 15,10 / 28,20); e 2,60+1,50 / 3,30 / 46,40 / 21,00 / 25,20 (was 3,40 / 3,50 / 47,60 / 13,00 / 32,50)",
       "mort_ne_version": f"{M6} still MODIFIE_MORT_NE"}]
CHG = (f"S7->S8 (decision date 2026-01-01): D613-4 {V4o} -> {N4} and D613-6 {V6o} -> {N6}, both now VIGUEUR from 2026-01-01 WITH text, modified by Décret n°2025-943 du 8 septembre 2025 art. 1 (applies to periods from 2026-01-01). "
       "BNC rate 24,6 -> 25,6 % (not the 26,1 % that G3 carried from the mort-ne Décret 2024-484 step); all D613-6 splits change for 2026 (a/d, b, c, e); the other 10 bounded articles are byte-identical (compare_S7_S8.txt).")
reports = sorted(glob.glob("work/sophon/reports/M1_*"))
def cnt(L): c = {}; [c.__setitem__(l.get("status"), c.get(l.get("status"), 0) + 1) for l in L.values()]; return c
revc = json.load(open("work/sophon/reports/M1_revalidate_S8_G3_cmd.json"))["counts"] if os.path.exists("work/sophon/reports/M1_revalidate_S8_G3_cmd.json") else None
revp = json.load(open("work/sophon/reports/M1_revalidate_S8_PM1_cmd.json"))["counts"] if os.path.exists("work/sophon/reports/M1_revalidate_S8_PM1_cmd.json") else None
ans = {"task": "M1", "decision_date": "2026-01-01", "law_snapshots": {"S7": "legi-data 2.469.0 (published 2025-10-01)", "S8": "legi-data 2.489.0 (published 2026-01-01)"}, "rules_pin": "G3 d6c374271727 (modele-social 10.0.0, committed 2025-12-30; 722 raw / 1427 parsed rules)",
       "unchanged_articles": ["L131-6", "L136-3", "L613-7", "D131-6-1", "D136-5", "D613-5", "D621-2", "D632-1", "D633-3", "D756-5"], "articles_missing_in_snapshot": [],
       "changed_articles": ch, "law_change_summary": CHG, "rules": R, "reassessed_rules": reassessed, "not_reassessed_rules": not_re, "no_change_needed": False,
       "proposal_dir": "work/proposals/M1/modele-social/règles", "proposal_script": "work/scripts/apply_proposal_M1.py", "proposal_diff": "work/proposals/M1/CHANGES.diff",
       "proposal_nature": "numeric transposition of D613-4 " + N4 + " / D613-6 " + N6 + " for date >= 01/2026 (BNC rate 25,6 %; 2026 splits for BNC, BIC, vente, Cipav; DROM BNC fractions 4,3/12,8/17,1), fix of the DROM CIPAV fractions (7,8/11,6/15,5 from 01/2025, on the 23,2 % of the S7 and S8 texts), références pinned to the version ids, notes; BIC/vente/Cipav rates unchanged (documentation only)",
       "build_ok": True, "build_counts": {"raw_rule_count": 722, "parsed_rule_count": 1427},
       "proposal_vs_G3_changed_values": sum(1 for k in B if A.get(k, (None,))[0] != B[k][0]), "evaluations": evals, "abstentions": abst, "approval": "none recorded",
       "notes": "See output/NOTES.md. " + CHG + " G3 reproduces the 2025 texts (controls at 01/07/2025 and 01/12/2025 unchanged) but its 2026 branches (BNC 26,1 %, BNC split 3/3,25/44,85/17,7/31,20, DROM BNC 4,4/13,1/17,4) rest on the withdrawn decree step, and BIC/vente/Cipav splits have no 2026 branch: AFFECTED, edited in the proposal (build 722/1427 OK). The DROM CIPAV fractions were already wrong (21,2 % basis) and are fixed from 01/2025. No value from outside S7/S8 was used; no approval exists in the corpus.",
       "sophon_reports": reports, "sophon_snapshots": {"law": ["S7 (already registered)", "S8"], "rules": ["G3 (re-registered, identical)", "P_M1 (proposal copy)"]},
       "sophon_links_added": [{"spec_id": i, "rules_snapshot": tag, "link_id": LID(l), "status": l.get("status"), "rule": spec[i]["rule"], "article": spec[i]["article"]} for tag, L in (("G3", LG), ("P_M1", LP)) for i, l in L.items()],
       "sophon_link_status_counts": {"G3": cnt(LG), "P_M1": cnt(LP)}, "sophon_revalidate_S8_G3_counts_before_M1_links": revc, "sophon_revalidate_S8_PM1_counts": revp, "self_reported_tool_calls": CALLS}
os.makedirs("output", exist_ok=True)
json.dump(ans, open("output/answer.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
cl = {}
for r in R: cl[r["classification"]] = cl.get(r["classification"], 0) + 1
N = f"""# M1 — change maintenance, decision date 2026-01-01 (arm B)

Law snapshots S7 (legi-data 2.469.0, published 2025-10-01) and S8 (legi-data 2.489.0, published 2026-01-01); rules pin G3 d6c374271727 (modele-social 10.0.0, 722 raw / 1427 parsed rules), unchanged since M0. Store: S8 and P_M1 registered (G3 re-registered, identical); revalidate S8xG3 run first (counts {revc}).

## 1. What changed between S7 and S8 (work/law/compare_S7_S8.txt, work/law/S8_dump.txt)
Only **D613-4** and **D613-6**; the 10 other bounded articles have identical version id, dates and text sha256.
- D613-4: {V4o} (2025-01-01..2026-01-01) -> **{N4}** (VIGUEUR 2026-01-01..2999-01-01, v8.0, sha256 f86c045c...). Modifying text now named: **Décret n°2025-943 du 8 septembre 2025, art. 1** (JORF 2025-09-09; nota: applies to periods from 2026-01-01). Text: e) BNC **25,6 %** ("{q['e']}"); a) 12,3 %, b) 23,2 %, c) 6 %, d) 21,2 % unchanged; all CA/revenue thresholds raised (89 776/26 035; 42 586/28 107; 31 115/4 045; 52 070/26 035; 23 609/15 582). The mort-né version {M4} stays MODIFIE_MORT_NE.
- D613-6: {V6o} -> **{N6}** (VIGUEUR 2026-01-01, v9.0, sha256 d91619e3...), same decree. New splits with separate L. 621-1 / L. 621-2 lines: a/d 8,80+1,25 / 3,15 / 43,45 / 19,75 / 23,60 ; b 10,60+0,80 / 1,40 / 24,30+5,20 / 30,70 / 27,00 ; c 0,00+5,10 / 3,80 / 50,20 / 18,60 / 22,30 ; e 2,60+1,50 / 3,30 / 46,40 / 21,00 / 25,20 (each sums to 100).

## 2. Impact on G3
G3's `date >= 01/2026` branches (BNC 26,1 %; BNC split 3/3,25/44,85/17,7/31,20; DROM BNC 4,4/13,1/17,4) came from the withdrawn Décret 2024-484 step and are now contradicted by the in-force text; BIC, vente and Cipav splits have no 2026 branch at all although D613-6 changes them; the BIC/vente/Cipav rates are confirmed unchanged. The DROM CIPAV fractions were already computed on 21,2 % instead of 23,2 % (pre-existing, confirmed by the new text).

## 3. Engine evidence (CA 1 000 €/mois; work/evals/M1_G3.jsonl vs M1_proposal.jsonl, grid M1_grid.txt; 39 cases)
| rule | 01/12/2025 (S7 text, G3 = proposal) | 01/01/2026 G3 | 01/01/2026 proposal (S8 text) |
|---|---|---|---|
| service BNC . taux | 24.6 | 26.1 | **25.6** ("{q['e']}") |
| service BNC (€/mois) / cotisations | 246 | 261 | **256** |
| BNC split | 3.4/3.5/47.6/13/32.5 | 3/3.25/44.85/17.7/31.2 | **4.1/3.3/46.4/21/25.2** (2,60+1,50 aggregated) |
| BIC split (vente identical) | 8.9/3.1/41.8/16.5/29.7 | same | **10.05/3.15/43.45/19.75/23.6** |
| Cipav split | 10.2/1.4/28.8/25.6/34 | same | **11.4/1.4/29.5/30.7/27** |
| BIC / vente / Cipav taux | 21.2 / 12.3 / 23.2 | same | same (confirmed by {N4}) |
| DROM BNC P1/P2/P3 | 4.1/12.3/16.4 (2025) | 4.4/13.1/17.4 | **4.3/12.8/17.1** |
| DROM CIPAV P1/P2/P3 | 7.1/10.6/14.2 (wrong) | 7.1/10.6/14.2 | **7.8/11.6/15.5** (also at 2025 dates) |
| DROM BIC / vente | 3.6/10.6/14.2 ; 2.1/6.2/8.2 | same | same |
Acre rules and `dirigeant . exonérations . ACRE` evaluate non applicable in the tested situations (no value asserted).

## 4. Classification ({cl}; {len(reassessed)} rules re-examined, {len(not_re)} not re-examined)
- **AFFECTED (own edit)**: `service BNC . taux`; the 5 BNC, 5 BIC, 5 vente and 4 Cipav `taux de répartition` (Cipav invalidité-décès unchanged at 1,40 %); `DROM . taux service BNC`; `DROM . taux CIPAV`. **AFFECTED (propagation, medium)**: category amounts, `cotisations`, `cotisations et contributions`, répartition amounts.
- **NEEDS_REVIEW**: `revenu net`, `revenu net . après impôt`, `Cipav . retraite complémentaire` (downstream, not evaluated); `Acre . taux service BNC` (2026 rounding branch harmless with 25,6 %; Acre rate outside the set).
- **UNAFFECTED after re-examination**: BIC/vente/Cipav rates and amounts, DROM BIC/vente, DROM applicability, Acre BIC/vente/CIPAV, CFP, `exonérations . ACRE`, `revenu abattu`.
- **Not re-examined**: all 273 `dirigeant . indépendant . *` rules and the AE rules not governed by D613-4/D613-6 — their governing bounded articles are byte-identical in S7 and S8 (compare_S7_S8.txt); inherited alignment status from earlier pins, stated as such.

## 5. Proposal
`work/proposals/M1/modele-social/règles` (script work/scripts/apply_proposal_M1.py, diff CHANGES.diff, registered as P_M1): build OK 722/1427; {ans['proposal_vs_G3_changed_values']} changed values over the 39 cases, all at 2026 dates or DROM CIPAV. Aggregation choice: the new separate L. 621-1 / L. 621-2 lines are summed into the existing single `maladie-maternité` share rule (documented in notes).

## 6. Abstentions
DROM CIPAV for 07/2024..12/2024 (text of v.LEGIARTI000049624068 not in S7/S8); D613-4 c) / D613-6 c) meublés de tourisme not implemented; AE Acre rate outside the set.

## 7. Sophon
42 links M1-01..42 recorded twice: on G3 {cnt(LG)} (FAILED = the documented 2026 misalignments and DROM CIPAV) and on P_M1 {cnt(LP)}. Reports: {', '.join(os.path.basename(p) for p in reports)}.

## 8. Approvals
None recorded anywhere in the corpus (no sign-off, ratification or approval file).

## 9. Still open
Meublés de tourisme 6 % (D613-4 c); D756-5 II CA cap; L613-7 minimum-contribution option; D613-5 conjoint collaborateur of AE; AE Acre rate article outside the set; Acre AE rules non applicable in probes (applicability not investigated); indépendant tree alignment on G3 not re-verified since the 2025-09-19 reorganisation.
"""
open("output/NOTES.md", "w", encoding="utf-8").write(N)
json.load(open("output/answer.json")); print("answer.json valid:", len(R), "rules", cl, "|", len(evals), "evaluations,", len(abst), "abstentions,", len(not_re), "not reassessed,", len(reassessed), "reassessed,", len(reports), "reports; links G3", cnt(LG), "P", cnt(LP))
