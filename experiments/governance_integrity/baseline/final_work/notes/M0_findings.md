# M0 findings (decision date 2025-10-01, law S6 legi-data 2.464.0 (2025-09-01) → S7 legi-data 2.469.0 (2025-10-01), rules G3 d6c374271727 committed 2025-12-30, modele-social 10.0.0)

## Law delta S6 -> S7 (work/law/S6_*, S7_*, M0_S6_S7_record_diff.json)
- Only D613-4 and D613-6 moved, and only in `articleVersions`: the 2026-01-01 versions announced since S1 (LEGIARTI000049624125 / LEGIARTI000049625445)
  became MODIFIE_MORT_NE with dateFin 2025-09-10; new VIGUEUR_DIFF versions LEGIARTI000052218738 (D613-4) / LEGIARTI000052218747 (D613-6) start 2026-01-01.
  Current texts (…097 / …405, 2025-01-01 → 2026-01-01), nota, lienModifications unchanged -> no text, no decree link for the 2026 versions. ABSTAINED on 2026.
- D633-3: two articleVersions entries swapped order (no content change). 9 other records byte-identical.
- S6 vs S5 (for the record, done this time): L136-3 re-issued LEGIARTI000051284498 (2025-02-28, LOI 2025-199 art. 13; III 26 % abattement, nota agricoles 2026);
  D613-4 current = …097 (2025-01-01, e) 24,6 %, b) 23,2 %), D613-6 current = …405 (e shares 3,40/3,50/47,60/13,00/32,50; b 9,30+0,90/1,40/23,45+5,35/25,60/34,00).

## Rules G3 (layout: modele-social/règles/dirigeant/auto-entrepreneur/{auto-entrepreneur,cotisations-et-contributions,exonérations,impôt}.publicodes)
- Names changed vs G0/G1: `… cotisations . service BNC . taux`, `… service BNC Cipav . taux`, `… service BIC . taux`, `… vente restauration hébergement . taux`;
  shares: `… <cat> . répartition . {maladie-maternité, invalidité-décès, retraite de base, retraite complémentaire, autres contributions} . taux de répartition`;
  DROM: `dirigeant . auto-entrepreneur . DROM . taux service BIC / taux service BNC / taux vente restauration hébergement / taux CIPAV` (public now);
  Acre: `dirigeant . auto-entrepreneur . Acre . taux Acre / taux service BNC / taux CIPAV / taux service BIC / taux vente restauration hébergement` (public);
  `dirigeant . auto-entrepreneur . Cipav` (affiliation CIPAV deprecated). TI rules: `dirigeant . indépendant . assiette des cotisations`, `… cotisations et contributions . {maladie, retraite de base, invalidité et décès, CSG-CRDS . assiette, exonérations . ACRE}`.
- G3 values: BNC 22 -> 21,1 (10/2022) -> 23,1 (07/2024) -> 24,6 (01/2025) -> 26,1 % (01/2026); BNC shares with 07/2024, 01/2025, 01/2026 branches (2026: 3/3,25/44,85/17,7/31,20);
  Cipav 21,2 -> 23,2 (07/2024), shares 10,20/1,40/28,8/25,60/34 from 07/2024; BIC 21,2; vente 12,3; a/d shares 8,90/3,10/41,80/16,50/29,70.
  DROM BNC 3,6/10,6/14,1 -> 3,9/11,6/15,4 (07/2024) -> 4,1/12,3/16,4 (01/2025) -> 4,4/13,1/17,4 (01/2026); DROM Cipav 7,1/10,6/14,2 (never updated: pre-existing mismatch vs ceil10(1/3 x 23,2) = 7,8/11,6/15,5);
  DROM BIC 3,6/10,6/14,2, vente 2,1/6,2/8,2. Acre = taux Acre (50 % if durée < 1 an; older grids) x rate, arrondi 1 déc. (BNC: 2 déc. from 01/2026 -> 13,05 %); Acre Cipav constant 13,90 % since 07/2024 (12,10 before).
  RCI `revenu cotisé auto-entrepreneur` = répartition . retraite complémentaire with contexte ACRE: non (BNC 2025: 383,76 €/an at 1 000 €/mois).
- At 01/10/2025 every AE value equals the S7 in-force text. The 2026 branches rest on no text in S6/S7 (the only 2026 version ever recorded, …125, is mort-né).
- Stale citation in G3: `service BNC Cipav . répartition . références` -> LEGIARTI000043656780 (2021 version). Fixed in proposal M0.

## Engine facts learned
- ACRE for AE needs BOTH `dirigeant . exonérations . ACRE: oui` AND `dirigeant . auto-entrepreneur . éligible à l'ACRE: oui` (+ `entreprise . durée d'activité . en début d'année < 1 an`, computed from `entreprise . date de création` and `date`); set `entreprise . durée d'activité` too (real-clock pitfall).
- BIC service: nature 'artisanale' + `entreprise . activités . service ou vente: 'service'`; BNC non-Cipav: nature 'libérale' + création >= 2018; Cipav: `entreprise . activité . nature . libérale . réglementée: oui`.
- Notification rule pattern builds fine on publicodes 1.10.4: `type: notification`, `sévérité: avertissement`, `valeur: date >= 01/2026`, as a child in `avec:`; evaluates to false/true; unknown-rule error on the untouched tree.
- Tools: run_checks.sh (spec -> jsonl), table_M0.mjs (compact table), compare_results.mjs (cell diff), make_answer_M0.mjs (quotes cut by [start,end] window from articles.json -> exact by construction; engine values read from results files).

## Decisions
- NEEDS_REVIEW (medium): the 4 rate rules, 20 share rules, RCI revenu cotisé AE, 4 DROM rates, 4 Acre rates (all depend on D613-4/D613-6 from 2026-01-01, text absent).
- UNAFFECTED (high): `… cotisations`, `… cotisations et contributions`, `retraite . base . cotisée . revenu auto-entrepreneur`, `dirigeant . exonérations . ACRE`, `Acre . taux Acre`
  (re-evaluated), and all `dirigeant . indépendant …` rules (NOT re-evaluated: their articles are byte-identical S6/S7 and unrelated to L613-7).
- Proposal M0 = documentation + notification only (no numeric change); 428 + 104 cells identical G3 vs proposal; build 1427 -> 1428 parsed.
- no_change_needed: false (flag + citations), with explicit statement that no numeric change is justified today.

## TO DO when the next snapshot / pin arrives
1. `node work/law/compare_snapshots.mjs <new articles.json> work/law/S7_index.json work/law/S7_texts.md S8`. Look for the TEXT of LEGIARTI000052218738 (D613-4) and
   LEGIARTI000052218747 (D613-6) and their lien (decree of ~2025-09). Then compare rows a–e and the shares with the G3 (or newer pin) 2026 branches:
   BNC 26,1 %; shares 3/3,25/44,85/17,7/31,20; DROM BNC 4,4/13,1/17,4 (= ceil10 of 1/6, 1/2, 2/3 x rate); Acre BNC 13,05 % (2 déc.); Cipav/BIC/vente carried 23,2/21,2/12,3 and their shares.
   If the text differs, edit those branches (dates `date >= 01/2026`) and drop/adjust the notification `taux 2026 à confirmer`.
2. Still open (pre-existing): DROM Cipav rates (7,1/10,6/14,2) vs 1/3 fraction; Acre Cipav 13,90 % source; D613-4 c) meublés, D613-5 conjoint, D756-5 II cap not implemented;
   D632-1 floor (T0-P1); L136-3 III 26 % abattement / D136-5 floor-cap implementation at the pin in use (T1b/R5 lines).
3. work/law also holds S9/S10 (2026, from the R4/R5 lines). They are later than 2025-10-01 and were not used in M0; use them only when the task's world date allows.
