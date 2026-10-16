"""M1 link spec (law S8). Quotes are extracted from the S8 texts between anchor tokens (so they are exact substrings; asserted).
The same spec is recorded twice: on rules G3 (pin; 2026 BNC/DROM checks expected to FAIL) and on P_M1 (proposal; expected VERIFIED).
Writes work/sophon/links_M1.json."""
import json
S8 = {a["num"]: a for lst in json.load(open("inputs/law/S8_legi-data-2.489.0/articles.json"))["articles"].values() for a in lst}
def Q(art, start, end):
    t = S8[art]["text"]; i = t.index(start); j = t.index(end, i) + len(end); return t[i:j]
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"; DR = "dirigeant . auto-entrepreneur . DROM"
D = "01/01/2026"
P = {"date": D, "salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois", "entreprise . date de création": "01/01/2021", "dirigeant . exonérations . ACRE": "non", "établissement . commune . département . outre-mer": "non"}
BNC = dict(P, **{"entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "non"})
CIP = dict(P, **{"entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "oui", "entreprise . date de création": "01/01/2019"})
BIC = dict(P, **{"entreprise . activité . nature": "'artisanale'", "entreprise . activités . service ou vente": "'service'"})
VEN = dict(P, **{"entreprise . activité . nature": "'commerciale'", "entreprise . activités . service ou vente": "'vente'"})
PER = {"P1": {"entreprise . durée d'activité": "300 jour", "entreprise . durée d'activité . trimestres civils": "4 trimestre civil", "entreprise . durée d'activité . années civiles": "1 année civile"},
       "P2": {"entreprise . durée d'activité": "900 jour", "entreprise . durée d'activité . trimestres civils": "10 trimestre civil", "entreprise . durée d'activité . années civiles": "3 année civile"},
       "P3": {"entreprise . durée d'activité": "1500 jour", "entreprise . durée d'activité . trimestres civils": "20 trimestre civil", "entreprise . durée d'activité . années civiles": "5 année civile"}}
def drom(base, per, date=D): s = dict(base, **PER[per]); s["établissement . commune . département . outre-mer"] = "oui"; s["date"] = date; return s
qa = Q("D613-4", "a) Travailleurs", "12,3 %"); qb = Q("D613-4", "b) Travailleurs", "23,2 %"); qc = Q("D613-4", "c) Travailleurs", "6 %")
qd = Q("D613-4", "d) Travailleurs", "21,2 %"); qe = Q("D613-4", "e) Travailleurs", "25,6 %")
q6ad = Q("D613-6", "-pour les personnes relevant des a et d", "23,60 %"); q6b = Q("D613-6", "-pour les personnes relevant du b", "27,00 %")
q6c = Q("D613-6", "-pour les personnes relevant du c", "22,30 %"); q6e = Q("D613-6", "-pour les personnes relevant du e", "25,20 %")
q7a = Q("D756-5", "après arrondi au dixième", "1/3 dans les autres cas"); q7b = Q("D756-5", "b) 1/2", "troisième année civile d'activité"); q7c = Q("D756-5", "c) 2/3", "quatrième année civile d'activité")
V4 = "D613-4 v.LEGIARTI000052218738 (VIGUEUR from 2026-01-01; Décret n°2025-943 du 8 septembre 2025 art. 1, JORF 2025-09-09; nota: periods from 2026-01-01; S8 legi-data 2.489.0)"
V6 = "D613-6 v.LEGIARTI000052218747 (VIGUEUR from 2026-01-01; Décret n°2025-943 du 8 septembre 2025 art. 1; S8)"
V7 = "D756-5 v.LEGIARTI000034726710 (unchanged S7->S8)"
S = []; n = [0]
def add(rule, art, quote, claim, check=None, status=None, note="M1"):
    n[0] += 1; d = {"id": f"M1-{n[0]:02d}", "rule": rule, "article": art, "quote": quote, "claim": claim, "note": note}
    if check: d["check"] = check
    else: d["status"] = status
    S.append(d)
def ck(rule, sit, exp, tol=0.001): return {"rule": rule, "situation": sit, "expect": exp, "tolerance": tol}
# D613-4 2026 rates
add(C + " . service BNC . taux", "D613-4", qe, V4 + ": e) BNC global rate 25,6 % on 01/01/2026.", ck(C + " . service BNC . taux", BNC, 25.6))
add(C + " . service BIC . taux", "D613-4", qd, V4 + ": d) service BIC global rate 21,2 % on 01/01/2026 (unchanged).", ck(C + " . service BIC . taux", BIC, 21.2))
add(C + " . vente restauration hébergement . taux", "D613-4", qa, V4 + ": a) vente global rate 12,3 % on 01/01/2026 (unchanged).", ck(C + " . vente restauration hébergement . taux", VEN, 12.3))
add(C + " . service BNC Cipav . taux", "D613-4", qb, V4 + ": b) CIPAV (11° R641-1) global rate 23,2 % on 01/01/2026 (unchanged).", ck(C + " . service BNC Cipav . taux", CIP, 23.2))
add(C + " . service BNC", "D613-4", qe, V4 + ": BNC AE, CA 1 000 €/mois -> 256 €/mois on 01/01/2026.", ck(C + " . service BNC", BNC, 256))
add(C, "D613-4", qe, V4 + ": BNC AE total cotisations 256 €/mois on 1 000 €/mois (01/01/2026).", ck(C, BNC, 256))
add(C + " . service BIC", "D613-4", qd, V4 + ": service BIC AE, CA 1 000 €/mois -> 212 €/mois.", ck(C + " . service BIC", BIC, 212))
add(C + " . vente restauration hébergement", "D613-4", qa, V4 + ": vente AE, CA 1 000 €/mois -> 123 €/mois.", ck(C + " . vente restauration hébergement", VEN, 123))
add(C + " . service BNC Cipav", "D613-4", qb, V4 + ": CIPAV AE (created 2019), CA 1 000 €/mois -> 232 €/mois.", ck(C + " . service BNC Cipav", CIP, 232))
add(C, "D613-4", qc, V4 + ": c) meublés de tourisme 6 % (31 115 euros, 87 %) - still no rule for this category in the tree (no meublé/tourisme rule name); not implemented.", status="UNKNOWN")
# D613-6 2026 shares
for s, v, cl in [("maladie-maternité", 4.1, "2,60 % (L621-1) + 1,50 % (L621-2 espèces) = 4,10 % aggregated in one rule"), ("invalidité-décès", 3.3, "3,30 %"), ("retraite de base", 46.4, "46,40 %"), ("retraite complémentaire", 21, "21,00 %"), ("autres contributions", 25.2, "25,20 % CSG-CRDS")]:
    add(f"{C} . service BNC . répartition . {s} . taux de répartition", "D613-6", q6e, V6 + f": e) share {s} = {cl} on 01/01/2026.", ck(f"{C} . service BNC . répartition . {s} . taux de répartition", BNC, v))
for cat, sit in [("service BIC", BIC), ("vente restauration hébergement", VEN)]:
    for s, v, cl in [("maladie-maternité", 10.05, "8,80 % (L621-1) + 1,25 % (L621-2 espèces) = 10,05 % aggregated"), ("invalidité-décès", 3.15, "3,15 %"), ("retraite de base", 43.45, "43,45 %"), ("retraite complémentaire", 19.75, "19,75 %"), ("autres contributions", 23.6, "23,60 % CSG-CRDS")]:
        add(f"{C} . {cat} . répartition . {s} . taux de répartition", "D613-6", q6ad, V6 + f": a/d share {s} = {cl} on 01/01/2026 ({cat}).", ck(f"{C} . {cat} . répartition . {s} . taux de répartition", sit, v))
for s, v, cl in [("maladie-maternité", 11.4, "10,60 % (L621-1) + 0,80 % (L621-2) = 11,40 % aggregated"), ("invalidité-décès", 1.4, "1,40 % (L644-2, unchanged)"), ("retraite de base", 29.5, "24,30 % (1° D642-3) + 5,20 % (2° D642-3) = 29,50 % aggregated"), ("retraite complémentaire", 30.7, "30,70 % (L644-1)"), ("autres contributions", 27, "27,00 % CSG-CRDS")]:
    add(f"{C} . service BNC Cipav . répartition . {s} . taux de répartition", "D613-6", q6b, V6 + f": b) share {s} = {cl} on 01/01/2026.", ck(f"{C} . service BNC Cipav . répartition . {s} . taux de répartition", CIP, v))
add(C, "D613-6", q6c, V6 + ": c) meublés de tourisme split (0,00 / 5,10 / 3,80 / 50,20 / 18,60 / 22,30 %) - category not implemented in the tree.", status="UNKNOWN")
# D756-5 x D613-4 2026 (DROM)
add(DR + " . taux service BNC", "D756-5", q7a, V7 + " a) 1/6 of 25,6 % (" + V4 + " e) = 4,27 -> 4,3 % (BNC, first period, 01/01/2026).", ck(DR + " . taux service BNC", drom(BNC, "P1"), 4.3))
add(DR + " . taux service BNC", "D756-5", q7b, V7 + " b) 1/2 of 25,6 % = 12,8 % (BNC, second period, 01/01/2026).", ck(DR + " . taux service BNC", drom(BNC, "P2"), 12.8))
add(DR + " . taux service BNC", "D756-5", q7c, V7 + " c) 2/3 of 25,6 % = 17,07 -> 17,1 % (BNC, from 4th civil year, 01/01/2026).", ck(DR + " . taux service BNC", drom(BNC, "P3"), 17.1))
add(DR + " . taux CIPAV", "D756-5", q7a, V7 + " a) 1/3 of 23,2 % (" + V4 + " b) = 7,73 -> 7,8 % (01/01/2026). G3 returns 7,1 (1/3 of the superseded 21,2 %): pre-existing mismatch.", ck(DR + " . taux CIPAV", drom(CIP, "P1"), 7.8))
add(DR + " . taux CIPAV", "D756-5", q7b, V7 + " b) 1/2 of 23,2 % = 11,6 % (01/01/2026); G3 returns 10,6.", ck(DR + " . taux CIPAV", drom(CIP, "P2"), 11.6))
add(DR + " . taux CIPAV", "D756-5", q7c, V7 + " c) 2/3 of 23,2 % = 15,47 -> 15,5 % (01/01/2026); G3 returns 14,2.", ck(DR + " . taux CIPAV", drom(CIP, "P3"), 15.5))
add(DR + " . taux service BIC", "D756-5", q7a, V7 + " a) 1/6 of 21,2 % = 3,53 -> 3,6 % (01/01/2026, unchanged).", ck(DR + " . taux service BIC", drom(BIC, "P1"), 3.6))
add(DR + " . taux service BIC", "D756-5", q7c, V7 + " c) 2/3 of 21,2 % = 14,13 -> 14,2 % (01/01/2026, unchanged).", ck(DR + " . taux service BIC", drom(BIC, "P3"), 14.2))
add(DR + " . taux vente restauration hébergement", "D756-5", q7a, V7 + " a) 1/6 of 12,3 % = 2,05 -> 2,1 % (01/01/2026, unchanged).", ck(DR + " . taux vente restauration hébergement", drom(VEN, "P1"), 2.1))
add(DR + " . taux vente restauration hébergement", "D756-5", q7c, V7 + " c) 2/3 of 12,3 % = 8,2 % (01/01/2026, unchanged).", ck(DR + " . taux vente restauration hébergement", drom(VEN, "P3"), 8.2))
add("dirigeant . auto-entrepreneur . Acre . taux service BNC", "D613-4", qe, "INFERRED (no engine check: the AE Acre rate article is outside the bounded set): the 2026 rounding branch (2 décimales) was designed for 50 % x 26,1 % = 13,05 %; with the in-force 25,6 % it yields 12,80 % = 12,8 %, so it is harmless and kept.", status="INFERRED")
for l in S: assert l["quote"] in S8[l["article"]]["text"], l["id"]
json.dump(S, open("work/sophon/links_M1.json", "w"), ensure_ascii=False, indent=1); print("spec ok", len(S))
for k, v in [("qa", qa), ("qb", qb), ("qc", qc), ("qd", qd), ("qe", qe), ("q6e", q6e), ("q6ad", q6ad[:120] + "..."), ("q6b", q6b[:120] + "..."), ("q7a", q7a)]: print(k, "=", v)
