# Claude Code — Sophon E5: One Approved Amendment → One Native Semantic Change

**Date:** 12 October 2026
**Status:** EXECUTE E5 ONLY, then STOP. E6–E8 and broad G1 integration are NOT authorized in this task.
**Charter:** `SOPHON_CHARTER.md` v1.1, especially §§2–4 and §4A; `CLAUDE.md`; `AGENTS.md`; `SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md` §5, E5 and R6.
**Dependency:** E4 **PASS_INDEPENDENT_VERIFICATION_SIGNAL**, recorded on draft PR #10 (`experiment/e4-independent-semantic-verify-2026-10-12`, head initially `d6fe13d182e0053831c0024314ac0afc484f681a`; verify current PR/head).
**Primary question:** **Given an explicitly approved LAB amendment and an existing real executable semantic definition, can a small Sophon transposition mechanism PROPOSE the correct, minimal native MetricFlow edit, without affecting an unrelated metric, then have an independent checker substantiate its behavior and provenance?**

This is a **Stage 1 infrastructure feasibility experiment** with a narrow reliability signal—not proof of legal accuracy, customer value, autonomous interpretation, production deployment, downstream BI/agent behavior, or general cross-platform transfer. The two Charter directions remain essential: E5 advances **governing→implementation**; E4's checker supplies independent behavioral evidence; E6 later tests **implementation-originated→governance**. Preserve TRANSPOSE / TRACE / VERIFY / AUDIT design compatibility; do not build all four product workflows now.

## 0. Entry and prerequisite gates

First fetch origin/main and **read in full** `SOPHON_CHARTER.md`, `CLAUDE.md`, `AGENTS.md`, `SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md`, and **this prompt** from origin/main using `git show`. Confirm no governing amendments since E4. Read actual E4 PR #10 `PRIOR.md`, frozen `PROTOCOL.md`, `REFERENCE.json`, `VARIANTS.json`, `DECISION.md`, `RESULTS.md`, `README.md` and E4 `src/{candidate_stack,checker,reference}.py`; inspect candidates `M6B` and `M2`, compiled SQL, E4's Q0–Q7 mechanical gate, and its limitation that all examples are designer-authored. Read E3.1's time/approval status code and E3 versioned records/approvals as needed.

Check GitHub PR #4–#10 chain, local `git status` and existing worktrees; preserve uncommitted work and all earlier evidence. **If E4 is no longer a defensible preregistered PASS, STOP and explain why.** E1's original B1 PASS was withdrawn (corrected by the E1 expressibility erratum), E2 discovery was PARTIAL; do not relabel either.

While PR #10 remains unmerged, create a separate isolated worktree/branch:
`experiment/e5-forward-transposition-2026-10-12`
from `origin/experiment/e4-independent-semantic-verify-2026-10-12`. Open a **draft PR stacked on E4's branch**. If E4 merged, determine and document the actual new base (not an empty branch from main lacking prerequisites).

All new files must be under `experiments/E5_forward_transposition/`. Do not edit historical E0/E1/E2/E1 erratum/E3/E3.1/E4 files or their frozen protocols. Do not merge anything.

Reuse public MIT upstream `behramkorkut/Governed-Analytics-Agent` pinned at `312e97ad192dcef02f688e31edc0a08c6cf4345f`, E0's locked dbt/MetricFlow/DuckDB env, E4's real candidate-stack executor, version-aware E3/E3.1 authority/timing checks and the independent E4 row-level comparison machinery.

## 1. One amendment, one affected metric, one unaffected control

**Governing meaning (LAB ONLY).**
- **P1 v1 (pre-existing from E4):** completed order-line revenue, selecting lines where charged `unit_price >= 100.00`, grouped by calendar year of order date. Same source lineage, quantity/revenue assumptions, and order-line grain as E4. `E4 M6B` demonstrates an executable **lab-added** native `premium_completed_revenue` metric with directly exposed `sales__unit_price`; this is NOT claimed to be an organically maintained enterprise metric.
- **P1 v2 (ONE LAB amendment):** change **only** the threshold from `>= 100.00` to `>= 120.00`; retain completed-status definition, amount, currency assumptions, unit price's business meaning, order-date year and grain. The amendment explicitly **supersedes P1 v1 for applicable effective dates starting 2025-01-01**. The 2025 date is deliberately *retroactive relative to the simulated 2026 observation*; label this a hypothetical retroactive amendment, not historical law.
- For a credible two-time-axis check, keep P1 v1's historical LAB source and approval intact, as known on `2026-10-06T00:00:00Z`. Introduce separately authored and separately **LAB_SIMULATED approved** P1 v2 amendment with **observed_at 2026-10-09T09:00:00Z**, simulated approval **known_at 2026-10-10T10:00:00Z**, and **effective_from 2025-01-01**. Use `eval_known_at` `2026-10-06T00:00:00Z` as pre-amendment and `2026-10-11T00:00:00Z` as post-approval contexts. All dates are hypothetical LAB times; do not invent real authority. Make any scope/version supersession rule explicit and testable.
- **P2 unaffected control:** approved customer-France completed revenue, using native E4 `M2` metric `french_market_revenue`. Its LAB-approved source, binding, filter, query, amounts and order-line membership must remain unchanged after the P1 amendment.
- The native baseline for the experiment is a disposable stack that **combines** E4 M6B and E4 M2 definitions and proves that both metrics build and query successfully **before** any v2 edit. The new proposed patch must **modify that existing P1 metric in place**, not merely create a second metric while claiming that P1 was transposed, and not mutate P2. The immutable original P1 revision and new candidate revision remain inspectable.

**Temporal semantics:** At post-amendment knowledge-time, P1 v1 controls **2024 order-date rows** and P1 v2 controls **2025+ order-date rows**. At pre-amendment knowledge-time, P1 v2 **must not appear** and P1 v1 remains the known rule. To avoid a false claim about native platform bitemporal capabilities, historical evaluation may explicitly select **the correct versioned native metric revision** per applicable time range and combine independently verified per-row results. Do NOT present a simple v2 metric queried over all 2024–2026 rows as historically correct if it incorrectly changes 2024. A single deployed MetricFlow metric is not magically version-aware; if automatic native date-conditional application is unavailable, document this limit and the explicit version routing used for the lab. Do not build a full event store or E7 history engine.

## 2. Scope: transposition, NOT another manually planted mutation

The experiment fails its central purpose if Claude the orchestrator manually types the correct YAML patch and then runs E4: **E4 already tested prewritten patches**.

Build the smallest **independent transposition step** that consumes:
1. P1 v1 and P1 v2 typed approved requirement records (or explicitly versioned E3-compatible IR; all difference source-grounded);
2. a fixed **authorized interpretation** and known predicate→native-object binding from E3/E4 (no autonomous legal interpretation or fresh blind mapping);
3. the actual pre-amendment metric definition/catalog and patch constraints.

It outputs:
- impacted objects and **the one existing P1 metric** it proposes changing, plus explicit P2 NOT_AFFECTED rationale;
- the structured clause-level delta (`GE 100.00 → GE 120.00`, same units/target/effective scope);
- a machine-consumable proposed native semantic YAML edit/patch **computed from the v2 specification** rather than pasted verbatim from `REFERENCE.json` or a hand-authored hardcoded 120 patch;
- old/new IR IDs, hashes, observed/effective times, lab-approval provenance, old/new semantic version identities, review status `PROPOSED_NOT_DEPLOYED`;
- unresolved or unsupported cases with explicit refusal rather than an invented default.

**Generation and checking must be separated.** Commit/freeze a small transposer-visible input packet from the approved LAB source/IR and native baseline. It must NOT contain hidden oracle results, scoring expectations or E4 reference expected totals. Run the transposer with only this packet and supported native-catalog evidence, in a separate process/working directory from the scorer. Capture the exact invocation, generated edit, tool/model identity if any, diff and log. A deterministic, limited Python transposer is acceptable; a proprietary DSL, generic AST/compiler, swarm of AI agents or expensive model contest is NOT required.

**Anti-tautology:** Independently demonstrate that the emitted patch is sensitive to the input `GE threshold` (a tiny **non-scored** alternate-value/invalid-unit parameter check, not a second business amendment). An emitter that merely copies a frozen known answer or a hardcoded string 120 is NOT evidence of IR-driven transposition. The verifier/reference must not be generated from the emitted candidate code.

## 3. Pre-freeze feasibility and frozen reference

Before implementing transposition or running scored checks:
1. Inspect the actual E4 `M6B` + `M2` native YAML, patch anchor uniqueness and MetricFlow query capabilities; build baseline in ignored disposable files and confirm genuinely native results. Record pre-freeze feasibility probes and **any** unforeseen expressibility limitation.
2. Create LAB-authored v2 amendment source, a separate LAB_SIMULATED approval object, and versioned normative/typed IR for v1 and v2. Approval scope must include exact source/content hash, clause version and normalized semantic claim. Do not silently modify original E3 v1 source/approval; when approval by reading ID alone is insufficient, bind approval to **meaning/content hash** in E5's minimal version-specific authority check. This is not identity authentication.
3. Create a **separate, independently written raw-CSV oracle** for P1 v1 and v2 using the original E4 source normalization and actual order-line rows, with distinct outcomes for threshold 100 and 120 on registered data. Freeze a control boundary fixture with completed positive-quantity lines at **99.99, 100.00, 119.99, 120.00, 120.01**, and returned/cancelled near boundaries; at least one line must distinguish >=100 from >=120. Pin raw CSV hashes and independent expected **line memberships plus totals**. If pinned data alone cannot distinguish v1/v2, the controlled fixture must; don't award vacuous PASS.
4. Freeze source/IR/approval files, original metric revision, E4 P2 reference, expected output/oracle code/membership, the exact scenarios below, scorer, acceptance gates and fingerprints in `PROTOCOL.md`, `PRIOR.md`, `REFERENCE.json`, `SCENARIOS.json`, `TRANSPOSE_PACKET.json` and a freeze manifest. **Commit and push before the first scored transposer proposal.** File hashes/commit SHA can be recorded in a second manifest commit; avoid self-referential hashes.
5. The person setting reference truth may know the answer, but the transposer process must not read hidden reference/scored decisions. Explicitly call this an **engineered hold-out packet**, not an independently authored unseen-contract experiment.

## 4. The minimally sufficient scored tests

Use one amendment only (100 → 120), one affected native metric and P2 unaffected. No new contract domains. Freeze expected states first.

**Positive lifecycle**
- **F1 – before authority:** `eval_known_at` before amendment observation/approval: P1 v2 is NOT_KNOWN / NOT_APPROVED, even if an implementation with 120 can technically execute. A successful query cannot confer authorization.
- **F2 – after approval / before implementation:** v2 becomes LAB-approved for its stipulated effective window, but the *old deployed/baseline semantic revision* still implements >=100. Detect that P1 v1 **does not conform to P1 v2 for 2025+**, citing a concrete row with unit price in [100,120); mark change **proposed**, never implemented.
- **F3 – generated change:** using only the v1/v2 IR delta + binding + native baseline, the transposer generates one valid minimal patch to the existing P1 semantic metric with >=120; it does not alter `french_market_revenue`, source models or raw input data. Build in disposable checkout and run actual `mf`, including compiled SQL and line-grain result. No pre-handwritten target patch silently substituted.
- **F4 – independent verification:** Compare generated candidate against **independent amended P1 v2 oracle** under E4's genuine native candidate execution and row-level checks, including exact-boundary controls. The v2 implementation passes for applicable rows/periods; the old revision fails under v2. Keep **E4 original comparator logic unchanged as far as its decoupled comparison mechanism permits**; supply new versioned reference via a small explicit adapter only if required by E4's hardcoded `P1>=100` policy and hardcoded E3 v1 approval. **Never claim the E4 checker ran unchanged if its source had to be copied or edited.** Freeze and report all adapter differences; do not change old E4 files.
- **F5 – historical continuity:** show **2024 v1** still matches independent v1 oracle and **2025–2026 v2** matches independent v2 oracle **as known after v2 approval**. As known *before* v2 observation, v2 must not leak into a prior decision. You may run separately preserved v1 and v2 executable native revisions and combine per-line/period results via an explicit, documented version-selection rule; label the result HISTORICAL_VERSION_ROUTING, not a single native metric offering automatic bitemporal joins.
- **F6 – untouched control:** P2's semantic definition (excluding irrelevant compilation metadata) and native output/line membership are identical on the SAME registered source snapshot before vs after P1 edit. Recompute P2 independently; don't infer lack of effect merely because the P2 filename was untouched.
- **F7 – state honesty:** Proposed change is NOT production deployment. Record original and proposed semantic SHA, actual native execution, simulated authority and verification receipts, reviewer role/decision placeholders, and explicit `PROPOSED_NOT_DEPLOYED`. No claimed human approval of deployment.
- **F8 – independent replay:** a new process, with cleared task/session state and rebuilt native candidate project, regenerates/verifies exactly the same normalized amendment→proposal→native outcomes and evidence. The reference/scorer is a distinct step; not a replay of stored candidate CSV only.

**Negative controls**
- **N1 – unauthorized or malformed amendment:** missing/v1-mismatched source hash, unapproved v2 reading, changed unit, unsupported operator or missing binding must STOP with `BLOCKED`/`UNRESOLVED` and no deployable proposal. Do not silently approximate.
- **N2 – wrong patch:** applying `>= 119` or `> 120` instead of `>= 120` (or changing completed to non-cancelled) must be rejected by independent comparison, with a discriminating row and no false verified claim.
- **N3 – P2 collateral mutation:** deliberately change P2 in disposable candidate and ensure the unchanged-control check FAILS with a row-level or semantic/lineage reason.
- **N4 – proposal without deployment:** a candidate patch file alone cannot produce `IMPLEMENTED`, `DEPLOYED` or unconditional compliance status. A simulated v2 approval is not a deployment authorization.

## 5. Evaluation and decisive gates

**PASS_FORWARD_TRANSPOSITION_SIGNAL** requires ALL:
- E4 prerequisite verified; genuine existing executable lab baseline P1/P2; protocol, reference, approved v2 meaning and scoring expectations frozen before generated patch.
- A separate transposer *actually consumes the approved amendment delta and known native binding* and emits a **minimal target-specific native edit**, without reading hidden reference/expected results and without hardcoded correct patch. The emitted edit modifies existing P1 metric in place; provenance chain and independent derivation of 120 from source/IR are inspectable.
- F1–F8 and N1–N4 all satisfy preregistered outcomes (or tighter named subcases). Zero unsupported `VERIFIED` / `APPROVED` / `IMPLEMENTED` / `DEPLOYED` claims.
- Genuine native MetricFlow execution on rebuilt **generated candidate**, fresh independent raw-data v2 oracle, year totals + line memberships/counterexamples, and E4 comparator reused with honest documented adapter if needed.
- Prior v1 remains reproducible; as-known/effective-time checks prevent future leakage and silent rewriting of 2024; P2 is independently checked unchanged; wrong changes are rejected, correct behavior accepted.
- Independent fresh-process reproduction, hash/source fingerprints, original E0–E4 files unchanged, and a bounded cost log.

**PARTIAL_FORWARD_TRANSPOSITION_SIGNAL:** a meaningful IR-driven native proposal is generated and native-checked without any false assurance, but at least one positive prerequisite/test is unproven; list exactly what failed and why. A hand-authored patch that happens to work is **not** an IR-driven transposition PASS.
**FAIL_UNSAFE_TRANSPOSITION:** any silent meaning change, unsupported approximation or unauthorized/unimplemented state is promoted as correct/authorized/implemented; old >=100 incorrectly certified as compliant with v2 on a discriminating dataset; or P2 materially changes without being reported.
**FAIL_NO_TRANSPOSITION:** no actual amendment→IR-driven native patch mechanism, only a manual rewrite or replay of a preexisting E4 candidate, regardless of passing native queries.
**BLOCKED:** genuine pinned native integration/baseline or version applicability prerequisites unavailable after one bounded fix attempt.
**INCONCLUSIVE:** source/approval/protocol identity, oracle independence, candidate isolation or freeze chronology cannot be trusted.

If more than one failure applies, prioritize **FAIL_UNSAFE_TRANSPOSITION**, then **INCONCLUSIVE**, then BLOCKED, then FAIL_NO_TRANSPOSITION, then PARTIAL; do not award PASS via scorer loopholes.

This PASS would retire **only R6 for one controlled native field-threshold amendment**. It does not demonstrate general language-to-code automation, authentic authority, production deployment, two-way continuous monitoring, full persistent audit or real demand.

## 6. Implementation guardrails

- Scope one amendment, P1 metric and P2 control. Keep pre-frozen v1/v2 models simple JSON/Pydantic; no proprietary DSL, parser/compiler framework, agent fleet, event sourcing, automatic PR merges or deployment orchestration.
- The E4 comparator needs a **versioned reference/approval adapter** because `E4/src/checker.py` hardcodes P1≥100 and the E3 v1 record. Reuse its real native candidate execution and row-comparison **algorithms** without modifying E4. Do not silently replace its frozen reference or label the old E4 scorer an independent v2 authority.
- Do not overclaim independent oracle authorship: same researcher knows the fixtures. Maintain mechanical independence between output producer and reference evaluator, frozen-before-scoring truth, mutation controls and distinct execution.
- E4's `M6B` and `M2` are lab-introduced native metrics. Build the baseline from them and label it correctly, not as an actual preexisting enterprise contract workflow.
- Avoid double-counting as-of/effective dates: version selection chooses which policy governs a *given order date/period under a given knowledge-time*; queries of a new metric across all past dates cannot automatically establish historical correctness.
- Do not use an LLM to invent approval, infer legal meaning or silently substitute another semantic platform if MetricFlow refuses the change. Declare absent capability and STOP/NARROW when necessary.
- Rerun/collect native compiled SQL, semantic manifest and source hashes from the actual generated checkout. A changed YAML hash alone is neither proof of success nor noncompliance.
- No production writes, no future-phase E6–E8 and no broad integration G1. Once E5 passes, only **recommend** E6 and eventual end-to-end governed-transition test.

## 7. Deliverables and stop

Create **only** `experiments/E5_forward_transposition/`:
- `PRIOR.md`, frozen `PROTOCOL.md`, v1/v2 LAB policy/approval docs, `REFERENCE.json`, `SCENARIOS.json`, `TRANSPOSE_PACKET.json`, freeze manifest and hashes; note baseline provenance from E4 M6B/M2.
- `src/`: minimal transposer consuming the packet; versioned authority/temporal check; targeted E4 reference adapter; independent scoring/replay; no general code generator.
- `tests/`: controlled amendment, authority refusal, wrong threshold, collateral P2 mutation, no-deployment, and historical no-future-leak controls.
- `evidence/`: freeze and first-pass logs, generated native patch and exact transposer invocation, real candidate YAML diffs, compiled SQL and `mf` receipts, native-vs-independent line-level evidence, false-positive/false-negative controls, P2 before/after, history/as-of reconstruction, independent replay, cost and trust limits.
- `RESULTS.md`, `DECISION.md`, `README.md` including actual commands run; Windows PowerShell marked UNTESTED unless executed.

Create freeze commit and push it **before scored proposal**. Commit final results afterward, push and open draft stacked PR targeting E4 branch (unless it merged, then actual topology). No automatic merge.

Final owner report must give: PR URL, branch/base, freeze and final SHAs; v1/v2 approval provenance and time windows; exact native edit Sophon GENERATED from v2 IR; actual before/after P1 native & independent outputs; specific >=100 vs >=120 boundary counterexamples; P2 unaffected evidence; before/after known-at behavior; E4 reuse/adapter disclosure; costs; exactly one verdict; one next experiment with kill condition.

**STOP AFTER E5. The result of interest is one correctly controlled, independently checked governed semantic proposal, not more architecture.**
