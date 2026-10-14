# Sophon V4 — Phase 0: credible cumulative contractual-learning test

**Repository:** `xuanhuyle/sophon`  
**Starting branch:** `experiment/jev-v4-sequential-provision-learning-2026-10-13` (draft PR #18)  
**Expected starting head:** `5b75e643c3d4459663f1aed518fffd2388c66f5b`  
**Target branch:** none; continue PR #18, do not merge into `main`  
**Scope:** one bounded **no-provider-call** feasibility and experiment-design increment. Do not run a scored V4 experiment yet.

## 0. Authority and existing work (mandatory)

Fetch current GitHub refs before work. **Use the current `origin/main`** as authoritative for `SOPHON_CHARTER.md` v1.2, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md`, `CLAUDE.md` and `AGENTS.md`. Do not rely on the older versions on PR #18. Current `main` was `77c8ba1` when this prompt was written; resolve a newer head if present. PR #18 branched from PR #17 **before** its adjudication commit; read current PR #17 head `b9d698c` and its actual implementation/experiment evidence separately (isolated worktree is fine). Read the original V4 specification on this branch but **challenge it**, don't blindly implement it.

Relevant existing evidence: V1 provider pilot/reviewers and its disputed/originally blocked chronology; V2 `NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE_ON_V2_PROXY` with near-ceiling scores; V3 frozen primary `INCONCLUSIVE`, secondary unadjudicated structural signal; PR #3 Publicodes `STOP_KERNEL` for one persistence differentiator; E0–E5 limited lab feasibility. Do not substitute any of these for a cumulative-learning result. Keep frozen sources, results and decisions intact.

## 1. The owner's actual research question — NOT an LLM competition

**Can Sophon accumulate, revise and reuse source-grounded *contractual knowledge* from successive agreements so that its future assessment of an unseen agreement improves?**

The motivating environment is an AI-native solo founder receiving successive contracts and amendments. The aim is a durable normative semantic layer—not a better pretrained LLM, buyer-demand discovery, an AI compliance chatbot, or merely a versioned amendment ledger.

Learning may concern (i) provision functions and expected semantic structure *within* a section/provision, (ii) conditions, exceptions, definitions, cross-references and dependencies across a contract, (iii) scope, evidence, uncertainty and counterexamples. Predictions are provisional review hypotheses, never claimed applicable governing obligations without source evidence and appropriate approval.

Do **not** make “Sophon beats Claude/GPT/Jev” a goal, mandatory baseline, or kill criterion. A fixed LLM may be used as an **unchanged internal component**, not the adversary. Distinguish:
- **Experience gain:** the same learner with accumulating prior evidence versus its library frozen after the seed agreements; same current-contract information, task, model/settings and scoring.
- **Mechanism value:** if feasible, compare the structured evolving knowledge against a *simple updating representation of the same previous experiences* (e.g., conditional counts or raw precedents) to test whether our extra mechanisms matter. This is an ablation of knowledge accumulation, **not** an LLM leaderboard.
- **State maintenance:** fidelity across amendments and effective dates is important but *not* a substitute for cross-contract learning. Do not quietly pivot to an amendment-chain ledger test.

## 2. The single task now: feasibility gate, then a design recommendation

Do not re-open a general architecture/product debate. Use existing V2/V3/V4 code and prior-art notes to investigate the following **before writing new implementation**:

1. **Precise observable task.** Identify ONE genuinely useful pre-observation or early-review prediction/assessment on an unfamiliar contract that prior-contract experience could improve. A common heading appearing in a section is insufficient by itself. Prefer a verifiable within-provision condition/exception/dependency or omission-check target if an independent reference actually supports it. If none is measurable, state that and do not invent a surrogate victory.
2. **Independent evidence feasibility.** Screen a small bounded set of existing authentic agreement sources and/or genuinely independent annotation datasets. First assess the current V3 sources and the possible independently labeled alternatives already listed in V3 prior art; extend the search only if necessary. Preserve exact source URLs/accessions, document identities, version dates, hashes where files are actually obtained, rights/availability, and what each oracle actually establishes. **An agent-produced label, LLM consensus, a heading-as-label shortcut, or source text alone are not independently validated semantic ground truth.** Mechanical source-text oracles may support strictly textual claims, but not legal interpretation claims.
3. **Test geometry.** Show there are enough *distinct independent* agreements and target cases, measurable headroom, and a credible chronological source split. Address template/issuer duplicates, contamination from V2/V3 and source familiarity, cross-contract leakage, how the target will be masked, and how source-anchored library updates occur only **after** each sealed prediction. Do not peek at held-out labels while designing the test. No need to attain a particular count if corpus screening proves infeasibility; report what was actually found.
4. **Competing explanations.** Explain how the proposed test would distinguish real accumulating evidence from (a) growing example counts, (b) copying old clauses, (c) memorized contract conventions, (d) target leakage, (e) relabeling/metric artifacts, or (f) simply exposing more context. Specify one hard negative and one genuinely novel/out-of-pattern case. Include library revision/counterexample handling and whether a prior mistaken inference can persist.
5. **Reuse and cost.** Locate specific reusable V2/V3 components, and only the smallest necessary new harness or schema (if any). Say when even that is premature. Estimate corpus and adjudication burden and any future provider-call budget; **make zero paid calls now**.

If sourcing is blocked by cloud networking, inspect accessible local evidence and identify the blocker precisely. Do not silently replace authentic inputs with self-authored agreements or fake independent annotations.

## 3. Deliverable and decision — bounded

Commit ONE short, concrete Phase-0 report **on this same PR #18 branch**, e.g. `prototype/contract_sequential_learning_v4/PHASE0_DECISION.md`. It must include:

- `REUSE_EXISTING / ONE_MINIMAL_TEST / BLOCKED_EVIDENCE / NO_BUILD` and your *independent* engineering rationale.
- ONE measured capability target, source family and independently available oracle (or explicit proof of lack of one), with at least one source citation/immutable identifier.
- What will be blinded, what will be learned after reveal, and how the library is updated/verified contract by contract.
- Frozen-library vs cumulative-library controls (same model/component), plus an updating-simple-knowledge control **only if it can be tested fairly**.
- Explicit success, failure, invalid/blocked criteria **that can genuinely fail**; avoid arbitrary gates or a near-ceiling task. Any later positive result must be assessed by agreement and remain scoped, not sold as general legal reasoning.
- Specific reuse paths/refs, minimal additional engineering, expected human-review and provider costs, risks, and a **single recommended next action**.

If a credible independent semantic oracle does not exist in a cheaply reachable source, **recommend NO_BUILD/BLOCKED** and name precisely what evidence would unblock it. A failed source search is not proof that Sophon's whole thesis is false.

**Constraints:** no new product architecture; no LLM comparison leaderboard; no cross-contract learning replaced by an amendment-only state test; no BI runtime work, full agent configuration, commercial interviews, model training, paid calls, or bulk manual annotation. Do not change `main`, merge/rebase the historical PR stack, change frozen results, modify `PROJECT_STATE.json` on `main`, or launch the subsequent experiment without a new decision. Do not open a separate PR by default. If even this Phase 0 duplicates available reliable evidence, challenge it and issue a shorter decision.

After pushing the Phase-0 report, provide its commit SHA and GitHub link, the exact sources actually checked, observed limitations, and **STOP**. Do not continue automatically to V4 implementation.
