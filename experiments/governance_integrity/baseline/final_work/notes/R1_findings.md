# R1 findings (decision date 2024-07-17, law S3 legi-data 2.381.0 = same as T1b, rules G1 2a0e452617fc = the reviewed commit)

## Event
Commit 2a0e452617fc "fix: met à jour les liens morts" (Fixes #2165; authored 2024-06-26, committed 2024-07-16). Rule tree: ONE line, `références:` URL of
`établissement . taux ATMP` (entreprise/établissement.publicodes l.61, net-entreprises -> ameli). 4 site/ UI files also changed (not supplied). Law S3 unchanged.
Verdict HARMLESS_REFACTOR (high). Approval: none recorded.

## Method that worked (reuse for the next reverse check)
1. `cp -r` G1 tree to work/proposals/<task>/modele-social/règles, reverse-apply diff.patch with sed, `diff -r` to prove the single difference.
2. `build` + `list` on both -> compare counts and name list (`work/engine/list_R1_*.json`).
3. Run the existing specs on both trees in parallel (4 background chains, ~1 min): `bash work/engine/run_checks.sh <tree> work/engine/checks_<spec>.json <out.jsonl>`;
   `cmp` the jsonl files (they contain no tree path, so byte-identical == no semantic change). 69 checks: R1_atmp(4) T1a_rates(24) T0_ae3(16) T1b_trader(7) T0_ti(18).
4. `work/engine/make_answer_R1.mjs`: answer generator; engine values from result files, quotes verified by `must()`; window helper `win()` for short exact quotes.
5. Bounded-article keyword scan (one node one-liner; articles.json = {snapshot, legi_data_version, published, articles:{num:[rec]}, articles_missing_in_snapshot}).

## Engine facts learned (salarié / AT-MP side, G1)
- Minimal salarié situation: `{"date":"01/07/2024","salarié . contrat . salaire brut":"3000 €/mois"}` (no `salarié: oui` needed).
- `établissement . taux ATMP` = question, défaut `taux collectif` (défaut `salarié . cotisations . ATMP . taux moyen` = 2.23 % in 2024), plancher `salarié . cotisations . ATMP . taux minimum` = 0.46 %
  (0.1 % entered -> 0.46 %). ATMP cotisation 3000 €/mois: 66.9 €/mois (2.23 %), 45 (1.5 %), 90 (3 % collectif), 13.8 (floor). employeur total 1074.68 €/mois at default.
- `références`, `description`, `question`, `note` are metadata: changing them leaves parsed_rule_count (1220) and every evaluation unchanged.

## Law side (S3, unchanged since T1b) — still open, expect a rules-side fix soon
- D613-4 LEGIARTI000049624068 (2024-07-01): b) 23,2 %, e) 23,1 % vs G1 21,2 / 21,1 % (BNC@01-07-2024, CIPAV@01-07-2024 in results_R1_G1_T1a_rates.jsonl). ACRE/DROM/RCI constants to re-derive (T1a to-do).
- D613-6 LEGIARTI000049625264 (2024-07-01) shares; D136-5 / D621-2 / D633-3 reform from periods 2025-01-01 (T1b proposal); D632-1 floor (T0-P1); D613-4 c), D613-5, D756-5 II.
- compare_snapshots.mjs v2 now stores/compares `nota` (S3_texts.md regenerated with NOTA lines). Run it first on any new snapshot.
