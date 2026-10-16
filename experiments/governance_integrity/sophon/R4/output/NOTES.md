# R4 — reverse check of commit d3e0cfe0f12d (decision date 2026-03-31)

**Verdict: LEGITIMATE_INDEPENDENT_CHANGE (high).** Approval: none recorded.

## The change
chore: remplace la formule de la retraite de base par celle de l'Urssaf (authored 2026-02-13 11:36:22 +0100, committed 2026-03-30 16:00:14 +0200, Alice Dahan). Files: modele-ti/règles/indépendant/cotisations-et-contributions/cotisations/cotisations.publicodes, indépendant/professions-libérales/CNAVPL.publicodes, protection-sociale/retraite-base.publicodes (+ site tests/locales, not in the trees).

- Before: `retraite de base` (non CNBF) = `tranche 1` (assiette plafonnée PSS proratisé × 17,15 %, or 8,73/8,23 % CNAVPL) + `tranche 2` (assiette × 0,72 %/0,60 %, uncapped; CNAVPL 1,87 % capped 5 PSS), each rounded.
- After: CNAVPL gets its own rule `indépendant . profession libérale . CNAVPL . retraite de base` (same tranches); everyone else gets a `barème` on `assiette` with multiplier `PSS proratisé`: `taux T1` = 17,87 % (après réforme, i.e. date >= 01/2025) / 17,75 % up to 1 PSS, `taux T2` = 0,72 % / 0,60 % above; one rounding.
- Comment in the diff: *Le code de la sécurité sociale décrit un calcul identique à celui des PLR (taux T1 sur la part de l'assiette < PASS + taux T2 sur toute l'assiette) mais l'Urssaf calcule différemment (taux T2 sur la part de l'assiette > PASS uniquement) et a insisté pour que l'on reprenne leur méthode.*
- `protection sociale . retraite . base . revenu cotisé` = retraite de base / `tranche 1 . taux` (17,15 %) becomes / `taux de cotisation` (= `taux T1` 17,87 % non-CNAVPL; CNAVPL tranche 1 taux unchanged).

## Governing text (S9, legi-data 2.514.0)
D633-3 v.LEGIARTI000049904636, in force 2024-07-07 (Décret n°2024-688 du 5 juillet 2024, art. 3; nota: applies to periods from 2025-01-01; text identical to S3/S5):

> Le taux des cotisations assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %.
> Le taux des cotisations assises sur la totalité de l'assiette de cotisations est fixé à 0,72 %.

17,15 % × min(A, P) + 0,72 % × A  ≡  17,87 % × min(A, P) + 0,72 % × max(A − P, 0) for every A: the Urssaf presentation is algebraically the same contribution. The text says nothing about rounding. The version in force before 2024-07-07 (LEGIARTI000041967101) has no text in the snapshot: the 2024 library rates (17,15/0,60 before, 17,75/0,60 after) cannot be checked.

## Engine (both trees, `--rules modele-ti/règles --rules modele-commun/règles`; assiette set directly)

| case | date | assiette | RB before | RB after | revenu cotisé before | after | trimestres before | after | pension before | after |
|---|---|---|---|---|---|---|---|---|---|---|
| AC_4000_2025 | 01/07/2025 | 4000 €/an | 955 | 955 | 5569 | 5344 | 3 | 2 | 232 | 223 |
| AC_6900_2025 | 01/07/2025 | 6900 €/an | 1233 | 1233 | 7190 | 6900 | 4 | 3 | 300 | 288 |
| AC_20000_2025 | 01/07/2025 | 20000 €/an | 3574 | 3574 | 20840 | 20000 | 4 | 4 | 868 | 833 |
| AC_23000_2025 | 01/07/2025 | 23000 €/an | 4110 | 4110 | 23965 | 22999 | 4 | 4 | 999 | 958 |
| AC_47100_2025 | 01/07/2025 | 47100 €/an | 8417 | 8417 | 3925 | 3925 | 4 | 4 | 1963 | 1963 |
| AC_60000_2025 | 01/07/2025 | 60000 €/an | 8510 | 8510 | 3925 | 3925 | 4 | 4 | 1963 | 1963 |
| AC_120000_2025 | 01/07/2025 | 120000 €/an | 8942 | 8942 | 3925 | 3925 | 4 | 4 | 1963 | 1963 |
| AC_250000_2025 | 01/07/2025 | 250000 €/an | 9878 | 9878 | 3925 | 3925 | 4 | 4 | 1963 | 1963 |
| PLNR_20000_2025 | 01/07/2025 | 20000 €/an | 3574 | 3574 | 20840 | 20000 | 4 | 4 | 868 | 833 |
| PLNR_60000_2025 | 01/07/2025 | 60000 €/an | 8510 | 8510 | 3925 | 3925 | 4 | 4 | 1963 | 1963 |
| CNAVPL_20000_2025 | 01/07/2025 | 20000 €/an | 2120 | 2120 | 24284 | 24284 | 4 | 4 | 13 | 13 |
| CNAVPL_60000_2025 | 01/07/2025 | 60000 €/an | 5234 | 5234 | 3925 | 3925 | 4 | 4 | 31 | 31 |
| CNAVPL_250000_2025 | 01/07/2025 | 250000 €/an | 8516 | 8516 | 3925 | 3925 | 4 | 4 | 32 | 32 |
| AC_tabac_60000_2025 | 01/07/2025 | 60000 €/an | 8438 | 8438 | 3925 | 3925 | 4 | 4 | 1963 | 1963 |
| AC_60000_2026 | 01/07/2026 | 60000 €/an | 8674 | 8674 | 4005 | 4005 | 4 | 4 | 2003 | 2003 |
| AC_4000_2024 | 01/07/2024 | 4000 €/an | 930 | 931 | 5423 | 5245 | 3 | 3 | 226 | 219 |
| AC_6900_2024 | 01/07/2024 | 6900 €/an | 1224 | 1225 | 7137 | 6901 | 4 | 3 | 297 | 288 |
| AC_20000_2024 | 01/07/2024 | 20000 €/an | 3550 | 3550 | 20700 | 20000 | 4 | 4 | 863 | 833 |
| AC_23000_2024 | 01/07/2024 | 23000 €/an | 4082 | 4083 | 23802 | 23003 | 4 | 4 | 992 | 958 |
| AC_60000_2024 | 01/07/2024 | 60000 €/an | 8312 | 8312 | 3864 | 3864 | 4 | 4 | 1932 | 1932 |
| AC_250000_2024 | 01/07/2024 | 250000 €/an | 9452 | 9452 | 3864 | 3864 | 4 | 4 | 1932 | 1932 |

- Retraite de base identical before/after in all 26 2025/2026 cases (AC, PLNR, CNAVPL, tabac): True. 2024 (pre-reform) 1 € rounding-path differences: [('AC_4000_2024', 930, 931), ('AC_6900_2024', 1224, 1225), ('AC_23000_2024', 4082, 4083), ('PLNR_4000_2024', 930, 931), ('PLNR_6900_2024', 1224, 1225), ('PLNR_23000_2024', 4082, 4083)].
- `revenu cotisé` changed in 16/50 cases (all non-CNAVPL below the PSS); `trimestres` changed: [('AC_6900_2024', 4, 3), ('AC_4000_2025', 3, 2), ('AC_6900_2025', 4, 3), ('PLNR_6900_2024', 4, 3), ('PLNR_4000_2025', 3, 2), ('PLNR_6900_2025', 4, 3)]; pension estimate follows. These rest on R351-9/R634-1/D634-1 (outside the set).
- Rates: before `tranche 1 . taux` 17.15 % / `tranche 2 . taux` 0.72 % (2025), 17.15/0.6 (2024); after `taux T1` 17.87 % / `taux T2` 0.72 % (2025), 17.75/0.6 (2024).
- Build: 296/446 → 295/449 rules (names diff in work/evals/list_R4_before.txt vs list_R4_after.txt).
- Side finding (outside the set): minimal assiette 5 346 (450 h × 11,88) → RB 955 both trees, but revenu cotisé after = 955/17,87 % = 5 344 < 5 346 → 2 trimestres instead of the 3 the cotisation minimale is meant to guarantee (before: 955/17,15 % = 5 569 → 3).

## Why LEGITIMATE_INDEPENDENT_CHANGE
- Not MISMATCH: every bounded requirement (D633-3 I and II) yields the same engine amounts before and after for the period the version governs (2025+); 13 executable sophon checks pass on both trees.
- Not HARMLESS_REFACTOR: the computation changed (new folded rate 17,87 % exposed as `taux T1`; `revenu cotisé`, `trimestres`, pension estimate change for incomes below the PSS; 1 € rounding differences at 2024 dates).
- The maintainers' stated reason is the Urssaf's method (outside the bounded set); the text does not forbid an equivalent decomposition.
- UNRESOLVED only for the 2024 rounding differences (no text for the pre-2024-07-07 version).

## Sophon
- Snapshots registered: law S9; rules G4 (modele-social pin, 1334 parsed), G4pre_R4 (446), G4post_R4 (449).
- Links L0146–L0159 (work/sophon/link_results_R4.jsonl; builder work/scripts/add_links_R4.py): {"R4-pre-D633-3-I-taux-17.15": ["L0146", "VERIFIED"], "R4-pre-D633-3-II-taux-0.72": ["L0147", "VERIFIED"], "R4-pre-D633-3-I-amount-60000": ["L0148", "VERIFIED"], "R4-pre-D633-3-II-amount-20000": ["L0149", "VERIFIED"], "R4-pre-D633-3-I-amount-250000": ["L0150", "VERIFIED"], "R4-post-D633-3-I+II-tauxT1-17.87": ["L0151", "VERIFIED"], "R4-post-D633-3-II-tauxT2-0.72": ["L0152", "VERIFIED"], "R4-post-D633-3-I-amount-60000": ["L0153", "VERIFIED"], "R4-post-D633-3-II-amount-20000": ["L0154", "VERIFIED"], "R4-post-D633-3-I-amount-250000": ["L0155", "VERIFIED"], "R4-post-D633-3-I-amount-PSS": ["L0156", "VERIFIED"], "R4-post-D633-3-I-amount-tabac": ["L0157", "VERIFIED"], "R4-post-D633-3-floor-4000": ["L0158", "VERIFIED"], "R4-2024-abstain-23000": ["L0159", "UNKNOWN"]}
- Revalidation counts: S9×G4 {'BROKEN': 26, 'REASSESS_LAW_CHANGED': 70, 'REASSESS_RULE_CHANGED': 14, 'RULE_CHANGED_CHECK_STILL_PASSES': 34, 'UNVERIFIED_NO_CHECK': 1}; S9×G4pre_R4 {'BROKEN': 60, 'REASSESS_LAW_CHANGED': 70, 'REASSESS_RULE_CHANGED': 15}; S9×G4post_R4 {'BROKEN': 62, 'REASSESS_LAW_CHANGED': 70, 'REASSESS_RULE_CHANGED': 15, 'RULE_CHANGED_CHECK_STILL_PASSES': 3, 'STILL_VERIFIED': 8, 'UNVERIFIED_NO_CHECK': 1}. Older links name modele-social rules (`dirigeant . ...`) → RULE_FILE_ABSENT/BROKEN on the modele-ti trees; LAW_CHANGED for D131-6-1, D613-4, D613-6, L136-3 (new 2025/2026 versions in S9, AE side, not part of this commit) and for the T0 links recorded against the pre-2024 D633-3/D621-2 versions.
- Reports: work/sophon/reports/R4_asof_D633-3_2026-03-31.json, work/sophon/reports/R4_evidence.json, work/sophon/reports/R4_evidence.md, work/sophon/reports/R4_report_cmd.json, work/sophon/reports/R4_revalidate_S9_G4.json, work/sophon/reports/R4_revalidate_S9_G4.md, work/sophon/reports/R4_revalidate_S9_G4_cmd.json, work/sophon/reports/R4_revalidate_S9_G4post_R4.json, work/sophon/reports/R4_revalidate_S9_G4post_R4.md, work/sophon/reports/R4_revalidate_S9_G4post_R4_cmd.json, work/sophon/reports/R4_revalidate_S9_G4pre_R4.json, work/sophon/reports/R4_revalidate_S9_G4pre_R4.md, work/sophon/reports/R4_revalidate_S9_G4pre_R4_cmd.json, work/sophon/reports/R4_verify-store.json
- Approval: none recorded (no sign-off, ratification or approval file exists in the corpus).

