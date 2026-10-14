# Sophon — One-increment repository housekeeping (14 October 2026)

**Task type:** bounded engineering maintenance, not a product experiment.
**Work on:** `infra/native-project-context-2026-10-13`, the existing open PR #19. Do not open another PR by default.
**Authority:** `SOPHON_CHARTER.md` v1.2, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md`, and observed code/results on the relevant PR heads.
**Approval:** owner has agreed to repository housekeeping. This does **not** authorize merging/closing PRs, altering frozen results, paid calls, deployment, charter changes, or a new research agenda.

## The problem to solve

A fresh coding agent currently sees a partial and biased engineering history. In PR #19, `PROJECT_STATE.json` indexes Jev/V1–V3 but largely omits the earlier native BI validation implementation, the direct normative-layer prototype, the public-data reviewer and the negative governance-integrity result. Much of the runnable research lives in **unmerged and sometimes stacked** PRs, not in `main`. A mechanically passing context hook can therefore faithfully repeat an incomplete picture of Sophon.

**Desired observable outcome:** after these maintenance changes, a new coding agent using the PR #19 branch can correctly distinguish the governing charter, the immediate research priority, existing implementation on other PR branches, verified experiment results and limits, and unexecuted ideas—without the owner narrating project history again.

The owner's **immediate research interest** is cumulative, source-grounded contractual learning across successive agreements; the solo-founder contracting scenario motivates it. Commercial interviews, re-running E0–E5 or automatically implementing contract-to-agent configuration are **not** the next task. E0–E5 are bounded technical feasibility evidence, not proof of generality or incremental value.

## Investigate first (you own the engineering decisions)

1. Inspect the *actual* current PR graph and relevant source/results, not only PR titles. Starting anchors: PR #2 public alignment/NYC experiment; PR #3 Publicodes `STOP_KERNEL`; PRs #4–#11 E0–E5 with the E1 erratum and E2's partial result; PR #12 limited two-client normative layer; PRs #13–#17 Jev/review/library/V3; PR #18 V4 **specification only**; PR #15 charter v1.2, already included in PR #19; PR #19 native context. PR #1 was merged historically. Verify every asserted status and path on the appropriate ref.
2. Compare that verified inventory to `PROJECT_STATE.json`, `README.md`, `CLAUDE.md`, `AGENTS.md`, and the existing `.claude/hooks/context_guard.py`. Look for facts missing from the context automatically given to an agent, outdated guidance, broken links, and status confusion. Do not mistake code on a draft PR for code on the checked-out branch.
3. Reconcile V1 chronology without rewriting history: the original `V1_LIVE_RESULTS.md` records a **blocked** provider run (0 actual calls *at that time*); later committed `live_runs` / V2 evidence records actual provider-output replays and a reported 40-call V1 pilot. Verify provenance, distinguish earlier readiness from later execution, and preserve unresolved evaluation questions.
4. Identify whether the existing native hook actually loads context in supported Claude Code sessions. A Python unit test/CI success is **not** proof of a fresh-session hook firing. If no supported end-to-end session is available, record NOT_VERIFIED and provide a tiny reproducible smoke test rather than claiming success.

## Make the smallest useful correction

- Update the **existing** `PROJECT_STATE.json` to give a *balanced*, evidence-qualified and ref-qualified view of historical work and currently reusable components. Do not introduce a second state file, new registry or product architecture. For any component, clearly say whether it is ON THIS BRANCH / ON OTHER PR, IMPLEMENTED / RUN / VERIFIED WITHIN SCOPE, and what it does **not** prove. Do not proliferate duplicate entries for every one-off test fixture.
- Align only the relevant entry surfaces, principally `README.md` and, if truly needed, the current Claude Code context-injection text. Keep the README's old investigations clearly historical rather than deleting or rewriting them. Keep the *current* research priority intact; do not promote the BI-first wedge into a mandate to abandon contractual-learning research.
- Amend the existing stdlib context guard and tests *only as necessary* to prevent the same omissions or mechanically invalid state. Avoid hard-coding historical research interpretations as immutable truths when new evidence might legitimately refine them. CI should catch structural defects, not pretend to judge semantic validity.
- Produce a concise, evidence-backed disposition for the PR graph: which PR content belongs in a durable development baseline, which remains immutable historical research, and which is merely a deferred hypothesis. Do not create a separate heavyweight PR-management system; use the PR #19 notes or an existing document if adequate. **Recommend** superseding/closing PRs if warranted, but do **not** merge or close them without owner approval.

## Acceptance and stop conditions

- A new agent can identify Sophon's product charter and immediate *cumulative contractual-learning* research objective without conflating either with business validation.
- It can locate E0–E5/BI validation, the independently authored public-data experiment, the Publicodes negative result, the direct normative-layer skeleton, and Jev/V1–V3; it can distinguish implemented experimental code from the `main` baseline and from V4's unexecuted proposal.
- It explicitly qualifies E0–E5 as limited author-designed feasibility tests, Publicodes `STOP_KERNEL` as narrow and valid, V2's lack of observed incremental library benefit, and V3's frozen INCONCLUSIVE vs provisional secondary evidence.
- No rewritten frozen protocols/results, no artificial PASS, no new code architecture, no new paid/model calls, no PR merges/closures, and no forced broad manual review.
- Run all relevant local static/unit checks, plus one negative test exposing a formerly missing/inconsistent context reference. Report CI status separately from actual hook smoke-test status. If a clean end-to-end session cannot be exercised, say so.
- End with a short **KEEP / REVISE / STOP**, actual changed files and commit SHA, verified vs unverified items, and **one owner decision** if needed (for example approval to merge PR #19 after checks).

**Challenge this specification** if an even smaller correction meets the same observable outcome. Do not quietly expand housekeeping into a rearchitecture, an E6/V4 experiment, a new PR stack, or a general research programme.
