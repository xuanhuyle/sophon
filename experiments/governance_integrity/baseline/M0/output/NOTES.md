# M0 — change maintenance notes (decision date 2025-10-01, law S6 → S7, rules G3 d6c374271727)

## 1. What changed in the law (S6 legi-data 2.464.0, 2025-09-01 → S7 legi-data 2.469.0, 2025-10-01)

Method: `work/law/compare_snapshots.mjs` (id / etat / dates / versions / liens / text / nota per article) plus a JSON deep-compare
of all 12 records (`work/law/M0_S6_S7_record_diff.json`). Result:

| article | S7 current version | record S6 = S7 ? | what moved |
|---|---|---|---|
| D613-4 | LEGIARTI000049624097, ABROGE_DIFF, 2025-01-01 → 2026-01-01 | no (articleVersions only) | future version LEGIARTI000049624125 (2026-01-01) : VIGUEUR_DIFF → **MODIFIE_MORT_NE**, dateFin 2025-09-10 ; **new** LEGIARTI000052218738, VIGUEUR_DIFF, 2026-01-01 → 2999-01-01 |
| D613-6 | LEGIARTI000049625405, ABROGE_DIFF, 2025-01-01 → 2026-01-01 | no (articleVersions only) | future version LEGIARTI000049625445 (2026-01-01) : VIGUEUR_DIFF → **MODIFIE_MORT_NE**, dateFin 2025-09-10 ; **new** LEGIARTI000052218747, VIGUEUR_DIFF, 2026-01-01 → 2999-01-01 |
| D633-3 | LEGIARTI000049904636, VIGUEUR, 2024-07-07 → | no (order only) | two articleVersions entries swapped (LEGIARTI000041967101 / LEGIARTI000031799496), same ids, etats, dates — non-substantive |
| the 9 others | — | **yes, byte-identical** | — |

For D613-4 and D613-6 the current text, text_sha256, nota and `lienModifications` are identical in S6 and S7. The only recorded
modifying text is still "Décret n°2024-484 du 30 mai 2024" (art. 1, 3° / art. 2, 3°). **No text and no decree link exist for the
new 2026 versions** — they are known by id and dates only.

Text in force on 2025-10-01 (D613-4 LEGIARTI000049624097): a) 12,3 % · b) 23,2 % · c) 6 % · d) 21,2 % · e) 24,6 %.
D613-6 LEGIARTI000049625405 shares: a/d 8,90 / 3,10 / 41,80 / 16,50 / 29,70 ; b 9,30 + 0,90 / 1,40 / 23,45 + 5,35 / 25,60 / 34,00 ;
c 4,90 / 3,50 / 48,30 / 15,10 / 28,20 ; e 3,40 / 3,50 / 47,60 / 13,00 / 32,50.

**Conclusion on relevance:** nothing in force changed. The change is a replacement of the announced 2026-01-01 versions by other
announced versions without text. No numeric edit is justified; the 2026 values that G3 already hard-codes are now unsupported by any
text in the corpus (the version they could have rested on is mort-né) → flagged, abstained.

## 2. Rule classification (details and quotes in `output/answer.json`)

Engine runs: 28 checks (+ 12 direct DROM checks, `checks_M0_drom.json`) (`work/engine/checks_M0_ae.json`, 4 categories × plain / ACRE / DROM × 01/10/2025 and 01/01/2026) + 8 ACRE
checks (`checks_M0_acre.json`), on G3 and on the proposal. Results in `work/engine/results_M0_{G3,proposal}_{ae,acre}.jsonl`,
tables via `node work/engine/table_M0.mjs <jsonl>`.

- **NEEDS_REVIEW (medium)** — rules whose value from 2026-01-01 is governed by the text-less versions:
  `… cotisations . service BNC . taux` (24,6 % at 01/10/2025 = row e ✓ ; **26,1 % at 01/01/2026 unsupported**), `… service BNC Cipav . taux`
  (23,2 % ✓ row b; carried into 2026), `… service BIC . taux` (21,2 % ✓ row d), `… vente restauration hébergement . taux` (12,3 % ✓ row a);
  the 20 `… <catégorie> . répartition . * . taux de répartition` rules (2025 values = D613-6 rows ✓ ; BNC 2026 branches 3 / 3,25 / 44,85 /
  17,7 / 31,20 % unsupported); `protection sociale . retraite . complémentaire . RCI . revenu cotisé auto-entrepreneur` (383,76 €/an at
  2025 = 12 000 × 24,6 % × 13 % ✓ ; 554,364 €/an at 2026 unsupported); `DROM . taux service BNC / taux CIPAV / taux service BIC / taux vente`
  (2025: ceil10 of 1/6, 1/2, 2/3 × rate ✓ for BNC, BIC, vente; **Cipav 7,1/10,6/14,2 ≠ 7,8/11,6/15,5 — pre-existing since 07/2024**, fraction
  depends on L611-1 outside the set); `Acre . taux service BNC / taux CIPAV / taux service BIC / taux vente` (50 % × rate; Cipav constant
  13,90 % has no source in the set; 2026 BNC 13,05 % rests on the unverified 26,1 %).
- **UNAFFECTED (high), re-evaluated**: `… cotisations` and `dirigeant . auto-entrepreneur . cotisations et contributions` (L613-7 I
  identical; structure only), `protection sociale . retraite . base . cotisée . revenu auto-entrepreneur` (L613-7 II: 7 920 / 6 000 /
  3 480 €/an = 12 000 × (1 − 34/50/71 %)), `dirigeant . exonérations . ACRE`, `Acre . taux Acre` (D131-6-1 identical).
- **UNAFFECTED (high), NOT re-evaluated** (`not_reassessed_rules`): the `dirigeant . indépendant …` rules bound to L131-6, L136-3,
  D621-2, D632-1, D633-3, D131-6-1 (`assiette des cotisations`, `CSG-CRDS . assiette`, `maladie`, `retraite de base`, `invalidité et
  décès`, `assiette minimale . invalidité et décès`, `exonérations . ACRE`). Evidence: their articles' records are byte-identical in S6
  and S7 (same id, text_sha256, versions, liens, nota) and the changed articles govern only the L613-7 micro-social regime, which these
  rules do not implement. D613-5 and D136-5: no bound rule at G3.

## 3. Proposal (`work/proposals/M0/modele-social/règles`, diff `work/proposals/M0/M0.diff`, re-apply with `apply_M0.mjs`)

Documentation-only, one file (`dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes`):
1. `cotisations` → `références` to L613-7 LEGIARTI000048683570, D613-4 LEGIARTI000049624097, D613-6 LEGIARTI000049625405.
2. New rule `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux 2026 à confirmer` — `type: notification`,
   `sévérité: avertissement`, `valeur: date >= 01/2026`, description = the S7 version situation (ids, états, dates) and which rule values
   are unconfirmed. Engine: unknown rule on G3; **false at 01/10/2025, true at 01/01/2026** on the proposal.
3. `note:` on the four rate rules (row, version, in-force dates; 2026 branch not supported by any text).
4. Stale citation `Article D613-6 … LEGIARTI000043656780` (2021 version) → `LEGIARTI000049625405`.

Build: G3 722 raw / 1427 parsed; proposal 722 / 1428 (the notification). Evaluations: 428 + 104 + 60 cells byte-identical G3 vs proposal
(`compare_results.mjs`). **Numeric values deliberately unchanged** — abstention on 2026.

## 4. Abstentions
- All D613-4 rates and D613-6 shares for dates ≥ 2026-01-01 (LEGIARTI000052218738 / LEGIARTI000052218747: id + dates only).
- Identity of the decree behind those versions (no lien in S7; dateFin 2025-09-10 of the mort-né versions is the only hint).
- Meaning of MODIFIE_MORT_NE beyond the recorded label; D756-5 fraction for Cipav (L611-1 outside the set).

## 5. Approval
None recorded — the corpus contains no sign-off, ratification or approval of any kind (commits, package versions and tests are not approvals).

## 6. For the next change
Persistent records updated: `work/README.md`, `work/notes/M0_findings.md`, `work/law/S6_*`, `work/law/S7_*`, `work/law/M0_S6_S7_record_diff.json`,
`work/engine/checks_M0_*.json`, `results_M0_*`, `table_M0.mjs`, `make_answer_M0.mjs`, `work/proposals/M0/`. First thing next time:
`node work/law/compare_snapshots.mjs <new articles.json> work/law/S7_index.json work/law/S7_texts.md S8` and look for the text of
LEGIARTI000052218738 / LEGIARTI000052218747; then compare the G3 (or newer pin) 2026 branches against it.
