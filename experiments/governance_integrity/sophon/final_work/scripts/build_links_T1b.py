"""T1b link spec (law S3 x rules G1 and x proposal P_T1b). Quotes are checked to be exact substrings of the S3 texts."""
import json
S3={a["num"]:a for lst in json.load(open("inputs/law/S3_legi-data-2.381.0/articles.json"))["articles"].values() for a in lst}
T={"dirigeant . régime social":"'indépendant'","entreprise . catégorie juridique":"'EI'","entreprise . imposition":"'IR'","entreprise . activité . nature":"'commerciale'","dirigeant . indépendant . revenu professionnel":"40000 €/an"}
D="01/12/2024"; TR=dict(T,date=D)
def rev(v): return dict(TR,**{"dirigeant . indépendant . revenu professionnel":f"{v} €/an"})
def ass(v,d=D): return dict(T,date=d,**{"dirigeant . indépendant . assiette des cotisations":f"{v} €/an"})
CC="dirigeant . indépendant . cotisations et contributions"; AC="dirigeant . indépendant . assiette des cotisations"; RF=AC+" . réforme assiette 2024"
MT=CC+" . maladie . taux progressif"; RB=CC+" . retraite de base"
Q={ # exact substrings of the S3 texts
 "L131":("L131-6","sont assises sur l'assiette définie à l'article L. 136-3"),
 "L131ded":("L131-6","En sont toutefois déduites les sommes mentionnées aux articles L. 3312-4, L. 3324-5 et L. 3332-27 du code du travail"),
 "q26":("L136-3","fait l'objet d'un abattement de 26 %"),
 "qfloor":("L136-3","ne peut être ni inférieur à un montant plancher, fixé par décret, qui ne peut dépasser le montant mentionné à la dernière phrase de l'article L. 633-1"),
 "qceil":("L136-3","ni supérieur à un montant plafond fixé, également par décret, à une valeur au moins égale au plafond annuel mentionné à l'article L. 241-3"),
 "qI1":("L136-3","sur le montant, hors plus-values et moins-values de long terme, des produits tirés de ces mêmes activités, diminué du montant des charges que l'acquisition de ces produits nécessitent"),
 "d136a":("D136-5","Le montant plancher prévu au III de l'article L. 136-3 est fixé à 1,76 % de la valeur annuelle du plafond de la sécurité sociale"),
 "d136b":("D136-5","Le montant plafond mentionné au III de l'article L. 136-3 est fixé à 130 % de la valeur annuelle du plafond de la sécurité sociale"),
 "m0":("D621-2","inférieur à 20 % de la valeur annuelle du plafond mentionné au premier alinéa de l'article L. 241-3, le taux est nul"),
 "mT1":("D621-2","T1 est égal à 1,5 %"),"mT2":("D621-2","T2 est égal à 4 %"),"mT3":("D621-2","T3 est égal à 6,5 %"),"mT4":("D621-2","T4 est égal à 7,7 %"),"mT5":("D621-2","T5 est égal à 8,5 %"),
 "m3x":("D621-2","fait l'objet d'une réduction lorsque le montant annuel de leur assiette de cotisations est inférieur à trois fois la valeur annuelle du plafond"),
 "ma":("D621-2","a est l'assiette, telle que définie à l'article L. 131-6"),
 "mF3":("D621-2","Taux = { (T3-T2) × [a-(0,6 × PSS)]/ (0,5 × PSS) } + T2"),
 "r1715":("D633-3","Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %"),
 "r072":("D633-3","Le taux des cotisations assises sur la totalité de l'assiette de cotisations est fixé à 0,72 %"),
}
for k,(art,q) in Q.items(): assert q in S3[art]["text"], (k,art)
V={"L131-6":"LEGIARTI000048683707 (in force 2023-12-28)","L136-3":"LEGIARTI000048683641 (in force 2023-12-28)","D136-5":"LEGIARTI000049899286 (in force 2024-07-07, Décret n°2024-688 du 5 juillet 2024 art. 1)","D621-2":"LEGIARTI000049904592 (in force 2024-07-07, Décret n°2024-688 art. 2)","D633-3":"LEGIARTI000049904636 (in force 2024-07-07, Décret n°2024-688 art. 3)"}
PH="[conditional on the PLACEHOLDER pre-abattement line = revenu professionnel + cotisations facultatives déductibles; which income lines enter the base is NOT settled by the texts]"
def L(i,rule,qk,claim,check=None,status=None,note="T1b"):
    art,q=Q[qk]; d={"id":i,"rule":rule,"article":art,"quote":q,"claim":f"{art} {V[art]}: {claim}","note":note}
    if check: d["check"]=check
    else: d["status"]=status
    return d
def ck(rule,sit,exp,tol=1e-9): return {"rule":rule,"situation":sit,"expect":exp,"tolerance":tol}
PSS=46368
# --- links on the proposal copy P_T1b (law S3) ---
P=[
 L("T1b-P01",RF+" . abattement forfaitaire","q26","abattement = 26 % x 40 000 = 10 400 €/an (within floor/ceiling).",ck(RF+" . abattement forfaitaire",TR,10400,0.001)),
 L("T1b-P02",RF+" . abattement forfaitaire","d136a","floor 1,76 % x PASS 46 368 = 816,0768 €/an binds when 26 % x 2 000 = 520 < floor.",ck(RF+" . abattement forfaitaire",rev(2000),816.0768,0.001)),
 L("T1b-P03",RF+" . abattement forfaitaire","d136b","ceiling 130 % x PASS 46 368 = 60 278,4 €/an binds when 26 % x 300 000 = 78 000 > ceiling.",ck(RF+" . abattement forfaitaire",rev(300000),60278.4,0.001)),
 L("T1b-P04",RF+" . plafond annuel","d136a","valeur annuelle du plafond: library PSS 2024 3 864 €/mois = 46 368 €/an (PSS 2025 not in corpus: same value used at 2025 dates).",ck(RF+" . plafond annuel",TR,PSS,0.001)),
 L("T1b-P05",AC,"L131","unified base for contributions = 40 000 - 10 400 = 29 600 €/an "+PH,ck(AC,TR,29600,0.001)),
 L("T1b-P06",CC+" . CSG-CRDS . assiette","q26","CSG-CRDS assessed on the same abated base: 29 600 €/an (G1 added the contributions back: 52 788) "+PH,ck(CC+" . CSG-CRDS . assiette",TR,29600,0.001)),
 L("T1b-P07",AC,"L131","before the decree's in-force date (01/06/2024) the base is unchanged: 40 000 €/an.",ck(AC,dict(T,date="01/06/2024"),40000,0.001)),
 L("T1b-P08",MT,"m0","assiette 10 % PASS (4 636,8) -> rate 0 %.",ck(MT,ass(4636.8),0,0.001)),
 L("T1b-P09",MT,"mT1","assiette 40 % PASS (18 547,2) -> T1 = 1,5 %.",ck(MT,ass(18547.2),1.5,0.001)),
 L("T1b-P10",MT,"mT2","assiette 60 % PASS (27 820,8) -> T2 = 4 %.",ck(MT,ass(27820.8),4,0.001)),
 L("T1b-P11",MT,"mT3","assiette 110 % PASS (51 004,8) -> T3 = 6,5 %.",ck(MT,ass(51004.8),6.5,0.001)),
 L("T1b-P12",MT,"mT4","assiette 200 % PASS (92 736) -> T4 = 7,7 %.",ck(MT,ass(92736),7.7,0.001)),
 L("T1b-P13",MT,"mT5","assiette 300 % PASS (139 104) -> T5 = 8,5 %.",ck(MT,ass(139104),8.5,0.001)),
 L("T1b-P14",MT,"mF3","4° formula at 50 % PASS (23 184): (4-1,5) x 0,5 + 1,5 = 2,75 % ; at 150 % PASS: (7,7-6,5) x (0,4/0,9) + 6,5 = 7,033 -> 7,03 (rule rounds to 2 decimals).",ck(MT,ass(23184),2.75,0.001)),
 L("T1b-P15",MT,"mT4","5° formula at 150 % PASS (69 552): 6,5 + 1,2 x 0,4/0,9 = 7,0333 ; rule rounds to 7,03.",ck(MT,ass(69552),7.0333,0.01)),
 L("T1b-P16",MT,"ma","'a' is the L131-6 base: trader base 29 600 = 63,84 % PASS -> 4 + 2,5 x (0,6384-0,6)/0,5 = 4,19 % "+PH,ck(MT,TR,4.19,0.001)),
 L("T1b-P17",MT,"m3x","ABSTENTION: above 300 % PASS the text ends the reduction and the base rate (L621-3 I / D621-1) applies; D621-1 is not in the bounded set. The proposal's 8,5 % above 300 % is the mechanical extension of the last tranche, not a transposed value.",status="UNKNOWN"),
 L("T1b-P18",RB+" . taux","r1715","first tranche (within PSS) = 17,15 % + 0,72 % on the whole base = 17,87 % (was 17,15 + 0,60 = 17,75).",ck(RB+" . taux",TR,17.87,0.001)),
 L("T1b-P19",RB+" . taux déplafonné","r072","rate on the whole base above the PSS: 0,72 % (was 0,60 %).",ck(RB+" . taux déplafonné",TR,0.72,0.001)),
 L("T1b-P20",RB,"r1715","trader: 29 600 x 17,87 % = 5 289,52 -> 5 290 €/an (rounded) "+PH,ck(RB,TR,5290,0.6)),
 L("T1b-P21",RB+" . taux","r1715","before 07/07/2024 the rule keeps 17,75 % (01/06/2024).",ck(RB+" . taux",dict(T,date="01/06/2024"),17.75,0.001)),
 L("T1b-P22",RF+" . assiette avant abattement","qI1","ABSTENTION (PLACEHOLDER): the texts do not settle which income lines enter the base (treatment of compulsory contributions, Madelin contributions, spouse contributions); the rule reuses the library's existing line pending a text.",status="UNKNOWN"),
 L("T1b-P23",RF+" . assiette avant abattement","L131ded","NOT transposed: deductions of épargne salariale sums (L. 3312-4, L. 3324-5, L. 3332-27 code du travail) and the inclusion of revenus de remplacement - no rule/input exists for them.",status="UNKNOWN"),
 L("T1b-P24",CC+" . retraite complémentaire","L131","base change only (7 %/8 % rates not in the bounded set): trader 29 600 x 7 % = 2 072 €/an "+PH,ck(CC+" . retraite complémentaire",TR,2072,0.6)),
 L("T1b-P25",CC+" . invalidité et décès","L131","base change only (1,3 % not in the bounded set): 29 600 x 1,3 % = 384,8 -> 385 €/an "+PH,ck(CC+" . invalidité et décès",TR,385,0.6)),
 L("T1b-P26",CC+" . indemnités journalières maladie","L131","base change only (0,5 % not in the bounded set): 29 600 x 0,5 % = 148 €/an "+PH,ck(CC+" . indemnités journalières maladie",TR,148,0.6)),
 L("T1b-P27",RF,"d136a","date gate: the rule is true from the consolidated in-force date of Décret n°2024-688 (2024-07-07); the application date to a given contribution year is not stated in the bounded texts -> flagged.",status="INFERRED"),
]
# --- links on G1 (law S3): document the misalignment of the unchanged pin ---
G=[
 L("T1b-G01",RB+" . taux","r072","G1 still 17,75 % (17,15 + 0,60) at 01/12/2024; text requires 0,72 % on the whole base -> 17,87 %. Expected to FAIL.",ck(RB+" . taux",TR,17.87,0.001)),
 L("T1b-G02",MT,"mT2","G1 gives 4,5 % at 60 % PASS; text T2 = 4 %. Expected to FAIL.",ck(MT,ass(27820.8),4,0.001)),
 L("T1b-G03",MT,"m0","G1 gives 0,5 % below 20 % PASS; text: taux nul. Expected to FAIL.",ck(MT,ass(4636.8),0,0.001)),
 L("T1b-G04",AC,"q26","G1 applies no 26 % abattement (base 40 000 instead of 29 600 "+PH+"). Expected to FAIL.",ck(AC,TR,29600,0.001)),
 L("T1b-G05",CC+" . CSG-CRDS . assiette","L131","G1 CSG-CRDS base = revenu + cotisations (52 788) while the cotisations base is 40 000: the two bases are not unified as L131-6 I requires.",status="INFERRED"),
 L("T1b-G06","dirigeant . indépendant . assiette minimale . maladie","m0","NEEDS_REVIEW: the 40 % PASS floor of the maladie/IJ base comes from an article outside the set; the new 0 % rate below 20 % PASS interacts with it. No value proposed.",status="UNKNOWN"),
 L("T1b-G07","dirigeant . indépendant . assiette minimale . retraite","qfloor","NEEDS_REVIEW: the abattement floor is capped by the amount in the last sentence of L. 633-1 (not in the set); D632-1 unchanged in S3; pre-existing 2024 floor mismatch (L0048) remains.",status="UNKNOWN"),
 L("T1b-G08",CC+" . maladie . taux progressif","ma","G1 rate at the trader's base: 5,92 % on 40 000 (old formula, old base); text requires 4,19 % on the abated base "+PH+". Expected to FAIL.",ck(MT,TR,4.19,0.001)),
]
json.dump(P,open("work/sophon/links_T1b_P.json","w"),ensure_ascii=False,indent=1); json.dump(G,open("work/sophon/links_T1b_G1.json","w"),ensure_ascii=False,indent=1)
print("specs written: P",len(P),"G1",len(G),"quotes all verified")
