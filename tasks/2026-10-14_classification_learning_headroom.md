# Sophon — next SINGLE increment: discriminating classification-learning test preflight

**Date:** 2026-10-14
**Source of truth:** `main` at `f1d7688` (PR #21 merged); this task branch starts there.
**Instruction to Claude Code:** independently challenge this task's assumptions. Prefer a smaller no-code answer if existing evidence settles feasibility. **Do not move to a next experiment automatically.**

## Owner-established research objective (DO NOT REINTERPRET)

Determine automatically the *intrinsic normative nature of each contractual provision*, with source-grounded, complementary machine checks and defensible abstention. A persistent **versioned provision-skeleton library must learn from successive contracts/counterexamples and reduce future classification errors**, developing narrow contract-family expertise. This is ONE coupled goal.

Proposed Jev + adversarial + backward + library-check architecture is a **candidate**, not a mandate to build three extra LLM agents. Downstream executability/contract-to-code is the purpose of classification, NOT the current task. No next-clause/heading/regex-feature prediction.

## Why this is the next increment, based on actual repository evidence

- Start from **V1/V2**, not V3/V4: on `experiment/jev-v3-context-funnel-2026-10-13` / PR #17 head `b9d698c`, read:
  - `prototype/jev_clause_router_v0/prototype.py`, `external_github_sla_2021.json`, `review_matrix.json`, `live_runs/live_EXT_20261013T094923Z.json`, `live_runs/compare_20261013T094923Z.md`;
  - `prototype/jev_library_transfer_v2/transfer.py`, `library_v0.json`, `library_v1.json`, `library_events.json`, `google_storage_sla_20210624.json`, `reference_checklist_b.json`, `V2_POSTRUN_REVIEW.md`.
- V1 performed genuine Jev + adversarial/backward provider calls, but its primary-label reference is agent-authored; apparently 5/5 against that proxy with very little observable error headroom.
- V2 transferred source-linked provisional skeletons from a GitHub SLA to a Google Storage SLA (three B packets). The **scored output was slot/fact recall, NOT correctness of intrinsic normative-function categories**. Cold scored 35/36, learned library 34/36, raw examples 36/36. Review of actual outputs found scoring/field-placement artifacts (material facts in `omitted_conditions`), and all 12 pipeline conditions remained `HOLD_UNRESOLVED`. This is a near-ceiling proxy, not a negative finding about classification learning.
- V2 has a **moving detailed-template vocabulary** between cold and warm arms. Carefully distinguish a changed template menu from changed intrinsic-normative classification. Use a **fixed outcome taxonomy** for comparisons (initially V1 `OBLIGATION / PROHIBITION / PERMISSION_RIGHT / DEFINITION / AUTHORITY / OTHER` plus modifiers, allowing source-supported compound functions and abstention). Do not treat a different template name as a classification correction without mapping to a stable normative outcome.
- V2 raw Google live recordings were deliberately gitignored; only receipts were committed. If they are not available in your current environment, say **UNAVAILABLE** and do not pretend to replay them.
- V3/V4 changed research target (structural/regex proxies; V4 provider calls = 0). Their outcomes do NOT answer this task.

## ONE unknown to resolve now — before any new paid experiment

**Can the existing authentic, source-linked V1/V2 material support a small, discriminating, independently checkable test of whether accumulating provision skeletons improves intrinsic normative-function classification, or do we need a different held-out corpus?**

The test MUST have classification-error headroom. A benchmark on which a cold classifier already earns almost every point is not informative. A reviewer's agreement with Jev, a matching quote, or an agent-authored interpretation does not independently establish legal truth.

## Required work — OFFLINE preflight only

1. **Inspect real artifacts**, not summaries alone. Inventory the exact classifier output, the role and source of each skeleton, actual vs replayed model calls, independence of the existing oracles, and the source of the V2 score pathology.
2. **Select the smallest meaningful evaluation unit**: provision/source text + necessary referenced context, fixed intrinsic-function target (possibly multiple simultaneous functions), significant modifiers, explicit unsupported/ambiguous cases, and a library-version history. Restrict the initial domain to the same SLA family already represented by V1/V2; do not switch silently to SEC credit agreements.
3. **Try to construct a frozen test with genuine headroom** from the existing authentic excerpts and, only where appropriate, narrowly controlled semantic counterfactuals (e.g., supported permission vs prohibition, moved exception, cross-reference needed). Every alteration must have an explicit provenance and a justified *expected relation between two classifications*. Counterfactual oracles test only that relation, NOT comprehensive legal correctness. Include at least one hard valid-but-atypical provision to test harmful template transfer.
4. **Design ONE constant-proposal comparison** so that the only causal change is what the provisional library knows: no-library or frozen-library vs prior source-backed skeletons (and raw prior examples if useful). Control for different label inventories, different reviewer prompts, leakage of target material into the library, and chronology. Demonstrate what will count as an error avoided, a new error introduced, or justified abstention. **Preserve the option of using V1/V2 code, do not reinvent it.**
5. Decide whether the test is **READY_FOR_A_LATER_SMALL_LIVE_PILOT** or **BLOCKED_BY_ORACLE_OR_HEADROOM**. If READY, freeze sources, examples, target relations, library versions, baseline, success/failure/inconclusive interpretation, next-call budget and any constraints on provenance. If BLOCKED, identify the exact missing information and recommend ONE low-cost remedy, such as a third genuinely held-out source with nontrivial category ambiguity. Do not invent labels to force READY.

You may write ONE small offline fixture/checker for source hashes, controlled transformations, leakage/headroom diagnostics, and frozen protocol reproducibility if justified; otherwise report the no-code result. Avoid new architecture, a taxonomy DSL, new review agents, extensive synthetic corpora, or large harness frameworks. The source corpus is small and the authenticity/scope limits must be explicit.

## Mandatory mechanics

- Read `SOPHON_CHARTER.md`, `PROJECT_STATE.json` (especially `research_contract`), `ENGINEERING_WORKFLOW.md`, and actual V1/V2 code/results BEFORE choosing a design.
- Work on this exact branch and existing PR; **do not branch from stacked PR #17, merge V3/V4 history, or silently modify frozen V1/V2 results**. Read old implementation through its Git ref; if truly necessary, copy only selected files with provenance instead of merging the branch.
- If you create a new experiment directory under `prototype/`, `experiments/`, or `viability/`, include `EXPERIMENT_ALIGNMENT.json` per the now-merged context guard. At this stage use relation `COMPONENT_ONLY`, `stage: PLANNED`, `goal_id: PROVISION_NATURE_CUMULATIVE_LEARNING_V1`, `claim_limit: COMPONENT_ONLY_NOT_END_TO_END`; never claim end-to-end learning was tested.
- **NO external provider calls, API keys, paid usage, novel contracts fetched, or network dependency.** Reading existing Git history/PR content is fine. Do not alter `SOPHON_CHARTER.md`, the approved `research_contract`, or unrelated project architecture.
- Freeze only what can be defensibly frozen; describe observed vs inferred vs assumed. All test reports must clearly state that provider experiment and legal truth are NOT established.
- Run offline tests and CI. Push to this branch / current PR. Finish with **one engineering verdict, objective evidence, and one recommendation**, then STOP.

### Acceptance criterion

Produce a reviewable `RESEARCH_PREFLIGHT.md` on this branch with:
- a truthful V1/V2 reuse and provenance map;
- one explicit classification-error/headroom evaluation proposal, or a specific BLOCKED verdict;
- how source-grounded library content *would affect later classification* and how the comparison can detect errors in either direction;
- exact reasons why the evidence is sufficient or insufficient to justify a limited later provider pilot;
- no experimental performance claims without a real run.

**This task is a discriminating preflight, not an authorization for another experiment.** Do not proceed to a live Jev/reviewer run without explicit owner approval.
