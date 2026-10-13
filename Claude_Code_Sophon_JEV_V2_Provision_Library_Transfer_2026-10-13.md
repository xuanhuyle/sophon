# Claude Code Task — JEV V2: Does an evolving provision library transfer from GitHub to Google?

**Date:** 13 October 2026  
**Status:** Implementation instruction, not an experimental result.  
**Repository:** `xuanhuyle/sophon`  
**Task branch:** `experiment/jev-v2-library-transfer-2026-10-13`  
**Stacked base:** `prototype/jev-v1-live-evidence-2026-10-13` (draft PR #14, itself stacked on PR #13).  
**Current product charter:** Sophon Charter **v1.2**, draft PR #15 (`docs/normative-semantic-layer-charter-v1-2-2026-10-13`). This charter supersedes the v1.1 copy inherited by this task branch. **Read it explicitly via `git show origin/docs/normative-semantic-layer-charter-v1-2-2026-10-13:SOPHON_CHARTER.md` before working.** Do not interpret the old branch copy of the charter as a mandate to make BI the only consumer; do not edit the charter here.

## Zero: what Sophon is, and what this experiment is NOT

**Sophon is a shared, evolving, source-grounded normative semantic layer for governing contracts, policies and other documents.** Its **initial commercial/engineering wedge is checking those requirements against the pre-existing BI/data semantic layer** (dbt/MetricFlow, Databricks, Snowflake, etc.), thereby exploiting data teams' existing semantic work. Non-BI agents must also be able to access applicable governing context directly. All four product capabilities remain **TRANSPOSE / TRACE / VERIFY / AUDIT**.

This task tests only an **upstream interpretation and learning subcomponent**: can Jev, with two independently invoked LLM checks and a *versioned library of provision structures*, retain useful structural knowledge from one genuine document and apply it to a second, unseen genuine document?

It does **not** establish legal authority, correct executable code generation, real BI semantic integration, enforcement by agents, end-to-end Sophon viability, or market demand. The eventual later engineering problem is **category/slots + authorized interpretation + real bindings → appropriate native executable representation**, which may be a metric, calculation, guard, workflow or *non-executable/UNKNOWN*. **Do not build that compiler or BI adapter in this task.** Preserve minimal, explicitly non-executable `transposition_candidate` metadata only if useful for future research.

**Project stage:** Charter §5 **Stage 1 component feasibility**, with very limited diagnostic evidence for Stage 2 (reliability/transfer). No generalizable accuracy percentages from three holdout packets.

## 1. Inspect the actual repository and preserve evidence

Use ONE primary Claude Code implementation agent; no agent swarm, open-ended search or architecture proliferation.

1. `git status --short --branch`; inspect branch/head, untracked files and remote. **Never reset, clean, force-push, stash, delete, overwrite or commit the user's local `.env` or original `live_runs/` recordings.** If the current branch is not this task branch, determine why and switch safely. If a local file blocks switching, STOP and ask rather than discarding it.
2. Read `SOPHON_CHARTER.md` **v1.2 from PR #15 using the explicit `git show` above**, then read current `CLAUDE.md`, `AGENTS.md`, the existing Jev prototype `README.md`, `V1_LIVE_RESULTS.md`, `prototype.py`, `compare.py`, `test_v1.py`, `external_github_sla_2021.json`, `review_matrix.json`, `RUNBOOK_V1_LIVE.ps1`, and relevant E0–E5 engineering notes as context only. Inherited v1.1 documents describe **prior technical hypotheses**, not today's charter.
3. Locate the **real local V1 live-run recordings**, especially `prototype/jev_clause_router_v0/live_runs/live_EXT_*.json` with corresponding `replay_EXT_*.json`. The owner previously completed **40 actual provider responses** across 5 LAB + 5 GitHub excerpts. The repo's committed `V1_LIVE_RESULTS.md` predates those local runs and still says `BLOCKED_NO_LIVE_RUN`; **do not misread that stale committed report as evidence that the owner's subsequent live run never occurred**. Verify actual `ACTUAL_PROVIDER` step provenance, input hashes, model IDs and completeness. Treat missing or unusable recordings as an explicit blocker; **do not fabricate or silently rerun Contract A**.
4. Run the existing offline unit tests. Preserve all V0/V1 outputs unchanged; add this experiment under a **separate `prototype/jev_library_transfer_v2/`** (or similar small directory). Reuse the V1 provider transport/validators as libraries when sensible; do not rewrite the existing Jev study.

**V1 empirical warning:** the owner's last 10-clause live comparison showed Jev-alone candidates on 9/10, adversarial and backward reviewers reporting `SUPPORTED_WITH_GAPS` on 10/10, and 7/10 blind LLM responses rejected as `invalid or unanchored baseline output`. These facts establish actual execution but NOT classification accuracy, reviewer value or semantic completeness. A fail-closed disposition is not a correctness score. This task MUST keep **provider completion, syntactic validity, anchored-evidence validity, true semantic coverage, unsupported claims and safety hold** as *separate measures*.

## 2. Sources: Contract A is already recorded; freeze Contract B first

### Contract A — learning source, NO new calls required for its initial extraction

Reuse the four source-backed provision packets **G1–G4** from the already frozen `prototype/jev_clause_router_v0/external_github_sla_2021.json`:

- G1 — tiered service-credit calculation and quarterly measurement.
- G2 — definition of Downtime / observation predicates.
- G3 — exclusions.
- G4 — claim deadlines, redemption requirements, limitations and remedy.

Use the **actual previously recorded Jev / adversarial / backward responses** for G1–G4 when available, not the LAB fixtures and not the June 2026 notice G5. Check source+context hashes and the model response provenance against the frozen GitHub SLA (June 2021). These are independently published vendor standard terms, **not a signed customer agreement** or a legally approved interpretation. A source-vendor PDF with access restrictions is not license to circumvent them.

### Contract B — held-out transfer source

**Google Cloud Storage SLA — archived version of 24 June 2021**:  
`https://cloud.google.com/storage/sla-20210624`

This is the verified official **archived** page (labelled “Last modified: June 24, 2021”), **NOT** the current `/storage/sla`. The Google source includes per-class/location SLOs, a monthly rather than quarterly measurement, five-minute Error Rate aggregation, qualifying Valid Requests/Back-off, tiered credits, a claim deadline, a monthly maximum and exclusions. Do not insert clauses or thresholds from the current version.

Before library induction or any Google model call:
- Fetch the archival primary source directly and record URL, HTTP status, retrieval UTC, full available source digest and exact version; if blocked, log `BLOCKED_B_SOURCE` and STOP rather than inventing text.
- Freeze **exactly three coherent, genuinely distinct Google packets** covering (B1) uptime metric / denominator / Valid Requests / five-minute aggregation, (B2) storage-class-and-region-specific SLO / financial-credit tiers, (B3) financial-credit claim deadline / maximum / exemptions or exclusions. Include short surrounding text needed to correctly interpret each packet, and explicitly record unresolved cross-references. **Do not split off crucial qualifiers just to make the task easier.**
- Record exact packet spans/anchors and hashes, minimal quote excerpts (do not publish the whole copyrighted page), source title/version and applicability `UNKNOWN`.
- Freeze a **provisional material-element assessment checklist** with exact source anchors, supported contextual dependencies and a deliberately novel/non-transferable detail, plus the scoring rubric, **before** any B provider responses. Label this agent-authored checklist `PROVISIONAL_NOT_INDEPENDENT_ORACLE`; it is not an expert/legal adjudication. Keep it separately sealed from the learning model's prompts.
- Do not pass B packets, reference checklist or post-run score to the library enrichment call. A coder may have seen B while preparing the freeze; record that weakness and do not claim fully blind development. No post-outcome source/label rewrites.

### Why GitHub → Google is interesting

GitHub's SLA expresses quarterly uptime/credits; Google Cloud Storage uses **monthly** scope, multiple service tiers and a different underlying observation/calculation. A useful library should transfer *the shapes* (threshold, measurement window, beneficiary, trigger, exclusion, claim condition) **without transplanting GitHub's literal numeric values, quarterly window or service definitions**. This is an explicit contamination/counterexample probe.

## 3. Learning target: X / Y / Z, not an encyclopedia

Use a tiny, **versioned provision-library** of structural templates, not a store of copied model answers. This is axis 3 of the triple specified in §3A; axes 1–2 are source-grounded, inherited document metadata in this experiment and are not scored as Jev learning.

- **X** = number of supported macro-categories/templates; use the existing V1 candidate labels as the minimal bootstrap vocabulary, not a universal ontology.
- **Z** = typed, source-evidenced elements of a template (for example `actor`, `beneficiary`, `normative_action`, `object`, `trigger`, `measurement_period`, `threshold`, `calculation`, `exception`, `deadline`, `remedy`, `source_reference`, `required_fact`, `uncertainty`). Do not assume every category requires every slot.
- **Y** = measured share of *material governing content* whose structure and critical elements are correctly represented within tested packets, **not** merely text classified or percent of words covered. Report numerator/denominator and unknown coverage.
- A template needs a stable ID and version, precise **definition**, required vs optional slots, slot types, qualifiers/conditions, positive examples, counterexamples/nonmatches, known limits, source references/hashes, status `PROVISIONAL` or `REJECTED/SUPERSEDED`, creation/update lineage and why it changed.
- One clause can instantiate **multiple** related structures. Missing/new structure may be `UNKNOWN_NO_TEMPLATE` or `NEEDS_REVIEW`; don't force closest-match classification.
- **Learning events:** `DISCOVER`, `REFINE`, `CORRECT/SPLIT`, or `ABSTAIN`, versioned and sourced. Counterexamples must be able to invalidate templates.

**Minimum credible enrichment:** Automatically propose at least one genuinely structural rule/refinement from A, using source-backed Jev + both recorded reviewer observations; one bounded *new* LLM synthesis call may be used at a later operator-authorized live phase if needed. A deterministic validator must reject missing source anchors, contradictory slot definitions, copied vendor-specific literals presented as general rules, supersession without evidence or untrusted `APPROVED` claims. The library remains **provisional**, never silently promoted to an authoritative legal interpretation. The synthesis prompt must be restricted to A evidence; no B content can enter.

The first library can be JSON/JSON Schema files plus standard-library Python. **No graph DB, vector DB, proprietary DSL, fine-tuning or large RAG stack.** For tiny X, simple bounded candidate selection is enough. **Jev is NOT an embedding/similarity search engine.** If Jev cannot accept the dynamic candidate list/definitions in its official Choice/Noul schema, document the limitation and keep retrieval a transparent deterministic step, rather than inventing unsupported provider behavior.

## 3A. Three-axis identity: governing legal context × contract family × provision structure

**Owner's additional architectural requirement:** the provision library is axis 3 of a **three-dimensional, progressively enriched structural model**:

1. **LEGAL CONTEXT / governing law:** Identify the law or jurisdiction governing a document/provision **where source evidence establishes it**. Distinguish (a) governing law, potentially subnational (e.g. New York state, England and Wales), (b) chosen court/forum, (c) mandatory regulatory applicability, (d) parties' domicile and service locations, and (e) absent referenced master agreements. These are different fields, **not** one automatically inferred country. A vendor's home country or text language does not prove governing law. Explicit `UNKNOWN`, `MULTIPLE`, `CONFLICT` and `REFERENCED_SOURCE_UNAVAILABLE` are valid results, with the exact evidence or missing source.
2. **DOCUMENT / CONTRACT FAMILY:** An evolving, versioned classification library of agreement families (e.g. `SERVICE_LEVEL_AGREEMENT`, `MASTER_SERVICES_AGREEMENT`, `FINANCING_AGREEMENT`, `EMPLOYMENT_AGREEMENT`, `LICENSING_AGREEMENT`, `DATA_PROCESSING_ADDENDUM`, `OTHER/UNKNOWN`). Each template has a definition, identifying elements, positive examples, counterexamples, limitations and update lineage. Contracts may combine families, and an SLA can be an annex to a broader agreement.
3. **PROVISION STRUCTURE:** The existing evolving library of macro-categories and Z elements, including actors, rights/duties, conditions, thresholds, measurement periods, exceptions, remedies, evidence, unresolved references and compound provisions.

**Every provision can reference a typed triple:** `(legal_context_id, contract_family_id(s), provision_template_id(s))`. The first two axes normally belong to the **document context**, inherited by linked provisions with source/version/scope; a provision-specific override is allowed only with evidence. This avoids repeatedly inferring governing law or contract family from isolated snippets. Do not treat a document classification as evidence that every provision falls into a specific category.

**Three libraries with the same integrity principles:** definitions, typed elements, canonical IDs, versions, examples and counterexamples, source anchoring, provider provenance, uncertainty/abstention, and `DISCOVER / REFINE / CORRECT / REJECT` history. Claims remain `PROVISIONAL` unless accepted by the actual competent authority. Learning a recurring pattern does **not** make it legally authoritative or universally applicable.

**Intended Jev + reviewers intake architecture (later independently scored):** Jev proposes contract family and legal-context/evidence-status from the **whole relevant document and incorporated context**, not each excerpt alone. Two fresh LLM calls independently challenge (i) material omissions, conflicts and external references, and (ii) whether library definitions and required evidence actually support the proposed label. Unknowns are first-class; probabilities are not calibrated legal certainty. Reuse the document-level determinations while Jev analyzes individual provisions. Do not substitute a guessed "US" label for lack of governing-law evidence.

**Strict V2 experiment boundary:** The GitHub → Google study comprises **two vendor-published SLAs** whose excerpt packets do not establish an executed master agreement's governing law. Thus **it cannot measure cross-family transfer or country/jurisdiction detection accuracy**. Keep the already-frozen *provision-structure* cold/warm/raw comparison and **31 logical-provider-call limit** unchanged. In this V2:
- Implement a **minimal, versioned `context_libraries/` sidecar** (or equivalent few JSON files) for legal-context status and contract-family identity, with definitions, statuses and evidence. Use explicit `UNKNOWN` on governing law unless the *accessible* source actually states it; don't infer country from GitHub/Google corporate location. Record the distinction between missing governing law, known forum and any mandatory law.
- Record the **source-anchored SLA contract-family label** from the archived title/headers, while preserving uncertainty about incorporation, scope and legal applicability.
- Make each frozen A/B provision reference its document's legal-context and contract-family records (with versioned inheritance, source hashes and scope), rather than re-running a document classifier per provision. No separate Jev/LLM calls for these two metadata axes in this task.
- Validate unsupported legal-jurisdiction inference, conflated forum/governing law, unjustified provision override and missing provenance **offline**. Report context status separately from scored provision-slot accuracy.
- **Do not assert that Jev has learned these two axes** from a pair of SLAs. A later dedicated study must compare different contract families and legal contexts, with sources explicitly containing applicable-law evidence and an independent oracle. Keep optional Jev intake hooks limited to a documented interface seam—not a speculative general library system.
- Preserve identical document-context sidecars across COLD_B, WARM_LIBRARY_B, WARM_RAW_A_B and BLIND_LLM_B; never let Google answer keys enter A-only induction.

This is a **design-contract extension**, not a new scored V2 hypothesis, live-call expansion or claim of comparative-law competence.

## 4. Required fixed comparison on exactly the SAME frozen Google packets

Keep model IDs, provider request recipes, maximum context budgets, two separate reviewer invocations, scoring and contract packets fixed. **Only permitted variable among the three pipeline conditions is the memory supplied**:

| Condition | Jev + two LLM checks see | Meaning |
|---|---|---|
| **COLD_B** | Fixed bootstrap category vocabulary, no Contract A knowledge or learned library | No-learning baseline |
| **WARM_LIBRARY_B** | Same fixed pipeline with A-derived **structured provision library V1** and template definitions/counterexamples | Structural-transfer hypothesis |
| **WARM_RAW_A_B** | Same fixed pipeline with *raw comparable A examples* (no induced structured library) | Strong retrieval-only alternative |

Also run **BLIND_LLM_B** once per B packet as a diagnostic, using only its source/context and the same typed element-output requirements. This is a single-LLM reference **not** a substitute for comparing full auditability and lifecycle evidence.

All three multi-model conditions MUST contain real Jev participation, even if the tiny library is embedded as bounded context rather than a dynamic Choice ontology. **Do not present LLM-only retrieval as Jev classification.** The two LLM roles are:
1. **ADVERSARIAL:** independent source-grounded challenge of Jev's candidate, seek omitted conditions, cross-references, wrong units/periods, false analogies and competing templates.
2. **DEFINITION/BACKWARD CHECK:** independently verify that each matched template's *definition and required slots* are satisfied by exact source evidence; seek necessary evidence absent from the proposal; report unsupported matches. Receives Jev + applicable template, but **never the first reviewer's output**.

V1's backward-review logic may be adapted, but **all conditions must get functionally equivalent reviewer questions** (with unavailable template facts represented honestly). Don't let the WARM role receive extra instructions like “you must be better.” Preserve independent prompts, retrieved sources, model version, state inputs, question definitions, slot-level answers, raw provider outputs, confidence as *un-calibrated* and decision rules.

**Score named slots and values for provision-structure transfer (axis 3)**, not merely presence of one of five V1 modifier labels. Report axis 1/2 metadata descriptively; do not mistake a source title or unknown jurisdiction for a scored Jev prediction. Separate: type accuracy; slot precision/recall per material element; verbatim support; wrong transfer (quarter/month, different service tiers, percentages and deadlines); missing cross-references; false reviewer challenges; invalid output; unjustified candidate; justified hold; latency, tokens and cost. Provider call-count equality for the three Jev pipelines matters; token count differences must be disclosed. The blind baseline is cheaper and should be reported as such.

**Schema repair before running B**: use recorded V1 outputs and offline fixtures to diagnose the generic `invalid or unanchored baseline output` errors; ensure field-level parse/schema/anchor diagnostics and equivalent *validation standards* for all arms. Repair schema systematically without looking at B outcomes; do not loosen evidence anchors silently, cherry-pick valid responses or run endless post-hoc retries. A reviewer `SUPPORTED_WITH_GAPS` is a question to verify, **not** an automatic semantic failure or proof of accuracy. Keep `HOLD_UNRESOLVED` separate from quality scores.

## 5. Small, prepaid-run boundary, anti-leakage and minimum runbook

**Do not initiate paid TypeSafe or Anthropic calls inside this Claude Code implementation session.** First implement/test in zero-provider-call mode. Produce a Windows PowerShell **`RUNBOOK_V2_TRANSFER.ps1`** and no-network `-PreflightOnly` option. The operator runs the live phase in a NEW terminal outside Claude Code, with explicit typed `YES` after printed call/cost cap. Reuse the safe allowlisted, non-executing repo-root `.env` loader from V1; never display values.

**Target maximum: 31 provider calls**, based on existing Contract A live Jev+reviewers:
- A training: **0** new Jev/reviewer calls (reuse V1 authentic recordings).
- Optional one-time A-only library-induction/synthesis: **1 LLM call** (if necessary, not an obligation to spend).
- 3 B packets × 3 conditions × (1 Jev + 2 LLM): **27 calls**.
- 3 B packets × 1 blind LLM: **3 calls**.
- **Total ≤31** (9 Jev + ≤22 LLM). **No unbounded retries**; count attempted HTTP requests including retries toward a separately logged hard physical request cap. The 31 figure is a *logical-call* cap; state the maximum actual network attempts and cost implications. Don't quietly retry an entire experiment after partial failure.

Estimate the actual model cost from the current provider and token assumptions in preflight, allow the operator to choose a smaller test or abort, and require **explicit confirmation** for the whole quoted ceiling. Since thinking-token and long-output costs vary, a dollar figure is an estimate, not a guarantee. If transport lacks a true enforceable spend cap, explicitly state this limitation. `claude-cli` access must not be nested inside Claude Code or falsely called free; prefer a reproducible API path if the operator has the key.

**Never put API secrets or full unreviewed provider transcripts in public commits.** Keep raw local evidence in `live_runs/` under ignored/private storage with SHA receipts and minimal redacted derived summaries in the PR; check or extend `.gitignore` carefully without erasing any existing user files. Never automatically publish copyrighted whole contracts, personal information or real user API metadata.

**Offline modes:** `preflight`, `replay`, `compare` and a deterministic learning-library validator **and a bounded three-axis metadata/inheritance validator**. Do not use self-written pretend Jev/LLM results as empirical transfer evidence. A safe test fixture may prove plumbing only and must say `LAB_FIXTURE`. Version/hash the initial library, learned library, three B packets, prompts, model IDs and scores. Do not replay warm evidence into cold state or let persistent notes/model chat contexts leak training/holdout information.

**If local V1 A recordings, official B source, provider credentials or permission are unavailable:** stop with a precise blocker and finish an honest offline/readiness result. Do not claim transfer and do not fabricate substituted source/model outputs.

## 6. Pre-register decision rule *before* the first Google provider response

Freeze this rule with the packets and provisional reference checklist. Human review of material items is required before claiming verified interpretation accuracy. A source quote alone does not validate its claimed meaning.

- **PROMISING TRANSFER (provisional only):** WARM_LIBRARY_B recovers **at least two additional correctly supported material slot/value facts**, improves recall by **≥20 percentage points** over COLD_B on the frozen provisional reference, causes **zero new critical wrong transfers or unsupported material assertions**, and beats WARM_RAW_A_B on **at least one substantive corrected omission**, all on the same B packets. Show the exact A-derived library entry that caused each improvement. This is an *engineering signal on n=3*, not statistical evidence of generalization.
- **NO OBSERVED INCREMENTAL LIBRARY VALUE:** WARM_LIBRARY_B provides no substantive advantage over COLD_B or the same-example retrieval baseline; or the additional matches are merely copied words/values; or it introduces a critical false interpretation. Record whether the issue seems to be the learned structure, Jev selection, LLM checking or the harness.
- **INCONCLUSIVE/BLOCKED:** no genuine A provider recordings, unavailable B source, provider errors, invalid/unscorable model outputs, insufficient adjudicable evidence, or ambiguous schema/corpus leakage. Do not relabel invalid schema as model reasoning failure or fail-closed holds as correct interpretations.

**Also report** if a simple blind LLM matches or exceeds WARM_LIBRARY_B; report operational overhead. An expensive complex pipeline cannot be called superior by virtue of producing more audit artifacts: Sophon's *auditable infrastructure* is relevant, but the **incremental Jev/library extraction claim** must independently earn its complexity.

## 7. Deliverables — implement, don't stop at planning

Keep additions small and isolated, with only targeted changes to V1 if strictly necessary.

1. `prototype/jev_library_transfer_v2/README.md`: protocol, frozen source reference, data boundaries and exact no-network/live/replay commands.
2. Frozen Google B source manifest/packs/checklist and hashes, with precise permissions/applicability and independently unverifiable caveats.
3. Small versioned `library_v0.json` and **A-derived `library_v1.json`** (the latter only after real A evidence and actual induction); recorded `DISCOVER/REFINE/CORRECT` events, rejected proposals/counterexamples, provenance and validation rules. Include the compact **versioned `context_libraries/`** legal-context and contract-family metadata, with cited document inheritance per provision; no additional scored calls.
4. Minimal runnable engine invoking actual V1 TypeSafe/Anthropic adapters, two LLM reviewers with library-conformance role, COLD/WARM/RAW comparison, blind baseline, per-field validation, evidence receipts and deterministic reconciliation. No arbitrary general framework.
5. `RUNBOOK_V2_TRANSFER.ps1` with `-PreflightOnly`, local allowlisted dotenv and explicit operator YES; zero external calls from CI/tests.
6. `V2_TRANSFER_RESULTS.md`: OBSERVED / INFERRED / ASSUMED; A reused source/model response counts, B source versions, actual paid call counts/errors/price, per-slot B comparison, missing critical facts, verdicts/reviewers' unique findings, library edit diffs and links to source hashes, code/tests, known limitations, no-claims and one narrow next task. If operator has not executed live calls, mark **READY_NOT_RUN**, not PASS.
7. Targeted Windows-compatible offline unit tests only (replay chronology, B-leakage, schema errors, no-template, quoted anchor validation, copied numeric values, reviewer conflict, unsupported-country inference, governing-law/forum separation, contract-family evidence, inherited context/provision overrides, no-network preflight); existing V0/V1 suite remains green. Do not reward number of tests.
8. Commit on **this task branch** and push; open a **DRAFT PR stacked on PR #14 branch** (`prototype/jev-v1-live-evidence-2026-10-13`), not `main`. Don't merge or rewrite PR #15 charter. If a PR is already open for this branch, update rather than duplicate. The owner must review new provider evidence and interpretation claims before promoting the library.

**Final Claude Code response:** actual files and commit/PR URL (only if real), source status, reused GitHub call counts, live B calls **0 or actual**, the cold/warm/raw results if live calls occurred, exact next PowerShell command, and the biggest unresolved question. Do **not** say “Experiment passed” because the code compiles.

## Stop conditions

- No real A recordings or no official archived B source → `BLOCKED`, do not fabricate replacements.
- Local modifications or raw evidence at risk of overwrite → STOP.
- No authority to make paid provider calls → only preflight/offline and operator runbook.
- Library improvement depends on leaking B into A training, hardcoding B thresholds, revision of B labels after viewing results, or LLM-created self-confirming gold answers → `INCONCLUSIVE` and disclose.
- Do not automatically begin the **later provision-to-executable-code / BI mapping experiment**. That is the next independent engineering stage, not a hidden scope expansion here.

**Execute as much of the legitimate scoped implementation as possible. Do not create a large roadmap, additional research agents or a simulated PASS.**
