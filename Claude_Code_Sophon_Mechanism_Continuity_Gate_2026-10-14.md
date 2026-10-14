# Sophon PR #21 — smallest honest research-continuity safeguard

**Repository:** `xuanhuyle/sophon`  
**Starting branch:** `guard/jev-lineage-continuity-2026-10-14` (existing draft PR #21)  
**Expected HEAD:** resolve current head after `5954549`; do not create another PR or merge.  
**Goal:** prevent another *false claim of experimental continuity*, without making the owner's architectural ideas mandatory.

## Engineering correction and scope

**Updated owner priority (2026-10-14):** the immediate outcome is reliable, **automatic categorization of each provision's intrinsic normative nature**, because that categorization will later inform how to approach its code-wise executability. The integrated research objective is **CLASSIFICATION WITH CUMULATIVE LEARNING**: repeatedly update a provisional source-grounded provision-skeleton library from genuine contract evidence and counterexamples, so later classifications become less error-prone and a narrow contract-family expertise accumulates. Automatic adversarial/backward/library checks are proposed quality controls. Do not replace this objective with standalone heading/regex/next-provision prediction. **Code executability** remains downstream and out of scope. This particular PR #21 changes only the context/evidence safeguard; it does NOT run that research experiment. Start from V1's normative primaries `OBLIGATION, PROHIBITION, PERMISSION_RIGHT, DEFINITION, AUTHORITY, OTHER` and modifiers `THRESHOLD, EXCLUSION, CONDITION, DEADLINE, CROSS_REFERENCE`; assess whether compound norms defeat a forced single primary. The owner **proposed** Jev classification + adversarial + backward + library-based challenge; treat reviewer topology as an engineering HYPOTHESIS, not a mandate. No expert reviewer is intended in the per-clause pipeline, but agreement among LLMs does NOT establish independent semantic truth.

**Real prior code/results:** V1 Jev and two LLM reviewers; V2 source-backed templates (induced partly by lab-authored detectors) and shared library context, **no separate library-based reviewer**, near-ceiling inconclusive transfer value. V3 heading priors; V4 regex-based text feature prediction, 0 Jev/reviewer calls, frozen STOP specific to V4 textual proxy. Actual code on PR #17 and V4 results on PR #18. Main has governance and a context hook but not the experimental code. Read current charter/workflow/state on main, branch `PROJECT_STATE.json`, prior PR refs, and the existing `.claude/hooks/context_guard.py` and tests.

**An earlier implementation on this draft PR was REJECTED and reverted.** It more than doubled the guard, generated a many-field MECHANISM.json per experiment, fingerprint-pinned the *entire* owner-proposed reviewer topology, forced a third reviewer as the next step, and attempted untrustworthy AST call reachability as proof of actual execution. GitHub CI correctly failed when that architecture was revised. **Do not resurrect that design**, fix its fingerprint, or add another elaborate framework.

## ONE minimal change, subject to engineering judgment

Recommend the smallest code-supported **claim/evidence scope check**, added to the EXISTING guard and its regression tests. It should be about *what an experiment claims versus what evidence it actually recorded*, not prescribing Jev, the number of agents, the next architectural delta, or the research method.

A valid new experiment or substantial result should state succinctly:
- owner research question and why this task is relevant to classification AND the library's causal contribution to reducing future classification errors;
- actual implementation parent ref and the ONE deliberate method change;
- which mechanisms were **actually executed**, which are only planned or absent;
- what the output can/cannot prove (e.g., regex proxy, source-anchored clause extraction, Jev+reviewer run, independent semantic correctness).

Use the simplest durable representation you can justify. **Only enforce on newly added/revised experiment work**, not historical directories and not minor fixes/docs. If an experiment claims a real Jev/reviewer execution but has no corresponding first-run trace/receipt, CI must NOT treat it as VERIFIED. If actual call count is zero, a claim of performed Jev+reviewer learning is false. A justified alternative implementation is legitimate and must not require owner sign-off for routine technical method choices; a material change in the *research goal* does.

Do not claim static checks prove provider authenticity, semantic validity or true architecture execution. If they can't verify a claim, make its status explicitly `UNVERIFIED` and require human review instead of an invented passing proof. Prefer a small attestation/trace check over parsing call graphs. Reuse the existing `check_pr_state_update` and CI. No new dependencies.

**Acceptance tests, offline only:**
1. A V4-shaped experiment scoring heading/regex predictions with `0` Jev calls that claims to validate **intrinsic normative classification via Jev and its reviewers** must be rejected or demonstrably downgraded to UNVERIFIED.
2. The same V4 evidence labeled as a `SEPARATE_MECHANISM` on regex/textual proxies is permitted as history but not presented as evidence for the **current classification reliability** objective.
3. A planned V1/V2-based test of library-augmented classification versus same-pipeline cold/frozen/raw controls is allowed as `PLANNED` without falsely claiming provider execution, contract-by-contract improvement or expert-verified legal semantics.
4. Existing guard and tests pass.
5. A short engineer-written review statement says what cannot be mechanically prevented and what requires inspection of code/results.

**Critical cost/simplicity boundary:** aim for a modest change measured in **tens of production lines**, not a new 250-line experiment verification engine. If claim/evidence enforcement cannot be made credible with a small change, explicitly recommend no new automation and improve the existing PR-review discipline instead; **do not fake a comprehensive safeguard**.

No provider calls, no experiments, no new architecture, no new PR, no changes to historical frozen V1–V4 outputs or to main. Update PR #21, demonstrate the negative regression, report commit SHA and current GitHub CI, then STOP. Main currently lacks branch protection, so CI is not automatically a required merge check.

**Important for subsequent engineering (not this task):** classification and source-backed **library learning across successive real agreements** form ONE research hypothesis: can accumulated, scoped provision skeletons and counterexamples prevent later intrinsic-nature classification errors, compared with the SAME Jev/reviewer pipeline without learning or with raw examples? Measure corrected/missed false class assignments, abstentions and new errors, not just library size, frequency counts or reviewer agreement. Choose ONE bounded, difficult but verifiable increment using V1/V2, and challenge whether a third LLM reviewer adds value beyond simpler source-backed library comparison. Classification can LATER inform executability; do not implement executable contract logic now. No expert in the routine classification loop is desired; without an independent semantic oracle, do not claim guaranteed correctness.
