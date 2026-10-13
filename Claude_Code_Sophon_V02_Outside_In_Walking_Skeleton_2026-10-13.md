# CLAUDE CODE TASK — Sophon V0.2: first real-world failure and working repair

**Date:** 2026-10-13  
**Mode:** IMPLEMENT AND VALIDATE, not planning-only. One primary coding agent; do not spawn a large research/audit swarm.  
**Starting branch:** `prototype/normative-v02-candidate-intake-2026-10-12` (based on the V0 walking skeleton, PR #12).  
**Destination:** code + executable demonstrations + regression tests + honest failure notes, committed on this branch, and a draft PR targeting `prototype/normative-layer-walking-skeleton-2026-10-12`. Do NOT merge.

## Mission — preserve the actual goal

Sophon is intended to become a **shared normative semantic layer**. A company's authoritative governing documents (contracts, financing agreements, supplier agreements, properly adopted policies, amendments, and ultimately applicable law) are the source of commitments. The layer helps different workers, agents, and existing systems reuse authorized, time-scoped operational meaning instead of reinterpreting the entire corpus independently. It must preserve ambiguity, missing facts, provenance, authority, and evidence. It must support **both** governing-source → operational implementation and implementation/change → governing-source reconciliation. This is an exploratory expansion beyond the owner-approved Charter's existing BI semantic-layer boundary, NOT an already ratified Charter revision.

Build vertically. Follow the path: **real source clause → extraction proposal → explicit review → persisted normative meaning → stable API → support and billing clients → amendment → changed agent-facing decision + evidence**. Improve the actual working system in response to failures. Do not optimize for an easy PASS or produce another isolated experiment.

## 0. Ground yourself before changing code

Read in full:
- `SOPHON_CHARTER.md`, `CLAUDE.md`, `AGENTS.md`.
- `prototype/normative_layer/README.md`, `ARCHITECTURE_DECISION.md`, `sophon_v0.py`, `demo.py`, `support_agent.py`, `billing_agent.py`, `test_sophon_v0.py`, and `V02_NEXT.md`.
- The actual limitations and results of V0 / PR #12, and the limitations/decision of E5 / PR #11.
- Rulebook `xuanhuyle/rulebook`, in particular Part II's false-confidence risk of ex-ante formalization, Part III's field/predicate fidelity caveat, and Part IV's nine steps and proposed comparison in IV.12, if network access permits. If inaccessible, record the limitation; do not invent results.

Confirm `git status` and branch before editing. Preserve unrelated or uncommitted work. Do not switch/reset over user changes. Main may not contain V0 because PR #12 is OPEN; do not implement against main alone.

**Critical repository fact:** In the prior conversation, a V0.2 ZIP was produced locally, but its code was **not committed to GitHub**. This branch currently contains the V0 files and `V02_NEXT.md`, NOT an assumed existing Claude extraction adapter. Work from files actually present. Do not depend on downloading that ZIP.

Before work, print a brief entry gate: charter conflict/experimental status, technical uncertainty, real vs synthetic source, and what cannot be proven. **Then implement**; do not stop after the gate, commentary, or a proposed plan.

## 1. Start with an externally authored source, and capture the failure

Find **one actual public, independently authored customer agreement or service-level agreement** with at least one concrete operational commitment (e.g. service credits) and one challenging element (exception, defined term, cross-reference, claims window, or tiered remedy). Initial candidate: Cloudflare's publicly available R2 Service Level Agreement; confirm the original page actually exists and read the text rather than assuming facts about it. You may select a better publicly accessible agreement if the R2 SLA is technically unsuitable; record why.

- Record official URL, retrieval date, title, relevant clause identifiers or limited excerpts, exact source hash for the material you exercised, copyright/access constraints, and whether it is genuinely independent of this prototype.
- Do not scrape private material, download user secrets, silently transmit contracts to an LLM provider, or paste large copyrighted contracts into the repository.
- Freeze the chosen text and a **separately written expectation matrix** before modifying the parser/evaluator. The matrix must include positive, negative, boundary, ambiguous, and missing-fact cases, plus one expected consequence of a source amendment. It must be based on direct reading of the source and explicitly mark any contested meaning, not on the implementation's output. For real legal conclusions, call it a **working interpretation**, not authoritative legal advice.
- Feed the source excerpt as text into current V0 **unchanged**, capture actual structured output and failures in `prototype/normative_layer/v02_evidence/` or equivalent. Expect the two exact-pattern regexes to abstain. Do not retouch source wording until it fits.
- If remote retrieval is blocked, do not fabricate a real-contract result. Try a different publicly accessible primary source already available in the repository or reachable in the environment, documenting provenance. If none is available, mark REAL_WORLD_SOURCE_BLOCKED and continue infrastructure work using clearly labelled lab fixtures; do not claim external transfer.

## 2. Implement the narrowest useful repair in the integrated application

Add **candidate-based extraction** to the existing V0 document-ingestion path, not a disconnected standalone toy.

Requirements:
- Keep the existing strict recognizer as a deterministic baseline and keep V0 API clients/tests working.
- Add a provider-neutral, mockable `candidate_proposals` intake: machine suggestions are `PROPOSED`, never approved merely because an LLM or other tool produced them.
- Add an optional Claude Code-assisted proposal producer for local experimentation if compatible with the installed CLI; inspect `claude --help` rather than assuming flags. Avoid nested agents, recursive CLI runs, paid API use, or transmitting a contract without an explicit user opt-in. The **entire demonstration and CI must work without network/model keys** using recorded untrusted candidate fixtures. If a genuine model invocation is impossible, document that and do NOT report one.
- Every proposed normative unit has: immutable/verbatim source span or clause quotation, document key and version/hash, proposed rule type, typed parameters and units, uncertainty/unresolved state, observed vs effective time, and evidence links. A JSON/SQLite representation is sufficient; do NOT invent a proprietary DSL.
- Validate proposals independently of the producing model: exact quote/source anchoring, coverage (unprocessed clauses become unresolved), bounded numbers/units, required fields, no injection-derived instructions, and a closed set of executable predicates. **Verbatim numeric anchors are necessary but not sufficient to establish meaning**: a quote supporting 5% doesn't prove how 5% should apply.
- Include an explicit **review of the proposed interpretation**: the review must reference an immutable candidate hash/version, show source and normalized candidate, and record a distinct LAB_REVIEWED_NOT_LEGALLY_AUTHORIZED state. Changing a proposal after review invalidates that review. Preserve old approved versions. Real identity verification/legal authority is NOT implemented and must not be claimed.
- Do not treat unresolved clauses as harmless merely because another clause is executable; a decision affected by them must return `UNRESOLVED` or `NOT_VERIFIED`, never confident permission/credit eligibility.
- Avoid reimplementing V0 from scratch, adding a frontend, inventing a policy engine, a graph DB, an agent swarm, a new workflow framework, or a DSL.
- Extend one concrete, independently authored contractual requirement **only as far as needed** for a working end-to-end consequence. If its semantics remain indeterminate, support safe abstention plus a review queue instead of inventing a formula.

## 3. Exercise BOTH directions on one connected path

**Forward (governance → agent context):** The support and billing clients, as distinct external programs using the same stable API (not sharing contract-specific prompts), must consume one approved/reviewed governing interpretation. Ingest a versioned amendment; show that before review both retain the old applicable context, and after review both see the updated effective context **without editing their code**. Demonstrate a negative example with a wrong date or still-unapproved revision.

**Reverse (implementation → governance):** Introduce one **actual consumer/operational-rule-originated change** (for example, a material changed mapping or credit calculation parameter) without changing the governing record. Sophon must detect or explicitly mark the mismatch/unverified status against its stored reviewed normative rule and show traceable counterevidence. Include a harmless/equivalent change control that should NOT be treated as material. Keep this narrow; if robust reverse reconciliation is not possible with the current adapter, surface that missing capability and do not fake a PASS.

Neither client is a production autonomous agent. Show source references, current vs historical version and the decision/evidence trail. No real payment/refund/external writes, credentials, production auth or final legal verdict. Keep all `execution_authorized` false.

## 4. Make failure-driven iteration visible

Conduct at least one actual `fail → inspect → fix → regression` cycle. Preserve both the **first failure** and the after-change outcome. A green synthetic suite alone does not satisfy this task.

Add tests that specifically try to break the system:
- unsupported/ambiguous clause and competing readings;
- forged or mismatched source quotes, unit confusion, omitted clause and unsupported exception;
- unauthorized or altered proposed candidates;
- amendment known before approval, effective in the future, and historical as-known lookup;
- missing/stale/contradictory operational evidence;
- one material reverse drift and one harmless/no-op change;
- no model keys/no network (the default CI path);
- old V0 two-client demo unchanged.

No test should simultaneously invent a governing source, supply its correct answer, and then claim independent semantic validity. Distinguish authored lab reference, source-anchored checking, and an actual independent judge.

## 5. Runnable deliverables and files

At minimum ship:
1. Working additions/changes under `prototype/normative_layer/` integrated with V0. Do not touch the historical E0–E5 implementation or experiment results.
2. One executable `demo_v02.py` or equivalent showing the entire path and actual API calls from support + billing; show abstention/clarification when necessary and one amendment.
3. Tests runnable with `python -m unittest discover -s prototype/normative_layer -p "test_*.py" -v` from the repo root. Update existing CI on Windows and Ubuntu to run the new tests and demo without external model/network.
4. `prototype/normative_layer/V02_RESULTS.md` with an **OBSERVED / INFERRED / NOT DEMONSTRATED** table, external-source provenance, initial failures and fixes, total tests, actual command outputs, agent/API evidence, unsolved semantics, and the exact next blocking failure.
5. Update the prototype README: setup and copy-paste PowerShell commands, optional consent-based model proposal workflow, and explicit limitation statements.

**Do not claim** “real-contract parsing works” merely because a model emitted a plausible JSON record. Do not claim that passing unit tests proves legal interpretation, enforceability, production authority, agent compliance, operational correctness from caller-supplied facts, or commercial usefulness.

## 6. Stop condition, branch hygiene and final response

Work to a **runnable v0.2 vertical slice**, not a new research roadmap. If the external contract defeats the current normalized model, *that is useful evidence*: either implement one small justified feature to address the witnessed failure, or retain honest `UNRESOLVED` with a precisely described semantic gap. Do not change the chosen clause merely to obtain a PASS.

Preserve `SOPHON_CHARTER.md` and `CLAUDE.md` unchanged. The broader normative-layer scope is **exploratory, not silently ratified**. Keep TRANSPOSE, TRACE, VERIFY and AUDIT in view, including both governance-to-implementation and implementation-to-governance. Follow established V0 architecture where possible; no new major subsystem without a demonstrated need.

Run tests and the actual demo in the available environment. Re-run after the last code change; record failures, platform limitations and final results faithfully. If possible, push the branch and open **one draft PR** targeting `prototype/normative-layer-walking-skeleton-2026-10-12` (PR #12's branch), not `main`; include commands and limitations. If push or PR is blocked, make a local commit and report the blocker—do not describe an unpushed PR as created. Do not merge or modify unrelated PRs.

Your final answer must state: source actually used and provenance, first observed failure, changed implementation, two-client behavior, reverse check outcome, exact tested commands/results, unverified claims, commit and PR URL if actually created, and **the one most important remaining failure**.

**You have authorization to implement this task. Do not stop after reading, scoping, drafting a plan, or writing only fixtures. Stop only after working code + executed evidence, or a specific hard environmental blocker with an honest partial deliverable.**
