# CLAUDE CODE IMPLEMENTATION TASK — JEV V1: genuine models, real omissions, and one decision

**Date:** 2026-10-13  
**Operator model recommendation:** latest Claude Opus (`claude --model opus`), **HIGH effort**. Do not use MAX by default.  
**Execution:** one primary coding agent; implementation + actual evidence, not a 20-agent audit, report, architecture diagram, or multi-week research sequence.  
**Starting point:** `xuanhuyle/sophon` branch `prototype/jev-clause-router-2026-10-13`, draft PR #13. It is stacked on `prototype/normative-v02-candidate-intake-2026-10-12`, NOT main.

## Objective

**Determine, using actual model outputs, whether JEV → adversarial reviewer → backward reviewer catches material contractual-structure omissions better than simpler alternatives, without laundering uncertainty into permissions.**

The existing prototype is `prototype/jev_clause_router_v0/`: five LAB-authored clauses, one Jev Choice + five Noul questions, two fresh LLM calls with opposing prompts, JSON reconciliation, suggested transposition routes. **15 tests passed, but every observed Jev score and reviewer answer is hand-authored.** Do not call this a live system, claim correctness, or move on to rule compilation until the model path is exercised.

The ultimate product is an agent-consumable normative semantic layer, with both **governing documents → operational implementation** AND **operational implementation → governing documents** reconciliation. This task is an upstream interpretation-component pilot ONLY. It is NOT authorization, legal verification, a new policy engine, or a Charter revision.

## Mandatory orientation / branch safety

1. Read `SOPHON_CHARTER.md`, `CLAUDE.md`, `AGENTS.md`, and the existing JEV `README.md`, `RESULTS.md`, `prototype.py`, `test_prototype.py`, `clauses.json`, `mock_evidence.json`. Inspect the related `prototype/normative_layer/` but do not modify its code in this iteration.
2. Read `prototype/normative_layer/V02_PUBLIC_SOURCE_GITHUB_SLA.md` for the independently authored GitHub SLA 2021/2026 sources; keep its contractual applicability caution in force. Do not read the protected `held_out/` of `xuanhuyle/contractual-harness`, change that repository, or claim its fixtures are independent ground truth for this pilot.
3. Confirm current branch, clean/dirty status, and head SHA. Preserve all local changes. Create a child branch named `prototype/jev-v1-live-evidence-2026-10-13` from the actual PR #13 head. If a branch exists, inspect it and do not reset it.
4. Print a short entry gate: this is FEASIBILITY of an upstream routing component, outside the existing Charter's ratified BI integration scope, exploratory only; identify what is genuinely source-authored vs LAB, and what it cannot prove. **Then implement**.

## 1. Verify and harden real provider connectivity

The model adapters already exist in `prototype.py`; reuse them. Do not redesign the architecture.

- Verify Jev against the **official TypeSafe System One request and response schema**, not community guesswork. The request uses `POST https://api.typesafe.ai/v1/systemone` with a Choice and five Noul questions. Inspect the current public SDK if useful; `jev-latest` is an alias and the response's actual model ID should be recorded.
- Guard against documented near-tie `Choice.choice` / `probabilities` inconsistencies caused by rounding. Do NOT silently replace Jev's reported label, invent a probability, or call near-tie disagreement a confident prediction: label provider inconsistency/uncertain and hold that field. Preserve the untouched provider response.
- Validate response shape, missing keys, probabilities, numeric boundaries, errors/429/retry behavior, usage and model IDs. No fallback to fabricated data on live errors. Avoid downloading or transmitting confidential documents.
- **CLI caveat:** existing `reviewer_claude_cli` spawns `claude -p`. When Claude Code itself is running the implementation, nested Claude Code invocations may be blocked or contaminated by session/project context. Do NOT bypass nesting restrictions or spoof the environment. Use an authorized, separate execution context or the Messages API if configured, or emit a standalone PowerShell runbook that the operator can run in a NEW terminal outside Claude Code. Mark a missing credential/access or nested-run blocker honestly.
- Keep `--allow-external-calls` explicit. Before any paid live API invocation, disclose the count and approximate cost, check credentials without printing values, obtain operator authorization if not already provided for those calls, and cap the pilot. The user's Claude Max subscription is not an Anthropic API key. The default offline demo/CI MUST make zero network/model calls.

**Do not spend effort making offline fake responses look like live observations.**

## 2. Freeze a very small but discriminating source set

Use the five existing unchanged LAB clauses as a **smoke test only**. Before modifying labels or using model outputs to define the expected result, write a short explicit provisional **human-review matrix**: primary type(s), all materially relevant modifiers, exact textual evidence, unresolved cross-document dependencies (C4's absent Schedule A), and the harm if a condition is missed. This is a transparent working reference, not an independent expert/legal oracle.

Then select **up to five actual, independently authored provision excerpts** from the official GitHub 2021/2026 SLA corpus already identified. Prefer different structures (credit tiers, exclusion, definition, claims timing, version/effectiveness). Record official URLs, document/version, exact excerpt hashes, available surrounding headings/chapeau, access date and unknown terms; respect copyright, don't copy whole documents or present unaccepted published terms as the signed contract of a real customer. Build a context pack that preserves surrounding conditions and explicitly calls out cross-references missing from the provided packet. Keep this external set FROZEN after choosing it; do not rewrite clauses to satisfy the classifier.

If official primary sources are blocked, record `EXTERNAL_CORPUS_BLOCKED`; do not simulate external validity.

The chief semantic risk to look for is **an omitted material condition**. A classifier that correctly identifies "permission" but misses "provided that no Event of Default is continuing" has failed a consequential part of the task. A source quote appearing in the input does not mean the extracted interpretation is complete.

## 3. Execute four cheap comparison arms on the SAME frozen content

For each clause, record outputs separately:

A. **Jev alone:** reported primary Choice + all five Noul modifiers, no other model.

B. **Jev + adversarial:** an LLM receives the original clause/context and Jev's proposal; assume the proposal is wrong, search for omissions, conflicting qualifications and scope.

C. **Jev + adversarial + backward:** a separate fresh LLM invocation receives the same original clause/context and Jev proposal but NOT the adversary's answer; assume the proposal is right, demand exact support for each asserted field, and explicitly examine qualifiers it omits. This is the owner's proposed architecture.

D. **Blind LLM baseline:** a fresh invocation receives ONLY the source/context, not Jev's predictions or either review, and produces proposed primary type(s), modifiers, evidence and unresolved dependencies. Compare to C rather than assuming the multi-model design is better.

For fair evaluation, keep model IDs and prompt recipes stable and visible, record usage/latency/provider response IDs where available, and classify each record as `ACTUAL_PROVIDER`, `RECORDED_ACTUAL`, `LAB_FIXTURE` or `NOT_RUN`. Even two different Claude reviewer prompts are not independent legal adjudicators; correlated failures remain possible. Do not describe model score values as calibrated correctness probabilities.

Only count actual live outcomes after genuine calls. In CI replay stored records using mocks so runs stay deterministic and free. No new architecture, no agent swarm.

## 4. Deterministic fail-closed decision and falsifiable usefulness comparison

Keep outputs small: source-anchored proposed labels, detected positive and missing modifiers, reviewer challenge/evidence, unresolved refs, hold/candidate-for-review, and **suggested transposition route**. Nothing receives a legally approved state; no operational actions are permitted.

Reconcile with code, not a fourth model:

- A finding of an extra condition/exclusion/deadline/reference must not be silently dropped merely because Jev's Noul score is below 0.50.
- Incompatible verdicts, invalid schema, unanchored citations, unsupported source dependencies, and ambiguous/missing context => `HOLD_UNRESOLVED`.
- If both reviewers support a classification, mark only `CANDIDATE_FOR_HUMAN_REVIEW`, never `COMPLETE`, `VERIFIED` or `AUTHORIZED`.
- Do not count **over-refusal** as correctness. Report candidate/hold coverage and both kinds of errors: missed material qualifiers and false or unsupported challenges. A failing, unanswerable excerpt is informative.

Compare A vs B vs C vs D on these criteria, recorded per clause, without extrapolating statistical rates from 5–10 cases. Include which errors were found *only* by the adversarial reviewer and *only* by the backward reviewer; ask whether C adds anything beyond B and whether either beats D. Record token/call overhead. If C is no better, recommend simplifying the architecture.

## 5. Scope and stop rule

This is **one integrated iteration**, NOT an open-ended experiment-series. Small necessary adapter fixes are allowed; new engines, bespoke DSL, graph DB, extensive tests, autonomous agent clients, production enforcement, UI, and changes to `contractual-harness` or historical Sophon E0–E5 are prohibited.

You must NOT generate a mock reviewer response that intentionally catches the model's known error and call that an experiment. No fine-tuning of Jev prompts against external held-out answers until you obtain a flattering PASS. Do not let a model score its own output as ground truth.

**No integration with Sophon's `/documents` or `/assess` yet.** First answer whether the live classifier/reviewer chain is worth using. A clean seam is allowed, but no transition to operational or approved meaning until the owner authorizes it and the technical evidence justifies it.

One hard stop: if no real Jev access, missing genuine model reviewer access, external requests explicitly unapproved, or no official external source can be retrieved, implement the minimal truthful readiness fixes, run the offline suite, preserve the blockers, produce the exact operator command to complete the real run and **STOP**. No simulated PASS substituted.

## 6. Required deliverables and final status

- Small executable changes in `prototype/jev_clause_router_v0/`: validated live adapters, portable offline replay, optional baseline prompt, and a minimal compare report. Preserve current fixture/demo and tests.
- `V1_LIVE_RESULTS.md`: immutable source identification, **ACTUAL vs SIMULATED** counts, original failure(s), changed code, model and prompts, Jev raw model ID, source snapshots/hash, reviewer outputs, per-clause comparison A/B/C/D, costs if available, known shared omissions, no-claim list and one next bottleneck. The absence of a live run is a blocker, not a PASS.
- Re-run existing V0 + Jev tests/demos and add targeted tests for genuine failures uncovered (no arbitrary test-count target). GitHub Actions Windows + Ubuntu must stay offline.
- Decision at the end: **REUSE, SIMPLIFY, or DROP** the Jev+two-reviewer routing design **for this narrowly tested function**, with 3–5 lines of evidence. This is NOT a go/no-go on Sophon itself.
- Commit only your child branch, push and open a DRAFT PR targeting `prototype/jev-clause-router-2026-10-13`; do not merge and do not rewrite Charter/CLAUDE instructions. If git/network permissions prevent it, report local SHA and precise blocker rather than claiming PR success.
- Final response should be concise: 5 LAB + N actual external counts, provider call counts, A/B/C/D differences, what remains unreliable, executed test commands/exit codes, PR URL if real, and one next action.

**Do not stop after planning or writing an audit. Implement and run what is possible. A successful iteration can conclude that Jev+two LLMs adds no value and should be simplified.**
