# T1a — forward transposition after décret n°2024-484 (decision date 2024-06-01)

Law: S1 (legi-data 2.361.0, published 2024-06-01). Rules: G0 d9242882f96b (2024-05-15). Previous snapshot S0
(legi-data 2.360.0, 2024-05-25) was not re-supplied; the comparison uses the index and full texts I kept in
`work/law/S0_index.json` / `work/law/S0_texts.md` (script: `work/law/compare_snapshots.mjs`).

## 1. What changed in the law (S0 -> S1)

| article | S0 version | S1 version | in force | modifying text | text |
|---|---|---|---|---|---|
| D613-4 | LEGIARTI000046714712 (2022-12-10) | LEGIARTI000049623867, etat ABROGE_DIFF, 2024-06-01 -> 2024-07-01 | 2024-06-01 | Décret n°2024-484 du 30 mai 2024 - art. 1 (JORF 2024-05-31) | supplied; rate table identical (a 12,3 / b 21,2 / c 6 / d 21,2 / e 21,1 %), only spacing differs |
| D613-6 | LEGIARTI000046714699 (2022-12-10) | LEGIARTI000049623885, etat ABROGE_DIFF, 2024-06-01 -> 2024-07-01 | 2024-06-01 | Décret n°2024-484 du 30 mai 2024 - art. 2 (JORF 2024-05-31) | supplied; identical to previous text |

Announced future versions (ids and dates only, **no text in S1**):
- D613-4: LEGIARTI000049624068 (2024-07-01; recorded end 2025-05-01, overlapping the next one), LEGIARTI000049624097 (2025-01-01), LEGIARTI000049624125 (2026-01-01).
- D613-6: LEGIARTI000049625264 (2024-07-01), LEGIARTI000049625405 (2025-01-01), LEGIARTI000049625445 (2026-01-01).

Nota on both new versions: « Conformément au 1° de l'article 1 [resp. 2] du décret n° 2024-484 du 30 mai 2024, ces
dispositions entrent en vigueur à compter du 1er juin 2024. » The 2022 decree link and the Conseil d'État annulment
link (décision n°471203, 2024-02-21) present in S0 no longer appear in `lienModifications`.

Unchanged (same id, same text): L131-6, L136-3, L613-7, D131-6-1, D613-5, D621-2, D632-1, D633-3, D756-5. D136-5 still missing.

## 2. Rule classification (details and quotes in answer.json)

- **AFFECTED (medium)** — the four D613-4 rate rules under `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations`:
  `taux service BNC` (row e, 21,1 %), `cotisations CIPAV . taux` (row b, 21,2 %), `taux service BIC` (row d, 21,2 %),
  `taux vente restauration hébergement` (row a, 12,3 %). The governing version changed on 2024-06-01 and three more
  versions are scheduled inside the rules' date range. The text does not say which rows change later, so the four are
  treated symmetrically. Values in force on 2024-06-01 are exactly what G0 computes.
- **NEEDS_REVIEW (medium)** — rules whose hard-coded constants are derived from D613-4/D613-6 rates:
  `… cotisations . taux ACRE` (50 % x rate; 12,10 % CIPAV constant), `dirigeant . auto-entrepreneur . DROM . {service BIC, taux service BNC, taux vente restauration hébergement, taux CIPAV}` (D756-5 fractions, ceil 0,1),
  `protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur` (16,50 % x rate = 2,03 % / 3,50 %).
- **UNAFFECTED (high)** — everything else in the bounded set (structure rules `cotisations`, `cotisations CIPAV`, `cotisations et contributions`, `affiliation CIPAV`, `DROM`; classic ACRE rules and `PSS proratisé` (D131-6-1); `maladie . taux progressif` (D621-2); `invalidité et décès . assiette` (D632-1 — T0 mismatch still open, unrelated); `retraite de base` (D633-3); `assiette des cotisations` (L131-6); `CSG-CRDS . assiette` (L136-3); `micro-entreprise . revenu abattu` and `retraite . base . cotisée . revenu auto-entrepreneur` (L613-7 II, abatements unchanged)).

## 3. Proposal (work/proposals/T1a/modele-social/règles — disposable copy, diff in work/proposals/T1a/T1a.diff)

One file: `dirigeant/auto-entrepreneur/auto-entrepreneur.publicodes`.
- The four rate rules get a `note` citing D613-4 LEGIARTI000049623867 / décret 2024-484 and an explicit `date >= 06/2024`
  branch carrying the **same** value the text states. No number changes.
- New rule `… cotisations . taux à confirmer` (type: notification, sévérité: avertissement, `valeur: date >= 07/2024`)
  flags every date governed by an announced version whose text is unavailable.
- Native build OK: 639 raw / 1173 parsed rules (G0: 1172). All regression-like checks identical to G0.

## 4. Engine results (src/publicodes_eval.mjs; 1000 €/mois CA; full situations in answer.json)

| situation | rule | 01/06/2024 | 01/07/2024 | 01/01/2025 | 01/01/2026 |
|---|---|---|---|---|---|
| BNC libérale | taux service BNC | 21,1 % (text: « … 6 600 euros 21,1 % ») | 21,1 % — ABSTAIN | 21,1 % — ABSTAIN | 21,1 % — ABSTAIN |
| CIPAV (libérale réglementée) | cotisations CIPAV . taux | 21,2 % (« … 23 150 euros 21,2 % », row b) | ABSTAIN | ABSTAIN | ABSTAIN |
| BIC service (artisanale + service ou vente = 'service') | taux service BIC | 21,2 % (row d) | ABSTAIN | ABSTAIN | ABSTAIN |
| vente (commerciale) | taux vente restauration hébergement | 12,3 % (row a) | ABSTAIN | ABSTAIN | ABSTAIN |
| totals `cotisations` | BNC 2532 / CIPAV 2544 / BIC 2544 / vente 1476 €/an | same before/after | follow the rates | | |
| notification `taux à confirmer` (proposal only) | | false | true | true | true |

Before = G0, after = proposal: identical for every numeric rule on every date (the text in force on 2024-06-01 does not
change any value; the later versions have no text). "ABSTAIN" = the engine still prints 21,1 % etc., but no
`expected_from_text` is asserted because the version governing that date (ids above) is not available.

## 5. Approval
None recorded. Nothing in the corpus is a sign-off, ratification or approval; a merge, commit, package or test is not one.

## 6. Pitfalls met
- `taux ACRE . *` and `DROM . première/seconde période` are private publicodes rules: not listed, not evaluable directly; observe them through the public rate rules (`remplace`).
- A BIC-service micro needs `entreprise . activités . service ou vente: 'service'`; nature 'artisanale' alone is billed at the vente rate.
- Tool calls used: 22 (including the final hand-back).
