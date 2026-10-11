# R5 findings (decision date 2026-10-05, law S10 legi-data 2.572.0 = S9 on all 12 articles; rules: diff context trees modele-ti + modele-commun)

## Event
Commit c14ee26d0c67 "fix: n'applique pas de plancher ni de plafond à l'abattement sur l'assiette à Mayotte" (Alice Dahan, 2026-07-06/09).
`assiette CSG-CRDS . abattement` (26 % x revenu brut): `plancher` 1,76 % PASS and `plafond` 130 % PASS get `non applicable si: … outre-mer . Mayotte`.
Verdict UNRESOLVED (medium): real semantic change (118/850 cells differ, all Mayotte post-reform), but no bounded article mentions Mayotte; whether
L136-3 III / D136-5 / L131-6 apply to Mayotte TI is settled by ordonnance 96-1122 & decrees (outside set). Full write-up: output/NOTES.md of R5.

## Mayotte model in the 2026 trees (useful for later Mayotte commits)
- Situation key: `établissement . commune . département: "'Mayotte'"` -> `établissement . commune . département . outre-mer . Mayotte` = true.
  `outre-mer` has `par défaut: non`; with département unset, Mayotte-dependent rules still evaluate (métropole values, flagged missing) - no regression risk.
- PSS Mayotte 2 821 €/mois (< 01/2026), 3 022 (2026); SMIC horaire Mayotte own series (modele-commun/base.publicodes). `PASS proratisé . métropole` exists
  because "pour certaines cotisations applicables à Mayotte, c'est quand même la valeur métropole du PSS qui est utilisée".
- `indépendant . cotisations et contributions . CSG-CRDS` non applicable at Mayotte (and if domiciliation fiscale à l'étranger).
- Mayotte-specific: `cotisations . exonérations . Mayotte` (notification, cites Urssaf taux-cotisations-ti-mayotte.html + CSSM leaflet), `exonérations . Mayotte 24 mois`,
  `taux Mayotte` variants in cotisations.publicodes, 50 % abattement on AF and maladie additionnelle, assiette minimale not applicable for non-CNAVPL Mayotte,
  DROM exonération excludes Mayotte, retraite de base `taux Mayotte`, impôt barème Guyane Mayotte.
- Floor/cap numbers: 2025 Mayotte 596 / 44 008 €/an (métropole 829 / 61 230); 2026 Mayotte 638 / 47 143 (métropole 846 / 62 478).
  Floor binds for RB < 2 292 €/an (596/0.26), cap binds for RB > 169 262 (Mayotte 2025).

## Engine facts
- `plancher:`/`plafond:` on a rule are mechanisms: `rule . plancher` is "introuvable" (not a rule). Evaluate the parent rule at binding revenues instead.
- publicodes `abattement` floors the result at 0 (RB 0, abattement 596 -> assiette 0, not negative).
- Rounding: `arrondi: oui` on abattement -> 595 for 26 % x 2 290 = 595.4.

## Law S10
All 12 records identical to S9 (ids, dates, text, nota). D613-4 LEGIARTI000052218738 / D613-6 LEGIARTI000052218747 / D131-6-1 LEGIARTI000053451315 (2026-01-01)
still TO CHECK against the auto-entrepreneur rules of the current tree (carried over from R4).

## Files
make_checks_R5.mjs, checks_R5_mayotte.json (34 x 25), results_R5_{parent,after}_mayotte.jsonl, log_R5_*, diff_R5_mayotte.txt, table_R5_mayotte.txt,
list_R5_context_*.json, make_answer_R5.mjs <tool_calls>. No proposal.
