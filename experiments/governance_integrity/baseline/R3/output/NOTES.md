# R3 — reverse check of commit 9bb43d710094 "fix: correction des taux auto-entrepreneur DROM" (decision date 2024-10-19)

**Verdict: MISMATCH (confidence high). Approval: none recorded.**

## What the commit changes (inputs/diffs/R3_9bb43d710094)
- `dirigeant/auto-entrepreneur/exonérations.publicodes`: the four replacement rules `service BIC` (renamed `taux service BIC`), `taux service BNC`,
  `taux vente restauration hébergement`, `taux CIPAV` move from 6-space indentation — i.e. keys inside the body of the private rule
  `dirigeant . auto-entrepreneur . DROM . seconde période` — to 4-space indentation, i.e. children of `dirigeant . auto-entrepreneur . DROM` under its `avec:`.
  The rate constants are untouched (3.60/10.60/14.20, 3.60/10.60/14.10, 2.10/6.20/8.20, 7.10/10.60/14.20 %). A misspelt duplicate key `references:` is removed
  (the PDF link now sits under `références:`); a leading blank line is removed.
- `dirigeant/dirigeant.publicodes`: blank lines only.
- `site/test/regressions/__snapshots__/auto-entrepreneur.test.ts.snap` (116 lines, per stat.txt): not supplied.
- Before-tree = G2 3a4091ae1caf exactly: git blob sha1 of both files = the patch's a-side (f760e73cc, 741068f66). After-tree = G2 + `patch -p1` in
  `work/proposals/R3/modele-social/règles` (blobs = b-side 3d217c4d4, a20c444d8; `diff -rq` shows only these two files).

## Why it is semantic, not a refactor
publicodes 1.10.4 `parseRule` keeps only the keys listed in `mecanismKeys` (`src/node_modules/publicodes/dist/index.js` l.1985-1987); any other key in a rule
body is silently dropped. So at G2 the four DROM rate rules did not exist:
- `build`: 636 raw / **1258** parsed (G2) → 636 / **1262** (after). `list`: the only new names are the four `dirigeant . auto-entrepreneur . DROM . taux …` rules.
- Engine (work/engine/checks_R3_drom.json, results_R3_before_drom.jsonl vs results_R3_after_drom.jsonl; situation = auto-entrepreneur EI, CA 1000 €/mois,
  `établissement . commune . département . outre-mer: oui`, `dirigeant . exonérations . ACRE: non`, periods set with `entreprise . durée d'activité . trimestres civils` /
  `années civiles` = 4/1, 12/3, 24/6; date 01/10/2024):

| rule (`… cotisations . X . taux`) | P1 before → after | P2 before → after | P3 before → after |
|---|---|---|---|
| service BNC (libérale non réglementée) | 23.1 → 3.6 % | 23.1 → 10.6 % | 23.1 → 14.1 % |
| cotisations CIPAV (libérale réglementée) | 23.2 → 7.1 % | 23.2 → 10.6 % | 23.2 → 14.2 % |
| service BIC (artisanale, service) | 21.2 → 3.6 % | 21.2 → 10.6 % | 21.2 → 14.2 % |
| vente restauration hébergement (commerciale, vente) | 12.3 → 2.1 % | 12.3 → 6.2 % | 12.3 → 8.2 % |

  `… cotisations` for BNC: 231 → 36 / 106 / 141 €/mois; `revenu net` 9204 → 11544 / 10704 / 10284 €/an. Decision date 19/10/2024, BNC P1: 23.1 → 3.6 %, 231 → 36 €/mois.
  Métropole controls (`outre-mer: non`) identical before/after (23.1 / 23.2 / 21.2 / 12.3 %).
- The 79 existing checks re-run on both trees: R1_atmp (4), T1b_trader (7), T0_ti (18) byte-identical; T1a_rates 27 cells, T0_ae3 30 cells, R2_acre 7 cells differ —
  every differing check is a DROM situation (DROM_Q8_BNC@…, AE_DROM_*). Nothing outside DROM moved.
- The maintainers' own fixture at G2 (existing_tests …/auto-entrepreneur.test.ts.snap, case "DROM 3" with `trimestres civils: 1`) records
  `… service BNC . taux: 23` and the same cotisations as the non-DROM case — the regression was captured in the snapshot.
- Origin: at G1 2a0e452617fc (2024-07-16, 4-space file) the four rules were siblings of `seconde période` and the G1-era results
  (work/engine/results_R2_after_T1a_rates.jsonl, DROM_Q8_BNC@01-06-2024) give 3.6 %. HISTORY.txt lists 05334b12 "refactor(auto-entrepreneur): Corrige
  l'indentation des règles AE" (2024-09-02) between the pins and history_bounded_rules.patch l.396-462 shows the hunk `-        seconde période:` /
  `-        service BIC:` → `+    seconde période:` / `+      service BIC:`. The DROM reductions were therefore absent from the published library for ~5 weeks.

## What the governing text requires (S5 = S4 = S3 on all 12 articles; compare_snapshots printed "same")
- **D756-5 LEGIARTI000034726710** (VIGUEUR since 2017-05-12, only version): « le taux mentionné au premier alinéa de l'article L. 133-6-8 correspond, après arrondi au
  dixième de pour cent supérieur, à une fraction des taux prévus par l'article D. 131-6-1 fixée à : a) 1/6 pour les travailleurs indépendants mentionnés au 2° de
  l'article L. 611-1 et 1/3 dans les autres cas, jusqu'à la fin du septième trimestre civil qui suit celui au cours duquel intervient la date d'effet de
  l'affiliation ; b) 1/2 pour la période qui court entre la fin de la période mentionnée au a et la fin de la troisième année civile d'activité ; c) 2/3 à compter de
  la quatrième année civile d'activité. »
- **D613-4 LEGIARTI000049624068** (VIGUEUR_DIFF 2024-07-01 → 2025-05-01; nota: « ces dispositions entrent en vigueur à compter du 1er juillet 2024 »):
  a) « 12,3 % », b) CIPAV « 23,2 % », d) « 21,2 % », e) « 23,1 % ».
- D756-5 cites the old numbering (L. 133-6-8 → L613-7 LEGIARTI000048683570 « un taux global fixé par décret pour chaque catégorie d'activité » ; D. 131-6-1, which in
  S5 — LEGIARTI000036475110 — is the ACRE article). Reading « taux prévus par l'article D. 131-6-1 » as the D613-4 rate table is the only way to apply D756-5;
  the renumbering instruments are outside the bounded set and are flagged as such.
- Expected DROM rates = ceil₀.₁(fraction × D613-4 v5 rate):

| category | in-force rate | a) 1/6 or 1/3 | b) 1/2 | c) 2/3 | rule (after) |
|---|---|---|---|---|---|
| vente (a) | 12.3 | 2.1 | 6.2 | 8.2 | 2.1 / 6.2 / 8.2 ✔ |
| service BIC (d) | 21.2 | 3.6 | 10.6 | 14.2 | 3.6 / 10.6 / 14.2 ✔ |
| BNC, PL non réglementée (e) | **23.1** | **3.9** (7.7 if 1/3) | **11.6** | **15.4** | 3.6 / 10.6 / 14.1 ✘ |
| CIPAV (b) | **23.2** | **7.8** | **11.6** | **15.5** | 7.1 / 10.6 / 14.2 ✘ |

- Consistency check (not a legal claim): all 12 rule constants equal the same derivation applied to the pre-2024-07-01 base rates the engine itself gives at
  01/06/2024 (21.1 % BNC, 21.2 % CIPAV, 21.2 % SBIC, 12.3 % vente) — the DROM constants were simply never re-derived after décret 2024-484.

## Classification
- Not HARMLESS_REFACTOR: four rules appear, DROM outputs change in every period and every category.
- Not LEGITIMATE_INDEPENDENT_CHANGE: the rule's own description defines the DROM rates as fractions of the « taux pleins de métropole »; the text does not leave 3.6 % open at a date where the base is 23.1 %.
- Not UNRESOLVED: periods b) and c) do not depend on the L611-1 category question, and D613-4 v5 text is in the snapshot.
- MISMATCH: after the change the library still computes, for DROM BNC and CIPAV auto-entrepreneurs at any date ≥ 2024-07-01, values the text in force does not
  support (3.6/10.6/14.1 and 7.1/10.6/14.2 % instead of 3.9/11.6/15.4 and 7.8/11.6/15.5 %). The change is nonetheless a real fix: before it, DROM
  auto-entrepreneurs were charged full métropole rates in all four categories.

## Outside the bounded set / abstentions
L. 756-5 and L. 751-1 (basis and territory), L. 611-1 2° (1/6 vs 1/3 — decides 3.9 vs 7.7 % for BNC period a), the renumbering of L. 133-6-8 / D. 131-6-1,
the Urssaf DROM guide cited by the rule. D613-4 LEGIARTI000049624097 (2025-01-01) and LEGIARTI000049624125 (2026-01-01): ids/dates only, no text → no expected
DROM values for 2025/2026 (the base rules already encode 24.6 / 26.1 % while the DROM constants stay flat at 3.6 %). Pre-07/2024 D613-4 texts: not in S5.

## Engine pitfalls recorded
`entreprise . durée d'activité . *` (mécanisme `durée`) counts up to the real clock, not the situation `date` — set trimestres civils / années civiles explicitly.
Unknown keys in a rule body are dropped silently (no build error). Floating artefacts such as 81.99999999999999 €/mois are arithmetic only.

Files: work/engine/checks_R3_drom.json, results_R3_{before,after}_{drom,R1_atmp,T1a_rates,T0_ae3,T1b_trader,T0_ti,R2_acre}.jsonl, log_R3_*.txt, list_R3_{before,after}.json,
compare_results.mjs, make_answer_R3.mjs (generator: quotes extracted from S5 by exact window, engine values from result files). work/proposals/R3 = after-tree (not a proposal).
