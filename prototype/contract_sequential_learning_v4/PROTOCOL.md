# V4 PROTOCOL — sequential learning on authentic EDGAR credit agreements (FROZEN)

**Frozen:** 2026-10-14, before any V4 agreement was selected, downloaded or read. Hashes: `frozen/freeze_receipt.json` (LF-normalized). `v4_sequential.py run` refuses to run if any frozen file changes. Any change after this point is a recorded deviation, not a silent repair.

**Charter fit (v1.2, §§3, 5, 7):** this is an isolated upstream TRANSPOSE learning component, at the feasibility / early-reliability stage. It tests whether a persistent, source-anchored library improves *pre-observation review hypotheses* on later unseen agreements. It does not test BI, agents, legal approval, LLM quality or demand.

**Builds on:**
- V2: no incremental library value, but on a ceiling proxy.
- V3: frozen primary INCONCLUSIVE; secondary provision-within-section signal; agent-authored labels.
- Phase-0 notes on this branch, which are now historical. ContractNLI, CUAD and MAUD are not used, per the owner's direction (`Claude_Code_Sophon_V4_Execute_Public_Agreements_2026-10-14.md`).

## 1. Corpus: content-blind selection

- **Source:** SEC EDGAR full-text search, fetched by the operator with a declared contact User-Agent (`SEC_USER_AGENT`).
  - Query: `"credit agreement" "administrative agent"`, form 8-K, filed 2024-01-01 to 2024-06-30.
  - Window chosen to fall after every V3 document (2023 filings).
- **Candidates:** hits are taken in the order EDGAR returns them, keeping only `EX-10*` exhibits.
- **Eligibility.** Checks run in this order and use only size, opening text and structure. No provision body is scored.
  1. Exclude any issuer CIK used in V3 or already accepted.
  2. Exclude files under 150,000 bytes.
  3. Amendment screen on the first 6,000 characters of cleaned text: `first|…|tenth|incremental amendment`, `amendment no. N`, `joinder`, `waiver`. This fixes V3's 400-character miss on Motorola.
  4. V3 ToC parser must find ≥ 6 articles and ≥ 40 sections.
  5. A body must be located for ≥ 80% of ToC sections.
  6. Exclude ToC near-template duplicates of an accepted document (heading-set Jaccard ≥ 0.8).
- **Selection and order:** the first 8 eligible exhibits are accepted, then ordered by (filing date, accession).
  - Documents 1–2 are **SEEDS**; documents 3–8 are **EVALUATION**.
  - Ingestion order is experimental chronology, not legal effective order.
- **Shortfall:** if fewer than 8 are eligible, the status is `BLOCKED_INSUFFICIENT_CORPUS`. The rules are not relaxed.
- **Recorded:** the manifest records every screened candidate and the reason it was accepted or rejected, plus the SHA-256 of each search response and each exhibit.
- **What is committed:** raw exhibits and bodies stay local. Views (ToC headings, rule labels, hashes) are committed.

## 2. Targets and masking

- **Targets per evaluation agreement:** 4 subsections.
  - Eligible positions: articles whose V3 function is affirmative, negative or financial covenants, combined covenants, events of default, conditions precedent or representations.
  - The body must be located, and the heading must not be `[Reserved]`.
  - Order is by `sha256("sophon-v4-sequential-targets-2026-10-14"|doc|path)`.
  - Target positions are fixed by this rule, not by content or success.
- **Visible to every arm:**
  - family;
  - evidenced governing law, or UNKNOWN;
  - the target's article function and ordinal position;
  - the V3 rule types of the *other* subsections in that article;
  - library `L(k-1)`.
- **Never visible:** the target's heading, type, body, or any body text of the current agreement.

## 3. Prediction outputs (all arms)

1. **Provision-type shortlist:** V3 `predict.predict(..., "PROVISION")`, unchanged, except that `CONFLICT=0` disables V3's misfiring context-conflict backoff (V3 RESULTS §5).
2. **Within-provision expectations:** P(present) for five mechanical, source-text features of the revealed body, after the heading prefix is removed:
   - `EXCEPTION`: except / other than / excluding / unless / notwithstanding;
   - `PROVISO`: provided that / however / further;
   - `QUANT_THRESHOLD`: `$` amount, %, ratio `x to 1.0`, or "percent";
   - `CROSS_REFERENCE`: a reference to another Section that exists in this agreement;
   - `INLINE_DEFINITION`: a defined term inside the provision.

   For the type-conditioned arms, these are mixed over V3's top-3 type shortlist (renormalized).
3. **Dependency expectations:** P(the provision cross-references a section of rule type T).

Each prediction carries its supporting library event IDs, counts and fallback path. These are **review hypotheses**, never obligations.

## 4. Arms

All arms use the same targets, the same view and the same predictor code.

| Arm | Knowledge used |
|---|---|
| `FROZEN_SEED` | Library frozen after the 2 seeds. Type-conditioned. |
| `CUMULATIVE` | Seeds plus every earlier evaluation agreement, added only after that agreement's predictions are sealed and revealed. Type-conditioned. |
| `SIMPLE_COUNTS` | Same growing history. Feature base rates per article function; V3 `FAMILY` type frequency. No type or dependency structure. |
| `PRECEDENT` | Same growing history. Copies the most recent prior provision at the same article function and nearest position (0.9 / 0.1). |

## 5. Sequential loop for agreement k

1. Predict all targets for all arms, from `L(k-1)` and the frozen seed library.
2. Write `results/predictions/<doc>.json` and append it to a SHA-256 hash chain.
3. Only then may hidden bodies be read. `Hidden.get` raises an error if they are requested before sealing.
4. Observe the truth mechanically, with exact offsets and a hash of the body and of each match.
5. Score.
6. Log a `COUNTEREXAMPLE` event for each confident `CUMULATIVE` error (p ≥ 0.8 but absent, or p ≤ 0.2 but present), with its anchor.
7. Append `OBSERVE` events for every located provision of agreement k to the growing library, as version k.

Events are append-only. Revision happens through accumulated counts: no event is edited or deleted. A wrong high-confidence belief therefore persists until contrary evidence outweighs it, and that persistence is reported. `replay` reruns the sequence in a fresh process and must reproduce every sealed prediction hash.

## 6. Metrics and verdict (lower Brier is better)

- **Primary:** per-agreement mean Brier over the five features.
- **Ceiling guard:** features with an observed evaluation rate ≥ 0.95 or ≤ 0.05 are excluded from the primary for all arms. Both versions are reported.
- **Secondary, provisional (agent-authored rule labels):**
  - provision-type hit@3;
  - cross-reference type recall@3;
  - false expectations@3.
- **Verdicts:**
  - **KEEP (`CUMULATIVE_SIGNAL_PROVISIONAL`):** CUMULATIVE beats FROZEN_SEED in ≥ 4/6 agreements with a mean gain ≥ 0.01, **and** beats SIMPLE_COUNTS in ≥ 4/6 with a mean gain ≥ 0.01.
  - **REVISE (`EXPERIENCE_GAIN_EXPLAINED_BY_SIMPLE_COUNTS`):** the first condition holds but the second does not.
  - **STOP (`NO_OBSERVED_CUMULATIVE_GAIN`):** the first condition fails.
  - **INCONCLUSIVE:** fewer than 4 scorable agreements, or every feature is at the ceiling.
- **Qualifier `PRECEDENT_COPY_EQUIVALENT_OR_BETTER`:** added if CUMULATIVE does not beat PRECEDENT, meaning the gain may be clause copying.
- **Uncertainty:** six agreements cannot support significance. Any KEEP is provisional and is reported per agreement.
- **Can it fail?** On synthetic fixtures (`test_v4.py`, plumbing only), random features give STOP or REVISE and a planted learnable dependency gives KEEP.

## 7. Integrity limits, stated in advance

- **Feature truth** is mechanical text matching. It verifies textual presence, not legal meaning.
- **Provision-type and cross-reference-type labels** come from V3's frozen heading rules: `PROVISIONAL_AGENT_AUTHORED`. `review_packet.csv` (blind to arm predictions) lets a human spot-check them. No VERIFIED claim is made without that review.
- **Not proved:** legal correctness, generalization beyond this family and window, BI/agent value, or superiority to any LLM.
- **Costs:** provider calls 0; SEC requests ≤ 4 searches plus the exhibits screened; human review is optional, ≈ 20–30 minutes for the 24-row packet.
