"""M0 link spec (law S7 x rules G3). Quotes are exact substrings of the S7 texts (asserted). Writes work/sophon/links_M0.json."""
import json
S7={a["num"]:a for lst in json.load(open("inputs/law/S7_legi-data-2.469.0/articles.json"))["articles"].values() for a in lst}
C="dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"; DR="dirigeant . auto-entrepreneur . DROM"
D="01/07/2025"
P={"date":D,"salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur . chiffre d'affaires":"1000 €/mois","entreprise . date de création":"01/01/2021","dirigeant . exonérations . ACRE":"non","établissement . commune . département . outre-mer":"non"}
BNC=dict(P,**{"entreprise . activité . nature":"'libérale'","entreprise . activité . nature . libérale . réglementée":"non"})
CIP=dict(P,**{"entreprise . activité . nature":"'libérale'","entreprise . activité . nature . libérale . réglementée":"oui","entreprise . date de création":"01/01/2019"})
BIC=dict(P,**{"entreprise . activité . nature":"'artisanale'","entreprise . activités . service ou vente":"'service'"})
VEN=dict(P,**{"entreprise . activité . nature":"'commerciale'","entreprise . activités . service ou vente":"'vente'"})
PER={"P1":{"entreprise . durée d'activité":"300 jour","entreprise . durée d'activité . trimestres civils":"4 trimestre civil","entreprise . durée d'activité . années civiles":"1 année civile"},
     "P2":{"entreprise . durée d'activité":"900 jour","entreprise . durée d'activité . trimestres civils":"10 trimestre civil","entreprise . durée d'activité . années civiles":"3 année civile"},
     "P3":{"entreprise . durée d'activité":"1500 jour","entreprise . durée d'activité . trimestres civils":"20 trimestre civil","entreprise . durée d'activité . années civiles":"5 année civile"}}
def drom(base,per): s=dict(base,**PER[per]); s["établissement . commune . département . outre-mer"]="oui"; return s
qa="79 828 euros 71 % 23 150 euros 12,3 %"; qb="11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 23,2 %"; qc="29 230 euros 87 % 3 800 euros 6 %"
qd="2° du 1 de l'article 50-0 du code général des impôt 46 300 euros 50 % 23 150 euros 21,2 %"; qe="10 000 euros 34 % 6 600 euros 24,6 %"
q6e="Cotisation d'assurance maladie maternité 3,40 % Cotisation d'assurance invalidité-décès 3,50 % Cotisations d'assurance vieillesse de base mentionnées aux I et II de l'article D. 633-3 du code de la sécurité sociale 47,60 % Cotisation d'assurance vieillesse complémentaire 13,00 % Contribution sociale généralisée et contribution pour le remboursement de la dette sociale 32,50 %"
q6ad="Cotisation d'assurance maladie-maternité 8,90 % Cotisation d'assurance invalidité-décès 3,10 % Cotisation d'assurance vieillesse de base mentionnée aux I et II de l'article D. 633-3 41,80 % Cotisation d'assurance vieillesse complémentaire 16,50 % Contribution sociale généralisée et contribution pour le remboursement de la dette sociale 29,70 %"
q6b="Cotisation d'assurance maladie maternité mentionnée au premier alinéa de l'article L. 621-1 9,30 % Cotisation de prestations maladie en espèces mentionnée au dernier alinéa de l'article L. 621-2 0,90 % Cotisation d'assurance invalidité décès 1,40 % Cotisation d'assurance vieillesse de base mentionnée au 1° de l'article D. 642-3 23,45 % Cotisation d'assurance vieillesse de base mentionnée au 2° de l'article D. 642-3 5,35 % Cotisation d'assurance vieillesse complémentaire 25,60 % Contribution sociale généralisée et contribution pour le remboursement de la dette sociale 34,00 %"
q7a="après arrondi au dixième de pour cent supérieur, à une fraction des taux prévus par l'article D. 131-6-1 fixée à : a) 1/6 pour les travailleurs indépendants mentionnés au 2° de l'article L. 611-1 et 1/3 dans les autres cas"
q7b="b) 1/2 pour la période qui court entre la fin de la période mentionnée au a et la fin de la troisième année civile d'activité"; q7c="c) 2/3 à compter de la quatrième année civile d'activité"
V4="D613-4 v.LEGIARTI000049624097 (in force 2025-01-01..2026-01-01; current text in S6 and S7)"; V6="D613-6 v.LEGIARTI000049625405 (in force 2025-01-01..2026-01-01; current text in S6 and S7)"; V7="D756-5 v.LEGIARTI000034726710 (unchanged S6->S7)"
AB4="ABSTENTION (M0, S6->S7): the 2026-01-01 version announced as LEGIARTI000049624125 is now MODIFIE_MORT_NE (dateFin 2025-09-10); the new version LEGIARTI000052218738 (VIGUEUR_DIFF from 2026-01-01) has no text in S7 and no modifying text is named in lienModifications. No available text settles the value for dates >= 2026-01-01."
AB6="ABSTENTION (M0, S6->S7): the 2026-01-01 version announced as LEGIARTI000049625445 is now MODIFIE_MORT_NE (dateFin 2025-09-10); the new version LEGIARTI000052218747 (VIGUEUR_DIFF from 2026-01-01) has no text in S7. No available text settles the shares for dates >= 2026-01-01."
def L(i,rule,art,quote,claim,check=None,status=None,note="M0"):
    d={"id":i,"rule":rule,"article":art,"quote":quote,"claim":claim,"note":note}
    if check: d["check"]=check
    else: d["status"]=status
    return d
def ck(rule,sit,exp,tol=0.001): return {"rule":rule,"situation":sit,"expect":exp,"tolerance":tol}
S=[]; n=[0]
def add(rule,art,quote,claim,check=None,status=None):
    n[0]+=1; S.append(L(f"M0-{n[0]:02d}",rule,art,quote,claim,check,status))
# D613-4 2025 rates (text available)
add(C+" . service BNC . taux","D613-4",qe,V4+": e) BNC global rate 24,6 %.",ck(C+" . service BNC . taux",BNC,24.6))
add(C+" . service BIC . taux","D613-4",qd,V4+": d) service BIC global rate 21,2 %.",ck(C+" . service BIC . taux",BIC,21.2))
add(C+" . vente restauration hébergement . taux","D613-4",qa,V4+": a) vente global rate 12,3 %.",ck(C+" . vente restauration hébergement . taux",VEN,12.3))
add(C+" . service BNC Cipav . taux","D613-4",qb,V4+": b) CIPAV (11° R641-1) global rate 23,2 %.",ck(C+" . service BNC Cipav . taux",CIP,23.2))
add(C+" . service BNC","D613-4",qe,V4+": BNC AE, CA 1 000 €/mois -> 246 €/mois.",ck(C+" . service BNC",BNC,246))
add(C,"D613-4",qe,V4+": BNC AE total cotisations 246 €/mois on 1 000 €/mois.",ck(C,BNC,246))
add(C+" . service BIC","D613-4",qd,V4+": service BIC AE, CA 1 000 €/mois -> 212 €/mois.",ck(C+" . service BIC",BIC,212))
add(C+" . vente restauration hébergement","D613-4",qa,V4+": vente AE, CA 1 000 €/mois -> 123 €/mois.",ck(C+" . vente restauration hébergement",VEN,123))
add(C+" . service BNC Cipav","D613-4",qb,V4+": CIPAV AE (created 2019), CA 1 000 €/mois -> 232 €/mois.",ck(C+" . service BNC Cipav",CIP,232))
add(C,"D613-4",qc,V4+": c) meublés de tourisme 6 % - still no rule for this category in G3 (names list has no meublé/tourisme).",status="UNKNOWN")
# D613-6 2025 shares
for s,v in [("maladie-maternité",3.4),("invalidité-décès",3.5),("retraite de base",47.6),("retraite complémentaire",13),("autres contributions",32.5)]:
    add(f"{C} . service BNC . répartition . {s} . taux de répartition","D613-6",q6e,V6+f": e) share {s} = {v} %.",ck(f"{C} . service BNC . répartition . {s} . taux de répartition",BNC,v))
for s,v in [("maladie-maternité",8.9),("invalidité-décès",3.1),("retraite de base",41.8),("retraite complémentaire",16.5),("autres contributions",29.7)]:
    add(f"{C} . service BIC . répartition . {s} . taux de répartition","D613-6",q6ad,V6+f": a/d share {s} = {v} % (service BIC).",ck(f"{C} . service BIC . répartition . {s} . taux de répartition",BIC,v))
add(f"{C} . vente restauration hébergement . répartition . retraite complémentaire . taux de répartition","D613-6",q6ad,V6+": a/d share retraite complémentaire 16,50 % (vente).",ck(f"{C} . vente restauration hébergement . répartition . retraite complémentaire . taux de répartition",VEN,16.5))
for s,v,cl in [("maladie-maternité",10.2,"9,30 % (L621-1) + 0,90 % (L621-2 espèces) = 10,20 % aggregated in one rule"),("invalidité-décès",1.4,"1,40 %"),("retraite de base",28.8,"23,45 % (1° D642-3) + 5,35 % (2° D642-3) = 28,80 % aggregated"),("retraite complémentaire",25.6,"25,60 %"),("autres contributions",34,"34,00 %")]:
    add(f"{C} . service BNC Cipav . répartition . {s} . taux de répartition","D613-6",q6b,V6+f": b) share {s}: {cl}.",ck(f"{C} . service BNC Cipav . répartition . {s} . taux de répartition",CIP,v))
# D756-5 x D613-4 2025 (DROM)
add(DR+" . taux service BNC","D756-5",q7a,V7+" a) 1/6 of 24,6 % = 4,1 % (BNC, first period).",ck(DR+" . taux service BNC",drom(BNC,"P1"),4.1))
add(DR+" . taux service BNC","D756-5",q7b,V7+" b) 1/2 of 24,6 % = 12,3 % (BNC, second period).",ck(DR+" . taux service BNC",drom(BNC,"P2"),12.3))
add(DR+" . taux service BNC","D756-5",q7c,V7+" c) 2/3 of 24,6 % = 16,4 % (BNC, from 4th civil year).",ck(DR+" . taux service BNC",drom(BNC,"P3"),16.4))
add(DR+" . taux service BIC","D756-5",q7a,V7+" a) 1/6 of 21,2 % = 3,53 -> 3,6 % (rounded up to 0,1).",ck(DR+" . taux service BIC",drom(BIC,"P1"),3.6))
add(DR+" . taux vente restauration hébergement","D756-5",q7a,V7+" a) 1/6 of 12,3 % = 2,05 -> 2,1 %.",ck(DR+" . taux vente restauration hébergement",drom(VEN,"P1"),2.1))
add(DR+" . taux CIPAV","D756-5",q7a,V7+" a) 1/3 of 23,2 % (D613-4 b, 2025) = 7,73 -> 7,8 %; G3 still returns 7,1 (1/3 of the superseded 21,2 %). PRE-EXISTING mismatch (since 07/2024), not caused by S6->S7; check expected to FAIL.",ck(DR+" . taux CIPAV",drom(CIP,"P1"),7.8))
add(DR+" . taux CIPAV","D756-5",q7b,V7+" b) 1/2 of 23,2 % = 11,6 %; G3 returns 10,6. Pre-existing mismatch; expected to FAIL.",ck(DR+" . taux CIPAV",drom(CIP,"P2"),11.6))
add(DR+" . taux CIPAV","D756-5",q7c,V7+" c) 2/3 of 23,2 % = 15,47 -> 15,5 %; G3 returns 14,2. Pre-existing mismatch; expected to FAIL.",ck(DR+" . taux CIPAV",drom(CIP,"P3"),15.5))
# abstentions for 2026
add(C+" . service BNC . taux","D613-4",qe,AB4+" G3 carries 'date >= 01/2026: 26.1%' transposed on 2024-08-01 (commit 1d2874c5) from the now mort-ne version; unverifiable.",status="UNKNOWN")
add(C+" . service BNC . répartition","D613-6",q6e,AB6+" G3 carries 2026 shares 3 / 3,25 / 44,85 / 17,7 / 31,20 % from the mort-ne version; unverifiable.",status="UNKNOWN")
add(DR+" . taux service BNC","D756-5",q7a,"ABSTENTION: DROM BNC 2026 values in G3 (4,4 / 13,1 / 17,4 %) are fractions of the unverifiable 26,1 %; D756-5 itself unchanged. "+AB4,status="UNKNOWN")
add(C+" . service BIC . taux","D613-4",qd,AB4+" G3 keeps 21,2 % for 2026 without textual support.",status="UNKNOWN")
add(C+" . vente restauration hébergement . taux","D613-4",qa,AB4+" G3 keeps 12,3 % for 2026 without textual support.",status="UNKNOWN")
add(C+" . service BNC Cipav . taux","D613-4",qb,AB4+" G3 keeps 23,2 % for 2026 without textual support.",status="UNKNOWN")
add("dirigeant . auto-entrepreneur . Acre . taux service BNC","D613-4",qe,"ABSTENTION: the 2026 rounding branch (2 décimales) presupposes the unverifiable 26,1 %; Acre rate article itself outside the bounded set. "+AB4,status="UNKNOWN")
for l in S: assert l["quote"] in S7[l["article"]]["text"], l["id"]
json.dump(S,open("work/sophon/links_M0.json","w"),ensure_ascii=False,indent=1); print("spec ok",len(S))
