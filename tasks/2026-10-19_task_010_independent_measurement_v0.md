# TASK 010 — Independent Measurement V0: one external case, one actual baseline data point

**Status:** Authorized research task replacing Task 009 (the E4/E5-centered plan). **Owner objective:** end the cycle of designing a new architecture and then declaring it successful on author-planted examples. Get ONE reproducible, externally grounded *measured observation* before building Sophon features. The first measured arm is a capable conventional baseline. Do not infer Sophon's benefit from that measurement.

## Project and chronology
- **Base:** `main` at `f1d7688b463009e92092cd5279b64cbb297ca914`; work on `research/measurement-v0-independent-baseline-2026-10-19` (already created). Read `SOPHON_CHARTER.md` v1.2, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md`, and applicable agent instructions first.
- `main` still contains the old Jev-learning active research contract; **that is out of sync with the owner's new institutional-reliability direction**. Task 008 addresses this on a separate branch. Do not mix in charter/guard edits or silently relabel historic experiments.
- E0 is infrastructure feasibility. E1–E5, especially E4/E5's LAB-authored source, lab-added metric, synthetic data and self-designed variants, are **reference code only, NOT the evaluation dataset, oracle or baseline for this task**. Read their decisions for the failure modes, but do not transfer their tests as independent evidence.
- This task is scoped to charter VERIFY/TRACE, Stage 2 *measurement-method setup*, **not** a demonstrated Stage 2 reliability result.

## The one research question
Can we observe and reliably score an actual governed-meaning/implementation alignment assessment on a case that was independently authored BEFORE Sophon entered the picture, using only a competent conventional AI-assisted/Git/tests/native-tools workflow?

A result of `BASELINE_CORRECT`, `BASELINE_MISS`, `BASELINE_ABSTAIN`, `INCONCLUSIVE` or `NO_ELIGIBLE_CASE` is acceptable if backed by raw evidence. **No Sophon-vs-baseline claim** is authorized yet.

## Precommitted case eligibility — gate before any scoring

Find *up to three* candidates and select **one**. Prefer a public, lawfully reusable governing contractual/policy/specification text with a specific observable condition, exception or threshold **and** an independently pre-existing executable operational implementation. Prefer a genuine native BI semantic definition where a credible governed one exists; do not fabricate a BI metric merely to fit the charter. An independently authored OSS business-rule implementation or executable policy system is an acceptable first measurement surface **only if explicitly labeled as non-BI exploratory evidence**, consistent with the charter's direct non-BI access path. Avoid a generic unit-test exercise unrelated to governance.

Both source text and implementation must predate this task and be pinned by stable URL+commit/version/hash. `independent` here means authored outside the Sophon experiment, not necessarily by unrelated companies. Show a *real* traceable binding between governing requirement and existing implementation (documented link, actual used field/API, or well-supported mapping); don't silently assume semantic equivalence based on names.

Reject candidates requiring a legal conclusion we cannot independently establish, unverifiable private facts, synthetic contracts/metrics, a new runtime, a conveniently rewritten policy, extensive integration or uncertain licenses/access. Mark unsupported conditions UNKNOWN, not a correct answer.

**Frozen expected behavior:** Make a checkable reference derived from the external normative source plus reproducible actual behavior or independently available official acceptance tests. A second model agreeing with Claude is **not** independent ground truth. If correctness cannot be independently established, STOP `BLOCKED_ORACLE`. Do not choose a case simply because it is likely to defeat the conventional baseline.

If none of the three candidates qualifies in a bounded search, STOP `NO_ELIGIBLE_CASE`. Record precisely what is missing and what kind of case could fix it. **Do not manufacture a substitute.**

## Only after one case passes eligibility: one measured baseline

1. **Freeze the case, scope, source, implementation revision, question, known-at/effective dates when relevant, expected outcomes, scorer and stop rules** in a committed `measurement_v0/PROTOCOL.md` **before** the scored baseline run. A historical real-world defect/change is preferred where provenance and chronology are verifiable. An artificially modified fixture may be used only as an *instrument sensitivity control*, NEVER passed off as a naturally occurring drift or independent reliability sample.
2. Establish what a competent engineer could do **without Sophon** using existing documentation, Git/history, native build/tests, normal automated checks and a capable LLM/Claude Code as engineering assistant. Grant access to the same source, relevant system and scope that a future Sophon arm would receive. Do not handicap it with `dbt build` alone, nor give it a hidden oracle.
3. In a fresh run, record the **actual baseline outcome** (`CORRECT_ALIGNMENT`, `DETECTED_MISMATCH`, `INCORRECT_ASSURANCE`, `FALSE_ALARM`, `ABSTAIN_UNOBSERVABLE`, `INCONCLUSIVE` as applicable). Include command inputs, stdout/stderr, exit codes, actual native program output or static checker evidence, elapsed wall time, setup/review effort (estimate only if not directly measured), source/commit hashes and limits. If access to native execution is blocked, STOP `BLOCKED_RUNTIME`; do not invent output.
4. Independently check that the scorer *could* reject a known-wrong answer (negative control); clearly distinguish this control from scored observations.
5. Produce `measurement_v0/SCORECARD.json` with **at least one actual scored baseline observation** (or an explicit no-score blocker outcome), `RESULTS.md` distinguishing OBSERVED/INFERRED/ASSUMED, and `DECISION.md` with `MEASURED_BASELINE` or explicit blocker. The measured quantity is the per-case decision and evidence, not misleading percentages. Attach a comparable schema for a later Sophon arm, but **do not run or create a Sophon arm in this task**.

## Hard stops
- **Do not** start from E4/E5 tests or author-built contracts; do not tune test cases to fit a method.
- **Do not** implement Sophon, build E6, train Jev, create classifiers/DSL/agents/BI adapters/extra test harness infrastructure, or change the charter.
- **Do not** make paid third-party API calls or deploy operational actions. Local Claude Code interactions permitted within existing user plan; record model/time if used as part of the baseline.
- Timebox candidate discovery and feasibility to roughly 90 minutes of active work. Do not continue indefinitely in search of a success case.
- If methodology fails, state why and STOP; no architecture rationale, post-hoc oracle repair or score inflation.

## Deliverable and review
One small draft PR from this branch to `main`, containing only the task/protocol, pinned external evidence references and baseline score or explicit blocker. Preserve raw results when lawful/practical; links alone do not prove a run happened. Explain the test's selection bias and the exact unanswered question. **STOP** for independent engineering-lead review. The next increment, if any, is a preregistered comparison on a separately held-out external case—not automatic enlargement of this experiment.

**Claim limit:** One externally grounded baseline observation is a starting data point, **not** a reliability rate, statistical estimate, proof of architecture or proof of customer value.
