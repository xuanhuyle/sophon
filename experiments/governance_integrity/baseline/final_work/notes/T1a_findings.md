# T1a findings (decision date 2024-06-01, law S1 legi-data 2.361.0, rules still G0 d9242882f96b)

## Law delta S0 -> S1 (work/law/compare_snapshots.mjs; S1 kept in work/law/S1_index.json + S1_texts.md)
- D613-4: LEGIARTI000046714712 -> LEGIARTI000049623867 (ABROGE_DIFF, 2024-06-01 -> 2024-07-01), décret n°2024-484 du 30 mai 2024 art. 1 (JORF 2024-05-31).
  Rate table IDENTICAL (12,3 / 21,2 / 6 / 21,2 / 21,1 %), only spacing differs. Future versions WITHOUT text:
  LEGIARTI000049624068 (2024-07-01, recorded end 2025-05-01 = overlap glitch), LEGIARTI000049624097 (2025-01-01), LEGIARTI000049624125 (2026-01-01).
- D613-6: LEGIARTI000046714699 -> LEGIARTI000049623885 (ABROGE_DIFF, 2024-06-01 -> 2024-07-01), same décret art. 2. Text IDENTICAL. Future versions WITHOUT text:
  LEGIARTI000049625264 (2024-07-01), LEGIARTI000049625405 (2025-01-01), LEGIARTI000049625445 (2026-01-01).
- lienModifications of both lost the 2022 decree link and the CE annulment link (décision 471203). All other 9 articles unchanged; D136-5 still missing.

## Decisions taken
- AFFECTED (medium): the 4 D613-4 rate rules (taux service BNC / cotisations CIPAV . taux / taux service BIC / taux vente restauration hébergement) — symmetric, since the text does not say which rows change later.
- NEEDS_REVIEW (medium): taux ACRE (private rule, 50 % x rate + 12,10 % CIPAV constant), DROM . {service BIC, taux service BNC, taux vente…, taux CIPAV} (D756-5 fractions), RCI . revenu cotisé auto-entrepreneur (16,50 % x rate).
- Everything else UNAFFECTED (high).
- Proposal T1a (work/proposals/T1a, diff T1a.diff): notes + `date >= 06/2024` branches with SAME values, plus notification rule
  `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux à confirmer` (true from 07/2024). Build OK 639/1173. No numeric change.
- ABSTAINED on 01/07/2024, 01/01/2025, 01/01/2026 for all rate rules and RCI: governing versions have no text in S1. Did NOT use any outside knowledge of the decree's figures.

## Engine facts learned
- Private rules (`privé: oui`): taux ACRE and its children, DROM . première/seconde période — `list` hides them, `evaluate` errors ("règle privée"). Observe via the public rate rules.
- BIC service situation MUST set `entreprise . activités . service ou vente: 'service'` (nature 'artisanale' alone => vente rate 12,3 %, cotisations 1476 €/an). With it: 21,2 %, 2544 €/an, CC 220 €/mois, RCI revenu 420 €/an, retraite base revenu 6000 €/an.
- Reference values at G0 (1000 €/mois, no ACRE, no DROM, any of the 4 dates): BNC 21,1 % / 2532 €/an / 213 €/mois / base revenu 7920; CIPAV 21,2 % / 2544 / 214; vente 12,3 % / 1476 / 124 / RCI 243,6 / base 3480.
  ACRE 6 mois: 10,6 / 10,6 / 6,2 / CIPAV 12,1 %. DROM Q8: 3,6 / 3,6 / 2,1 / CIPAV 7,1 %.
- Specs: work/engine/checks_T1a_rates.json (6 situations x 4 dates), checks_T1a_sbic.json, checks_T1a_notif.json; results_T1a_*.jsonl (G0 and proposal). Printer: work/engine/print_results.mjs. Answer generator with quote verification: work/engine/make_answer_T1a.mjs.

## TO DO when the next snapshot / rule pin arrives
1. Check whether the texts of LEGIARTI000049624068 / 097 / 125 (D613-4) and LEGIARTI000049625264 / 405 / 445 (D613-6) are now supplied. If yes: read the new rows a-e and shares, then add real `date >= 07/2024`, `01/2025`, `01/2026` branches in the 4 rate rules, recompute ACRE (50 %, CIPAV constant), DROM (ceil10 of 1/3, 1/2, 2/3 — 1/6 etc. for vente) and RCI constants (16,50 % share x rate), and drop/adjust the `taux à confirmer` notification.
2. If the rules side (new pin) already changed the rates: compare its values and dates against the text, not against memory; check it also updated DROM/ACRE/RCI derived constants.
3. Still open from T0: D632-1 floor mismatch (proposal T0-P1), unified base L131-6/L136-3 entry into force (LOI 2023-1250 art. 18, outside set), D613-4 c) meublés, D613-5 conjoint, D756-5 II cap, RCI BNC share (service BIC x 0 %).
4. D613-4 version date overlap (…068 ending 2025-05-01 vs …097 starting 2025-01-01): see whether legi-data fixes it.
