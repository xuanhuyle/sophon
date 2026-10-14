# Sophon V4 — Sequential, evidence-backed learning of contractual provisions

**Date:** 13 October 2026
**Status:** NEXT EXECUTION PROMPT — prompt-only; NO V4 experiment has been run.
**Repository:** xuanhuyle/sophon
**Working branch:** experiment/jev-v4-sequential-provision-learning-2026-10-13
**PR arrangement:** Stack this work on V3 PR #17, which is itself stacked on V2 PR #16. Update the V4 draft PR rather than altering historic V2/V3 results or merging branches.
**Operator intent:** Test a small, falsifiable increment of contract-by-contract learning. Not a general-purpose contract foundation model, a proprietary language, a BI product demo, or a race against a pretrained LLM.

## 0. Mandatory orientation and charter gate

Read in full BEFORE any substantive work:
1. Charter v1.2 from PR #15, branch docs/normative-semantic-layer-charter-v1-2-2026-10-13: SOPHON_CHARTER.md, CLAUDE.md and AGENTS.md. The V4 branch may have older versions because #15 is a separate draft PR. The v1.2 owner-approved clarification controls this work.
2. V3 PR #17: prototype/contract_structure_prediction_v3/README.md, PROTOCOL.md, RESULTS.md, PRIOR_ART.md, predict.py, labels.py, and the original V3 prompt. Inspect the actual evidence, not only the PR description.
3. V2 addendum: prototype/jev_library_transfer_v2/V2_POSTRUN_REVIEW.md and relevant V2 experiment design.
4. The existing repo layout, tests, historical reports and decision boundaries. Preserve them.

At task entry write a short alignment note:
- **Mission:** Sophon is a persistent, source-grounded NORMATIVE SEMANTIC LAYER. Its preferred product wedge is checking actual existing BI semantic definitions against governing contracts; direct source-backed access for non-BI consumers is complementary. Do not redefine the product.
- **Capabilities:** TRANSPOSE / TRACE / VERIFY / AUDIT all remain requirements, even if this experiment tests only one upstream component.
- **Stage:** Upstream TRANSPOSE learning component, exploratory engineering feasibility / early reliability (§5). **No BI runtime, agent deployment, legal approval, buyer outcome or downstream execution is being tested.**
- **Source:** authentic, public, precisely identified agreement versions; source authority for each contract is limited by what the document actually is (public vendor standard terms are not evidence of a signed customer agreement).
- **Artifact:** a versioned, inspectable collection of learned provision-structure hypotheses with exact supporting source anchors, learned scope, conflicts, known-at/ingestion chronology and uncertainty; a small typed JSON schema is acceptable.
- **Consumer:** an offline provision-structure predictor and independent reviewer/audit replay. This is an explicitly isolated upstream component, NOT a substitute for the charter's BI-first product integration.
- **No new DSL, proprietary programming language, new foundation-model training, universal ontology, agent control plane, semantic compiler or operational integration.** A future language is an OPEN design question, not a V4 prerequisite.

The owner's analogy is: LLMs predict next tokens; TSFMs predict next numbers; perhaps a conditional learner can predict the NEXT LIKELY PROVISION STRUCTURE from evidenced governing law, contract family, section and surrounding provisions. "Next" primarily means a provision expected/present within a contextual section, not necessarily the immediately next paragraph in textual order. The foundational approach is a research horizon, not an instruction to build a foundation model.

## 1. The ONE primary research question

When Sophon processes unfamiliar contracts ONE BY ONE, does the accumulating, evidence-backed provision library improve **pre-observation predictions** of an unseen provision's likely functional archetype, required semantic fields and structural dependencies, compared with a library frozen after the seed contracts?

Distinguish three different tasks:
- **A: Pre-observation prediction (PRIMARY).** Before seeing the masked target heading/body, rank plausible provision archetypes and predict which executable-relevant semantic components should be checked (e.g. actor/beneficiary, normative action, trigger, threshold, measurement period, calculation, condition, deadline, exception, remedy, definitions and cross-references). Never invent actual contractual values. Predictions create a SEARCH/REVIEW checklist, not a legal assertion.
- **B: Source-grounded encoding after reveal (SECONDARY).** Once the actual clause is revealed, record which predicted elements were present or absent, extract only source-supported values and dependencies, keep unknowns explicitly unresolved and expose exact evidence spans. Do NOT equate a filled schema with a correct legally executable rule.
- **C: Library revision (MECHANISM).** Incorporate only the now-observed, source-anchored structures into a versioned library for the NEXT contract; retain support and counterexamples, preserve conflicting variants and never silently convert predictions into authoritative interpretations.

Primary outcome is a **learning curve across successive previously unseen agreements**, not an LLM answer-quality leaderboard. A pretrained LLM can know common clauses already; this experiment asks whether Sophon's OWN external, explicit, inspectable knowledge actually accumulates and makes a measurable difference. A fixed-model control may be useful to isolate memory effects, but "Sophon beats Claude" is NOT a claim or success criterion.

## 2. What previous experiments do and do not support

V2: actual 30 provider calls, quote/slot proxy scores COLD 35/36, WARM_LIBRARY 34/36, WARM_RAW_A 36/36, BLIND 35/36. The high cold ceiling made the predefined +20 pp hurdle impossible. Warm's B2 facts were sometimes in omitted_conditions rather than scored slots. Verdict: NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE_ON_V2_PROXY, not a verdict on cumulative learning or auditability.

V3: pre-registered masked-structure primary INCONCLUSIVE after two segmentation failures. Post-freeze repair PREDICTIVE_SIGNAL_PROVISIONAL, confined to within-section provision rankings (FAMILY_SECTION 3.09/8 versus FAMILY 0.36/8); section prediction adds nothing beyond FAMILY; Brier worse than GLOBAL; governing-law effect untestable (credit evidence all NY, SLA law UNKNOWN). Sparse support was incorrectly flagged as conflict, plausible wrong section context escaped detection. Labels were agent-authored and not human adjudicated.

**Do not silently promote V3's repaired pilot to independent evidence.** The V3 report recommends human adjudication of eight secondary cases and a fresh frozen protocol. Keep the eight-case adjudication request visible, optionally prepare a compact reviewer packet with source anchors, but DO NOT relabel old scores, invent human approval, or make V3 adjudication an excuse to reuse already-seen agreements as new V4 heldout observations.

## 3. Smallest credible V4 study design — PROTOCOL/FREEZE BEFORE TEST

Before browsing/reading any heldout target provisions or scoring, write PROTOCOL.md and freeze its hash, prediction task, masks, corpus eligibility, schema vocabulary, update rules, arm definitions, metrics, chronological sequence and pass/fail/inconclusive gates. Commit/push that freeze and its receipt BEFORE a test run that reveals target clauses. Report deviations as deviations, NEVER repair the primary retrospectively. Development changes can use seed or synthetic plumbing fixtures.

**Corpus:** prefer ONE authentic contract family with recurring, operationally interpretable provision structures. Default candidate is public vendor service-level agreements with credit eligibility, calculation, claims and exclusions, because these have concrete conditions and dependencies; if sources or clause boundaries are inadequate, document the reason and choose another SINGLE family prospectively using a bounded search. An EDGAR credit-agreement family is acceptable if a narrow executable-relevant provision subset can be labeled credibly. Do not blend unrelated families to manufacture a baseline gain.

Target **at least 8 distinct fresh authentic agreements**: 2 initial seed contracts, then 6 sequential evaluation contracts; aim for at least 2 substantive prediction targets per evaluation document. Across the six evaluation documents, aim for 12+ scored target structures (report achieved denominators, not invented targets). Prefer independent issuers/templates and screen for near duplicates. If there are fewer than 6 genuinely scorable fresh evaluation documents, or too few unambiguous target spans, return BLOCKED_INSUFFICIENT_CORPUS or INCONCLUSIVE rather than shrinking the rule after seeing results. Keep the search modest; do not spend days gathering a huge corpus.

**Freshness/leakage:** V2/V3 agreements already visible to this coding agent may be used ONLY for pipeline development and robustness tests, not V4 fresh scored examples. Do not present material from documents seen in V2/V3 as blind V4 evidence. Split by entire agreement/issuer/template group where practical, never by clause within the same agreement. Save URLs/SEC accessions, publisher, timestamp/as-of status, document hashes, access rights, duplicates, known-at and effective dates where actually evidenced; never invent a governing law from issuer, geography or style. If law lacks contrasting support, explicitly report LAW_EFFECT_UNTESTABLE. Private or unclear-rights raw documents must not be pushed to this public repository.

**Isolation:** the learner gets only the documented allowable context: evidenced/UNKNOWN law; family and optional subtype; observed section function/path where justified; other already-observed provisions; and library version available at step k. The masked target's heading, body, target label, source URL, issuer, filename and target-adjacent duplicate text MUST be excluded from its prediction view. All arms receive identical current-contract observable context. The scoring oracle and full target text must remain outside the learner's prediction inputs. Coding-agent prior exposure is not an independent blind oracle; do not rely on a model claiming it "forgot."

**Reference:** use a SMALL typed JSON/JSON Schema representation of provision archetypes and slot presence / dependency edges, not a new language. Separate:
- provision-type hypothesis / family-section context;
- semantic-field PRESENCE prediction (not guessed values);
- SOURCE-OBSERVED slot values and exact spans after reveal;
- dependencies, qualifications and exceptions;
- predicted versus evidenced versus disputed versus unresolved;
- support/counterexample IDs, status, revision, known-at and applicable/valid dates where known.
A provision may contain multiple archetypes. Unknown and novel variants must be expressible; absent fields are not necessarily errors. Never treat a prior as legal authority or presume any predicted skeleton is an executable obligation.

**Annotation honesty:** heldout reference labels must be tied to exact cited clause spans and independently checked for semantic claims. Claude Code can prepare a provisional annotation packet, but its own annotations are PROVISIONAL_AGENT_AUTHORED, NOT independent human truth. A human or genuinely independent qualified reviewer must adjudicate scored semantic labels before a VERIFIED learning-effect claim. Do not let a self-review, two agreeing LLMs or a deterministic regex labeler satisfy this condition. If human adjudication is not available, complete a clearly marked PROVISIONAL engineering pilot and issue the exact smallest reviewer packet; no semantic-success claim.

## 4. Prequential test: predict → reveal → verify → learn

For contract k after the two fixed seeds, perform in a strictly recorded order:
1. Snapshot library L(k-1), available evidence/time and its hash; snapshot a FROZEN_SEED library identical to L(2) for every evaluation step.
2. For each target, use only the allowed masked context to emit time-stamped top-k archetype candidates, structured slot/dependency expectations, uncertainty, source-support IDs and conditional-frequency denominators/backoff path. Save RAW predictions BEFORE reveal.
3. Score the prediction against the frozen independent reference (or mark provisional); separately record missed critical components, false expectations, novelty/UNKNOWN, context conflicts and untestable legal conditions.
4. Reveal the CURRENT source clause, compare predictions with actual source anchors, record correction/counterexamples, and update L(k) for FUTURE contracts only. Do not use the current contract to rescore its own pre-observation predictions.
5. Make library additions/revisions reproducible, versioned, non-destructive and attributable to exact observations; changes may revise probabilities but may not silently rewrite earlier evidence or claim legal approval.
6. Restart in an independent process and reconstruct one prior prediction and one library update from persisted inputs and receipts, without trusting retrospective model text.

Allow multiple targets in the same contract only if no within-document target answers leak into others: freeze and score the complete batch before revealing any target within that contract, then update once at the end. If the contract contains context that already reveals a target elsewhere, mark that target invalid for primary scoring.

**Chronology:** Freeze the evaluation sequence independently of target labels; make all persistent state monotonically knowledge-time ordered. For alternate-order diagnostics, restart from an entirely new isolated seed/state; never shuffle a single live library backward. Ingestion order is experimental chronology, NOT a claim about real-world legal effective order.

## 5. Baselines — isolate LEARNING, do not run an LLM contest

All comparisons must see the same source-side context and be evaluated on exactly the same frozen targets:
- **FROZEN_SEED:** library fixed after two seed agreements. This is the primary comparison for whether accumulating evidence helps at all.
- **CUMULATIVE_LIBRARY:** same representation, predictor and hyperparameters; learns only from earlier evaluation contracts after their predictions are sealed.
- **SIMPLE_INCREMENTAL_COUNTS:** an updating family/section conditional-frequency baseline using the same previous contracts but no richer structural/dependency library. This is a test of whether sophisticated learned structure adds anything beyond straightforward counts.
- **RAW_PRECEDENT_RETRIEVAL:** a transparent nearest/similar prior provision or document retrieval baseline, seeing exactly the same prior-contract history as CUMULATIVE_LIBRARY. If a fair, reproducible baseline cannot be implemented cheaply without paid models, label NOT_TESTED with reason, and do not assert uniqueness of the learning mechanism.
- **Optional fixed-LLM control:** not the primary comparator; only if a genuinely controlled incremental-information ablation warrants it. Do not call paid APIs or run Jev automatically. Ask for explicit operator approval and specify call/token/US-dollar caps first.

Use simple, inspectable conditional counts / matching / typed slot patterns first. No neural finetuning or bespoke DSL. Be particularly careful not to misinterpret SPARSE SUPPORT as CONTRADICTORY CONTEXT; detect genuinely impossible context separately, with negative controls involving wrong-but-plausible section labels and genuinely novel provision types.

## 6. What to measure and how to decide

Pre-register metrics that test the question actually asked:
- **Pre-observation provision archetype**: top-1/top-3 hit or multi-label precision/recall, plus rate of honest UNKNOWN/novel structures.
- **Predicted executable-relevant slot/dependency SHAPE**: per-document precision, recall and F1 for required field presence and dependency/exception types, with separately weighted critical omissions; NEVER score made-up values as correct. Include overprediction/review burden.
- **Learning curve**: per-contract score at k=3..8, cumulative versus FROZEN_SEED and simple updating/retrieval controls; report distribution by document, not only pooled target count.
- **Provenance/audit**: percent of learned structural claims reconstructable from exact source and version; percent of predictions backed by specific prior observations; missing/corrupt evidence and temporal leakage caught by test; explicit uncertainty and conflicts.
- **After-reveal source encoding (diagnostic)**: correctness of populated slots, exceptions, thresholds and dependencies against an independent source-grounded oracle, separate from pre-observation prediction. No claim of an actually working executable rule, native semantic integration or legal correctness from schema coverage alone.
- Record runtime, requests, tokens, cost and human adjudication time. Zero paid provider calls is the default.

Propose and FREEZE an explicit practical gate BEFORE test outputs. Suggested conservative geometry: minimum six scored later agreements and 12 valid target structures; at least a meaningful improvement over FROZEN_SEED on critical-slot coverage or omission rate across multiple contracts, with no material explosion of false fields; evidence integrity and no future leakage are hard requirements. A gain confined to one near-duplicate issuer/template, a trivial ceiling baseline, an unadjudicated semantic oracle, or failure against an equally updating simple-count baseline must be reported separately. Do not call a result "foundation-style learning" on six documents. Make statistical uncertainty explicit; a small positive trend can only be PROVISIONAL.

Use the following verdict classes:
- BLOCKED_CORPUS_OR_EVIDENCE (insufficient authentic inputs, missing source evidence, unsupported environment).
- INCONCLUSIVE (too few valid targets, label ambiguity, ceiling or insufficient independent review).
- NO_OBSERVED_CUMULATIVE_GAIN (baseline with headroom, no meaningful gain under the fixed gate).
- CUMULATIVE_SIGNAL_PROVISIONAL (fixed gate met, integrity clean, but limited scale and/or not independently adjudicated).
- CUMULATIVE_SIGNAL_INDEPENDENTLY_CHECKED (gate met with independent adjudication; still narrow Stage-1/2 evidence, not a product or foundation-model result).
Only claim an advantage over updating simple counts or retrieval if those arms are actually beaten under a predeclared metric.

## 7. Execution discipline, budget, outputs

**Phase 0 — Inspection and blocker screen:** confirm charter v1.2, current branch/PRs, known V2/V3 problems, authentic corpus access and secrets status. If inaccessible, create a blocker note and STOP; do not substitute synthetic contracts as primary evidence.

**Phase 1 — Freeze:** create prototype/contract_sequential_learning_v4/PROTOCOL.md, typed schema definition, source manifest/split/sequence and immutable freeze receipt. Commit/push freeze BEFORE heldout clauses are parsed or evaluated. A limited synthetic unit fixture may validate code plumbing; synthetic scoring is never evidence of real contractual learning.

**Phase 2 — Offline implementation and pilot:** implement deterministic library updates, baselines, scoring, versioned evidence graph/ledger, masking and tests. Keep the experiment focused; no unbounded refactor. Reuse V3 code only if it passes masking, parser and contamination checks. Provider calls: **0**; if an essential real corpus cannot be accessed, STOP with honest blocker and no fabricated results. Native BI is out of scope here because this is explicitly an isolated upstream learning test.

**Phase 3 — Independent review handoff:** create a concise human adjudication packet for heldout provision archetypes, critical slots/exceptions/dependencies and disputed cases. If no independent labels are received, keep the report PROVISIONAL and state precisely what cannot be inferred.

**Deliverables:** PROTOCOL.md; README.md; source manifest with references/hashes and license notes; a minimal typed schema; versioned learning ledger; offline code/tests; results by contract and arm; primary first-run outputs and immutable receipts; audit/replay check; RESULTS.md with OBSERVED / INFERRED / ASSUMED, adversarial failures, cost, limitations, exact gate and next cheapest decision. Include a brief appendix on the outstanding V3 eight-case human review. Do NOT modify historical V2/V3 primary scores or rewrite charter/CLAUDE.md/AGENTS.md. Do not commit private raw contracts, credentials, API outputs with secrets, or proprietary unlicensed document texts.

**Review gates:** respect the owner's explicit approval before any paid provider call, any material architecture change, any new language/DSL, any broad research program or merger of draft PRs. Use a single primary Claude Code worker; no multi-agent swarm needed. If test geometry cannot distinguish cumulative learning from baseline or corpus quality is inadequate, STOP with the minimum fix and next decision instead of manufacturing a win.

## 8. Final response and decision requested

At completion report:
1. Exact branch, commit, draft PR, source versions and freeze hash.
2. What genuinely ran (especially paid calls = 0), what data was independent versus provisional, and first-run scores for EVERY arm.
3. Did sequential exposure cause a measurable incremental gain? Did it beat simple frequency updating and fair retrieval? Which source-backed structures transferred, and which falsely transferred?
4. Could an independent reader reproduce WHY any predicted archetype/slot was suggested, and HOW each contract modified the library? Show one complete concrete example with source anchor → predicted schema → observation → correction → new library version.
5. What this says about the feasibility of Sophon's cumulative, auditable normative learning—and what it does NOT say about downstream executability, proprietary language, BI compliance checking, Jev or foundation-model generalization.
6. One smallest next action or kill/hold decision, based strictly on the observed evidence.

**Do not drift. The goal is not to win an LLM benchmark. The goal is to test whether Sophon learns something inspectable, reusable and operationally meaningful with each additional contract.**
