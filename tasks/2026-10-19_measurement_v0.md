> **SUPERSEDED — DO NOT EXECUTE (19 October 2026).** This E4/E5-centered task reuses lab-authored fixtures and is not a valid first external performance benchmark. Replacement: [Task 010](../../tree/research/measurement-v0-independent-baseline-2026-10-19/tasks/2026-10-19_task_010_independent_measurement_v0.md) on branch `research/measurement-v0-independent-baseline-2026-10-19`. Historical text below retained solely for traceability.

# TASK 009 — Measurement V0: first falsifiable baseline-versus-Sophon observation

**Owner intent (19 October 2026):** Stop building architectures without a repeatable performance datum. Measure a stable governed-change task, then improve only one identified failure. This is a ONE-INCREMENT, measurement-only experiment; **no new Sophon capability**.

**Current binding product direction:** read `origin/main:SOPHON_CHARTER.md` v1.2, `PROJECT_STATE.json` and `ENGINEERING_WORKFLOW.md`, plus `CLAUDE.md` and `AGENTS.md`. The older E5 branch carries charter v1.1 and lacks modern project-state/guard files: treat that as historical branch context, **not** permission to revive the old product/research goal. Record the discrepancy; do not merge whole branches to repair it. Separate, previously saved Task 008 concerns current-state reconciliation; do NOT implement it here.

**Implementation branch:** `experiment/measurement-v0-2026-10-19`, already created from `experiment/e5-forward-transposition-2026-10-12` @ `8277cd8607df4344f05070a34c615997ce78eeb8`. Keep E0–E5 directories and recorded verdicts untouched. New work only in `experiments/Measurement_V0/`. Open one **draft stacked PR** against `experiment/e5-forward-transposition-2026-10-12`. Do not merge.

## Required grounding, before writing/running

Inspect actual E0 native source/environment and E4/E5 implementation, including:
- `experiments/E0_native_adapter/DECISION.md`, `README.md`, `src/mf_adapter.py`;
- `experiments/E4_independent_verification/src/checker.py`, `src/candidate_stack.py`, `RESULTS.md`, `DECISION.md`;
- `experiments/E5_forward_transposition/PROTOCOL.md`, `RESULTS.md`, `DECISION.md`, `README.md`, `src/e4_adapter.py`, `ir/NATIVE_BINDING.json`, `ir/P1_v2.json`, `evidence/gate.json`.
- Relevant conventional upstream project's native dbt tests and Git/CI behavior. Upstream project is `behramkorkut/Governed-Analytics-Agent@312e97ad192dcef02f688e31edc0a08c6cf4345f` (pinned in E0); confirm the source/license/lock, do not substitute other projects.

**Known observations, not new scores:** E4 already catches author-planted `>` vs `>=`, status changes, country swaps, dbt staging alias changes; E5 already catches wrong `>=119`, `>120`, returned-status changes and P2 collateral edits. All are LAB_AUTHORED tests against a synthetic warehouse. Merely replaying these and announcing another PASS is **not Measurement V0**. The actual question is whether a *competent conventional alternative* already handles a changed implementation as well, for the same approved meaning and evidence. The traditional baseline must not be just `dbt build` without any governing semantics.

## One unknown

> For a *fixed, already-LAB-approved* E5 policy/metric binding, does the existing Sophon E4/E5 checking path identify an implementation-originated material semantic drift and accept a harmless change **better than ordinary Git/dbt/MetricFlow + appropriately written conventional tests and review**, when both have the same information?

**Primary measured outcomes**: material miss count, harmless-change false alarm count, appropriately indeterminate outcomes, native-evidence validity, elapsed runtime and separately identifiable setup/maintenance effort. Avoid a single composite accuracy percentage for two examples.

## Increment procedure with fail-fast gates

**Gate 0 — Preflight/reproduction (read-only).** Inspect `git status`/worktrees; do not overwrite local work. Reconstruct the pinned Linux/WSL-capable E5 environment and execute at least its unchanged relevant native control and frozen reference check, or the shortest existing reproduction command. Record the exact commands, stdout/stderr/exit codes, tool versions, source hashes, elapsed time and whether source data were regenerated. If native execution fails, allow only a short reproducible environmental diagnosis; **STOP with `BLOCKED_REPRODUCTION`** and a single concrete blocker. Never replace native execution with invented SQL/YAML.

**Gate 1 — Freeze a small discriminating plan, BEFORE scoring.** One independently introduced material implementation-side change **not already one of E4/E5's named mutations**, and one meaning-preserving edit. Fix the unchanged approved E5 v2 meaning and applicability date, frozen source rows/snapshots, unchanged semantic binding, and the intended positive/negative outcomes. Restrict changes to a disposable clone of the pinned *existing* dbt semantic project (native dbt/model code). Prefer using a separate changer with no access to scorer/reference if the environment permits genuine isolation; otherwise label the test `AUTHOR_DESIGNED_NONBLIND`. Never call that independent validation. Freeze scenario manifests, hashes, evaluation protocol and independent source-row oracle BEFORE revealing candidate results. Use a genuine counterexample row for a material change and verify that the oracle differentiates it; otherwise mark `INVALID_NONDISCRIMINATING_CASE` and STOP. Do not quietly edit the test after a failure. Do not invent extra cases to find one baseline miss.

**Gate 2 — Competent baseline first.** With the *same* approved requirement, initial native metric, version history, binding/source-data access and time budget, perform the ordinary reasonable workflow: Git diff/review, current dbt checks/native MetricFlow query, and conventional assertions/test(s) written from the approved requirement in advance rather than after inspecting the answer. Baseline can reuse established independent row-level verification if that is what competent teams would normally use; charge its setup/maintenance cost and do not withhold from the baseline any evidence given to Sophon. Record how it classifies BOTH candidate changes: material / harmless / unknown, with supporting native/source data and time spent. If baseline detects both correctly, this is **valuable zero-gap evidence**; still run or compare the unchanged Sophon path only if fair/reproducible, then STOP.

**Gate 3 — Existing Sophon path, unchanged.** Run the *already-existing* E4/E5 native verifier on the exact same fixed inputs/snapshots after baseline verdicts are locked. Reuse E4's comparison algorithm and E5's v2 oracle/adapter without altering their reference or writing mutation-specific branch logic. If the interface cannot accept such an implementation-originated change without substantive new code, score `BLOCKED_NO_GENERAL_RECONCILIATION_INTERFACE` and STOP rather than implementing E6. Do not conflate E5's `PROPOSED_VERIFIED_NOT_DEPLOYED` with actual deployment. Do not claim this measured production agent conduct or contract/legal accuracy.

**Gate 4 — Write the data point.** Save `experiments/Measurement_V0/PROTOCOL.md` (pre-scored and committed/frozen), a machine-readable `SCORECARD.json` with **one row per arm × scenario**, a human-readable `RESULTS.md` with observed/inferred/assumed separated, the exact execution references and setup/assessment time, and `DECISION.md` with one of:
- `NO_OBSERVED_INCREMENTAL_ADVANTAGE_IN_V0` — competent baseline works as well;
- `CANDIDATE_INCREMENTAL_SIGNAL_NOT_INDEPENDENTLY_VALIDATED` — Sophon wins one case but this is small/author-designed;
- `BOTH_ARMS_FAIL_OR_UNRESOLVED` — localize failures next;
- `BLOCKED_REPRODUCTION`, `BLOCKED_NO_GENERAL_RECONCILIATION_INTERFACE`, or `INVALID_NONDISCRIMINATING_CASE` — do not claim a scored comparison.

Score reliability first, not lines of code, test count or documentation length. Show raw per-case results; zero samples is not a score. Any baseline or Sophon setup labor already invested must be disclosed as prior sunk effort, not fabricated exact human minutes. Do not compare a sophisticated Sophon oracle to a conventional baseline denied that oracle.

**Budget and exclusions:** Zero TypeSafe/Jev/external model-provider API calls, zero deployments, no paid services, no new software architecture, event store, policy engine, parsing model, agent executor, ontology, additional BI adapters or app UI. Reuse pinned tooling. Budget approximately 90 minutes of investigation/runtime; if native rebuild makes this impossible, record the bottleneck and STOP rather than silently exceed or change methodology.

**One adverse case required:** show either a real material mismatch caught by reference evidence or a concrete counterexample that invalidates the comparison. Do not relabel a failed experiment as a green setup test.

After writing the result, STOP. Do not automatically fix errors, tune prompts, modify golden fixtures or start E6. Ask the engineering lead to review `SCORECARD.json` and the real evidence before another increment.
