import json,os
def load(f):
    out={}
    for line in open(f):
        r=json.loads(line); res=json.loads(r["stdout"])
        for k in ("results","evaluations","values"):
            if isinstance(res.get(k),dict): res=res[k]; break
        for k,v in res.items():
            if isinstance(v,dict) and "nodeValue" in v: out[(r["id"].split("@")[0],r["id"].split("@")[1],k)]=(v.get("nodeValue"),r["situation"])
    return out
B=load("work/evals/T1a_before_G0.jsonl"); B.update(load("work/evals/T1a_extra_before_G0.jsonl"))
A=load("work/evals/T1a_after_proposal.jsonl"); A.update(load("work/evals/T1a_extra_after_proposal.jsonl"))
C="dirigeant . auto-entrepreneur . cotisations et contributions . cotisations"
RCI="protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur"
qa="79 828 euros 71 % 23 150 euros 12,3 %"; qb="11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 21,2 %"
qd="2° du 1 de l'article 50-0 du code général des impôt 46 300 euros 50 % 23 150 euros 21,2 %"; qe="10 000 euros 34 % 6 600 euros 21,1 %"
q6="Cotisation d'assurance vieillesse complémentaire 16,50 %"
q6e="Cotisation d'assurance maladie maternité 3,90 % Cotisation d'assurance invalidité-décès 4,10 % Cotisations d'assurance vieillesse de base mentionnées aux I et II de l'article D. 633-3 du code de la sécurité sociale 55,50 % Contribution sociale généralisée et contribution pour le remboursement de la dette sociale 36,50 %"
V4={"D613-4":"LEGIARTI000049623867","D613-6":"LEGIARTI000049623885"}
FUT={"D613-4":{"01/07/2024":"LEGIARTI000049624068","01/01/2025":"LEGIARTI000049624097","01/01/2026":"LEGIARTI000049624125"},
     "D613-6":{"01/07/2024":"LEGIARTI000049625264","01/01/2025":"LEGIARTI000049625405","01/01/2026":"LEGIARTI000049625445"}}
# (case, rule, article, quote, expected at 01/06/2024, comment)
plan=[("PROMPT_BNC",C+" . taux service BNC","D613-4",qe,21.1,"I e) BNC (L631-1 + CGI 102 ter): taux global 21,1 %"),
 ("PROMPT_BNC",C+" . taux service BIC","D613-4",qd,21.2,"I d) service BIC: 21,2 %"),
 ("PROMPT_BNC",C+" . taux vente restauration hébergement","D613-4",qa,12.3,"I a) vente: 12,3 %"),
 ("CIPAV_2021",C+" . cotisations CIPAV . taux","D613-4",qb,21.2,"I b) section 11° R641-1 (CIPAV): 21,2 %"),
 ("PROMPT_BNC",C,"D613-4",qe,2532,"12 000 €/an x 21,1 %"),
 ("BIC_service",C,"D613-4",qd,2544,"12 000 €/an x 21,2 %"),
 ("VENTE",C,"D613-4",qa,1476,"12 000 €/an x 12,3 %"),
 ("CIPAV_2019",C,"D613-4",qb,2544,"12 000 €/an x 21,2 % (AE created 2019; for an AE created >= 04/2020 the engine returns 1 452 = pre-existing bug T0 L0006 / T1a-09)"),
 ("VENTE",RCI,"D613-6",q6,243.54,"a) share 16,50 % of 12 000 x 12,3 % = 243,54; rule uses rounded 2,03 % -> 243,6"),
 ("BIC_service",RCI,"D613-6",q6,419.76,"d) share 16,50 % of 12 000 x 21,2 % = 419,76; rule uses rounded 3,50 % -> 420"),
 ("BNC_rich",RCI,"D613-6",q6e,0,"e) lists no complementary-pension share -> 0")]
dates=["01/06/2024","01/07/2024","01/01/2025","01/01/2026"]
evals=[];abst=[];seen=set()
for case,rule,art,quote,exp,comment in plan:
    for d in dates:
        vb,sit=B[(case,d,rule)]; va,_=A[(case,d,rule)]
        e={"rule":rule,"date":d,"situation":sit,"value_before":vb,"value_after":va,"article":art}
        if d=="01/06/2024":
            e.update({"expected_from_text":exp,"quote":quote,"article_version_id":V4[art],"in_force":"2024-06-01..2024-07-01","text_available":True,"comment":comment,
                      "aligned": abs((vb or 0)-exp)<=0.3})
        else:
            e.update({"expected_from_text":None,"quote":None,"article_version_id":FUT[art][d],"text_available":False,"abstain":True,
                      "comment":f"Version {FUT[art][d]} of {art} is announced in force from {d[-4:]}-{d[3:5]}-{d[:2]} but its text is not in snapshot S1; the engine value shown is the unchanged G0/proposal value, not a value derived from text."})
            key=(rule,d)
            if key not in seen:
                seen.add(key); abst.append({"rule":rule,"date":d,"article":art,"announced_version_id":FUT[art][d],
                  "reason":f"{art} version {FUT[art][d]} (Décret n°2024-484 du 30 mai 2024) is announced for this date by id and date only; S1 contains only the text of the version in force 2024-06-01..2024-07-01. No available text states the rate/split for this date, so no value is proposed and the current rule value is not asserted to be correct."})
        evals.append(e)
links=[json.loads(l) for l in open("work/sophon/link_results_T1a.jsonl")]
lk={l["spec_id"]:l for l in links}
def ev_link(ids): return [f"sophon {i}: {lk[i].get('status')} (link {lk[i].get('link_id') or lk[i].get('id')}) observed={((lk[i].get('check_result') or {}).get('observed'))}" for i in ids]
taux_ev=lambda name,val,q,ids: [f"D613-4 LEGIARTI000049623867 (in force 2024-06-01, Décret n°2024-484 du 30 mai 2024 art. 1): \"{q}\"",
  f"engine G0 and proposal: {name} = {val} on 01/06/2024, 01/07/2024, 01/01/2025, 01/01/2026 (prompt BNC situation); text supports the value only for 01/06/2024",
  "announced versions without text: LEGIARTI000049624068 (2024-07-01), LEGIARTI000049624097 (2025-01-01), LEGIARTI000049624125 (2026-01-01) -> abstain",
  "sophon revalidate S1xG0: REASSESS_LAW_CHANGED (LAW_CHANGED, RULE_SAME, CHECK_PASS)"]+ev_link(ids)
R=[]
def rule(r,cl,conf,ev): R.append({"rule":r,"classification":cl,"confidence":conf,"evidence":ev})
rule(C+" . taux service BNC","NEEDS_REVIEW","high",taux_ev("taux service BNC",21.1,qe,["T1a-01","T1a-11"]))
rule(C+" . taux service BIC","NEEDS_REVIEW","high",taux_ev("taux service BIC",21.2,qd,["T1a-02","T1a-12"]))
rule(C+" . taux vente restauration hébergement","NEEDS_REVIEW","high",taux_ev("taux vente restauration hébergement",12.3,qa,["T1a-03","T1a-13"]))
rule(C+" . cotisations CIPAV . taux","NEEDS_REVIEW","high",taux_ev("cotisations CIPAV . taux",21.2,qb,["T1a-04","T1a-14"])+["evaluated with CIPAV situation (libérale réglementée = oui)"])
rule(C,"NEEDS_REVIEW","high",["amount = CA x D613-4 global rate; on 01/06/2024: BNC 2 532, BIC 2 544, vente 1 476, CIPAV(created 2019) 2 544 €/an for 12 000 €/an CA, all matching the LEGIARTI000049623867 table","same values on 01/07/2024, 01/01/2025, 01/01/2026 but no text supports them (announced versions) -> abstain","pre-existing, unrelated to S1: CIPAV AE created >= 04/2020 pays 1 452 (12,1 %) instead of 2 544 (T1a-09 FAILED); category c) meublés de tourisme 6 % not implemented (T1a-10 UNKNOWN); D613-6 split not implemented (T1a-19 UNKNOWN)"]+ev_link(["T1a-05","T1a-06","T1a-07","T1a-08","T1a-09","T1a-10"]))
rule(C+" . taux prestation de service","NEEDS_REVIEW","medium",["déprécié alias of taux service BIC (valeur: taux service BIC); follows its classification"])
rule("dirigeant . auto-entrepreneur . cotisations et contributions","NEEDS_REVIEW","medium",["parent sum; engine 213 €/mois (= 2 532/12) on all four dates for the prompt BNC situation; depends entirely on the rules above"])
rule(RCI,"AFFECTED","high",["rule références pin D613-6 to LEGIARTI000046714699/2022-12-10, a version now MODIFIE (ended 2024-06-01); new version LEGIARTI000049623885 (Décret n°2024-484 art. 2, in force 2024-06-01) has an identical text","D613-6 a)/d): \"Cotisation d'assurance vieillesse complémentaire 16,50 %\"; engine G0 = proposal: vente 243.6 €/an (text 243.54), BIC 420 €/an (text 419.76), BNC 0 on all four dates","proposal: re-pin références to LEGIARTI000049623885 + note on announced versions LEGIARTI000049625264 (2024-07-01), LEGIARTI000049625405 (2025-01-01), LEGIARTI000049625445 (2026-01-01) without text -> abstain for those dates; no numeric change","minor pre-existing wording issue: third term multiplies 'service BIC' by 0 % where 'service BNC' is meant (no numeric effect)"]+ev_link(["T1a-15","T1a-16","T1a-17","T1a-18"]))
for r in ["dirigeant . auto-entrepreneur . DROM . taux service BNC","dirigeant . auto-entrepreneur . DROM . service BIC","dirigeant . auto-entrepreneur . DROM . taux vente restauration hébergement","dirigeant . auto-entrepreneur . DROM . taux CIPAV"]:
    rule(r,"NEEDS_REVIEW","medium",["D756-5 unchanged in S1 (LEGIARTI000034726710, LAW_SAME; T0 links L0014-L0025 STILL_VERIFIED)","but D756-5 defines fractions of the D613-4 global rates, which have announced future versions without text; if those versions change the rates these fractions must follow -> review when text arrives; no change proposed now"])
rule("dirigeant . auto-entrepreneur . DROM","UNAFFECTED","medium",["applicability logic (periods, DROM) governed by D756-5/L613-7, both unchanged in S1 (LAW_SAME)"])
for r,arts,ids in [("dirigeant . exonérations . ACRE","L613-7 (LEGIARTI000048683570), D131-6-1 (LEGIARTI000036475110)","L0011"),
 ("entreprise . imposition . régime . micro-entreprise . revenu abattu","L613-7 (LEGIARTI000048683570)","L0012 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . prorata sur l'année","D131-6-1","L0028 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux","D131-6-1","L0031/L0036/L0037 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . maladie","D131-6-1","L0038 (no check)"),
 ("dirigeant . indépendant . cotisations et contributions . PSS proratisé","D131-6-1","L0039/L0040 (no check)"),
 ("dirigeant . indépendant . cotisations et contributions . retraite de base","D131-6-1, D633-3 (LEGIARTI000041967101)","L0032/L0049/L0050 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . retraite de base . taux","D633-3","L0051 (no check)"),
 ("dirigeant . indépendant . cotisations et contributions . maladie","D131-6-1, D621-2 (LEGIARTI000046714747)","L0033 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . maladie . taux progressif","D621-2","L0041-L0043 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . invalidité et décès","D131-6-1, D632-1 (LEGIARTI000041966755)","L0034 STILL_VERIFIED"),
 ("dirigeant . indépendant . cotisations et contributions . retraite complémentaire","D131-6-1","L0035 (no check)"),
 ("dirigeant . indépendant . conjoint collaborateur . cotisations","D613-5 (LEGIARTI000041918205)","L0053 UNKNOWN (not implemented for AE)"),
 ("dirigeant . indépendant . assiette des cotisations","L131-6 (LEGIARTI000048683707)","L0054 UNKNOWN"),
 ("dirigeant . indépendant . cotisations et contributions . CSG-CRDS . assiette","L136-3 (LEGIARTI000048683641)","L0055 UNKNOWN")]:
    rule(r,"UNAFFECTED","high",[f"governing article(s) {arts}: same version id and text hash in S1 as in S0 (revalidate LAW_SAME)",f"sophon links {ids}; status unchanged by S1"])
rule("dirigeant . indépendant . cotisations et contributions . invalidité et décès . assiette","UNAFFECTED","high",["D632-1 LEGIARTI000041966755 unchanged (LAW_SAME); L0046/L0047 STILL_VERIFIED","L0048 BROKEN = pre-existing 2024 floor mismatch found in T0 (library 450 h SMIC = 5 243 vs 11,5 % PSS = 5 332), not caused by S1"])
ch=[{"article":"D613-4","from_version_id":"LEGIARTI000046714712","to_version_id":"LEGIARTI000049623867","in_force_from":"2024-06-01","in_force_to":"2024-07-01","etat":"ABROGE_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 - art. 1 (JORFTEXT000049620955, JORF 2024-05-31)","what_changed":"New version 4.0 whose text differs from 3.0 only by whitespace (4 occurrences of \"l'article\" -> \"l' article\"); the I. table keeps 12,3 / 21,2 / 6 / 21,2 / 21,1 %; the Conseil d'Etat annulation nota and ANNULATION link (décision 471203) are no longer attached; nota: entry into force 1 June 2024 per 1° of art. 1.","new_text_available":True},
 {"article":"D613-4","from_version_id":"LEGIARTI000049623867","to_version_id":"LEGIARTI000049624068","in_force_from":"2024-07-01","in_force_to":"2025-05-01 (as recorded; overlaps version 6.0 starting 2025-01-01 - metadata inconsistency in the snapshot)","etat":"VIGUEUR_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 (announced version 5.0; lienModifications lists only art. 1 for the current version)","what_changed":"Announced future version; text not included in S1 -> content unknown, abstain.","new_text_available":False},
 {"article":"D613-4","from_version_id":"LEGIARTI000049624068","to_version_id":"LEGIARTI000049624097","in_force_from":"2025-01-01","in_force_to":"2026-01-01","etat":"VIGUEUR_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 (announced version 6.0)","what_changed":"Announced future version; text not included in S1 -> abstain.","new_text_available":False},
 {"article":"D613-4","from_version_id":"LEGIARTI000049624097","to_version_id":"LEGIARTI000049624125","in_force_from":"2026-01-01","in_force_to":"2999-01-01","etat":"VIGUEUR_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 (announced version 7.0)","what_changed":"Announced future version; text not included in S1 -> abstain.","new_text_available":False},
 {"article":"D613-6","from_version_id":"LEGIARTI000046714699","to_version_id":"LEGIARTI000049623885","in_force_from":"2024-06-01","in_force_to":"2024-07-01","etat":"ABROGE_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 - art. 2 (JORFTEXT000049620955, JORF 2024-05-31)","what_changed":"New version 5.0 with a text byte-identical to version 4.0 (same split percentages); Conseil d'Etat annulation nota/link removed; nota: entry into force 1 June 2024 per 1° of art. 2.","new_text_available":True},
 {"article":"D613-6","from_version_id":"LEGIARTI000049623885","to_version_id":"LEGIARTI000049625264","in_force_from":"2024-07-01","in_force_to":"2025-01-01","etat":"VIGUEUR_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 (announced version 6.0)","what_changed":"Announced future version; text not included in S1 -> abstain.","new_text_available":False},
 {"article":"D613-6","from_version_id":"LEGIARTI000049625264","to_version_id":"LEGIARTI000049625405","in_force_from":"2025-01-01","in_force_to":"2026-01-01","etat":"VIGUEUR_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 (announced version 7.0)","what_changed":"Announced future version; text not included in S1 -> abstain.","new_text_available":False},
 {"article":"D613-6","from_version_id":"LEGIARTI000049625405","to_version_id":"LEGIARTI000049625445","in_force_from":"2026-01-01","in_force_to":"2999-01-01","etat":"VIGUEUR_DIFF","modifying_text":"Décret n°2024-484 du 30 mai 2024 (announced version 8.0)","what_changed":"Announced future version; text not included in S1 -> abstain.","new_text_available":False}]
reports=[p for p in ["work/sophon/reports/T1a_revalidate_S1_G0.json","work/sophon/reports/T1a_revalidate_S1_G0.md","work/sophon/reports/T1a_revalidate_cmd.json","work/sophon/reports/T1a_revalidate_S1_PT1a.json","work/sophon/reports/T1a_revalidate_S1_PT1a.md","work/sophon/reports/T1a_revalidate_PT1a_cmd.json","work/sophon/reports/T1a_evidence.json","work/sophon/reports/T1a_evidence.md","work/sophon/reports/T1a_report_cmd.json","work/sophon/reports/T1a_verify-store.json","work/sophon/reports/T1a_asof_D613-4_2024-07-01.json"] if os.path.exists(p)]
ans={"task":"T1a","decision_date":"2024-06-01","law_snapshot":"S1 (legi-data 2.361.0, published 2024-06-01)","rules_pin":"G0 d9242882f96b","unchanged_articles":["L131-6","L136-3","L613-7","D131-6-1","D613-5","D621-2","D632-1","D633-3","D756-5"],"articles_missing_in_snapshot":["D136-5"],
 "changed_articles":ch,"rules":R,"proposal_dir":"work/proposals/T1a/modele-social/règles","proposal_nature":"traceability-only: références re-pinned to the 2024-06-01 versions (D613-4 LEGIARTI000049623867, D613-6 LEGIARTI000049623885) and notes recording the announced versions whose text is unavailable; NO numeric value changed (none is supported by available text)","proposal_diff":"work/proposals/T1a/CHANGES.diff","build_ok":True,"build_counts":{"raw_rule_count":639,"parsed_rule_count":1172},
 "evaluations":evals,"abstentions":abst,"approval":"none recorded",
 "notes":"S1 vs S0: only D613-4 and D613-6 changed, both re-versioned on 2024-06-01 by Décret n°2024-484 du 30 mai 2024 with no substantive text change (D613-4: whitespace only; D613-6: identical). The same decree announces three further versions of each article (2024-07-01, 2025-01-01, 2026-01-01) whose text is NOT in the snapshot; every value for those dates is therefore abstained. No value from outside the corpus was used. Engine values before and after the proposal are identical by construction. Pre-existing, S1-independent defects remain: CIPAV AE created >= 04/2020 charged 12,1 % (T1a-09 FAILED), D632-1 2024 floor (L0048 BROKEN), meublés de tourisme 6 % and D613-6 split not implemented. See output/NOTES.md.",
 "sophon_reports":reports,"sophon_snapshots":{"law":["S0","S1"],"rules":["G0","P_T1a (proposal copy)"]},"sophon_links_added":[{"spec_id":l["spec_id"],"link_id":l.get("link_id") or l.get("id"),"status":l.get("status")} for l in links],
 "self_reported_tool_calls":22}
json.dump(ans,open("output/answer.json","w"),ensure_ascii=False,indent=1)
print("answer.json written:",len(evals),"evaluations,",len(abst),"abstentions,",len(R),"rules,",len(ch),"changed entries,",len(reports),"reports")
json.load(open("output/answer.json")); print("json valid")
