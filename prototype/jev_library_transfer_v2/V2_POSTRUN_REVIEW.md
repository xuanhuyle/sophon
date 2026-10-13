# Jev V2: post-run review of the owner's live run (addendum, written on the V3 branch)

**Scoped result: `NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE_ON_V2_PROXY`.** This is *not* a global Jev or Sophon no-go.

- The original [`V2_TRANSFER_RESULTS.md`](V2_TRANSFER_RESULTS.md) is preserved unchanged as historical readiness evidence (`READY_NOT_RUN` at `1151c0f`).
- The raw recordings stay local and git-ignored. Only the SHA receipt file `receipts_20261013T130630Z.json` is committed.
- No provider was called during this review. Replay and scoring are offline re-derivations from the stored raw outputs.

## 1. Screenshot vs verified raw evidence

| Item | Owner screenshot (provisional) | Verified from local raw files (2026-10-13, Claude Code) |
|---|---|---|
| Files | `live_V2_20261013T130630Z.json` etc. | All 5 files present. SHA-256 of each matches `receipts_20261013T130630Z.json` exactly (live `3465e248…`, replay `09d1d1bd…`, score `2c16140b…`, score.md `6ab8c11b…`, preflight `000fe2e7…`). |
| Frozen inputs | – | The recording's canonical-JSON digests match the committed B corpus, sealed checklist (`7fa0bd30…`), library v0/v1 and all 5 context sidecars. The V1 A-recording sha `a562ccf8…` matches. (Raw-byte file hashes differ only because the harness hashes canonical JSON.) |
| Calls | 30 logical, 30 attempts, 0 failed | `budget`: 30 logical / 30 HTTP attempts / 0 failed (cap 31 / 93). Planned = 9 Jev + 18 reviewer + 3 blind + 0 synthesis. |
| Provenance / models | 9 Jev + 21 Claude `claude-opus-5-5` | All 30 are `ACTUAL_PROVIDER`, all HTTP 200. Jev reported `jev-1.13.0` (requested `jev-latest`) ×9. Claude requested and reported `claude-opus-5-5` ×21, effort `medium`, all `stop_reason=end_turn`. 21 distinct Anthropic `msg_…` ids, 30 distinct raw responses (no duplicates). All 12 condition outputs passed field validation. |
| Window | – | Started 13:06:36Z, finished 13:18:18Z (2026-10-13). |
| Replay determinism | "REPLAY_OF_RECORDED_PROVIDER_OUTPUTS" | Re-running `--mode replay` then `--mode score` into the scratchpad reproduced **byte-identical** replay and score files (same SHA-256 as the receipts). |
| Scores | COLD 35, WARM_LIBRARY 34, WARM_RAW_A 36, BLIND 35 of 36 | Confirmed. Per packet: B1 9/9 for all arms. B2: COLD 12, WARM 11, RAW 13, BLIND 12 (of 13). B3 14/14 for all arms. |
| Decision | `HOLD_UNRESOLVED` ×12; rule fails | Confirmed. Rule checks: ≥2 additional facts ✗, ≥20 pp ✗ (−2.8 pp), zero new critical wrong transfers ✓, beats raw on ≥1 element ✗. Blind ≥ warm ✓. |
| Cost | "≈ $0.82" | **$0.82 was the preflight *estimate*.** Real usage: Claude 118,057 input + 85,595 output tokens. At the repo's assumed price table (`prototype.PRICES`: $4 / $20 per MTok, not an invoice) that is **≈ $2.18**, plus Jev ≈ $0.001. Output averaged ~4,076 tokens/call (thinking included) vs 1,246 assumed, so actual cost was ~2.7× the estimate. |

### Tokens and cost per condition (real `usage` metadata; USD at the repo's assumed prices)

| Condition | Calls | Claude in | Claude out | Jev in | ≈ USD |
|---|---|---|---|---|---|
| COLD_B | 9 | 28,584 | 24,236 | 5,662 | 0.60 |
| WARM_LIBRARY_B | 9 | 34,920 | 23,828 | 6,820 | 0.62 |
| WARM_RAW_A_B | 9 | 44,604 | 23,699 | 7,489 | 0.65 |
| BLIND_LLM_B | 3 | 9,949 | 13,832 | 0 | 0.32 |

The single-call blind arm cost about half of any pipeline arm and matched COLD (35/36).

## 2. Why WARM_LIBRARY_B lost on B2

Per element (Y = slot quote overlaps the anchor *and* uses an acceptable slot):

| Element | COLD | WARM_LIBRARY | WARM_RAW_A | BLIND |
|---|---|---|---|---|
| B2.E4: three distinct Financial Credit schedules | Y | n | Y | n |
| B2.E13: Customer means Partner/Reseller under resale | n | n | Y | Y |
| all other 11 B2 elements | Y | Y | Y | Y |

**Diagnosis: a reconciliation/scoring artifact compounded by template slot scope. It was not a Jev routing error and not an omission by the model.**

1. **The warm reviewers did surface both facts, but filed them under `omitted_conditions`, not `slots`.**
   - E4: the adversarial reviewer wrote: *"There are three distinct schedules keyed to storage class and location. The SLO thresholds and band values differ per schedule."* It quoted the E4 anchor verbatim.
   - E13: *"In resale arrangements, references to Customer are substituted with Partner or Reseller."* It quoted `all references to Customer in this SLA mean Partner or Reseller (as applicable)`.
   - `score_condition` credits only slot entries, so these became neither recovered elements nor (because they overlap an anchor) "unmatched challenges". They are invisible in the score.
2. **Template slot scope:**
   - Jev routed B2 to `TIERED_SERVICE_CREDIT_SCHEDULE` at p=0.96 with no order flags. Cold/raw routed it to `DEFINITION` at p=0.63/0.72. B2 *is* a tiered credit schedule, so the routing is defensible.
   - That template's slot set is calculation, condition, measurement_period, threshold, deadline, exception, source_reference. E4's acceptable slots are object, condition, remedy, normative_action, calculation; E13's are beneficiary, condition, exception, actor.
   - Under the TIERED template, the reviewers apparently treated "three schedules" and "reseller substitution" as gaps in the template rather than as slot facts.
   - COLD's E4 credit came from a backward-review `normative_action` slot whose *value* was only "defines 'Financial Credit' for the third tier". That is quote-anchored but semantically partial.
3. **Not raw-output normalization:** all 12 outputs passed validation with no field errors.
4. **Post-hoc diagnostic (not a re-score; the frozen score stands):** if anchor quotes inside `omitted_conditions` also counted, the totals would be COLD 35, **WARM_LIBRARY 36**, WARM_RAW_A 36, BLIND 35. Even then WARM vs COLD is +1 < +2 and the 20 pp gain is impossible, so **the pre-registered decision is unchanged**.
5. **Ceiling:** COLD started at 35/36, so the maximum possible gain was 1/36 = 2.8 pp. The 20 pp criterion could not be met on this baseline. V2 says nothing about context-conditioned *structure prediction*.
6. **All 12 dispositions are `HOLD_UNRESOLVED`,** so disposition cannot distinguish the arms.

## 3. Bounded quality audit (8 facts)

Status levels:
- `QUOTE_ANCHORED`: the frozen scorer's criterion.
- `SEMANTICALLY_CORRECT (prelim.)`: this agent compared each arm's slot *values* with the Google source text. It is the same model family as the reviewers and the checklist author, so this is **not** independent.
- `INDEPENDENT_HUMAN_REVIEWED`: **none.**

| Fact | Source | COLD | WARM_LIB | WARM_RAW | BLIND | Prelim. semantic note |
|---|---|---|---|---|---|---|
| B1.E2 five-minute Error Rate periods | "measured over each five minute period" | QA ✓ | QA ✓ | QA ✓ | QA ✓ | All values correct. Several arms add that weighting and zero-request periods are unstated (a fair gap). |
| B1.E3 averaging window | "during a monthly billing cycle" | QA ✓ | QA ✓ | QA ✓ | QA ✓ | Correct. WARM, RAW and BLIND (COLD in an omitted note) flag the conflict with "calendar month basis per Project" (B1.E9). **A genuine source ambiguity for human review.** |
| B2.E4 three credit schedules | lead-in of schedule 3 | QA ✓ (value partial) | ✗ (stated in omitted) | QA ✓ ("three tier-specific definitions") | ✗ | Only RAW states it fully in a slot; WARM states it fully outside slots. |
| B2.E8 schedule-3 top band 98.0%–<99.0% → 10% | table row | QA ✓ | QA ✓ | QA ✓ | QA ✓ | All correct. No GitHub 99.9/quarterly values were transplanted. |
| B2.E13 reseller substitution | context sentence | ✗ (only the impacted-orders clause) | ✗ (stated in omitted) | QA ✓ | QA ✓ | WARM correct but not credited. COLD truly missed the anchor. |
| B3.E2 claim deadline | "within 30 days from the time Customer becomes eligible…" | QA ✓ | QA ✓ | QA ✓ | QA ✓ | All correct, and all flag that the start event ("eligible") is undefined. |
| B3.E4 cap | "will not exceed 50% of the amount due … for the applicable month" | QA ✓ | QA ✓ | QA ✓ | QA ✓ | All correct, including the base (applicable Covered Service, per month). |
| B3.E12 exclusion: Admin Console quotas | exclusion (c)(iv) | QA ✓ | QA ✓ | QA ✓ | QA ✓ | Correct. Several arms note that quota values sit outside the packet. |

**Human review still required:**
- all 36 checklist elements × 4 arms (the checklist itself is agent-authored);
- the 3–7 "unmatched reviewer challenges" per packet/arm;
- the billing-cycle vs calendar-month question;
- whether WARM's E4/E13 statements in `omitted_conditions` should count under a revised rubric (any such revision must be prospective, not applied to this run).

## 4. What this does and does not show

- **Observed:** on three Google packets, a GitHub-derived template library gave no measurable proxy gain over cold or raw-example memory, and cost slightly more than cold. The cheaper blind single call matched cold.
- **Not shown:** legal correctness, generalization, that libraries cannot help where the baseline has headroom, or anything about structure prediction. Those claims remain open.
- **Lesson carried into V3:** do not choose a benchmark whose baseline sits at the ceiling. Score facts wherever the pipeline surfaces them, prospectively. Measure cost from real usage, not the preflight estimate.
