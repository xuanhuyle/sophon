# T1b — forward transposition of the self-employed contribution-base reform (decision date 2024-07-17)

Law snapshot S3 = legi-data 2.381.0 (published 2024-07-17). Rules pin G1 = 2a0e452617fc (committed 2024-07-16). Arm B (sophon store).

## 1. What changed in the law (S1 -> S3)

| article | version in S3 | in force | modifying text | content |
|---|---|---|---|---|
| D136-5 | LEGIARTI000049899286 (**created**, absent from S0/S1) | 2024-07-07 | Décret n°2024-688 du 5 juillet 2024, art. 1 (JORF 2024-07-06) | "Le montant plancher prévu au III de l'article L. 136-3 est fixé à 1,76 % de la valeur annuelle du plafond de la sécurité sociale" ; "Le montant plafond mentionné au III de l'article L. 136-3 est fixé à 130 % de la valeur annuelle du plafond de la sécurité sociale" |
| D621-2 | LEGIARTI000049904592 (was LEGIARTI000046714747, 2022-12-10) | 2024-07-07 | Décret 2024-688 art. 2 | reduction of the maladie base rate when the base is "inférieur à trois fois la valeur annuelle du plafond": "inférieur à 20 % ... le taux est nul"; "T1 est égal à 1,5 %" (40 %), "T2 est égal à 4 %" (60 %), "T3 est égal à 6,5 %" (110 %), "T4 est égal à 7,7 %" (200 %), "T5 est égal à 8,5 %" (300 %), linear in between, with "a est l'assiette, telle que définie à l'article L. 131-6" |
| D633-3 | LEGIARTI000049904636 (was LEGIARTI000041967101, 2020-05-25) | 2024-07-07 | Décret 2024-688 art. 3 | "dans la limite du plafond est fixé à 17,15 %" (unchanged) ; "sur la totalité de l'assiette de cotisations est fixé à 0,72 %" (was 0,60 %) |
| D613-4 | LEGIARTI000049624068 (AE) | 2024-07-01..2025-05-01 | Décret 2024-484 art. 1 | text now available: b) 23,2 %, e) 23,1 % (were 21,2 / 21,1) — auto-entrepreneur rules, outside this task's rule set |
| D613-6 | LEGIARTI000049625264 (AE) | 2024-07-01..2025-01-01 | Décret 2024-484 art. 2 | new branch splits — outside this task's rule set |

L131-6 (LEGIARTI000048683707) and L136-3 (LEGIARTI000048683641), both in force 2023-12-28 (LOI n°2023-1250 du 26 décembre 2023 art. 18), are **unchanged since S0**: "sont assises sur l'assiette définie à l'article L. 136-3" (L131-6 I) and "fait l'objet d'un abattement de 26 %" bounded by a floor and a ceiling "fixé par décret" (L136-3 III). S3 is the first snapshot where that decree exists, so the mechanism becomes computable. L613-7, D131-6-1, D613-5, D632-1, D756-5: unchanged.

## 2. Classification (81 rules: 76 `dirigeant . indépendant . cotisations et contributions . …` + `assiette des cotisations` + 4 `assiette minimale`)

- **AFFECTED (22, high/medium)**: the total, `cotisations`, `CSG-CRDS` (+ `assiette`, `déductible`, `non déductible`), `maladie` (+ `total`, `taux progressif`, `taux progressif . assiette`), `retraite de base` (+ `taux`), `retraite complémentaire`, `invalidité et décès` (+ `assiette`), `indemnités journalières maladie` (+ `assiette`), `allocations familiales` (+ `taux`), `non déductibles`, `Urssaf`, `assiette des cotisations`. Direct text: D621-2 and D633-3 (rates), L131-6/L136-3/D136-5 (base). The others only through the base; their own rates are outside the bounded set and are not asserted.
- **NEEDS_REVIEW (20, medium)**: `exonérations` + ACRE rules (D131-6-1 unchanged but its PSS thresholds compare the redefined base), `déduction tabac`, `début activité` (forfaits outside the set; contexte bypasses the abattement), `maladie domiciliation fiscale étranger`, the `revenus de remplacement` CSG lines (L131-6 I includes revenus de remplacement in the base), `assiette minimale`, `. maladie`, `. retraite`.
- **UNAFFECTED (39, high/medium)**: covid, ZFU, âge, pension invalidité, DROM exemptions (no bounded article), `formation professionnelle` (PSS-based), `PSS proratisé`, `ACRE . prorata sur l'année`, `maladie . réduction supplémentaire` (pre-2022), `assiette minimale . retraite . en 2022`, nominal rates/plafonds outside the set (CSG 6,8/2,9 %, IJ 0,5 %, PRCI), `contributions spéciales`, `PCV`, `régularisation`.

Engine evidence that G1 is misaligned (sophon FAILED checks on G1): `retraite de base . taux` 17,75 vs 17,87 (T1b-G01); `maladie . taux progressif` 4,5 vs 4 at 60 % PSS (G02), 0,5 vs 0 at 10 % PSS (G03), 5,92 vs 4,19 for the trader (G08); no abattement (G04).

## 3. Proposal (`work/proposals/T1b/modele-social/règles`, script `work/scripts/apply_proposal_T1b.py`, diff `CHANGES.diff`)

Five edits in `dirigeant/indépendant.publicodes`, all gated on `date >= 07/07/2024` (the consolidated in-force date of the decree):
1. `assiette des cotisations` = `réforme assiette 2024 . assiette unifiée` = `assiette avant abattement` − `abattement forfaitaire`, where abattement = 26 % × base, `plancher: 1.76% * plafond annuel`, `plafond: 130% * plafond annuel` (`plafond annuel` = PSS in €/an = 46 368).
2. `maladie . taux progressif`: tranches 0 % (20 %), 1,5 % (40 %), 4 % (60 %), 6,5 % (110 %), 7,7 % (200 %), 8,5 % (300 %) — the publicodes `taux progressif` mechanism interpolates linearly, which is exactly the D621-2 formulas (verified at 50 % and 150 % PSS).
3. `retraite de base . taux` 17,87 % (= 17,15 + 0,72) and new `taux déplafonné` 0,72 %.
4. `CSG-CRDS . assiette` = the same unified base (no add-back of contributions).
Build: 641 raw / 1226 parsed rules (G1: 1220). Control date 01/06/2024: proposal values identical to G1.

### Trader (EI, IR, commerciale, indépendant, revenu professionnel 40 000 €/an) — G1 -> proposal, identical at 2024-12-01 and 2025-06-01 (PSS 2025 absent: 3 864 €/mois used)

| rule | G1 | proposal |
|---|---|---|
| assiette des cotisations | 40 000 | **29 600** (= 40 000 − 10 400) |
| CSG-CRDS . assiette | 52 788 | **29 600** |
| maladie . taux progressif | 5,92 % | **4,19 %** |
| maladie (maladie 1) / total | 2 168 / 2 368 | **1 092 / 1 240,24** |
| retraite de base . taux / amount | 17,75 % / 7 100 | **17,87 % / 5 290** |
| retraite complémentaire | 2 800 | 2 072 |
| invalidité et décès | 520 | 385 |
| indemnités journalières maladie | 200 | 148 |
| allocations familiales / formation professionnelle | 0 / 116 | 0 / 116 |
| CSG-CRDS | 5 121 | **2 871** |
| cotisations / total cotisations et contributions | 12 788 / 18 025 | **8 987 / 11 974** |

Probes (proposal, 01/12/2024): abattement 10 400 ; floor binds at revenu 2 000 (816,0768) ; ceiling binds at revenu 300 000 (60 278,4) ; maladie rate 0 / 0,75 / 2,75 / 6 / 7,03 / 8,1 / 8,5 % at 10 / 30 / 50 / 100 / 150 / 250 / 350 % PSS.

## 4. Abstentions (see answer.json `abstentions`)

1. **Which income lines enter the base** (L136-3 I 1°/2°, L131-6 I): the text does not say whether compulsory contributions, Madelin or spouse contributions are "charges"; the old add-back of contributions has no counterpart. The proposal reuses the library's line (`revenu professionnel + cotisations facultatives déductibles`) as a flagged PLACEHOLDER (`réforme assiette 2024 . assiette avant abattement`). Every "after" amount for the trader is conditional on it; the percentages and PSS shares are not.
2. Épargne-salariale deductions and revenus de remplacement in the base (L131-6 I): no input, not transposed.
3. Maladie rate at/above 300 % PSS: the text ends the reduction; the base rate (L621-3 I / D621-1) is outside the set. The 8,5 % above 300 % in the proposal is the mechanical extension of the last tranche.
4. Application to contribution years: only consolidated in-force dates are available (2023-12-28 / 2024-07-07); the LFSS 2024 art. 18 schedule is not in the corpus. Gating on 07/07/2024 is what makes the reform active at 2024-12-01 — NEEDS_REVIEW.
5. PSS 2025 absent; rounding of the maladie rate (library: 2 decimals) not stated by the text; minimum bases vs the abated base and the L633-1 cap of the floor; pre-existing D632-1 2024 floor mismatch (L0048 BROKEN) unresolved.
6. AE D613-4 / D613-6 2024-07-01 texts (now available) not transposed here: outside the T1b rule set; recorded in work/README.md for a later task. Their 2025/2026 versions still have no text.

## 5. Sophon

Snapshots S3 and G1 registered; revalidate S3×G1: 36 REASSESS_LAW_CHANGED (D613-4, D613-6, D621-2, D633-3 links), 1 BROKEN (L0048, pre-existing), D136-5 had no link. 35 links added (T1b-G01..G08 on G1: 5 FAILED, 1 INFERRED, 2 UNKNOWN; T1b-P01..P27 on the proposal copy P_T1b: 22 VERIFIED, 1 INFERRED, 3 UNKNOWN abstentions). Revalidate S3×P_T1b: 31 STILL_VERIFIED, no article without a link. `verify-store`: 109 links, no problems. Reports under `work/sophon/reports/T1b_*`.

## 6. Approval

None recorded. The corpus contains no sign-off, ratification or approval record; a merge, commit, package or test is not an approval.
