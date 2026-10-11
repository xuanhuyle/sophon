"""Builds output/answer.json for T1b from the eval jsonl files, the sophon link results and the revalidate reports."""
import json
def load(f):
    out={}
    for line in open(f):
        r=json.loads(line)
        try: res=json.loads(r["stdout"]).get("evaluations",{})
        except Exception: continue
        for k,v in res.items(): out[(r["id"],k)]=(v.get("nodeValue"),v.get("unit"),r["situation"])
    return out
B=load("work/evals/T1b_before_G1.jsonl"); A=load("work/evals/T1b_after_proposal.jsonl"); PA=load("work/evals/T1b_probes_after_proposal.jsonl"); PB=load("work/evals/T1b_probes_before_G1.jsonl")
links=[json.loads(l) for l in open("work/sophon/link_results_T1b.jsonl")]; lk={l["spec_id"]:l for l in links}
specs={s["id"]:s for f in ("work/sophon/links_T1b_P.json","work/sophon/links_T1b_G1.json") for s in json.load(open(f))}
def lid(i): return lk[i].get("link_id") or lk[i].get("id")
def ev_link(ids): return [f"sophon {i} (link {lid(i)}): {lk[i].get('status')} observed={((lk[i].get('check_result') or {}).get('observed'))} expected={((lk[i].get('check_result') or {}).get('expected'))}" for i in ids]
ART={"L131-6":{"version_id":"LEGIARTI000048683707","in_force":"2023-12-28","modified_by":"LOI n°2023-1250 du 26 décembre 2023 art. 18 (JORF 2023-12-27)"},
     "L136-3":{"version_id":"LEGIARTI000048683641","in_force":"2023-12-28","modified_by":"LOI n°2023-1250 du 26 décembre 2023 art. 18 (JORF 2023-12-27)"},
     "D136-5":{"version_id":"LEGIARTI000049899286","in_force":"2024-07-07","modified_by":"Décret n°2024-688 du 5 juillet 2024 art. 1 (JORF 2024-07-06) - CREE"},
     "D621-2":{"version_id":"LEGIARTI000049904592","in_force":"2024-07-07","modified_by":"Décret n°2024-688 du 5 juillet 2024 art. 2 (JORF 2024-07-06)"},
     "D633-3":{"version_id":"LEGIARTI000049904636","in_force":"2024-07-07","modified_by":"Décret n°2024-688 du 5 juillet 2024 art. 3 (JORF 2024-07-06)"}}
def J(*ids):
    out=[]
    for i in ids:
        s=specs[i]; a=s["article"]; out.append({"article":a,**ART[a],"quote":s["quote"],"sophon_link":lid(i),"sophon_status":lk[i].get("status")})
    return out
CC="dirigeant . indépendant . cotisations et contributions"; AC="dirigeant . indépendant . assiette des cotisations"; RF=AC+" . réforme assiette 2024"
PH="Conditional on the PLACEHOLDER pre-abattement line (revenu professionnel + cotisations facultatives déductibles): which income lines enter the L136-3 base is NOT settled by the texts (see abstentions)."
# ---------- transposed numbers (each justified by quote + version id) ----------
T=[("26 % flat abattement",RF+" . abattement forfaitaire","ABATTEMENT_TRADER@01/12/2024",10400,"26 % x 40 000 = 10 400 €/an",["T1b-P01"]),
   ("abattement floor 1,76 % of annual PSS",RF+" . abattement forfaitaire","FLOOR_rev2000@01/12/2024",816.0768,"1,76 % x 46 368 = 816,0768 €/an (binds: 26 % x 2 000 = 520 < floor)",["T1b-P02"]),
   ("abattement ceiling 130 % of annual PSS",RF+" . abattement forfaitaire","CEILING_rev300000@01/12/2024",60278.4,"130 % x 46 368 = 60 278,4 €/an (binds: 26 % x 300 000 = 78 000 > ceiling)",["T1b-P03"]),
   ("annual PSS used for floor/ceiling",RF+" . plafond annuel","ABATTEMENT_TRADER@01/12/2024",46368,"library PSS 2024 = 3 864 €/mois x 12 ; PSS 2025 not in corpus",["T1b-P04"]),
   ("maladie: rate nil below 20 % PSS",CC+" . maladie . taux progressif","MALADIE_10pct@01/12/2024",0,"assiette 10 % PSS -> 0 % (G1: 0,5 %)",["T1b-P08","T1b-G03"]),
   ("maladie T1 = 1,5 % at 40 % PSS",CC+" . maladie . taux progressif",None,1.5,"assiette 18 547,2 €/an (40 % PSS) -> 1,5 %",["T1b-P09"]),
   ("maladie T2 = 4 % at 60 % PSS",CC+" . maladie . taux progressif",None,4,"assiette 27 820,8 €/an (60 % PSS) -> 4 % (G1: 4,5 %)",["T1b-P10","T1b-G02"]),
   ("maladie T3 = 6,5 % at 110 % PSS",CC+" . maladie . taux progressif",None,6.5,"assiette 51 004,8 €/an -> 6,5 %",["T1b-P11"]),
   ("maladie T4 = 7,7 % at 200 % PSS",CC+" . maladie . taux progressif",None,7.7,"assiette 92 736 €/an -> 7,7 %",["T1b-P12"]),
   ("maladie T5 = 8,5 % at 300 % PSS",CC+" . maladie . taux progressif",None,8.5,"assiette 139 104 €/an -> 8,5 %",["T1b-P13"]),
   ("maladie linear formula (3° tranche) at 50 % PSS",CC+" . maladie . taux progressif","MALADIE_50pct@01/12/2024",2.75,"(4-1,5) x (0,5-0,4)/0,2 + 1,5 = 2,75 % (G1: 2,5 %)",["T1b-P14"]),
   ("maladie linear formula (5° tranche) at 150 % PSS",CC+" . maladie . taux progressif","MALADIE_150pct@01/12/2024",7.03,"(7,7-6,5) x (1,5-1,1)/0,9 + 6,5 = 7,0333 ; the rule rounds to 2 decimals (7,03) - rounding not stated by the text",["T1b-P15"]),
   ("retraite de base within PSS: 17,15 % + 0,72 % = 17,87 %",CC+" . retraite de base . taux","TRADER@01/12/2024",17.87,"first tranche cumulates D633-3 I (17,15 %) and II (0,72 % on the whole base); before: 17,15 + 0,60 = 17,75 %",["T1b-P18","T1b-G01"]),
   ("retraite de base above PSS: 0,72 %",CC+" . retraite de base . taux déplafonné",None,0.72,"D633-3 II (was 0,60 %)",["T1b-P19"]),
   ("in-force date 2024-07-07 (decree) - gate",RF,"ABATTEMENT_TRADER@01/12/2024",True,"true at 01/12/2024, false at 01/06/2024 (BEFOREDATE probe); application to a given contribution year not stated in the bounded texts",["T1b-P27","T1b-P07","T1b-P21"])]
evaluations=[]
for name,rule,case,exp,comment,ids in T:
    e={"transposed":name,"rule":rule,"expected_from_text":exp,"comment":comment,"justification":J(*ids)}
    if case and (case,rule) in PA: v=PA[(case,rule)]; e.update({"date":case.split("@")[1],"situation":v[2],"value_after":v[0],"unit":v[1],"value_before_G1":(PB.get((case,rule)) or (None,))[0]})
    else:
        c=lk[ids[0]].get("check_result") or {}; e.update({"date":"01/12/2024","situation":specs[ids[0]]["check"]["situation"],"value_after":c.get("observed"),"unit":c.get("unit")})
    evaluations.append(e)
# ---------- trader before/after ----------
trader=[]
for case in ("TRADER@01/12/2024","TRADER@01/06/2025","TRADER@01/06/2024"):
    d=case.split("@")[1]; rows=[]
    for (c,r),(va,ua,sit) in A.items():
        if c!=case: continue
        vb=B[(c,r)][0]; rows.append({"rule":r,"value_before_G1":vb,"value_after_proposal":va,"unit":ua,"changed":vb!=va})
    trader.append({"date":d,"situation":A[(case,AC)][2],"rules":rows,"comment":("reform gate true (date >= 07/07/2024): abated unified base 29 600 €/an. "+PH) if d!="01/06/2024" else "control date before the decree: proposal identical to G1 (no regression)."})
# ---------- classification ----------
names=[l.strip().strip('",') for l in open("work/evals/list_indep_T1b.txt")]
R=[]
def rule(r,cl,conf,ev): R.append({"rule":r,"classification":cl,"confidence":conf,"evidence":ev})
BASE=f"L131-6 {ART['L131-6']['version_id']} ({ART['L131-6']['in_force']}): \"sont assises sur l'assiette définie à l'article L. 136-3\" ; L136-3 {ART['L136-3']['version_id']}: \"fait l'objet d'un abattement de 26 %\" ; D136-5 {ART['D136-5']['version_id']} ({ART['D136-5']['in_force']}): floor 1,76 % / ceiling 130 % of the annual PSS"
NOTIN="no article of the bounded set states this rule's own rate/threshold; not asserted"
def tr(r): 
    b=B.get(("TRADER@01/12/2024",r)); a=A.get(("TRADER@01/12/2024",r))
    return f"engine trader@01/12/2024: G1 {b[0] if b else 'n/a'} -> proposal {a[0] if a else 'n/a'} {a[1] if a else ''}"
for n in names:
    s=n.replace(CC+" . ","")
    if n==CC: rule(n,"AFFECTED","high",[BASE,"total of changed components",tr(n)]+ev_link(["T1b-P05"]))
    elif s=="cotisations": rule(n,"AFFECTED","high",[BASE,"sum of contributions assessed on the new base",tr(n)])
    elif s=="CSG-CRDS": rule(n,"AFFECTED","high",[BASE,"L136-3 I/III: CSG-CRDS assessed on the abated base; G1 adds the contributions back (52 788)",tr(n)]+ev_link(["T1b-P06","T1b-G05"]))
    elif s=="CSG-CRDS . assiette": rule(n,"AFFECTED","high",[BASE,tr(n)]+ev_link(["T1b-P06","T1b-G05"]))
    elif s in ("CSG-CRDS . déductible","CSG-CRDS . non déductible"): rule(n,"AFFECTED","high",[BASE,"base change; the 6,8 % / 2,9 % rates are outside the bounded set",tr(n)])
    elif s in ("CSG-CRDS . déductible . taux","CSG-CRDS . non déductible . taux"): rule(n,"UNAFFECTED","medium",[NOTIN,tr(n)])
    elif s.endswith("revenus de remplacement"): rule(n,"NEEDS_REVIEW","medium",["L131-6 I: \"Cette assiette inclut également le montant des revenus de remplacement sans lien avec une affection de longue durée\" - the treatment of IJSS in the new base is not transposed; reduced CSG rates are outside the set"])
    elif s in ("maladie","maladie . total","maladie . taux progressif","maladie . taux progressif . assiette"): rule(n,"AFFECTED","high",[f"D621-2 {ART['D621-2']['version_id']} ({ART['D621-2']['in_force']}): \"T1 est égal à 1,5 %\" \"T2 est égal à 4 %\" \"T3 est égal à 6,5 %\" \"T4 est égal à 7,7 %\" \"T5 est égal à 8,5 %\", nil below 20 % PSS, 'a' = L131-6 base",BASE,tr(n)]+ev_link(["T1b-P08","T1b-P10","T1b-P16","T1b-G02","T1b-G08"]))
    elif s=="maladie . réduction supplémentaire": rule(n,"UNAFFECTED","high",["deprecated rule applicable only before 01/2022; no S3 text concerns that period"])
    elif s in ("retraite de base","retraite de base . taux"): rule(n,"AFFECTED","high",[f"D633-3 {ART['D633-3']['version_id']} ({ART['D633-3']['in_force']}): \"dans la limite du plafond est fixé à 17,15 %\" ; \"sur la totalité de l'assiette de cotisations est fixé à 0,72 %\" (was 0,60 %)",BASE,tr(n)]+ev_link(["T1b-P18","T1b-P19","T1b-P20","T1b-G01"]))
    elif s=="retraite complémentaire": rule(n,"AFFECTED","medium",[BASE,"base change only; 7 %/8 % rates and PRCI ceiling outside the set",tr(n)]+ev_link(["T1b-P24"]))
    elif s in ("retraite complémentaire . plafond","retraite complémentaire . références"): rule(n,"UNAFFECTED","medium",[NOTIN])
    elif s in ("invalidité et décès","invalidité et décès . assiette"): rule(n,"AFFECTED","medium",[BASE,"base change only; 1,3 % outside the set; D632-1 floor/cap unchanged in S3 (pre-existing 2024 floor mismatch L0048 BROKEN: 5 243 vs 5 332)",tr(n)]+ev_link(["T1b-P25"]))
    elif s in ("indemnités journalières maladie","indemnités journalières maladie . assiette"): rule(n,"AFFECTED","medium",[BASE,"base change only; 0,5 % and the 40 % PSS floor outside the set",tr(n)]+ev_link(["T1b-P26"]))
    elif s=="indemnités journalières maladie . taux": rule(n,"UNAFFECTED","medium",[NOTIN,tr(n)])
    elif s in ("allocations familiales","allocations familiales . taux"): rule(n,"AFFECTED","medium",[BASE,"base change only (thresholds 110-140 % PSS compare the base); AF article outside the set",tr(n)])
    elif s=="formation professionnelle": rule(n,"UNAFFECTED","high",["computed on the PSS, not on income; no bounded article",tr(n)])
    elif s in ("non déductibles","Urssaf"): rule(n,"AFFECTED","medium",["derived from changed CSG-CRDS/contribution amounts",tr(n) if s=="Urssaf" else "aggregate of CSG-CRDS non déductible"])
    elif s in ("contributions spéciales","PCV","régularisation"): rule(n,"UNAFFECTED","high",["no formula / not applicable / documentation only; no bounded article"])
    elif s=="PSS proratisé": rule(n,"UNAFFECTED","high",["PSS x activity duration; no bounded article; sophon L0039/L0040 (D131-6-1) unchanged"])
    elif s.startswith("déduction tabac"): rule(n,"NEEDS_REVIEW","medium",["applies on assiette des cotisations, which becomes the abated base; order of the tobacco deduction vs the abattement not settled by the texts"])
    elif s.startswith("début activité"): rule(n,"NEEDS_REVIEW","medium",["forfaits 19 % / 40 % PSS come from articles outside the set; the contexte overrides assiette des cotisations so the abattement is bypassed in the proposal; whether the forfait is a pre- or post-abattement base is not settled"])
    elif s=="maladie domiciliation fiscale étranger": rule(n,"NEEDS_REVIEW","medium",["14,5 % outside the set; input base changes under the reform"])
    elif s=="exonérations . ACRE . prorata sur l'année": rule(n,"UNAFFECTED","high",["date-based prorata; D131-6-1 unchanged in S3; sophon L0028 STILL_VERIFIED"])
    elif s.startswith("exonérations . ACRE"): rule(n,"NEEDS_REVIEW","medium",["D131-6-1 unchanged in S3 (LEGIARTI000036475110) but its 3/4 PSS - PSS thresholds are compared to the base, which the reform redefines; amounts exempted derive from changed contributions"])
    elif s=="exonérations": rule(n,"NEEDS_REVIEW","medium",["sum of exemptions; ACRE depends on the redefined base"])
    elif s.startswith("exonérations . covid"): rule(n,"UNAFFECTED","high",["2020-2021 covid scheme; no bounded article; dates before the reform"])
    elif s.startswith("exonérations . pension invalidité"): rule(n,"UNAFFECTED","medium",["no bounded article; exempted amounts derive from the affected contributions"])
    elif s.startswith("exonérations"): rule(n,"UNAFFECTED","high",["no bounded article governs ZFU / âge / DROM exemptions of indépendants"])
    else: rule(n,"NEEDS_REVIEW","low",["not individually analysed"])
rule(AC,"AFFECTED","high",[BASE,tr(AC)]+ev_link(["T1b-P05","T1b-P07","T1b-G04"]))
rule("dirigeant . indépendant . assiette minimale","NEEDS_REVIEW","medium",["L136-3 III: the abattement floor \"ne peut dépasser le montant mentionné à la dernière phrase de l'article L. 633-1\" (L633-1 outside the set); D632-1 unchanged in S3; how minimum bases interact with the abated base is not settled"]+ev_link(["T1b-G07"]))
rule("dirigeant . indépendant . assiette minimale . maladie","NEEDS_REVIEW","medium",["40 % PSS floor from an article outside the set; D621-2 new 1°: \"inférieur à 20 % ... le taux est nul\" interacts with it",tr("dirigeant . indépendant . assiette minimale . maladie")]+ev_link(["T1b-G06"]))
rule("dirigeant . indépendant . assiette minimale . retraite","NEEDS_REVIEW","medium",["D632-1 LEGIARTI000041966755 unchanged in S3; pre-existing mismatch: library 450 h SMIC = 5 243 vs 11,5 % PSS = 5 332 in 2024 (sophon L0048 BROKEN); comparison with the abated base not settled",tr("dirigeant . indépendant . assiette minimale . retraite")]+ev_link(["T1b-G07"]))
rule("dirigeant . indépendant . assiette minimale . retraite . en 2022","UNAFFECTED","high",["2022-only value; no S3 text concerns 2022"])
# ---------- abstentions ----------
abst=[{"topic":"income lines entering the unified base","articles":["L136-3 I 1°/2°","L131-6 I"],"reason":"L136-3 I 1° defines the base as \"sur le montant, hors plus-values et moins-values de long terme, des produits tirés de ces mêmes activités, diminué du montant des charges que l'acquisition de ces produits nécessitent\"; whether compulsory social contributions, Madelin contributions or the spouse's contributions are such 'charges' is not stated; the former explicit add-back of contributions (old CSG base) has no counterpart in the text. The proposal keeps the library's existing line as a flagged PLACEHOLDER; all 'after' amounts are conditional on it.","sophon":[lid("T1b-P22"),lid("T1b-P23")]},
 {"topic":"épargne salariale deductions and revenus de remplacement in the base","articles":["L131-6 I"],"reason":"\"En sont toutefois déduites les sommes mentionnées aux articles L. 3312-4, L. 3324-5 et L. 3332-27 du code du travail\" and the inclusion of revenus de remplacement: no input exists in the library; not transposed.","sophon":[lid("T1b-P23")]},
 {"topic":"maladie rate at/above 300 % PSS","articles":["D621-2","D621-1 (not in set)","L621-3 (not in set)"],"reason":"D621-2: reduction applies only when the base is \"inférieur à trois fois la valeur annuelle du plafond\"; above, the base rate of D621-1 applies, which is not in the bounded set. The proposal's 8,5 % above 300 % is the mechanical extension of the last tranche, not a transposed value.","sophon":[lid("T1b-P17")]},
 {"topic":"application date to contribution years","articles":["L131-6","L136-3","D136-5","D621-2","D633-3"],"reason":"The consolidated records give in-force dates only (law articles 2023-12-28; decree articles 2024-07-07). The schedule of application to the contributions of a given year (LFSS 2024 art. 18 transitional provisions) is not in the corpus. The proposal gates on 07/07/2024; evaluating the reform at 2024-12-01 follows from that gate alone and is flagged NEEDS_REVIEW.","sophon":[lid("T1b-P27")]},
 {"topic":"PSS 2025","articles":[],"reason":"No 2025 value of the plafond de la sécurité sociale is in the corpus or the library; the 2025-06-01 evaluations use the library's 2024 value (3 864 €/mois)."},
 {"topic":"rounding of the maladie rate","articles":["D621-2"],"reason":"The text gives formulas without a rounding rule; the library rounds the rate to 2 decimals (7,0333 -> 7,03). Kept, not asserted."},
 {"topic":"minimum bases (assiette minimale)","articles":["L136-3 III","D632-1","L633-1 (not in set)"],"reason":"The floor's cap refers to L633-1 (outside the set); D632-1 is unchanged; the pre-existing 2024 floor mismatch (5 243 vs 5 332) is not resolved here."},
 {"topic":"rates outside the bounded set","articles":[],"reason":"CSG 6,8 % / 2,9 %, RCI 7 % / 8 %, invalidité-décès 1,3 %, IJ 0,5 %, AF thresholds, CFP 0,25 % / 0,29 %, maladie 6,5 % above 5 PSS: unchanged in the proposal and not asserted."},
 {"topic":"AE articles D613-4 / D613-6 (out of T1b scope)","articles":["D613-4","D613-6"],"reason":"S3 now carries the text of D613-4 LEGIARTI000049624068 (2024-07-01..2025-05-01: b) 23,2 %, e) 23,1 %, a) 12,3 %, c) 6 %, d) 21,2 %) and D613-6 LEGIARTI000049625264 (2024-07-01..2025-01-01, new splits). They concern auto-entrepreneur rules, not the indépendant rules of this task; recorded for a later task (sophon REASSESS_LAW_CHANGED on the T0/T1a links). Versions LEGIARTI000049624097 / LEGIARTI000049624125 / LEGIARTI000049625405 / LEGIARTI000049625445 still have no text."}]
rv1=json.load(open("work/sophon/reports/T1b_revalidate_cmd.json")); rv2=json.load(open("work/sophon/reports/T1b_revalidate_PT1b_cmd.json"))
ans={"task":"T1b","decision_date":"2024-07-17","law_snapshot":"S3 (legi-data 2.381.0, published 2024-07-17)","rules_pin":"G1 2a0e452617fc (committed 2024-07-16)",
 "changed_articles":[
  {"article":"D136-5","change":"CREATED","version_id":"LEGIARTI000049899286","in_force":"2024-07-07","modifying_text":"Décret n°2024-688 du 5 juillet 2024 art. 1 (JORF 2024-07-06)","content":"floor 1,76 % and ceiling 130 % of the annual PSS for the L136-3 III abattement"},
  {"article":"D621-2","change":"MODIFIED","previous_version_id":"LEGIARTI000046714747 (2022-12-10)","version_id":"LEGIARTI000049904592","in_force":"2024-07-07","modifying_text":"Décret n°2024-688 du 5 juillet 2024 art. 2 (JORF 2024-07-06)","content":"maladie reduced-rate formula on the L131-6 base: nil < 20 % PSS; T1 1,5 % (40 %), T2 4 % (60 %), T3 6,5 % (110 %), T4 7,7 % (200 %), T5 8,5 % (300 %); reduction only below 3 PSS"},
  {"article":"D633-3","change":"MODIFIED","previous_version_id":"LEGIARTI000041967101 (2020-05-25)","version_id":"LEGIARTI000049904636","in_force":"2024-07-07","modifying_text":"Décret n°2024-688 du 5 juillet 2024 art. 3 (JORF 2024-07-06)","content":"17,15 % within the PSS (unchanged), 0,72 % on the whole base (was 0,60 %)"},
  {"article":"D613-4","change":"MODIFIED (AE, out of T1b scope)","previous_version_id":"LEGIARTI000049623867 (2024-06-01)","version_id":"LEGIARTI000049624068","in_force":"2024-07-01 .. 2025-05-01","modifying_text":"Décret n°2024-484 du 30 mai 2024 art. 1","content":"b) 21,2 -> 23,2 % ; e) 21,1 -> 23,1 %"},
  {"article":"D613-6","change":"MODIFIED (AE, out of T1b scope)","previous_version_id":"LEGIARTI000049623885 (2024-06-01)","version_id":"LEGIARTI000049625264","in_force":"2024-07-01 .. 2025-01-01","modifying_text":"Décret n°2024-484 du 30 mai 2024 art. 2","content":"new branch splits (e.g. b) 9,30/0,90/1,40/23,45/5,35/25,60/34,00 ; e) 3,60/3,70/50,75/7,85/34,10)"}],
 "law_side_unchanged_since_S0":[{"article":"L131-6",**ART["L131-6"]},{"article":"L136-3",**ART["L136-3"]}],
 "unchanged_articles":["L131-6","L136-3","L613-7","D131-6-1","D613-5","D632-1","D756-5"],"articles_missing_in_snapshot":[],
 "rules":R,"proposal_dir":"work/proposals/T1b/modele-social/règles","proposal_script":"work/scripts/apply_proposal_T1b.py","proposal_diff":"work/proposals/T1b/CHANGES.diff",
 "proposal_nature":"5 edits in dirigeant/indépendant.publicodes gated on date >= 07/07/2024: (1) assiette des cotisations = unified base = placeholder line - abattement(26 %, floor 1,76 % PSS, ceiling 130 % PSS) via new sub-rules `réforme assiette 2024 . {plafond annuel, assiette avant abattement, abattement forfaitaire, assiette unifiée}`; (2) maladie . taux progressif new tranches 0/1,5/4/6,5/7,7/8,5 % at 20/40/60/110/200/300 % PSS; (3) retraite de base . taux 17,87 % and new `taux déplafonné` 0,72 %; (4) CSG-CRDS . assiette = the same unified base (no add-back of contributions). Before 07/07/2024 every value is unchanged (control run 01/06/2024 identical to G1).",
 "build_ok":True,"build_counts":{"raw_rule_count":641,"parsed_rule_count":1226,"G1_parsed_rule_count":1220},
 "evaluations":evaluations,"trader_before_after":trader,"abstentions":abst,"approval":"none recorded",
 "notes":"See output/NOTES.md. All 'after' amounts for the trader depend on the placeholder base line; the percentages, floor/ceiling shares and the maladie/retraite rates are settled by the quoted texts and verified by the engine (sophon T1b-P01..P26).",
 "sophon_reports":["work/sophon/reports/T1b_revalidate_S3_G1.json","work/sophon/reports/T1b_revalidate_S3_G1.md","work/sophon/reports/T1b_revalidate_cmd.json","work/sophon/reports/T1b_revalidate_S3_PT1b.json","work/sophon/reports/T1b_revalidate_S3_PT1b.md","work/sophon/reports/T1b_revalidate_PT1b_cmd.json","work/sophon/reports/T1b_evidence.json","work/sophon/reports/T1b_evidence.md","work/sophon/reports/T1b_report_cmd.json","work/sophon/reports/T1b_verify-store.json","work/sophon/reports/T1b_asof_D621-2_2024-12-01.json","work/sophon/reports/T1b_asof_D633-3_2024-12-01.json","work/sophon/reports/T1b_asof_D136-5_2024-12-01.json"],
 "sophon_revalidate":{"S3_x_G1":rv1["counts"],"S3_x_P_T1b":rv2["counts"],"articles_without_any_link_before_T1b":rv1["articles_without_any_link"],"after_T1b":rv2["articles_without_any_link"]},
 "sophon_snapshots":{"law":["S0","S1","S3"],"rules":["G0","P_T1a","G1","P_T1b (proposal copy)"]},
 "sophon_links_added":[{"spec_id":l["spec_id"],"link_id":lid(l["spec_id"]),"status":l.get("status")} for l in links],
 "self_reported_tool_calls":27}
json.dump(ans,open("output/answer.json","w"),ensure_ascii=False,indent=1)
from collections import Counter
print("rules classified:",len(R),Counter(r["classification"] for r in R)); print("evaluations:",len(evaluations),"abstentions:",len(abst),"links:",len(links))
