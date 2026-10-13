# V3 masked contract-structure prediction: RESULTS

**Date:** 2026-10-13. **Provider calls: 0.** Offline, standard library, deterministic. Protocol: [PROTOCOL.md](PROTOCOL.md), frozen at commit `e205a3b` (pushed before any heldout document was parsed; `frozen/freeze_receipt.json`).

## Verdict

- **Pre-registered primary (frozen run): `INCONCLUSIVE`.** Two of the four heldout documents failed segmentation, leaving 9 scorable targets. The fixed negative-control subset landed on exactly those two failed documents, so the "observable backoff" check could not pass.
- **Secondary (post-freeze segmentation repair, *not* pre-registered): `PREDICTIVE_SIGNAL_PROVISIONAL`** under the same frozen rule, on 18 targets across 4 documents.
- **What the signal actually is:**
  1. **Provision-in-section conditioning helps ranking.** Knowing *which article* a hidden subsection belongs to moved targets into the top-3 that family-level frequency could not rank: FAMILY_SECTION 3.09/8 vs FAMILY 0.36/8 vs GLOBAL 0.36/8 provision targets in top-3.
  2. **Section level adds nothing beyond family.** Conditioning on the other observed sections gave *exactly* FAMILY's result (6.80/10 for both). Most of the section-task gain over GLOBAL is simply knowing the contract family, and GLOBAL is a weak baseline here because it mixes two unrelated families.
  3. **The proper scoring rule does not favour the funnel over GLOBAL.** Brier: FAMILY_SECTION 0.256 vs GLOBAL 0.183 (secondary); 0.240 vs 0.185 (primary). The context arms are over-confident about family-typical types that are absent from a given section. FAMILY_SECTION does beat FAMILY on Brier (0.256 vs 0.343).
  4. **Law: `LAW_EFFECT_UNTESTABLE` everywhere.** Every evidenced credit-agreement law is New York, and every SLA is `UNKNOWN`. No law-layer benefit is claimed. Wrong-law inferences: **0**. SLAs stayed `UNKNOWN`. When the choice-of-law article was masked (Markel), law correctly fell back to `UNKNOWN`.
  5. **The context-conflict backoff misfired on real data.** In 2 of the 4 real provision cases (Markel art. 7 *Affirmative Covenants*, Old Dominion art. 6 *Negative Covenants*), only one training document (Best Buy) has split affirmative/negative covenant articles. The predictor read that *sparse support* as a *conflicting context*, backed off, and lost the signal (0.0 and 0.09 hits).
     - Post-hoc diagnostic only, not used for the decision ([results/posthoc_no_conflict_backoff.json](results/posthoc_no_conflict_backoff.json)): with the backoff disabled, secondary provision hit@3 would be 5.0/8.
     - The backoff did work on the family-swap negative controls (secondary: 2/2 flagged; FAMILY_SECTION recovered 2.0 hits each, FAMILY 0.0 and 1.0).
     - A **wrong-but-plausible section label** (Affirmative Covenants → Representations) was **not detected**, and the predictions silently shifted to representation-type provisions.

**Net:** this is an *engineering signal* that a hierarchical, section-conditioned prior carries ranking information beyond family frequency, **at the provision-within-section level only**, on 4 heldout documents with agent-authored labels. It is not calibrated and not robust to plausible mislabeling. It establishes nothing about Jev extraction, interpretation accuracy, omission or defect detection, or BI value.

## Data actually used

| Doc | Family | Split | Segmentation | Evidenced law |
|---|---|---|---|---|
| CA-LINCOLN, CA-INTLPAPER, CA-BESTBUY, CA-EQUITABLE | credit agreement | TRAIN | TOC parse OK | NY (all 4) |
| SLA-AWS_EC2, SLA-GCP_COMPUTE (forced train), SLA-ATLASSIAN, SLA-FASTLY | vendor SLA | TRAIN | headings OK (Google: table-header noise) | UNKNOWN |
| CA-MARKEL | credit agreement | HELDOUT | OK | NY |
| CA-MOTOROLA | credit agreement | HELDOUT | **failed**: the exhibit is a *First Amendment* with a redlined conformed copy (corpus-screening error) | (amendment's own NY clause) |
| SLA-MONGODB | vendor SLA | HELDOUT | OK (5 units) | UNKNOWN |
| SLA-CLOUDFLARE | vendor SLA | HELDOUT | **failed** in the frozen run (no HTML headings; numbered paragraphs); fallback in the secondary run | UNKNOWN |
| CA-OLDDOMINION | credit agreement | secondary replacement | frozen parser OK | NY |

The replacement was the next unused EX-10 in the original EDGAR search order. Blue Owl Credit Income Corp. was screened out as an amendment. The full list of excluded candidates and reasons is in `data/source_manifest.json` and `data/records_heldout_secondary.json`.

**Training-set caveat:** Equitable and Lincoln are near-identical templates, so training support is effectively 3 credit-agreement styles.

## Per-case results

#### PRIMARY (frozen, pre-registered)

| Case | Hidden positives | GLOBAL top-3 | FAMILY top-3 | FAMILY_SECTION top-3 | hit@3 G / F / FS | false exp@3 G / F / FS | Brier G / F / FS | FS flags |
|---|---|---|---|---|---|---|---|---|
| CA-MOTOROLA:SECTION | — (segmentation failed) | DEFINITIONS, AGENCY, CLAIM_PROCEDURE | DEFINITIONS, AGENCY, CONDITIONS_PRECEDENT | DEFINITIONS, AGENCY, CONDITIONS_PRECEDENT | 0.00 / 0.00 / 0.00 | 3.00 / 3.00 / 3.00 | 0.193 / 0.310 / 0.357 | — |
| CA-MARKEL:SECTION | AGENCY, MISCELLANEOUS | AGENCY, CLAIM_PROCEDURE, CREDIT_CALCULATION_APPLICATION | AGENCY, MISCELLANEOUS, COVENANTS_COMBINED | AGENCY, MISCELLANEOUS, COVENANTS_COMBINED | 1.20 / 2.00 / 2.00 | 1.80 / 1.00 / 1.00 | 0.156 / 0.050 / 0.024 | — |
| CA-MARKEL:Article 7 | USE_OF_PROCEEDS, BOOKS_INSPECTION | BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS | BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS | BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS | 0.00 / 0.00 / 0.00 | 3.00 / 3.00 / 3.00 | 0.195 / 0.574 / 0.574 | CONTEXT_CONFLICT(consistency=0.38)_BACKOFF |
| CA-MARKEL:Article 1 | INTERPRETATION, DEFINED_TERMS | AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, BENCHMARK_RATES | AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, BENCHMARK_RATES | BENCHMARK_RATES, DEFINED_TERMS, INTERPRETATION | 0.18 / 0.18 / 2.00 | 2.82 / 2.82 / 1.00 | 0.195 / 0.589 / 0.082 | — |
| SLA-CLOUDFLARE:SECTION | — (segmentation failed) | DEFINITIONS, AGENCY, CLAIM_PROCEDURE | DEFINITIONS, CLAIM_PROCEDURE, CREDIT_CALCULATION_APPLICATION | DEFINITIONS, CLAIM_PROCEDURE, CREDIT_CALCULATION_APPLICATION | 0.00 / 0.00 / 0.00 | 3.00 / 3.00 / 3.00 | 0.193 / 0.263 / 0.299 | — |
| SLA-MONGODB:SECTION | CREDIT_SCHEDULE, EXCLUSIONS, SOLE_REMEDY | AGENCY, CONDITIONS_PRECEDENT, CREDIT_FACILITIES | CREDIT_SCHEDULE, CREDIT_CAP, EXCLUSIONS | CREDIT_SCHEDULE, CREDIT_CAP, EXCLUSIONS | 0.43 / 1.80 / 1.80 | 2.57 / 1.20 / 1.20 | 0.175 / 0.097 / 0.103 | — |

| Arm | targets | hit@1 | hit@3 | section hit@3 | provision hit@3 | false exp@3 | Brier | log loss |
|---|---|---|---|---|---|---|---|---|
| GLOBAL_FREQ | 9 | 0.60 | 1.80 | 1.63/5 | 0.18/4 | 16.20 | 0.1845 | 0.5610 |
| FAMILY | 9 | 2.06 | 3.98 | 3.80/5 | 0.18/4 | 14.02 | 0.3137 | 0.9213 |
| FAMILY_SECTION | 9 | 2.67 | 5.80 | 3.80/5 | 2.00/4 | 12.20 | 0.2398 | 0.8171 |
| EVIDENCED_LAW_FAMILY_SECTION | 9 | 2.67 | 5.80 | 3.80/5 | 2.00/4 | 12.20 | 0.2398 | 0.8171 |

Decision: {"decision": "INCONCLUSIVE", "hurdle_met": false, "checks": {"global_top3_rate": 0.201, "ceiling_effect": false, "fs_minus_global_hit3": 3.995, "fs_gain_docs": ["CA-MARKEL", "SLA-MONGODB"], "fs_false_exp_not_worse_than_global": true, "observable_backoff_in_negative_controls": 0, "fs_minus_family_hit3": 1.8239999999999998, "fs_minus_family_brier": -0.0739, "fs_minus_global_brier": 0.0553}}

Negative controls:
- `CA-MARKEL:Article 7` (section AFFIRMATIVE_COVENANTS -> REPRESENTATIONS): FAMILY hit@3=0.0, flags=—; FAMILY_SECTION hit@3=0.0, flags=—
- `CA-MOTOROLA:SECTION` (family CREDIT_AGREEMENT -> VENDOR_SLA): FAMILY hit@3=0, flags=—; FAMILY_SECTION hit@3=0, flags=—
- `SLA-CLOUDFLARE:SECTION` (family VENDOR_SLA -> CREDIT_AGREEMENT): FAMILY hit@3=0, flags=—; FAMILY_SECTION hit@3=0, flags=—

Sequence diagnostic (credit agreements):
- CA-MARKEL: true `AGENCY` after `EVENTS_OF_DEFAULT` -> rank 1 (top-3 ['AGENCY', 'MISCELLANEOUS', 'COVENANTS_COMBINED'], bigram n=4)
- CA-MARKEL: true `MISCELLANEOUS` after `EVENTS_OF_DEFAULT` -> rank 2 (top-3 ['AGENCY', 'MISCELLANEOUS', 'COVENANTS_COMBINED'], bigram n=4)

#### SECONDARY (post-freeze segmentation repair)

| Case | Hidden positives | GLOBAL top-3 | FAMILY top-3 | FAMILY_SECTION top-3 | hit@3 G / F / FS | false exp@3 G / F / FS | Brier G / F / FS | FS flags |
|---|---|---|---|---|---|---|---|---|
| CA-MARKEL:SECTION | AGENCY, MISCELLANEOUS | AGENCY, CLAIM_PROCEDURE, CREDIT_CALCULATION_APPLICATION | AGENCY, MISCELLANEOUS, COVENANTS_COMBINED | AGENCY, MISCELLANEOUS, COVENANTS_COMBINED | 1.20 / 2.00 / 2.00 | 1.80 / 1.00 / 1.00 | 0.156 / 0.050 / 0.024 | — |
| CA-MARKEL:Article 7 | USE_OF_PROCEEDS, BOOKS_INSPECTION | BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS | BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS | BAIL_IN_QFC, BENCHMARK_RATES, COMMITMENTS_BORROWINGS | 0.00 / 0.00 / 0.00 | 3.00 / 3.00 / 3.00 | 0.195 / 0.574 / 0.574 | CONTEXT_CONFLICT(consistency=0.38)_BACKOFF |
| CA-MARKEL:Article 1 | INTERPRETATION, DEFINED_TERMS | AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, BENCHMARK_RATES | AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC, BENCHMARK_RATES | BENCHMARK_RATES, DEFINED_TERMS, INTERPRETATION | 0.18 / 0.18 / 2.00 | 2.82 / 2.82 / 1.00 | 0.195 / 0.589 / 0.082 | — |
| CA-OLDDOMINION:SECTION | CONDITIONS_PRECEDENT, NEGATIVE_COVENANTS | CLAIM_PROCEDURE, CONDITIONS_PRECEDENT, CREDIT_CALCULATION_APPLICATION | CONDITIONS_PRECEDENT, COVENANTS_COMBINED, GUARANTY | CONDITIONS_PRECEDENT, GUARANTY, COVENANTS_COMBINED | 0.75 / 1.00 / 1.00 | 2.25 / 2.00 / 2.00 | 0.184 / 0.112 / 0.098 | — |
| CA-OLDDOMINION:Article 6 | FUNDAMENTAL_CHANGES, LIENS | ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC | ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC | ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC | 0.09 / 0.09 / 0.09 | 2.91 / 2.91 / 2.91 | 0.200 / 0.600 / 0.543 | CONTEXT_CONFLICT(consistency=0.33)_BACKOFF |
| CA-OLDDOMINION:Article 5 | BOOKS_INSPECTION, FINANCIAL_REPORTING | ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC | ACCOUNTING_TERMS, AUTHORIZATION_ENFORCEABILITY, BAIL_IN_QFC | FINANCIAL_REPORTING, MAINTENANCE_INSURANCE, ACCOUNTING_TERMS | 0.09 / 0.09 / 1.00 | 2.91 / 2.91 / 2.00 | 0.200 / 0.600 / 0.486 | — |
| SLA-CLOUDFLARE:SECTION | CREDIT_CALCULATION_APPLICATION, DEFINITIONS, EXCLUSIONS | DEFINITIONS, AGENCY, CONDITIONS_PRECEDENT | DEFINITIONS, CREDIT_CALCULATION_APPLICATION, CREDIT_SCHEDULE | DEFINITIONS, CREDIT_CALCULATION_APPLICATION, CREDIT_SCHEDULE | 1.25 / 2.00 / 2.00 | 1.75 / 1.00 / 1.00 | 0.161 / 0.126 / 0.142 | — |
| SLA-MONGODB:SECTION | CREDIT_SCHEDULE, EXCLUSIONS, SOLE_REMEDY | AGENCY, CONDITIONS_PRECEDENT, CREDIT_FACILITIES | CREDIT_SCHEDULE, CREDIT_CAP, EXCLUSIONS | CREDIT_SCHEDULE, CREDIT_CAP, EXCLUSIONS | 0.43 / 1.80 / 1.80 | 2.57 / 1.20 / 1.20 | 0.175 / 0.097 / 0.103 | — |

| Arm | targets | hit@1 | hit@3 | section hit@3 | provision hit@3 | false exp@3 | Brier | log loss |
|---|---|---|---|---|---|---|---|---|
| GLOBAL_FREQ | 18 | 1.91 | 3.99 | 3.63/10 | 0.36/8 | 20.01 | 0.1831 | 0.5479 |
| FAMILY | 18 | 4.12 | 7.16 | 6.80/10 | 0.36/8 | 16.84 | 0.3433 | 0.9737 |
| FAMILY_SECTION | 18 | 5.20 | 9.89 | 6.80/10 | 3.09/8 | 14.11 | 0.2564 | 0.7157 |
| EVIDENCED_LAW_FAMILY_SECTION | 18 | 5.20 | 9.89 | 6.80/10 | 3.09/8 | 14.11 | 0.2564 | 0.7157 |

Decision: {"decision": "PREDICTIVE_SIGNAL_PROVISIONAL", "hurdle_met": true, "checks": {"global_top3_rate": 0.222, "ceiling_effect": false, "fs_minus_global_hit3": 5.904000000000002, "fs_gain_docs": ["CA-MARKEL", "CA-OLDDOMINION", "SLA-CLOUDFLARE", "SLA-MONGODB"], "fs_false_exp_not_worse_than_global": true, "observable_backoff_in_negative_controls": 2, "fs_minus_family_hit3": 2.7330000000000014, "fs_minus_family_brier": -0.0869, "fs_minus_global_brier": 0.0733}}

Negative controls:
- `CA-MARKEL:Article 7` (section AFFIRMATIVE_COVENANTS -> REPRESENTATIONS): FAMILY hit@3=0.0, flags=—; FAMILY_SECTION hit@3=0.0, flags=—
- `CA-MARKEL:SECTION` (family CREDIT_AGREEMENT -> VENDOR_SLA): FAMILY hit@3=0.0, flags=—; FAMILY_SECTION hit@3=2.0, flags=['CONTEXT_CONFLICT(consistency=0.12)_BACKOFF']
- `SLA-CLOUDFLARE:SECTION` (family VENDOR_SLA -> CREDIT_AGREEMENT): FAMILY hit@3=1.0, flags=—; FAMILY_SECTION hit@3=2.0, flags=['CONTEXT_CONFLICT(consistency=0.00)_BACKOFF']

Sequence diagnostic (credit agreements):
- CA-MARKEL: true `AGENCY` after `EVENTS_OF_DEFAULT` -> rank 1 (top-3 ['AGENCY', 'MISCELLANEOUS', 'COVENANTS_COMBINED'], bigram n=4)
- CA-MARKEL: true `MISCELLANEOUS` after `EVENTS_OF_DEFAULT` -> rank 2 (top-3 ['AGENCY', 'MISCELLANEOUS', 'COVENANTS_COMBINED'], bigram n=4)
- CA-OLDDOMINION: true `CONDITIONS_PRECEDENT` after `REPRESENTATIONS` -> rank 2 (top-3 ['COVENANTS_COMBINED', 'CONDITIONS_PRECEDENT', 'GUARANTY'], bigram n=4)
- CA-OLDDOMINION: true `NEGATIVE_COVENANTS` after `AFFIRMATIVE_COVENANTS` -> rank 1 (top-3 ['NEGATIVE_COVENANTS', 'CONDITIONS_PRECEDENT', 'COVENANTS_COMBINED'], bigram n=1)

Primary-run note: the two segmentation-failed cases have no positives but still enter the per-case Brier means. Their top-3 lists are all false expectations.

## Segmentation and labeling errors observed (heldout)

- **CA-MOTOROLA:** my pre-split amendment screen only scanned the first 400 characters and missed "FIRST AMENDMENT". The frozen parser produced 3 headless units. Excluded in the secondary run.
- **SLA-CLOUDFLARE:** no HTML heading names the SLA, so the frozen run returned `SLA_TITLE_NOT_FOUND`. The secondary numbered-paragraph fallback truncates headings ("3. Service" for "3. Service Credit Claims"). Labels come from heading plus text, so truncation matters little, but two units were mislabeled `OTHER`:
  - "1. Business SLA" is a service commitment phrased as "commits to provide", which the rule does not catch.
  - "6. Service Credit Calculation" was missed by the credit-calculation rule.
- **CA-MARKEL:** many miscellaneous and other subsections fell to provision `OTHER` (rules written on 4 training documents).
- **Possible rule-order artifact:** Best Buy's "Use of Proceeds; Federal Reserve Regulations" matches MARGIN_REGULATIONS before USE_OF_PROCEEDS. This may explain the Markel art. 7 miss even without the backoff. Not adjusted.

## Costs and effort

- Provider spend: **$0**. Data: 12 SEC requests (1 initial full-text search refused with 403 for lacking a contact User-Agent; then, with the owner-approved contact User-Agent, 1 search + 10 exhibit downloads, rate-limited) and 10 SLA page fetches.
- Human labeling time: **0**. All labels are rule-based and agent-authored, with no independent adjudication.
- Corpus capture and segmentation was the largest share of the engineering effort.

## Commands

```powershell
cd C:\Claude\sophon\prototype\contract_structure_prediction_v3
python -m unittest test_v3 -v                       # offline tests (synthetic fixtures; plumbing only)
python predict.py --mode dev                        # train-only leave-one-out
python predict.py --mode heldout                    # frozen primary (needs data/records_heldout.json)
python secondary.py --raw-dir <local corpus_dl>     # post-freeze repaired secondary (needs local raw docs)
python llm_baseline.py --mode preflight             # optional LLM arm: prompts, cap 8, estimate; no network
```

The raw documents are not in the repository. Re-create them from the URLs and SHA-256 hashes in `data/source_manifest.json` (SEC requires a declared contact User-Agent).

## Next action and gate to Jev

- **Next action (cheap, offline):** human-adjudicate the 8 secondary heldout cases' labels (about 30–45 min), so that this result is no longer purely agent-authored. Then decide, prospectively, whether to re-specify the conflict rule ("sparse support ≠ conflict") and fix the amendment screen. Any such change needs a **new** frozen protocol and **new** heldout documents, which CUAD or the Material Contracts Corpus could supply.
- Optionally the owner may run `RUNBOOK_V3_LLM_BASELINE.ps1` (≤8 calls, est. ≈ $0.67; V2's real cost was about 2.7× its estimate).
- **Concrete criterion for moving to a Jev-based interpretation test:**
  - on a fresh, human-adjudicated heldout set of **at least 6 documents**, FAMILY_SECTION must beat FAMILY on provision hit@3 by **at least 3 targets** across **at least 3 documents**, *and* must not be worse than GLOBAL on Brier;
  - only then run `masked-section prediction → Jev candidate ranking / omission search → independently verified interpretation`, scored on independently verified omissions found, not on quote overlap.
