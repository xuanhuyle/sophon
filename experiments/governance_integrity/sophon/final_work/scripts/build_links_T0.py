#!/usr/bin/env python3
"""Build the T0 link specification (work/sophon/links_T0.json). Quotes are extracted from the real
article text by a tolerant regex so that they are exact substrings by construction."""
import json, re, sys
ART = json.load(open("inputs/law/S0_legi-data-2.360.0/articles.json"))["articles"]
def text(num): return ART[num][0]["text"]
def rx(lit):
    """literal -> regex: apostrophes, multiplication signs and spaces are made flexible"""
    out = ""
    for ch in lit:
        if ch in "'’": out += "[’']"
        elif ch in "×x": out += "[×x]"
        elif ch == " ": out += r"\s+"
        else: out += re.escape(ch)
    return out
def quote(num, lit):
    m = re.search(rx(lit), text(num), re.S)
    if not m: sys.exit(f"QUOTE NOT FOUND in {num}: {lit[:80]}")
    return m.group(0)
AE = {"date":"01/05/2024","salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur":"oui","entreprise . activité . nature":"'libérale'","dirigeant . auto-entrepreneur . chiffre d'affaires":"1000 €/mois","entreprise . date de création":"01/01/2021","dirigeant . exonérations . ACRE":"non","établissement . commune . département . outre-mer":"non"}
def ae(**kw):
    s = dict(AE); s.update(kw); return s
REG = {"entreprise . activité . nature . libérale . réglementée":"oui"}
OM = {"établissement . commune . département . outre-mer":"oui"}
def drom(q, y, reg=False):
    s = ae(**OM); s["entreprise . durée d'activité . trimestres civils"] = f"{q} trimestre civil"; s["entreprise . durée d'activité . années civiles"] = f"{y} année civile"
    if reg: s.update(REG)
    return s
def ae_acre(days, created):
    s = ae(); s["dirigeant . exonérations . ACRE"] = "oui"; s["entreprise . date de création"] = created; s["entreprise . durée d'activité"] = f"{days} jour"; return s
def ind(revenu, created="01/01/2021", date="01/07/2024"):
    return {"date":date,"salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"non","entreprise . activité . nature":"'commerciale'","entreprise . imposition":"'IR'","dirigeant . indépendant . revenu professionnel":revenu,"entreprise . date de création":created}
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"
D = "dirigeant . auto-entrepreneur . DROM"
I = "dirigeant . indépendant . cotisations et contributions"
L = []
def add(id, rule, article, q, claim, check=None, status=None, note=None, confidence="medium", answer_status=None, expected_display=None):
    L.append({"id":id,"rule":rule,"article":article,"quote":quote(article,q),"claim":claim,"check":check,"status":status,"note":note,"confidence":confidence,"answer_status":answer_status,"expected_display":expected_display})
def chk(rule, situation, expect, tol=0.001): return {"rule":rule,"situation":situation,"expect":expect,"tolerance":tol}

# ---------- D613-4 : global rates ----------
Qa="79 828 euros 71 % 23 150 euros 12,3 %"; Qb="11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 21,2 %"
Qc="meublés de tourisme, définis conformément à l'article L. 324-1 du code du tourisme 29 230 euros 87 % 3 800 euros 6 %"
Qd="2° du 1 de l'article 50-0 du code général des impôt 46 300 euros 50 % 23 150 euros 21,2 %"; Qe="10 000 euros 34 % 6 600 euros 21,1 %"
add("D613-4_e_BNC", C+" . taux service BNC", "D613-4", Qe, "Category e) (L631-1 + CGI 102 ter, BNC): global contribution rate 21,1 %.", chk(C+" . taux service BNC", ae(), 21.1), confidence="high")
add("D613-4_d_BIC", C+" . taux service BIC", "D613-4", Qd, "Category d) (CGI 50-0 1 2°, prestations de service BIC): global rate 21,2 %.", chk(C+" . taux service BIC", ae(), 21.2), confidence="high")
add("D613-4_a_vente", C+" . taux vente restauration hébergement", "D613-4", Qa, "Category a) (CGI 50-0 1 1°, vente/restauration/hébergement): global rate 12,3 %.", chk(C+" . taux vente restauration hébergement", ae(), 12.3), confidence="high")
add("D613-4_b_CIPAV_taux", C+" . cotisations CIPAV . taux", "D613-4", Qb, "Category b) (section professionnelle 11° R641-1 = CIPAV): global rate 21,2 % (rate constant).", chk(C+" . cotisations CIPAV . taux", ae(**REG), 21.2), confidence="high")
add("D613-4_e_montant", C, "D613-4", Qe, "BNC AE with CA 12 000 €/an pays 12 000 × 21,1 % = 2 532 €/an.", chk(C, ae(), 2532), confidence="high")
add("D613-4_b_CIPAV_montant_created2021", C, "D613-4", Qb, "CIPAV AE with CA 12 000 €/an should pay 12 000 × 21,2 % = 2 544 €/an; engine returns 1 452 (12,1 %) for a company created on/after 01/04/2020 even with Acre = non (the Acre CIPAV rate replacement leaks).", chk(C, ae(**REG), 2544), confidence="high", answer_status="FAILED")
add("D613-4_b_CIPAV_montant_created2019", C, "D613-4", Qb, "Same CIPAV AE created 01/01/2019 (before 01/04/2020): 2 544 €/an = 21,2 % as required.", chk(C, ae(**REG, **{"entreprise . date de création":"01/01/2019"}), 2544), confidence="high")
add("D613-4_c_meubles_tourisme", C, "D613-4", Qc, "Category c) meublés de tourisme: 6 % global rate — no rule distinguishes this category; not implemented.", status="UNKNOWN", note="not observable through any rule at G0", confidence="high")
# ---------- L613-7 ----------
add("L613-7_structure", C, "L613-7", "en appliquant au montant de leur chiffre d'affaires ou de leurs recettes effectivement réalisés le mois ou le trimestre précédent un taux global fixé par décret pour chaque catégorie d'activité", "AE contributions = turnover × a global rate per activity category (rates in D613-4).", status="INFERRED", confidence="high")
add("L613-7_taux_different_DROM", D, "L613-7", "Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité sociale", "The DROM reduced rates are a 'different global rate' for exemption periods (decree D756-5).", status="INFERRED", confidence="medium")
add("L613-7_taux_different_ACRE", "dirigeant . exonérations . ACRE", "L613-7", "Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité sociale", "AE Acre = reduced global rate (library: 50 % of the rate, 12,1 % for CIPAV); the decree fixing these reduced rates is NOT in the bounded set, so the 50 %/12,1 % values cannot be verified.", status="INFERRED", confidence="low")
add("L613-7_abattement_34", "entreprise . imposition . régime . micro-entreprise . revenu abattu", "L613-7", "après application d'un taux d'abattement de 71 % lorsqu'elles relèvent du 1° du 1 de l'article 50-0 du code général des impôts, de 50 % lorsqu'elles relèvent du 2° du même 1 et de 34 % lorsqu'elles relèvent de l'article 102 ter du même code", "34 % abattement for BNC (102 ter): 12 000 × (1 − 0,34) = 7 920 €/an (rule is the fiscal abattement; the article uses it for benefits).", chk("entreprise . imposition . régime . micro-entreprise . revenu abattu", ae(), 7920), confidence="medium")
add("L613-7_cotisations_minimales_option", C, "L613-7", "peuvent demander que leurs cotisations ne soient pas inférieures au montant minimal de cotisations de sécurité sociale", "Option for AE to pay at least the minimum contributions — not implemented.", status="UNKNOWN", confidence="high")
# ---------- D756-5 : DROM ----------
Q5a="a) 1/6 pour les travailleurs indépendants mentionnés au 2° de l'article L. 611-1 et 1/3 dans les autres cas, jusqu'à la fin du septième trimestre civil qui suit celui au cours duquel intervient la date d'effet de l'affiliation"
Q5b="b) 1/2 pour la période qui court entre la fin de la période mentionnée au a et la fin de la troisième année civile d'activité"
Q5c="c) 2/3 à compter de la quatrième année civile d'activité"
Q5r="après arrondi au dixième de pour cent supérieur, à une fraction des taux prévus par l'article D. 131-6-1"
for rule, base, p1, p2, p3, reg in [(D+" . taux service BNC", 21.1, 3.6, 10.6, 14.1, False), (D+" . service BIC", 21.2, 3.6, 10.6, 14.2, False), (D+" . taux vente restauration hébergement", 12.3, 2.1, 6.2, 8.2, False), (D+" . taux CIPAV", 21.2, 7.1, 10.6, 14.2, True)]:
    short = rule.split(" . ")[-1]; frac1 = "1/3" if reg else "1/6"
    add(f"D756-5_a_{short}", rule, "D756-5", Q5a, f"First period (8 civil quarters incl. the affiliation quarter): {frac1} × {base} % rounded up to 0,1 → {p1} %.", chk(rule, drom(8, 2, reg), p1))
    add(f"D756-5_b_{short}", rule, "D756-5", Q5b, f"Second period (9th quarter to end of 3rd civil year): 1/2 × {base} % rounded up → {p2} %.", chk(rule, drom(9, 3, reg), p2))
    add(f"D756-5_c_{short}", rule, "D756-5", Q5c, f"From the 4th civil year: 2/3 × {base} % rounded up → {p3} %.", chk(rule, drom(16, 4, reg), p3))
add("D756-5_arrondi_base", D, "D756-5", Q5r, "Rounding up to the next tenth; the library applies the fractions to the D613-4 rates although the article still cites D. 131-6-1 (stale cross-reference, D131-6-1 now holds the Acre rules).", status="INFERRED", confidence="medium")
add("D756-5_II_plafond_CA", D, "D756-5", "L'exonération prévue au I est calculée sur le chiffre d'affaires ou les recettes dans la limite du seuil fixé par les articles 50-0 et 102 ter du code général des impôts", "DROM reduced rates only up to the micro thresholds — no cap implemented.", status="UNKNOWN", confidence="high")
# ---------- D131-6-1 : Acre ----------
Qdur="La durée de l'exonération des cotisations dues par les personnes bénéficiant de l'aide à la création et à la reprise d'entreprise prévue à l'article L. 131-6-4 est de douze mois"
Qtot="Lorsque le revenu ou la rémunération est inférieur ou égal aux trois quarts de la valeur du plafond mentionné à l'article L. 241-3, l'exonération applicable pendant la période mentionnée au I correspond au montant total des cotisations dues aux régimes d'assurance maladie, maternité, veuvage, vieillesse de base, invalidité et décès et d'allocations familiales"
Qform="Montant de l'exonération = E/0,25 PSS × (PSS-R)"
QE="E est le montant total des cotisations dues aux régimes d'assurance maladie, maternité, veuvage, vieillesse de base, invalidité et décès et d'allocations familiales mentionnées au 1° ou au 2° du II de l'article L. 131-6-4 dues pour un revenu ou une rémunération égal aux trois quarts de la valeur du plafond"
Qsup="supérieur au trois quarts de la valeur du plafond mentionné à l'article L. 241-3 mais inférieur ou égal à la valeur de ce plafond"
Qpro="En cas de période d'affiliation inférieure à une année, cette valeur est réduite au prorata de la durée d'affiliation"
QPSS="La valeur du plafond de la sécurité sociale mentionné à la présente section est la valeur annuelle de ce plafond, tel que prévu à l'article L. 241-3, en vigueur au 1er janvier de l'année au titre de laquelle les cotisations sont dues"
add("D131-6-1_12mois_prorata", I+" . exonérations . ACRE . prorata sur l'année", "D131-6-1", Qdur, "12 months: company created 01/07/2023 → 50 % of year 2024 is still under Acre.", chk(I+" . exonérations . ACRE . prorata sur l'année", ind("20000 €/an", "01/07/2023"), 50), confidence="high")
add("D131-6-1_12mois_AE_fin", C+" . taux service BNC", "D131-6-1", Qdur, "AE with Acre after 12 months (durée 400 jours): reduced rate no longer applies, BNC rate back to 21,1 % (D613-4).", chk(C+" . taux service BNC", ae_acre(400, "01/04/2023"), 21.1), confidence="medium")
add("D131-6-1_12mois_AE_debut", C+" . taux service BNC", "D131-6-1", Qdur, "AE with Acre within 12 months (270 jours): rate reduced (observed 10,6 % = 50 % × 21,1 % rounded); the 50 % factor is not in the bounded set so the value is not verifiable here.", status="INFERRED", confidence="low")
add("D131-6-1_total_taux", I+" . exonérations . ACRE . taux", "D131-6-1", Qtot, "Revenue ≤ 3/4 PSS → exemption = 100 % of the listed contributions (taux 100 %).", chk(I+" . exonérations . ACRE . taux", ind("20000 €/an", "01/01/2024"), 100), confidence="high")
add("D131-6-1_total_retraite_base_0", I+" . retraite de base", "D131-6-1", Qtot, "Vieillesse de base fully exempted at 20 000 €/an (≤ 3/4 PSS) with Acre → 0.", chk(I+" . retraite de base", ind("20000 €/an", "01/01/2024"), 0), confidence="high")
add("D131-6-1_total_maladie_0", I+" . maladie", "D131-6-1", Qtot, "Maladie-maternité fully exempted at 20 000 €/an with Acre → 0.", chk(I+" . maladie", ind("20000 €/an", "01/01/2024"), 0), confidence="high")
add("D131-6-1_total_invalidite_0", I+" . invalidité et décès", "D131-6-1", Qtot, "Invalidité-décès fully exempted at 20 000 €/an with Acre → 0.", chk(I+" . invalidité et décès", ind("20000 €/an", "01/01/2024"), 0), confidence="high")
add("D131-6-1_RC_non_exoneree", I+" . retraite complémentaire", "D131-6-1", Qtot, "Retraite complémentaire is not in the exempted list and is indeed not reduced (observed 1 400 €/an at 20 000 with Acre; the 7 % RC rate is outside the bounded set).", status="INFERRED", confidence="medium")
add("D131-6-1_formule_50", I+" . exonérations . ACRE . taux", "D131-6-1", Qform, "Degressive zone: R = 87,5 % PSS (40 572 €/an) → (PSS − R)/(0,25 PSS) = 50 %.", chk(I+" . exonérations . ACRE . taux", ind("40572 €/an", "01/01/2024"), 50), confidence="high")
add("D131-6-1_formule_0_au_dessus_PSS", I+" . exonérations . ACRE . taux", "D131-6-1", Qsup, "Formula bounded at R = PSS where it gives 0; above the PSS (50 000 €/an) the engine gives 0 %.", chk(I+" . exonérations . ACRE . taux", ind("50000 €/an", "01/01/2024"), 0), confidence="medium")
add("D131-6-1_E_base_deviation", I+" . exonérations . ACRE . maladie", "D131-6-1", QE, "E is the contribution due at 3/4 PSS (fixed), but the engine applies the fraction to the contribution due at R: at R = 87,5 % PSS the Acre maladie exemption observed is 1 114 = 50 % × 2 228 (contribution at R), whereas the article requires 50 % × E (contribution at 34 776 €/an, smaller because the maladie rate is increasing). Executable deviation, no single expected number asserted.", status="INFERRED", confidence="low", answer_status="FAILED")
add("D131-6-1_PSS_prorata", I+" . PSS proratisé", "D131-6-1", Qpro, "PSS prorated by affiliation duration: created 01/07/2024 → 184 jours/365 → 23 375 €/an (article silent on the day-count; 184/366 would give 23 311).", status="INFERRED", confidence="medium")
add("D131-6-1_PSS_annuel", I+" . PSS proratisé", "D131-6-1", QPSS, "Annual PSS in force on 1 January of the year (library value 46 368 €/an for 2024; L241-3 is outside the bounded set).", status="INFERRED", confidence="medium")
# ---------- D621-2 : maladie reduced rate ----------
Q21="Lorsque le montant annuel de leur revenu d'activité est inférieur à 40 % de la valeur annuelle du plafond mentionné au premier alinéa de l'article L. 241-3, le taux prévu au I est égal à 0,50 %"
Q22="Taux = { [(T2-T1)/ (0,2 × PSS)] × [r-(0,4 × PSS)] } + T1 Où : -T2 est égal à 4,5 % ; -T1 est égal à 0,5 %"
Q23="Taux = { [(T3-T2)/ (0,5 × PSS)] × [r-(0,6 × PSS)] } + T2 Où : -T3 est égal au taux de cotisation fixé au I de l'article D. 621-1"
Q2110="fait l'objet d'une réduction lorsque le montant annuel de leur revenu d'activité est inférieur à 110 % de la valeur annuelle du plafond mentionné au premier alinéa de l'article L. 241-3"
TP = I+" . maladie . taux progressif"
add("D621-2_1_0.5", TP, "D621-2", Q21, "r = 9 000 €/an < 40 % PSS → maladie rate 0,50 %.", chk(TP, ind("9000 €/an"), 0.5), confidence="high")
add("D621-2_2_mid", TP, "D621-2", Q22, "r = 50 % PSS (23 184 €/an) → (4,5−0,5)/0,2 × 0,1 + 0,5 = 2,5 %.", chk(TP, ind("23184 €/an"), 2.5), confidence="high")
add("D621-2_2_T2", TP, "D621-2", Q22, "r = 60 % PSS (27 821 €/an) → T2 = 4,5 %.", chk(TP, ind("27821 €/an"), 4.5), confidence="high")
add("D621-2_3_T3_hors_set", TP, "D621-2", Q23, "60–110 % PSS: linear from 4,5 % to T3 (rate of D621-1, outside the bounded set); library uses T3 = 7,20 % (observed 5,99 % at 87,5 % PSS, 7,2 % above 110 %).", status="INFERRED", confidence="medium")
add("D621-2_seuil_110", TP, "D621-2", Q2110, "No reduction above 110 % PSS: engine gives the full rate 7,20 % at 60 000 €/an; the full rate itself (D621-1) is outside the bounded set.", status="UNKNOWN", confidence="medium")
# ---------- D632-1 : invalidité-décès ----------
Qcap="est assise sur les revenus définis par l'article L. 131-6 , dans la limite du plafond de la sécurité sociale"
Qfloor="La cotisation annuelle ne peut être calculée sur une assiette inférieure à 11,5 % de la valeur du plafond de la sécurité sociale"
IA = I+" . invalidité et décès . assiette"
add("D632-1_plafond", IA, "D632-1", Qcap, "Base capped at the PSS: revenu 60 000 €/an → assiette = PSS (engine returns 3 864 €/mois = 46 368 €/an; PSS value from the library, L241-3 outside the set).", chk(IA, ind("60000 €/an"), 3864), confidence="medium")
add("D632-1_plancher_2022", IA, "D632-1", Qfloor, "Floor 11,5 % PSS: 2022, revenu 0 → 11,5 % × 41 136 = 4 730,64 → 4 731 €/an.", chk(IA, ind("0 €/an", date="01/07/2022"), 4731), confidence="high")
add("D632-1_plancher_2024", IA, "D632-1", Qfloor, "Floor 11,5 % PSS: 2024, revenu 0 → 11,5 % × 46 368 = 5 332 €/an expected; engine gives 5 243 (450 h × SMIC, the retraite floor) since the 2023 change of 'assiette minimale . retraite'.", chk(IA, ind("0 €/an"), 5332, tol=1), confidence="high", answer_status="FAILED")
# ---------- D633-3 : retraite de base ----------
Q33I="Le taux des cotisations assises sur le revenu d'activité dans la limite du plafond est fixé à 17,15 %"
Q33II="Le taux des cotisations assises sur la totalité du revenu d'activité est fixé à 0,60 %"
RB = I+" . retraite de base"
add("D633-3_I_II_sous_plafond", RB, "D633-3", Q33I, "r = 9 000 €/an ≤ PSS: (17,15 % + 0,60 %) × 9 000 = 1 597,5 → 1 598 €/an.", chk(RB, ind("9000 €/an"), 1598), confidence="high")
add("D633-3_II_au_dessus", RB, "D633-3", Q33II, "r = 60 000 €/an > PSS: 17,15 % × 46 368 + 0,60 % × 60 000 = 8 312 €/an.", chk(RB, ind("60000 €/an"), 8312), confidence="high")
add("D633-3_taux_combine", RB+" . taux", "D633-3", Q33I, "Library single first-tranche rate 17,75 % = 17,15 % (I) + 0,60 % (II); the 0,6 % second tranche carries II above the PSS.", status="INFERRED", confidence="high")
# ---------- D613-6 / D613-5 / L131-6 / L136-3 : watch links ----------
add("D613-6_repartition_e", C, "D613-6", "Cotisation d'assurance maladie maternité 3,90 % Cotisation d'assurance invalidité-décès 4,10 % Cotisations d'assurance vieillesse de base mentionnées aux I et II de l'article D. 633-3 du code de la sécurité sociale 55,50 % Contribution sociale généralisée et contribution pour le remboursement de la dette sociale 36,50 %", "Split of the AE global amount between branches (category e) — no rule splits the AE forfait; not implemented.", status="UNKNOWN", confidence="high")
add("D613-5_conjoint_AE", "dirigeant . indépendant . conjoint collaborateur . cotisations", "D613-5", "Le pourcentage mentionné au premier alinéa est fixé à 58 % pour les conjoints collaborateurs des personnes des travailleurs indépendants mentionnés à l'article L. 631-1 et à 46 % pour les conjoints collaborateurs des professions libérales", "Conjoint collaborateur of an AE (58 %/46 % of turnover × D613-4 rates): the only conjoint rules are for classic indépendants; for an AE situation the rule evaluates to null.", status="UNKNOWN", confidence="high")
add("L131-6_assiette_2025", "dirigeant . indépendant . assiette des cotisations", "L131-6", "Les cotisations de sécurité sociale dues par les travailleurs indépendants non agricoles ne relevant pas du dispositif prévu à l'article L. 613-7 sont assises sur l'assiette définie à l'article L. 136-3", "Text in force since 2023-12-28 (applies to periods from 2025-01-01 per nota): unified base = L136-3 base. G0 implements the pre-2025 base (revenu professionnel + Madelin déductibles) whose text version is not in the snapshot → abstain.", status="UNKNOWN", confidence="medium")
add("L136-3_abattement_26", I+" . CSG-CRDS . assiette", "L136-3", "L'assiette résultant de l'application des I et II du présent article fait l'objet d'un abattement de 26 %", "26 % abattement on the CSG/cotisations base (periods from 2025-01-01 per nota) — not implemented at G0; G0 CSG base = revenu + cotisations (old regime, text not in snapshot).", status="UNKNOWN", confidence="medium")
json.dump(L, open("work/sophon/links_T0.json","w"), ensure_ascii=False, indent=1)
print("links built:", len(L))
