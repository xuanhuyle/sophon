# T0 — initial binding of the bounded CSS articles to modele-social at G0 (decision date 2024-05-25)

Law snapshot S0 = legi-data 2.360.0 (published 2024-05-25T23:36Z), 11 articles present, **D136-5 missing** from the snapshot.
Rules pin G0 = d9242882f96b (2024-05-15), 45 files, 639 top-level / 1172 parsed rules, native build OK.
System of record: `work/sophon/store` (55 links L0001–L0055, every quote verified by the store against the S0 text, every number checked by running the engine). Reports: `work/sophon/reports/` (evidence table, revalidate baseline, as-of 2024-05-25, verify-store). Spec of the links: `work/sophon/links_T0.json`; raw engine runs: `work/evals/`.

## Method
1. Dumped the articles (`work/law/S0_dump.txt`), read the four rule families: `dirigeant . auto-entrepreneur . …` (auto-entrepreneur.publicodes), `dirigeant . auto-entrepreneur . DROM` + AE Acre (auto-entrepreneur/exonérations.publicodes), `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE` (dirigeant/exonérations.publicodes), the indépendant base/maladie/retraite/invalidité rules (indépendant.publicodes), and the conjoint-collaborateur file.
2. For each provision that states a number, built a situation and ran `publicodes_eval.mjs evaluate`; compared to the number derived from the article text only.
3. Recorded each link with `sophon link add` (quote = exact substring extracted by regex from the real text; checks re-runnable). The store confirmed 34 VERIFIED, 2 FAILED, 11 INFERRED, 8 UNKNOWN (answer.json reports 34 VERIFIED, 3 FAILED, 10 INFERRED, 8 UNKNOWN because the Acre E-base deviation is stored INFERRED but reported FAILED).

### Engine caveat that shapes every period check
`durée` (publicodes) without `jusqu'à` counts up to the **real clock date**, not the situation `date`: with `entreprise . date de création = 01/07/2022` and `date = 01/05/2024` the engine reported 18 civil quarters (= up to today, 2026). `entreprise . durée d'activité`, `. trimestres civils`, `. années civiles` are affected, hence the AE Acre grille (`taux ACRE`) and the DROM periods. The rules `… en début d'année` / `… en fin d'année` use `période . début/fin d'année` and are fine. All DROM/AE-Acre checks therefore set the duration rules directly in the situation (`"entreprise . durée d'activité . trimestres civils": "8 trimestre civil"`, `"… années civiles": "2 année civile"`, `"entreprise . durée d'activité": "270 jour"`), which makes them deterministic on revalidation. Private rules (`taux ACRE`, `DROM . première période`) cannot be evaluated from the CLI; the public rules they replace were evaluated instead.

## Results by article

### D613-4 (LEGIARTI000046714712, in force 2022-12-10) — AE global rates
VERIFIED at 01/05/2024: `taux service BNC` 21,1 % (row e), `taux service BIC` 21,2 % (row d), `taux vente restauration hébergement` 12,3 % (row a), `cotisations CIPAV . taux` 21,2 % (row b); amount `cotisations` = 12 000 × 21,1 % = 2 532 €/an.
**FAILED (bug):** CIPAV-affiliated AE (`libérale . réglementée = oui`) created on/after 01/04/2020 pays **1 452 €/an = 12,1 %** on 12 000 € CA even with `dirigeant . exonérations . ACRE = non` (expected 2 544 = 21,2 %). Created 01/01/2019 → 2 544 (OK). Cause: `taux ACRE . CIPAV` (`remplace: cotisations CIPAV . taux`, `si date de création >= 01/04/2020 alors 12.10%`) is applied although its parent `taux ACRE` is not applicable; the 12,1 % is the Acre CIPAV rate. Fix to propose in a later task: guard that replacement with `applicable si: dirigeant . exonérations . ACRE` (not done here: budget). Row c) (meublés de tourisme 6 %) is not implemented (UNKNOWN). Rates before 10/2022 in the library (22/22/12,8) correspond to a prior article version whose text is not in the snapshot → abstain.
Nota: CE decision n° 471203 (2024-02-09) annuls the last column of row e) and the last two paragraphs of D613-6 for not including a 7 % retraite complémentaire share — no replacement value in the snapshot → abstain; watch for a new version.

### L613-7 (LEGIARTI000048683570, in force 2023-12-28)
INFERRED: contributions = CA × global rate per category (`… cotisations`), 'different global rate' during exemption periods = DROM rates / AE Acre. VERIFIED: 34 % abattement (`revenu abattu` = 7 920 on 12 000) — note this is the fiscal rule; the article uses the abattement for benefits. UNKNOWN/not implemented: minimum-contribution option, floor of the global rate, end of regime (III). The AE Acre rate (50 %, CIPAV 12,1 %) is fixed by a decree article outside the set → value unverifiable (INFERRED, low).

### D756-5 (LEGIARTI000034726710, in force 2017-05-12) — DROM AE rates
All 12 values VERIFIED as fraction × D613-4 rate, rounded **up** to 0,1 % (`après arrondi au dixième de pour cent supérieur`): period 1 (8 civil quarters: `trimestres civils <= 8` matches 'fin du septième trimestre civil qui suit celui … de l'affiliation') 1/6 → 3,6 / 3,6 / 2,1 and 1/3 (CIPAV) → 7,1; period 2 (to end of 3rd civil year) 1/2 → 10,6 / 10,6 / 6,2 / 10,6; from the 4th civil year 2/3 → 14,1 / 14,2 / 8,2 / 14,2. Confidence medium: the article still cites `D. 131-6-1` (now the Acre article) and `L. 133-6-8` (old L613-7) — the library applies the fractions to D613-4, which is the only reading that makes sense but is an inference. The 1/6-vs-1/3 split is keyed on `affiliation CIPAV` while the text says '2° de l'article L. 611-1' (outside the set). II (CA cap at micro thresholds) not implemented. DROM makes `exonérations . ACRE` non applicable (library choice).

### D131-6-1 (LEGIARTI000036475110, in force 2018-01-01) — Acre (indépendants; 12-month duration also for AE)
VERIFIED: 12 months (`ACRE . prorata sur l'année` = 50 % for a company created 01/07/2023 at 01/07/2024; AE created 400 days ago → full rate 21,1 % again); full exemption ≤ 3/4 PSS (`ACRE . taux` = 100 %; `retraite de base`, `maladie`, `invalidité et décès` = 0 at 20 000 €/an); degressive formula (`ACRE . taux` = 50 % at R = 87,5 % PSS = 40 572 €/an; 0 % above the PSS). INFERRED: retraite complémentaire not exempted (1 400 remains), PSS prorated for a partial year (23 375 = 184/365 of 46 368; article silent on day count), annual PSS of 1 January (value from the library, L241-3 outside).
**FAILED (deviation):** in the 75–100 % PSS zone the article's amount is `E/0,25 PSS × (PSS−R)` with **E fixed at the contribution due for 3/4 PSS**; the engine applies the same fraction to the contribution due at R (observed Acre maladie exemption 1 114 = 50 % × 2 228 at R = 40 572). Since the maladie rate increases with R, the engine over-exempts in that zone. No single expected number asserted (E depends on the maladie/IJ split) — the mismatch is structural and executable.

### D621-2 (LEGIARTI000046714747, in force 2022-12-10) — reduced maladie rate
VERIFIED (`maladie . taux progressif`, 2024): 0,50 % at 9 000 €/an (< 40 % PSS); 2,5 % at 23 184 (= 50 % PSS, formula 2°); 4,5 % at 27 821 (= 60 % PSS). INFERRED: 60–110 % linear to T3 (library 7,20 %; T3 is D621-1, outside the set; observed 5,99 % at 87,5 % PSS). UNKNOWN: full rate above 110 % (7,20 % from outside the set).

### D632-1 (LEGIARTI000041966755, in force 2020-05-25) — invalidité-décès base
VERIFIED: cap at the PSS (assiette = 3 864 €/mois = 46 368 €/an at 60 000 €/an); floor 11,5 % PSS in 2022 (4 731 = 11,5 % × 41 136).
**FAILED:** in 2024 the floor is 5 243 (= `assiette minimale . retraite` = 450 h × 11,65 € SMIC since `date >= 01/2023`) instead of 11,5 % × 46 368 = 5 332 required by the article as in force. The library changed the retraite floor in 2023 and the invalidité-décès rule reuses it; D632-1 itself is unchanged since 2020-05-25 in this snapshot. The 1,3 % rate is outside the set.

### D633-3 (LEGIARTI000041967101, in force 2020-05-25) — retraite de base
VERIFIED: the library's 17,75 % first tranche + 0,6 % second tranche equals I (17,15 % up to PSS) + II (0,60 % on all income): 1 598 at 9 000 €/an; 8 312 at 60 000 €/an (17,15 % × 46 368 + 0,60 % × 60 000). The minimum base (floor) is outside the set.

### D613-6, D613-5, L131-6, L136-3 — recorded as UNKNOWN 'watch' links
D613-6 répartition of the AE forfait: not implemented. D613-5 conjoint collaborateur of an AE (58 %/46 %): not implemented (`conjoint collaborateur . cotisations` = null in an AE situation). L131-6 I and L136-3 III in force since 2023-12-28 describe the **2025 unified base with 26 % abattement** (nota: periods from 2025-01-01); G0 implements the pre-2025 regime (base = revenu professionnel + Madelin déductibles; CSG base = revenu + cotisations) whose text version is not in the snapshot → abstain on verifying G0's base against text. Épargne salariale deductions and IJ inclusion (L131-6 I) not implemented; L136-3 IV not implemented. L136-3 II (IS dividends > 10 % of capital) was not examined in this task.

## Approvals
None recorded: the corpus contains no legal sign-off, ratification or approval file. Commits, the published package 2.1.0 and the regression snapshots are not approvals.

## Status vocabulary in answer.json
VERIFIED / INFERRED / UNKNOWN as requested; **FAILED** added for the three links where an executable check exists and does not reproduce the article (same word as the store). `store_status` shows what the store recorded (the Acre E-base deviation is stored INFERRED because no single expected number could be asserted).

## For the next tasks
- Run `snapshot-law` / `snapshot-rules` for the new ids, then `revalidate` (baseline in `work/sophon/reports/T0_revalidate_baseline`), then look at `articles_without_any_link` and the nota-announced changes (CE 471203 on D613-4/D613-6; LFSS 2024 art. 18 on L131-6/L136-3/L613-7 for 2025).
- Open bugs to propose fixes for (in `work/proposals/<task>/…`): CIPAV 12,1 % leak; invalidité-décès floor; Acre degressive base.
- Tool calls used in T0: 26 (incl. this correction and the final hand-back). Details of engine quirks and standard situations: `work/README.md`.
