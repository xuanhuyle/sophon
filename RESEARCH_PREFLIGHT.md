# Research preflight — fixed-model provision classification with cumulative library memory

**Date:** 2026-10-14. **Status: BLOCKED for a credible classification-error reduction claim on the existing V1/V2 evidence; READY to specify a narrow offline relational/headroom check.** No new model calls, provider expenses or classifier experiments were performed in this review.

## Research target — scope and success

Determine whether a **fixed, inexpensive classifier** becomes more reliable at categorizing actual contractual provisions' intrinsic normative functions and modifiers **because a versioned, source-linked library accumulates narrow expertise** across successive agreements. Desired benefit is fewer wrong or confidently unsupported classifications, without routine legal experts in the production loop. The claim is about *incremental competence from retained knowledge*, **NOT outperforming stronger pretrained LLMs**, buying a bigger model, increasing context indiscriminately, or predicting the next heading.

Jev and the adversarial/backward reviewer topology are optional engineering means, not mandatory product requirements. Later analysis of code-wise executability remains out of scope. This upstream task is a research component of the normative semantic layer, not a replacement for Sophon's broader charter.

## Evidence examined (historical code, not in main)

Source ref: [PR #17 / `experiment/jev-v3-context-funnel-2026-10-13`](https://github.com/xuanhuyle/sophon/tree/experiment/jev-v3-context-funnel-2026-10-13) at `b9d698c`.

| Artifact | Observed | Limit |
|---|---|---|
| `prototype/jev_clause_router_v0/prototype.py`, frozen `review_matrix.json`, `live_runs/compare_20261013T094923Z.md` | Six primary classes + five modifiers; Jev, adversarial and backward calls on V1; provisional 5/5 primary-category matches on each tiny corpus vs the author-written matrix | Matrix is not an independent semantic oracle. Real GitHub SLA has only five excerpt packets; the other five are fictional. A correct dominant label may conceal multiple normative functions. No credible class-error headroom established. |
| `prototype/jev_library_transfer_v2/transfer.py`, `library_v0.json`, `library_v1.json`, `library_events.json` | `library_v0`: six hand-initialized broad categories. `library_v1`: same six plus **three provisional structures**, each from a **single GitHub SLA excerpt** (G1, G2, G4). G3 produced ABSTAIN. V2 used lab-authored detectors and source/provider receipts to induce templates. | This is **one induction event from one authentic SLA**, not repeated successful contract-by-contract self-correction. The library includes three examples, not demonstrated specialist expertise. |
| V2 `google_storage_sla_20210624.json`, `reference_checklist_b.json`, `V2_POSTRUN_REVIEW.md` | Three held-out **bundled** Google packets B1–B3; 30 actual provider calls in recorded V2 run. Source/recording checks matched; B scoring cold 35/36, warm library 34/36, raw examples 36/36; all pipeline dispositions HOLD. | **Metric is source-quoted slot/fact extraction**, not intrinsic function-classification error. Baseline 35/36 cannot meet original ≥20pp improvement rule. Warm reviewer identified some facts under `omitted_conditions`, not scoreable slots; changed template assignment may be defensible. V2 raw Google responses were git-ignored and cannot be reproduced merely from committed receipt hashes. |
| V2 `jev_request_v2` and `_criteria` | **Cold and warm Jev Choice option sets differ** (warm adds specialist template names). Library context is also passed to reviewer prompts. | A different chosen template cannot be interpreted as a corrected **fixed-label intrinsic function**; the intervention conflates changed candidate vocabulary, retrieval and reviewer conditioning. |
| V3/V4 statistical predictors | Separate tasks with headings/regex proxy predictions, V4 with zero Jev/reviewer calls | Neither addresses intrinsic normative classification or cumulative semantic error reduction. |

**Structural unit defect visible in authentic Google packet text:** B1 contains several named definitions, B2 contains a service-level commitment plus multiple credit calculation definitions/schedules, and B3 combines a claim obligation, forfeiture condition, credit cap and exclusions. A single mandatory primary class for each large packet would discard meaningful normative distinctions. **First compare extracted, evidence-anchored normative spans/functions; only then optionally summarize the provision.**

## Independent engineering recommendation

**Do not build or run the proposed three-reviewer architecture.** A strong LLM is *not* the relevant comparator and should not become the headline objective. A single fixed cheap classifier with source-grounded structure (potentially Jev if it proves economical) is enough for the first causal library test. Complementary reviewer calls are only worth introducing if they demonstrably catch additional source-verifiable errors without excessive false HOLD cases.

The library is a **versioned, provisional and revocable hypothesis store**, not an authority. An error cannot legitimately become a learned truth because multiple similar LLM calls agree. The ability to reject conflicting or inapplicable memories matters as much as retaining them.

### The smallest scientifically relevant comparison

Freeze the **same model/version, temperature or sampling settings, contract packet boundaries, normative-function label inventory, schema, source access, prompt rules, abstention mechanism and call budget** in every arm. Intervention is only the memory:

- **FROZEN:** a fixed bootstrap library (or no prior learned skeletons).
- **CUMULATIVE:** the same library after source-anchored prior-agreement skeleton additions/revisions, with exact timestamps, provenance, applicability and counterexamples.
- **RAW-EXAMPLE diagnostic, optional:** same base model with previously seen source excerpts but no induced structure. This separates useful generalization from merely retrieving old text.

**No strong-model head-to-head success criterion.** The primary quantity is whether CUMULATIVE avoids classification mistakes or correctly abstains where FROZEN fails, *minus* new mistakes induced by false/inapplicable memories; report both directions per provision and per document (no statistical claims from a handful of packets). Cost/latency matters because the purpose is reusable narrow expertise at a stable model price point.

**Fixed target:** evidence-anchored normative-function instances and modifiers; compound functions allowed. Template IDs are library metadata, *not* target classes. A system can classify 'DEFINITION' correctly while missing an adjacent 'OBLIGATION'. Missing source, unsupported interpretation and contradictions must remain explicit.

### What can be tested without a human legal expert per clause

- Controlled, clearly labeled **synthetic edits of authentic clauses** can supply a *relational* oracle: adding a clean prohibition, replacing a permission with a prohibition, inserting a literal exception, or changing a named reference must trigger a specified **difference in tagged functions/modifiers** or an explicit unsupported/ambiguous result. Keep whole-contract context and check the editing preconditions; some 'may/must' substitutions alter multiple rights/duties or produce contradiction, so do not blindly call them ground truth.
- Source-span anchoring, input perturbation consistency, no-target-in-memory chronological partition, withheld family/contract details, false analogies, refusal to copy literal thresholds and rollback after contradicted memories provide automated **falsification tests**, not a guarantee of legal correctness.
- Record separately: invariant violated / unsupported evidence / overconfident result / justified abstention. LLM self-voting and matching quotes are not independent labels.

**Important limit:** synthetic relational tests can demonstrate robustness to well-specified changes; they **cannot** yield absolute accuracy on unmodified real contracts. Existing V1/V2 artifacts have no independently validated, non-ceiling normative-function truth set. Without such a set, the broader claim 'library learning reduces real classification error' remains **BLOCKED**.

## Readiness decision and smallest next delta

**Verdict: `BLOCKED_BY_NO_CLASSIFICATION_ORACLE_AND_HEADROOM` for a credible live cumulative-accuracy pilot using the present V1/V2 artifacts.**

*(Superseded by the Independent challenge below: do not build metamorphic pairs first; screen cold headroom first.)* **REVISE, do not STOP Sophon:** the smallest next **offline** increment, if implementation is authorized, is to freeze a handful of source-linked, provenance-marked **metamorphic function/exception pairs** derived from existing authentic SLA packets, with only the *known required classification change* evaluated. Start by inspecting B1/B2/B3 compound segmentation; add one deliberately inapplicable template transfer. An independent checker can verify edit locations, target relations, source hashes and memory exclusion without provider calls. If edits are ambiguous, reject the case rather than invent an oracle. Claude Code should first challenge whether an available existing fixture/test suffices; do not build a new benchmark platform.

After that independent offline check, decide whether one **fixed-model** minimal call-based pilot can expose headroom. **No provider run is authorized by this preflight.** Further authentic unseen contracts or a small independently validated reference may ultimately be necessary to measure real-world absolute accuracy; routine human expert review is not presumed part of production.

## Observed vs inferred vs assumed

- **Observed in committed repository:** V1/V2 code, source excerpts, template counts, reference labels/provenance, post-run reported V2 metrics, check/receipt metadata. Not a new independent replay; the original V2 raw live files are not committed.
- **Inferred engineering concerns:** compound normative-function loss, correlated-review risk, library feedback contamination, changed taxonomy confounding. These have specific source/code support but are not newly measured failure rates.
- **Assumed until tested:** that a model with fixed capability can learn narrower contractual patterns from evidence-linked, correctable structured memory and improve later classifications. Not yet demonstrated.

**KEEP the owner-defined research objective. REVISE the validation strategy. NO-GO on adding reviewer agents or claiming automated legal correctness at present.**

---

## Independent challenge — Claude Code, 2026-10-14

**Verdict: the `BLOCKED` result above holds, but for stronger reasons than the ones given. REVISE the smallest next step: do not build metamorphic pairs first.** No provider calls were made. Every number below is re-derived offline from PR #17 head `b9d698c` by [`audit/classification_headroom_2026-10-14/headroom_audit.py`](audit/classification_headroom_2026-10-14/headroom_audit.py). The script exits non-zero if any finding stops holding. Its output is in [`headroom_audit_output.json`](audit/classification_headroom_2026-10-14/headroom_audit_output.json). The script reads the historical files through `git show`/`git archive` and builds the V2 Jev requests with the historical `transfer.py`.

The fixed inexpensive model in this evidence is **Jev (`jev-1.13.0`)**: about 280 ms per call, about 1.1k input tokens, and about $0.001 for 9 calls. The `claude-opus-5-5` calls were the reviewers, not the classifier.

### Preflight claims re-checked against source

| Preflight claim | Status |
|---|---|
| V1 has six primary labels and five modifiers. Jev's primary label is in the matrix's acceptable list for 5/5 packets in each corpus. | **Confirmed**: 10/10, all `ACTUAL_PROVIDER`, `jev-1.13.0`. |
| `library_v1` adds three single-excerpt templates from G1, G2 and G4. G3 abstained. | **Confirmed** (`library_events.json`). G5 was excluded by protocol. |
| Cold and warm Jev option sets differ. | **Confirmed** behaviourally: COLD has 7 options (6 labels plus `NO_TEMPLATE`), WARM has 10. |
| V2 raw provider outputs are not in Git. | **Confirmed**: `.gitignore` at the ref excludes `prototype/jev_library_transfer_v2/live_runs/`, and the path is absent at the ref. **UNAVAILABLE** here, so nothing V2-specific was replayed. |
| V2 scored 35/34/36 of 36 on slot extraction. | Recorded in `V2_POSTRUN_REVIEW.md`; cannot be re-derived without the raw files. |

### Corrections, each verified in the code and recordings

1. **V2 never tested whether the same cheap model learns from the library.** In `jev_request_v2`, the WARM Jev request carries `state = {clause, context}` and option definitions of at most 400 characters (`_criteria`). It carries **none** of the library's positive-example quotes, structural rules or counterexamples (audit check). That source-anchored content went only to the `claude-opus-5-5` reviewer prompts (`reviewer_prompt_v2`, `memory`). V2 is therefore not evidence, in either direction, about cumulative expertise in the fixed cheap classifier. The preflight's "library context is also passed to reviewer prompts" understates this: the library content went *only* to the expensive model.
2. **The V1 ceiling is partly a property of the scoring.**
   - The matrix accepts two primary labels for G1, G3 and C5.
   - Under the V1 criteria, Jev answered "yes" (p ≥ 0.5) to **42/50** modifier questions. CONDITION, DEADLINE and CROSS_REFERENCE fired on 9/10 packets each.
   - The criteria are near-tautological for SLA text. Any "timing condition" counts as DEADLINE, and any capitalized defined term counts as CROSS_REFERENCE.
   - "0 missed required modifiers" is therefore uninformative. Specificity cannot be scored without an oracle.
3. **The library absorbed the only observed same-model instability instead of resolving it.**
   - G1 is the only option-order flip: PERMISSION_RIGHT 0.56 forward, DEFINITION 0.58 reversed.
   - Template induction takes its category readings from Jev's own output (`transfer.py` around lines 593 and 625–631). `TIERED_SERVICE_CREDIT_SCHEDULE` therefore reads as **both** `DEFINITION` and `PERMISSION_RIGHT`.
   - Mapped back to the fixed taxonomy, the WARM B2 routing (TIERED, p = 0.96) includes the COLD B2 answer (`DEFINITION`, as reported). The only observed V2 routing change is a **fixed-label no-op**, and it was learned from the model's own predictions.
4. **Observed headroom on the fixed six-label question is two compound packets, and neither shows a demonstrable error.**
   - 11 cheap-model answers are known: V1 ×10 recorded, plus V2 COLD B2 as reported in `V2_POSTRUN_REVIEW.md`. COLD B1 and B3 labels appear in no committed file.
   - Only G1 (order flip) and B2 (`DEFINITION`, p = 0.63) are unstable. C5 (p = 0.85) and G5 (p = 0.80) are lower but stable under reversal. Both are tiered-credit compounds, where one "dominant" label is ill-posed.
   - The one plausible miss is B2. It opens with a service-level commitment ("the Covered Service will provide a Monthly Uptime Percentage … >= 99.95%"), so an OBLIGATION is co-present. This is agent judgement, not an independent label.
   - `library_v1` could not have fixed it either: GitHub's commitment sentence appears only inside G1's `context`, never as a packet, so no skeleton for it exists.
5. **Metamorphic pairs as the next step test the wrong thing.**
   - Edits such as may → may not or an added exception test the base model's sensitivity to edits, not memory. Jev already returns p = 1.0 on the clean modal and definitional cases (C1, C2, C4, G2, G3).
   - A pair isolates the library effect only if the correct answer depends on knowledge that exists only in prior-contract memory, and no existing packet has that property.
   - Building them now adds synthetic text without testing the goal.

### Feasibility answer

**A small, source-grounded classification-error test is not feasible on the existing V1/V2 material.** Three reasons:

- On the fixed question, the cheap model shows no demonstrable errors, only two taxonomy-compound ambiguities.
- No independent oracle exists.
- The V2 harness would first need an interface change before the cheap model could receive library knowledge at all.

No offline code can remove these blockers.

A later valid test, frozen here as a design and **not authorized**, needs all of the following:

- **Same question in every arm.** The V1 six-label and modifier question bytes are identical, with the same `jev-1.13.0` and the same order-reversal check.
- **The library in one field only.** The library goes into one extra Jev `state` field: rules, positive examples and counterexamples, each with source hashes. FROZEN gets that same field with the bootstrap library, and the field's content is the only delta.
- **Compound targets.** The per-packet target is a set of co-present functions, not one dominant label.
- **Errors counted in both directions.** Errors avoided and errors newly introduced are reported separately per packet.
- **Clean chronology.** No target text appears in memory.

### One recommendation

**Find cold headroom before doing any library work.** With owner approval, run one COLD screen at a cost of a few cents:

- **Fixed inputs:** the same `jev-1.13.0` and the byte-identical V1 question set, over at least 20 held-out authentic SLA provisions from another vendor, split into single normative sentences.
- **Measures:** count order flips and primary p < 0.9. This needs no oracle.
- **Pre-registered rule:** if fewer than 5 packets are unstable, **STOP** the library-accuracy line for this taxonomy on SLAs, because there is nothing to learn. Otherwise, obtain a bounded one-time independent label for only the flagged packets, then run FROZEN vs CUMULATIVE as specified above.

No stronger model, no reviewers and no new architecture.

**KEEP** the `BLOCKED` verdict. **REVISE** the next step to: headroom screen → interface fix → comparison. **STOP** any further code toward a library pilot on the V1/V2 material.
