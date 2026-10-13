# Sophon V3 Task — Masked contract-structure prediction (minimal test of the probabilistic funnel)

**Date:** 13 October 2026  
**Status:** owner-directed follow-on prompt, **NOT RUN**, no evidence of predictive benefit yet.  
**Repo:** `xuanhuyle/sophon`  
**Existing draft PR:** #17, branch `experiment/jev-v3-context-funnel-2026-10-13`, stacked on Jev V2 PR #16. **Update the same draft PR, do not open another.**  
**Read first:** Sophon Charter v1.2 from `origin/docs/normative-semantic-layer-charter-v1-2-2026-10-13:SOPHON_CHARTER.md` (PR #15); `CLAUDE.md`, `AGENTS.md`, V2 `prototype/jev_library_transfer_v2/README.md`, `V2_TRANSFER_RESULTS.md`, `transfer.py`, and the original V3 proposal `Claude_Code_Sophon_JEV_V3_Contextual_Funnel_Transfer_2026-10-13.md`. This focused task takes **priority** over implementing the original V3 full Jev matrix. The broader V3 task is deferred, not deleted.

## 0. Product framing and the owner's actual new hypothesis

Sophon is a shared, source-grounded **normative semantic layer**. Its first product wedge remains checking **governing contract meaning against existing BI/data semantic definitions**; non-BI agents must be able to query governing context. The current work is only an **upstream learning kernel**, not a legal engine, SaaS app, BI compiler, agent controller, legal authorization system, or product-wide go/no-go.

The owner makes a **jungle / tiger / domestic cat** analogy: knowing legal jurisdiction, contract family, section and provisions already observed changes the *prior probability* of the next type of provision. Given enough agreements, Sophon should learn (a) which sections usually occur and (b) which provision structures and dependencies are likely inside them. It should not merely categorize the clauses already observed or copy a template from another agreement.

Potential long-term aim: a **contract-structure foundation approach**, but the next experiment is deliberately **not a new foundation model**. Build the least complicated conditional-frequency / hierarchical-prior test and see whether prediction has genuine informational value.

### Four dimensions and their distinct roles

1. **Evidenced governing law:** jurisdiction/choice-of-law can be subnational; separate governing law, forum, mandatory rules, domicile, incorporation; `UNKNOWN` is acceptable. Never infer New York law because a loan is US-style, and never infer US law because a cloud vendor is US-based.
2. **Contract family:** SLA, syndicated / leveraged credit agreement, etc.; hierarchical subtype, multiple/integrated documents possible.
3. **Agreement section:** *real source path, heading and nesting* plus independently assigned semantic section function; headings can mislead and cross-section definitions/exclusions can change the meaning of a provision.
4. **Provision structure:** potentially multiple interacting abstract skeletons plus Z typed elements (actor, obligation/right, trigger, threshold, calculation, exception, deadline, remedy, conditions, definitions, dependencies).

**The central prediction questions are different from interpretation:**
- `P(section_function is present | evidenced_law_or_UNKNOWN, contract_family, other_observed_sections)` — which section functions would be reasonable to look for?
- `P(provision_skeleton is present | evidenced_law_or_UNKNOWN, contract_family, section_function, already_seen_provisions)` — which skeletons are plausible in this section?
- Optionally, `P(next_section_function | law, family, ordered_prior_sections)` — *only* if document order turns out stable enough to be informative.

A missing high-probability section means **SEARCH/REVIEW**, never "the agreement violates the law" or "the drafter omitted a mandatory clause." Negotiated omissions, unconventional placement, uninformative headings, and unexpected legal contexts must stay possible.

Unlike next-token prediction, **presence / multi-label and dependency prediction should be the default**, with sequential next-section prediction as a secondary diagnostic, because agreements can reorder their sections.

## 1. Mandatory entry gate: V2 actual run and repo safety

1. Read `git status --short --branch`, current remote/head and any local uncommitted changes; do not reset, clean, force-push, stash or discard anything. Preserve the owner's ignored `.env`, original V1 `live_runs/` and V2 `live_runs/`.
2. Establish whether the owner **actually ran V2 on Google**, using the original local `prototype/jev_library_transfer_v2/live_runs/` raw output/receipts, timestamps, hashes and V2 score. **As of drafting, V2 PR #16 reports `READY_NOT_RUN`, zero Google provider calls, although its offline implementation and tests have landed at `1151c0ff`.**
3. If V2 remains `READY_NOT_RUN`, **do not start a new paid trial or elaborate V3 implementation**. Report `BLOCKED_PENDING_V2`, the runbook path and next exact command (below) and STOP. This prevents running a new hypothesis while the preceding transfer mechanism's basic evidence has not been collected. The task prompt remains saved in PR #17 for when the gate clears.
4. V2 operator command, run in a **NEW PowerShell window outside Claude Code** with credentials locally provisioned:
   ```powershell
   cd C:\Claude\sophon\prototype\jev_library_transfer_v2
   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -Reviewer anthropic
   ```
   The runbook prints model call counts, approximate pricing and requires the user to type YES; **do not** run it inside Claude Code or call APIs for the user from this task.
5. Once V2 live evidence exists, inspect provider validity, COLD / WARM_LIBRARY / WARM_RAW / BLIND outcomes, V2 `score_condition` and corpus/protocol limitations. **Do not equate anchor+slot overlap with semantic correctness**, do not count HOLD as correct and do not rely on V1's stale committed `BLOCKED_NO_LIVE_RUN` report. Summarize V2 verdict in a short evidence note: `OBSERVED / INFERRED / ASSUMED`, genuine calls, output validity, material slots/values checked and human-adjudication status. If this review reveals a fatal input contamination or scoring blocker, log it and STOP before extending the model.

**V2 outcome does not need to show Jev wins for this predictor idea to be worth testing**: predicting expected contractual structure is a distinct falsifiable mechanism. But proceed only after V2 evidence has been honestly processed.

## 2. Prior art gate — limit to one page, don't build yet

Check authoritative primary research and existing code for **ClauseRec** (clause-type recommendation from contract context), relevant clause-sequence/contract structure prediction, **LEDGAR** clause-classification data, and any publicly accessible section-structure datasets. Record direct URLs and specifically: what predicts document-level sections versus the next clause versus generic text; whether source data has legal jurisdiction, contract family, section path, and whole-document boundaries; license and reproducibility.

**Do not spend days doing a literature sweep.** Maximum 4 substantive primary-source candidates and 1 page. Do not conclude "already solved" merely because clause recommendations exist: the question is whether *learned hierarchical contextual priors improve held-out identification and reduce omissions* in an auditable contract-to-semantics pipeline. Equally, don't claim innovation just from finding a paper gap.

If an existing public well-supported dataset and baseline directly solves the proposed masked-section task, **reuse it** and state what Sophon-specific question remains.

## 3. Dataset: genuine agreement-level train/test separation

**Do not re-use Google 2021 B as "unseen"**: the same V2 coding agent saw it before the induction. GitHub 2021 A is also already exposed. They can be development/smoke controls, never fresh heldout evidence.

Prefer small genuine, source-linked public agreements, two distinct families, with the actual documents and structural boundaries available:

- **6 publicly available syndicated / leveraged credit agreements** from lawfully accessible SEC/EDGAR-filed exhibits (aim for *evidenced* governing-law clauses where present; New York is a hypothesis, not the default).
- **6 publicly published vendor SLAs / service agreements** with stable archived versions and enough headings/structure to examine; do not treat them as signed enforceable customer contracts.

**Total target: 12 documents: 4 development/train + 2 holdout per family.** For the tiny pilot, evaluation may mask ~2 section-functions per heldout and ~2 provision-type presences per selected section: roughly **16 heldout predictive decisions** (actual count depends on structure and data availability). Preserve enough natural negative outcomes, rather than labeling every absent category an error. With this sample size, the result is an *engineering signal*, not population-level calibration.

**Source limits:** SEC accession/issuer/form/exhibit and canonical URL for credit agreements; official issuer URL/version for SLAs. Record source digest, publication/as-of dates, license/reuse status, partial-text or inaccessible references and unknown legal context. Do not reproduce LSTA model forms: LSTA is an association and drafting convention, not governing law. No confidential credit agreements, no private file ingestion, no unlicensed full-text copies in a public repository.

**Corpus capture should be bounded:** Search at most 3 credit-agreement candidates per needed credit slot and 2 SLA candidates per SLA slot; log `CORPUS_BLOCKED` if sources unavailable or not programmatically retrievable. Do not invent documents, hidden sections, laws or oracle labels. You may use a reputable existing corpus if it preserves **whole-document identity and boundaries** and terms permit use; random splitting individual clauses across train/test is prohibited.

**Freeze test agreements before training:** assign document-level train/test IDs and SHA receipts. Lock a **small common section-function/provision-skeleton vocabulary** using training data or pre-existing definitions. Label section boundaries and provision-presence with exact source passages and links to definitions/exceptions; include `OTHER/UNKNOWN` and multi-label categories. Prefer a separate human adjudicator for heldout semantic labels; otherwise label explicitly `PROVISIONAL_AGENT_AUTHORED` and limit claims. No later edits to heldout labels, taxonomy or split to engineer a win. Never feed heldout text into the induction process, candidate prior counts or experimental prompt recipes.

**IMPORTANT distinction:** section headings are observable evidence to extract, but a masked section's heading/text must not remain exposed to a predictor asked to predict it; mask the target **heading and body**, not just its label. Prevent file path/URL/issuer metadata from inadvertently encoding the target. Retain only allowed prior sections and document-level facts. For within-section provision prediction, mask the target provision and any near-duplicate text/heading elsewhere that would leak its answer; preserve explicitly permissible surrounding context equally across arms.

## 4. Simplest predictive engine: counts before neural training

Start with **transparent conditional frequencies / hierarchical smoothing** over training agreement records, not a Jev model finetune, vector DB, Bayesian-network mega-engine, deep learning or synthetic data generator.

Required benchmark arms, same frozen heldout targets:
- **GLOBAL_FREQ:** global rate of a section-function or provision type (multi-label presence), ignoring family.
- **FAMILY:** conditional rate given contract family; use smoothing/backoff to global.
- **FAMILY_SECTION:** for provision predictions only, condition on contract family and the **observable** section-function; for section-set predictions, use family + observable already seen sections. This is the first contextual funnel step.
- **EVIDENCED_LAW_FAMILY_SECTION:** additionally incorporate governing law **only if training support exists and law is evidenced on heldout**; otherwise explicit `LAW_EFFECT_UNTESTABLE` and fall back rather than inventing a probability.
- **SEQUENCE_DIAGNOSTIC:** optionally predict next section from prior observed section sequence, separately from bag-of-section prediction; if order data is inadequate, report `NOT_TESTED` without failing the primary experiment.
- **STRONG_LLM_CONTEXT** (optional, paid phase only after operator consent): a fixed general LLM asked to predict the same heldout targets using the same observable document context and a comparably sized list of allowed category definitions; **never** give it the masked text, source URL, or target labels. A retrieval-only reference from training agreements, using exactly the same available training corpus, is a valuable simpler comparator if trivially available.

**Keep the context hierarchy a SOFT PRIOR, not a filter:** always assign nonzero probability/mass or explicit `OTHER/UNKNOWN` to unobserved valid structures; a `law`/family/section label with weak, missing or conflicting evidence must back off, not force decisions. A provision outside the expected category family is allowed. Never treat the absence of a predicted common provision as legal noncompliance.

**Prediction outputs** should include ranked top-k possibilities and clear evidence: numerator, denominator, conditioning key, source document IDs, model version, uncertainty, and fallback path. Do NOT turn counts from 4 training documents/family into confident calibrated accuracy claims. No magic hardcoded finance-specific conditional associations: all learned frequency tables must be automatically computed **from training-only documents**.

## 5. Scoring and experiment gates

Pre-register metrics *before* looking at heldout outcomes:
1. Section-function **presence / retrieval**: top-1/top-3 hit rate on true masked section types and precision / false-alarm burden on suggested extra section types; macro summary by document family and heldout doc.
2. Provision-structure **multi-label presence**: top-1/top-3 hit rate and ranking quality, including legitimate absence of common provision types. Don't force one exclusive primary type.
3. Where enough decisions exist, **Brier score or log loss** on binary presence events for a fixed candidate universe, with smoothing and explicit abstention. With ~16 targets, report raw per-case scores and extreme uncertainty; avoid ungrounded calibration claims.
4. **Negative-control context test:** on a small fixed subset, replace the provided section family/function metadata with an explicit **wrong but plausible** label and check whether prior predictions become overconfident/irrecoverable; retain target text fully masked. This tests robustness of the *predictor*, not Jev's actual interpretation.
5. Report costs, human labeling time, missing coverage, false expectations, wrong-law inferences, unknown-context backoffs and errors from incorrect agreement-section segmentation.

**Provisional hurdle:** at least **3 additional correct top-3 masked targets across ≥2 different heldout documents** for FAMILY_SECTION over GLOBAL_FREQ, **without a substantial explosion in false expectations**, and at least one observable sensible backoff from incorrect/missing upstream metadata. This is an *illustrative feasibility gate*, not validated predictive performance. It must also compete reasonably with FAMILY-only: if family already explains the gain and sections add none, say so. If all laws are the same, **do not claim a law-layer benefit**. If no category distribution is meaningfully supported by the tiny training sample, record `INSUFFICIENT_DATA`, not a fabricated model success.

A positive result means **context priors contain some useful predictive signal**. It does NOT establish Jev extraction accuracy, learned transfer to interpretation, legal authority, missing-clause defect detection, independent model calibration, or value for downstream BI execution.

**Only after** the prediction result: if the signal is encouraging, propose but **do not silently run** the next causal link:
`masked-section prediction → Jev candidate-ranking / omission search → independently verified better interpretation`.
That later Jev test, and contractual semantics → executable BI/agent transposition, remain separate gates.

## 6. Execution instructions / budget

- One primary Claude Code agent; no swarms. Reuse the four-dimensional source representation and schema from V2, but don't mutate V2 data/code/frozen checklists.
- First implement an **OFFLINE, STANDARD-LIBRARY** dataset parser/freeze, conditional frequency estimator, backoff, heldout masking, scoring/replay and targeted tests in an isolated folder `prototype/contract_structure_prediction_v3/`. If V2 remains `READY_NOT_RUN`, **stop before implementing**.
- Keep the experiment around a few hundred lines where practical. **No foundation-model pretraining, new DSL, database, multi-agent architecture, UI or BI adapter**. If corpus extraction becomes the dominant engineering task or rights/source access fail, report a precise blocker; don't grow the system to accommodate scraping.
- **Zero paid provider calls during Claude Code.** Optional later LLM baseline: maximum **8 logical calls** total, **0 without explicit operator authorization**; prepare a new PowerShell runbook with `-PreflightOnly`, truthful estimate and typed YES. Jev is NOT required for the pure structural prior test. Keep the original V2 live cap completely separate from this budget.
- No vendor API keys or full copyrighted documents committed to GitHub. `.env` and raw responses locally ignored; include SHA receipts, extracted metadata, source anchors and short lawful excerpts where permitted. Record source licensing and model memorization risk.
- **Tests must run without network and provider calls**. Do not report passing plumbing tests as evidence for prediction.
- Decide `PREDICTIVE_SIGNAL_PROVISIONAL`, `NO_INCREMENTAL_SECTION_SIGNAL`, `GLOBAL_OR_FAMILY_AS_GOOD`, `INCONCLUSIVE`, or `BLOCKED` based on factual per-case output. No premature global no-go on Sophon.

## 7. Deliverables and stop conditions

If V2 is still `READY_NOT_RUN`: create a small `V3_ENTRY_GATE.md` or write a precise blocker in your final response, showing current head and exact V2 runbook command. **Do not implement V3 on guesses.**

Once V2 actual outputs have been reviewed and the corpus is available:
1. `prototype/contract_structure_prediction_v3/PROTOCOL.md` — source selection, frozen train/test split, target definitions, masked inputs, baselines, pre-registered outcomes, known limits.
2. Small source manifests with refs/hashes, train-only learned frequency/prior library and heldout annotation references, with `UNKNOWN` and cross-section dependency handling.
3. Minimal deterministic Python predictor, scorer and tests, with exact offline commands and baseline comparisons.
4. `RESULTS.md` with per-heldout-packet top-k predictions, proper presence/absence counts, honest scoring, human-reviewed vs provisional answer statuses, contradiction/backoff probes and costs.
5. Optional future LLM baseline runbook (not run without explicit consent), versioned prompts and local evidence storage.
6. Commit and push to **the existing V3 draft PR #17 branch**, update its description and provide PR link. Do not create another PR, merge anything, edit charter, overwrite V2 original files or silently revise V2 results.

**Final Claude Code response:** exact current V2 status, genuine V2 live call counts, what was actually implemented/scored and what was not, files/commit/PR, blockers, next PowerShell command, and one concrete criterion for moving to Jev-based interpretation.

**Do not stop at planning if prerequisites are satisfied. Conversely, do not fabricate a predictive PASS or proceed when V2's live evidence is absent.**
