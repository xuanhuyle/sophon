# Warehouse alignment test — first results

Executed 28 September 2026. **Integration gate: 9/9 expected outcomes. Autonomous-agent gate: NOT RUN. Live-platform gate: NOT RUN.**

This establishes a runnable local route from an existing dbt model to its dependency code, physical schemas, actual records and governing-rule counterexamples. It does not confirm unattended semantic interpretation or compatibility with a production Snowflake/Databricks and Omni/Hex stack.

## Setup

Existing project: dbt Labs Jaffle Shop Classic at `fd7bfacae4f497ff044a6a0275268676bf1b64c3`, preserved with its license and hashes. Synthetic governing agreement: five explicit requirements plus one controlled amendment. Target BI query: total order consideration in AUD for the supplied historical cohort. Runtime: dbt-core 1.12.5, dbt-duckdb 1.11.0 and DuckDB 1.5.5.

The clean existing project has 99 orders and 113 payment records. The inspection follows five dbt dependencies, ending at the original raw order and payment tables. Source data and model code are queried locally; no screenshots or precomputed metric values substitute for warehouse execution.

## Observations

| Controlled case | Executed BI total (AUD) | Governing-rule result | Existing dbt data tests |
|---|---:|---|---|
| Original model and V1 agreement | 1,672.00 | No issue detected | 20/20 pass |
| Amendment received; model unchanged | 1,672.00 | Definition mismatch on 8 affected orders; correct amended total is 1,577.00 | 20/20 pass |
| Cents conversion removed upstream | 167,200.00 | Definition mismatch | 20/20 pass |
| Coupon contribution added twice | 1,857.00 | Definition mismatch on 13 orders | 20/20 pass |
| Order 2 payment increased above its ceiling | 1,677.00 | Data violation: order 2 is AUD 5.00 above its AUD 20.00 limit | 20/20 pass |
| One payment amount missing | 1,649.00 | Missing evidence; NULL was not treated as acceptable | 20/20 pass |
| Amendment correctly applied from its effective date | 1,577.00 | No issue detected, including the pre-effective-date portion | 20/20 pass |
| Equivalent wording in the metric description | 1,672.00 | No issue detected | 20/20 pass |
| Unrelated downstream customer-model change | 1,672.00 | No issue detected; selected dependency fingerprint unchanged | 20/20 pass |

The missing-amount case matters: the affected order has more than one payment, so aggregation can hide a missing contribution while the final amount stays non-null. Generic output not-null checks consequently pass.

The over-ceiling case demonstrates a separate distinction: the order model correctly represents the altered records, while those records violate a supplied business limit. A data problem and a transformation problem must not receive the same diagnosis.

## What the comparison does and does not show

The reference queries were explicitly authored from the test agreement. They demonstrate that governing-source assertions can add detection beyond this project's generic dbt tests. A data team could add the same assertions to ordinary dbt. This is not evidence of a proprietary detection advantage, reduced review effort or demand for a standalone product.

The reference queries are not model-generated. The equivalent-wording control passed because these queries were unchanged; that does not establish that an LLM avoids paraphrase false positives. Neither the clauses nor their mappings were discovered automatically in this run.

The full model path is implemented separately: an explicitly configured model receives the governing text, selected metric, dependency code and warehouse evidence; it proposes SQL checks which the restricted adapter executes. Scenario names, mutations, expected outcomes and reference queries are withheld. No API credential was available, so this path has not been live-tested. Even a later 9/9 classification score must be accompanied by inspection of the supporting rules, queries and counterexample records.

The commercial agreement is synthetic, designed for a controlled test. The public project is a teaching dataset. One author defined the cases and reference probes. No independent customer evidence or unseen-case accuracy estimate exists.

## Boundary validation

Eleven additional tests passed: SELECT execution preserving nulls; rejection of writes, multiple statements and external file reads; row-limit disclosure; detection of changed record snapshots; actual lineage reaching both seed tables; missing requirement-account rejection; fabricated clause rejection; unknown dependency-citation rejection; and wrong-snapshot rejection.

Queries run with a read-only connection, disabled external access and bounded resources. This is a local test adapter, not a production SQL access-control system. Snapshot generation scans the small supplied tables; production scale and transactional consistency remain to be designed and tested.

## Evidence and reproduction

- `evidence/integration_results.json`: all nine classifications, dbt statuses, metric query outputs, snapshot identities and counterexample query receipts.
- `evidence/execution.log`: first successful run console output.
- `PROTOCOL.md`: frozen requirements and expected outcomes.
- `vendor/PROVENANCE.json`: exact public source commit and file hashes.
- `README.md`: integration and optional live-model commands.
- Generated `runs/integration/`: full local case projects, databases, manifests, input packets and plans; excluded from Git, reproducible from committed inputs.

Protocol SHA-256 used by the run: `e8c865e2d66ed702b9e627f1a508c908a66fe4744530560dc81e7725efb462dd`.

Execution notes: the first launch failed before any case ran because the old workspace virtual environment lacked its Python executable. A new isolated environment was installed from the pinned requirements. Before execution, the protocol's license label was corrected from MIT to Apache 2.0 after inspecting the upstream license; the requirements and expected outcomes were unchanged. The first actual nine-case run completed without unexpected test failures or post-result tuning.

## Follow-up: interactive review in this conversation

The conversational assistant can perform the reviewing role without a separate API credential. It read the governing V2 clauses, compiled dbt code, lineage and physical schemas, then wrote and executed new read-only reconciliation SQL without importing the reference probe implementation. The source model aggregates all payments before joining order dates, so it cannot apply the amendment's date-dependent coupon exclusion.

The queries found eight affected orders (42, 58, 76, 81, 86, 92, 94 and 95), totaling AUD 95 of excess inclusion. The 29 pre-amendment orders remain AUD 496. For the 70 later orders, reported AUD 1,176 should be AUD 1,081 under the fictional amendment. The full cohort therefore changes from AUD 1,672 to AUD 1,577. Data prerequisites returned zero missing amounts, duplicate keys, invalid order links, missing dates or unrecognized payment methods. Source snapshots matched before and after execution.

Replay: `python -B -m viability.interactive_amendment_review`, after building the integration fixtures. Evidence: `evidence/interactive_amendment_review.json`, including executed SQL and returned rows. The first replay attempt had a stray `+` at the start of a query and failed to parse; the typo was corrected before successful execution.

This is a known-fixture demonstration, not the frozen autonomous-agent gate: previous scenarios and outcomes were already visible to the reviewer. It covers the amendment and comparison prerequisites, not the independent G4 ceiling check. It supplies no independent accuracy score and demonstrates neither unattended operation nor downstream context propagation. The replay script contains the SQL derived during the conversation; replaying it is not another model review.

## Technical verdict

**Confirmed within this fixture:** existing dbt work can be inspected and reused to execute governing-source checks against actual records, with traceable counterexamples and separate model/data diagnoses.

**Still unconfirmed:** an autonomous model reliably discovering the right interpretation, selecting the right dependencies and generating valid checks on unseen agreements; live-platform integration; and a useful false-alarm/missed-issue rate. Those gates must run before claiming the full Sophon solution is technically validated.
