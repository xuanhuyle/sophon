# Microsoft cold Jev screen — results, 2026-10-16

**Decision: `STOP_DATASET_AT_CEILING`.** Of 6 authorized calls, exactly 6 attempts were made and 6 responses received, with no retries or failures. **Zero candidate reproducible disagreements**: all three definitive Microsoft decisions agree with their frozen engineering prelabels in both repeats.

Per Task 007, there is no Oracle holdout query, no library update and no new sourcing. The owner approves any further paid work separately.

Scope labels: `MANUALLY_CURATED_SOURCE_EXCERPTS` · `MULTI_LABEL_PER_EXCERPT` · `AUTOMATIC_SUBPROVISION_SEGMENTATION_NOT_IMPLEMENTED`. The prelabels are the implementer's judgement, not certified legal truth, so agreement validates nothing legally.

## Run facts

| Item | Observed |
|---|---|
| Authorization | Owner, 2026-10-16: ≤6 calls on MS1–MS3, two repeats each (`tasks/2026-10-16_approved_microsoft_cold_screen.md`) |
| Window | 07:27:00Z → 07:27:01Z; per-call latency 156–466 ms |
| Model | requested **`jev-1.13.0`** explicitly, reported `jev-1.13.0` in all 6 responses; nothing was substituted |
| Inputs | Each request carried the frozen MS context as `state.clause`, a one-line source identification as `state.context`, and `prior_provision_skeletons = []`. Questions were the 10 `probe.questions()`, byte-identical to PR #22 (`questions_sha256 eebc8252…`). Each pair repeated the identical request object. |
| Not sent | Labels, evidence fields, split names, other decisions' quotes and any Oracle text (offline test `test_cold_screen.py`) |
| Hashes | plan `1d46a876…`; request MS1 `7f45bfa1…`, MS2 `525fab95…`, MS3 `79ecca69…`; raw recording SHA-256 `6e963839…` (git-ignored; see `receipt_ms_cold_20261016_approved_001.json`) |
| Tokens | 1,105–1,226 input and 190 output per call (6,970 input and 1,140 output in total) |
| Cost | Not reported by the API; not estimated |

## Per-case outcome (scored function only; pass = p ≥ 0.5)

| Case | Function | Frozen label | Repeat 1 | Repeat 2 | Verdict |
|---|---|---|---|---|---|
| MS1: "We will provide at least 90 days’ notice…" | OBLIGATION | YES | 0.74 | 0.73 | agrees in both |
| MS2: "You may not unilaterally offset…" | PROHIBITION | YES | 0.90 | 0.90 | agrees in both |
| MS3: Limitations ("do not apply to…") | PROHIBITION | NO | 0.07 | 0.07 | agrees in both |

**Repeat stability.** Across all 30 label pairs (3 cases × 10 labels), the largest repeat-to-repeat change is 0.06 and the mean is 0.014. Two unscored labels cross 0.5 between repeats, both on MS1: EXCLUSION 0.53 → 0.48 and CROSS_REFERENCE 0.45 → 0.50. Two repeats are not a noise distribution, but they show this endpoint is close to deterministic for identical requests.

**Unscored observations.** These are not scored, and no negative oracle exists for them.
- **MS1:** PROHIBITION 0.61/0.62. Its context also contains "We will not modify the terms of your SLA…", a self-restraint promise, so the reading is defensible.
- **MS2:** PERMISSION_RIGHT 0.79/0.78.
- **MS3:** EXCLUSION 0.99/0.98, which matches the source.

## Interpretation and limits

- **Ceiling.** The three update decisions show no headroom for the cold model. This mirrors PR #22 (15/16 cold; Google B3c PROHIBITION 0.07).
  - MS3 is easier than intended, because the frozen PROHIBITION question itself says "Do not infer prohibitions from mere definitions or exclusions".
  - MS1 and MS2 are explicit modal language.
- **No library-learning test is justified on this dataset.** It has no cold error to correct. Querying the Oracle holdout would spend calls on a holdout with nothing learned to evaluate.
- **What this does not show.** It is not general Jev accuracy (three checks; no population rate) and not legal correctness. It also says nothing about the four UNRESOLVED cases, which still turn on the owner's undecided claim-prerequisite rule.
- **What would change the picture.** Same-family provisions whose correct function is clear *and* not cued by the question wording, or an owner taxonomy rule that makes MS5/OR5-style claim prerequisites scorable. Either needs separate approval.

Reproduce offline: `python3 prototype/jev_memory_causal_probe_v0/cold_screen.py score`. This needs the local git-ignored recording; its hash is in the receipt.
