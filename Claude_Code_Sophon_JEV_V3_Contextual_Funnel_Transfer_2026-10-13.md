> **DEFERRED — 13 October 2026.** This was the original broad V3 Jev-contextual-funnel design. The owner's newer, more fundamental hypothesis concerns **predicting the next likely agreement section/provision from learned contextual distributions**. **Execute [Claude_Code_Sophon_V3_Masked_Contract_Structure_Prediction_2026-10-13.md](Claude_Code_Sophon_V3_Masked_Contract_Structure_Prediction_2026-10-13.md) first**, after processing the actual V2 live results. Preserve this older V3 plan as historical rationale; do **not** execute it in parallel or incur its proposed 66-call budget without a new owner decision.

---

# Sophon / Jev V3 — Does a learned four-dimensional SOFT funnel reduce errors?

**13 October 2026 — FOLLOW-ON TASK PROMPT; NOT EXECUTED.**
Repository: `xuanhuyle/sophon`. Branch: `experiment/jev-v3-context-funnel-2026-10-13`. This is a **draft prompt-only child** of V2 PR #16 (`experiment/jev-v2-library-transfer-2026-10-13`, implementation head at time of drafting `1151c0ff304f277e5b33432d2a564d51cc4990de`). Do not merge V2 or rewrite its original evidence. Read Sophon Charter v1.2 from `origin/docs/normative-semantic-layer-charter-v1-2-2026-10-13:SOPHON_CHARTER.md` (PR #15), since the V2 branch still inherits the historical narrower charter.

## A. THE USER'S ACTUAL THESIS — read this before proposing architecture

The founder's key claim is **not** "four classification folders are useful." It is:

> Knowing we're in a jungle changes how likely we think a tiger is, compared with a domestic cat. In the same way, an explicitly accumulated, evidence-grounded model of governing law, contract family, agreement section and provision structure should make the correct governing skeleton more likely and wrong interpretations less likely before Jev examines a new clause.

Each document enters a **contextual/probabilistic recognition funnel**:
1. Governing **legal context** (actual evidenced governing law, legal dependencies; not the vendor's address; possible UNKNOWN).
2. **Contract family** (SLA, US leveraged/syndicated credit agreement, etc.; subtype, parents and exceptions).
3. **Section** (real section path/title **AND** its semantic function; cross-section definitions, exclusions, priorities).
4. **Provision structures** (possibly multiple interacting skeletons with Z typed elements: actor, trigger, threshold, calculation, qualifying condition, exception, deadline, remedy, external facts).

A full document can enrich **the library of abstract skeletons AND the learned contextual relationships that associate contexts with skeletons**. The next document should benefit through reusable structural knowledge and **context-conditioned candidate prioritization**, not from copied numbers, drafting literals or access to a secretly pre-labeled test corpus. A financing agreement under explicitly evidenced New York law, in a Negative Covenants section, makes certain provision structures a priori more plausible than an SLA Definitions section. This is a **soft** prior: unfamiliar or contradictory text must override the prior, open new branches or `UNKNOWN`; the funnel must never exclude out-of-family structures by fiat. Misclassified early dimensions must not cascade silently.

This subcomponent sits **upstream of Sophon's TRANSPOSE / TRACE / VERIFY / AUDIT product**. The first actual product wedge remains **governing contracts ↔ existing enterprise BI semantic layers** (Databricks, Snowflake, dbt/MetricFlow), while non-data agents access scoped normative meaning directly. Later, a *source + context + skeleton + instantiated Z values + dependencies* must be **transposed to executable or non-executable business semantics**, followed by independent runtime validation. **Do not build the compiler, legal authority engine, new BI layer or agent controller in this task.**

The user is deliberately asking for a **serious, fair experiment rather than a veto-by-adversarial-review**. Do not label novelty unproven as a global NO-GO; do not reward intricate code/tests. Test whether the funnel produces measurable incremental benefit over a competent conventional alternative.

## B. First gate — V2 is IMPLEMENTED but still READY_NOT_RUN

**Inspect before doing anything:** `git status --short --branch`, current commit, new untracked local evidence, PR #16, V2 README, `V2_TRANSFER_RESULTS.md`, `transfer.py`, `library_v0/v1.json`, `library_events.json`, archived Google source/checklist, V2 PowerShell runbook/tests, and the **owner's local ignored** `prototype/jev_clause_router_v0/live_runs/` and `prototype/jev_library_transfer_v2/live_runs/`.

**Verified as of V3 task drafting:**
- V2 is on PR #16 at `1151c0f`: 17 changed files, 29 offline V2 + 40 V1 + 6 V0 tests reported passing; no V2 Google calls yet.
- GitHub Contract A live evidence was reused with real `jev-1.13.0` and `claude-opus-5-5` outputs, 20 external provider responses (G1–G5) of which G1–G4 supplied induction. No new A provider calls.
- Three A-derived templates were created by a **deterministic, agent-authored lexical inducer**, not a demonstrably autonomous, model-general learning algorithm: tiered service-credit schedule, availability metric definition, credit claim/remedy procedure. G3 exclusion abstained because enumerators were omitted from reviewer quotes; G5 by protocol. The inducer and reference checklist were made **after the developer saw B**; V2 cannot support claims of fully blind transfer.
- V2 B is the archived Google Cloud Storage SLA of 24 June 2021, 3 packets, 36 material elements on an **agent-authored, NOT independent legal gold** checklist.
- V1 baseline invalidity was traced for G1–G3 to `evidence_quotes` being a dictionary rather than an array, **not** unanchored quotations; the V2 validator reports per-field errors.
- V2's `score_condition` primarily credits overlap of a quote with the checklist anchor **plus an acceptable slot name**; this is a **diagnostic proxy, not independent evidence that the slot's interpreted value, units, applicability or legal effect are correct**.
- The COLD / WARM_LIBRARY / WARM_RAW comparison also changes Jev's available Choice template criteria and example context. Treat its outcome as **an integrated treatment**, not a clean estimate of a calibrated four-factor Bayesian model or of Jev versus the reviewers.
- Legal context/contract family/section sidecars are **unscored descriptions** in V2; both source documents are SLAs and signed-agreement governing law is unestablished.
- V2 live run plan was up to 30 logical B calls (31 with optional synthesis), 93 maximum HTTP attempts, ≈ USD 0.82 *estimate only*, no enforceable dollar cap. V2 raw provider outputs belong in ignored local files; SHA receipts can be shared.

**Mandatory hard gate:** First determine whether the genuine V2 Google live run has been performed and locally replayed/scored and whether its recorded output is valid. If NOT: **STOP BEFORE V3 MODEL EXPERIMENTATION OR LARGE IMPLEMENTATION.** Output the precise V2 operator command and explain that completing V2 and human-adjudicating its contested material elements comes first. You may inspect/propose changes, but **do not add a large V3 implementation or spend a provider dollar while V2 is not even observed**. The owner can run in a NEW terminal outside Claude Code:

```powershell
cd C:\Claude\sophon\prototype\jev_library_transfer_v2
powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -Reviewer anthropic
```

Check that operator authorization, API credentials and budget estimate are handled by the runbook. The Claude Code session **must not itself initiate paid calls** or bypass CLI nesting restrictions. V2 may be `INCONCLUSIVE`; report exact reason. Do not silently rerun B, change frozen B/checklist or fix its scoring after seeing its results. Any correction must be a new explicitly amended experiment.

**Once V2 actual evidence exists**, prepare a short `V2_POSTRUN_INDEPENDENT_REVIEW.md` with:
- genuine Jev/LLM calls, outputs, validity, per-field and per-value errors, results by COLD / WARM_LIBRARY / WARM_RAW / BLIND, costs, reviewer-only corrections, no-op/critical failures;
- 36-item checklist's independently **human-reviewed** status per material claim (or `NOT_HUMAN_ADJUDICATED`; do not claim semantic accuracy if missing);
- at least 3 substantive spot-checks of units, windows, thresholds, exclusion, claim conditions and whether `quote+slot` was a false positive;
- clear decision on what V2 does and does NOT establish; whether Jev template-choice instability or library induction undermines the next test.

The V3 decision depends on these results:
- If V2 shows a plausible signal: test **incremental benefit of learned priors and skeletons** without allowing post-hoc library tailoring.
- If V2 finds no benefit over cold or raw retrieval: still permit ONE small direct **context funnel vs flat** diagnostic, but do not build a generalized evolving prior system first.
- If V2 source validity/scorer/schema is fatally inconclusive: repair that specific bottleneck in a *new versioned protocol* and STOP instead of expanding the matrix of arms.
- Never infer that failure of Jev routing disproves the normative layer or Sophon's BI-first wedge.

## C. Pre-register the V3 causal question and success criteria

**Central test:** For unfamiliar governing provisions, does adding correctly evidenced context and then **experience-derived conditional skeleton priors** improve recovery of *material governing meaning* and reduce misclassification/omission **relative to a strong flat interpretation and conventional LLM given the same available evidence**?

Disentangle three effects as far as a cheap experiment permits:
- **E1, basic context:** Does explicit four-dimensional context improve interpretation versus local-clause classification alone?
- **E2, learned funnel:** Given the same context, do *A-derived* abstract skeletons plus learned context→skeleton associations improve performance versus a frozen/unlearned context-only pipeline?
- **E3, robustness:** Can the soft funnel correctly **override misleading but plausible upstream context** and retain `UNKNOWN` rather than doubling down on an incorrect contract-family/section label?

Distinguish **context access advantage** (extra source paragraphs), **context organization/explicit priors**, and **actual cumulative knowledge transfer**. An LLM that reads the same relevant full passages may already get those benefits. Avoid claims of clean isolation where the prompt and dynamic Jev criteria are unavoidably different.

**Primary endpoint:** independently reviewed count of **correctly recovered material slot/value/dependency relationships** across *each* held-out provision, including their negations, qualifiers and scope. A literal quote matching an anchor plus a plausible slot label is **not sufficient**. Report missed critical conditions, false affirmative assertions, mismatched numeric/temporal units, wrong cross-section inheritance, true UNKNOWN, false abstention, time, tokens and costs separately. Preserve per-provision and per-contract totals; no false large-sample statistics.

**Pre-registered indicative hurdle (n ~6; a feasibility signal, not significance):** the LEARNED_FUNNEL should correctly recover at least **three additional material facts across at least two distinct held-out provisions** versus CONTEXT_ONLY, with **no new critical false claims**, and demonstrate at least one real counterfactual-context correction. It must not be substantively worse than the strong full-context conventional LLM once cost is considered. If E1 helps but E2 does not, conclude **CONTEXT_HELPS_BUT_LIBRARY_INCREMENT_UNPROVEN** rather than killing the product. If E2 helps but reviewers/extra cost negate the advantage, classify **TECHNICAL_SIGNAL_COST_UNJUSTIFIED**. If no trustworthy oracle, report **UNADJUDICATED / INCONCLUSIVE**.

## D. Data: deliberately small, genuine, heterogeneous and anti-leakage

V2 used GitHub/Google *SLAs only*. To investigate the real four-dimensional hypothesis we need **different contract families, genuinely named sections and, where actually stated, legal context**. Avoid a giant legal ontology or synthetic contracts invented to flatter the funnel.

Target a **training/transfer triplet** of new publicly retrievable, rights-compatible documents:
1. One independently filed **US syndicated/leveraged credit agreement**, preferably with an actual, express **New York governing-law** clause and sections on defined terms, negative covenants and debt baskets. Use e.g. properly linked SEC EDGAR company exhibits as primary sources. Its public market drafting may resemble LSTA conventions but **LSTA is an industry association, not a jurisdiction or proof a document adopts a proprietary standard**. Do not reproduce proprietary or unlicensed LSTA model documents.
2. A genuinely distinct public **second credit agreement** held out from learning, ideally with a different issuer, drafting style, time and covenant structures; law based on actual clause, not guessed. It tests in-family finance transfer.
3. A genuinely separate **public service/SLA agreement** with definitions, remedies and exclusions not previously seen by the V2 developer. It tests whether the learned specialized finance prior abstains or backs off out of family.

Aim for **six held-out packets total**: ~3 credit and ~3 SLA (multiple sections per document) plus ~3 small training packets from the first credit agreement. Frozen packet source text must include exact nearby definitions, dependencies, exceptions and section paths; do not copy entire credit agreements into the repo. Cite issuer, filing accession, filing date, document/exhibit and accessible URL. Check legal reuse/copyright before storing excerpts. No confidential deal documents, private accounts, undisclosed LSTA drafts or other projects' protected `held_out` files.

The new packet/corpus selection, SHA receipts, inclusion rules, source chronology and element-oracle rubric MUST be frozen **before any V3 provider response or tuning against heldout claims**. A separate person/expert should ideally adjudicate the critical contractual relationships; absent that, clearly label the provisional checklist and limit conclusions to diagnostic evidence. A single Claude agent choosing contracts, choosing labels and writing scoring code is a serious non-blindness limitation. Split source-freeze and model induction into logically separate stages, and never present agent-authored references as independent truth.

Important: **V2 Google B has already been seen in implementation and is NOT a fresh V3 test set.** GitHub A is also exposed. Use them for diagnostic examples only. No fake "new unseen" status. Do not use any data from V3 heldout credit/service agreements to generate training signatures, thresholds, contextual priors, comparison prompts or test conditions.

If you cannot find authentic suitable sources with credible cross-references in a bounded source search (maximum **3 candidate credit agreements and 2 SLA candidates**), emit `BLOCKED_V3_CORPUS` with exact blockers. Do not substitute self-authored clauses to claim transfer.

## E. Learning: make the contextual funnel actually do work

Retain V2 `library_v0/v1` and `context_libraries` **as evidence, unchanged**. Add a new isolated experiment folder only if justified by V2 (e.g. `prototype/jev_context_funnel_v3/`).

Represent two distinct accumulations:
- **Structural skeleton library:** versioned parameterized structures, required/optional typed slots, parent/child relations, semantic/nonmatching counterexamples, known limits, source provenance and dependency edges.
- **Contextual prior table:** record **counts/examples and evidence strength** of `(evidenced legal context, contract family, section function) → candidate skeleton` observed in training. Keep explicit per-dimension `UNKNOWN`, sparse/support-count states, competing alternatives and a soft-prior/backoff rule. Do **NOT** present counts from one or two provisions as statistically calibrated probabilities; no arbitrary "95% correct" labels. Do not hardcode `financing + negative covenants → limitation on indebtedness` in code based on reading the heldout.
  
Every new agreement can `DISCOVER`, `REFINE`, `SPLIT`, `CORRECT` or `ABSTAIN`; version with accepted and rejected evidence. **Transfer abstract shapes and conditional associations only**, never the specific credit ratio, basket cap, threshold, legal effectiveness, issuer, date or financial definition of the training agreement. External relevant defined terms and cross-section exceptions must be retained as dependency edges; a provision can belong to multiple structures.

**Soft funnel design requirement:** ranked candidates and reason/evidence at each stage; explicit top alternatives; a `NO_TEMPLATE/UNKNOWN` candidate always available; a full-coverage fallback to text-based category discovery; a source contradiction or missing required slot must override the prior. If law/family/section are uncertain, pass distributions or `UNKNOWN` context to downstream stages, do not force a single answer. `governing_law` must not be learned as an authoritative country label from service-provider domicile. Preserve choices, context, model outputs, counterexamples and dates for independent audit.

The two LLM roles are **source-omission challenger** and **definition/entailment checker**, independently invoked with no review cross-contamination. A second LLM sharing a model family is not automatically independent legal validation. `SUPPORTED_WITH_GAPS` is a reviewer opinion, not a ground-truth score or automatic proof of unsafe content.

## F. Lean controlled arms — don't add a zoo of agents

Using identical **held-out target provision IDs**, model version, output schema and independent semantic scoring rules, compare:

| Arm | Source/context and memory | What it probes |
|---|---|---|
| **FLAT** | Jev + 2 LLM checks, local provision with the minimum explicit cross-referenced source facts needed to attempt interpretation, **no supplied document/section classification or learned structural priors** | Practical flat baseline; missing context identified honestly |
| **CONTEXT_ONLY** | Same Jev + 2 checks, actual document-level legal evidence or UNKNOWN, contract family, exact section/path/function, dependencies and relevant source text; **no learned conditional skeleton associations** | Incremental benefit of context and its explicit organization |
| **LEARNED_FUNNEL** | Identical source evidence + identical explicit context as CONTEXT_ONLY, **plus frozen training-derived structural skeletons and soft context→skeleton associations** | Incremental knowledge reuse and narrowing |
| **STRONG_LLM** | One conventional LLM with **the same available relevant full source evidence as the contextual arms**, clear typed output requirements, and competent retrieval of linked definitions/sections; no Sophon learned library | Strong/simple alternative, not a deliberately handicapped blind baseline |

This is an integrated *context/funnel* comparison, not a claim of perfect per-dimension statistical attribution. Where Jev choice criteria expand between arms, report the candidate-list change, option order sensitivity, probabilities as raw uncalibrated outputs, model disagreement and alternate-template availability. Do not let `CONTEXT_ONLY` see the learned templates, and do not secretly give the learned arm extra contract source facts.

**Counterfactual robustness probes:** on **two of the heldout packets**, take the unchanged actual source text and deliberately supply one **false but plausible section/family label** in a clearly labeled adversarial copy of the context. These are NOT real governing-law facts. Run LEARNED_FUNNEL with those false labels, keeping the real primary source text and cross-references available; record whether it challenges the upstream label, backs off and recovers the source-grounded interpretation. Do not turn this into an ordinary scored test case or silently treat bad metadata as ground truth.

Target upper bound for a pilot with six held-out packets:
- `6 × (3 Jev pipeline arms × [1 Jev + 2 LLM]) = 54` logical provider calls.
- `6 × (1 STRONG_LLM) = 6` more.
- `2 × (1 Jev + 2 reviewers)` misleading-context probes = 6 more.
- **Maximum 66 logical provider calls**, with a separately enforced maximum of 198 physical HTTP attempts if retry policy allows 3 attempts per call. Training may reuse existing evidence or offline induction; if extra A provider calls would exceed the cap, require separate operator consent rather than silently expanding it.

**No provider calls from Claude Code implementation session.** First implement minimal offline adapters/validators/replay and a separate PowerShell `RUNBOOK_V3_CONTEXT.ps1` with credential-safe preflight, **printed exact call counts/model IDs**, a credible token/cost estimate, and a typed `YES` in a new terminal. No enforceable cost cap should be misrepresented as one. The operator may choose to not run. `.env` and original V1/V2 raw recordings must remain ignored and untouched. Record raw provider results locally with SHA receipts and only permission-cleared excerpts/summaries in PR.

## G. Independent verification & failure attribution

Freeze an answer-key/assessment checklist with **specific material facts and exact source references** before provider outputs. Mark each critical item `INDEPENDENTLY_ADJUDICATED`, `PROVISIONAL_AGENT_AUTHORED` or `UNKNOWN`. Blind-review condition labels when human-scoring extracted facts. Count:
- **semantic meaning**, including correct metric units, timing, temporal applicability and actual conditions—not merely anchor overlap;
- cross-section definition, exceptions, priority and supersession;
- false inclusion or omission of negotiated exceptions;
- category/template confusion, `NO_TEMPLATE` correctness and overabstention;
- false confidence when family/section label is wrong;
- actual incremental contribution of each Jev, omission reviewer, entailment reviewer and library entry when observable;
- output-schema/provider problems distinct from semantic problems; cost/time/token overhead and effect of source context length.

**Do not assume every provision compiles.** For each learned skeleton record a future `transposition_target_kind` as a *hypothesis* (native BI metric check, executable conditional policy, human-only/legal interpretation, insufficient observable facts). No code generation or claims of verified compliance here. If a financing ratio is eventually tested against a BI model, it needs actual executed native semantic data and contract-specific definitions, a **separate experiment**.

**Decision rubric at end:** `FUNNEL_ADDS_VALUE_PROVISIONAL`, `CONTEXT_BUT_NO_LEARNING`, `RETRIEVAL_OR_LLM_AS_GOOD`, `HARMFUL_PRIOR/OVERGENERALIZATION`, or `INCONCLUSIVE`. State which exact stage/structure failed and what narrower change or replacement would be justified. **Never automatically infer a product-wide GO/NO-GO**.

## H. Deliverables and workflow

**If V2 is still READY_NOT_RUN:** finish **only** the V2 live-run audit/readiness gate and an honest handoff note; do not prematurely implement V3. Give the operator's exact new-terminal V2 runbook command and stop. This document remains a **draft follow-on prompt**.

**If V2 live results and adjudicable evidence exist:** implement only the smallest V3 experiment consistent with their failures/successes:
1. Concise `V2_POSTRUN_INDEPENDENT_REVIEW.md` (raw evidence counts, semantic spot checks, limits).
2. `V3_PROTOCOL.md` with sources, explicitly frozen training-vs-holdout split, material-element reference and model/call budget.
3. Small versioned learned-context/prior and skeleton files with `UNKNOWN`, alternate classes, provenance, event ledger, testable validation and no learned B vocabulary.
4. Minimal source/hierarchy / cross-section representation; **reuse V2 code** rather than duplicating its 1,473-line `transfer.py` into a larger framework.
5. Native Jev + two-reviewer arms and a strong comparable-context LLM baseline, replay and a separate preflight/runbook, targeted offline tests, no paid calls in implementation.
6. `V3_RESULTS.md` with `READY_NOT_RUN / BLOCKED / ACTUAL_RUN`, causal contrasts, semantic adjudication, error/cost trade-off, specific contrary examples, and a careful stage-limited decision.

Create work in **a new child branch of this prompt branch** if the working directory is already in use or has local changes; do not force-reset any branch. Do not merge, change the v1.2 charter, overwrite PR #16, tamper with frozen V2 sources/checklist, or commit unreviewed private provider evidence. Commit/push only if authorized and safe; **update the existing draft PR for the follow-on branch rather than opening duplicates**, or state why blocked. One primary Claude Code implementation agent, not a swarm.

The intended eventual domain specialization (for a later, independently validated version) is **US leveraged finance / LSTA-style public-market credit agreements**, trained from lawfully accessible actual contracts. LSTA drafting conventions are not governing law and do not license copying protected association templates. Domain-specific priors should *specialize shared primitives*, not create disconnected, conflicting legal authorities.

**Final Claude Code reply:** verified V2 status and correctness limitations; what actually ran and what did not; source/prompt/version hashes; precise branch/PR/commit links; paid call count = 0 inside Claude; operator's next PowerShell command; one unresolved causal uncertainty. **Do not stop after superficial planning when evidence is available, and do not conceal a missing V2 live run under a big V3 implementation.**
