# V3 masked contract-structure prediction: PROTOCOL (pre-registered, frozen before heldout)

**Status:** this protocol was frozen (see `frozen/freeze_receipt.json`) **before** any heldout document was parsed, labeled or scored. Task prompt: `Claude_Code_Sophon_V3_Masked_Contract_Structure_Prediction_2026-10-13.md`. Charter: v1.2 (PR #15).

## 0. Entry gate (CLAUDE.md)

1. **Charter section / stage:** Charter v1.2 §1 and §3 TRANSPOSE (identify applicable provisions, definitions, conditions, exceptions). This is **Stage 1 component feasibility**. It tests an *upstream learning kernel* that might later tell an interpreter where to look. It is not a product, BI-integration, reliability or adoption test.
2. **Smallest uncertainty:** whether context learned from *training-only* agreements (contract family, observed sections, the section a provision sits in, evidenced governing law) ranks **masked** section functions and provision types higher than simple frequency baselines. The comparison is against GLOBAL frequency, and above all against FAMILY-only frequency.
3. **Data:** 12 genuine public documents: 6 SEC EDGAR credit-agreement exhibits and 6 published vendor cloud SLAs (`data/source_manifest.json`). Section and provision labels come from **agent-written deterministic rules**, labeled `PROVISIONAL_AGENT_AUTHORED`, with no independent human adjudication. No semantic layer and no BI system is touched. The pilot does **not** prove interpretation accuracy, legal correctness, omission or defect detection, calibration, or downstream BI value.
4. **Architecture fit:** a structural prior is a candidate input to a TRANSPOSE "search/review here" queue. A missing high-probability structure is **SEARCH/REVIEW**, never non-compliance. No Jev call, no LLM, and no executable compiler are involved.
5. **Prior result built on:** V2 (`NO_OBSERVED_INCREMENTAL_LIBRARY_VALUE_ON_V2_PROXY`, see `../jev_library_transfer_v2/V2_POSTRUN_REVIEW.md`) had a 35/36 cold-baseline ceiling. This test was designed so the baseline has headroom, and a ceiling guard is pre-registered.

## 1. Sources and split (frozen)

- **Credit agreements (family `CREDIT_AGREEMENT`):** 8 EDGAR candidates from a full-text search (2023–2024, "syndicated" "credit agreement" "administrative agent"). Two were excluded as amendments (Ameresco, Tetra Tech). Six were kept: Lincoln National, International Paper, Motorola Solutions, Best Buy, Markel Group, Equitable Holdings. Accession, URL, filing date and SHA-256 are in the manifest. The subtype (revolver / LC facility) was not assessed.
- **Vendor SLAs (family `VENDOR_SLA`):** 10 candidate URLs were tried. Excluded: DigitalOcean (404), Linode (403), Slack and Twilio (no SLA text without client-side rendering). Six were kept: AWS EC2, Google Compute Engine, Atlassian, Cloudflare, Fastly, MongoDB Atlas. These are current pages at retrieval time, not archived snapshots. They are vendor standard terms, not signed agreements.
- **Split rule:** within each family, documents are sorted by `sha256(salt|name)` and the first 2 become HELDOUT. Google Compute Engine is forced to TRAIN because its issuer matches V2 Contract B, which this agent has already seen. **HELDOUT:** CA-MOTOROLA, CA-MARKEL, SLA-CLOUDFLARE, SLA-MONGODB. The split was computed from document names only, before any document was parsed.
- GitHub 2021 (V1/V2 Contract A) and Google Cloud Storage 2021 (V2 Contract B) are excluded entirely.
- **Rights:** raw documents stay local (scratchpad) and are never committed. The repository holds only headings, labels, hashes and short excerpts.

## 2. Structure and labels (rules frozen from TRAINING documents only)

- `extract.py`: credit agreements are parsed from the table of contents (`ARTICLE` / `SECTION n.nn`, heading text). If ARTICLE markers are missing, sections are grouped by major number and the heading is recorded as `HEADING_ABSENT`. For SLAs, the content region starts at the HTML heading that names an SLA. Units split at h1–h4 headings and at bold-only paragraphs that are not table headers. Trailing site-chrome units are dropped.
- `labels.py`:
  - **Credit-agreement section function:** first matching rule on the ARTICLE heading.
  - **Credit-agreement provision type:** first matching rule on the SECTION heading.
  - **SLA section functions:** multi-label rules over the unit's heading and text.
  - Unmatched units are `OTHER`; `[Reserved]` units are `RESERVED`. Neither label is ever a target or a candidate.
- **Governing law** counts only if the text contains an explicit "governed by … and construed …" or "construed in accordance with and governed by" clause. Otherwise it is `UNKNOWN`, and it is never inferred from where a party is based.
- **Development history:** the rules were revised several times while reading TRAINING documents only. Examples: the SERVICE_COMMITMENT and SCOPE patterns over-fired; "Indemnification" missed the indemnity rule; the International Paper law clause has a reversed word order. **Known residual training noise:** Google Compute repeated table-header bold cells become units; some SLA multi-labels are approximate.

## 3. Tasks, targets and masking (deterministic, frozen)

- **SECTION task:** one case per heldout document.
  - Two present section functions are chosen by `sha256(SALT|doc|SECTION|function)`.
  - **Every unit carrying a chosen function is masked: heading and body.** Any other function that occurred *only* in masked units also becomes hidden; these are scored as additional positives and marked `collateral_positives`.
  - The predictor sees only: the family label, the evidenced law (set to `UNKNOWN` if the choice-of-law evidence sits in a masked unit), and the functions of the visible units.
  - Candidates are the shared vocabulary minus the visible functions. Positives are the hidden functions; negatives are vocabulary functions absent from the whole document.
- **PROVISION task:** credit agreements only. SLAs have no source-level sub-structure, so the provision task is `NOT_TESTED` for SLAs.
  - Per heldout credit agreement, 2 articles with at least 4 typed provisions are chosen by hash. Within each, 2 provision types are chosen by hash, **excluding any type that also appears in another article of the same document** (leak guard against near-duplicate headings). All subsections of a chosen type are masked.
  - Candidates are the provision vocabulary minus the types visible in that article. Negatives are vocabulary types absent from that article.
- **Inputs never given to a predictor:** source URL, issuer, file name, raw text, or target headings.

## 4. Arms (identical frozen targets)

| Arm | Section task | Provision task |
|---|---|---|
| `GLOBAL_FREQ` | (docs with f + 0.5) / (N + 1) over all training docs | same, with "type anywhere in doc" |
| `FAMILY` | family frequency, backoff pseudo-count M=1 to global | family frequency of "type anywhere in doc" |
| `FAMILY_SECTION` | family docs weighted by 0.5^(observed functions they lack), backoff to FAMILY | P(type in **this section function** \| family), weighted by 0.5^(observed provisions the training section lacks), backoff to FAMILY |
| `EVIDENCED_LAW_FAMILY_SECTION` | as FAMILY_SECTION, also conditioned on law **only if** the heldout law is evidenced **and** the training docs show at least 2 distinct evidenced laws. Otherwise `LAW_EFFECT_UNTESTABLE` and identical to FAMILY_SECTION | same |
| `SEQUENCE_DIAGNOSTIC` | credit agreements only: bigram P(function at masked position \| previous visible function), backoff to family frequency. Reported, not scored for the decision. SLAs `NOT_TESTED` | – |
| `STRONG_LLM_CONTEXT` | **NOT RUN.** Optional, operator-consented, at most 8 calls. See `RUNBOOK_V3_LLM_BASELINE.md` | – |

**Soft prior, never a filter.** Every candidate keeps nonzero probability. If fewer than 50% of observed labels have support under the declared family (or section), the predictor sets a `CONTEXT_CONFLICT` flag and backs off. For sections it falls back to all-family training docs weighted by observed structure; for provisions, to the family "anywhere" distribution. Every probability reports its numerator, denominator, conditioning key, training-document weights and fallback path.

## 5. Metrics (fixed)

- **Hit@1 and hit@3 per positive target,** computed tie-aware: a candidate tied with others counts the expected fraction of the tie inside the top-k. This was adopted after the dev run showed that alphabetical tie-breaking arbitrarily decided GLOBAL and FAMILY top-3s. The change is neutral to all arms.
- **False expectations@3:** the expected number of true negatives (absent in the source) inside the top-3.
- **Brier score and log loss** over each case's candidate set (y=1 hidden-present, y=0 absent), with smoothing. With n≈16 targets these are reported raw. No calibration claim is made.
- **Negative controls (fixed subset):** the first case of each (family, task) in sorted order.
  - Section case: the family label is swapped to the other family.
  - Provision case: the section function is swapped to a wrong but plausible one (REPRESENTATIONS↔COVENANTS_COMBINED, MISCELLANEOUS↔AGENCY, CREDIT_FACILITIES↔YIELD_PROTECTION_TAXES, otherwise REPRESENTATIONS).
  - The record shows whether FAMILY_SECTION flags the conflict and backs off, and whether hits recover.

## 6. Pre-registered decision rule (`predict.decide`)

- **`CEILING_EFFECT_UNINFORMATIVE`:** GLOBAL hit@3 ≥ 90% of targets.
- **Hurdle:** FAMILY_SECTION must get at least 3 more top-3 hits than GLOBAL, with the gain spread across at least 2 heldout documents. Its false expectations@3 must be no worse than GLOBAL's, and at least 1 negative control must show an observable backoff.
- **`PREDICTIVE_SIGNAL_PROVISIONAL`:** the hurdle passes **and** FAMILY_SECTION beats FAMILY on pooled hit@3 or Brier.
- **`GLOBAL_OR_FAMILY_AS_GOOD`:** FAMILY_SECTION beats GLOBAL but not FAMILY on either measure.
- **`NO_INCREMENTAL_SECTION_SIGNAL`:** FAMILY_SECTION is not better than GLOBAL on hit@3 or Brier.
- **`INCONCLUSIVE`:** any other combination. **`BLOCKED`:** no scorable targets.
- **Also reported, separately per task:** whether *section-level* conditioning adds anything over FAMILY. On the dev run it adds **nothing** at section level; all of the pooled gain comes from the provision-in-section task. A pooled pass therefore must not be described as "section co-occurrence works".
- **GLOBAL_FREQ is a weak baseline here by construction:** it mixes two very different families. FAMILY is the meaningful comparator, and the result must say so.

## 7. Dev check (TRAINING only, leave-one-document-out; not evidence)

`python predict.py --mode dev`, on 35 LOO targets:

| Arm | hit@3 | false expectations@3 | Brier |
|---|---|---|---|
| GLOBAL | 2.54 | – | 0.184 |
| FAMILY | 15.67 | – | 0.315 |
| FAMILY_SECTION | 23.96 | 24.04 | 0.136 |

- **Section task:** FAMILY_SECTION = FAMILY exactly (15.13 / 19).
- **Provision task:** FAMILY_SECTION 8.83 / 16 vs FAMILY 0.54 / 16.

No ceiling, so the task discriminates. Equitable and Lincoln are near-identical templates, which inflates within-training agreement. The decision rule and vocabulary were **not** changed after this check; only the tie-aware scoring correction above was made.

## 8. Known limits

- 4+4 training documents. All training credit agreements cite New York law, so a law effect is untestable by construction.
- Labels are rule-based and agent-authored; the headings are the drafters' own and can mislead.
- SLA segmentation is HTML-dependent, and SLA pages are current rather than archived versions.
- Provision types are subsection *functions*, not the abstract deontic skeletons (actor, trigger, threshold …) of the four-dimension design. That finer level is **NOT_TESTED**.
- Memorization risk: credit-agreement article structure is highly conventional and appears in pretraining corpora. That matters only for the unrun LLM arm.
