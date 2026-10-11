# T0 — initial binding of the bounded CSS articles to modele-social (G0), decision date 2024-05-25

## What I did

1. Read the law snapshot S0 (legi-data 2.360.0, published 2024-05-25). 11 of the 12 requested articles have a
   current-version text; **D136-5 is missing from the snapshot** (`articles_missing_in_snapshot`). Full texts and an
   index of versions/modifications are kept in `work/law/S0_texts.md` and `work/law/S0_index.json`.
2. Read the rule files that matter for the four areas (micro-entrepreneur contributions, DROM override, Acre,
   indépendant contribution base): `dirigeant/auto-entrepreneur/*.publicodes`, `dirigeant/exonérations.publicodes`,
   `dirigeant/indépendant.publicodes`, `dirigeant/dirigeant.publicodes`, plus `protection-sociale.publicodes` and
   `entreprise/imposition.publicodes` where the micro abatements live.
3. Built the tree with the organisation's engine (`build`: 639 raw / 1172 parsed rules, no error) and ran ~60
   evaluations through a small reusable runner (`work/engine/run_checks.sh`, specs `checks_T0_*.json`, results
   `results_T0_*.jsonl`). Every number quoted in `answer.json` comes from one of those runs.
4. Made one disposable proposal (`work/proposals/T0`) for the single mismatch found, built it and compared outputs.

## How the articles bind (summary)

| Article (version, in force) | Rule(s) | Result |
|---|---|---|
| D613-4 (LEGIARTI000046714712, 2022-12-10) a/b/d/e | `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux vente restauration hébergement` 12,3 ; `cotisations CIPAV . taux` 21,2 ; `taux service BIC` 21,2 ; `taux service BNC` 21,1 | **VERIFIED** at 01/07/2024 (CA 1000 €/mois → 1476 / 2544 / 2544 / 2532 €/an) |
| D613-4 c (meublés de tourisme 6 %) | none | not implemented |
| L613-7 I (CA × taux global, monthly/quarterly) | `… cotisations` | INFERRED (structure; numbers come from D613-4) |
| L613-7 I al. 2 (different rate during exemption) | `… cotisations . taux ACRE` (privé) → replaced rates 10,6 / 10,6 / 6,2 ; CIPAV 12,1 | INFERRED, value abstained: the Acre micro rates are in D131-6-2, outside the set |
| L613-7 II (abattements 71/50/34 % for benefits) | `protection sociale . retraite . base . cotisée . revenu auto-entrepreneur` (= `entreprise . imposition . régime . micro-entreprise . revenu abattu`) | VERIFIED: 3480 / 6000 / 7920 for CA 12 000 |
| D613-6 (16,50 % share to RC for a/d) | `protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur` (2,03 % / 3,50 % hard-coded) | VERIFIED up to rounding (243,6 vs 243,54 ; 420 vs 419,76); other shares not implemented |
| D613-5 (conjoint collaborateur du micro) | none | not implemented |
| D756-5 (DROM fractions 1/6–1/3, 1/2, 2/3, rounded up to 0,1) | `dirigeant . auto-entrepreneur . DROM . *` | VERIFIED for all 12 rates and both period boundaries (trimestres civils 8→9, années civiles 3→4). Caveats: D756-5 cites stale articles (L133-6-8, D131-6-1); the 1/6 vs 1/3 split depends on L611-1 (outside) |
| D756-5 II (cap at micro threshold) | none | not implemented |
| D131-6-1 (Acre: 12 months, total ≤ 3/4 PSS, linear to 0 at PSS, prorated PSS, scope) | `dirigeant . exonérations . ACRE`, `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE (. taux, . prorata sur l'année)`, `… PSS proratisé` | VERIFIED (100 % at 0,75 PSS; 50 % at 0,875 PSS; 0 % at PSS; prorata 50 % for a 01/07/2023 creation seen in 2024; PSS proratisé 23 375 for a 01/07/2024 creation; maladie / retraite de base / invalidité-décès / AF / IJ zeroed, retraite complémentaire and CSG untouched) |
| D621-2 (sickness rate 0,5 % < 40 % PSS; linear to 4,5 % at 60 %; linear to T3 at 110 %) | `… maladie . taux progressif` | 0,5 / 2,5 / 4,5 / 110 % ceiling VERIFIED; T3 (rule: 7,20 %) UNKNOWN — D621-1 not in the set |
| D633-3 (17,15 % ≤ PSS + 0,60 % total) | `… retraite de base` (17,75 % then 0,6 %) | VERIFIED (3550 at 20 000; 8312 at 60 000; 9152 at 200 000) — arithmetically equivalent encoding |
| D632-1 (ID base = L131-6 income capped at PSS, floor 11,5 % PSS) | `… invalidité et décès . assiette` | cap VERIFIED; floor VERIFIED for 2022 (4731) but **MISMATCH from 2023**: 5243 (450 h SMIC) instead of 5332,32 in 2024 |
| L131-6 / L136-3 (versions in force 2023-12-28: unified base, 26 % abatement) | `dirigeant . indépendant . assiette des cotisations`, `… CSG-CRDS . assiette` | UNKNOWN / INFERRED: at G0 the contribution base (20 000) ≠ CSG base (25 436) and no 26 % abatement exists; whether that is already required depends on LOI 2023-1250 art. 18 (outside the set) |

## The one mismatch and the proposal

`dirigeant . indépendant . cotisations et contributions . invalidité et décès . assiette` floors the base with
`assiette minimale . retraite`. Until 2022 that rule was 11,5 % of the PSS, which is exactly D632-1; since 01/2023 it is
450 h × SMIC (a basic-pension rule, source outside the set), so the ID floor drifted away from D632-1
(2024: 5 243 vs 5 332,32; contribution 68 vs 69 €/an at zero income). `work/proposals/T0/modele-social/règles` adds a
dedicated `assiette . minimale = plafond sécurité sociale × 11,5 %` under that rule; it builds (1173 parsed rules) and
gives 5 332 €/an in 2024, 4 731 in 2022 (unchanged), and unchanged values above the floor. No one has approved it
("none recorded").

## Things a future maintainer must know (also in work/notes)

* `entreprise . durée d'activité` is measured from `date de création` to the **real system clock**, not to the
  situation's `date`. With a 01/01/2024 creation the engine reports 1014 days today, so the micro Acre rate never fires
  unless `entreprise . durée d'activité` (and for DROM `… trimestres civils` / `… années civiles`) is set directly in
  the situation — which is what the project's own regression fixtures do. `… en début d'année` / `… en fin d'année`
  use `période . début/fin d'année` and therefore follow `date` (default `date: 06/01/2024` in période.publicodes).
* If `entreprise . date de création` is absent, the CIPAV micro contribution comes out at 12,1 % (the Acre CIPAV
  replacement) even with `dirigeant . exonérations . ACRE: non` (1452 instead of 2544 €/an for CA 12 000). Always
  provide a creation date; for a non-CIPAV BNC use a date ≥ 01/2018 (earlier dates make `affiliation CIPAV` true).
* `taux ACRE` and the DROM period rules are `privé`; observe them through the replaced rate rules.
* The engine wrapper reports capped values in the cap's unit (e.g. ID base at 1,1 PSS prints `3864 €/mois`).
* Nothing dated after 2024-05-25 exists here. Any later decree changing micro rates (BNC in particular) is **not** in
  this corpus and must not be assumed; the 21,1 % BNC rate is what D613-4 says on the decision date.
* No legal sign-off, ratification or approval record exists anywhere in the inputs: approval = "none recorded".

## Abstentions

* Acre micro rates (D131-6-2), T3 of D621-2 (D621-1), ID rate 1,3 %, PSS amounts, SMIC-based minima, Acre eligibility,
  the 2022 rate switch date, the LFSS-2024 entry-into-force clause, L611-1 categories for D756-5, R641-1 11° for CIPAV,
  CGI thresholds, and the effect of CE decision n°471203 (annulment flagged on D613-4/D613-6) are all outside the
  bounded set — observed values are reported, expected values are not asserted.
* Pre-2022-12-10 micro rates (engine: 22 / 22 / 12,8 %) are not asserted because the earlier D613-4 version
  (LEGIARTI000043656794) has no text in the snapshot.

Tool calls used for this task: see `self_reported_tool_calls` in answer.json (26 incl. this write; final count in the hand-back).


## Addendum — dividends (L136-3 II 2°)

A late grep found a 10 % threshold in `bénéficiaire.publicodes`: `bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire max indépendant` = (capital social + compte courant d'associé) x 10 % and `… assiette régime indépendant` = bruts - min(bruts, that), block marked [TODO] [dividendes-indep]. Engine run (EI at IS, rémunération nette 30 000, capital 10 000, dividendes bruts 5 000, 01/01/2024): all three dividend rules returned null (non applicable) and `dirigeant . indépendant . assiette des cotisations` = 31 183,89 with or without the dividends. So the check is inconclusive (status INFERRED, confidence low) and the provision stays in not_observable; primes d'émission and the family-member extension are not modelled anyway. Next time: find the company situation (catégorie juridique SARL/EURL, associés) that activates `bénéficiaire . dividendes`. Results in work/engine/results_T0_dividendes.json.
