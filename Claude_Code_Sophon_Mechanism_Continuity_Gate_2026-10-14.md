# Sophon — implement a real experiment-lineage continuity gate (ONE increment)

**Date:** 2026-10-14  
**Repository:** `xuanhuyle/sophon`  
**Starting branch:** `guard/jev-lineage-continuity-2026-10-14`  
**Starting HEAD:** resolve latest on this branch (the owner-reconfirmed `PROJECT_STATE.json` commit is `ab377211`)  
**Target:** a single PR from this branch to `main`; no merge without review  
**This is a PROCESS FIX ONLY:** No new experiment, no new scorer, no change to V1–V4 frozen code, no paid model/API calls.

## Why this is needed (verified, not speculative)

Current `main` v1.2 has `ENGINEERING_WORKFLOW.md`, `PROJECT_STATE.json`, `.claude/hooks/context_guard.py` and one context-integrity workflow. Its hook injects a list of existing components and instructions; **it does NOT reject a new 'cumulative Jev learning' experiment that never imports/runs Jev or either reviewer**. Indeed V3 statistical heading prediction and V4 regex/textual-proxy prediction diverged from the intended pipeline without being flagged. V4's frozen STOP is valid **for its own proxy only**.

The owner reconfirmed the experiment lineage:

1. Jev classifies each provision (existing V1 adapter).
2. Separate adversarial reviewer challenges it (existing).
3. Separate backward/source reviewer checks required evidence (existing).
4. A genuinely **independent** library-based review evaluates the candidate against source-backed provision skeletons (**NOT implemented as a third review mechanism in V2**: V2 passed the learned library as shared context to Jev and the first two reviewers).
5. Deterministic reconciliation retains disagreements and scope/unknowns (existing).
6. Learn source-anchored semantic skeletons (conditions, exceptions, dependencies, definitions; provisional unless independently verified), preserve support/counterexamples, and revise as additional agreements arrive (partly implemented V2).

The agreed **next SINGLE delta after this guard task** is to add/test step 4 within the existing V2 pipeline. The owner has NOT yet authorized another paid run. Do not implement it here.

`PROJECT_STATE.json.active_research_mechanism` on this branch pins that lineage, real code refs, missing component, and V4 limitation. Consult the actual V1/V2 code on current PR #17, V3/V4 results on #17/#18, the current charter and workflow. Never assume experimental code lives on `main`.

## REQUIRED change (scope is the existing guard, not another governance layer)

Implement the **smallest viable executable check** using the existing `.claude/hooks/context_guard.py`, CI workflow and existing `tests/test_context_guard.py`:

1. **At session/prompt entry:** clearly inject the pinned `active_research_mechanism` chain, its existing V2 code ref, the *not-yet-implemented* independent library reviewer, the next single delta, and an explicit warning that V3/V4 statistical experiments are **separate**. Read from `PROJECT_STATE.json` rather than duplicating prose in multiple files. If the pin is deleted, malformed or silently changed while claiming the same research lineage, the context check MUST fail.

2. **At new prototype experiment entry / PR check:** a new or materially changed experiment protocol/runner/results under `prototype/` that purports to advance the active Jev provision-learning work must include a *small, machine-checkable mechanism declaration* naming:
   - parent implementation **source ref** (`PR #17`, actual branch/head; not only the prompt);
   - single new capability/delta and explicitly preserved mechanisms;
   - which paths/functions are actually invoked (versus merely referenced, mocked, proposed or absent);
   - expected method and separate actual run provenance/status, including whether real Jev and reviewer calls happened;
   - scope of legitimate claims and what it cannot prove.

   Check what is **truthfully attestable** by reading actual source code and recorded run receipts, not only declaration text. Be honest about limits of static checks: a string naming Jev is NOT evidence of invoking Jev. At minimum an automated negative regression must reject a *V4-shaped regex/count-only* experiment mislabeled as the Jev review-loop increment. Ensure a genuine zero-provider-call plumbing fixture is allowed only when clearly labeled *PLUMBING_ONLY*, not as proof that Jev review ran.

3. **Changing mechanisms must be conspicuous:** distinct experimental hypotheses remain possible, but MUST be called `SEPARATE_MECHANISM`, must not be presented as continuing the Jev loop, and must not silently revise the active research focus. An actual pivot of the active owner-confirmed lineage requires separate explicit owner authorization reflected in a reviewed canonical `main` state change **before** a replacement experiment begins. A PR must not self-authorize its own pivot by setting a Boolean.

4. **Keep CI practical.** No new agent/plugin/framework, enterprise governance architecture, full-blown manifest registry or onerous procedure for minor docs/bugfixes. Reuse existing `check_pr_state_update` machinery and `.github/workflows/context-integrity.yml` where possible. There must be no required network calls or model calls in tests. The PR check should be FAIL-CLOSED for substantive experiment claims but not freeze all ordinary development. Record any enforcement limitation clearly.

5. **Test both sides.** Add regression tests for:
   - missing / tampered active lineage pin;
   - prompt/context displaying the EXACT Jev+adversarial+backward+library/skeleton lineage with the missing third reviewer clearly marked;
   - an invented V4 statistical runner claiming to exercise the Jev loop is REJECTED;
   - a properly labeled **separate** structural-prediction experiment is not confused with the Jev loop;
   - a valid single-delta V2-lineage task passes at the *planning* stage without pretending providers were invoked;
   - a result claiming Jev reviewers ran but lacking supporting execution receipts is rejected or explicitly **UNVERIFIED**, NEVER treated as verified.

6. Existing `tests/test_context_guard.py` must remain green. Preserve all V1–V4 frozen data and historical branch topology. `PROJECT_STATE.json` already records V4's scoped STOP; correct only demonstrably wrong factual details. Avoid further repo housekeeping unrelated to this gate.

## Important operational caveat

Historical PRs #16–#18 **predate** the main guard and may not execute it on their own bases. Do NOT claim the new guard retroactively controls those branches. For future Jev incremental implementation, start a CLEAN branch from guarded main and import/reuse the relevant code from PR #17 intentionally, with no uncontrolled merge/rebase of old experiments. The new gate should fail when running in a checkout that lacks the authoritative state; fail clearly rather than continue from an older memory.

GitHub `main` is currently **not protected**; a passing GitHub Action without required-check enforcement is not an absolute gate. Report this residual risk; don't claim it is resolved unless enforcement is demonstrably configured. The active GitHub App may lack permission to set branch-protection rules. Do not spend time inventing workarounds.

## Definition of done

- ONE focused reviewable PR/branch; do not open more.
- Evidence: offline tests pass plus one intentional fail-closed example (V4 false-continuity case).
- Verify the GitHub Actions check if access permits.
- Summarize exactly what is prevented, what remains possible, and the next single increment (not executed).
- No Jev provider calls, no new contractual experiment, no model training, no extra roadmap.

After committing/pushing the guard implementation, **STOP** and send the commit SHA and one recommendation for review/merge. Challenge this task if there is a significantly simpler way to achieve the *same enforceable* outcome; do not substitute a prose-only checklist or lengthy process document for a working gate.
