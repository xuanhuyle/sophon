# V3 secondary heldout: independent human-adjudication package

**Package:** `v3-secondary-adjudication-package-1`, generated offline by `build_review_package.py` from committed files only (input SHA-256 in `package_manifest.json`). **Status: `AWAITING_HUMAN_ADJUDICATION`.** **Every label below is `PROVISIONAL_AGENT_AUTHORED`** (frozen rules `labels-v1-2026-10-13`). Nothing in this package has been adjudicated, and no agent opinion here counts as validation.

Task prompt: [`ADJUDICATION_TASK_PROMPT.md`](ADJUDICATION_TASK_PROMPT.md). Frozen results are untouched: `../results/heldout_run.json` (primary, `INCONCLUSIVE`) and `../results/secondary_repaired_run.json` (post-freeze secondary, `PREDICTIVE_SIGNAL_PROVISIONAL`).

## 0. Evidence status: original passages are BLOCKED in the session that built this package

- **Blocker (exact):** from the Claude Code cloud session on 2026-10-13 (last check 16:30:29Z), every request to `www.sec.gov`, `www.cloudflare.com` and `www.mongodb.com` failed with `CONNECT tunnel failed, response 403`. The environment's network policy does not allow these hosts. No raw document from the manifest exists in that container; the frozen run's raw copies were kept outside the repository, in the earlier session's local scratchpad on the owner's machine.
- **Consequence:** this package contains **no body passages**. It does not paraphrase or reconstruct any. The column `body_passage` reads `..._PENDING_LOCAL_RETRIEVAL` wherever the text is needed.
- **What IS genuine source evidence here:** the verbatim headings and (for credit agreements) the full article → section table of contents. The frozen extractor took them from files whose SHA-256 matched the manifest at freeze time, and they are committed in `../data/records_heldout_secondary.json`. SLA unit-text hashes are included so retrieved text can be checked against exactly what the predictor saw.
- **To unblock (either):**
  1. On a machine with internet access, run `python fetch_local_evidence.py --download --user-agent "<Name> <email>"` (SEC requires a declared contact), or `--raw-dir <old corpus_dl>` if the earlier raw copies still exist. It verifies every SHA-256, rebuilds the structure with the frozen code, checks it is identical to the committed records, and writes passages to `local_evidence/` (git-ignored; full text is never committed).
  2. Or allow the three hosts in the cloud environment's network settings and ask Claude Code to run the same script there.
- **SLA caveat:** both SLA URLs are *current* pages (not archives), retrieved 2026-10-13 ~13:33Z. If a page has changed, its hash will not match, and the script refuses to treat it as the frozen evidence (`HASH_MISMATCH`). Do not adjudicate SLA units from a changed page without recording that substitution.

| Doc | Source | Recorded SHA-256 | Needed for |
|---|---|---|---|
| CA-MARKEL | https://www.sec.gov/Archives/edgar/data/1096343/000109634323000160/markel2023-amendedandresta.htm (0001096343-23-000160, filed 2023-06-23) | `7d5e107559ebb8d7ce17b25bb01e5bcbd595a726a4e92cd2d50959c5005f13c3` | PROVISION cases (section bodies); SECTION case reviewable from TOC |
| CA-OLDDOMINION | https://www.sec.gov/Archives/edgar/data/885568/000095017023069906/ck0000885568-ex10_1.htm (0000950170-23-069906, filed 2023-12-13) | `aac7e9d04b13e0f9d3a5ed43f5fd73099c46a7409551c50614cf50cd8eb07320` | PROVISION cases (section bodies); SECTION case reviewable from TOC |
| SLA-CLOUDFLARE | https://www.cloudflare.com/business-sla/ (current page) | `40fe0ef53fa8e8981afde2c22ed1b6f4c967e5e94332c15cbf8800f82f5edf40` | all units (labels were assigned from unit text) |
| SLA-MONGODB | https://www.mongodb.com/legal/sla/cloud/atlas-database (current page) | `67ba7b3e30871e8d01692537e1e37e719197daf186268630b3bf8698cd306719` | all units (labels were assigned from unit text) |

## 1. What to review, in priority order

- **Tier 1A, the 18 hidden-positive labels.** Each is validated when the masked unit really carries the type **and** no visible unit in the same scope carries it. If a visible unit carries it, the target was never hidden, because the leak guard assumes the labels are right.
- **Tier 1B, the 148 negative labels with non-zero tie-aware top-3 mass in at least one arm** (G = GLOBAL_FREQ, F = FAMILY, FS = FAMILY_SECTION; EVIDENCED_LAW is identical to FS in every case). Of these, **27 carry mass ≥ 0.25**. The rest sit in large alphabetical ties (Markel Art. 7 and Old Dominion Art. 6/5), where each member gets a small share of a top-3 slot. Each is validated when **no unit in its scope carries the type**.
- **Tier 2, the 127 further negative labels needed only for Brier and log loss.** Per-case Brier averages over **every** candidate, so every negative must be confirmed absent, not only those near the top.
- **One pass resolves all three tiers.** Every label in a case refers to the same scope (the article for PROVISION cases, the whole document for SECTION cases). So the worksheet `review_units.csv` asks you to label each of the **78 units** once. The difference between tiers is how thorough that check has to be:
  - **For Tier 1 (hit@3 and false expectations@3):** confirm the masked units' types, and check every visible unit in scope for the case's Tier 1 types (listed per case in §4).
  - **For Tier 2 (Brier):** additionally give each unit its **complete** label set from the frozen vocabulary (`labels.SECTION_VOCAB` or `labels.PROVISION_VOCAB`; multiple labels allowed).
- **Unit priority in the worksheet:** **P1** is a masked target unit (16). **P2** is a visible unit with a mechanical flag: OTHER, multi-match, recorded V3 error or truncated heading (31). **P3** is a visible unit matched by exactly one rule (31).

**What can be reviewed before retrieval, and what cannot:**
- **Credit-agreement SECTION cases (2 cases, 21 article units):** reviewable now. The article function is judged from the verbatim article heading plus its full section list, both committed. Body text is optional.
- **Credit-agreement PROVISION cases (4 cases, 44 section units):** heading-level review is possible now. OTHER and multi-match units need the section body (retrieval).
- **SLA cases (2 cases, 13 units):** **not reviewable until retrieval.** Their labels were assigned from unit text, and Cloudflare's headings are truncated. Mark them `NOT_REVIEWABLE` rather than guessing from headings.

**Verdict codes (`reviewer_verdict`).**
- `AGREE`: your complete label set equals `agent_labels`.
- `DISAGREE`: write your labels in `reviewer_labels`.
- `UNSURE`: say why. Both bounds will be reported.
- `NOT_REVIEWABLE`: the evidence is unavailable or the hash does not match.
- Put a short verbatim quote of the decisive text in `reviewer_evidence_quote`.

**Reviewer independence (record at the top of the filled sheet).**
- Name and role.
- That you did not write the label rules.
- Whether you read §3's predictions before labelling (ideally not: label first, using §2 and the worksheet).
- Time spent.
- Evidence source: hash-verified local copy, or live page (with the date).

An agent re-reading these labels would **not** count as independent adjudication.

## 2. Known problems the reviewer must keep in view (from V3 RESULTS.md, PROTOCOL.md and the post-run audit)

**Segmentation**
- **CA-MOTOROLA:** the exhibit is a *First Amendment* with a redlined conformed copy. The pre-split amendment screen only read the first 400 characters. It failed segmentation in the frozen primary and is **excluded** from these 8 cases.
- **CA-OLDDOMINION:** POST-FREEZE replacement for CA-MOTOROLA (an amendment, screened out after the freeze). Title observed: 'SECOND AMENDED AND RESTATED CREDIT AGREEMENT'. The reviewer should confirm it is a complete restated agreement, not an amendment. TOC lists no sections under Article 7 (EVENTS OF DEFAULT).
- **SLA-CLOUDFLARE:** POST-FREEZE segmentation (numbered-paragraph fallback written after the frozen run returned SLA_TITLE_NOT_FOUND). Headings are truncated at the first word after the number (e.g. '3. Service' for '3. Service Credit Claims'); unit boundaries themselves are unvalidated. In the frozen primary it was unscorable (`SLA_TITLE_NOT_FOUND`).
- **Credit agreements are labelled from table-of-contents headings only.** A heading can understate a section's content, and body text was never read by the labeller.

**Sparse support misread as conflict**
- **CA-MARKEL:Article 7** (consistency 0.38) and **CA-OLDDOMINION:Article 6** (consistency 0.33): CONTEXT_CONFLICT backoff fired: fewer than 50% of the VISIBLE provision labels have support under this section function in training (only CA-BESTBUY splits affirmative/negative covenants). The predictor fell back to the family-wide distribution, producing a large alphabetical tie. RESULTS.md calls this 'sparse support read as conflict'. Visible-label errors (see multi-match flags) also enter this consistency check, so human labels for the VISIBLE units matter here, not only for the targets.
- Post-hoc diagnostic only (`../results/posthoc_no_conflict_backoff.json`): with the backoff disabled, provision hit@3 would have been 5.0/8 instead of 3.09/8.
- **Adjudication validates labels; it cannot repair the predictor.** A prospective fix belongs in a new frozen protocol.

**Misclassification risks (mechanical flags, not verdicts)**
- **First-match-wins on multi-topic headings.** For example, Markel 7.08 'Compliance with Laws and Approvals' becomes AUTHORIZATION_ENFORCEABILITY, not COMPLIANCE_WITH_LAWS. Markel 7.01 'GAAP Financial Statements' becomes ACCOUNTING_TERMS, not FINANCIAL_REPORTING. Old Dominion 6.09 'Sanctions; Anti-Corruption; Use of Proceeds' becomes SANCTIONS_AML, though USE_OF_PROCEEDS also matches. These are **visible** units, so they change the prediction context, not only the score.
- **Substring artifacts.** For example, Markel 12.06 'Stay of Acceleration' becomes FINANCIAL_RATIO_COVENANT via 'accele**ratio**n', and 9.02 'Remedies' becomes GUARANTEE_TERMS. Both are outside the 8 scored scopes, but they show the rules cannot be trusted without review.
- **Thin keyword support for positives.** The Markel Art. 1 positive INTERPRETATION rests on '1.10 Divisions' (keyword 'divisions'), while visible siblings '1.02 Other Definitions and Provisions' and '1.05 References to Agreement and Laws' are OTHER. Whether INTERPRETATION was really hidden depends on those OTHER units.
- **Recorded Cloudflare label errors.** These are V3's own audit, quoted in the unit flags: Unit 2 is a probable SERVICE_COMMITMENT and Unit 7 a probable CREDIT_CALCULATION_APPLICATION.
- **A plausible wrong section label goes undetected.** In the negative control (Affirmative Covenants relabelled as Representations), predictions silently shifted. Labels for section function are therefore inputs that matter.
- **Training labels (8 documents) are out of scope here** but also agent-authored. Example: the Best Buy rule-order artifact where 'Use of Proceeds; Federal Reserve Regulations' becomes MARGIN_REGULATIONS. This remains a limitation after this adjudication.

**Post-run audit findings (agent-authored, not adjudication)**
- **The split was hash-based, not chronological.** CA-MARKEL (filed 2023-06-23) and CA-OLDDOMINION (2023-12-13) were scored using CA-LINCOLN (2023-12-21) as training.
- **Training support is thinner than it looks.** Equitable and Lincoln are near-identical templates, so the four training credit agreements amount to about 3 drafting styles.
- **The provisional signal comes from two conventional cases.** FAMILY_SECTION's provision hit@3 of 3.09/8 comes from Markel Art. 1 (2.0) and Old Dominion Art. 5 (1.0). Section-level adds nothing over FAMILY, and Brier is worse than GLOBAL (0.256 vs 0.183).
- **Reproducibility.** Both frozen result files re-score exactly from the committed records, and all 9 freeze-receipt files are unchanged.

## 3. Compact review table (one row per case)

Predicted structures show each arm's top-3 with smoothed frequency p. FS flags and fallback come from the frozen run. Agent labels and predictions are **not** validated.

| Case | Contract, section and source reference | Original contractual passage (what exists now) | Proposed section/provision classification (hidden positives ← masked unit) | Relevant predicted provision structures (top-3 per arm) | Supporting evidence and disputed classifications | What the human reviewer needs to validate |
|---|---|---|---|---|---|---|
| **CA-MARKEL:SECTION** | CA-MARKEL, whole document; https://www.sec.gov/Archives/edgar/data/1096343/000109634323000160/markel2023-amendedandresta.htm | Article 10 'THE ADMINISTRATIVE AGENT'; Article 11 'MISCELLANEOUS' — TOC headings + section lists (body optional) | AGENCY ← Article 10; MISCELLANEOUS ← Article 11 | GLOBAL_FREQ: AGENCY 0.50, CLAIM_PROCEDURE 0.50, CREDIT_CALCULATION_APPLICATION 0.50 (5-way tie at p=0.500 crosses rank 3)<br>FAMILY: AGENCY 0.90, MISCELLANEOUS 0.90, COVENANTS_COMBINED 0.68<br>FAMILY_SECTION: AGENCY 0.96, MISCELLANEOUS 0.96, COVENANTS_COMBINED 0.50<br>hit@3 G/F/FS: 1.2/2.0/2.0 | Article 10: AGENCY <- heading keyword 'agent' (first match wins); Article 11: MISCELLANEOUS <- heading keyword 'miscellaneous' (first match wins)<br>**Disputed:** 3 flagged visible unit(s): Article 6 'REPRESENTATIONS AND WARRANTIES OF THE CREDIT ' [REPRESENTATIONS: MULTI-MATCH CREDIT_FACILITIES ('credit')]; Article 7 'AFFIRMATIVE COVENANTS' [AFFIRMATIVE_COVENANTS: MULTI-MATCH COVENANTS_COMBINED ('covenant')]; Article 8 'NEGATIVE COVENANTS' [NEGATIVE_COVENANTS: MULTI-MATCH COVENANTS_COMBINED ('covenant')] | (1) 2 masked unit(s) carry AGENCY, MISCELLANEOUS; (2) none of the 10 visible units carries them; (3) no unit in scope carries the 4 Tier-1B types (4 with mass ≥ 0.25: CLAIM_PROCEDURE, COVENANTS_COMBINED, CREDIT_CALCULATION_APPLICATION, CREDIT_SCHEDULE); (4) for Brier, full labels for all 12 units (9 Tier-2 types) |
| **CA-MARKEL:Article 7** | CA-MARKEL Article 7 'AFFIRMATIVE COVENANTS' (AFFIRMATIVE_COVENANTS); https://www.sec.gov/Archives/edgar/data/1096343/000109634323000160/markel2023-amendedandresta.htm | Section 7.10 'Maintenance of Books and Records; Inspection'; Section 7.11 'Use of Proceeds' — body: BLOCKED (see §0) | BOOKS_INSPECTION ← Section 7.10; USE_OF_PROCEEDS ← Section 7.11 | GLOBAL_FREQ: BAIL_IN_QFC 0.50, BENCHMARK_RATES 0.50, COMMITMENTS_BORROWINGS 0.50 (27-way tie at p=0.500 crosses rank 3)<br>FAMILY: BAIL_IN_QFC 0.90, BENCHMARK_RATES 0.90, COMMITMENTS_BORROWINGS 0.90 (27-way tie at p=0.900 crosses rank 3)<br>FAMILY_SECTION: BAIL_IN_QFC 0.90, BENCHMARK_RATES 0.90, COMMITMENTS_BORROWINGS 0.90 (27-way tie at p=0.900 crosses rank 3)<br>hit@3 G/F/FS: 0.0/0.0/0.0<br>FS flags: CONTEXT_CONFLICT(consistency=0.38)_BACKOFF | Section 7.10: BOOKS_INSPECTION <- heading keyword 'books' (first match wins); Section 7.11: USE_OF_PROCEEDS <- heading keyword 'use of proceeds' (first match wins)<br>**Disputed:** 4 flagged visible unit(s): Section 7.01 'GAAP Financial Statements' [ACCOUNTING_TERMS: MULTI-MATCH FINANCIAL_REPORTING ('financial statements')]; Section 7.03 'Certificates; Other Reports' [OTHER: OTHER]; Section 7.04 'Notice of Litigiation and Other Matters' [OTHER: OTHER]; Section 7.08 'Compliance with Laws and Approvals' [AUTHORIZATION_ENFORCEABILITY: MULTI-MATCH COMPLIANCE_WITH_LAWS ('compliance with laws')] | (1) 2 masked unit(s) carry USE_OF_PROCEEDS, BOOKS_INSPECTION; (2) none of the 10 visible units carries them; (3) no unit in scope carries the 27 Tier-1B types (0 with mass ≥ 0.25: —); (4) for Brier, full labels for all 12 units (23 Tier-2 types) |
| **CA-MARKEL:Article 1** | CA-MARKEL Article 1 'DEFINITIONS' (DEFINITIONS); https://www.sec.gov/Archives/edgar/data/1096343/000109634323000160/markel2023-amendedandresta.htm | Section 1.01 'Definitions'; Section 1.10 'Divisions' — body: BLOCKED (see §0) | DEFINED_TERMS ← Section 1.01; INTERPRETATION ← Section 1.10 | GLOBAL_FREQ: AUTHORIZATION_ENFORCEABILITY 0.50, BAIL_IN_QFC 0.50, BENCHMARK_RATES 0.50 (34-way tie at p=0.500 crosses rank 3)<br>FAMILY: AUTHORIZATION_ENFORCEABILITY 0.90, BAIL_IN_QFC 0.90, BENCHMARK_RATES 0.90 (34-way tie at p=0.900 crosses rank 3)<br>FAMILY_SECTION: BENCHMARK_RATES 0.97, DEFINED_TERMS 0.97, INTERPRETATION 0.97<br>hit@3 G/F/FS: 0.176/0.176/2.0 | Section 1.01: DEFINED_TERMS <- heading keyword 'definitions' (first match wins); Section 1.10: INTERPRETATION <- heading keyword 'divisions' (first match wins)<br>**Disputed:** 6 flagged visible unit(s): Section 1.02 'Other Definitions and Provisions' [OTHER: OTHER]; Section 1.04 'Rounding' [OTHER: OTHER]; Section 1.05 'References to Agreement and Laws' [OTHER: OTHER]; Section 1.06 'Times of Day' [OTHER: OTHER]; Section 1.08 'Exchange Rates; Currency Equivalents' [OTHER: OTHER]; Section 1.09 'Rates' [OTHER: OTHER] | (1) 2 masked unit(s) carry INTERPRETATION, DEFINED_TERMS; (2) none of the 8 visible units carries them; (3) no unit in scope carries the 32 Tier-1B types (1 with mass ≥ 0.25: BENCHMARK_RATES); (4) for Brier, full labels for all 10 units (24 Tier-2 types) |
| **CA-OLDDOMINION:SECTION** | CA-OLDDOMINION, whole document; https://www.sec.gov/Archives/edgar/data/885568/000095017023069906/ck0000885568-ex10_1.htm | Article 4 'CONDITIONS'; Article 6 'NEGATIVE COVENANTS' — TOC headings + section lists (body optional) | CONDITIONS_PRECEDENT ← Article 4; NEGATIVE_COVENANTS ← Article 6 | GLOBAL_FREQ: CLAIM_PROCEDURE 0.50, CONDITIONS_PRECEDENT 0.50, CREDIT_CALCULATION_APPLICATION 0.50 (4-way tie at p=0.500 crosses rank 3)<br>FAMILY: CONDITIONS_PRECEDENT 0.90, COVENANTS_COMBINED 0.68, GUARANTY 0.68<br>FAMILY_SECTION: CONDITIONS_PRECEDENT 0.97, GUARANTY 0.77, COVENANTS_COMBINED 0.62<br>hit@3 G/F/FS: 0.75/1.0/1.0 | Article 4: CONDITIONS_PRECEDENT <- heading keyword 'condition' (first match wins); Article 6: NEGATIVE_COVENANTS <- heading keyword 'negative covenant' (first match wins)<br>**Disputed:** 1 flagged visible unit(s): Article 5 'AFFIRMATIVE COVENANTS' [AFFIRMATIVE_COVENANTS: MULTI-MATCH COVENANTS_COMBINED ('covenant')]. Masked-unit flags: MULTI-MATCH COVENANTS_COMBINED ('covenant') | (1) 2 masked unit(s) carry CONDITIONS_PRECEDENT, NEGATIVE_COVENANTS; (2) none of the 7 visible units carries them; (3) no unit in scope carries the 5 Tier-1B types (5 with mass ≥ 0.25: CLAIM_PROCEDURE, COVENANTS_COMBINED, CREDIT_CALCULATION_APPLICATION, CREDIT_SCHEDULE, GUARANTY); (4) for Brier, full labels for all 9 units (9 Tier-2 types) |
| **CA-OLDDOMINION:Article 6** | CA-OLDDOMINION Article 6 'NEGATIVE COVENANTS' (NEGATIVE_COVENANTS); https://www.sec.gov/Archives/edgar/data/885568/000095017023069906/ck0000885568-ex10_1.htm | Section 6.01 'Liens'; Section 6.02 'Fundamental Changes' — body: BLOCKED (see §0) | LIENS ← Section 6.01; FUNDAMENTAL_CHANGES ← Section 6.02 | GLOBAL_FREQ: ACCOUNTING_TERMS 0.50, AUTHORIZATION_ENFORCEABILITY 0.50, BAIL_IN_QFC 0.50 (33-way tie at p=0.500 crosses rank 3)<br>FAMILY: ACCOUNTING_TERMS 0.90, AUTHORIZATION_ENFORCEABILITY 0.90, BAIL_IN_QFC 0.90 (33-way tie at p=0.900 crosses rank 3)<br>FAMILY_SECTION: ACCOUNTING_TERMS 0.86, AUTHORIZATION_ENFORCEABILITY 0.86, BAIL_IN_QFC 0.86 (33-way tie at p=0.857 crosses rank 3)<br>hit@3 G/F/FS: 0.091/0.091/0.091<br>FS flags: CONTEXT_CONFLICT(consistency=0.33)_BACKOFF | Section 6.01: LIENS <- heading keyword 'liens' (first match wins); Section 6.02: FUNDAMENTAL_CHANGES <- heading keyword 'fundamental change' (first match wins)<br>**Disputed:** 5 flagged visible unit(s): Section 6.03 'Lines of Business' [OTHER: OTHER]; Section 6.06 'Hedging Agreements' [OTHER: OTHER]; Section 6.07 'Wholesale Power Contracts' [OTHER: OTHER]; Section 6.08 'Corporate Documents; Fiscal Year' [OTHER: OTHER]; Section 6.09 'Sanctions; Anti-Corruption; Use of Proceeds' [SANCTIONS_AML: MULTI-MATCH USE_OF_PROCEEDS ('use of proceeds')] | (1) 2 masked unit(s) carry FUNDAMENTAL_CHANGES, LIENS; (2) none of the 7 visible units carries them; (3) no unit in scope carries the 32 Tier-1B types (0 with mass ≥ 0.25: —); (4) for Brier, full labels for all 9 units (23 Tier-2 types) |
| **CA-OLDDOMINION:Article 5** | CA-OLDDOMINION Article 5 'AFFIRMATIVE COVENANTS' (AFFIRMATIVE_COVENANTS); https://www.sec.gov/Archives/edgar/data/885568/000095017023069906/ck0000885568-ex10_1.htm | Section 5.01 'Financial Statements and Other Information'; Section 5.05 'Books and Records; Inspection Rights' — body: BLOCKED (see §0) | FINANCIAL_REPORTING ← Section 5.01; BOOKS_INSPECTION ← Section 5.05 | GLOBAL_FREQ: ACCOUNTING_TERMS 0.50, AUTHORIZATION_ENFORCEABILITY 0.50, BAIL_IN_QFC 0.50 (33-way tie at p=0.500 crosses rank 3)<br>FAMILY: ACCOUNTING_TERMS 0.90, AUTHORIZATION_ENFORCEABILITY 0.90, BAIL_IN_QFC 0.90 (33-way tie at p=0.900 crosses rank 3)<br>FAMILY_SECTION: FINANCIAL_REPORTING 0.91, MAINTENANCE_INSURANCE 0.91, ACCOUNTING_TERMS 0.80 (31-way tie at p=0.800 crosses rank 3)<br>hit@3 G/F/FS: 0.091/0.091/1.0 | Section 5.01: FINANCIAL_REPORTING <- heading keyword 'financial statements' (first match wins); Section 5.05: BOOKS_INSPECTION <- heading keyword 'books' (first match wins)<br>**Disputed:** 5 flagged visible unit(s): Section 5.04 'Payment of Obligations; Taxes' [TAXES: MULTI-MATCH PAYMENT_OF_OBLIGATIONS ('payment of obligations')]; Section 5.08 'Further Assurances' [OTHER: OTHER]; Section 5.09 'Identification of Parties' [OTHER: OTHER]; Section 5.10 'Certain Equity and Security' [OTHER: OTHER]; Section 5.12 'Ranking' [OTHER: OTHER] | (1) 2 masked unit(s) carry BOOKS_INSPECTION, FINANCIAL_REPORTING; (2) none of the 11 visible units carries them; (3) no unit in scope carries the 32 Tier-1B types (1 with mass ≥ 0.25: MAINTENANCE_INSURANCE); (4) for Brier, full labels for all 13 units (20 Tier-2 types) |
| **SLA-CLOUDFLARE:SECTION** | SLA-CLOUDFLARE, whole document; https://www.cloudflare.com/business-sla/ | Unit 3 '2. Definitions'; Unit 5 '4. SLA' — body: BLOCKED (see §0) | DEFINITIONS, CREDIT_CALCULATION_APPLICATION ← Unit 3; EXCLUSIONS ← Unit 5 (collateral: DEFINITIONS) | GLOBAL_FREQ: DEFINITIONS 0.94, AGENCY 0.50, CONDITIONS_PRECEDENT 0.50 (8-way tie at p=0.500 crosses rank 3)<br>FAMILY: DEFINITIONS 0.99, CREDIT_CALCULATION_APPLICATION 0.90, CREDIT_SCHEDULE 0.90<br>FAMILY_SECTION: DEFINITIONS 1.00, CREDIT_CALCULATION_APPLICATION 0.98, CREDIT_SCHEDULE 0.98<br>hit@3 G/F/FS: 1.25/2.0/2.0 | Unit 3: multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256); Unit 5: multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256)<br>**Disputed:** 6 flagged visible unit(s): Unit 1 'HEADING_ABSENT' [OTHER: OTHER, TRUNCATED HEADING]; Unit 2 '1. Business' [OTHER: OTHER, V3-RECORDED LABEL ERROR, TRUNCATED HEADING]; Unit 4 '3. Service' [CLAIM_PROCEDURE: TRUNCATED HEADING]; Unit 6 '5. Service' [SOLE_REMEDY: TRUNCATED HEADING]; Unit 7 '6. Service' [OTHER: OTHER, V3-RECORDED LABEL ERROR, TRUNCATED HEADING]; Unit 8 '7. Methodology' [OTHER: OTHER, TRUNCATED HEADING]. Masked-unit flags: TRUNCATED HEADING; TRUNCATED HEADING | (1) 2 masked unit(s) carry CREDIT_CALCULATION_APPLICATION, DEFINITIONS, EXCLUSIONS; (2) none of the 6 visible units carries them; (3) no unit in scope carries the 7 Tier-1B types (7 with mass ≥ 0.25: AGENCY, CONDITIONS_PRECEDENT, CREDIT_FACILITIES, CREDIT_SCHEDULE, EVENTS_OF_DEFAULT, MISCELLANEOUS, REPRESENTATIONS); (4) for Brier, full labels for all 8 units (11 Tier-2 types) |
| **SLA-MONGODB:SECTION** | SLA-MONGODB, whole document; https://www.mongodb.com/legal/sla/cloud/atlas-database | Unit 1 'HEADING_ABSENT'; Unit 4 'Service Credits' — body: BLOCKED (see §0) | CREDIT_SCHEDULE, EXCLUSIONS ← Unit 1; SOLE_REMEDY ← Unit 4 (collateral: EXCLUSIONS) | GLOBAL_FREQ: AGENCY 0.50, CONDITIONS_PRECEDENT 0.50, CREDIT_FACILITIES 0.50 (7-way tie at p=0.500 crosses rank 3)<br>FAMILY: CREDIT_SCHEDULE 0.90, CREDIT_CAP 0.68, EXCLUSIONS 0.68 (5-way tie at p=0.678 crosses rank 3)<br>FAMILY_SECTION: CREDIT_SCHEDULE 0.98, CREDIT_CAP 0.74, EXCLUSIONS 0.74 (5-way tie at p=0.736 crosses rank 3)<br>hit@3 G/F/FS: 0.429/1.8/1.8 | Unit 1: multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256); Unit 4: multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256)<br>**Disputed:** 1 flagged visible unit(s): Unit 5 'Limitations' [OTHER: OTHER] | (1) 2 masked unit(s) carry CREDIT_SCHEDULE, EXCLUSIONS, SOLE_REMEDY; (2) none of the 3 visible units carries them; (3) no unit in scope carries the 9 Tier-1B types (9 with mass ≥ 0.25: AGENCY, CONDITIONS_PRECEDENT, CREDIT_CAP, CREDIT_FACILITIES, EVENTS_OF_DEFAULT, MISCELLANEOUS, REPRESENTATIONS, SCOPE_APPLICABILITY, SERVICE_COMMITMENT); (4) for Brier, full labels for all 5 units (8 Tier-2 types) |

## 4. Per-case scope: every unit the reviewer labels

Units are in source order. **Bold** marks masked target units. The unit labels below are exactly what the predictor used; fill your answers in `review_units.csv`, keyed by `unit_id`.

### CA-MARKEL:SECTION (SECTION; law given to the predictor: UNKNOWN)

Scope: **all top-level units of CA-MARKEL**. Frozen pipeline (pre-registered primary and secondary). Many subsections fell to OTHER (rules were written on 4 training documents).

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P3 | Article 1 | DEFINITIONS <br><sub>10 sections: 1.01 Definitions · 1.02 Other Definitions and Provisions · 1.03 Accounting Terms · 1.04 Rounding · 1.05 References to Agreement and Laws · 1.06 Times of Day · 1.07 Letter of Credit Amounts · 1.08 Exchange Rates; Currency Equivalents · 1.09 Rates · 1.10 Divisions</sub> | DEFINITIONS | DEFINITIONS <- heading keyword 'definition' (first match wins) | — |
| P3 | Article 2 | REVOLVING CREDIT FACILITY <br><sub>6 sections: 2.01 Revolving Credit Loans · 2.02 Swingline Loans · 2.03 Procedure for Advances of Revolving Credit Loans and Swingline Loans · 2.04 Repayment and Prepayment of Loans · 2.05 Voluntary Reduction of the Commitments · 2.06 Termination of Revolving Credit Facility</sub> | CREDIT_FACILITIES | CREDIT_FACILITIES <- heading keyword 'credit' (first match wins) | — |
| P3 | Article 3 | LETTER OF CREDIT FACILITY <br><sub>11 sections: 3.01 Syndicated Letters of Credit · 3.02 Participated Letters of Credit · 3.03 Expiry Date of Letters of Credit · 3.04 Obligations Absolute · 3.05 Interest · 3.06 Cash Collateralization of Letters of Credit · 3.07 Use of Letters of Credit · 3.08 The Fronting Bank and L/C Agent · 3.09 Letter of Credit Fees and Other Charges · 3.10 Letters of Credit Issued of Subsidiaries · 3.11 Designation of Additional Account Partie…</sub> | CREDIT_FACILITIES | CREDIT_FACILITIES <- heading keyword 'credit' (first match wins) | — |
| P3 | Article 4 | GENERAL LOAN PROVISIONS <br><sub>16 sections: 4.01 Interest · 4.02 Notice and Manner of Conversion or Continuation of Loans · 4.03 Fees · 4.04 Manner of Payment · 4.05 Evidence of Indebtedness · 4.06 Sharing of Payments by Lenders · 4.07 Administrative Agent's Clawback · 4.08 Changed Circumstances · 4.09 Indemnity · 4.10 Increased Costs · 4.11 Taxes · 4.12 Mitigation Obligations; Replacement of Lenders · 4.13 Increase in Commitments · 4.14 Cash Collateral · 4.15…</sub> | CREDIT_FACILITIES | CREDIT_FACILITIES <- heading keyword 'loan' (first match wins) | — |
| P3 | Article 5 | CONDITIONS OF CLOSING AND ISSUANCE <br><sub>2 sections: 5.01 Conditions to Closing and Initial Credit Extensions · 5.02 Conditions Precedent to all Credit Extensions</sub> | CONDITIONS_PRECEDENT | CONDITIONS_PRECEDENT <- heading keyword 'condition' (first match wins) | — |
| P2 | Article 6 | REPRESENTATIONS AND WARRANTIES OF THE CREDIT PARTIES <br><sub>16 sections: 6.01 Organization; Power; Qualification · 6.02 Ownership · 6.03 Authorization; Enforceability · 6.04 Compliance of Agreement, Loan Documents and Credit Extensions with Laws, Etc · 6.05 Compliance with Law; Governmental Approvals · 6.06 Tax Returns and Payments · 6.07 Environmental Matters · 6.08 Employee Benefit Matters · 6.09 Margin Stock · 6.10 Government Regulation · 6.11 Financial Statements · 6.12 No Material Ad…</sub> | REPRESENTATIONS | REPRESENTATIONS <- heading keyword 'representation' (first match wins) | multi-match: CREDIT_FACILITIES ('credit') |
| P2 | Article 7 | AFFIRMATIVE COVENANTS <br><sub>12 sections: 7.01 GAAP Financial Statements · 7.02 Statutory Financial Statements · 7.03 Certificates; Other Reports · 7.04 Notice of Litigiation and Other Matters · 7.05 Preservation of Existence, Etc · 7.06 Insurance · 7.07 Payment of Taxes and Other Obligations · 7.08 Compliance with Laws and Approvals · 7.09 Compliance with ERISA · 7.10 Maintenance of Books and Records; Inspection · 7.11 Use of Proceeds · 7.12 Compliance with…</sub> | AFFIRMATIVE_COVENANTS | AFFIRMATIVE_COVENANTS <- heading keyword 'affirmative covenant' (first match wins) | multi-match: COVENANTS_COMBINED ('covenant') |
| P2 | Article 8 | NEGATIVE COVENANTS <br><sub>7 sections: 8.01 Subsidiary Indebtedness · 8.02 Liens · 8.03 Acquisitions · 8.04 Fundamental Changes · 8.05 Transactions with Affiliates · 8.06 Accounting Changes · 8.07 Financial Covenants</sub> | NEGATIVE_COVENANTS | NEGATIVE_COVENANTS <- heading keyword 'negative covenant' (first match wins) | multi-match: COVENANTS_COMBINED ('covenant') |
| P3 | Article 9 | DEFAULT AND REMEDIES <br><sub>5 sections: 9.01 Events of Default · 9.02 Remedies · 9.03 Rights and Remedies Cumulative; Non-Waiver, Etc · 9.04 Crediting of Payments and Proceeds · 9.05 Administrative Agent May File Proofs of Claim</sub> | EVENTS_OF_DEFAULT | EVENTS_OF_DEFAULT <- heading keyword 'default' (first match wins) | — |
| P1 | **Article 10** | THE ADMINISTRATIVE AGENT <br><sub>10 sections: 10.01 Appointment and Authority · 10.02 Rights as a Lender · 10.03 Exculpatory Provisions · 10.04 Reliance by the Administrative Agent · 10.05 Delegation of Duties · 10.06 Resignation of Administrative Agent · 10.07 Non-Reliance on Administrative Agent and Other Lenders · 10.08 No Other Duties, Etc · 10.09 Lender ERISA Representations · 10.10 Erroneous Payments</sub> | AGENCY | AGENCY <- heading keyword 'agent' (first match wins) | carries hidden positive(s): AGENCY |
| P1 | **Article 11** | MISCELLANEOUS <br><sub>25 sections: 11.01 Notices · 11.02 Amendments, Waivers and Consents · 11.03 Expenses; Indemnity · 11.04 Right of Setoff · 11.05 Governing Law, Jurisdiction, Etc · 11.06 Waiver of Jury Trial · 11.07 Reversal of Payments · 11.08 [Reserved] · 11.09 Successors and Assigns; Participations · 11.10 Treatment of Certain Information; Confidentiality · 11.11 Performance of Duties · 11.12 All Powers Coupled with Interest · 11.13 Survival · …</sub> | MISCELLANEOUS | MISCELLANEOUS <- heading keyword 'miscellaneous' (first match wins) | carries hidden positive(s): MISCELLANEOUS |
| P3 | Article 12 | GUARANTY <br><sub>8 sections: 12.01 The Guaranty · 12.02 Guaranty Unconditional · 12.03 Discharge Only upon Payment in Full; Reinstatement in Certain Circumstances · 12.04 Waiver by the Guarantor · 12.05 Subrogation · 12.06 Stay of Acceleration · 12.07 Continuing Guaranty; Assignments · 12.08 Subordination of Other Obligations</sub> | GUARANTY | GUARANTY <- heading keyword 'guarant' (first match wins) | — |

- **Tier 1A (2):** AGENCY, MISCELLANEOUS
- **Tier 1B (4):** mass ≥ 0.25: CLAIM_PROCEDURE [G 0.6], COVENANTS_COMBINED [F 1.0/FS 1.0], CREDIT_CALCULATION_APPLICATION [G 0.6], CREDIT_SCHEDULE [G 0.6]. Tie-share only (< 0.25): 0 types — —.
- **Tier 2, Brier only (9):** CREDIT_CAP, EXCLUSIONS, FINANCIAL_COVENANTS, MEASUREMENT_METHOD, SCOPE_APPLICABILITY, SERVICE_COMMITMENT, SOLE_REMEDY, TERMINATION_RIGHT, YIELD_PROTECTION_TAXES.

### CA-MARKEL:Article 7 (PROVISION; law given to the predictor: STATE_OF_NEW_YORK)

Scope: **Article 7 'AFFIRMATIVE COVENANTS'** → section function `AFFIRMATIVE_COVENANTS` (itself an agent label; validate it in the SECTION case of CA-MARKEL).

> **Sparse-support backoff case.** CONTEXT_CONFLICT backoff fired: fewer than 50% of the VISIBLE provision labels have support under this section function in training (only CA-BESTBUY splits affirmative/negative covenants). The predictor fell back to the family-wide distribution, producing a large alphabetical tie. RESULTS.md calls this 'sparse support read as conflict'. Visible-label errors (see multi-match flags) also enter this consistency check, so human labels for the VISIBLE units matter here, not only for the targets.

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P2 | Section 7.01 | GAAP Financial Statements | ACCOUNTING_TERMS | ACCOUNTING_TERMS <- heading keyword 'gaap' (first match wins) | multi-match: FINANCIAL_REPORTING ('financial statements') |
| P3 | Section 7.02 | Statutory Financial Statements | FINANCIAL_REPORTING | FINANCIAL_REPORTING <- heading keyword 'financial statements' (first match wins) | — |
| P2 | Section 7.03 | Certificates; Other Reports | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 7.04 | Notice of Litigiation and Other Matters | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P3 | Section 7.05 | Preservation of Existence, Etc | EXISTENCE_ORGANIZATION | EXISTENCE_ORGANIZATION <- heading keyword 'existence' (first match wins) | — |
| P3 | Section 7.06 | Insurance | MAINTENANCE_INSURANCE | MAINTENANCE_INSURANCE <- heading keyword 'insurance' (first match wins) | — |
| P3 | Section 7.07 | Payment of Taxes and Other Obligations | TAXES | TAXES <- heading keyword 'taxes' (first match wins) | — |
| P2 | Section 7.08 | Compliance with Laws and Approvals | AUTHORIZATION_ENFORCEABILITY | AUTHORIZATION_ENFORCEABILITY <- heading keyword 'approvals' (first match wins) | multi-match: COMPLIANCE_WITH_LAWS ('compliance with laws') |
| P3 | Section 7.09 | Compliance with ERISA | ERISA | ERISA <- heading keyword 'erisa' (first match wins) | — |
| P1 | **Section 7.10** | Maintenance of Books and Records; Inspection | BOOKS_INSPECTION | BOOKS_INSPECTION <- heading keyword 'books' (first match wins) | carries hidden positive(s): BOOKS_INSPECTION |
| P1 | **Section 7.11** | Use of Proceeds | USE_OF_PROCEEDS | USE_OF_PROCEEDS <- heading keyword 'use of proceeds' (first match wins) | carries hidden positive(s): USE_OF_PROCEEDS |
| P3 | Section 7.12 | Compliance with Anti-Corruption Laws; Anti-Money Laundering Laws; Sanctions and Beneficial Ownership | SANCTIONS_AML | SANCTIONS_AML <- heading keyword 'anti-corruption' (first match wins) | — |

- **Tier 1A (2):** USE_OF_PROCEEDS, BOOKS_INSPECTION
- **Tier 1B (27):** mass ≥ 0.25: —. Tie-share only (< 0.25): 27 types — BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS, COMMITMENT_CHANGES, CONDITIONS_EFFECTIVENESS, CONFIDENTIALITY, COUNTERPARTS_INTEGRATION, DEFAULTING_LENDERS, DEFINED_TERMS, EXPENSES_INDEMNITY, FEES_INTEREST, FINANCIAL_CONDITION_NO_MAC, FINANCIAL_RATIO_COVENANT, GOVERNING_LAW_JURISDICTION, INCREASED_COSTS_ILLEGALITY, INTERPRETATION, INVESTMENT_COMPANY, JURY_TRIAL_WAIVER, LIENS, LITIGATION, MITIGATION_REPLACEMENT, NOTICES_COMMUNICATIONS, NO_FIDUCIARY_DUTY, PAYMENTS_SHARING, REPAYMENT_PREPAYMENT, SUCCESSORS_ASSIGNS, WAIVERS_AMENDMENTS.
- **Tier 2, Brier only (23):** AFFILIATE_TRANSACTIONS, AGENT_PROVISIONS, AMEND_RESTATE_EXISTING, COMPLIANCE_WITH_LAWS, ENVIRONMENTAL, ERRONEOUS_PAYMENTS, EVENTS_OF_DEFAULT_LIST, FULL_DISCLOSURE, FUNDAMENTAL_CHANGES, GUARANTEE_TERMS, INDEBTEDNESS, INTEREST_RATE_LIMITATION, JUDGMENT_CURRENCY, LETTERS_OF_CREDIT, MARGIN_REGULATIONS, NOTICE_OF_EVENTS, NO_DEFAULT, PARI_PASSU, PAYMENT_OF_OBLIGATIONS, SETOFF, SEVERABILITY, SUBSIDIARIES, SURVIVAL.

### CA-MARKEL:Article 1 (PROVISION; law given to the predictor: STATE_OF_NEW_YORK)

Scope: **Article 1 'DEFINITIONS'** → section function `DEFINITIONS` (itself an agent label; validate it in the SECTION case of CA-MARKEL).

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P1 | **Section 1.01** | Definitions | DEFINED_TERMS | DEFINED_TERMS <- heading keyword 'definitions' (first match wins) | carries hidden positive(s): DEFINED_TERMS |
| P2 | Section 1.02 | Other Definitions and Provisions | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P3 | Section 1.03 | Accounting Terms | ACCOUNTING_TERMS | ACCOUNTING_TERMS <- heading keyword 'accounting terms' (first match wins) | — |
| P2 | Section 1.04 | Rounding | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 1.05 | References to Agreement and Laws | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 1.06 | Times of Day | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P3 | Section 1.07 | Letter of Credit Amounts | LETTERS_OF_CREDIT | LETTERS_OF_CREDIT <- heading keyword 'letter of credit' (first match wins) | — |
| P2 | Section 1.08 | Exchange Rates; Currency Equivalents | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 1.09 | Rates | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P1 | **Section 1.10** | Divisions | INTERPRETATION | INTERPRETATION <- heading keyword 'divisions' (first match wins) | carries hidden positive(s): INTERPRETATION |

- **Tier 1A (2):** INTERPRETATION, DEFINED_TERMS
- **Tier 1B (32):** mass ≥ 0.25: BENCHMARK_RATES [G 0.088/F 0.088/FS 1.0]. Tie-share only (< 0.25): 31 types — AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, COMMITMENTS_BORROWINGS, COMMITMENT_CHANGES, CONDITIONS_EFFECTIVENESS, CONFIDENTIALITY, COUNTERPARTS_INTEGRATION, DEFAULTING_LENDERS, ERISA, EXISTENCE_ORGANIZATION, EXPENSES_INDEMNITY, FEES_INTEREST, FINANCIAL_CONDITION_NO_MAC, FINANCIAL_RATIO_COVENANT, FINANCIAL_REPORTING, GOVERNING_LAW_JURISDICTION, INCREASED_COSTS_ILLEGALITY, INVESTMENT_COMPANY, JURY_TRIAL_WAIVER, LIENS, LITIGATION, MAINTENANCE_INSURANCE, MITIGATION_REPLACEMENT, NOTICES_COMMUNICATIONS, NO_FIDUCIARY_DUTY, PAYMENTS_SHARING, REPAYMENT_PREPAYMENT, SANCTIONS_AML, SUCCESSORS_ASSIGNS, TAXES, WAIVERS_AMENDMENTS.
- **Tier 2, Brier only (24):** AFFILIATE_TRANSACTIONS, AGENT_PROVISIONS, AMEND_RESTATE_EXISTING, BOOKS_INSPECTION, COMPLIANCE_WITH_LAWS, ENVIRONMENTAL, ERRONEOUS_PAYMENTS, EVENTS_OF_DEFAULT_LIST, FULL_DISCLOSURE, FUNDAMENTAL_CHANGES, GUARANTEE_TERMS, INDEBTEDNESS, INTEREST_RATE_LIMITATION, JUDGMENT_CURRENCY, MARGIN_REGULATIONS, NOTICE_OF_EVENTS, NO_DEFAULT, PARI_PASSU, PAYMENT_OF_OBLIGATIONS, SETOFF, SEVERABILITY, SUBSIDIARIES, SURVIVAL, USE_OF_PROCEEDS.

### CA-OLDDOMINION:SECTION (SECTION; law given to the predictor: STATE_OF_NEW_YORK)

Scope: **all top-level units of CA-OLDDOMINION**. POST-FREEZE replacement for CA-MOTOROLA (an amendment, screened out after the freeze). Title observed: 'SECOND AMENDED AND RESTATED CREDIT AGREEMENT'. The reviewer should confirm it is a complete restated agreement, not an amendment. TOC lists no sections under Article 7 (EVENTS OF DEFAULT).

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P3 | Article 1 | DEFINITIONS <br><sub>8 sections: 1.01 Defined Terms · 1.02 Terms Generally · 1.03 Accounting Terms; GAAP · 1.04 Classification of Loans and Borrowings · 1.05 Times of Day · 1.06 Amendment and Restatement of Existing Credit Agreement · 1.07 Divisions · 1.08 Rates</sub> | DEFINITIONS | DEFINITIONS <- heading keyword 'definition' (first match wins) | — |
| P3 | Article 2 | THE CREDITS <br><sub>24 sections: 2.01 The Commitments · 2.02 Loans and Borrowings · 2.03 Requests for Syndicated Borrowings · 2.04 Letters of Credit · 2.05 Funding of Borrowings · 2.06 Interest Elections · 2.07 Termination and Reduction of the Commitments · 2.08 Repayment of Loans: Evidence of Debt · 2.09 Prepayment of Loans · 2.10 Fees · 2.11 Interest · 2.12 Inability to Determine Rates · 2.13 Increased Costs; Illegality · 2.14 Compensation for Los…</sub> | CREDIT_FACILITIES | CREDIT_FACILITIES <- heading keyword 'credits' (first match wins) | — |
| P3 | Article 3 | REPRESENTATIONS AND WARRANTIES <br><sub>17 sections: 3.01 Organization; Powers · 3.02 Authorization; Enforceability · 3.03 Governmental Approvals; No Conflicts · 3.04 Financial Condition: No Material Adverse Change · 3.05 Properties · 3.06 Litigation · 3.07 Environmental Matters · 3.08 Compliance with Laws and Agreements · 3.09 Investment Status · 3.10 Taxes · 3.11 ERISA · 3.12 Disclosure · 3.13 Margin Stock · 3.14 Wholesale Power Contracts · 3.15 Sanctions; Anti-Corru…</sub> | REPRESENTATIONS | REPRESENTATIONS <- heading keyword 'representation' (first match wins) | — |
| P1 | **Article 4** | CONDITIONS <br><sub>2 sections: 4.01 Effective Date · 4.02 Each Credit Event</sub> | CONDITIONS_PRECEDENT | CONDITIONS_PRECEDENT <- heading keyword 'condition' (first match wins) | carries hidden positive(s): CONDITIONS_PRECEDENT |
| P2 | Article 5 | AFFIRMATIVE COVENANTS <br><sub>13 sections: 5.01 Financial Statements and Other Information · 5.02 Notices of Material Events · 5.03 Existence; Conduct of Business · 5.04 Payment of Obligations; Taxes · 5.05 Books and Records; Inspection Rights · 5.06 Compliance with Laws and Agreements · 5.07 Use of Proceeds · 5.08 Further Assurances · 5.09 Identification of Parties · 5.10 Certain Equity and Security · 5.11 Compliance with Laws Policies · 5.12 Ranking · 5.13 …</sub> | AFFIRMATIVE_COVENANTS | AFFIRMATIVE_COVENANTS <- heading keyword 'affirmative covenant' (first match wins) | multi-match: COVENANTS_COMBINED ('covenant') |
| P1 | **Article 6** | NEGATIVE COVENANTS <br><sub>9 sections: 6.01 Liens · 6.02 Fundamental Changes · 6.03 Lines of Business · 6.04 Transactions with Affiliates · 6.05 Certain Financial Covenants · 6.06 Hedging Agreements · 6.07 Wholesale Power Contracts · 6.08 Corporate Documents; Fiscal Year · 6.09 Sanctions; Anti-Corruption; Use of Proceeds</sub> | NEGATIVE_COVENANTS | NEGATIVE_COVENANTS <- heading keyword 'negative covenant' (first match wins) | carries hidden positive(s): NEGATIVE_COVENANTS \|\| multi-match: COVENANTS_COMBINED ('covenant') |
| P3 | Article 7 | EVENTS OF DEFAULT <br><sub>0 sections: </sub> | EVENTS_OF_DEFAULT | EVENTS_OF_DEFAULT <- heading keyword 'default' (first match wins) | — |
| P3 | Article 8 | AGENCY <br><sub>12 sections: 8.01 Appointment and Authority · 8.02 Rights as a Lender · 8.03 Exculpatory Provisions · 8.04 Reliance by Administrative Agent · 8.05 Delegation of Duties · 8.06 Resignation of Administrative Agent · 8.07 Non-Reliance on Administrative Agent and Other Lenders · 8.08 No Other Duties, etc · 8.09 Indemnity · 8.10 Administrative Agent May File Proofs of Claim · 8.11 Certain ERISA Matters · 8.12 Erroneous Payments</sub> | AGENCY | AGENCY <- heading keyword 'agency' (first match wins) | — |
| P3 | Article 9 | MISCELLANEOUS <br><sub>17 sections: 9.01 Notices · 9.02 Waivers; Amendments · 9.03 Expenses; Indemnity; Damage Waiver · 9.04 Successors and Assigns · 9.05 Survival · 9.06 Counterparts; Integration; Effectiveness · 9.07 Severability · 9.08 Right of Setoff · 9.09 Governing Law; Jurisdiction; Etc · 9.10 WAIVER OF JURY TRIAL · 9.11 Headings · 9.12 Treatment of Certain Information; Confidentiality · 9.13 USA PATRIOT Act · 9.14 No Advisory or Fiduciary Respo…</sub> | MISCELLANEOUS | MISCELLANEOUS <- heading keyword 'miscellaneous' (first match wins) | — |

- **Tier 1A (2):** CONDITIONS_PRECEDENT, NEGATIVE_COVENANTS
- **Tier 1B (5):** mass ≥ 0.25: CLAIM_PROCEDURE [G 0.75], COVENANTS_COMBINED [F 1.0/FS 1.0], CREDIT_CALCULATION_APPLICATION [G 0.75], CREDIT_SCHEDULE [G 0.75], GUARANTY [F 1.0/FS 1.0]. Tie-share only (< 0.25): 0 types — —.
- **Tier 2, Brier only (9):** CREDIT_CAP, EXCLUSIONS, FINANCIAL_COVENANTS, MEASUREMENT_METHOD, SCOPE_APPLICABILITY, SERVICE_COMMITMENT, SOLE_REMEDY, TERMINATION_RIGHT, YIELD_PROTECTION_TAXES.

### CA-OLDDOMINION:Article 6 (PROVISION; law given to the predictor: STATE_OF_NEW_YORK)

Scope: **Article 6 'NEGATIVE COVENANTS'** → section function `NEGATIVE_COVENANTS` (itself an agent label; validate it in the SECTION case of CA-OLDDOMINION).

> **Sparse-support backoff case.** CONTEXT_CONFLICT backoff fired: fewer than 50% of the VISIBLE provision labels have support under this section function in training (only CA-BESTBUY splits affirmative/negative covenants). The predictor fell back to the family-wide distribution, producing a large alphabetical tie. RESULTS.md calls this 'sparse support read as conflict'. Visible-label errors (see multi-match flags) also enter this consistency check, so human labels for the VISIBLE units matter here, not only for the targets.

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P1 | **Section 6.01** | Liens | LIENS | LIENS <- heading keyword 'liens' (first match wins) | carries hidden positive(s): LIENS |
| P1 | **Section 6.02** | Fundamental Changes | FUNDAMENTAL_CHANGES | FUNDAMENTAL_CHANGES <- heading keyword 'fundamental change' (first match wins) | carries hidden positive(s): FUNDAMENTAL_CHANGES |
| P2 | Section 6.03 | Lines of Business | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P3 | Section 6.04 | Transactions with Affiliates | AFFILIATE_TRANSACTIONS | AFFILIATE_TRANSACTIONS <- heading keyword 'transactions with affiliates' (first match wins) | — |
| P3 | Section 6.05 | Certain Financial Covenants | FINANCIAL_RATIO_COVENANT | FINANCIAL_RATIO_COVENANT <- heading keyword 'financial covenants' (first match wins) | — |
| P2 | Section 6.06 | Hedging Agreements | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 6.07 | Wholesale Power Contracts | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 6.08 | Corporate Documents; Fiscal Year | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 6.09 | Sanctions; Anti-Corruption; Use of Proceeds | SANCTIONS_AML | SANCTIONS_AML <- heading keyword 'sanction' (first match wins) | multi-match: USE_OF_PROCEEDS ('use of proceeds') |

- **Tier 1A (2):** FUNDAMENTAL_CHANGES, LIENS
- **Tier 1B (32):** mass ≥ 0.25: —. Tie-share only (< 0.25): 32 types — ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS, COMMITMENT_CHANGES, CONDITIONS_EFFECTIVENESS, CONFIDENTIALITY, COUNTERPARTS_INTEGRATION, DEFAULTING_LENDERS, DEFINED_TERMS, ERISA, EXISTENCE_ORGANIZATION, EXPENSES_INDEMNITY, FEES_INTEREST, FINANCIAL_CONDITION_NO_MAC, FINANCIAL_REPORTING, GOVERNING_LAW_JURISDICTION, INCREASED_COSTS_ILLEGALITY, INTERPRETATION, INVESTMENT_COMPANY, JURY_TRIAL_WAIVER, LITIGATION, MAINTENANCE_INSURANCE, MITIGATION_REPLACEMENT, NOTICES_COMMUNICATIONS, NO_FIDUCIARY_DUTY, PAYMENTS_SHARING, REPAYMENT_PREPAYMENT, SUCCESSORS_ASSIGNS, TAXES, WAIVERS_AMENDMENTS.
- **Tier 2, Brier only (23):** AGENT_PROVISIONS, AMEND_RESTATE_EXISTING, BOOKS_INSPECTION, COMPLIANCE_WITH_LAWS, ENVIRONMENTAL, ERRONEOUS_PAYMENTS, EVENTS_OF_DEFAULT_LIST, FULL_DISCLOSURE, GUARANTEE_TERMS, INDEBTEDNESS, INTEREST_RATE_LIMITATION, JUDGMENT_CURRENCY, LETTERS_OF_CREDIT, MARGIN_REGULATIONS, NOTICE_OF_EVENTS, NO_DEFAULT, PARI_PASSU, PAYMENT_OF_OBLIGATIONS, SETOFF, SEVERABILITY, SUBSIDIARIES, SURVIVAL, USE_OF_PROCEEDS.

### CA-OLDDOMINION:Article 5 (PROVISION; law given to the predictor: STATE_OF_NEW_YORK)

Scope: **Article 5 'AFFIRMATIVE COVENANTS'** → section function `AFFIRMATIVE_COVENANTS` (itself an agent label; validate it in the SECTION case of CA-OLDDOMINION).

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P1 | **Section 5.01** | Financial Statements and Other Information | FINANCIAL_REPORTING | FINANCIAL_REPORTING <- heading keyword 'financial statements' (first match wins) | carries hidden positive(s): FINANCIAL_REPORTING |
| P3 | Section 5.02 | Notices of Material Events | NOTICE_OF_EVENTS | NOTICE_OF_EVENTS <- heading keyword 'notices of material events' (first match wins) | — |
| P3 | Section 5.03 | Existence; Conduct of Business | EXISTENCE_ORGANIZATION | EXISTENCE_ORGANIZATION <- heading keyword 'existence' (first match wins) | — |
| P2 | Section 5.04 | Payment of Obligations; Taxes | TAXES | TAXES <- heading keyword 'taxes' (first match wins) | multi-match: PAYMENT_OF_OBLIGATIONS ('payment of obligations') |
| P1 | **Section 5.05** | Books and Records; Inspection Rights | BOOKS_INSPECTION | BOOKS_INSPECTION <- heading keyword 'books' (first match wins) | carries hidden positive(s): BOOKS_INSPECTION |
| P3 | Section 5.06 | Compliance with Laws and Agreements | COMPLIANCE_WITH_LAWS | COMPLIANCE_WITH_LAWS <- heading keyword 'compliance with laws' (first match wins) | — |
| P3 | Section 5.07 | Use of Proceeds | USE_OF_PROCEEDS | USE_OF_PROCEEDS <- heading keyword 'use of proceeds' (first match wins) | — |
| P2 | Section 5.08 | Further Assurances | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 5.09 | Identification of Parties | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P2 | Section 5.10 | Certain Equity and Security | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P3 | Section 5.11 | Compliance with Laws Policies | COMPLIANCE_WITH_LAWS | COMPLIANCE_WITH_LAWS <- heading keyword 'compliance with laws' (first match wins) | — |
| P2 | Section 5.12 | Ranking | OTHER | no rule matched heading -> OTHER | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |
| P3 | Section 5.13 | Letter of Credit Diligence | LETTERS_OF_CREDIT | LETTERS_OF_CREDIT <- heading keyword 'letter of credit' (first match wins) | — |

- **Tier 1A (2):** BOOKS_INSPECTION, FINANCIAL_REPORTING
- **Tier 1B (32):** mass ≥ 0.25: MAINTENANCE_INSURANCE [G 0.091/F 0.091/FS 1.0]. Tie-share only (< 0.25): 31 types — ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS, COMMITMENT_CHANGES, CONDITIONS_EFFECTIVENESS, CONFIDENTIALITY, COUNTERPARTS_INTEGRATION, DEFAULTING_LENDERS, DEFINED_TERMS, ERISA, EXPENSES_INDEMNITY, FEES_INTEREST, FINANCIAL_CONDITION_NO_MAC, FINANCIAL_RATIO_COVENANT, GOVERNING_LAW_JURISDICTION, INCREASED_COSTS_ILLEGALITY, INTERPRETATION, INVESTMENT_COMPANY, JURY_TRIAL_WAIVER, LIENS, LITIGATION, MITIGATION_REPLACEMENT, NOTICES_COMMUNICATIONS, NO_FIDUCIARY_DUTY, PAYMENTS_SHARING, REPAYMENT_PREPAYMENT, SANCTIONS_AML, SUCCESSORS_ASSIGNS, WAIVERS_AMENDMENTS.
- **Tier 2, Brier only (20):** AFFILIATE_TRANSACTIONS, AGENT_PROVISIONS, AMEND_RESTATE_EXISTING, ENVIRONMENTAL, ERRONEOUS_PAYMENTS, EVENTS_OF_DEFAULT_LIST, FULL_DISCLOSURE, FUNDAMENTAL_CHANGES, GUARANTEE_TERMS, INDEBTEDNESS, INTEREST_RATE_LIMITATION, JUDGMENT_CURRENCY, MARGIN_REGULATIONS, NO_DEFAULT, PARI_PASSU, PAYMENT_OF_OBLIGATIONS, SETOFF, SEVERABILITY, SUBSIDIARIES, SURVIVAL.

### SLA-CLOUDFLARE:SECTION (SECTION; law given to the predictor: UNKNOWN)

Scope: **all top-level units of SLA-CLOUDFLARE**. POST-FREEZE segmentation (numbered-paragraph fallback written after the frozen run returned SLA_TITLE_NOT_FOUND). Headings are truncated at the first word after the number (e.g. '3. Service' for '3. Service Credit Claims'); unit boundaries themselves are unvalidated.

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P2 | Unit 1 | HEADING_ABSENT | OTHER | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) \|\| heading truncated by post-freeze fallback |
| P2 | Unit 2 | 1. Business | OTHER | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) \|\| RECORDED V3 ERROR CANDIDATE: RESULTS.md: '1. Business SLA' is a service commitment ('commits to provide') that the rule does not catch -> labelled OTHER. If true, SERVICE_COMMITMENT is VISIBLE in this document. \|\| heading truncated by post-freeze fallback |
| P1 | **Unit 3** | 2. Definitions | DEFINITIONS+CREDIT_CALCULATION_APPLICATION | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | carries hidden positive(s): DEFINITIONS, CREDIT_CALCULATION_APPLICATION \|\| heading truncated by post-freeze fallback |
| P2 | Unit 4 | 3. Service | CLAIM_PROCEDURE | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | heading truncated by post-freeze fallback |
| P1 | **Unit 5** | 4. SLA | EXCLUSIONS | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | carries hidden positive(s): EXCLUSIONS \|\| heading truncated by post-freeze fallback |
| P2 | Unit 6 | 5. Service | SOLE_REMEDY | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | heading truncated by post-freeze fallback |
| P2 | Unit 7 | 6. Service | OTHER | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) \|\| RECORDED V3 ERROR CANDIDATE: RESULTS.md: '6. Service Credit Calculation' was missed by the credit-calculation rule -> labelled OTHER. If true, CREDIT_CALCULATION_APPLICATION is VISIBLE, so it cannot be a hidden positive of this case. \|\| heading truncated by post-freeze fallback |
| P2 | Unit 8 | 7. Methodology | OTHER | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) \|\| heading truncated by post-freeze fallback |

- **Tier 1A (3):** CREDIT_CALCULATION_APPLICATION, DEFINITIONS, EXCLUSIONS (collateral: DEFINITIONS)
- **Tier 1B (7):** mass ≥ 0.25: AGENCY [G 0.25], CONDITIONS_PRECEDENT [G 0.25], CREDIT_FACILITIES [G 0.25], CREDIT_SCHEDULE [G 0.25/F 1.0/FS 1.0], EVENTS_OF_DEFAULT [G 0.25], MISCELLANEOUS [G 0.25], REPRESENTATIONS [G 0.25]. Tie-share only (< 0.25): 0 types — —.
- **Tier 2, Brier only (11):** AFFIRMATIVE_COVENANTS, COVENANTS_COMBINED, CREDIT_CAP, FINANCIAL_COVENANTS, GUARANTY, MEASUREMENT_METHOD, NEGATIVE_COVENANTS, SCOPE_APPLICABILITY, SERVICE_COMMITMENT, TERMINATION_RIGHT, YIELD_PROTECTION_TAXES.

### SLA-MONGODB:SECTION (SECTION; law given to the predictor: UNKNOWN)

Scope: **all top-level units of SLA-MONGODB**. Frozen pipeline (pre-registered primary and secondary). 5 units only.

| Pri | Unit | Verbatim heading | Agent label(s) | Assigned by (frozen rule) | Flags for the reviewer |
|---|---|---|---|---|---|
| P1 | **Unit 1** | HEADING_ABSENT | CREDIT_SCHEDULE+EXCLUSIONS | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | carries hidden positive(s): CREDIT_SCHEDULE, EXCLUSIONS |
| P3 | Unit 2 | Definitions | DEFINITIONS+CREDIT_CALCULATION_APPLICATION | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | — |
| P3 | Unit 3 | Customer Obligations | CLAIM_PROCEDURE | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | — |
| P1 | **Unit 4** | Service Credits | CREDIT_CALCULATION_APPLICATION+SOLE_REMEDY | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | carries hidden positive(s): SOLE_REMEDY |
| P2 | Unit 5 | Limitations | OTHER | multi-label rules over heading + unit TEXT (text not in repo; see unit_text_sha256) | OTHER: may carry a vocabulary type (a hidden positive would then be VISIBLE, or a negative PRESENT) |

- **Tier 1A (3):** CREDIT_SCHEDULE, EXCLUSIONS, SOLE_REMEDY (collateral: EXCLUSIONS)
- **Tier 1B (9):** mass ≥ 0.25: AGENCY [G 0.429], CONDITIONS_PRECEDENT [G 0.429], CREDIT_CAP [F 0.4/FS 0.4], CREDIT_FACILITIES [G 0.429], EVENTS_OF_DEFAULT [G 0.429], MISCELLANEOUS [G 0.429], REPRESENTATIONS [G 0.429], SCOPE_APPLICABILITY [F 0.4/FS 0.4], SERVICE_COMMITMENT [F 0.4/FS 0.4]. Tie-share only (< 0.25): 0 types — —.
- **Tier 2, Brier only (8):** AFFIRMATIVE_COVENANTS, COVENANTS_COMBINED, FINANCIAL_COVENANTS, GUARANTY, MEASUREMENT_METHOD, NEGATIVE_COVENANTS, TERMINATION_RIGHT, YIELD_PROTECTION_TAXES.

## 5. Pre-registered rule for applying the adjudication (fixed before any human verdict)

1. **What the reviewer produces.** One complete label set per unit in `review_units.csv`, using the frozen vocabulary (plus OTHER and RESERVED). The frozen files under `../data`, `../results` and `../frozen` are never edited.
2. **Derived sets per case.**
   - **Positives:** types carried by a masked unit and by **no** visible unit in scope.
   - **Negatives:** vocabulary types carried by **no** unit in scope.
   - **Removed from candidates:** a type carried by a visible unit.
   - **No positives left:** the case is reported as `TARGET_LEAKED_OR_EMPTY` and dropped from the re-score. It is not repaired.
3. **Re-score A (labels only).** Keep the frozen predictions. Drop removed candidates from each ranked list without renormalising. Apply the frozen `predict.score_case`, `summarize` and `decide`. Output to `results/adjudicated_secondary_rescore_A.json`, labelled `POST_HOC_HUMAN_ADJUDICATED_SECONDARY`.
4. **Re-score B (context corrected).** Required only if any **visible** label changes. Rebuild the case context from the human labels and re-run the frozen `predict.predict` (training labels unchanged). Output to `results/adjudicated_secondary_rescore_B.json`. If a section function changes, the provision case is re-run under the human section function.
5. **`UNSURE` units.** Report lower and upper bounds (UNSURE resolved against and for each arm). Do not choose a single value.
6. **What stays fixed.**
   - The pre-registered primary stays `INCONCLUSIVE`.
   - The re-score is still a **post-freeze secondary on agent-chosen documents**.
   - It **cannot** satisfy the gate to a Jev test, which requires ≥ 6 fresh, human-adjudicated documents.
   - Training labels remain agent-authored.
   - No rule, vocabulary or predictor change is made on the basis of these verdicts within V3.

## 6. Label glossary: the frozen operational definitions

The vocabulary has **no prose definitions**; each label is defined only by the frozen rule below (`../labels.py`, first match wins for credit agreements, multi-label for SLAs). Judge each unit by **meaning**, using the rule as a pointer to the intended category. Where the intended category is unclear, use `UNSURE` and say so: an unclear category is itself a finding about the vocabulary.

Structural notes:
- `COVENANTS_COMBINED` catches any 'covenant' heading not already caught by AFFIRMATIVE_/NEGATIVE_/FINANCIAL_COVENANTS. It is a top-3 false expectation for F and FS in both credit-agreement SECTION cases, so decide whether a combined-covenants article exists.
- `CREDIT_SCHEDULE` is computed: at least 2 band boundaries such as 'less than 99.9%'.
- `OTHER` and `RESERVED` are never targets or candidates.

| Task | Label | Frozen rule pattern (lower-cased heading; SLA: heading + text) |
|---|---|---|
| SECTION (credit agreement) | `DEFINITIONS` | `definition\|interpretation` |
| SECTION (credit agreement) | `AFFIRMATIVE_COVENANTS` | `affirmative covenant` |
| SECTION (credit agreement) | `NEGATIVE_COVENANTS` | `negative covenant` |
| SECTION (credit agreement) | `FINANCIAL_COVENANTS` | `financial covenant` |
| SECTION (credit agreement) | `COVENANTS_COMBINED` | `covenant` |
| SECTION (credit agreement) | `GUARANTY` | `guarant` |
| SECTION (credit agreement) | `REPRESENTATIONS` | `representation` |
| SECTION (credit agreement) | `CONDITIONS_PRECEDENT` | `condition` |
| SECTION (credit agreement) | `EVENTS_OF_DEFAULT` | `default` |
| SECTION (credit agreement) | `AGENCY` | `\bagen(t\|cy)\b` |
| SECTION (credit agreement) | `YIELD_PROTECTION_TAXES` | `change in circumstances\|yield protection\|increased cost\|taxes` |
| SECTION (credit agreement) | `CREDIT_FACILITIES` | `\bcredits?\b\|loans?\|commitments?\|facilit\|amount and terms` |
| SECTION (credit agreement) | `MISCELLANEOUS` | `miscellaneous\|general provisions` |
| SECTION (SLA) | `DEFINITIONS` | `(^\|\s)definitions?\b\|\"[^\"]{2,60}\" (means\|is\|are\|occurs)` |
| SECTION (SLA) | `SCOPE_APPLICABILITY` | `^appendix[^\n]{0,20}eligible\|policy governing the use\|applies separately to\|depend on the type of account\|(this\|the) (sla\|service level agreement) (applies\|governs)` |
| SECTION (SLA) | `SERVICE_COMMITMENT` | `(will\|must\|shall) (use commercially reasonable efforts to )?(provide\|make\|maintain)[^.]{0,200}\d{2}(\.\d+)?%\|(will\|must\|shall) provide an? (monthly )?(uptime\|availability) percentage` |
| SECTION (SLA) | `CREDIT_SCHEDULE` | `computed: >= 2 band boundaries (less than / below / < / - NN.N%)` |
| SECTION (SLA) | `CREDIT_CALCULATION_APPLICATION` | `credits? (are\|is\|will be) (calculated\|applied\|issued\|made)\|percentage of (the )?monthly (bill\|fees\|usage)\|credited to\|apply (any )?service credits\|applied (to\|against\|within)` |
| SECTION (SLA) | `CLAIM_PROCEDURE` | `(submit\|request\|notify\|open\|file)[^.]{0,80}(claim\|ticket\|case\|credit\|support)[^.]{0,120}within \d+\|must (submit\|request\|notify\|open)\|requests? for [^.]{0,40}credits?[^.]{0,40}must be made` |
| SECTION (SLA) | `CREDIT_CAP` | `maximum (aggregate )?(amount\|number)?[^.]{0,40}credits?\|credits?[^.]{0,120}(will\|shall) not exceed\|in no event[^.]{0,80}exceed` |
| SECTION (SLA) | `EXCLUSIONS` | `exclusions?\b\|(does\|do\|will) not apply to\|not entitled to (any )?service credits` |
| SECTION (SLA) | `SOLE_REMEDY` | `(sole\|exclusive) (and exclusive )?remed` |
| SECTION (SLA) | `TERMINATION_RIGHT` | `(right\|days) to terminate\|may terminate` |
| SECTION (SLA) | `MEASUREMENT_METHOD` | `(is\|are) (determined\|calculated) by subtracting\|^calculation$\|example calculation\|sampled every` |
| PROVISION (credit agreement) | `JURY_TRIAL_WAIVER` | `jury` |
| PROVISION (credit agreement) | `COUNTERPARTS_INTEGRATION` | `counterparts\|integration\|electronic (execution\|records)` |
| PROVISION (credit agreement) | `GOVERNING_LAW_JURISDICTION` | `governing law\|new york law\|judicial proceedings\|jurisdiction` |
| PROVISION (credit agreement) | `BAIL_IN_QFC` | `bail-in\|affected financial\|qfc\|covered entit` |
| PROVISION (credit agreement) | `ERRONEOUS_PAYMENTS` | `erroneous` |
| PROVISION (credit agreement) | `SANCTIONS_AML` | `sanction\|anti-terror\|anti-corruption\|patriot\|beneficial ownership` |
| PROVISION (credit agreement) | `ERISA` | `erisa` |
| PROVISION (credit agreement) | `DEFINED_TERMS` | `defined terms\|^definitions$` |
| PROVISION (credit agreement) | `ACCOUNTING_TERMS` | `accounting terms\|gaap` |
| PROVISION (credit agreement) | `BENCHMARK_RATES` | `benchmark\|alternate rate\|inability to determine\|substituted for\|^interest rates$` |
| PROVISION (credit agreement) | `AMEND_RESTATE_EXISTING` | `amendment and restatement` |
| PROVISION (credit agreement) | `INTERPRETATION` | `terms generally\|interpretive\|classification of loans\|types of borrowings\|divisions\|^headings$` |
| PROVISION (credit agreement) | `LETTERS_OF_CREDIT` | `letters? of credit\|lc disbursement\|issuance and administration` |
| PROVISION (credit agreement) | `COMMITMENT_CHANGES` | `termination, reduction\|changes of commitments\|expansion option\|increase of\|extension of` |
| PROVISION (credit agreement) | `COMMITMENTS_BORROWINGS` | `commitments\|loans and borrowings\|^loans$\|requests? for\|notice of borrowings\|funding of (loans\|borrowings)\|interest elections\|competitive bid\|borrowings by` |
| PROVISION (credit agreement) | `REPAYMENT_PREPAYMENT` | `repayment\|prepayment\|evidence of\|maturity` |
| PROVISION (credit agreement) | `FEES_INTEREST` | `^fees$\|^interest$\|interest rates of loans\|computation of interest\|agent'?s fee` |
| PROVISION (credit agreement) | `INCREASED_COSTS_ILLEGALITY` | `increased cost\|illegality\|break funding\|funding losses` |
| PROVISION (credit agreement) | `TAXES` | `taxes` |
| PROVISION (credit agreement) | `PAYMENTS_SHARING` | `payments generally\|sharing of payments\|pro rata` |
| PROVISION (credit agreement) | `MITIGATION_REPLACEMENT` | `mitigation\|replacement of` |
| PROVISION (credit agreement) | `DEFAULTING_LENDERS` | `defaulting` |
| PROVISION (credit agreement) | `INTEREST_RATE_LIMITATION` | `interest rate limitation\|usury` |
| PROVISION (credit agreement) | `GUARANTEE_TERMS` | `guarant\|subrogation\|reinstatement\|obligations unconditional\|^remedies$\|contribution\|discharge only\|waiver by the company\|instrument for the payment` |
| PROVISION (credit agreement) | `CONDITIONS_EFFECTIVENESS` | `effective date\|effectiveness\|each credit\|initial loan` |
| PROVISION (credit agreement) | `EXISTENCE_ORGANIZATION` | `existence\|^organization\|conduct of business` |
| PROVISION (credit agreement) | `AUTHORIZATION_ENFORCEABILITY` | `authorization\|corporate action\|binding effect\|enforceab\|approvals\|no breach\|no conflicts` |
| PROVISION (credit agreement) | `FINANCIAL_CONDITION_NO_MAC` | `financial condition\|financial information\|material adverse` |
| PROVISION (credit agreement) | `LITIGATION` | `litigation` |
| PROVISION (credit agreement) | `INVESTMENT_COMPANY` | `investment company` |
| PROVISION (credit agreement) | `ENVIRONMENTAL` | `environmental\|hazardous` |
| PROVISION (credit agreement) | `FULL_DISCLOSURE` | `disclosure` |
| PROVISION (credit agreement) | `MARGIN_REGULATIONS` | `margin\|federal reserve` |
| PROVISION (credit agreement) | `PARI_PASSU` | `pari passu` |
| PROVISION (credit agreement) | `NO_DEFAULT` | `^no default` |
| PROVISION (credit agreement) | `FINANCIAL_REPORTING` | `financial statements\|^information$\|reporting` |
| PROVISION (credit agreement) | `NOTICE_OF_EVENTS` | `notices? of (material )?events\|notice of default` |
| PROVISION (credit agreement) | `PAYMENT_OF_OBLIGATIONS` | `payment of obligations` |
| PROVISION (credit agreement) | `MAINTENANCE_INSURANCE` | `insurance\|maintenance of propert` |
| PROVISION (credit agreement) | `BOOKS_INSPECTION` | `inspection\|books` |
| PROVISION (credit agreement) | `COMPLIANCE_WITH_LAWS` | `compliance with laws` |
| PROVISION (credit agreement) | `USE_OF_PROCEEDS` | `use of (proceeds\|credit\|loans)` |
| PROVISION (credit agreement) | `FINANCIAL_RATIO_COVENANT` | `ratio\|net worth\|financial covenants` |
| PROVISION (credit agreement) | `LIENS` | `liens\|negative pledge` |
| PROVISION (credit agreement) | `FUNDAMENTAL_CHANGES` | `fundamental change\|consolidation\|merger\|sales? of assets` |
| PROVISION (credit agreement) | `INDEBTEDNESS` | `indebtedness\|certain debt` |
| PROVISION (credit agreement) | `AFFILIATE_TRANSACTIONS` | `transactions with affiliates` |
| PROVISION (credit agreement) | `SUBSIDIARIES` | `subsidiar` |
| PROVISION (credit agreement) | `EVENTS_OF_DEFAULT_LIST` | `events of default` |
| PROVISION (credit agreement) | `EXPENSES_INDEMNITY` | `expenses\|indemn` |
| PROVISION (credit agreement) | `AGENT_PROVISIONS` | `agent\|arrangers\|credit decision\|consultation with experts\|acknowledgments of lenders\|authorization and action\|delegation` |
| PROVISION (credit agreement) | `NOTICES_COMMUNICATIONS` | `^notices$\|posting of communications` |
| PROVISION (credit agreement) | `WAIVERS_AMENDMENTS` | `waiver\|amendment` |
| PROVISION (credit agreement) | `SUCCESSORS_ASSIGNS` | `successors\|assign` |
| PROVISION (credit agreement) | `SURVIVAL` | `survival` |
| PROVISION (credit agreement) | `SEVERABILITY` | `severab\|unenforceab` |
| PROVISION (credit agreement) | `SETOFF` | `setoff\|set-off` |
| PROVISION (credit agreement) | `CONFIDENTIALITY` | `confidential\|non-public` |
| PROVISION (credit agreement) | `NO_FIDUCIARY_DUTY` | `fiduciary` |
| PROVISION (credit agreement) | `JUDGMENT_CURRENCY` | `judgment currency` |

## 7. Files

| File | Role |
|---|---|
| `review_units.csv` | **Worksheet to fill** (78 units, P1→P3; reviewer columns empty) |
| `review_labels.csv` | Derived label view: 18 positives + 275 negatives with tier, top-3 mass, p and the units that resolve each label (do not fill) |
| `fetch_local_evidence.py` | Operator-run retrieval: SHA-256 check, rebuild with frozen code, identity check against committed records, passages into git-ignored `local_evidence/` |
| `build_review_package.py` | Regenerates this package offline and deterministically |
| `package_manifest.json` | Input hashes and counts |
| `test_adjudication.py` | Offline tests: frozen files untouched, counts, determinism, retrieval plumbing (synthetic) |
| `ADJUDICATION_TASK_PROMPT.md` | The task as given, constraints, charter anchor |

