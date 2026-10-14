# Sophon — engineering-accountability + experiment-continuity gate (ONE increment)

**Repository:** `xuanhuyle/sophon`  
**Starting branch:** `guard/jev-lineage-continuity-2026-10-14` (draft PR #21)  
**Expected starting head:** `d9de5f3` before this task-file update; fetch current HEAD first  
**Target:** update **existing PR #21** against main, do not create a new PR or merge.  
**Scope:** implement ONE light, executable check in the existing context guard and CI, with regression tests. No Jev/live contract experiment; zero paid calls.

## First principles (owner and engineer roles)

The owner fixes Sophon's **problem and outcome**: can a persistent, source-grounded, provisional library of contractual knowledge improve later real-contract analysis, and eventually supply a normative semantic layer? Owner's V1/V2 design—Jev classification → adversarial/backward challenge → proposed library-based check → source-anchored provision skeletons → reconciliation/retention—is an **architectural hypothesis**. It is NOT a requirement to build three AI reviewer agents, use Jev forever, or assume a single source document establishes a universal skeleton.

Engineering lead must independently test alternatives, identify redundant agents/components, compare against the smallest honest alternative, and choose an increment. Claude Code must challenge engineering specifications if they overbuild. Changing *methods* with a defensible reason is legitimate; silently changing the *research question* or claiming that a new proxy tested the old mechanism is not.

Verified real lineage:
- V1: Jev + separately called adversarial/backward LLM reviewers + reconciliation (actual provider recordings, 10 clauses; no independent semantic oracle).
- V2: source-linked templates and provisional skeleton induction from GitHub SLA, shared as context with Jev and BOTH reviewers for Google SLA; **no independent library-based third reviewer**. Library inducer uses LAB_AUTHORED detectors. V2 35/36 cold, 34/36 learned-library, 36/36 raw-example, near-ceiling proxy. A schema-scoping/scoring artifact excluded correct content in omitted_conditions. This is NOT a global conclusion.
- V3: offline heading/context statistical predictor, distinct method and unadjudicated results.
- V4: frozen authentic SEC EDGAR run on regex/heading textual proxies (mean Brier cumulative 0.2427 vs frozen 0.2147 vs counts 0.2036; 0 Jev/LLM reviewer calls). Valid STOP **for that predictor**, NOT evidence about the V1/V2 Jev architecture.

Read current `SOPHON_CHARTER.md`, `PROJECT_STATE.json` (including `active_research_mechanism` and its **candidate-not-mandate** status), `ENGINEERING_WORKFLOW.md`, existing `.claude/hooks/context_guard.py`, `.github/workflows/context-integrity.yml`, `tests/test_context_guard.py`, and real V1/V2 code/results on PR #17 and V4 evidence on PR #18. Main holds governance but not those experimental implementations.

## Failure mode to prevent

The current hook injects a *component inventory* but does not demand evidence that an experiment actually exercises the declared mechanism or assesses the same outcome. As a result, V3/V4 were repeatedly promoted as incremental Jev-learning work although they ran an entirely different, regex/statistical mechanism.

**Build a narrow enforceable gate that checks research/claim continuity, not architecture obedience.** Before accepting a substantively new/revised experimental runner, protocol or result, the PR must explicitly distinguish:
1. **Research objective** (invariant, unless owner authorizes a material pivot).
2. **Existing implementation and evidence ref** (including unmerged PR head).
3. **Single engineering-chosen change** and credible simpler alternative rejected.
4. **Planned vs actually exercised mechanisms** with exact code and run-receipt paths—source extraction, Jev classification, adversarial/backward calls, library query/skeleton comparison, reconciliation, etc. Distinguish NOT_IMPLEMENTED, MOCK, RECORDED, ACTUAL_PROVIDER and NOT_RUN.
5. **Allowed claim** and explicitly untested parts. No claim of "Jev-system learning validated" when the actual method is only heading/regex predictions.

Prefer expanding the current context-check and test machinery, with one tiny per-experiment declaration if necessary; do not create an agent framework, separate manifest registry or a documentation ceremony. Ensure historical V1–V4 files need not be retroactively relabeled. Minor bugfixes/docs must not be blocked.

**Important:** static scanners cannot prove an imported method was invoked, and author-written declarations are not execution evidence. If receipts/traces cannot confirm provider calls and independent verification, classify the claim **UNVERIFIED/PLUMBING_ONLY**, never as tested/verified. Do not implement a placebo green check that simply searches for words such as "Jev" or "adversarial" in a document.

## Required tests (offline)

- Missing/malformed/tampered owner-goal and lineage/claim boundaries are detected.
- Session/user-prompt hook tells the coding agent the V1/V2 real status and the three unproven assumptions: necessity of Jev, necessity of multiple reviewers, and autonomous skeleton learning.
- **NEGATIVE:** V4-shaped regex/count-only runner or protocol falsely claiming to have exercised Jev + adversarial/backward reviewer + evolving skeleton library fails.
- **POSITIVE:** same regex/count-only work is allowed to be recorded as a `SEPARATE_MECHANISM` with claims restricted to its proxy (assuming an explicitly distinct research question; cannot silently replace current goal).
- **POSITIVE:** a declared V2-derived single-delta library check can be planned without provider calls if labeled `PLANNED/PLUMBING_ONLY` rather than evaluated.
- **NEGATIVE:** results claiming live Jev/reviewer success without corresponding execution receipts are rejected or flagged as UNVERIFIED; do not silently pass as verified.
- Existing regression suite stays green; run a genuine fail-closed example and show the result.

## Deliverable / boundaries

Commit only the existing guard/CI and tests plus justified minimal state amendments on this PR. Preserve frozen historical V1–V4 results. No new research architecture, no experimental implementation, no model calls, no network dependency inside guard/tests, no PR merge. End with pass/fail observations, actual enforcement limits, SHA, and STOP.

`main` currently has no enforced branch protection. A green status check by itself is not an absolute merge gate; record this limitation. Claude Code does not control organization admin policy, and the historical PR stack predates the guard.

**Engineering discretion is explicit:** if the full test matrix cannot be honestly enforced without large, brittle machinery, choose the *smallest robust check* and document exactly what remains a human review responsibility. Do not pretend an unverified claim has been mechanically proved.

No subsequent experiment begins automatically. The next engineering decision should ask whether an ordinary source-backed skeleton-difference checker is more useful than adding a third LLM reviewer, using V2 artifacts; do not implement either in this task.
