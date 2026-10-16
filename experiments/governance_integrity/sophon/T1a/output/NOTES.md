# T1a — forward transposition after a governing change (decision date 2024-06-01) — arm B notes

Law snapshot S1 = legi-data 2.361.0 (published 2024-06-01), compared with S0 = legi-data 2.360.0 preserved in `work/` (store `work/sophon/store/law/S0.json`, dump `work/law/S0_dump.txt`). Rules pin G0 = d9242882f96b (unchanged).

## 1. What changed in the law (S0 -> S1)

Method: `work/scripts/compare_law.py` (id / etat / dates / versions / word-level text diff) and `diff` of the two human-readable dumps (`work/law/S0_dump.txt` vs `work/law/S1_dump.txt`). Sophon `revalidate --law-snapshot S1 --rules-snapshot G0` confirmed: `articles_changed = [D613-4, D613-6]`, all other links LAW_SAME.

| article | S0 version | S1 version | in force | modifying text (lienModifications) | text |
|---|---|---|---|---|---|
| D613-4 | LEGIARTI000046714712 (v3.0, 2022-12-10) | **LEGIARTI000049623867** (v4.0, etat ABROGE_DIFF) | 2024-06-01 .. 2024-07-01 | Décret n°2024-484 du 30 mai 2024 - art. 1 (JORFTEXT000049620955, JORF 2024-05-31; nota: in force 1 June 2024 per 1° of art. 1) | available; differs from v3.0 **only by whitespace** (4 x "l'article" -> "l' article"); table unchanged: a) 12,3 % · b) 21,2 % · c) 6 % · d) 21,2 % · e) 21,1 % |
| D613-4 | — | LEGIARTI000049624068 (v5.0, VIGUEUR_DIFF) | 2024-07-01 .. 2025-05-01 (sic: overlaps v6.0) | same decree (announced) | **not available** |
| D613-4 | — | LEGIARTI000049624097 (v6.0, VIGUEUR_DIFF) | 2025-01-01 .. 2026-01-01 | same decree (announced) | **not available** |
| D613-4 | — | LEGIARTI000049624125 (v7.0, VIGUEUR_DIFF) | 2026-01-01 .. | same decree (announced) | **not available** |
| D613-6 | LEGIARTI000046714699 (v4.0, 2022-12-10) | **LEGIARTI000049623885** (v5.0, ABROGE_DIFF) | 2024-06-01 .. 2024-07-01 | Décret n°2024-484 du 30 mai 2024 - art. 2 (nota: in force 1 June 2024 per 1° of art. 2) | available; **byte-identical** to v4.0 |
| D613-6 | — | LEGIARTI000049625264 (v6.0) / LEGIARTI000049625405 (v7.0) / LEGIARTI000049625445 (v8.0) | 2024-07-01 / 2025-01-01 / 2026-01-01 | same decree (announced) | **not available** |

Also gone in S1: the Conseil d'État nota and ANNULATION link (décision n°471203 du 9 février 2024) that S0 attached to D613-4 and D613-6. Unchanged (same id and text hash): L131-6, L136-3, L613-7, D131-6-1, D613-5, D621-2, D632-1, D633-3, D756-5. D136-5 is still missing from the snapshot.

Interpretation (stated as such): the decree re-versions both articles on 2024-06-01 without changing their substance, and schedules three further versions each. **Nothing in the corpus states what those later versions contain.** No value from outside the corpus was used anywhere in this task.

## 2. Rule classification (bounded set)

Policy: `AFFECTED` = the rule must be edited now because of S1; `NEEDS_REVIEW` = current value confirmed against the 2024-06-01 text, but a governing version with unknown text is announced inside the evaluation horizon; `UNAFFECTED` = governing articles LAW_SAME.

- **NEEDS_REVIEW (high)**: `… cotisations . taux service BNC` (21,1 %), `… taux service BIC` (21,2 %), `… taux vente restauration hébergement` (12,3 %), `… cotisations CIPAV . taux` (21,2 %), `… cotisations` (amounts 2 532 / 2 544 / 1 476 / 2 544 €/an for 12 000 €/an CA). Engine values (G0 and proposal) are identical on 01/06/2024, 01/07/2024, 01/01/2025, 01/01/2026; the text supports them **only for 01/06/2024**.
- **NEEDS_REVIEW (medium)**: `… taux prestation de service` (deprecated alias), `dirigeant . auto-entrepreneur . cotisations et contributions` (sum), the four `dirigeant . auto-entrepreneur . DROM . taux …` rules (fractions of D613-4 rates per D756-5, itself unchanged).
- **AFFECTED (high)**: `protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur` — its `références` pin D613-6 to the now-superseded version LEGIARTI000046714699/2022-12-10. Text identical, so values unchanged (vente 243,6 €/an vs text 243,54; BIC 420 vs 419,76; BNC 0).
- **UNAFFECTED (high)**: all indépendant rules linked to D131-6-1, D621-2, D632-1, D633-3, D613-5, L131-6, L136-3, and the L613-7-linked rules (`dirigeant . exonérations . ACRE`, `… revenu abattu`), `dirigeant . auto-entrepreneur . DROM` (medium).

## 3. Proposal (`work/proposals/T1a/modele-social/règles`, diff in `work/proposals/T1a/CHANGES.diff`)

Traceability-only, **no numeric change** (none is supported by available text):
- `dirigeant/auto-entrepreneur/auto-entrepreneur.publicodes`: `cotisations` gets a `note` + `références` to D613-4 LEGIARTI000049623867 and to Décret n°2024-484; each taux rule (service BIC, service BNC, vente, CIPAV . taux) gets a `note` quoting its table line and listing the announced versions as *not transposed*, plus a `références` entry. `cotisations CIPAV . taux: 21.2%` became a mapping with `valeur: 21.2%`.
- `protection-sociale.publicodes`: `revenu cotisé auto-entrepreneur` références re-pinned to D613-6 LEGIARTI000049623885/2024-06-01 (+ decree), `note` on the announced versions.
- Native `build`: OK, 639 raw / 1172 parsed rules (same as G0). Registered in the store as rules snapshot `P_T1a`; `revalidate S1 x P_T1a`: all T1a checks RULE_CHANGED_CHECK_STILL_PASSES or STILL_VERIFIED; the two BROKEN are the pre-existing failures below.

## 4. Evaluations and abstentions

44 evaluation records in `answer.json` (rules x {prompt BNC, BIC service, vente, CIPAV created 2019/2021, BNC rich} x four dates). Before = after everywhere. `expected_from_text` is given only for 01/06/2024 (version LEGIARTI000049623867 / LEGIARTI000049623885 quotes). **18 abstentions**: for 01/07/2024, 01/01/2025 and 01/01/2026 the versions in force are announced by id and date only; the engine's unchanged value is reported but not asserted to be right.

## 5. Pre-existing defects, unrelated to S1 (carried from T0)

- CIPAV AE created on/after 01/04/2020 is charged 12,1 % (1 452 €/an) instead of 21,2 % (2 544) even with Acre = non (T1a-09 FAILED, T0 L0006).
- D632-1 2024 floor: library 450 h SMIC (5 243) vs 11,5 % PSS (5 332) (L0048 BROKEN).
- Not implemented: D613-4 c) meublés de tourisme 6 %; D613-6 split (only the RCI share is derived; its third term multiplies `service BIC` by 0 % where `service BNC` is meant, no numeric effect); L613-7 minimum-contribution option; D756-5 II CA cap.

## 6. Sophon store

Snapshots: law S0, S1; rules G0, P_T1a. Links added this task: T1a-01..19 = L0056..L0074 (11 VERIFIED, 1 FAILED on purpose = the CIPAV bug, 7 UNKNOWN of which 5 are explicit abstention records). Reports: `work/sophon/reports/T1a_revalidate_S1_G0.{json,md}`, `T1a_revalidate_S1_PT1a.{json,md}`, `T1a_evidence.{json,md}`, `T1a_verify-store.json` (ok, 0 problems, 74 links), `T1a_asof_D613-4_2024-07-01.json`.

Approval: **none recorded** (no sign-off, ratification or approval record exists in the corpus; merges/commits/tests are not approvals).
