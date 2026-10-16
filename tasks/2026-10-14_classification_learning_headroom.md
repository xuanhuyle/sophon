# Sophon — next SINGLE increment: discriminating classification-learning test preflight

**Date:** 2026-10-14
**Source of truth:** `main` at `f1d7688` (PR #21 merged); this task branch starts there.
**Instruction to Claude Code:** independently challenge the engineering lead's recorded preflight in `RESEARCH_PREFLIGHT.md` before any code. Prefer a short no-code finding if the existing source evidence settles the question. **Do not move to a subsequent experiment automatically.**

> **ENGINEERING LEAD PREFLIGHT NOW COMPLETED:** Read `RESEARCH_PREFLIGHT.md` at PR #22 HEAD before doing anything. Its scoped verdict is `BLOCKED_BY_NO_CLASSIFICATION_ORACLE_AND_HEADROOM` for a credible real-world accuracy claim on existing V1/V2 data. Do **not** reproduce that report as though it did not exist. Claude Code must *independently challenge* it against actual source/code and may produce a small, justified offline verification or a concise defect report, then STOP.
>
> **OWNER CONSTRAINT:** Sophon is **NOT trying to beat stronger LLMs**. We are testing whether a **fixed inexpensive model** develops narrow, auditable contractual expertise through accumulated source-linked library knowledge. The primary causal comparison is **the same frozen model and configuration** under COLD/FROZEN vs GROWING source-grounded library (optional RAW-PRECEDENT); stronger-model races are excluded from acceptance criteria.



## Independent engineering verdict — review BEFORE following this task

**Decision: NO-GO for the proposed Jev + adversarial + backward + third library-reviewer architecture as a claim of reliable, expert-free legal classification. CONDITIONAL GO for ONE small evaluation of whether source-grounded memory helps a simpler source-citing normative-function classifier.** The owner owns the objective, NOT the model composition; the task below is subject to this engineering conclusion.

**Reasons rooted in actual implementation/results:**
1. **Wrong unit of classification:** V1 forces one dominant type (OBLIGATION / PROHIBITION / PERMISSION_RIGHT / DEFINITION / AUTHORITY / OTHER) plus five modifiers. A single provision can express multiple duties, rights, exceptions and definitions. Forcing one label can be structurally wrong even when Jev returns high confidence. Before another run, separate per-span normative functions from a coarse provision-level summary and permit unresolved references/abstention. Do this by *evaluating outputs*, not building a new universal legal ontology.
2. **Wrong causal assumption:** adverse/backward prompts to similar LLMs, with a shared Jev proposal, are NOT independent semantic validators. Adding a third library-using LLM risks three correlated votes plus template anchoring. Show a distinct additional detected error before paying for another reviewer.
3. **No autonomous correctness signal:** source snippets, model agreement and self-inducted templates can all be consistently wrong. Updating memory from the model's own predictions without an external truth or falsifying signal can *increase* future error. `PROVISIONAL` and source citation are not correctness certifications. Test negative/contradictory precedents, reject/self-correction behavior and library rollback; do not assert autonomous error reduction by counting stored examples.
4. **V2 did not measure what we claim:** its score was 35/36 cold, 34/36 warm, 36/36 raw on **slot/fact retrieval**, not normative-function classification; 12/12 had HOLD dispositions and a scorer failed to count real omitted-condition findings. The V2 warm/cold template menus also differed. There is no observed evidence that the library reduces true intrinsic classification errors.
5. **Classification does not determine executable behavior by itself:** the same obligation label can mean deterministic formula, external event, subjective judgment, or unobservable data. The category is at most a first descriptor; later code-wise executability requires parties, object/action, preconditions, time, exceptions, references, observability and authority. Do NOT implement downstream executable routing now.

**Required competent baseline:** **same fixed inexpensive model**, same decoding, same prompts/allowed evidence, and the same output normative-function inventory for FROZEN vs CUMULATIVE; optionally compare RAW-EXAMPLE memory to distinguish structure learning from simply retrieving precedent. A one-call source-quoting baseline using the **same model** is a cost/complexity control, NOT a competition with bigger/stronger LLMs. No Jev monopoly; no automatic 2–3 reviewer agents. Only retain extra checks that catch incremental errors per unit cost. Prefer standard evidence/contradiction checking over a bespoke model or DSL.

**Independent measurement constraint:** the *best* available public legal benchmarks are not drop-in truth for our six normative-function labels. CUAD's expert labels describe topical clause types, and ContractNLI provides document-level entailment/contradiction/not-mentioned labels with supporting spans; they can provide existing source-rich examples or test subclaims but cannot be relabeled as our function-classification oracle. Metamorphic clause pairs (e.g. may↔must not, added exclusion) can test targeted invariance/changes but cannot certify real-world legal correctness. Without **any** independently validated semantic target (public expert labels when aligned, constrained verified examples, or a bounded one-time external review), claims about absolute accuracy or autonomous improvement are **BLOCKED**, not promising.

**My recommended next incremental decision:** run the **OFFLINE HEADROOM/ORACLE preflight only** using existing V1/V2 authentic clauses and recorded outputs. Produce either (a) a small frozen, genuinely discriminating classification-error test with credible independent checking and a controlled same-fixed-inexpensive-model baseline, or (b) `BLOCKED_BY_NO_CLASSIFICATION_ORACLE` and identify the smallest missing evidence. Do NOT build a third reviewer, issue provider calls, or assume a cumulative library has already been validated. If the smallest retrieval baseline suffices, **STOP architecture expansion**.

**Not a novelty claim:** these are engineering inferences based on inspected Sophon code/results and established legal NLP tasks (CUAD, ContractNLI), not a completed new experiment.

---

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

You may write ONE small offline fixture/checker for source hashes, controlled transformations, leakage/headroom diagnostics, and frozen protocol reproducibility if it resolves a specific preflight uncertainty; otherwise report the no-code result. Do not use a provider just to compare stronger LLMs. Avoid new architecture, a taxonomy DSL, new review agents, extensive synthetic corpora, or large harness frameworks. The source corpus is small and the authenticity/scope limits must be explicit.

## Mandatory mechanics

- Read `SOPHON_CHARTER.md`, `PROJECT_STATE.json` (especially `research_contract`), `ENGINEERING_WORKFLOW.md`, and actual V1/V2 code/results BEFORE choosing a design.
- Work on this exact branch and existing PR; **do not branch from stacked PR #17, merge V3/V4 history, or silently modify frozen V1/V2 results**. Read old implementation through its Git ref; if truly necessary, copy only selected files with provenance instead of merging the branch.
- If you create a new experiment directory under `prototype/`, `experiments/`, or `viability/`, include `EXPERIMENT_ALIGNMENT.json` per the now-merged context guard. At this stage use relation `COMPONENT_ONLY`, `stage: PLANNED`, `goal_id: PROVISION_NATURE_CUMULATIVE_LEARNING_V1`, `claim_limit: COMPONENT_ONLY_NOT_END_TO_END`; never claim end-to-end learning was tested.
- **NO external provider calls, API keys, paid usage, novel contracts fetched, or network dependency.** Reading existing Git history/PR content is fine. Do not alter `SOPHON_CHARTER.md`, the approved `research_contract`, or unrelated project architecture.
- Freeze only what can be defensibly frozen; describe observed vs inferred vs assumed. All test reports must clearly state that provider experiment and legal truth are NOT established.
- Run offline tests and CI. Push to this branch / current PR. Finish with **one engineering verdict, objective evidence, and one recommendation**, then STOP.

### Acceptance criterion

Independently verify/challenge the existing `RESEARCH_PREFLIGHT.md` already committed to this branch; if defective, update it with grounded corrections, with:
- a truthful V1/V2 reuse and provenance map;
- one explicit classification-error/headroom evaluation proposal, or a specific BLOCKED verdict;
- how source-grounded library content *would affect later classification* and how the comparison can detect errors in either direction;
- exact reasons why the evidence is sufficient or insufficient to justify a limited later provider pilot;
- no experimental performance claims without a real run.

**This task is a discriminating preflight, not an authorization for another experiment.** Do not proceed to a live Jev/reviewer run without explicit owner approval.
