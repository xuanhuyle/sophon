# V4 Phase 0: can cumulative contractual learning be tested credibly?

**Date:** 2026-10-14. **Branch:** `experiment/jev-v4-sequential-provision-learning-2026-10-13` (draft PR #18). **Provider calls: 0.** No scored experiment was run, no learner was built, and no held-out label was read.

**Authority read:** `origin/main` at `77c8ba1`: `SOPHON_CHARTER.md` v1.2, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md`, `AGENTS.md`, `CLAUDE.md`. PR #17 head `b9d698c`, read in an isolated worktree. The V4 spec on this branch: `Claude_Code_Sophon_V4_Sequential_Contract_Learning_2026-10-13.md`.

## Decision: `ONE_MINIMAL_TEST`, conditional on a protocol freeze

There is a cheaply reachable, **independently labelled**, single-family corpus with enough distinct agreements, real headroom and a filing-date order. It is the EDGAR subset of **ContractNLI** (NDAs).

It supports one zero-call, deterministic test with these properties:
- It can fail.
- It separates conditional structural knowledge from a growing base-rate count.
- Its oracle was not produced by this agent, an LLM, or a heading rule.

A scored run still needs a new owner decision, per the Phase-0 prompt. This report does not launch one.

### Why this, and not the original V4 spec

I deviate from the original V4 spec in three places:

1. **No new agent-authored labels.** The spec relied on "provisional agent annotation plus later human adjudication". V3 shows where that leads: 78 review units prepared, none adjudicated. Choosing a corpus that already carries third-party labels removes the adjudication bottleneck. It does not remove the need to state what those labels establish.
2. **No two-contract seed.** The spec's `FROZEN_SEED` froze the library after 2 seed contracts. Against 17 roughly balanced targets, any updating counter beats a 2-document seed, so that comparison cannot fail and proves nothing. The frozen control here is frozen after a **36-document dev slice**. The experience-gain question then becomes whether 180 more contracts add anything beyond a reasonable start.
3. **No separate "structured library" arm.** On a presence/entailment oracle, a source-anchored library and a conditional count table with the same anchors produce **identical predictions**. Anchors improve AUDIT, not accuracy; this is the PR #3 `STOP_KERNEL` lesson. So the mechanism ablation that can be tested fairly is **conditional (uses the current contract's other reviewed provisions) vs marginal (same history, no conditioning) vs precedent copying**. Provenance is checked as an audit property, not scored as a learning gain.

## 1. Measured capability: one target

**Carve-out omission check on an unfamiliar NDA.** Some of the NDA's provisions are assumed already reviewed. Before the reviewer reads the confidentiality-exception provisions, Sophon predicts the status of two standard carve-outs from the definition of Confidential Information:

| Key | ContractNLI hypothesis (verbatim short description) | Why it matters |
|---|---|---|
| `nda-12` | Permissible development of similar information | Without it, a recipient that builds similar products is exposed. |
| `nda-13` | Permissible acquirement of similar information | Without it, information lawfully obtained from third parties is captured. |

- **Prediction:** a distribution over `Entailment / Contradiction / NotMentioned` for each target, with the precedent IDs behind it.
- **Use:** a provisional review hypothesis that drives a "check for / flag missing carve-out" item. It is never an applicable obligation.
- **Not a heading test:** the label concerns an exception *inside* the confidentiality definition, not the presence of a heading.

## 2. Sources checked and what each oracle establishes

| Source (checked 2026-10-14) | Identifier / hash | Oracle? | Verdict for V4 |
|---|---|---|---|
| **ContractNLI** (Koreeda & Manning, Findings of EMNLP 2021) | `github.com/stanfordnlp/contract-nli` gh-pages `eced6528`; `resources/contract-nli.zip` sha256 `e03fc77bbf8b53e2976a250e81d8a294bc3d5e5fb014521e477dee9340d6287b`; `train.json` `dbceb356cd6203b35b27be94a5fa85e499a81c34c42c89ad53060b39f0257ba5`, `dev.json` `310af7d661d2ab50ee3700169cef524c75f39fb296bbf5a515c229eb0f42e68e`, `test.json` `460267b56052a2dc5aead98eb35eadef9e6734d5723d37b4a9790e410f812387` | **Yes, third-party.** 607 NDAs × 17 fixed hypotheses, 3-way label plus evidence spans; one annotation set per document (observed). Licence CC BY 4.0 plus Hitachi America terms (read). | **PRIMARY.** |
| **CUAD v1** (Atticus Project, NeurIPS 2021) | `github.com/TheAtticusProject/cuad` `67faa0e6`; `data.zip` sha256 `f8161d18bea4e9c05e78fa6dda61c19c846fb8087ea969c172753bc2f45b999a` | **Yes, expert.** 510 EDGAR contracts × 41 categories. Described as law-student annotators led by lawyers, with multiple review passes (secondary source). | **Replication candidate.** Carve-out pairs: Cap on Liability → *Uncapped Liability*; Non-Compete/Exclusivity/No-Solicit → *Competitive Restriction Exception*. Not primary: 25+ mixed contract types (largest about 31 docs), and only 302/510 titles carry a date (64 of them in 2020). |
| **MAUD** (Atticus Project, 2023) | `github.com/TheAtticusProject/maud` `46403160`; `data.zip` sha256 `75af5a33d038e9254864f043da38072490ffe11e8488d58d0a2dd39c8f554519` | **Yes, lawyer-annotated.** 153 merger agreements, 92 deal-point questions including MAE carve-outs. | **Later within-provision replication only.** All deals come from one ABA 2021 study window, so there is no usable chronology; big-law templates are shared; it is far from the solo-founder stream. |
| V3 corpus (EDGAR credit agreements, vendor SLAs) | `prototype/contract_structure_prediction_v3/data/source_manifest.json` @ `b9d698c` | **No.** Labels are agent-authored rules; the 78-unit adjudication was never done. | **Rejected for V4 scoring.** The documents are contaminated (already seen by this agent) and there are only about 8 per family. |
| LEDGAR | (V3 `PRIOR_ART.md`) | **No.** Labels are derived from headings. | Disqualified: the prompt rules out heading-as-label. |
| Material Contracts Corpus | (V3 `PRIOR_ART.md`) | **No labels.** | Source of text only. |

**What the ContractNLI label establishes:** that a third-party annotation judged the hypothesis entailed, contradicted or not mentioned, citing specific spans. It does **not** establish:
- legal effect, enforceability or applicability;
- inter-annotator agreement (not verified);
- expert adjudication by us.

The first author's Hitachi blog reports that annotation was done "through consultation with attorneys and paralegals". That is secondhand. The paper's appendix A.1 could not be read because `arxiv.org` and `aclanthology.org` were unreachable from this container.

## 3. Test geometry (structural screen, plus label counts on the dev slice only)

- **Chronology:** 232/607 ContractNLI documents are SEC files whose name carries an EDGAR accession. The accession year is the **filing year**, not the signing or effective date. Order is by (accession year, accession, file name). This is experimental ingestion order, not legal effective order.
- **Duplicates and leakage:**
  - One document per CIK (10 dropped).
  - Greedy 8-word-shingle Jaccard ≥ 0.8 on the first 4,000 words (6 dropped).
  - That leaves **216 distinct-issuer NDAs**.
  - The 375 undated `search-pdf` NDAs are excluded from the sequence.
- **Split, fixed before any later label was read:**
  - **DEV slice:** filing year ≤ 1998, **36 documents**. Used for design, headroom checks and the frozen control. Never scored.
  - **SEQUENCE:** **180 documents** from 1999 to 2019 (15/25/11/13 in 1999–2002, then 1–12 per year), giving **360 primary targets**.
  - Train/dev/test membership in the original release is ignored.
- **Headroom (DEV only, E/C/N):**
  - `nda-12`: 16/0/20.
  - `nda-13`: 21/0/15.
  - Neither is near ceiling, so a marginal predictor has real room to be beaten.
  - Near-ceiling hypotheses are excluded from the diagnostic set: `nda-4` (32/36 E) and `nda-11` (35/36 N).
- **Masking:** the learner sees only the reference determinations of the *other* reviewed hypotheses. The masking groups were fixed from hypothesis text plus evidence-span overlap measured on DEV only.
  - nda-12/13 share spans in 14/36 DEV docs, so the whole group `{nda-12, nda-13}` is hidden.
  - nda-2 and nda-3 border the confidentiality definition (DEV overlaps 1–3: 10 docs, 2–3: 7, 1–2: 6), so `{nda-1, nda-2, nda-3}` is hidden too.
  - Visible context: nda-4, 5, 7, 8, 10, 11, 15, 16, 17, 18, 19, 20.
  - At run time, any target whose evidence spans overlap a *visible* hypothesis's spans is set INVALID for primary scoring. This rule is mechanical and applies to every arm.
- **Sealed update order, per contract k:**
  1. Hash library `L(k-1)`.
  2. Emit predictions for both targets with precedent IDs, and append them to a hash-chained prediction log.
  3. Only then read the reference.
  4. Score.
  5. Append one update event (doc ID, accession, evidence span IDs, known-at = step k) to produce `L(k)`.

  No event is ever rewritten. Both targets in a contract are sealed before either is revealed.
- **Contamination:** this agent has now seen the 17 hypothesis texts, DEV labels and dataset structure. It has **not** seen any SEQUENCE label. The learner has no pretrained knowledge, because it is counts only. ContractNLI is a public benchmark and probably sits in LLM pretraining, which matters only for a future LLM arm.

## 4. Arms and competing explanations

All arms get the same current-contract context and the same targets.

| Arm | History | Representation | Explanation it isolates |
|---|---|---|---|
| `FROZEN_DEV` | DEV only, never updated | conditional (as below) | Is there any experience gain? |
| `CUMULATIVE_CONDITIONAL` (learner) | DEV + every earlier sealed contract | similarity-weighted conditional frequency over visible determinations, with backoff to marginal; every number traceable to precedent IDs | — |
| `CUMULATIVE_MARGINAL` | same history | target base rate only | (a) growing counts / base-rate drift |
| `CUMULATIVE_PRECEDENT_kNN` | same history | label of the k nearest prior contracts (Hamming distance on visible context, k fixed on DEV) | (b) copying old precedents |
| `SHUFFLED_CONTEXT` (negative control) | same as learner | learner fed the visible context of a different, hash-chosen contract | (e)/(f) artifacts: gains that do not need the current contract's own evidence |

How the remaining explanations are handled:
- **(c) Memorized conventions:** there is no LLM in the loop, and no hand-written priors are allowed. All parameters are chosen on DEV leave-one-out only.
- **(d) Target leakage:** handled by group masking, the span-overlap invalidation rule, whole-document order, and the CIK/near-duplicate filter.
- **(e) Metric artifacts:** labels are used exactly as released; a proper scoring rule is used; results are reported per document, not only pooled.
- **(f) More context:** identical context across all arms.

**Hard negative (pre-declared subgroup, not selected now):** targets where `CUMULATIVE_CONDITIONAL` gives P(Entailment) ≥ 0.8 but the reference is NotMentioned or Contradiction. This is the "confident false-safe" rate, reported per arm.

**Novel case:** a `Contradiction` for nda-12 or nda-13, which never occurs in DEV. If one appears in SEQUENCE:
- the prediction must have kept non-zero mass on it (smoothing);
- it is logged as `NOVEL_OUTCOME`;
- the class enters the library as a counterexample with its span IDs.

If none appears, report `NOT_OBSERVED`. Do not search for one.

**Revision and persistence:** run a separate, clearly `LAB_INJECTED` diagnostic. Start from DEV plus one false high-weight claim (e.g. 20 pseudo-observations "nda-12 always Entailment when nda-8 Entailment") and report how many contracts pass before its predictions come within 0.02 Brier of the clean run.

With counts, a mistaken inference persists in proportion to its weight, because there is no retraction mechanism. That is an expected property to measure, not a feature to claim.

## 5. Pre-declared outcome classes

All of these must be frozen before the run.
- **Primary metric:** per-document mean 3-class Brier over the two targets.
- **Comparison method:** paired document bootstrap (10,000 resamples, fixed seed) for the 95% CI of the per-document difference.

| Verdict | Condition |
|---|---|
| `CONDITIONAL_CUMULATIVE_SIGNAL_EXTERNALLY_LABELLED` | CONDITIONAL beats both MARGINAL and FROZEN_DEV with the CI excluding 0. SHUFFLED_CONTEXT does **not** beat MARGINAL. No more than 50% of the gain comes from any single filing year. Integrity checks pass. A qualifier is added if kNN ≥ CONDITIONAL: `PRECEDENT_EQUIVALENT`, meaning nothing beyond copying precedents. |
| `BASE_RATE_EXPERIENCE_ONLY` | MARGINAL (cumulative) beats FROZEN_DEV, but CONDITIONAL does not beat MARGINAL. Accumulation then tracks frequencies, not structure. |
| `NO_OBSERVED_CUMULATIVE_GAIN` | No cumulative arm beats FROZEN_DEV. |
| `INVALID` | Any of: a sealed-order or hash-chain violation; >20% of targets invalidated by span overlap; SHUFFLED_CONTEXT beats MARGINAL with the CI excluding 0. |
| `BLOCKED` | Dataset bytes no longer match the hashes above. |

Even the best outcome remains narrow: one family, two carve-outs, filing-order chronology, and oracle context. It must be reported by document and is not legal reasoning.

## 6. Reuse, cost and risks

- **Reuse (PR #17 `b9d698c`):**
  - V3 `predict.py` `est()`: weighted conditional frequency with backoff; it maps directly onto "precedent contracts weighted by context agreement". Do **not** reuse its `CONTEXT_CONFLICT` backoff, which misread sparse support as conflict in V3.
  - V3 `h()`: salted deterministic ordering.
  - V3 `score_case()`: Brier and log-loss pattern.
  - V3 `frozen/freeze_receipt.json` refuse-if-changed pattern.
  - V2 `library_events.json`: append-only `DISCOVER`-style events with evidence anchors.
  - V2 `validate_library()`: forbidden-target-token guard, adapted as a leakage check.
- **New code:** one offline runner of about 250 lines (loader → sequence → 5 arms → sealed log → scorer/bootstrap → replay check) and about 8 unit tests, using the standard library only. Raw contract text is not committed; IDs, hashes and span indices are.
- **Cost:**
  - $0 in provider calls; runtime of seconds.
  - Human review: none required for the primary.
  - Optional: owner spot-checks 20 randomly drawn SEQUENCE labels *after* the run (≈30 min) to test oracle credibility, reported separately.
- **Main risks:**
  1. **Population skew.** At least 40 of the 232 EDGAR NDAs are tender-offer `ex99(d)` confidentiality agreements, i.e. M&A NDAs rather than a founder's vendor NDAs.
  2. **Oracle context is an upper bound.** A real pipeline must first extract the other determinations, which needs a component, probably an LLM.
  3. **Label provenance.** There is a single annotation set and inter-annotator agreement is unverified.
  4. **Small effects.** 180 documents may yield a CI that straddles zero. That outcome is `NO_OBSERVED…` or inconclusive, not a reason to change the gate.
  5. **The mechanism question stays open.** A positive result shows that conditional structure accumulates; it says nothing about BI, Jev or authority.

**Not proved here:** anything about BI integration, legal correctness, LLM review quality or adoption. This is an isolated upstream TRANSPOSE component at the feasibility/early-reliability stage (charter §5). The V3 8-case adjudication remains open and is not a prerequisite.

## 7. Single recommended next action

**Owner: authorize (or decline) ONE zero-call run of this test.** If authorized, the implementer would:
1. Commit `PROTOCOL.md` with the split, masks, arms, metric and verdicts above, plus the runner and freeze receipt.
2. Push that freeze before reading any SEQUENCE label.
3. Run once.
4. Report per-document results and update `PROJECT_STATE.json` in the same PR.

**What would reverse this decision:** evidence that ContractNLI labels are unreliable (e.g. a failed owner spot-check), or that the dataset hashes have changed. In either case the correct status is `BLOCKED_EVIDENCE`. CUAD's carve-out pairs would then be the fallback oracle.

## Appendix: reproduce the screen

Shallow `git clone` of the three repositories above (HTTPS to HuggingFace, Zenodo, SEC, arXiv and ACL Anthology is denied by this environment's egress policy, while git reads of public GitHub repositories work). Unzip and hash, then:

- Parse EDGAR file names with `^(\d+)_(\d{10})-(\d{2})-(\d{6})_` to get CIK and accession year.
- Deduplicate by CIK, then by greedy shingle Jaccard ≥ 0.8.
- Compute label counts and span overlaps **only** for accession year ≤ 1998.

Results: 607 docs (375 search-pdf, 119 sec-text, 113 sec-html); 232 EDGAR → 216 kept; DEV 36; SEQUENCE 180. CUAD: 510 contracts, 466 company prefixes, 41 categories. MAUD: 153 contracts, 92 questions.

The screening scripts ran from the session scratchpad and were not committed. This file is the record.
