# M2 — change maintenance, decision date 2026-03-31 (arm B)

Law snapshots S8 (legi-data 2.489.0, published 2026-01-01) and S9 (legi-data 2.514.0, published 2026-03-31); rules pin **G4 a61b72947fec** (modele-social 10.0.1, 2026-03-03; 652 raw / 1334 parsed) — the pin also moved from G3 (M1). Store: S8/S9 re-registered (identical hashes), G4 already registered (58/58 file hashes identical), P_M2 registered; revalidate S9×G4 run first: {'BROKEN': 60, 'REASSESS_LAW_CHANGED': 102, 'REASSESS_RULE_CHANGED': 23, 'RULE_CHANGED_CHECK_STILL_PASSES': 114, 'UNVERIFIED_NO_CHECK': 1}; D131-6-1 links in that report: {'REASSESS_LAW_CHANGED': 15}.

## 1. What changed between S8 and S9 (work/law/compare_S8_S9.txt, work/law/S9_dump.txt)
Only **D131-6-1**: LEGIARTI000036475110 (2018-01-01..2026-01-01, now MODIFIE) -> **LEGIARTI000053451315** (VIGUEUR 2026-01-01..2999-01-01, v8.0, sha256 59f4edcf15fb…). Modifying text: **Décret n°2026-69 du 6 février 2026, art. 1** (JORF 2026-02-08). Nota: "Conformément au premier alinéa de l'article 3 du décret n° 2026-69 du 6 février 2026, ces dispositions, dans leur rédaction issue de l'article 1er du décret précité, entrent en vigueur le 1 er janvier 2026 et s'appliquent aux créations et reprises d'entreprise intervenant à compter de cette date."
- II: " 241-3, l'exonération applicable pendant la période mentionnée au I correspond au quart du montant total des cotisations" (was "… mentionnée au I correspond au montant total des cotisations"); formula "rmule suivante : Montant de l'exonération = 0,25 E/0,25 PSS​​×(PSS−R)." (was "Montant de l'exonération = E/0,25 PSS × (PSS-R)"); new: "Les dispositions du présent II s'appliquent sans préjudice des dispositions de l'article L. 131-6-5.".
- III: the marins sentence is deleted (outside the library's scope). IV new: "La demande d'exonérations de cotisations sociales mentionnée au II de l'article L. 131-6-4 est introduite au plus tard le soixantième jour qui suit la date d'ouverture de…".
The 11 other bounded articles have identical version ids and text sha256 (D136-5, D613-4, D613-5, D613-6, D621-2, D632-1, D633-3, D756-5, L131-6, L136-3, L613-7).

## 2. Rules pin G3 -> G4 (inputs HISTORY / history_bounded_rules.patch; store file hashes)
Bounded files changed: règles/base.publicodes, règles/bénéficiaire.publicodes, règles/dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes, règles/dirigeant/auto-entrepreneur/exonérations.publicodes, règles/dirigeant/auto-entrepreneur/impôt.publicodes, règles/dirigeant/dirigeant.publicodes, règles/dirigeant/professions-libérales/CARCDSF.publicodes, règles/dirigeant/professions-libérales/CAVP.publicodes, règles/dirigeant/professions-libérales/CNBF.publicodes, règles/dirigeant/professions-libérales/PAMC.publicodes, règles/entreprise/duree-activité.publicodes, règles/impôt.publicodes, règles/protection-sociale.publicodes, règles/période.publicodes, règles/salarié/aides-employeur.publicodes, règles/salarié/conventions-collectives/bâtiment.publicodes, règles/salarié/conventions-collectives/hôtels-cafés-restaurants.publicodes, règles/salarié/conventions-collectives/spectacle-vivant.publicodes, règles/salarié/cotisations.publicodes, règles/salarié/exonérations/JEI.publicodes, règles/salarié/exonérations/exonérations.publicodes, règles/salarié/exonérations/lodeom.publicodes, règles/salarié/exonérations/réduction-générale.publicodes, règles/salarié/rémunération.publicodes, règles/salarié/temps-de-travail.publicodes. Commits 88cb2ce9 + 55470937 (2026-01-08) and ea8f00f0 (2026-01-27) transposed the 2026 D613-4/D613-6 values (BNC 25,6 %, all splits, `arrondi`, références pinned to LEGIARTI000052218738/…747) and fixed the DROM CIPAV fractions (7,8/11,6/15,5 from 07/2024): G4 equals my M1 proposal on all 39 AE cases except **DROM BNC 2026 (4,4/13,1/17,4 kept, mort-né basis)** (work/evals/M2_AE_grid_PM1_vs_G4.txt). No dirigeant/indépendant/*.publicodes or dirigeant/exonérations* file changed; dirigeant/professions-libérales/CARCDSF, CAVP, CNBF, PAMC changed (caisse values / PAMC fixes; articles outside the set), plus non-bounded files (base.publicodes: Smic/PSS 2026, salarié, impôt). New bounded name: `dirigeant . auto-entrepreneur . impôt . versement libératoire . plafond` (tax, no CSS article).

## 3. Impact on G4 — indépendant Acre (D131-6-1 II)
`dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux` is a `taux progressif` 100 % up to 75 % of `PSS proratisé`, 0 % at 100 %, whatever the creation date. For créations/reprises from 2026-01-01 the text now gives a quarter: AFFECTED.

## 4. Engine evidence (work/evals/M2_G4.jsonl vs M2_proposal.jsonl, grid M2_grid.txt; PSS 2026 = 48 060 €/an, 2025 = 47 100)
| case (EI/IR commerciale, Acre oui) | ACRE . taux | retraite de base | invalidité-décès | IJ maladie | cotisations | total cot.+contrib. |
|---|---|---|---|---|---|---|
| création 01/01/2026, R 20 000, 01/07/2026 | 100 -> 25 | 0 -> 2663 | 0 -> 195 | 0 -> 75 | 1400 -> 4333 | 3596 -> 6814 |
| création 2026, R 36 045 (= 3/4 PSS) | 100 -> 25 | 0 -> 4799 | 0 -> 352 | 0 -> 135 | 2523 -> 8975 | 6384 -> 13462 |
| création 2026, R 42 052,5 (87,5 % PSS) | 50.0 -> 12.5 | 3732 -> 6531 | 274 -> 479 | 105 -> 184 | 8102 -> 11970 | 13087 -> 17331 |
| création 2026, R 60 000 (> PSS) | 0 -> 0 | 8602 -> 8602 | - | - | 18528 -> 18528 | 26265 -> 26265 |
| PLNR création 2026, R 20 000 | 100 -> 25 | 0 -> 2663 | 0 -> 195 | 0 -> 75 | 1400 -> 4333 | 3596 -> 6814 |
| création 01/07/2025, R 20 000, 01/07/2026 (old text, prorata 49 %) | 100 -> 100 | 1811 -> 1811 | 133 -> 133 | 51 -> 51 | 3395 -> 3395 | 5784 -> 5784 |
| création 2025, R 42 052,5, 01/07/2026 | 50.0 -> 50.0 | 5635 -> 5635 | - | - | 10732 -> 10732 | 15972 -> 15972 |
| 2025 control, création 01/01/2025, R 20 000 / 41 212,5 | 100 -> 100 / 50 -> 50 | - | - | - | 1400 -> 1400 / 7940 -> 7940 | 3594 -> 3594 |
Acre non (création 2026, R 20 000): retraite de base 3550, invalidité-décès 260, IJ 100, cotisations 5310 €/an -> the proposal's 2 663 / 195 / 75 are 3/4 of these (quarter exonerated).
DROM BNC 01/01/2026 (AE grid): P1 4.4 -> 4.3, P2 13.1 -> 12.8, P3 17.4 -> 17.1 %; everything else in the 39 AE cases identical G4 = proposal.

## 5. Classification ({'AFFECTED': 18, 'NEEDS_REVIEW': 15, 'UNAFFECTED': 43}; 76 rules re-examined, 300 not re-examined)
- **AFFECTED (own edit, high)**: `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux`. **AFFECTED (propagation)**: `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE` and its 5 children, `IND . maladie / retraite de base / invalidité et décès / allocations familiales / indemnités journalières maladie / CSG-CRDS / cotisations`, `dirigeant . indépendant . cotisations et contributions`; carried-over: `dirigeant . auto-entrepreneur . DROM . taux service BNC` (+ BNC amount / cotisations in DROM).
- **NEEDS_REVIEW**: `dirigeant . exonérations . ACRE` (I unchanged; IV 60-day deadline and L. 131-6-5 not modelled, documentation added); the 7 AE `Acre` rules and `éligible à l'ACRE` (micro-social Acre article outside the set; probes evaluate None); 8 downstream indépendant sums/net not evaluated.
- **UNAFFECTED after re-examination**: `ACRE . prorata sur l'année` (III), `exonérations . DROM`, `exonérations`, the AE 2026 rates/splits/amounts (G4 == M1 proposal, revalidated M1 links RULE_CHANGED_CHECK_STILL_PASSES, fresh links M2-21..25 VERIFIED), DROM CIPAV/BIC/vente, versement libératoire rules (no CSS article).
- **Not re-examined** (300 rules): governing articles byte-identical S8 -> S9 and top-level rule body hash identical G3 -> G4 in the store (or body changed only by the AE 2026 constants covered by the regression grid) — reasons per rule in answer.json.

## 6. Proposal
`work/proposals/M2/modele-social/règles` (script work/scripts/apply_proposal_M2.py, diff CHANGES.diff, registered as P_M2): build OK 652/1334; 53 changed values over the 10 + 39 cases, all for créations 2026 or DROM BNC 2026. Condition chosen: `entreprise . date de création >= 01/01/2026` (nota: créations et reprises à compter de cette date), not the evaluation date.

## 7. Abstentions
- L. 131-6-5 reservation: "Les dispositions du présent II s'appliquent sans préjudice des dispositions de l'article L. 131-6-5." - L. 131-6-5 is not in the bounded set; its effect on the quarter exoneration is unknown
- 60-day request deadline (IV): "La demande d'exonérations de cotisations sociales mentionnée au II de l'article L. 131-6-4 est introduite au plus tard le soixantième jour qui suit la..." - procedural condition on the request of II of L. 131-6-4 (outside the set); no request-date input exists; documented, not modelled
- micro-social Acre rate: the AE Acre rate (50 %, CIPAV 13,40 % in G4) is fixed by an article outside the set; whether the 2026 quarter has a micro-social counterpart cannot be checked; AE Acre rules evaluate None in the probes
- E vs R in the degressive zone: "E est le montant total des cotisations dues aux régimes d'assurance maladie, maternité, veuvage, vie...": the text applies the rate to E (contributions at 3/4 PSS), the library to the contributions at R; pre-existing structure kept, documented in the proposal note
- transitional cases: the S9 nota ties the new text to créations/reprises from 2026-01-01; the proposal uses `entreprise . date de création >= 01/01/2026` (reprises are not distinguished in the library); affiliation-date nuances (I: 'date d'effet d'affiliation') are not modelled
- salarié Acre rules: salarié . cotisations . exonérations . Acre . * (assimilés salariés) cite D131-6-1 LEGIARTI000036475110 and implement the former 100 % / degressive rule; they are outside the bounded rule files, so not classified here, but the same 2026 change applies to 'la rémunération' - flagged for the salarié maintainer
- D613-4 c) meublés de tourisme, D756-5 II CA cap, L613-7 minimum option, D613-5 conjoint collaborateur AE: still not implemented (unchanged since T0/M1); texts identical S8 -> S9

## 8. Sophon
28 links M2-01..28 recorded twice: on G4 {'FAILED': 10, 'VERIFIED': 11, 'INFERRED': 3, 'UNKNOWN': 4} (FAILED = the 2026-création quarter and DROM BNC 2026) and on P_M2 {'VERIFIED': 21, 'INFERRED': 3, 'UNKNOWN': 4}. Revalidate S9×P_M2: {'BROKEN': 54, 'REASSESS_LAW_CHANGED': 112, 'REASSESS_RULE_CHANGED': 27, 'RULE_CHANGED_CHECK_STILL_PASSES': 128, 'STILL_VERIFIED': 24, 'UNVERIFIED_NO_CHECK': 11}. Reports: M2_asof_D131-6-1_2026-03-31.json, M2_evidence.json, M2_evidence.md, M2_report_cmd.json, M2_revalidate_S9_G4.json, M2_revalidate_S9_G4.md, M2_revalidate_S9_G4_cmd.json, M2_revalidate_S9_PM2.json, M2_revalidate_S9_PM2.md, M2_revalidate_S9_PM2_cmd.json, M2_verify_store.json.

## 9. Approvals
None recorded anywhere in the corpus (no sign-off, ratification or approval file).

## 10. Still open
L. 131-6-5 and L. 131-6-4 texts; micro-social Acre rate article; 60-day request deadline; salarié Acre rules (outside bounded files) still on the 2018 text; E-vs-R structure of the degressive zone; meublés de tourisme 6 %; D756-5 II CA cap; L613-7 minimum option; D613-5 conjoint collaborateur AE; AE Acre rules non applicable in probes.
