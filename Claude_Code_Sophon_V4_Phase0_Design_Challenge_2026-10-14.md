# Sophon V4 — Correct the discriminating test before execution

**Repository:** `xuanhuyle/sophon`  
**Starting branch:** `experiment/jev-v4-sequential-provision-learning-2026-10-13` (PR #18)  
**Expected starting HEAD:** `6d45d371167d2cdb9f0ba3c8780367624d878688`  
**Target:** continue PR #18 only; do not merge, rebase or open a new PR.  
**Task:** one bounded **read-only-in-evaluation** design challenge and decision. No V4 scoring, no provider calls, no new architecture.

## Grounding

Read the current `SOPHON_CHARTER.md`, `PROJECT_STATE.json`, and `ENGINEERING_WORKFLOW.md` from **`origin/main`**, not older text on this unmerged experimental branch. Consult actual PR #17 V1–V3 code and frozen results, original V4 specification on PR #18, and **`prototype/contract_sequential_learning_v4/PHASE0_DECISION.md` at `6d45d37`**. Preserve all historical first-run evidence.

Owner's motivating scenario: an AI-native solo founder processes successive contracts and amendments. The immediate technical question is **whether Sophon acquires, retains, revises and reuses source-grounded contractual knowledge so that prior contractual experience improves later assessments**. The underlying LLM, if any, is a replaceable component, **not a competitor**; no LLM leaderboard, no commercial validation, no amendment-only ledger pivot.

## Critical flaw to resolve

Phase 0 proposes predicting two ContractNLI exception labels (nda-12, nda-13) **from the released ground-truth labels of other hypotheses in the same current agreement**. Its learner is similarity-weighted conditional counts. That is a valid *statistical-label-correlation* task, but not yet evidence of contractual semantic knowledge acquisition or of an actual Sophon process obtaining source-grounded context. Even a statistically significant improvement on 180 documents could merely show co-occurrence of editorial annotations with no contractual understanding or actionable review improvement.

Do NOT claim this Phase-0 test is invalid purely because it lacks an LLM. Do NOT introduce an LLM-versus-Sophon comparator. Determine the **minimal change in observable inputs and outputs** that makes a possible positive result worth learning about—while retaining independent ContractNLI reference annotations and avoiding a full system build.

## Your single bounded investigation

1. **Audit task construct validity.** State exactly what the current five-arm design would demonstrate if it wins, and what it cannot demonstrate. Pay attention to gold-label current-contract context, the two highly standardized target carve-outs, inability to represent source-supported exceptions/dependencies beyond the 3-class answer, unequal applicability to a deployed review workflow, and whether any improvement comes solely from base rates, near-duplicate templates or issuer patterns.
2. **Test a source-grounded alternative ON DEV DOCUMENTS ONLY.** Inspect the already-designated 36 DEV NDAs, including the independent evidence-span annotations. Without using or computing any SEQUENCE labels, check whether a current agreement can provide a plausible *observable* context (e.g. reviewed passages and their source-linked provisional interpretations rather than omniscient gold labels), and whether a library from earlier contracts can encode a reusable, evidence-cited structure or counterexample that informs an exception/condition/dependency review hypothesis. Clarify the status of using third-party gold labels after each reveal as a *simulation* of a reviewer; there is no independently validated automatic interpreter in V4.
3. **Decide whether a repaired experiment can genuinely discriminate.** At minimum: compare frozen experience with accumulating experience, under identical current observable inputs, plus a simple accumulating knowledge control; keep the same underlying components and evaluate on independent annotations. The comparison is **learning mechanism versus ablated learning mechanism**, not an LLM leaderboard. Check negative controls, abstention/novelty and evidence-linked library revision. A model-free statistical prior may be useful, but call it that; don't relabel it “semantic learning.”
4. **Find actual limitations before proceeding.** Confirm evidence spans and context masking can avoid leaking target text, and that the legal-reference task is source-supported rather than just a label shortcut. Check chronological split and dataset/license/provenance assertions. Note that Phase 0's scratch screening scripts were not committed; any future freeze must include reproducible corpus-screen logic and hashes, not merely aggregate numbers. Question the arbitrary `INVALID` rule where shuffled context beating a marginal baseline automatically invalidates the experiment: a successful negative control often means a hypothesis failed, not that the data are invalid.
5. **Recommend exactly one of two decisions:**
   - `ONE_REVISED_MINIMAL_TEST`: one precisely specified, realistically observable task with accessible independent oracle, a strong simple accumulating control, a testable learning effect and an honest scope of inference; OR
   - `NO_BUILD_FOR_THIS_PROXY`: if no source-grounded and potentially informative task is attainable with the available dataset, retain Phase 0 as a screened but insufficient label-correlation proxy and do not authorize its runner.

Do not compensate for missing semantic observability with new infrastructure, extra agents, synthetic contracts, agent-authored scoring labels or broader contract families. No paid models, no new model training, no V4 scoring, no heldout labels or hidden source passages read, no PR merges, and no changes to `main`.

## Deliverable

Append a clearly dated **`PHASE0_DESIGN_REVIEW.md`** alongside `PHASE0_DECISION.md` in `prototype/contract_sequential_learning_v4/` on the **existing PR #18 branch**. Keep the original Phase 0 report unchanged. One page preferred; name verified observations versus assumptions, task inputs visible to the learner, prediction outputs, source-backed library updates, honest controls, concrete failure criteria, reproducibility blockers, and one next action. Commit/push and STOP. A statistically significant label-prediction gain must **never** be called proof of Sophon's broader semantic-learning capability.
