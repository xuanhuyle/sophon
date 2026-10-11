# R3 — reverse check of commit 9bb43d710094 « fix: correction des taux auto-entrepreneur DROM » (decision date 2024-10-19)

**Verdict: MISMATCH (confidence high).** Law S5 = legi-data 2.385.0 (identical texts to S4/S3). Rules pin G2 = 3a4091ae1caf; commit authored 2024-10-03 14:56:55 +0200, committed 2024-10-11 09:34:14 +0200 by Alice Dahan; applied forward on a copy (`work/proposals/R3/after`).

## 1. What the commit changes (engine evidence)

- `exonérations.publicodes`: the four DROM rate rules were nested in the BODY of the private rule `dirigeant . auto-entrepreneur . DROM . seconde période` (6-space indent, since the re-indentation commit 05334b12 of 2024-09-02); publicodes silently ignored them. The commit moves them to `DROM . avec` (and renames `service BIC` -> `taux service BIC`), merges the misspelt `references:` key into `références:`. `dirigeant.publicodes`: blank lines only.
- `build`: parsed_rule_count **1258 -> 1262**; `list --prefix 'dirigeant . auto-entrepreneur . DROM'`: 1 name -> 5 names.
- Before/after engine values (AE in the DROM, CA 1 000 €/mois, ACRE non; P1 = trimestres civils 4 / années civiles 1, P2 = 10 / 3, P3 = 20 / 5 — overrides needed because `durée d'activité` follows the wall clock):

| case | activity | period | date | BEFORE G2 (full rate) | AFTER commit (rate) | proposal | law in force -> expected |
|---|---|---|---|---|---|---|---|
| DROM_BNC_P1_05-2024 | BNC | P1 | 01/05/2024 | 211.0 €/mois (21.1 %) | 36 €/mois (3.6 %) | 36 €/mois | 21,1/6->3,6 % = 36 (S0 version) |
| DROM_BNC_P1_10-2024 | BNC | P1 | 01/10/2024 | 231 €/mois (23.1 %) | 36 €/mois (3.6 %) | 39 €/mois | 23,1/6=3,85->3,9 % = 39 €/mois **MISMATCH** |
| DROM_BNC_P2_05-2024 | BNC | P2 | 01/05/2024 | 211.0 €/mois (21.1 %) | 106 €/mois (10.6 %) | 106 €/mois | 10,55->10,6 % = 106 |
| DROM_BNC_P2_10-2024 | BNC | P2 | 01/10/2024 | 231 €/mois (23.1 %) | 106 €/mois (10.6 %) | 116 €/mois | 11,55->11,6 % = 116 **MISMATCH** |
| DROM_BNC_P3_05-2024 | BNC | P3 | 01/05/2024 | 211.0 €/mois (21.1 %) | 141 €/mois (14.1 %) | 141 €/mois | 14,07->14,1 % = 141 |
| DROM_BNC_P3_10-2024 | BNC | P3 | 01/10/2024 | 231 €/mois (23.1 %) | 141 €/mois (14.1 %) | 154 €/mois | 15,4 % = 154 **MISMATCH** |
| DROM_CIPAV_P1_05-2024 | CIPAV | P1 | 01/05/2024 | 1452 €/an (21.2 %) | 852 €/an (7.1 %) | 852 €/an | 21,2/3->7,1 % = 852 |
| DROM_CIPAV_P1_10-2024 | CIPAV | P1 | 01/10/2024 | 1452 €/an (23.2 %) | 852 €/an (7.1 %) | 936 €/an | 23,2/3=7,73->7,8 % = 936 €/an **MISMATCH** |
| DROM_CIPAV_P2_05-2024 | CIPAV | P2 | 01/05/2024 | 1452 €/an (21.2 %) | 1272 €/an (10.6 %) | 1272 €/an | 10,6 % = 1 272 |
| DROM_CIPAV_P2_10-2024 | CIPAV | P2 | 01/10/2024 | 1452 €/an (23.2 %) | 1272 €/an (10.6 %) | 1392 €/an | 11,6 % = 1 392 **MISMATCH** |
| DROM_CIPAV_P3_05-2024 | CIPAV | P3 | 01/05/2024 | 1452 €/an (21.2 %) | 1704 €/an (14.2 %) | 1704 €/an | 14,13->14,2 % = 1 704 |
| DROM_CIPAV_P3_10-2024 | CIPAV | P3 | 01/10/2024 | 1452 €/an (23.2 %) | 1704 €/an (14.2 %) | 1860 €/an | 15,47->15,5 % = 1 860 **MISMATCH** |
| DROM_BIC_P1_05-2024 | BIC | P1 | 01/05/2024 | 212 €/mois (21.2 %) | 36 €/mois (3.6 %) | 36 €/mois | (same as 10/2024: D613-4 unchanged for this category) |
| DROM_BIC_P1_10-2024 | BIC | P1 | 01/10/2024 | 212 €/mois (21.2 %) | 36 €/mois (3.6 %) | 36 €/mois | 21,2/6=3,53->3,6 % = 36 |
| DROM_BIC_P2_05-2024 | BIC | P2 | 01/05/2024 | 212 €/mois (21.2 %) | 106 €/mois (10.6 %) | 106 €/mois | (same as 10/2024: D613-4 unchanged for this category) |
| DROM_BIC_P2_10-2024 | BIC | P2 | 01/10/2024 | 212 €/mois (21.2 %) | 106 €/mois (10.6 %) | 106 €/mois | 10,6 % = 106 |
| DROM_BIC_P3_05-2024 | BIC | P3 | 01/05/2024 | 212 €/mois (21.2 %) | 142 €/mois (14.2 %) | 142 €/mois | (same as 10/2024: D613-4 unchanged for this category) |
| DROM_BIC_P3_10-2024 | BIC | P3 | 01/10/2024 | 212 €/mois (21.2 %) | 142 €/mois (14.2 %) | 142 €/mois | 14,13->14,2 % = 142 |
| DROM_VENTE_P1_05-2024 | VENTE | P1 | 01/05/2024 | 123 €/mois (12.3 %) | 21 €/mois (2.1 %) | 21 €/mois | (same as 10/2024: D613-4 unchanged for this category) |
| DROM_VENTE_P1_10-2024 | VENTE | P1 | 01/10/2024 | 123 €/mois (12.3 %) | 21 €/mois (2.1 %) | 21 €/mois | 12,3/6=2,05->2,1 % = 21 |
| DROM_VENTE_P2_05-2024 | VENTE | P2 | 01/05/2024 | 123 €/mois (12.3 %) | 62 €/mois (6.2 %) | 62 €/mois | (same as 10/2024: D613-4 unchanged for this category) |
| DROM_VENTE_P2_10-2024 | VENTE | P2 | 01/10/2024 | 123 €/mois (12.3 %) | 62 €/mois (6.2 %) | 62 €/mois | 6,15->6,2 % = 62 |
| DROM_VENTE_P3_05-2024 | VENTE | P3 | 01/05/2024 | 123 €/mois (12.3 %) | 82.0 €/mois (8.2 %) | 82.0 €/mois | (same as 10/2024: D613-4 unchanged for this category) |
| DROM_VENTE_P3_10-2024 | VENTE | P3 | 01/10/2024 | 123 €/mois (12.3 %) | 82.0 €/mois (8.2 %) | 82.0 €/mois | 8,2 % = 82 |

Metropolitan controls (outre-mer: non, 01/10/2024) identical before/after: METRO_BNC_P1_10-2024: 231 €/mois -> 231 €/mois; METRO_CIPAV_P1_10-2024: 1452 €/an -> 1452 €/an; METRO_BIC_P1_10-2024: 212 €/mois -> 212 €/mois; METRO_VENTE_P1_10-2024: 123 €/mois -> 123 €/mois. The library already applies D613-4 v.LEGIARTI000049624068 (23,1 / 23,2 %) in metropole since 07/2024 (history commits 8d04dbb6 / 1d2874c5 / d0a49c3f per `history_bounded_rules.patch`); the new DROM constants override it.

Maintainers' own fixture: `existing_tests/.../auto-entrepreneur.test.ts.snap` 'DROM 1..4' at the G2 pin shows `service BNC . taux: 23`, `service BIC . taux: 21`, `vente . taux: 12` (no reduction); the commit rewrites 116 lines of that snapshot.

## 2. Governing text (exact quotes, S5)

- **D756-5** `LEGIARTI000034726710` (VIGUEUR since 2017-05-12): « après arrondi au dixième de pour cent supérieur, à une fraction des taux prévus par l'article D. 131-6-1 » ; « le taux mentionné au premier alinéa de l'article L. 133-6-8 correspond, après arrondi au dixième de pour cent supérieur, à une fraction des taux prévus par l'article D. 131-6-1 fixée à : a) 1/6 pour les travailleurs indépendants mentionnés au 2° de l'article L. 611-1 et 1/3 dans les autres cas, jusqu'à la fin du septième trimestre civil qui suit celui au cours duquel intervient la date d'effet de l'affiliation ; b) 1/2 pour la période qui court entre la fin de la période mentionnée au a et la fin de la troisième année civile d'activité ; c) 2/3 à compter de la quatrième année civile d'activité. » ; II: « II. – L'exonération prévue au I est calculée sur le chiffre d'affaires ou les recettes dans la limite du seuil fixé par les articles 50-0 et 102 ter du code général des impôts. ».
- **D613-4** `LEGIARTI000049624068` (2024-07-01..2025-05-01): « a) Travailleurs indépendants appartenant à la catégorie mentionnée au 1° du 1 de l' article 50-0 du code général des impôts 79 828 euros 71 % 23 150 euros 12,3 % » ; « b) Travailleurs indépendants affiliés à la section professionnelle mentionnée au 11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 23,2 % » ; « d) Travailleurs indépendants appartenant à la catégorie mentionnée au 2° du 1 de l'article 50-0 du code général des impôt 46 300 euros 50 % 23 150 euros 21,2 % » ; « e) Travailleurs indépendants relevant à la fois de l'article L. 631-1 et du régime prévu à l' article 102 ter du code général des impôts 10 000 euros 34 % 6 600 euros 23,1 % ».
- **D613-4** `LEGIARTI000046714712` (2022-12-10..2024-06-01, text from store snapshot S0; S5 lists the id only): « e) Travailleurs indépendants relevant à la fois de l'article L. 631-1 et du régime prévu à l'article 102 ter du code général des impôts 10 000 euros 34 % 6 600 euros 21,1 % » ; « b) Travailleurs indépendants affiliés à la section professionnelle mentionnée au 11° de l'article R. 641-1 35 076 euros 34 % 23 150 euros 21,2 % ».
- **L613-7** `LEGIARTI000048683570` (since 2023-12-28): « Un taux global différent peut être fixé par décret pour les périodes au cours desquelles le travailleur indépendant est éligible à une exonération de cotisations et de contributions de sécurité sociale. » (D756-5 is such a decree provision).
- D756-5 cites « D. 131-6-1 » and « L. 133-6-8 » = pre-2020 numbering of D613-4 / L613-7 (renumbering decree outside the set); the current D131-6-1 (ACRE) has no rate table. The 1/6 vs 1/3 split refers to L. 611-1 2° (outside the set); the library's reading (1/3 = CIPAV) is adopted for the expected numbers but flagged.

## 3. Derivation and mismatch table (date >= 01/07/2024)

| category | base D613-4 in force | 1/6 (1/3 CIPAV) | 1/2 | 2/3 | commit values | status |
|---|---|---|---|---|---|---|
| vente (a) | 12,3 % | 2,05 -> **2,1** | 6,15 -> **6,2** | **8,2** | 2,1 / 6,2 / 8,2 | aligned (L0129-L0132 VERIFIED) |
| BIC services (d) | 21,2 % | 3,53 -> **3,6** | **10,6** | 14,13 -> **14,2** | 3,6 / 10,6 / 14,2 | aligned (L0124-L0128 VERIFIED) |
| BNC (e) | 23,1 % | 3,85 -> **3,9** | 11,55 -> **11,6** | **15,4** | 3,6 / 10,6 / 14,1 | **MISMATCH** (L0133-L0136 FAILED); values = 1/6.. of superseded 21,1 % (L0137-L0138 VERIFIED at 01/05/2024) |
| CIPAV (b) | 23,2 % | 7,73 -> **7,8** | **11,6** | 15,47 -> **15,5** | 7,1 / 10,6 / 14,2 | **MISMATCH** (L0139-L0142 FAILED); values = 1/3.. of superseded 21,2 % (L0143 VERIFIED at 01/05/2024) |
| meublés de tourisme (c) 6 % | 6 % | 1,0 | 3,0 | 4,0 | not implemented | pre-existing gap (abstain on category mapping) |

Before the commit (G2) none of the fractions applied (L0120-L0123 FAILED: 211/231/212/123 instead of 36/39/36/21).

## 4. Why MISMATCH and not another label

- Not HARMLESS_REFACTOR: engine values change for every DROM AE (e.g. BNC 231 -> 36 €/mois).
- Not LEGITIMATE_INDEPENDENT_CHANGE: restoring the D756-5 reduction is required, but the BNC/CIPAV constants contradict the rate table in force (D613-4 v.LEGIARTI000049624068) which the library itself already applies in metropole; the rule cites the URSSAF DROM guide (outside the set) but no bounded text supports 3,6 % for BNC after 2024-07-01.
- Not UNRESOLVED: the only open points (old numbering in D756-5, L. 611-1 classification, L. 751-1) affect which fraction/base applies, not whether 3,6 % is derivable — under every reading of the bounded texts it is not. Confidence on the label: high; on the exact expected numbers: medium-high (depends on the 1/6-for-BNC reading).

## 5. Disposable proposal (traceability only, never applied to inputs/)

`work/proposals/R3/proposal` = after-tree + `work/scripts/apply_proposal_R3.py`: `taux service BNC` and `taux CIPAV` get `date >= 07/2024` variations (3,90/11,60/15,40 and 7,80/11,60/15,50, with a `note:` giving the derivation). Build OK (1262 rules). Engine 01/10/2024: BNC 39/116/154 €/mois, CIPAV 936/1 392/1 860 €/an; 01/05/2024 and metropole unchanged (`work/evals/R3_drom_proposal.jsonl`). Still missing (abstain): values for 2025-01-01 / 2026-01-01 (D613-4 versions without text), the D756-5 II CA cap, category c).

## 6. Sophon store

- Snapshots: law S5; rules G2 (1258 parsed) and G2post_R3 (1262 parsed).
- `revalidate S5/G2`: {"BROKEN": 42, "REASSESS_LAW_CHANGED": 36, "REASSESS_RULE_CHANGED": 11, "RULE_CHANGED_CHECK_STILL_PASSES": 10, "STILL_VERIFIED": 10, "UNVERIFIED_NO_CHECK": 10} ; `revalidate S5/G2post_R3`: {"BROKEN": 33, "REASSESS_LAW_CHANGED": 36, "REASSESS_RULE_CHANGED": 11, "RULE_CHANGED_CHECK_STILL_PASSES": 19, "STILL_VERIFIED": 10, "UNVERIFIED_NO_CHECK": 10} (9 T0 DROM links pass again after the commit — they were recorded on the 01/05/2024 base). Rules to reassess include the DROM rules and all AE rate rules; `articles_without_any_link`: none.
- New links (law S5 unless noted; checks run against the engine now):

| id | tag | article (version) | rules snapshot | check rule / case | expected | observed | status |
|---|---|---|---|---|---|---|---|
| L0120 | R3-G2-D756-5-1/6-BNC-05/2024 | D756-5 (LEGIARTI000034726710) | G2 | COT . service BNC / DROM_BNC_P1_05-2024 | 36 | 211.00000000000003 | FAILED |
| L0121 | R3-G2-D756-5-1/6-BNC-10/2024 | D756-5 (LEGIARTI000034726710) | G2 | COT . service BNC / DROM_BNC_P1_10-2024 | 39 | 231 | FAILED |
| L0122 | R3-G2-D756-5-1/6-BIC-10/2024 | D756-5 (LEGIARTI000034726710) | G2 | COT . service BIC / DROM_BIC_P1_10-2024 | 36 | 212 | FAILED |
| L0123 | R3-G2-D756-5-1/6-VENTE-10/2024 | D756-5 (LEGIARTI000034726710) | G2 | COT . vente restauration hébergement / DROM_VENTE_P1_10-2024 | 21 | 123 | FAILED |
| L0124 | R3-after-D756-5-1/6-BIC-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BIC / DROM_BIC_P1_10-2024 | 36 | 36 | VERIFIED |
| L0125 | R3-after-D613-4-BIC-base | D613-4 (LEGIARTI000049624068) | G2post_R3 | COT . service BIC / DROM_BIC_P1_10-2024 | 36 | 36 | VERIFIED |
| L0126 | R3-after-D756-5-1/2-BIC-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BIC / DROM_BIC_P2_10-2024 | 106 | 106 | VERIFIED |
| L0127 | R3-after-D756-5-2/3-BIC-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BIC / DROM_BIC_P3_10-2024 | 142 | 142 | VERIFIED |
| L0128 | R3-after-D756-5-arrondi-BIC | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BIC / DROM_BIC_P3_10-2024 | 142 | 142 | VERIFIED |
| L0129 | R3-after-D756-5-1/6-VENTE-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . vente restauration hébergement / DROM_VENTE_P1_10-2024 | 21 | 21 | VERIFIED |
| L0130 | R3-after-D613-4-VENTE-base | D613-4 (LEGIARTI000049624068) | G2post_R3 | COT . vente restauration hébergement / DROM_VENTE_P1_10-2024 | 21 | 21 | VERIFIED |
| L0131 | R3-after-D756-5-1/2-VENTE-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . vente restauration hébergement / DROM_VENTE_P2_10-2024 | 62 | 62 | VERIFIED |
| L0132 | R3-after-D756-5-2/3-VENTE-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . vente restauration hébergement / DROM_VENTE_P3_10-2024 | 82 | 81.99999999999999 | VERIFIED |
| L0133 | R3-after-D756-5-1/6-BNC-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BNC / DROM_BNC_P1_10-2024 | 39 | 36 | FAILED |
| L0134 | R3-after-D613-4-BNC-base-23,1 | D613-4 (LEGIARTI000049624068) | G2post_R3 | COT . service BNC / DROM_BNC_P1_10-2024 | 39 | 36 | FAILED |
| L0135 | R3-after-D756-5-1/2-BNC-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BNC / DROM_BNC_P2_10-2024 | 116 | 106 | FAILED |
| L0136 | R3-after-D756-5-2/3-BNC-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BNC / DROM_BNC_P3_10-2024 | 154 | 141 | FAILED |
| L0137 | R3-after-S0-D613-4-BNC-21,1-05/2024 | D613-4 (LEGIARTI000046714712, S0) | G2post_R3 | COT . service BNC / DROM_BNC_P1_05-2024 | 36 | 36 | VERIFIED |
| L0138 | R3-after-S0-D613-4-BNC-2/3-05/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . service BNC / DROM_BNC_P3_05-2024 | 141 | 141 | VERIFIED |
| L0139 | R3-after-D756-5-1/3-CIPAV-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . cotisations CIPAV / DROM_CIPAV_P1_10-2024 | 936 | 852 | FAILED |
| L0140 | R3-after-D613-4-CIPAV-base-23,2 | D613-4 (LEGIARTI000049624068) | G2post_R3 | COT . cotisations CIPAV / DROM_CIPAV_P1_10-2024 | 936 | 852 | FAILED |
| L0141 | R3-after-D756-5-1/2-CIPAV-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . cotisations CIPAV / DROM_CIPAV_P2_10-2024 | 1392 | 1272 | FAILED |
| L0142 | R3-after-D756-5-2/3-CIPAV-10/2024 | D756-5 (LEGIARTI000034726710) | G2post_R3 | COT . cotisations CIPAV / DROM_CIPAV_P3_10-2024 | 1860 | 1704 | FAILED |
| L0143 | R3-after-S0-D613-4-CIPAV-21,2-05/2024 | D613-4 (LEGIARTI000046714712, S0) | G2post_R3 | COT . cotisations CIPAV / DROM_CIPAV_P1_05-2024 | 852 | 852 | VERIFIED |
| L0144 | R3-after-D756-5-II-plafond-CA | D756-5 (LEGIARTI000034726710) | G2post_R3 | - / - | - | - | INFERRED |
| L0145 | R3-after-L613-7-taux-different-exoneration | L613-7 (LEGIARTI000048683570) | G2post_R3 | - / - | - | - | INFERRED |

- Reports: `work/sophon/reports/R3_asof_D613-4_2024-10-19.json`, `work/sophon/reports/R3_asof_D756-5_2024-10-19.json`, `work/sophon/reports/R3_evidence.json`, `work/sophon/reports/R3_evidence.md`, `work/sophon/reports/R3_report_cmd.json`, `work/sophon/reports/R3_revalidate_S5_G2.json`, `work/sophon/reports/R3_revalidate_S5_G2.md`, `work/sophon/reports/R3_revalidate_S5_G2_cmd.json`, `work/sophon/reports/R3_revalidate_S5_G2post_R3.json`, `work/sophon/reports/R3_revalidate_S5_G2post_R3.md`, `work/sophon/reports/R3_revalidate_S5_G2post_R3_cmd.json`, `work/sophon/reports/R3_verify-store.json`. `verify-store`: {"ok": true, "problems": [], "links_checked": 145}.

## 7. Approval

none recorded (no sign-off, ratification or approval record exists in the corpus; a merge, a test snapshot or a package is not an approval).

## 8. Budget

Self-reported tool calls: 24.
