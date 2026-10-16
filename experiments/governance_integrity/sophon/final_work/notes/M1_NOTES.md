# M1 — change maintenance, decision date 2026-01-01 (arm B)

Law snapshots S7 (legi-data 2.469.0, published 2025-10-01) and S8 (legi-data 2.489.0, published 2026-01-01); rules pin G3 d6c374271727 (modele-social 10.0.0, 722 raw / 1427 parsed rules), unchanged since M0. Store: S8 and P_M1 registered (G3 re-registered, identical); revalidate S8xG3 run first (counts {'BROKEN': 67, 'REASSESS_LAW_CHANGED': 87, 'REASSESS_RULE_CHANGED': 20, 'RULE_CHANGED_CHECK_STILL_PASSES': 34, 'STILL_VERIFIED': 5, 'UNVERIFIED_NO_CHECK': 3}).

## 1. What changed between S7 and S8 (work/law/compare_S7_S8.txt, work/law/S8_dump.txt)
Only **D613-4** and **D613-6**; the 10 other bounded articles have identical version id, dates and text sha256.
- D613-4: LEGIARTI000049624097 (2025-01-01..2026-01-01) -> **LEGIARTI000052218738** (VIGUEUR 2026-01-01..2999-01-01, v8.0, sha256 f86c045c...). Modifying text now named: **Décret n°2025-943 du 8 septembre 2025, art. 1** (JORF 2025-09-09; nota: applies to periods from 2026-01-01). Text: e) BNC **25,6 %** ("e) Travailleurs indépendants relevant à la fois de l'article L. 631-1 et du régime prévu à l'article 102 ter du code général des impôts 23 609 euros 34 % 15 582 euros 25,6 %"); a) 12,3 %, b) 23,2 %, c) 6 %, d) 21,2 % unchanged; all CA/revenue thresholds raised (89 776/26 035; 42 586/28 107; 31 115/4 045; 52 070/26 035; 23 609/15 582). The mort-né version LEGIARTI000049624125 stays MODIFIE_MORT_NE.
- D613-6: LEGIARTI000049625405 -> **LEGIARTI000052218747** (VIGUEUR 2026-01-01, v9.0, sha256 d91619e3...), same decree. New splits with separate L. 621-1 / L. 621-2 lines: a/d 8,80+1,25 / 3,15 / 43,45 / 19,75 / 23,60 ; b 10,60+0,80 / 1,40 / 24,30+5,20 / 30,70 / 27,00 ; c 0,00+5,10 / 3,80 / 50,20 / 18,60 / 22,30 ; e 2,60+1,50 / 3,30 / 46,40 / 21,00 / 25,20 (each sums to 100).

## 2. Impact on G3
G3's `date >= 01/2026` branches (BNC 26,1 %; BNC split 3/3,25/44,85/17,7/31,20; DROM BNC 4,4/13,1/17,4) came from the withdrawn Décret 2024-484 step and are now contradicted by the in-force text; BIC, vente and Cipav splits have no 2026 branch at all although D613-6 changes them; the BIC/vente/Cipav rates are confirmed unchanged. The DROM CIPAV fractions were already computed on 21,2 % instead of 23,2 % (pre-existing, confirmed by the new text).

## 3. Engine evidence (CA 1 000 €/mois; work/evals/M1_G3.jsonl vs M1_proposal.jsonl, grid M1_grid.txt; 39 cases)
| rule | 01/12/2025 (S7 text, G3 = proposal) | 01/01/2026 G3 | 01/01/2026 proposal (S8 text) |
|---|---|---|---|
| service BNC . taux | 24.6 | 26.1 | **25.6** ("e) Travailleurs indépendants relevant à la fois de l'article L. 631-1 et du régime prévu à l'article 102 ter du code général des impôts 23 609 euros 34 % 15 582 euros 25,6 %") |
| service BNC (€/mois) / cotisations | 246 | 261 | **256** |
| BNC split | 3.4/3.5/47.6/13/32.5 | 3/3.25/44.85/17.7/31.2 | **4.1/3.3/46.4/21/25.2** (2,60+1,50 aggregated) |
| BIC split (vente identical) | 8.9/3.1/41.8/16.5/29.7 | same | **10.05/3.15/43.45/19.75/23.6** |
| Cipav split | 10.2/1.4/28.8/25.6/34 | same | **11.4/1.4/29.5/30.7/27** |
| BIC / vente / Cipav taux | 21.2 / 12.3 / 23.2 | same | same (confirmed by LEGIARTI000052218738) |
| DROM BNC P1/P2/P3 | 4.1/12.3/16.4 (2025) | 4.4/13.1/17.4 | **4.3/12.8/17.1** |
| DROM CIPAV P1/P2/P3 | 7.1/10.6/14.2 (wrong) | 7.1/10.6/14.2 | **7.8/11.6/15.5** (also at 2025 dates) |
| DROM BIC / vente | 3.6/10.6/14.2 ; 2.1/6.2/8.2 | same | same |
Acre rules and `dirigeant . exonérations . ACRE` evaluate non applicable in the tested situations (no value asserted).

## 4. Classification ({'AFFECTED': 56, 'UNAFFECTED': 316, 'NEEDS_REVIEW': 4}; 79 rules re-examined, 297 not re-examined)
- **AFFECTED (own edit)**: `service BNC . taux`; the 5 BNC, 5 BIC, 5 vente and 4 Cipav `taux de répartition` (Cipav invalidité-décès unchanged at 1,40 %); `DROM . taux service BNC`; `DROM . taux CIPAV`. **AFFECTED (propagation, medium)**: category amounts, `cotisations`, `cotisations et contributions`, répartition amounts.
- **NEEDS_REVIEW**: `revenu net`, `revenu net . après impôt`, `Cipav . retraite complémentaire` (downstream, not evaluated); `Acre . taux service BNC` (2026 rounding branch harmless with 25,6 %; Acre rate outside the set).
- **UNAFFECTED after re-examination**: BIC/vente/Cipav rates and amounts, DROM BIC/vente, DROM applicability, Acre BIC/vente/CIPAV, CFP, `exonérations . ACRE`, `revenu abattu`.
- **Not re-examined**: all 273 `dirigeant . indépendant . *` rules and the AE rules not governed by D613-4/D613-6 — their governing bounded articles are byte-identical in S7 and S8 (compare_S7_S8.txt); inherited alignment status from earlier pins, stated as such.

## 5. Proposal
`work/proposals/M1/modele-social/règles` (script work/scripts/apply_proposal_M1.py, diff CHANGES.diff, registered as P_M1): build OK 722/1427; 72 changed values over the 39 cases, all at 2026 dates or DROM CIPAV. Aggregation choice: the new separate L. 621-1 / L. 621-2 lines are summed into the existing single `maladie-maternité` share rule (documented in notes).

## 6. Abstentions
DROM CIPAV for 07/2024..12/2024 (text of v.LEGIARTI000049624068 not in S7/S8); D613-4 c) / D613-6 c) meublés de tourisme not implemented; AE Acre rate outside the set.

## 7. Sophon
42 links M1-01..42 recorded twice: on G3 {'FAILED': 28, 'VERIFIED': 11, 'UNKNOWN': 2, 'INFERRED': 1} (FAILED = the documented 2026 misalignments and DROM CIPAV) and on P_M1 {'VERIFIED': 39, 'UNKNOWN': 2, 'INFERRED': 1}. Reports: M1_asof_D613-4_2025-12-01.json, M1_asof_D613-4_2026-01-01.json, M1_asof_D613-6_2026-01-01.json, M1_evidence.json, M1_evidence.md, M1_report_cmd.json, M1_revalidate_DONE, M1_revalidate_G3final_DONE, M1_revalidate_PM1_DONE, M1_revalidate_S8_G3.json, M1_revalidate_S8_G3.md, M1_revalidate_S8_G3_cmd.json, M1_revalidate_S8_G3_final.json, M1_revalidate_S8_G3_final.md, M1_revalidate_S8_G3_final_cmd.json, M1_revalidate_S8_PM1.json, M1_revalidate_S8_PM1.md, M1_revalidate_S8_PM1_cmd.json, M1_verify-store.json.

## 8. Approvals
None recorded anywhere in the corpus (no sign-off, ratification or approval file).

## 9. Still open
Meublés de tourisme 6 % (D613-4 c); D756-5 II CA cap; L613-7 minimum-contribution option; D613-5 conjoint collaborateur of AE; AE Acre rate article outside the set; Acre AE rules non applicable in probes (applicability not investigated); indépendant tree alignment on G3 not re-verified since the 2025-09-19 reorganisation.
