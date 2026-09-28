# Warehouse alignment viability test — frozen before implementation

28 September 2026. This test concerns whether a reviewer can inspect an existing BI metric, trace its dbt dependencies and query warehouse data against governing requirements. It does not retest authority-grant execution.

## Inputs and independence

Reuse dbt Labs' Apache-2.0-licensed `jaffle-shop-classic`, commit `fd7bfacae4f497ff044a6a0275268676bf1b64c3`. This is a public teaching project, not customer production evidence. Preserve its original model SQL, metadata and seeds in the clean case. Adapt only the local connection profile to DuckDB.

The governing agreement is fictional and explicitly supplied for this test. It describes a commercial metric compatible with the baseline models, plus an order-specific limit. It is not a contract of dbt Labs. Challenges and expected outcomes are controlled fixtures authored in this session, not an independent benchmark.

The BI surface is the executed query `SUM(amount)` over the existing `orders` model, in AUD, for the supplied reporting cohort. No live Omni, Hex, Snowflake or Databricks connection is represented. The implementation must expose the warehouse adapter boundary and leave those integrations unverified.

## Frozen requirements

G1. At the order grain, amounts are expressed in AUD. Raw payment amounts are integer Australian cents; 100 cents equals AUD 1. Every non-null payment contribution is counted once.
G2. Version 1 includes credit card, bank transfer, gift card and coupon payments, across all order statuses. It aggregates by order date, without inferring settlement or cash collection.
G3. Every raw payment needs a non-null amount, a unique payment ID and a valid order link. Missing amounts must not be treated as zero.
G4. Order 2 has an agreed gross payment ceiling of AUD 20.00. Actual recorded payments exceeding it are a data/operational discrepancy even if the model computes their sum correctly.
G5. Reporting scope is orders dated from 2018-01-01 through 2018-04-30 inclusive.
Version 2 amendment changes only G2: coupons are excluded for orders dated on or after 2018-02-01. Earlier orders retain their original treatment. A changed description does not by itself change the calculation.

## Cases and expected outcomes

| Case | Expected result |
|---|---|
| Clean existing project, V1 | NO_ISSUE_DETECTED |
| Governing V2 arrives, model unchanged | DEFINITION_MISMATCH with affected post-effective-date orders |
| Upstream cents conversion removed | DEFINITION_MISMATCH |
| Coupon contribution added twice | DEFINITION_MISMATCH |
| Order 2 payment raised from 2000 to 2500 cents | DATA_VIOLATION, AUD 5 excess; metric may still match actual payments |
| One amount missing in a multi-payment order | MISSING_EVIDENCE; no clean clearance |
| V2 applied correctly to the model | NO_ISSUE_DETECTED, including unchanged pre-effective-date orders |
| Equivalent metric-description paraphrase | NO_ISSUE_DETECTED |
| Only downstream customer-model documentation changes | NO_ISSUE_DETECTED; selected metric dependency fingerprint unchanged |

## Two separate gates

**Integration gate:** build the real dbt project per case, obtain manifest lineage plus physical schemas and data, execute read-only checks, and reproduce every expected outcome. Compare ordinary dbt test results so catching an issue already covered by dbt is not misrepresented as added detection. Keep event/source snapshot hashes and query receipts. Reject write queries, external file reads, malformed plans and missing requirement dispositions. Preserve nulls.

**Autonomous-agent gate:** give a configured model the governing text, target definition, dependency code and warehouse schemas, without case names, mutations, expected answers or evaluator queries. It must propose supported checks, execute them through the restricted adapter, and correctly distinguish the nine outcomes. Score evidence validity, missed violations and false alarms. Success in this small set supports only bounded feasibility. Use an independently adjudicated unseen set before reliability claims.

With no model credential available, run the integration gate with explicitly human/assistant-authored SQL probes. Mark the autonomous-agent gate NOT_RUN. Do not use those probes as evidence that the model discovered the contractual meaning or the correct mapping.

## Decision rule

All nine integration cases, clean controls, dependency tracing and query-boundary checks must pass. Any unrun agent or platform gate prevents a claim that the full proposed solution is confirmed. Do not quote a model accuracy percentage from an assisted or reference-probe run. Report operational compatibility, semantic accuracy and business value separately.
