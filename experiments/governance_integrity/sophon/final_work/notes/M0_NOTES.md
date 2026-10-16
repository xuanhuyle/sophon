# M0 — change maintenance, decision date 2025-10-01 (arm B)

Law snapshots S6 (legi-data 2.464.0, published 2025-09-01) and S7 (legi-data 2.469.0, published 2025-10-01); rules pin G3 d6c374271727 (modele-social 10.0.0, 722 raw / 1427 parsed rules). Store: snapshots S6, S7, G3, P_M0 registered; revalidate S7xG3 run first (counts {'BROKEN': 64, 'REASSESS_LAW_CHANGED': 55, 'REASSESS_RULE_CHANGED': 20, 'RULE_CHANGED_CHECK_STILL_PASSES': 34, 'UNVERIFIED_NO_CHECK': 2}).

## 1. What changed between S6 and S7
Only **D613-4** and **D613-6**, and only in their future-version metadata (work/law/compare_S6_S7.txt; the 10 other bounded articles have identical version id, dates and text sha256):
- D613-4: current version LEGIARTI000049624097 (2025-01-01..2026-01-01) unchanged (sha256 8c3b3865...). The 2026-01-01 version announced as LEGIARTI000049624125 is now **MODIFIE_MORT_NE** (dateFin 2025-09-10); a new version **LEGIARTI000052218738** (v8.0, VIGUEUR_DIFF 2026-01-01..2999-01-01) appears **without text**.
- D613-6: current version LEGIARTI000049625405 unchanged (sha256 69b8e1b5...). LEGIARTI000049625445 -> MODIFIE_MORT_NE (2025-09-10); new **LEGIARTI000052218747** (v9.0, 2026-01-01) without text.
- Modifying text: **not named** in S7 (lienModifications still lists only Décret n°2024-484 du 30 mai 2024 art. 1, 3° / art. 2, 3°). The mort-né date points to a text of early September 2025; I abstain from naming it.

## 2. Why this matters for G3
G3 already carries `date >= 01/2026` branches in the AE rules: BNC rate **26,1 %**, BNC split 3 / 3,25 / 44,85 / 17,7 / 31,20 %, DROM BNC 4,4 / 13,1 / 17,4 %, Acre BNC rounding to 2 decimals. They were added on 2024-08-01 by commit 1d2874c5 ("Ajoute les taux de cotisation BNC pour 2025 et 2026") from the Décret 2024-484 schedule, i.e. from the versions that S7 now marks mort-né. No snapshot available to me ever carried the text of those versions, and the replacement versions have no text: **every 2026 value is unsupported -> abstain**. The 2025 values (current text) are reproduced exactly.

## 3. Engine evidence (G3, CA 1 000 €/mois; work/evals/M0_G3.jsonl, cases_M0.json)
| rule | 01/12/2024 | 01/07/2025 (text LEGIARTI000049624097/LEGIARTI000049625405) | 01/01/2026 (no text) |
|---|---|---|---|
| service BNC . taux | 23.1 | **24.6** ("10 000 euros 34 % 6 600 euros 24,6 %") | 26.1 (abstain) |
| service BIC . taux | 21.2 | **21.2** ("ôt 46 300 euros 50 % 23 150 euros 21,2 %") | 21.2 (abstain) |
| vente . taux | 12.3 | **12.3** ("79 828 euros 71 % 23 150 euros 12,3 %") | 12.3 (abstain) |
| service BNC Cipav . taux | 23.2 | **23.2** ("... 076 euros 34 % 23 150 euros 23,2 %") | 23.2 (abstain) |
| BNC split (5 shares) | 3.6/3.7/50.75/7.85/34.1 | **3.4/3.5/47.6/13/32.5** (D613-6 e) | 3/3.25/44.85/17.7/31.2 (abstain) |
| BIC & vente split | 8.9/3.1/41.8/16.5/29.7 | **same** (D613-6 a/d) | same (abstain) |
| Cipav split | 10.2/1.4/28.8/25.6/34 | **same** (D613-6 b: 9,30+0,90 ; 1,40 ; 23,45+5,35 ; 25,60 ; 34,00) | same (abstain) |
| DROM BNC P1/P2/P3 | - | **4.1 / 12.3 / 16.4** (D756-5 1/6, 1/2, 2/3 of 24,6 %) | 4.4 / 13.1 / 17.4 (abstain) |
| DROM BIC P1, vente P1 | - | **3.6**, **2.1** (rounded up to 0,1) | - |
| DROM CIPAV P1/P2/P3 | - | 7.1 / 10.6 / 14.2 — **pre-existing mismatch** (expected 7,8 / 11,6 / 15,5 from 23,2 %) | - |
Acre rules evaluated non applicable (None) in the tested situations; no value asserted.

## 4. Classification ({'AFFECTED': 8, 'NEEDS_REVIEW': 64, 'UNAFFECTED': 304})
- **AFFECTED (8)**: `service BNC . taux`, the 5 `service BNC . répartition . * . taux de répartition`, `DROM . taux service BNC`, `Acre . taux service BNC` — their own 2026 branch rests on the withdrawn versions. Edit proposed: documentation only (références pinned to LEGIARTI000049624097 / LEGIARTI000049625405, notes), **numeric values abstained**.
- **NEEDS_REVIEW**: BIC / vente / Cipav rates and splits (2025 verified; 2026 version textless), DROM BIC/vente/CIPAV fractions (CIPAV also pre-existing FAILED), and all rules that merely propagate these values (amounts, totals, revenu net, Acre BIC/vente/CIPAV, Cipav points).
- **UNAFFECTED / not re-examined**: all 273 `dirigeant . indépendant . *` rules, `dirigeant . exonérations . ACRE`, DROM applicability, TFC/CFP/impôt/affiliation AE rules, `revenu abattu`: their governing bounded articles are byte-identical in S6 and S7 (compare_S6_S7.txt) or outside the set. Their alignment with G3 itself was not re-verified in M0 (links from earlier pins show RULE_FILE_ABSENT/RULE_CHANGED after the 2025-09-19 indépendant reorganisation) — an inherited status, stated as such.

## 5. Proposal
`work/proposals/M0/modele-social/règles` (script work/scripts/apply_proposal_M0.py, diff CHANGES.diff): build OK (722/1427, same as G3), 0 changed values over the 25 cases (work/evals/M0_grid.txt). Registered as P_M0; revalidate S7xP_M0 in work/sophon/reports/.

## 6. Sophon
41 links M0-01..M0-41 on S7xG3 ({'VERIFIED': 30, 'UNKNOWN': 8, 'FAILED': 3}): 30 VERIFIED (2025 rates, splits, DROM BNC/BIC/vente), 3 FAILED (DROM CIPAV, documented pre-existing), 8 UNKNOWN (7 abstentions on the 2026 versions without text + meublés de tourisme 6 % not implemented). Reports: M0_asof_D613-4_2025-10-01.json, M0_asof_D613-4_2026-01-01.json, M0_evidence.json, M0_evidence.md, M0_final_DONE, M0_report_cmd.json, M0_revalidate_DONE, M0_revalidate_S6_G3.json, M0_revalidate_S6_G3.md, M0_revalidate_S6_G3_cmd.json, M0_revalidate_S7_G3.json, M0_revalidate_S7_G3.md, M0_revalidate_S7_G3_cmd.json, M0_revalidate_S7_G3_final.json, M0_revalidate_S7_G3_final.md, M0_revalidate_S7_G3_final_cmd.json, M0_revalidate_S7_PM0.json, M0_revalidate_S7_PM0.md, M0_revalidate_S7_PM0_cmd.json, M0_verify-store.json.

## 7. Approvals
None recorded anywhere in the corpus (no sign-off, ratification or approval file).

## 8. Still open (unchanged by this task)
DROM CIPAV fractions on 21,2 % instead of 23,2 %; meublés de tourisme 6 % (D613-4 c) not implemented; D756-5 II CA cap; L613-7 minimum-contribution option; D613-5 conjoint collaborateur of AE; AE Acre rate article outside the set; 2026 values for D613-4 / D613-6 pending the text of LEGIARTI000052218738 / LEGIARTI000052218747.

## 9. Final revalidate S7xG3 (after recording M0-01..41)
The 41 new links: 30 STILL_VERIFIED, 3 BROKEN (M0-32..34 = the deliberate DROM CIPAV literal-reading checks, FAILED at creation), 8 UNVERIFIED_NO_CHECK (= the 8 UNKNOWN links: 7 abstentions on the textless 2026 versions + the meublés-de-tourisme link; see work/sophon/reports/M0_revalidate_S7_G3_final.md). verify-store: ok, 216 links, no problems.
