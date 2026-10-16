"""M2 link spec (law S9; S8 for the pre-2026 version of D131-6-1). Quotes are exact substrings extracted between anchors (asserted).
Recorded twice: on G4 (the pin; 2026-création checks expected to FAIL) and on P_M2 (proposal; expected VERIFIED). Writes work/sophon/links_M2.json."""
import json
def load(p): return {a["num"]: a for lst in json.load(open(p))["articles"].values() for a in lst}
S9 = load("inputs/law/S9_legi-data-2.514.0/articles.json"); S8 = load("inputs/law/S8_legi-data-2.489.0/articles.json")
def Q(SN, art, start, end):
    t = SN[art]["text"]
    for s_, e_ in ((start, end), (start.replace("'", "’"), end.replace("'", "’"))):
        if s_ in t: i = t.index(s_); j = t.index(e_, i) + len(e_); return t[i:j]
    raise KeyError((art, start))
IND = "dirigeant . indépendant . cotisations et contributions"; EX = IND + " . exonérations . ACRE"; AE = "dirigeant . auto-entrepreneur"
C = AE + " . cotisations et contributions . cotisations"; DR = AE + " . DROM"
BASE = {"salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "non", "entreprise . imposition": "'IR'",
        "établissement . commune . département . outre-mer": "non", "dirigeant . exonérations . ACRE": "oui", "entreprise . activité . nature": "'commerciale'"}
def sit(cre, date, R): s = dict(BASE); s.update({"entreprise . date de création": cre, "date": date, "dirigeant . indépendant . revenu professionnel": f"{R} €/an"}); return s
N26_20, N26_42, N26_60 = sit("01/01/2026", "01/07/2026", 20000), sit("01/01/2026", "01/07/2026", 42052.5), sit("01/01/2026", "01/07/2026", 60000)
O25_20, O25_42 = sit("01/07/2025", "01/07/2026", 20000), sit("01/07/2025", "01/07/2026", 42052.5)
C25_20, C25_41 = sit("01/01/2025", "01/07/2025", 20000), sit("01/01/2025", "01/07/2025", 41212.5)
# quotes (S9 text of D131-6-1 v8.0)
q_I = Q(S9, "D131-6-1", "La durée de l'exonération", "douze mois")
q_quart = Q(S9, "D131-6-1", "Lorsque le revenu ou la rémunération est inférieur ou égal aux trois quarts", "au quart du montant total des cotisations")
q_form = Q(S9, "D131-6-1", "Lorsque le revenu ou la rémunération est supérieur au trois quarts", "(PSS−R).")
q_E = Q(S9, "D131-6-1", "E est le montant total des cotisations", "égal aux trois quarts de la valeur du plafond mentionné à l'article L. 241-3")
q_1365 = Q(S9, "D131-6-1", "Les dispositions du présent II", "L. 131-6-5.")
q_III = Q(S9, "D131-6-1", "La valeur du plafond de la sécurité sociale mentionné à la présente section", "durée d'affiliation.")
q_60 = Q(S9, "D131-6-1", "La demande d'exonérations de cotisations sociales", "code de commerce.")
# quotes (S8 text of D131-6-1 v7.0, in force 2018-01-01..2026-01-01, still governing créations before 2026-01-01 per the S9 nota)
q8_total = Q(S8, "D131-6-1", "Lorsque le revenu ou la rémunération est inférieur ou égal aux trois quarts", "correspond au montant total des cotisations")
q8_form = Q(S8, "D131-6-1", "Montant de l'exonération = E/0,25 PSS", "(PSS-R)")
# AE quotes (S9 == S8 texts)
qe = Q(S9, "D613-4", "e) Travailleurs", "25,6 %"); qb = Q(S9, "D613-4", "b) Travailleurs", "23,2 %")
q7a = Q(S9, "D756-5", "après arrondi au dixième", "1/3 dans les autres cas"); q7b = Q(S9, "D756-5", "b) 1/2", "troisième année civile d'activité"); q7c = Q(S9, "D756-5", "c) 2/3", "quatrième année civile d'activité")
q6e = Q(S9, "D613-6", "-pour les personnes relevant du e", "25,20 %"); q6ad = Q(S9, "D613-6", "-pour les personnes relevant des a et d", "23,60 %"); q6b = Q(S9, "D613-6", "-pour les personnes relevant du b", "27,00 %")
V9 = "D131-6-1 v.LEGIARTI000053451315 (v8.0, VIGUEUR 2026-01-01..2999-01-01; Décret n°2026-69 du 6 février 2026 art. 1, JORF 2026-02-08; nota: en vigueur le 1er janvier 2026, s'applique aux créations et reprises d'entreprise intervenant à compter de cette date; S9 legi-data 2.514.0, text sha256 59f4edcf15fb...)"
V8 = "D131-6-1 v.LEGIARTI000036475110 (v7.0, in force 2018-01-01..2026-01-01 per S9 metadata; S8 legi-data 2.489.0 text sha256 af896c573ea3...; still governs créations/reprises before 2026-01-01 per the S9 nota)"
V4 = "D613-4 v.LEGIARTI000052218738 (VIGUEUR 2026-01-01; identical in S8 and S9)"; V6 = "D613-6 v.LEGIARTI000052218747 (identical in S8 and S9)"; V7 = "D756-5 v.LEGIARTI000034726710 (identical in S8 and S9)"
S = []; n = [0]
def add(rule, art, quote, claim, check=None, status=None, law="S9", note="M2"):
    n[0] += 1; d = {"id": f"M2-{n[0]:02d}", "rule": rule, "article": art, "quote": quote, "claim": claim, "note": note, "law": law}
    if check: d["check"] = check
    else: d["status"] = status
    S.append(d)
def ck(rule, s, exp, tol=0.001): return {"rule": rule, "situation": s, "expect": exp, "tolerance": tol}
# --- new text, créations 2026 (G4 expected FAIL on the first ones)
add(EX + " . taux", "D131-6-1", q_quart, V9 + ": II, revenu <= 3/4 PSS -> exoneration = a quarter of the contributions => rate 25 % (création 01/01/2026, R 20 000, 01/07/2026; PSS 2026 48 060).", ck(EX + " . taux", N26_20, 25))
add(EX + " . taux", "D131-6-1", q_quart, V9 + ": II, R = 36 045 = exactly 3/4 of PSS 48 060 -> still the quarter => 25 %.", ck(EX + " . taux", sit("01/01/2026", "01/07/2026", 36045), 25))
add(EX + " . taux", "D131-6-1", q_form, V9 + ": II formula 0,25 E/0,25 PSS×(PSS−R) = E×(PSS−R)/PSS; at R = 87,5 % PSS (42 052,5) => 12,5 % of E (library: 12,5 % of the contributions at R).", ck(EX + " . taux", N26_42, 12.5))
add(EX + " . taux", "D131-6-1", q_form, V9 + ": II formula gives 0 at R >= PSS (R 60 000 > 48 060) => 0 % (unchanged).", ck(EX + " . taux", N26_60, 0))
add(IND + " . retraite de base", "D131-6-1", q_quart, V9 + ": vieillesse de base contribution for création 2026 at R 20 000 = 3/4 of the full 3 550 €/an (engine without ACRE) = 2 662,5 €/an.", ck(IND + " . retraite de base", N26_20, 2662.5, 1))
add(IND + " . invalidité et décès", "D131-6-1", q_quart, V9 + ": invalidité-décès for création 2026 at R 20 000 = 3/4 x 260 = 195 €/an.", ck(IND + " . invalidité et décès", N26_20, 195, 1))
add(IND + " . indemnités journalières maladie", "D131-6-1", q_quart, V9 + ": IJ maladie (part of the maladie-maternité contributions) for création 2026 at R 20 000 = 3/4 x 100 = 75 €/an.", ck(IND + " . indemnités journalières maladie", N26_20, 75, 1))
add(IND + " . cotisations", "D131-6-1", q_quart, V9 + ": total cotisations for création 2026 at R 20 000 = 1 400 (retraite complémentaire, not exonerated) + 2 662,5 + 195 + 75 = 4 332,5 €/an (G4: 1 400).", ck(IND + " . cotisations", N26_20, 4332.5, 3))
add(EX, "D131-6-1", q_E, V9 + ": E = contributions due for a revenue equal to 3/4 PSS; the library applies the rate to the contributions at R (pre-existing structural deviation, unchanged by the 2026 text) - no check.", status="INFERRED")
# --- old text still governs créations before 2026 (both snapshots expected VERIFIED)
add(EX + " . taux", "D131-6-1", q8_total, V8 + ": création 01/07/2025 still in its 12 months on 01/07/2026, R 20 000 <= 3/4 PSS -> total exoneration => 100 %.", ck(EX + " . taux", O25_20, 100), law="S8")
add(EX + " . taux", "D131-6-1", q8_form, V8 + ": création 01/07/2025, R = 87,5 % PSS 2026 -> E/0,25 PSS × (PSS-R) = 50 % of E (library: 50 % at R).", ck(EX + " . taux", O25_42, 50), law="S8")
add(EX + " . taux", "D131-6-1", q8_total, V8 + ": 2025 control, création 01/01/2025, R 20 000 on 01/07/2025 (PSS 2025 47 100) => 100 %.", ck(EX + " . taux", C25_20, 100), law="S8")
add(EX + " . taux", "D131-6-1", q8_form, V8 + ": 2025 control, R = 41 212,5 = 87,5 % of PSS 2025 => 50 %.", ck(EX + " . taux", C25_41, 50), law="S8")
add(IND + " . cotisations", "D131-6-1", q8_total, V8 + ": 2025 control, création 2025, R 20 000: only retraite complémentaire remains => 1 400 €/an.", ck(IND + " . cotisations", C25_20, 1400, 1), law="S8")
# --- unchanged / non-numeric parts
add("dirigeant . exonérations . ACRE", "D131-6-1", q_I, V9 + ": I unchanged - 12 months from affiliation; the rule's applicability (durée d'activité en début d'année < 1 an) is unchanged; textual link only.", status="INFERRED")
add(EX + " . prorata sur l'année", "D131-6-1", q_III, V9 + ": III - annual PSS at 1 January, prorated for an affiliation shorter than a year (marins sentence deleted, irrelevant here); prorata rule unchanged; textual link.", status="INFERRED")
add("dirigeant . exonérations . ACRE", "D131-6-1", q_60, V9 + ": IV new - the Acre request (II of L. 131-6-4) must be filed within 60 days of the start of activity; not modelled (no date-of-request input; L. 131-6-4 outside the set).", status="UNKNOWN")
add(AE + " . éligible à l'ACRE", "D131-6-1", q_60, V9 + ": IV 60-day request deadline concerns the micro-entrepreneur request; the eligibility rule has no request-date input; L. 131-6-4 outside the set - abstain.", status="UNKNOWN")
add(EX + " . taux", "D131-6-1", q_1365, V9 + ": II applies 'sans préjudice' of L. 131-6-5, which is outside the bounded set - its effect cannot be assessed; abstain.", status="UNKNOWN")
add(AE + " . Acre . taux Acre", "D131-6-1", q_quart, V9 + ": the micro-social Acre rate (50 % in the library) is set by another article outside the set; whether the 2026 'quart' has a micro-social counterpart cannot be checked here - abstain.", status="UNKNOWN")
# --- AE side on G4 x S9 (D613-4/D613-6 unchanged S8->S9; G4 transposed the 2026 values; DROM BNC 2026 still on the mort-né basis)
BNC = {"date": "01/01/2026", "salarié": "non", "entreprise . catégorie juridique": "'EI'", "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois", "entreprise . date de création": "01/01/2021", "dirigeant . exonérations . ACRE": "non", "établissement . commune . département . outre-mer": "non", "entreprise . activité . nature": "'libérale'", "entreprise . activité . nature . libérale . réglementée": "non"}
CIP = dict(BNC, **{"entreprise . activité . nature . libérale . réglementée": "oui", "entreprise . date de création": "01/01/2019"})
BIC = dict(BNC, **{"entreprise . activité . nature": "'artisanale'", "entreprise . activités . service ou vente": "'service'"}); BIC.pop("entreprise . activité . nature . libérale . réglementée")
PER = {"P1": {"entreprise . durée d'activité": "300 jour", "entreprise . durée d'activité . trimestres civils": "4 trimestre civil", "entreprise . durée d'activité . années civiles": "1 année civile"},
       "P2": {"entreprise . durée d'activité": "900 jour", "entreprise . durée d'activité . trimestres civils": "10 trimestre civil", "entreprise . durée d'activité . années civiles": "3 année civile"},
       "P3": {"entreprise . durée d'activité": "1500 jour", "entreprise . durée d'activité . trimestres civils": "20 trimestre civil", "entreprise . durée d'activité . années civiles": "5 année civile"}}
def drom(b, per): s = dict(b, **PER[per]); s["établissement . commune . département . outre-mer"] = "oui"; return s
add(C + " . service BNC . taux", "D613-4", qe, V4 + ": e) BNC 25,6 % on 01/01/2026 - transposed by G4 commit 88cb2ce9 (2026-01-08).", ck(C + " . service BNC . taux", BNC, 25.6))
add(C + " . service BNC . répartition . maladie-maternité . taux de répartition", "D613-6", q6e, V6 + ": e) 2,60 + 1,50 = 4,10 % on 01/01/2026 (G4).", ck(C + " . service BNC . répartition . maladie-maternité . taux de répartition", BNC, 4.1))
add(C + " . service BIC . répartition . maladie-maternité . taux de répartition", "D613-6", q6ad, V6 + ": a/d 8,80 + 1,25 = 10,05 % on 01/01/2026 (G4).", ck(C + " . service BIC . répartition . maladie-maternité . taux de répartition", BIC, 10.05))
add(C + " . service BNC Cipav . répartition . maladie-maternité . taux de répartition", "D613-6", q6b, V6 + ": b) 10,60 + 0,80 = 11,40 % on 01/01/2026 (G4).", ck(C + " . service BNC Cipav . répartition . maladie-maternité . taux de répartition", CIP, 11.4))
add(DR + " . taux CIPAV", "D756-5", q7a, V7 + " a) 1/3 of 23,2 % (" + V4 + " b) = 7,8 % - fixed by G4 commit 55470937 (2026-01-08).", ck(DR + " . taux CIPAV", drom(CIP, "P1"), 7.8))
add(DR + " . taux service BNC", "D756-5", q7a, V7 + " a) 1/6 of 25,6 % (" + V4 + " e) = 4,27 -> 4,3 % on 01/01/2026; G4 still 4,4 % (mort-né 26,1 % basis).", ck(DR + " . taux service BNC", drom(BNC, "P1"), 4.3))
add(DR + " . taux service BNC", "D756-5", q7b, V7 + " b) 1/2 of 25,6 % = 12,8 %; G4 13,1 %.", ck(DR + " . taux service BNC", drom(BNC, "P2"), 12.8))
add(DR + " . taux service BNC", "D756-5", q7c, V7 + " c) 2/3 of 25,6 % = 17,07 -> 17,1 %; G4 17,4 %.", ck(DR + " . taux service BNC", drom(BNC, "P3"), 17.1))
for l in S: assert l["quote"] in (S9 if l["law"] == "S9" else S8)[l["article"]]["text"], l["id"]
json.dump(S, open("work/sophon/links_M2.json", "w"), ensure_ascii=False, indent=1); print("spec ok", len(S))
for k, v in [("q_I", q_I), ("q_quart", q_quart), ("q_form", q_form), ("q_1365", q_1365), ("q_60", q_60[:90] + "..."), ("q8_total", q8_total[-80:]), ("q8_form", q8_form)]: print(k, "=", v)
