# E2 — results

Freeze commit `6f736d77` (FREEZE_MANIFEST.txt in `b295857`, pushed 2026-10-12T08:05:41Z). Scored solver run
started 08:05:47Z. Labels: **OBSERVED**, **INFERRED**, **ASSUMED**. Cases and reference are LAB-authored; data
synthetic.

## 1. The scored run (OBSERVED, `evidence/solver/run_meta.json`)

| Item | Value |
|---|---|
| Invocations | 1 scored (plus 2 non-scored one-word diagnostics before the freeze, `evidence/isolation_diagnostic/`, and one during the pre-freeze isolation check) |
| Process | fresh `claude -p`, Claude Code CLI 2.1.296, model `claude-opus-5-5` (envelope `modelUsage` confirms), 1 turn |
| Tools | none (`--tools ""`), `--safe-mode`, `--strict-mcp-config`, `--no-session-persistence`; 0 permission denials |
| Environment | `env -i` with PATH, HOME, proxy/CA variables, ANTHROPIC_BASE_URL only; HOME = new empty dir with only the login credential; cwd = new empty dir outside any repository |
| Input | stdin = `packet/solver_input.txt`, 82 958 bytes, sha256 `77e181e6…` (equal to the frozen packet) |
| Output | 25 380 bytes, unedited in `evidence/solver/raw_output.json` (sha256 `a3d5fabe…`); JSON inside one markdown code fence (accepted by the frozen parsing rule) |
| Cost | wall 82.0 s, API 80.5 s; 33 659 cache-creation input tokens, 10 384 output tokens (2 512 thinking); USD 0.477 as reported by the CLI |

## 2. Per-case outcome (OBSERVED, `evidence/score/score_report.json`)

| Id | Stratum | Expected verdict | Solver verdict | Correct (frozen) | Notes |
|---|---|---|---|---|---|
| H1 | missing fact, tempting proxy | NOT_VERIFIABLE / PARTIAL | NOT_VERIFIABLE | **yes** | payment predicate NOT_FOUND, no field bound; solver explicitly refused `status = 'completed'` as payment evidence |
| H2 | representable positive | VERIFIED | VERIFIED | **yes** | `gross_profit`, status completed, `product__category = 'Electronics'`; its native query reproduced the reference exactly (189 330.77 / 164 032.78 / 94 006.03) |
| H3 | ambiguity | REQUIRES_AUTHORIZED_INTERPRETATION | REQUIRES_AUTHORIZED_INTERPRETATION | **no** | ambiguity identified correctly (store country vs customer country, plus a channel-dependent third reading); **missed_predicate: completed**, because the solver merged "revenue from completed orders" into one predicate bound to `completed_revenue` and the frozen matcher assigns one solver predicate to one reference predicate |
| H4 | near-match, representable | VERIFIED | VERIFIED | **yes** | chose `quantity_sold` (not `orders`/`revenue`), `store__store_country` (not customer), `!= 'cancelled'` (not `= 'completed'`); native result reproduced exactly (1 218 / 1 192 / 534) |
| H5 | present in source, not exposed | PARTIAL / NOT_VERIFIABLE | PARTIAL_OR_UNKNOWN | **yes** | e-mail predicate PRESENT_IN_SOURCE_NOT_EXPOSED with the gold/silver/bronze `email` columns; noted custom SQL would be needed |
| H6 | representable positive | VERIFIED | PARTIAL_OR_UNKNOWN | **no** | correct native query proposed (`orders`, online, `customer__country = 'France'`); classified "country of residence is France" as NOT_ESTABLISHED_AUTHORITY because nothing in the packet says `customers.country` is the country of residence → over_abstention |

**4 of 6 correct.** Severe errors: **0** (no false VERIFIED, no proxy bound, no invented evidence). Errors:
missed_predicate 1, wrong_exposure_classification 1, over_abstention 1. Corrections a reviewer would need: 3.
Evidence validity: every physical field cited in all six cases exists in the estate. Every VERIFIED claim (H2,
H4) was reproduced by native MetricFlow execution of the solver's own query.

## 3. Gate criteria (frozen, PROTOCOL.md §7)

| # | Criterion | Result |
|---|---|---|
| 1 | Fresh, isolated, no measured leakage | **met**: packet audit ok; fresh tool-less process; no repo, history or transcripts reachable (HOME contained only the credential before the run; afterwards only CLI bookkeeping files) |
| 2 | ≥ 5 of 6 correct | **not met** (4) |
| 3 | Both representable positives correct | **not met** (H2 yes, H6 no) |
| 4 | H1, H5, H3 not claimed VERIFIED | **met** |
| 5 | Zero false VERIFIED | **met** |
| 6 | Scorer controls reject wrong proposals; replay identical | **met**: 9/9 controls passed before the freeze; fresh-process re-score byte-identical (`score_report_replay.json`, sha256 `eeb9309d…` both) |

Mechanical gate: **PARTIAL_DISCOVERY_SIGNAL**.

## 4. Native checks used by scoring (OBSERVED)

Positive bindings accepted natively (H2, H4 and the H6 query, all reproducing the reference). Rejections shown
natively: `Dimension('customer__email')` (reference build and control `mut_false_verified_H5`); wrong metric and
wrong dimension controls produce mismatching native numbers. Native execution of solver queries ran on a
disposable warehouse copy.

## 5. Deviations and non-scored analysis (after seeing the output; primary score unchanged)

1. **H3 is a scoring-granularity miss, not a reasoning miss** (INFERRED from the solver's text). The task asked
   for atomic predicates; the solver bound "revenue from completed orders" jointly to `completed_revenue` (whose
   filter is `sales__status = 'completed'`) and listed `fact_sales.status`. A NON-SCORED relaxation that lets
   one merged predicate serve several reference predicates (`src/sensitivity_nonscored.py`,
   `evidence/score/sensitivity_nonscored.json`) makes H3 correct: **5 of 6, gate still PARTIAL** (criterion 3,
   H6).
2. **H6 exposes a defect in my clause, not only in the solver** (INFERRED). I wrote "country of residence"; the
   upstream column is just `country` (`customers.csv`, `stg_customers.sql`: "standardize … country spellings"),
   with no documentation of what country it is. The solver produced the exact native query and flagged that the
   packet does not establish the field's meaning. That is the charter's "do not infer authority" behaviour. The
   frozen reference assumed the equivalence. I do not re-score it. The honest reading: E2 shows no case where the
   solver failed to find a representable binding; it shows one case where it declined to accept an
   undocumented semantic equivalence that the reference author accepted.
3. Parsing tolerance used: the output was inside one markdown code fence, which the frozen rule accepts.
4. The E1 finding (PRIOR.md): E1's B1 is natively expressible through metric filters at line grain. Not an E2
   result; recorded for the owner.

## 6. Limitations

- Six LAB-authored cases on one small synthetic stack, written by the orchestrator, who also wrote E0/E1 and
  the reference; no accuracy or reliability estimate is possible.
- One sample from one model (`claude-opus-5-5`, same family as the orchestrator); no variance measured.
- Isolation is strong for context (no tools, fresh HOME, no repo, no history) but cannot remove pretraining
  exposure to the public upstream project.
- One-shot packet: the solver could not query data, run `mf`, or ask questions; this is bounded read-only
  discovery, not interactive enterprise retrieval.
- Scoring of the H3 reason uses a frozen keyword rule ("customer" and "store"); the solver's text was also read
  by the orchestrator and agrees.
- No Windows execution; PowerShell commands in README.md are UNTESTED.
- No CI exists in the repository; PRs #4, #5 and this one have no checks.
