# T0 findings (decision date 2024-05-25, law S0, rules G0 d9242882f96b 2024-05-15, modele-social 2.1.0)

## Binding map (article -> rule) — details and engine evidence in output/answer.json of T0
- D613-4 (LEGIARTI000046714712, 2022-12-10): a 12,3 -> `… cotisations . taux vente restauration hébergement`; b 21,2 -> `… cotisations CIPAV . taux`;
  d 21,2 -> `… taux service BIC`; e 21,1 -> `… taux service BNC` (all under `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations`).
  c (meublés de tourisme 6 % / 87 %) NOT implemented. Rule switch date 10/2022 (old 22/22/12,8) — old version text not in snapshot.
- L613-7 (LEGIARTI000048683570, 2023-12-28): I structure -> `… cotisations`; I al.2 (Acre rate by decree) -> `… cotisations . taux ACRE` (privé; 50 % -> 10,6/10,6/6,2; CIPAV 12,1 fixed);
  II abatements 71/50/34 -> `protection sociale . retraite . base . cotisée . revenu auto-entrepreneur` (via `entreprise . imposition . régime . micro-entreprise . revenu abattu`).
  Minimum-contribution option, meublés dérogation, III cessation: not implemented.
- D613-6 (LEGIARTI000046714699, 2022-12-10): only the 16,50 % RC share is used -> `protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur` (2,03 % / 3,50 % hard-coded; third product uses `service BIC` x 0 % — intended `service BNC`).
- D613-5 (LEGIARTI000041918205): conjoint collaborateur du micro — not implemented.
- D756-5 (LEGIARTI000034726710, 2017-05-12): `dirigeant . auto-entrepreneur . DROM . {service BIC, taux service BNC, taux vente restauration hébergement, taux CIPAV}`;
  première période = trimestres civils <= 8; seconde période = années civiles <= 3. Rates = ceil10(fraction x D613-4 rate): 2,1/3,6/3,6/7,1 ; 6,2/10,6/10,6/10,6 ; 8,2/14,2/14,1/14,2. II (cap at micro threshold) not implemented. DROM makes ACRE non applicable.
- D131-6-1 (LEGIARTI000036475110, 2018-01-01): `dirigeant . exonérations . ACRE` (applicable if durée en début d'année < 1 an; AE: < 3 ans & création < 04/2020), `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE` (+ . taux: 100 % <= 0,75 PSS, linear to 0 at PSS; . prorata sur l'année), `… PSS proratisé`.
- D621-2 (LEGIARTI000046714747, 2022-12-10): `… maladie . taux progressif` 0,5 % (<=40 % PSS) -> 4,5 % (60 %) -> 7,20 % (110 %, T3 from D621-1, outside set). `maladie . total` additionally floors the assiette at `assiette minimale . maladie` (40 % PSS) — source outside set.
- D632-1 (LEGIARTI000041966755, 2020-05-25): `… invalidité et décès . assiette` = assiette des cotisations, plancher `assiette minimale . retraite`, plafond PSS. MISMATCH since 2023 (450 h SMIC = 5243 vs 11,5 % PSS = 5332,32). Proposal in work/proposals/T0.
- D633-3 (LEGIARTI000041967101, 2020-05-25): `… retraite de base` barème 17,75 % (= 17,15 + 0,60) up to PSS, 0,6 % above. Equivalent.
- L131-6 (LEGIARTI000048683707, 2023-12-28) / L136-3 (LEGIARTI000048683641, 2023-12-28): G0 keeps the pre-reform logic: `dirigeant . indépendant . assiette des cotisations` = revenu professionnel (+ facultatives déductibles), `… CSG-CRDS . assiette` = that + cotisations (+ conjoint) - revenus étrangers - IJSS imposable. No 26 % abatement; dividends > 10 % not modelled (no rule mentions dividends in indépendant.publicodes). Applicability date depends on LOI 2023-1250 art. 18 (outside set) — WATCH THIS in later tasks (expected: 2025 contributions).
- D136-5: missing from snapshot.

## Engine facts (publicodes via src/publicodes_eval.mjs)
- PSS rule: 3864 €/mois (2024), 3666 (2023), 3428 (before). SMIC used for assiette minimale retraite 2024: 5243 €/an = 450 h x 11,65.
- `entreprise . durée d'activité` = durée depuis date de création jusqu'à the REAL system date (today), not `date`. `… en début/fin d'année` follow `date`. Default `date: 06/01/2024`.
  => set `entreprise . durée d'activité`, `… trimestres civils`, `… années civiles` directly in situations for Acre/DROM tests.
- Missing `entreprise . date de création` makes CIPAV micro cotisations = 12,1 % even with ACRE: non. Always set it. BNC non-CIPAV needs création >= 01/2018.
- `remplace` rules apply when evaluating the replaced rule directly (DROM/Acre rates are visible on `taux service BNC` etc.).
- Capped values print in the cap's unit (3864 €/mois = 46368 €/an).
- Situations that worked: see work/engine/checks_T0_ae3.json (AE), checks_T0_ti.json (TI, uses `dirigeant . indépendant . revenu professionnel` override).

## Regression fixtures at G0 (existing_tests/site/test/regressions/auto-entrepreneur.yaml)
- échelle de revenus, aides (ACRE), impôt (versement libératoire), ACRE (création période . début d'année / 01/06/2023), activités (6 natures), activité mixte, DROM (4 cases setting trimestres civils / années civiles directly). Snapshot values consistent with engine.

## Open questions / to re-check in later tasks
1. Any decree after 2024-05-25 changing D613-4 (esp. BNC e) and CIPAV b) rates) — none in this corpus; if a later snapshot adds one, compare `taux service BNC` / `cotisations CIPAV . taux` and their date variations.
2. Entry into force of the unified base / 26 % abatement (L131-6, L136-3 2023-12-28 versions) — needs LOI 2023-1250 art. 18 or a later consolidated text.
3. D632-1 floor mismatch (proposal T0-P1) — check whether the rules side fixes it.
4. CE decision 471203 (annulment on D613-4 / D613-6) — effect unknown from the snapshot.
5. D613-6 shares, D613-5 conjoint, D613-4 c meublés, D756-5 II cap: still not implemented at G0.


## Addendum — dividends (L136-3 II 2°)

A late grep found a 10 % threshold in `bénéficiaire.publicodes`: `bénéficiaire . dividendes . cotisations et contributions . assiette forfaitaire max indépendant` = (capital social + compte courant d'associé) x 10 % and `… assiette régime indépendant` = bruts - min(bruts, that), block marked [TODO] [dividendes-indep]. Engine run (EI at IS, rémunération nette 30 000, capital 10 000, dividendes bruts 5 000, 01/01/2024): all three dividend rules returned null (non applicable) and `dirigeant . indépendant . assiette des cotisations` = 31 183,89 with or without the dividends. So the check is inconclusive (status INFERRED, confidence low) and the provision stays in not_observable; primes d'émission and the family-member extension are not modelled anyway. Next time: find the company situation (catégorie juridique SARL/EURL, associés) that activates `bénéficiaire . dividendes`. Results in work/engine/results_T0_dividendes.json.
