# Sophon — Claude Code Execution Prompt E2: Blind Semantic Relationship Discovery

**Date:** 12 October 2026
**Status:** Authorize E2 ONLY; do not execute E3–E8 or the deferred comprehensive G1.
**Governing:** SOPHON_CHARTER.md v1.1; CLAUDE.md; AGENTS.md.
**Programme:** SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md, especially E2 and experimental integrity.
**Dependency:** E0 PR #4 PASS_NATIVE_RUNTIME; E1 PR #5 PASS_KNOWN_BINDING (BOTH are currently draft, unmerged, stacked). This E2 prompt is committed to main; implementation must branch from **E1's head**, not main.
**Critical risk:** R2/R3 with **bindings not supplied**: can a fresh AI solver discover relevant business predicates, actual metric/semantic objects and physical data relationships without wrongly promoting unobserved or untrusted facts into verified status?

## 0. Executive constraint

**One primary experiment:** Blind, evidence-grounded discovery of clause → business predicate → existing MetricFlow object → underlying field, or explicit abstention/unknown where that chain cannot be established.

We have demonstrated:
- E0: genuine native MetricFlow integration, reproducible synthetic warehouse.
- E1: deterministic known-binding validator for one small lab policy, *with the correct bindings and a lab authority registry supplied*. E1 is not proof of AI discovery or source authority inference.

E2 tests the missing step: **proposals without answer keys**. Do not spend the experiment writing a sophisticated agent, legal DSL, transposition compiler, approval workflow, policy database, or audit platform.

E2 outcome must distinguish:
(A) finding actual relevant objects and connections;
(B) identifying source facts not exposed in native semantics;
(C) detecting a missing/unsupported fact and refusing proxy substitution;
(D) recognizing genuinely unresolved meaning or authority;
(E) declining to invent evidence.
A native calculation can be validated only AFTER these predicates have been accounted for.

### Essential research-integrity warning — E1 answer leakage

The E1 branch and earlier Claude Code session **already contain** lab clause text, mappings, authority designations, EXPECTED.json and evaluator code. Simply asking the SAME Claude Code session, or a subagent with repository/history access, to "discover" E1's answers is **NOT BLIND**.

A fresh session is necessary but not sufficient. In E2:
- Prepare **new held-out clauses**, not merely rename E1 A/B1/B2; keep old cases only as clearly labeled diagnostics.
- Freeze expected references **before** scored solving.
- Execute the scored solver in a **fresh, isolated model session**, supplied only with a sanitized read-only evidence packet and the requirements. The solver gets NO E0/E1 experiment results, binding registry, evaluator, expected keys, E1 prompt, Git checkout/history or unpublished oracle.
- The *orchestrator* may know the oracle, but must not answer on the solver's behalf, summarize hints into its inputs, amend the packet after viewing results, or grade via the solver's own claimed confidence.
- Record exact solver input, tool permissions, model/version, session method, output and isolation limitations. If safe context separation cannot be demonstrated, classify BLOCKED_BLIND_RUN/INCONCLUSIVE rather than claim autonomous discovery.

A fresh Claude Code CLI **non-interactive** invocation (e.g., claude -p) is preferred for the scored solver, with the entire bounded evidence packet provided as input and **tools disabled** if the installed CLI supports that. Check the actual locally installed CLI help; do not invent flags. Use a new process/session, not --continue or --resume. If tools cannot be disabled confidently, use a sandboxed external working directory with no git history, no E1 files and explicitly constrained read-only tools; disclose any residual access to private oracle material. If neither isolation route is available, STOP and document BLOCKED_BLIND_RUN. Do not fake model outputs as a pass. A one-shot packet is a **bounded read-only discovery task**, not a demonstration of interactive tool-using enterprise retrieval.

## 1. Mandatory read / current repository state

Read in full:
1. origin/main:SOPHON_CHARTER.md, CLAUDE.md, AGENTS.md.
2. origin/main:SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md.
3. origin/main:Claude_Code_Sophon_E2_Blind_Relationship_Discovery_2026-10-12.md (this file).
4. E0 branch: experiments/E0_native_adapter/{PRIOR,PROTOCOL,RESULTS,DECISION,README,SOURCE_GATE}.md and src/mf_adapter.py, crosscheck.py; key native manifests.
5. E1 branch: experiments/E1_predicate_binding/{PRIOR,PROTOCOL,RESULTS,DECISION,SOURCE_INVENTORY,README}.md; FROZEN_CASES.json, EXPECTED.json, src/evaluator.py, inventory.py, oracle.py and tests.
6. Live PR #4 and #5 status/heads, any review and CI. Do not call missing CI a pass or merge anything silently.

In E2/PRIOR.md document the **previous observations and limitations**, including E1's lab-defined authority registry, supplied bindings, 16 passing *reported* tests, no Windows run and no external authority. Record any conflicts between a broad older plan and this small E2 prompt; follow the owner's most recent E2 request within the charter.

## 2. Worktree / stacked PR hygiene

1. Inspect git status and worktrees; never reset or overwrite user changes.
2. Fetch origin and verify the latest E0/E1 head commits. As of prompt creation: E0 a84c855 and E1 e0dd474; do NOT assume these SHAs are unchanged.
3. Create isolated worktree and branch experiment/e2-blind-discovery-2026-10-12 based on origin/experiment/e1-known-binding-2026-10-12 (unless PR #5 has merged, in which case verify its contents in main and branch from the proper landed base).
4. Keep E0 and E1 directories **byte-identical**, do not rewrite their protocols or results. Work only in experiments/E2_blind_discovery/.
5. Open a **draft stacked PR**, base experiment/e1-known-binding-2026-10-12 while E1 is unmerged; if stacked base later changes, reflect it transparently.
6. Clone the same pinned upstream behramkorkut/Governed-Analytics-Agent at 312e97ad192dcef02f688e31edc0a08c6cf4345f (MIT), rebuild with E0's locked environment when needed, never edit it in place. Label all retail fixtures LAB_AUTHORED/synthetic. Preserve source provenance and actual executed commands.

**A suggested E1 cleanup is NOT a prerequisite:** E1's read-only wrapper for native --where works. Adding a public where option to the E0 adapter is optional only if it is a real blocker and can be made as a separate minimal reviewed patch. Do NOT let this become an adapter refactoring project.

## 3. Test design — bounded but actually discriminating

The environment stays ONE pinned dbt/MetricFlow/DuckDB project and ONE coherent retail revenue/order policy area; the model may need to choose between several *pre-existing* MetricFlow metrics (not automatically handed the correct target).

Before coding the solver, construct a **small, preregistered held-out set of SIX** original, lab-authored clauses in this familiar policy area, including at minimum:

- **Two genuinely representable cases**: distinct but plausible requirements whose correct native metric + key predicates/fields can be substantiated. They must not both be simple rephrasings of the E1 completed_revenue clause. Prefer selecting from the existing revenue, completed_revenue, related measures/dimensions; verify that the chosen metric can execute the required calculation. Target identifiers are NOT given to the solver.
- **One source-present / native-unexposed case**: an additional requirement whose needed field demonstrably exists upstream but cannot be filtered or otherwise represented through the current metric's actual native semantic constructs (confirm native limitation, not just missing YAML).
- **One genuinely missing fact** in the bounded estate, with a tempting proxy such as an order lifecycle status that *cannot prove* payment settlement.
- **One misleading-near-match case**: a superficially plausible but wrong metric or physical fact, requiring the solver to distinguish e.g. cost/profit/revenue, quantity versus amount, order status versus external business fact; no artificially misleading source evidence should be invented.
- **One legitimate semantic/authority ambiguity**: the requirement alone and supplied written context do not resolve a material business distinction. Correct answer is a specific missing interpretation/approval, not a guessed field. This case tests abstention and should not be scored as an automatic failure to answer an impossible question.

The exact six clauses must be chosen and sealed, not published in this prompt as reusable answer templates. Vary phrasing and decoys. No real contracts/authorizations are implied. Record which clauses, if any, overlap prior E1 material. If the requested strata cannot be constructed honestly on this one small estate, report the limitation and revise case selection **before** freezing; after freeze, never invent a source to force the target classification.

Include irrelevant metrics/dimensions and near-matches in the solver-visible catalog. The solver must choose **all relevant predicates**; returning one metric name is not enough.

### Ground truth / answer-key requirements

Prepare a **human-reviewable, independently sourced reference** from pinned native semantic YAML + manifests + dbt lineage + raw CSV generator/source docs, validated using actual native queries/negative controls where appropriate. The oracle is still LAB-authored; do NOT call it independent legal judgment.

For each case, pre-register:
- Required normative predicates and their source clauses.
- Accepted native metric/semantic objects, valid physical lineage and any valid equivalent alternatives.
- Exactly what is known from the source, what is only suggestive, and what requires external authorized interpretation.
- Expected coverage classification and the material traps/false assurances.
- Source evidence supporting the reference; native compiled/executed results where the rule is objectively expressible.
- A deterministic scoring rubric, including acceptable equivalent identifiers and strict treatment of unsupported "fully verified" claims.

**The individual who knows the key must not be the scored solver session.** Freeze the source and key with a hash/commit **before** scored solver invocation; keep them in the trusted evaluator area, never the solver packet. A hash is integrity evidence, not independence proof.

### Solver-visible evidence packet

Build only from existing pinned upstream or E0's source-extracted native artifacts, **not from E1 FROZEN_CASES, EXPECTED, authority registry, E1 case summaries or prior solved answers**.

Include enough information to make the task answerable:
- The six full governing-clause texts with explicit provenance "LAB_AUTHORED, not approved organizational policy".
- A reasonably complete catalog of candidate metrics, semantic models, dimensions, measures and names/descriptions (not a cherry-picked subset that reveals the answer).
- Relevant dbt field identities, native declarations, source-schema/lineage excerpts, upstream description of their meaning, and scope of the inspected estate.
- The fact that upstream data are synthetic; definitions of what "source-present", "semantically exposed" and "not established" mean.
- Clear output JSON schema below and conservative guidance: do not treat order status as a payment confirmation unless authoritative equivalence is explicitly evidenced.
- **Do not** include the hidden expected outcomes, reference mapping, authority registry or any field explicitly labeled "correct answer".

A packet may contain honest domain facts already present in upstream documentation; facts must not be stripped so aggressively that no solver could succeed. Equally, do not convert the packet into a solved tutorial. Hash and freeze exact solver packet bytes before the scored call.

## 4. One fresh blind scoring run

**Preferred implementation:** Build the packet as plain text or JSON, pass it (as stdin/CLI prompt, based on installed CLI behavior) into ONE fresh, non-resumed Claude Code CLI process. Restrict tools to none if the CLI supports it. The solver should not have file/network access to the orchestrator repo, hidden keys or model memory of this E1 run; there is no guarantee against pretrained knowledge of public upstream, so disclose residual limitations.

All six cases are in this one scored batch; do not let solver see case status/reference or learn from per-case feedback between outputs. If the CLI demands tool permissions or a different invocation to run, inspect help and record exact working command; do not change case selection/scoring to accommodate solver performance.

Output a structured response (a single JSON object or JSONL) for each clause ID containing:
1. Atomic business predicates extracted from the text with exact phrase/span supporting each.
2. Candidate native metric(s), semantic object(s), physical relation.column references, with precise source-evidence pointers.
3. For EACH predicate: classification BOUND_AND_EXPOSED / PRESENT_IN_SOURCE_NOT_EXPOSED / NOT_FOUND_IN_BOUNDED_ESTATE / UNRESOLVED_INTERPRETATION / NOT_ESTABLISHED_AUTHORITY; list unknown/uncertainty rather than force a mapping.
4. Statement of what the native semantic calculation can and cannot establish, plus any missing evidence; NEVER convert a proxy into verified authorization.
5. Confidence as stated by solver, and any explicit abstention, at both predicate and overall-case level.
6. Overall verdict restricted to VERIFIED_FOR_SPECIFIED_CHECKS / PARTIAL_OR_UNKNOWN / NOT_VERIFIABLE / REQUIRES_AUTHORIZED_INTERPRETATION. Do not allow a model's overall claim to overrule the deterministic independent evaluator.

If the solver emits malformed JSON, record raw output and score it as a format failure; don't manually repair scoring input. You may record an unscored diagnostic repair afterward, keeping the original scored artifact untouched.

Run ONE attempt. Do not retry with a better prompt after seeing accuracy. Additional samples or alternative models are separately labeled non-scored diagnostics, never used to cherry-pick E2 PASS.

**Cost:** Record prompts, output size, token counts/cost only if obtainable, model/build, wall time and invocation count. Do not require additional paid API keys; use existing Claude Code CLI access. If that cannot provide the blind scored process, classify BLOCKED_BLIND_RUN rather than quietly replace it with the orchestrating assistant's answer.

## 5. Independent mechanical scoring, not model self-grading

Build the smallest scorer for the frozen six cases **without introducing a new bespoke governance framework**.

- Validate schema and exact clause IDs; don't score a partial/truncated response as complete.
- Require exact (or preregistered equivalent) **semantic object + physical field + predicate meaning**. Matching a string name, providing a plausible explanation or citing irrelevant YAML is not enough.
- Use E1's *existing* deterministic validator and native E0 queries **when compatible** with the proposed predicate classes; translate proposal → evaluator input **without backfilling missing entries with the reference answer**. When a new predicate is outside E1's supported grammar, use preregistered targeted native/source tests or classify the validator coverage as untested.
- Cross-check every positively verified native relation against the actual native catalog, compiled/executed metric result and independent source-row calculation where the predicate is expressible. Do not award verified from the solver's confidence alone.
- For missing-source or ambiguous clauses, award proper abstention **only if the reason is correctly identified**, not blanket UNKNOWN on everything.
- Report **false positive full assurances** as a distinct severe error; conservative abstention on a plainly verifiable case is not an equal success.
- Attribute errors separately: missed requirement predicate, wrong metric, wrong physical lineage, incorrect exposure classification, untrusted proxy/authority, failure to abstain, malformed output.
- Report evidence validity and actual human corrections needed to accept proposals. Count how often manual "fixing" is necessary; no unstated manual repair.
- Show per-case details and a confusion table. Six cases do not justify statistical accuracy/reliability claims, and no enterprise adoption evidence is produced.

### Frozen decision gates (must be copied into E2/PROTOCOL.md BEFORE scoring)

**PASS_BOUNDED_DISCOVERY_SIGNAL** if ALL:
1. The scored solver was demonstrably fresh and received no hidden oracle, E1 answer keys, registry or solver-readable E1 git/history; no measured leakage.
2. At least FIVE of SIX cases are classified correctly, with exact required predicates and **evidence-grounded** semantic/physical relationships for every counted success. Pure name matches are insufficient.
3. BOTH genuinely representable positive cases include all required bindings and correct native semantic targets (not blanket abstention).
4. ALL three materially dangerous negative/uncertain classes — untrusted external-fact proxy, source present but not natively exposed, and ambiguous/authority-required — are **not** confidently misrepresented as verified for the whole governing requirement.
5. **ZERO materially false VERIFIED_FOR_SPECIFIED_CHECKS** claims across the six; an unknown mapping is not an actual verified mapping.
6. Frozen scorer and negative controls reject known-wrong example proposals and reproduce the scored output without model access.

**PARTIAL_DISCOVERY_SIGNAL** if the blind run is sound and some genuine mappings are found with useful abstention, but one or more PASS thresholds are missed without any materially false verified claim. Spell out what prevents PASS and whether a human-approved workflow could safely compensate.

**FAIL_UNSAFE_DISCOVERY** if the blinded solver invents authoritative evidence, confidently substitutes an unsupported proxy, or claims full requirement verification when a mandatory predicate is missing/unexposed or an authorized interpretation is absent. Also report other material misbinding, even if the model avoids a verified label.

**BLOCKED_BLIND_RUN** if a sufficiently isolated fresh model invocation or necessary native setup cannot be performed under the bounded budget. No substitute with stored answers.

**INCONCLUSIVE** if leakage/isolation integrity, frozen key, scorer or factual source reference is compromised such that the recorded score is not credible.

Prefer FAIL_UNSAFE_DISCOVERY over PARTIAL when a false assurance occurs. The primary gate is a **small feasibility signal**, not a credible production error-rate estimate.

## 6. Anti-leakage and anti-vacuity checks (required)

1. **Packet audit:** a script checks that the solver-visible packet contains NONE of these files or explicit answer-key structures: E1 EXPECTED.json, E1 FROZEN_CASES.json, E1 authority_registry, E1 DECISION/RESULTS, E2 hidden oracle/scorer, git metadata/checkout history. Manually review packet for paraphrased answer leakage. Record bytes/hashes.
2. **Source separation:** print the exact files/directories and tools the solver process could access. Fresh process + complete input packet + no tools is the preferred isolation mode. If exposure cannot be limited, do not claim a blind PASS.
3. **Scorer mutations:** score deliberately wrong metric, wrong physical column, missing mandatory predicate, payment status used as settlement proxy, and blanket UNKNOWN across all six; all must lose relevant credit, and false VERIFIED claims must register as severe.
4. **Metric native checks:** demonstrate live MetricFlow can accept a declared positive binding and reject invalid metric/dimension or unsupported predicate filter when scoring requires it. Source-only SQL is not a native semantic query.
5. **No self-confirmation:** scored solver is never asked to grade itself; score computed in separate process against sealed reference. Do not reveal reference before score.
6. **Reproducibility:** scorer run again from frozen packet, unedited raw solver output and hidden reference in a fresh process, producing identical detailed verdict; no original model context necessary.
7. **Contamination statement:** even with isolation, prior model training/public sources and designer's knowledge of E1 are not eliminated; report this limitation. Holdouts are LAB_AUTHORED and constructed knowing the stack.

## 7. Size, stop rules, and deliverables

**Budget:** exactly one pinned semantic estate, six held-out clauses, one scored fresh Claude solver invocation, simple Python/JSON harness, E0/E1 tools reused; do not trigger elaborate multi-agent research or model ensembles, do not generate new warehouse features, do not add external datasets, no automated policy writing or approval.

Directory experiments/E2_blind_discovery/ should contain:
- PRIOR.md — charter alignment, E0/E1 prior results and caveats.
- PROTOCOL.md — protocol, exact thresholds, frozen solver packet construction and source references, solver isolation rules, hash/commit freeze.
- CASES.md or CASES.json — exact six LAB_AUTHORED texts.
- REFERENCE.json — hidden from solver, evidence-backed reference/accepted alternatives, rubric; labelled constructed and not an independent adjudication.
- packet/ — **the exact sanitized solver-visible input** and catalog/lineage extracts (no E1 answers), hashes.
- src/ — minimal packet builder, blind-session runner and independent scorer, with replay.
- evidence/ — scored solver invocation, raw output, tool access declaration, model/version, timing/tokens when available, actual scoring report, scorer-negative-controls, independent replay.
- RESULTS.md — per-case outcomes, binding/evidence errors, false assurances, abstentions, corrections and experimental limitations.
- DECISION.md — exactly one E2 gate verdict and a narrowly justified E3/formal-IR next step only if results warrant it.
- README.md — commands **actually executed**; Windows instructions, with UNTESTED marking unless they ran.

If the frozen oracle must be committed to the PR (for reviewability), it must still be **physically inaccessible to the scored solver** (packet-only input, tools disabled, no repo mount/history). No secrecy claim beyond the controlled invocation.

**Precommitment sequence:**
(a) inspect immutable source and compile evidence packet;
(b) create cases, source-backed reference and rubric, scorer negative controls;
(c) freeze hashes + commit the protocol / packet / oracle, and push **before** solver run;
(d) invoke one genuinely fresh blind solver with exactly that packet;
(e) mechanically score and replay;
(f) commit results, push, open draft PR **stacked on E1**.

If source/rubric corrections are necessary **after** seeing solver output, preserve original output and original score, publish deviations and amended analysis separately; do not upgrade the primary score via post-hoc changes.

**STOP AFTER E2.** Do not build the IR (E3), modify live semantic definitions (E5), attempt persistent production governance (E7), or execute the broad G1 plan.

Final report to owner: branch, PR/base, freeze and final commits, exact six cases, how solver was isolated, PASS/PARTIAL/FAIL/BLOCKED/INCONCLUSIVE, per-case score, false assurances or abstentions, what this does/does not prove, and ONE smallest technically justified next move.

**Remember Sophon's two-direction thesis: E2 tests discovery needed by both governance→implementation and implementation→governance, not the full lifecycle of either.**