"""T1a link spec (law S1 x rules G0). Quotes are exact substrings of the S1 texts (checked here before writing)."""
import json
S1={a["num"]:a for lst in json.load(open("inputs/law/S1_legi-data-2.361.0/articles.json"))["articles"].values() for a in lst}
C="dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"
RCI="protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur"
D="01/06/2024"
P={"date":D,"salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur":"oui","entreprise . activité . nature":"'libérale'","dirigeant . auto-entrepreneur . chiffre d'affaires":"1000 €/mois"}
base=dict(P,**{"entreprise . date de création":"01/01/2021","dirigeant . exonérations . ACRE":"non","établissement . commune . département . outre-mer":"non"})
BNC=dict(base,**{"entreprise . activité . nature . libérale . réglementée":"non"})
CIP21=dict(base,**{"entreprise . activité . nature . libérale . réglementée":"oui"})
CIP19=dict(CIP21,**{"entreprise . date de création":"01/01/2019"})
BIC=dict(base,**{"entreprise . activité . nature":"'artisanale'","entreprise . activités . service ou vente":"'service'"})
VEN=dict(base,**{"entreprise . activité . nature":"'commerciale'","entreprise . activités . service ou vente":"'vente'"})
qa="79 828 euros 71 % 23 150 euros 12,3 %"; qb="11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 21,2 %"
qc="29 230 euros 87 % 3 800 euros 6 %"; qd="2° du 1 de l'article 50-0 du code général des impôt 46 300 euros 50 % 23 150 euros 21,2 %"; qe="10 000 euros 34 % 6 600 euros 21,1 %"
q6="Cotisation d'assurance vieillesse complémentaire 16,50 %"
q6e="Cotisation d'assurance maladie maternité 3,90 % Cotisation d'assurance invalidité-décès 4,10 % Cotisations d'assurance vieillesse de base mentionnées aux I et II de l'article D. 633-3 du code de la sécurité sociale 55,50 % Contribution sociale généralisée et contribution pour le remboursement de la dette sociale 36,50 %"
V4="D613-4 version LEGIARTI000049623867 (Décret n°2024-484 du 30 mai 2024 art. 1, in force 2024-06-01..2024-07-01), text identical in substance to LEGIARTI000046714712"
PEND4="Announced versions without text in S1: LEGIARTI000049624068 (2024-07-01), LEGIARTI000049624097 (2025-01-01), LEGIARTI000049624125 (2026-01-01). The rate for those dates is NOT settled by any text available; the rule keeps its current value beyond 2024-07-01 without textual support -> ABSTAIN (no value proposed)."
PEND6="Announced versions without text in S1: LEGIARTI000049625264 (2024-07-01), LEGIARTI000049625405 (2025-01-01), LEGIARTI000049625445 (2026-01-01) -> split for those dates NOT settled -> ABSTAIN."
def L(i,rule,art,quote,claim,check=None,status=None,note="T1a"):
    d={"id":i,"rule":rule,"article":art,"quote":quote,"claim":claim,"note":note}
    if check: d["check"]=check
    else: d["status"]=status
    return d
def ck(rule,sit,exp,tol=1e-9): return {"rule":rule,"situation":sit,"expect":exp,"tolerance":tol}
spec=[
 L("T1a-01",C+" . taux service BNC","D613-4",qe,V4+": category e) BNC global rate 21,1 % (unchanged).",ck(C+" . taux service BNC",P,21.1)),
 L("T1a-02",C+" . taux service BIC","D613-4",qd,V4+": category d) service BIC global rate 21,2 % (unchanged).",ck(C+" . taux service BIC",P,21.2)),
 L("T1a-03",C+" . taux vente restauration hébergement","D613-4",qa,V4+": category a) vente global rate 12,3 % (unchanged).",ck(C+" . taux vente restauration hébergement",P,12.3)),
 L("T1a-04",C+" . cotisations CIPAV . taux","D613-4",qb,V4+": category b) CIPAV global rate 21,2 % (unchanged).",ck(C+" . cotisations CIPAV . taux",CIP21,21.2)),
 L("T1a-05",C,"D613-4",qe,V4+": BNC AE, CA 12 000 €/an -> 12 000 x 21,1 % = 2 532 €/an.",ck(C,BNC,2532,0.001)),
 L("T1a-06",C,"D613-4",qd,V4+": service BIC AE, CA 12 000 €/an -> 12 000 x 21,2 % = 2 544 €/an.",ck(C,BIC,2544,0.001)),
 L("T1a-07",C,"D613-4",qa,V4+": vente AE, CA 12 000 €/an -> 12 000 x 12,3 % = 1 476 €/an.",ck(C,VEN,1476,0.001)),
 L("T1a-08",C,"D613-4",qb,V4+": CIPAV AE created 2019, CA 12 000 €/an -> 12 000 x 21,2 % = 2 544 €/an.",ck(C,CIP19,2544,0.001)),
 L("T1a-09",C,"D613-4",qb,V4+": CIPAV AE created 2021 should also pay 2 544 €/an; engine returns 1 452 (12,1 %: Acre CIPAV rate replacement leaks with Acre = non). Pre-existing bug (T0 L0006), unrelated to S1; check expected to FAIL.",ck(C,CIP21,2544,0.001)),
 L("T1a-10",C,"D613-4",qc,V4+": category c) meublés de tourisme 6 % global rate - still not implemented (no rule distinguishes this category).",status="UNKNOWN"),
 L("T1a-11",C+" . taux service BNC","D613-4",qe,"ABSTENTION. "+PEND4,status="UNKNOWN"),
 L("T1a-12",C+" . taux service BIC","D613-4",qd,"ABSTENTION. "+PEND4,status="UNKNOWN"),
 L("T1a-13",C+" . taux vente restauration hébergement","D613-4",qa,"ABSTENTION. "+PEND4,status="UNKNOWN"),
 L("T1a-14",C+" . cotisations CIPAV . taux","D613-4",qb,"ABSTENTION. "+PEND4,status="UNKNOWN"),
 L("T1a-15",RCI,"D613-6",q6,"D613-6 version LEGIARTI000049623885 (Décret 2024-484 art. 2, in force 2024-06-01), text identical to LEGIARTI000046714699: a) vente share for complementary pension 16,50 % of the global amount: 12 000 x 12,3 % x 16,5 % = 243,54 €/an; the rule uses the rounded rate 2,03 % -> 243,6 (tolerance 0,3).",ck(RCI,VEN,243.54,0.3)),
 L("T1a-16",RCI,"D613-6",q6,"D613-6 d) service BIC share 16,50 %: 12 000 x 21,2 % x 16,5 % = 419,76 €/an; the rule uses the rounded rate 3,50 % -> 420 (tolerance 0,3).",ck(RCI,BIC,419.76,0.3)),
 L("T1a-17",RCI,"D613-6",q6e,"D613-6 e) (BNC, 102 ter) lists no complementary-pension share -> revenu cotisé RCI = 0 for a BNC AE.",ck(RCI,BNC,0)),
 L("T1a-18",RCI,"D613-6",q6,"ABSTENTION. "+PEND6,status="UNKNOWN"),
 L("T1a-19",C,"D613-6",q6e,"Split of the AE global amount between branches (D613-6) is not implemented as such in the library (only the RCI share is derived); unchanged by S1. "+PEND6,status="UNKNOWN"),
]
for l in spec: assert l["quote"] in S1[l["article"]]["text"], l["id"]
json.dump(spec,open("work/sophon/links_T1a.json","w"),ensure_ascii=False,indent=1); print("spec ok",len(spec))
