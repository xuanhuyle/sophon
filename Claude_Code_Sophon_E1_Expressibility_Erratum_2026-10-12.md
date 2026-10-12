# Claude Code — Sophon E1 Erratum: Native Expressibility Is Not Only Direct Dimensions

**Date:** 12 October 2026
**Status:** EXECUTE FIRST, BEFORE E3. This is a bounded retrospective correction, not a rerun of the original precommitted E1 experiment.
**Governing:** SOPHON_CHARTER.md v1.1, CLAUDE.md, AGENTS.md and SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md.
**Source of defect:** E1 PR #5 concluded B1 ("completed-order revenue for lines with charged unit price >= 100") was PRESENT_IN_SOURCE_NOT_EXPOSED and *not natively expressible*. E2 PR #6 subsequently found a valid native MetricFlow **metric-filter expression at order-line grain** that reproduces the E1 reference amount. The distinction is architectural: "not a declared semantic dimension" does **not** imply "impossible to express using native semantic metrics".

## Mission — one correction, no architectural expansion

Independently reproduce the E2 counterexample and issue a transparent E1 erratum. Show precisely:
1. That `unit_price` is not directly declared as a native dimension in this pinned metric stack (still true).
2. That the threshold is **natively expressible by combining existing MetricFlow metrics at the sales-line grain**, **if its mathematical preconditions hold** (to be independently confirmed).
3. That the historical E1 B1 assertion of "cannot be expressed" was wrong in the bounded environment and therefore its formal PASS_KNOWN_BINDING *as originally precommitted* must be qualified / withdrawn. Preserve E1's evidence as an immutable historical result; do not erase its other positive or safety findings.
4. That later checking must distinguish DIRECTLY_EXPOSED, NATIVELY_DERIVABLE_WITH_PROOF_AND_GUARDS, SOURCE_PRESENT_BUT_UNSUPPORTED_BY_NATIVE_SEMANTICS, and NOT_FOUND_IN_BOUNDED_ESTATE. These are engineering distinctions, NOT a claim to have developed a complete semantic-logic solver.

**Important limitations:** This is a **retrospective replication** of an already observed discrepancy, not a newly blinded discovery; do not call it independent exploratory validation. Verify mathematical equivalence within the pinned generator and data: `revenue = quantity * unit_price` and `quantity > 0` at sales-line grain (rounding/decimal considerations recorded). The expression `revenue >= 100 * quantity` does NOT generally imply `unit_price >= 100` if quantity is zero or negative. Do not generalize beyond proved inputs.

## Mandatory read + branch rules

- Read full `origin/main:SOPHON_CHARTER.md`, CLAUDE.md, AGENTS.md, the engineering plan and this prompt.
- Read E0 PR #4, E1 PR #5 and E2 PR #6 actual PROTOCOL, DECISION, RESULTS, evidence and relevant implementation. Inspect E2 PRIOR.md's recorded native witness, not just its summary.
- Check PR states and `git status` and worktrees; do not overwrite user work.
- Because E0/E1/E2 are currently **unmerged stacked drafts**, create an isolated worktree and branch `experiment/e1-expressibility-erratum-2026-10-12` from **`origin/experiment/e2-blind-discovery-2026-10-12`** so all prior work is present and immutable. If the PR chain merged by execution time, resolve the actual branch topology and document it before branching.
- Work only under `experiments/E1_expressibility_erratum/`; do not modify existing E0/E1/E2 evidence, precommitted scoring, raw solver outputs, charter, plan or prior prompts.
- Push a **draft PR stacked on E2's branch** while PR #6 is unmerged, noting explicitly that it is a chronological erratum to E1 despite being applied later in the PR stack. Link PR #5 in the PR description; leave a comment with the erratum PR link on PR #5 if permitted. Do not merge.
- Pin the external MIT upstream `behramkorkut/Governed-Analytics-Agent` at `312e97ad192dcef02f688e31edc0a08c6cf4345f`, reuse E0 adapter and E1/E2 evaluator/oracle/checks **without modifying them**, and reuse the existing locked virtual environment and build path.

## Procedure and freeze

1. Inspect the original E1 B1 claim and the E2 counterexample code/receipt before writing this erratum. Record them with exact commits and hashes.
2. Prepare a tiny `PROTOCOL.md` stating expected outcome, independent row-based oracle, original-metric baseline, targeted native query, two mathematical guard requirements and negative controls. Commit and push the protocol **before the erratum scored reproduction**; disclose this is not a fresh blind experiment because E2 already reported the outcome.
3. Rebuild the pinned upstream into an ignored local folder or reuse an equivalently verified pinned checkout, confirming original fingerprints and native MetricFlow query.
4. Execute **genuine native MetricFlow**, using the installed `mf` interface, for the line-grain metric-filter witness:

   `mf query --metrics revenue --group-by metric_time__year --where "{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }} AND {{ Dimension('sales__status') }} = 'completed'"`

   This syntax is an **E2-reported candidate**, not a premise of success. Verify exact CLI arguments, compiled SQL / filter semantics and outputs; fail explicitly if the native query doesn't run as claimed.
5. Independently compute **the actual B1 clause** directly from raw order/order-item CSVs (status completed, charged unit_price >= 100, quantity times unit price, year from order date). Do not use the native output as the independent oracle.
6. Confirm the two totals match for every year (E2 reported 2024 1,634,542.08; 2025 1,400,232.75; 2026 752,191.54); validate decimal rounding and line-grain execution. Report actual observed values, not copied expected numbers.
7. **Guard tests:** independently establish whether every relevant line has strictly positive quantity and whether revenue is exactly quantity × unit_price under the pinned model. Include a controlled zero-quantity / negative-quantity counterexample in a disposable copy or a formal numeric proof + minimal computational check to show why the derived filter cannot be authorized universally without guards. Include near-threshold 99.99/100.00/100.01 tests if feasible, without expanding the project.
8. **Anti-vacuity:** prove the witness doesn't merely reproduce the original unfiltered metric; a known below-threshold completed sale must be excluded. Verify the underlying `unit_price` dimension is absent, while the native metric-level filter is accepted. Distinguish "direct exposure absent" from "native derivation possible".
9. Produce a short targeted expressibility capability check for **this pattern** (optional executable helper), not a generalized planner. It must refuse the derived equivalence if guards fail or source computation can't be justified. Do not change E1 evaluator/fixture or E0 adapter in place. No synthetic result substituted for a native result.

## Bounded acceptance decision

Report exactly one:
- **CONFIRMED_E1_ERRATUM:** the existing E1 B1 requirement executes natively through the metric-filter derivation, equals independently computed actual B1 values on the pinned rows, the needed math and granularity assumptions are evidenced, and negative controls reject invalid generalization.
- **NOT_CONFIRMED:** the alleged native derivation is wrong or the independent B1 results fail to agree, despite functioning native runtime. Preserve errors and qualify earlier E2 claim if needed.
- **BLOCKED:** pinned upstream/native runtime unavailable after one narrow repair attempt; no SQL-only workaround.
- **INCONCLUSIVE:** source identity, arithmetic assumptions or oracle independence cannot be established.

**Regardless of which status:** original E1 scored records stay unchanged. Document exact E1 statements that survive and the exact statement that should be superseded, including how that affects E1's original PASS under its frozen protocol. Avoid rewriting history.

## Deliverables

`experiments/E1_expressibility_erratum/`:
- `PRIOR.md`: source evidence, original E1 claim, E2 competing evidence, retrospective nature, precise scope.
- `PROTOCOL.md`: frozen replication gates, guard checks, hashes and protocol commit.
- `README.md`: exact commands actually run; PowerShell equivalents explicitly UNTESTED if so.
- Minimal witness/check script + tests under `src/` and `tests/` if useful.
- `evidence/`: native command, compiled SQL, receipts, data / semantic hashes, row-level oracle result, negative/guard checks.
- `ERRATUM.md`: corrected exposure-vs-expressibility taxonomy, original E1 conclusion's status (withdrawn/qualified), remaining valid E1 observations, impact on R2/R3.
- `DECISION.md`: one gate verdict and direct technical prerequisite for E3.

Commit frozen protocol before reproduction, then corrections and evidence after. Push and open draft stacked PR as above.

**STOP at the erratum. Do not implement E3 in this task.** If confirmed, recommend starting the independently specified E3 prompt on a **new branch** based on this erratum PR head. If not confirmed, block the affected E3 derivation case and report the evidence; do not automatically reinterpret the original experiment as successful.

**Output to owner:** branch/base, PR URL, protocol SHA, actual native/oracle values, proof scope and guard/counterexample, exact corrected E1 conclusion and one status. No proprietary language, full compiler or other side quest.
