# Measurement V0 — decision

**Task outcome: `MEASURED_BASELINE`.** The record holds one externally grounded, reproducible baseline observation. Baseline-A reviewed PolicyEngine-US PRE `5152b5f7` against 7 CFR 273.10(e)(2)(ii)(A) and 7 U.S.C. 2017(a). It was given a **pre-scoped** question (the net-income → allotment relation). Its result: **`BASELINE_CORRECT` (`DETECTED_MISMATCH`)** after 293 s of session wall time. That figure excludes candidate search, oracle construction, protocol and scorer writing, setup and review, none of which was measured as labour.

*Editorially revised after the engineering-lead review on this PR. The frozen protocol, scorer, scorecard and raw evidence are unchanged.*

## Disposition

- **KEEP the primary observation** as one narrow, real baseline datum: one correctly answered pre-scoped external review.
- **The evaluation harness is NOT validated.**
  - The frozen scorer mis-scored the secondary run B as `BASELINE_ABSTAIN`. That frozen score remains B's machine score of record. The post-hoc reading does not replace it.
  - The 6/6 scorer controls missed this real pattern, so they cannot certify the scoring method.
  - B was cued by in-window fix commit messages. It is a contaminated secondary observation, not an uncued hard negative, and no false-alarm rate can be derived from it.
- **Archive Measurement V0** as one baseline observation. Do not add a Sophon arm, an E6, a re-score, a re-run or a second case under this PR.

## What was learned

Once a competent conventional AI-assisted reviewer is handed three things, it identifies this arithmetic mismatch rapidly:
- the governing source,
- the code revision,
- **which relation to inspect**.

The case selection (found by searching known fixes) and the prompt were favourable to baseline success. This is a capability demonstration, not a prospective error-discovery test and not a representative sample. The upstream defect's historical persistence is **not** a measured inability to detect drift.

## What remains completely unmeasured

The following are all unmeasured:
- unprompted discovery of *which* existing governance requirement and operational implementation are affected by a change;
- amendment propagation;
- source-corpus evolution;
- any incremental value of Sophon.

As-of applicability is also unverified. Continuity of the pinned 2025 CFR and 2024 USC texts to January 2026 was not established.

## Required before any reuse of this harness

1. Scorer semantic precedence and contradiction tests (for example, `CONFORMS` versus an equivalence-noted `STATE_OPTION_DEPENDENT`), frozen before scoring.
2. Negative controls whose visible history does not narrate the fix.
3. An explicit end-to-end effort accounting if effort is to be claimed.

## Next decision (not started; not authorized by this PR)

Before commissioning any further build, independently define a **prospective** task. It should measure unprompted discovery of which existing governance requirement and operational implementation a change affects. It needs a competent Git/LLM/search/lineage baseline and an independently established scoring reference. Do not assume a normative layer is needed: only a measured residual gap can justify adding Sophon code.

**STOP.**
