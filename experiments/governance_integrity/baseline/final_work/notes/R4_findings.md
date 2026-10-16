# R4 findings (decision date 2026-03-31, law S9 legi-data 2.514.0, rules: diff context trees modele-ti + modele-commun; G4 pin a61b72947fec = old single-package modele-social 10.0.1)

## Event
Commit d3e0cfe0f12d "chore: remplace la formule de la retraite de base par celle de l'Urssaf" (Alice Dahan, authored 2026-02-13, committed 2026-03-30).
Verdict LEGITIMATE_INDEPENDENT_CHANGE (medium). Non-CNAVPL retraite de base: 2 tranches (17.15 % <= PSS + 0.60/0.72 % total, each rounded) -> barème
(17.75/17.87 % <= PSS, 0.60/0.72 % above, rounded once). Algebraically identical to D633-3 (T1+T2)·min(A,P)+T2·max(A-P,0) = T1·min(A,P)+T2·A; engine: 73/81
identical, 8 differ by 1 € (rounding). CNAVPL branch moved to `indépendant . profession libérale . CNAVPL . retraite de base` (identical values).
`protection sociale . retraite . base . revenu cotisé` now divides by taux T1 (17.75/17.87) instead of 17.15 -> revenu cotisé, trimestres and pension estimate
change for all non-CNAVPL below PSS (R351-9/R634-1/D634-1/L161-17-3 outside the set). Full write-up: output/NOTES.md of R4; generator engine/make_answer_R4.mjs.

## Repo layout change (IMPORTANT for later tasks)
- The 2026 repo is split: `modele-ti/règles` (indépendant, protection sociale, entreprise TI) + `modele-commun/règles` (base, période, entreprise, impôt).
  Evaluate with `--rules <tree>/modele-ti/règles --rules <tree>/modele-commun/règles`. run_checks.sh now takes several dirs separated by "|".
- Rule names dropped the `dirigeant .` prefix: `indépendant . cotisations et contributions . cotisations . retraite de base`, `indépendant . revenu professionnel`,
  `indépendant . cotisations et contributions . assiette sociale`, `protection sociale . retraite . base . *`. `entreprise . activité` is a single choice
  ('artisanale'|'commerciale'|'libérale'); `entreprise . activité . libérale . réglementée: oui/non`; `indépendant . profession libérale . réglementée . métier`
  ('santé'|'juridique'|'expert-comptable'|'rattaché Cipav'), `… métier . santé` ('médecin'…), `… médecin . secteur` ('S1'…).
- Reform is in: `indépendant . cotisations et contributions . après réforme: date >= 01/2025`; post-reform `assiette sociale` = `assiette CSG-CRDS` = `revenu brut`
  abattu 26 % (+ IJSS, revenus étrangers) -> set BOTH `indépendant . revenu professionnel` (pre-2025 path) and `indépendant . revenu brut` (2025+ path) and
  `entreprise . imposition . IR . régime micro-fiscal: non`, otherwise 2025+ values are null. PSS: 3 864 (2024), 3 925 (2025), 4 005 €/mois (2026).
- PLNR created before 2018 (date de création 01/01/2015) -> `profession libérale . CNAVPL` = true (Cipav); created 2020 -> false (régime général branch).
- Assiette minimale retraite = 450 SMIC h (5 243 € in 2024, 5 346 € in 2025, 5 409 € in 2026). `revenu cotisé` capped at `plafond sécurité sociale` returns
  "3 864 €/mois" (unit quirk, both trees).
- The G4 pin (inputs/rules/G4_a61b72947fec) is still the OLD layout (modele-social/règles/…, no dirigeant/indépendant.publicodes found at that path); the diff's
  parent tree is a later, restructured state. Use the diff's context trees, not the pin, for such commits.

## Engine facts learned
- publicodes chainable order (dist l.4258): contexte, variable manquante, avec, applicable si, non applicable si, arrondi, unité, simplifier unité, plancher, plafond,
  par défaut, situation, résoudre référence circulaire, abattement = OUTERMOST first -> value is computed, then abattement, then plafond, then plancher, then arrondi.
  So `plancher` is applied AFTER `plafond`; moving a `plafond` to a consuming rule is value-neutral when plancher <= plafond.
- `barème` with `multiplicateur` and `plafond: 1` = one PSS; rounding once vs per-tranche gives ±1 € differences in ~10 % of cases.
- Dividing a rounded cotisation by its rate loses up to 0.5 €/rate: at the minimum base 955/17.87 % = 5 344 < 5 346 -> trimestres 3 -> 2 in 2025 (after tree).

## Law S9 vs S5 (compare_snapshots.mjs; work/law/S9_index.json + S9_texts.md)
- D633-3 LEGIARTI000049904636 unchanged (17,15 % / 0,72 %, periods from 2025-01-01). Pre-2025 version LEGIARTI000041967101 text-less.
- D632-1, D136-5, D621-2, D613-5, D756-5 unchanged.
- D613-4 -> LEGIARTI000052218738 (VIGUEUR 2026-01-01, décret 2025-943 art. 1, applies from 2026-01-01); the former text-less 2025/2026 ids are MODIFIE / MORT_NE.
- D613-6 -> LEGIARTI000052218747 (VIGUEUR 2026-01-01, same decree; text len 2400 -> 3061).
- D131-6-1 -> LEGIARTI000053451315 (VIGUEUR 2026-01-01, décret 2026-69 art. 1; applies to créations/reprises from 2026-01-01).
- L136-3 -> LEGIARTI000051284498 (2025-02-28, loi 2025-199 art. 13; nota: agricoles from 2026-01-01). L131-6, L613-7 unchanged (liens only).
  => TO DO next: read the new D613-4 / D613-6 / D131-6-1 texts (S9_texts.md) and check the auto-entrepreneur rules of the current tree against them.

## Files
checks_R4_rb.json (81 checks x 25 rules), make_checks_R4.mjs, results_R4_{parent,after}_rb.jsonl, log_R4_*_rb.txt, table_R4_rb.txt, list_R4_context_*.json,
make_answer_R4.mjs [tool_calls]. No proposal (the change is legitimate); flags for maintainers in output/NOTES.md §5.
