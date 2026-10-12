# Claude Code Execution — Sophon E0: Native Semantic Layer Access

**Date:** 12 October 2026
**Status:** Execute now. This is the ONLY experiment authorized for this run.
**Primary plan:** SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md, Section E0.
**Governing authority:** SOPHON_CHARTER.md v1.1 and CLAUDE.md.
**Prior broad prompt:** Claude_Code_Sophon_Governed_Transition_Experiment_2026-10-12.md is a DEFERRED integration test; do not execute it during E0.

## 0. Mission

**One primary uncertainty (R1):** Can we inspect **and execute** an existing, independently authored, native dbt/MetricFlow semantic metric against its actual warehouse data, through MetricFlow's own interface, and retain independently reproducible evidence of what ran?

Do not build an entire Sophon workflow, a proprietary governance language, typed governing-rule IR, policy store, amendment mechanism, LLM pipeline, audit database, a GUI or a new general semantic engine.

E0 is a disposable but reusable **engineering substrate** for later E1–E8. It is NOT a governed-transition validation, a governance accuracy result, a customer outcome validation, or a comparative Claude-vs-Sophon experiment.

Read fully, in order:
1. origin/main:SOPHON_CHARTER.md (v1.1) and origin/main:CLAUDE.md.
2. origin/main:SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md.
3. origin/main:Claude_Code_Sophon_E0_Native_Semantic_Adapter_2026-10-12.md (this file).
4. Relevant bounded prior results: origin/codex/alignment-review-agent:viability/RESULTS.md and viability/public_nyc/README.md; origin/experiment/governance-integrity-2026-10-11:experiments/governance_integrity/DECISION.md and RESULTS.md. Preserve the STOP_KERNEL result as a **bounded former hypothesis**, not a reason to abandon an actual native semantic integration.

State explicitly in PRIOR.md that E0 tests only infrastructure feasibility (§5 Stage 1) and is compatible with TRANSPOSE, TRACE, VERIFY and AUDIT later without pretending to implement those here.

## 1. Protect local work; isolate the experiment

- Inspect git status and git worktrees. Do not discard, overwrite, reset or stash changes without owner consent.
- Fetch origin/main. Work on an **isolated worktree + branch** created from that ref:
  experiment/e0-native-metricflow-2026-10-12
- Store all new Sophon E0 materials under experiments/E0_native_adapter/.
- Do not edit or merge existing PR #2, PR #3, the v1.1 charter, prior prompts, Rulebook or the external upstream project in place.
- E0 upstream may be cloned or installed into a local ignored/cache directory; record exact URLs, SHAs, licenses, dependency versions and file hashes. Do not vendor copyrighted external files into Sophon without verifying permissions and necessity.
- Use PowerShell-friendly commands whenever possible; if a native Windows dependency fails and a Linux/WSL reproduction is needed, clearly distinguish what was **actually executed** from what is merely suggested.

## 2. Establish and freeze the source/runtime gate first

Candidate external semantic project:
https://github.com/behramkorkut/Governed-Analytics-Agent
Previously inspected candidate revision:
312e97ad192dcef02f688e31edc0a08c6cf4345f

On a clean pinned checkout:
- Confirm the repository and revision exist; inspect LICENSE, README, project lock/requirements, dbt profiles, actual semantic-model and metric definitions, data generator and CI workflow.
- Confirm it includes *pre-existing* native dbt/MetricFlow semantic models and declared metrics (e.g. completed_revenue or revenue), plus DuckDB and a data generator. Do not assume README claims imply runnable behavior.
- Choose ONE existing metric, and record its exact semantic model, measure/expression, dependencies, dimensional grain, filtered status if applicable and source revision.
- Record whether inputs are real/customer or synthetic. This upstream appears to use **synthetic retail data**. That is acceptable for E0, but it MUST be labelled and not presented as authentic compliance evidence.
- Record commands for installation and reproducible data generation, dbt build and parse, native MetricFlow metric listing/compile/query.
- Record first-failure diagnostics and one focused environment repair if necessary.
- Freeze a tiny E0 PROTOCOL.md and environment/source manifest **in a commit before executing the scored acceptance query**. Do not adjust pass criteria post-result. Any protocol correction must be explicit, dated and leave originals intact.

Budget: **one upstream + at most one fallback only if blocked**, one metric, one native query, one repeat, one negative control, one independent cross-check when feasible. No platform provisioning, no paid model API calls, no extensive research or sprawling architecture.

## 3. Build the narrow executable path

Using the pinned external project's documented build path:

1. Generate/load actual upstream data rows; record row counts and stable dataset fingerprints or reproducible generator seeds.
2. Run dbt build and parse so the semantic-layer manifest exists; preserve environment, exit codes and logs.
3. Run **the native MetricFlow interface** to list/query the selected metric on those warehouse rows. Collect actual metric output, command invocation, exit status, relevant native compilation/SQL when exposed, object identity and origin hashes.
4. Repeat the identical native query against unchanged inputs; confirm the result is stable (or document why stability cannot be guaranteed and choose INCONCLUSIVE if the gate depends on it).
5. Run a negative control: an invalid metric name or unsupported dimension must be rejected by the native client. The wrapper must not fabricate a successful result.
6. When tractable, independently compute the expected result from source/fact rows with an explicit query; label that query as a **cross-check**, never as evidence that MetricFlow itself executed. Explain any discrepancies.
7. Inspect whether an existing downstream dashboard/AI consumer actually calls the same native metric/catalog; report SUPPORTED_BY_SOURCE_CODE vs NOT_VERIFIED. Do not create a new consumer merely for the demo.
8. Create, only if necessary, a **thin read-only adapter** that invokes the native CLI/library and serializes metadata/results/evidence. It must never return fixture values in place of native engine output or implement another metric calculator.

Verification must examine real command exit codes, fingerprints and results. Automated negative tests should fail if native invocation is stubbed, results are replaced by canned fixtures or upstream metric identity silently changes.

## 4. Acceptance criteria / decision

**PASS_NATIVE_RUNTIME** requires:
- Exact source revision and executable environment recorded.
- Successful dbt build + semantic manifest.
- Successful native MetricFlow query on underlying records, with result.
- Verified association between actual metric identity, existing definition and the executed native result.
- Identical query reproducible or any legitimate nondeterminism adequately isolated.
- Native negative control rejects invalid input.
- Independent evidence retained that a fresh process can inspect to reproduce the result.

**BLOCKED_NATIVE_RUNTIME** if the necessary native execution cannot run after the bounded repair and allowed fallback. Do not simulate it with SQL/CSV/Publicodes/mock YAML; preserve exact errors and smallest suspected blocker.

**FAIL_E0** if purported native execution proves to be a stub, cannot be associated with the existing declared metric or produces contradictory evidence that cannot be reconciled.

**INCONCLUSIVE** when provenance/oracle/reference cannot be established, or execution is unstable and cannot be reliably attributed.

Never change the statuses or acceptance threshold after observing results. A successful E0 retires ONLY R1. It does not prove interpretation, binding, typed IR value, independent legal/semantic verification, customer value or feasibility of a production Snowflake/Databricks integration.

## 5. Deliverables and stop

Produce in experiments/E0_native_adapter/:
- PRIOR.md — charter alignment, prior negative experiments, what is and is not being tested.
- PROTOCOL.md — one hypothesis, preregistered PASS/FAIL/BLOCKED/INCONCLUSIVE criteria, and protocol commit SHA.
- SOURCE_GATE.md — exact upstream revision, license, generated-data classification, setup/dependency provenance.
- README.md — *exact commands actually run* and replay instructions for PowerShell; Linux/WSL commands if applicable.
- Minimal adapter (if needed) and tests, one valid query + repeat + invalid control.
- RESULTS.md — command/output/identity receipts, fingerprints, observed exceptions and corrections, elapsed/runtime inputs if actually recorded.
- DECISION.md — one exact gate result and the single smallest next experiment, E1 known predicate binding, ONLY if E0 passes. If E0 does not pass, report the smallest diagnostic/repair before E1.
- Evidence/log files small enough to commit. Larger generated DB/data remain ignored with reproducible generation instructions.

**Mandatory end condition:** STOP after E0. Do not implement E1, E2, E3, IR, change propagation, approval systems or the broad G1 integration test in this run.

Commit protocol before execution, then results/implementation to the experiment branch; push it and open a **draft PR** if supported, without merging.

Report back:
- Branch, commit SHAs and PR URL.
- Pinned source, one metric and genuine native query result.
- Reproduction commands and negative-control outcome.
- Exactly what succeeded, failed, was not attempted, or remained unverified.
- ONE gate status and reason.
- Recommended E1 input/next step, **not** automatic execution.

**No architectural theater. No self-confirming synthetic substitutes. Prove native execution first.**
