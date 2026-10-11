import json, glob, os, datetime
spec = json.load(open("work/sophon/links_T0.json"))
res = {}
for line in open("work/sophon/link_results_T0.jsonl"):
    j = json.loads(line); res[j["spec_id"]] = j
ART = json.load(open("inputs/law/S0_legi-data-2.360.0/articles.json"))["articles"]
def dt(ms): return datetime.datetime.fromtimestamp(ms/1000, datetime.timezone.utc).strftime("%Y-%m-%d")
links = []
for l in spec:
    r = res[l["id"]]; a = ART[l["article"]][0]
    status = l["answer_status"] or r.get("status")
    check = None
    if l["check"]:
        cr = r.get("check_result") or {}
        check = {"rule": l["check"]["rule"], "situation": l["check"]["situation"], "date": l["check"]["situation"].get("date"),
                 "observed": cr.get("observed"), "expected": l["check"]["expect"], "unit": cr.get("unit"), "passed": cr.get("passed")}
    if l["id"] == "D131-6-1_E_base_deviation":
        check = {"rule": "dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . maladie",
                 "situation": {"date":"01/07/2024","salarié":"non","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"non","entreprise . activité . nature":"'commerciale'","entreprise . imposition":"'IR'","dirigeant . indépendant . revenu professionnel":"40572 €/an","entreprise . date de création":"01/01/2024"},
                 "date": "01/07/2024", "observed": 1114, "expected": None,
                 "expected_note": "article: 50 % x E where E = maladie contribution due at 3/4 PSS (34 776 EUR/an), which is lower than the 2 228 EUR contribution at R = 40 572 that the engine halves; exact E depends on the IJ/maladie split, so no number is asserted (abstention on the value, not on the mismatch)", "passed": False}
    links.append({"rule": l["rule"], "rules_pin": "G0", "article": l["article"], "article_version_id": a["id"], "in_force_from": dt(a["dateDebut"]),
                  "quote": l["quote"], "claim": l["claim"], "status": status, "store_status": r.get("status"), "sophon_link_id": r.get("link_id"),
                  "check": check, "approval": "none recorded", "confidence": l["confidence"]})
reports = sorted(p for p in glob.glob("work/sophon/reports/*") if os.path.isfile(p)) + sorted(glob.glob("work/sophon/reports/*/*"))
answer = {
 "task": "T0", "decision_date": "2024-05-25", "law_snapshot": "S0 (legi-data 2.360.0, published 2024-05-25T23:36:37Z)", "rules_pin": "G0 (d9242882f96b, 2024-05-15)",
 "status_legend": "VERIFIED / INFERRED / UNKNOWN as specified; FAILED (used for 3 links) = an executable check exists and the engine does NOT reproduce the article's number (same vocabulary as the sophon store). store_status is what the store recorded.",
 "links": links,
 "not_observable": [
  "D613-4 (LEGIARTI000046714712) row c): 6 % global rate for 'location de locaux d'habitation meublés de tourisme' (6° L611-1) — no AE category or rate for furnished tourist lettings exists in the library.",
  "D613-6 (LEGIARTI000046714699): répartition of the AE global amount between maladie-maternité / invalidité-décès / vieillesse de base / vieillesse complémentaire / CSG-CRDS (four tables: a-d, b, c, e) — no rule splits the AE forfait; protection-sociale rules work from income, not from these shares.",
  "D613-5 (LEGIARTI000041918205): conjoint collaborateur of an AE (58 % / 46 % of turnover or of the forfaitaire income ÷ abattement, D613-4 rates) and II (first due date) — conjoint rules exist only for classic indépendants; 'dirigeant . indépendant . conjoint collaborateur . cotisations' evaluates to null in an AE situation.",
  "L613-7 (LEGIARTI000048683570) I al. 4-6: AE option to pay at least the minimum contributions (deadlines 31 December / end of 3rd month after creation; L131-6-1/L131-6-2 recovery) — not implemented.",
  "L613-7 I al. 3: floor of the global rate (>= CSG + CRDS + retraite complémentaire rates, given the abattements) — no rule checks it.",
  "L613-7 II al. 3-4: benefits computed on turnover after 71/50/34 % abattement, with the 64 bis CGI derogation for meublés de tourisme — only the fiscal abattement rule exists (71/50/34 reproduced for 34 %); the tourism derogation is not implemented.",
  "L613-7 III: end of the micro-social regime when leaving CGI 50-0/102 ter (options 4 of 50-0 / 5 of 102 ter) — not implemented.",
  "D756-5 (LEGIARTI000034726710) II: DROM reduced rates limited to turnover within the 50-0/102 ter thresholds — no cap in 'dirigeant . auto-entrepreneur . DROM'.",
  "D131-6-1 (LEGIARTI000036475110) I: start of the 12 months at the 'date d'effet d'affiliation' (non-salariés) vs 'début d'activité' (salariés) — the library uses one 'entreprise . date de création' for everybody.",
  "D131-6-1 II formula: E is fixed at the contribution due for 3/4 PSS — the engine prorates the contribution actually due at R (see FAILED link D131-6-1_E_base_deviation).",
  "D131-6-1 III al. 3 (marins, salaire forfaitaire L42 du code des pensions de retraite des marins) and IV (R131-3 conditions) — not implemented.",
  "L131-6 (LEGIARTI000048683707) I: deduction of épargne salariale sums (L3312-4, L3324-5, L3332-27 code du travail) and inclusion of revenus de remplacement (IJ, 154 bis CGI contracts) in the contribution base — not implemented (IJSS only enter the CSG base in the library).",
  "L131-6 I as applicable to periods from 2025-01-01 (nota, LOI 2023-1250 art. 18 VII): contribution base = L136-3 base — not implemented at G0 (pre-2025 regime: revenu professionnel + Madelin déductibles).",
  "L136-3 (LEGIARTI000048683641) III: 26 % abattement with decree floor/ceiling — not implemented at G0 (CSG base = revenu + cotisations); applies from 2025-01-01 per nota.",
  "L136-3 IV: CSG base for micro-fiscal taxpayers outside L613-7 = bénéfices 50-0/102 ter — not implemented.",
  "D621-2 (LEGIARTI000046714747) scope '1° de l'article L. 621-1' — the library applies the reduction to 'dirigeant . indépendant' generally; population mapping not observable.",
  "D136-5: listed in 'articles_missing_in_snapshot' — no text, nothing can be stated."
 ],
 "outside_bounded_set": [
  "AE Acre reduced global rate (library: 50 % of the D613-4 rate during the first 12 months, 12,1 % for CIPAV): the decree article fixing it is not in the set (D131-6-1 only gives duration and amount for non-AE); value unverifiable.",
  "D613-4 rates before 2022-12-10 (library: 22 % / 22 % / 12,8 % for date < 10/2022): earlier version LEGIARTI000043656794 (2021-06-14 -> 2022-12-10) text not provided -> abstain.",
  "D613-4 / D613-6 nota: Conseil d'État decision n° 471203 of 2024-02-09 (JORF 2024-02-21) annuls the last column of row e) of D613-4 and the last two paragraphs of D613-6 'en tant qu'ils n'incluent pas une cotisation au titre du régime complémentaire obligatoire de retraite à un taux de 7 %' — no replacement rate is in the snapshot -> abstain on any new BNC rate; expect a new D613-4/D613-6 version.",
  "L613-7 I/II: categories and populations rely on CGI 50-0, 102 ter, 64 bis and CSS L631-1, L640-1, L611-1 (8°), L136-8 / ordonnance 96-50 art. 14 (CSG-CRDS rates for the floor) — all outside.",
  "D756-5: L751-1 (which collectivités = 'département . outre-mer'), L611-1 2° (who gets 1/6 vs 1/3; library maps it to 'affiliation CIPAV'), L133-6-8 and D131-6-1 cited with their old meaning (now L613-7 / D613-4), CGI 50-0/102 ter thresholds.",
  "D131-6-1: L131-6-4 (eligibility, contributions 1°/2° of II), L241-3 (PSS value: library 46 368 EUR/an 2024, 41 136 EUR/an 2022), R131-3.",
  "D621-2: T3 = rate of D621-1 I (library 7,20 %, and 6,50 % above 5 PSS), population L621-1 1°, revenue definition L131-6, PSS L241-3.",
  "D632-1: the invalidité-décès rate itself (library 1,3 %) is fixed elsewhere; revenue definition L131-6; PSS L241-3.",
  "D633-3: scope (artisans-commerçants, L631-1/L633-1) and the minimum retraite base (library: 11,5 % PSS until 2022, 450 h x SMIC from 2023) are fixed outside the set; D633-3 nota (2016 derogation) irrelevant at this date.",
  "D613-6: references L621-2, D642-3 (PL) and D633-3 for the branches; D613-5 references D633-19-2 (revenu forfaitaire).",
  "L131-6 / L136-3: CGI 34, 35, 36-40, 38, 92, 93, 93 A, 93 quater, 111, 111 bis, 124, 8, 154 bis; L160-14 3°/4°; L213-1, L752-4, L641-2, L641-5, L651-1; decree floor/ceiling of the 26 % abattement; L633-1; L241-3.",
  "AE contributions outside the CSS set entirely: CFP 0,1/0,2/0,3 % (code du travail L6331-48), TFC, versement libératoire (CGI 151-0), micro-fiscal abattement (CGI 50-0/102 ter)."
 ],
 "notes": "See output/NOTES.md for the full reasoning. Key points: (1) the publicodes 'durée' mechanism uses the real wall clock, not the situation date, so every DROM/Acre-AE check overrides 'entreprise . durée d'activité (. trimestres civils / . années civiles)' in the situation to stay deterministic on revalidation; (2) three executable mismatches at G0: CIPAV AE created >= 01/04/2020 charged 12,1 % instead of 21,2 % even without Acre (replacement 'taux ACRE . CIPAV' leaks), invalidité-décès floor 2024 = 450 h SMIC (5 243) instead of 11,5 % PSS (5 332) required by D632-1, Acre degressive exemption prorates the contribution at R instead of E (3/4 PSS); (3) no approval record exists anywhere in the corpus; (4) the nota on D613-4/D613-6 (CE 471203) and the nota on L131-6/L136-3/L613-7 (LFSS 2024 art. 18, periods from 2025) announce changes whose values are not in the snapshot — abstain; (5) D136-5 missing from the snapshot. Statuses: VERIFIED only when the store's check passes against a number stated in the article; INFERRED when the rule plausibly implements the text without a settling check; UNKNOWN when nothing can be told (incl. provisions not implemented, recorded as 'watch' links so revalidation flags future law changes); FAILED when a check exists and fails.",
 "sophon_reports": reports,
 "sophon_store": "work/sophon/store (links.jsonl: 55 links L0001-L0055, snapshots S0 and G0)",
 "self_reported_tool_calls": 25
}
json.dump(answer, open("output/answer.json", "w"), ensure_ascii=False, indent=1)
from collections import Counter
print("answer.json written:", len(links), "links", Counter(l["status"] for l in links), "reports:", reports)
