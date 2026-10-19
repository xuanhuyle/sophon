# Measurement V0 — results

**Outcome: `MEASURED_BASELINE`.** Primary scored observation: **`BASELINE_CORRECT` (`DETECTED_MISMATCH`)**. Protocol frozen at `88e1107`, before either run. This is NON-BI EXPLORATORY evidence: one case and one primary observation. It is not a rate and makes no Sophon claim.

## What was measured

Case C1 (see `PROTOCOL.md`): does PolicyEngine-US compute the monthly SNAP allotment from net income as 7 CFR 273.10(e)(2)(ii)(A) and 7 U.S.C. 2017(a) require? Under either State rounding option the allotment must be a whole dollar, equal to M − ceil(0.3·N). The implementation at PRE (`5152b5f7`) multiplied floor(N) by 0.3 and kept the cents. PolicyEngine maintainers fixed this in merge `5d88007d` (POST) on 2026-08-25, after the formula had been in place since at least 2022.

## Per-observation results

| Run | Revision | Role | Expected | Baseline said | Frozen scorer | Read adjudication | Wall time |
|---|---|---|---|---|---|---|---|
| baseline-A | PRE | **primary** | DETECTED_MISMATCH | DOES_NOT_CONFORM; R1 = F2 DOES_NOT_CONFORM | **DETECTED_MISMATCH → BASELINE_CORRECT** | same | 4 min 53 s |
| baseline-B | POST | secondary, cued | CORRECT_ALIGNMENT | CONFORMS; R1 = F1 CONFORMS + F2 STATE_OPTION_DEPENDENT ("all options give identical results") | ABSTAIN_UNOBSERVABLE → BASELINE_ABSTAIN | CORRECT_ALIGNMENT → BASELINE_CORRECT (**disagrees with scorer**) | 6 min 05 s |

These are separate quantities, all reported. Formatting failures: 0/2. False alarms: 0/2. Protocol violations found in the transcripts: 0/2. Abstentions: 0 by reading, 1 by the frozen scorer. The non-R1 findings were adjudicated in `SCORECARD.json`. Net-income rounding was flagged as State-option dependent by both runs (A: F3, B: F6), which matches the protocol's UNKNOWN.

## OBSERVED

- The native PolicyEngine model at PRE returns allotments with cents. For a Texas household of 3 in 2026-01, N=1391 gives 367.70 where the source arithmetic gives 367, and 4 of 5 frozen inputs fail. POST passes 5 of 5. Evidence: `evidence/reference_*.json`, Python 3.13.16 with lockfile dependency versions.
- Baseline-A was a fresh Claude Code cloud session with no repository attached, the same model as the orchestrator, and 11 Bash calls. It fetched the pinned commit and the two pinned sources and confirmed both hashes. It read the code, ran the native model on 8 net incomes, and ran 17 repo tests, all of which passed. It reported that the allotment keeps cents "up to $0.90 too high", with example 1001 → 484.70 where 484 is correct. It also gave a phase-out consequence: 2616 → $0.20 where $0 is correct, which matches the oracle arithmetic. It said the non-conformance holds under either State option.
- **The repo's own tests passed on the defective revision.** They encode the defective arithmetic, for example 833×0.3 = 249.9. "Native tests green" alone would have given an incorrect assurance. The baseline caught the defect by reading the governing text and running targeted native checks, not from the test suite.
- Baseline-B was a separate fresh session with 13 Bash calls. It reported CONFORMS and verified this with 19 native runs and a 0..20000 arithmetic sweep, with 0 mismatches.
- Full transcripts (`evidence/baseline_*/transcript_events.json`) show no WebSearch or WebFetch. The only URLs used were the pinned GitHub fetch and the two pinned govinfo URLs.

## INFERRED

- On this case, a competent conventional workflow (Claude Code plus git, native runtime and the governing text) detects the mismatch quickly and cheaply. The PRE defect is therefore **not** a gap that needs Sophon to close it.
- The defect persisted upstream for about 4 years. That says the existing workflow never asked this question. It does not say the workflow was unable to answer it. The measurable gap, if there is one, is *triggering and tracing* (knowing which governing requirement to check against which implementation and when), not *assessing* once asked. This is a hypothesis, not a result.

## ASSUMED / NOT VERIFIED

- Paragraph (e)(2)(ii)(A) was not amended between 2025-01-01 and 2026-01. The CFR 2026 edition was unavailable and eCFR returned 403.
- The maximum allotment M=785 is taken from the model and is outside the checked claim.
- The model has no memorized knowledge of the fix: the fix (Aug 2026) is after the model's training cutoff (June 2026). The bans on post-commit history and web search were instruction-based. The audit confirms compliance, but nothing enforced it.
- The baseline and the orchestrator are the same model family. The oracle does not rely on model agreement (it is source arithmetic plus native execution), but the scorer's "read adjudication" was done by the orchestrator, not by an independent human.

## Protocol deviations and defects (not repaired)

1. **Scorer defect (POST rule ordering).** The frozen scorer checks `STATE_OPTION_DEPENDENT` before `CONFORMS` on POST. It therefore scores B's substantively conforming report as an abstention. The scorer's 6 controls did not cover this pattern. Both values are reported, the frozen value is kept, and nothing was repaired after the fact.
2. **B was cued.** B's legitimate in-window git history showed the commit message "Fix SNAP expected contribution rounding per 7 CFR 273.10(e)". B therefore had a strong hint, and it is not an independent hard negative. A future negative control should use a revision whose history does not narrate the fix (for example, a shallow fetch, at the cost of removing history from the engineer's toolbox).
3. **Scope hint.** The prompt scoped the review to "net income → allotment". That is a narrow question in which the defect is one of a few candidate requirements. A future Sophon arm must receive the identical scope.

## Selection bias and the unanswered question

The case was selected by searching PolicyEngine history for fixes that cite regulations. It is arithmetic, sits in a single paragraph, comes from a well-known federal program, and has an explicit statutory rounding sentence. It is much easier than contractual meaning with cross-references, definitions and amendments. It was not chosen to defeat the baseline, and the baseline did not fail.

**Unanswered:** when a governing source or an implementation changes *without* someone posing the precise question, does a conventional workflow find the affected requirement–implementation pairs at all? And on harder, cross-referenced contractual meaning, does a narrowly scoped assessment still succeed? This measurement does not address either question.
