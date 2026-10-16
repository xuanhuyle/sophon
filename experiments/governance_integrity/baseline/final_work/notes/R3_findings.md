# R3 findings (decision date 2024-10-19, law S5 legi-data 2.385.0 = S4 = S3 on all 12 articles, rules G2 3a4091ae1caf = parent of the reviewed commit)

## Event
Commit 9bb43d710094 "fix: correction des taux auto-entrepreneur DROM" (Alice Dahan, authored 2024-10-03, committed 2024-10-11). Re-indents the four DROM
replacement rules out of the body of the private rule `DROM . seconde période` (6 spaces) into `DROM`'s `avec:` (4 spaces); renames `service BIC` -> `taux service BIC`;
removes a duplicate misspelt `references:` key. Verdict MISMATCH (high): fix restores the D756-5 reductions, but BNC/CIPAV constants (3.6/10.6/14.1, 7.1/10.6/14.2)
are derived from 21.1/21.2 %, not from D613-4 v5 (23.1/23.2 % since 2024-07-01) -> expected 3.9/11.6/15.4 and 7.8/11.6/15.5. Full write-up: output/NOTES.md of R3
(copy of the reasoning is in make_answer_R3.mjs). Approval: none recorded.

## Engine facts learned
- publicodes 1.10.4 parseRule (dist/index.js l.1985-1987) keeps only `mecanismKeys` keys; unknown keys in a rule body are DROPPED SILENTLY (no build error).
  A mis-indented nested rule therefore disappears without trace: check `list` counts after any re-indentation commit (G2 1258 parsed vs 1262 after).
- `entreprise . durée d'activité . trimestres civils / années civiles` (mécanisme `durée`, `depuis: date de création`) count up to the REAL CLOCK, not the situation
  `date`: création 01/01/2024 at date 01/10/2024 gave 12 trimestres / 3 années (today 2026). Always set them explicitly in situations (4/1, 12/3, 24/6 used here).
- BNC situation needs `entreprise . activité . nature . libérale . réglementée: non`, otherwise `cotisations CIPAV . taux` is null/missing.
- G2 base rates at 01/10/2024: BNC 23.1, CIPAV 23.2, SBIC 21.2, vente 12.3 %; at 01/01/2025 BNC 24.6, 01/01/2026 26.1 % (G2 already encodes the text-less D613-4 v6/v7).
- Results files contain no tree path: `cmp` of jsonl = semantic equality. compare_results.mjs prints per-cell differences.

## Origin of the regression (for the record)
G1 (2024-07-16, 4-space file): rules were siblings of `seconde période`, DROM_Q8_BNC@01-06-2024 = 3.6 % (results_R2_after_T1a_rates.jsonl). Between G1 and G2,
HISTORY.txt has 05334b12 "refactor(auto-entrepreneur): Corrige l'indentation des règles AE" (2024-09-02); history_bounded_rules.patch l.396-462 shows the hunk that
nested `service BIC:` under `seconde période:`. Published library charged DROM AE the métropole rates from ~2024-09-02 to 2024-10-11; the G2 snapshot fixture
(DROM 3: `service BNC . taux: 23`) had recorded it.

## Law side — still open after R3 (expect rules-side fixes)
- DROM BNC/CIPAV constants (this task). Expected from D756-5 x D613-4 v5: BNC 3.9/11.6/15.4 (7.7 in period a if L611-1 puts PLNR in the 1/3 group), CIPAV 7.8/11.6/15.5.
  From 2025-01-01 D613-4 v6 LEGIARTI000049624097 has no text -> abstain (G2 base rule gives 24.6 %: if that were the text, DROM BNC would be 4.1/12.3/16.4).
- D756-5 cites L. 133-6-8 and D. 131-6-1 (old numbering); renumbering instruments, L756-5, L751-1, L611-1 outside the set.
- Carried over: reform 01/2025 (T1b proposal), D632-1 floor (T0-P1), `taux ACRE . service BIC` not halved (R2 note), D613-6 shares.

## Files
checks_R3_drom.json (20 checks x 15 rules), results_R3_{before,after}_{drom + 6 existing specs}.jsonl, log_R3_*.txt, list_R3_{before,after}.json,
compare_results.mjs (<before.jsonl> <after.jsonl> [all]), make_answer_R3.mjs [tool_calls]. proposals/R3 = G2 + patch (after-tree), not a proposal.
