# Public-source alignment review — frozen before querying trip records

2026-09-28. This follow-up is performed by the conversational assistant, with no externally invoked model, inserted faults, supplied clause-to-column mapping, or supplied expected numerical answer. It is exploratory source-grounded review, not a blinded benchmark or an independent assessment of the assistant's accuracy.

## Selected pair

- Governing source: NYC TLC's yellow-taxi data dictionary dated 18 March 2025, official trip-record publication notes, and NYC311's Congestion Pricing Program description. These govern the meaning of the public dataset and describe a real fare-rule change. They are not a customer's signed commercial agreement.
- Existing analytics implementation: `bISTP/nyc-taxi-databricks-dbt`, commit `b79ecaefb12ae4a7e42314a3a2cee9645d401791`. The repository describes January–March 2025 inputs and a monthly BI revenue mart. It is an independently authored demonstration project, not verified production infrastructure.
- Actual records: the complete official January 2025 yellow-taxi Parquet release; January green-taxi data may be loaded to build the existing union model, but governing-rule conclusions in this review concern yellow taxis only.
- Source selection: GitLab's public handbook was considered, but its analytics repository redirected to sign-in. The NYC project was selected for accessible definitions, a pre-existing dbt pipeline, and actual matching records. It was not selected using published defect reports. The assistant has now read its SQL and identified hypotheses, but has not queried the records.

## Questions and pre-execution hypotheses

1. **Record identity:** TLC defines VendorID as a technology-provider code, not a unique vehicle or trip. Does the staging key `(vendorid, pickup timestamp)` collapse distinct records, and do some collisions differ in routes or fares? Count rows lost separately from byte-identical duplicates; do not call every lost row a proven distinct journey.
2. **Amendment representation:** the 2025 data introduces `cbd_congestion_fee`, associated with a new per-trip charge starting 5 January. Trace the field through staging, facts, and the monthly mart. Recognize correct propagation as a positive control; do not infer that a new source field is absent without inspecting the SQL.
3. **Amount precision:** the project casts monetary values to bare `numeric`. Databricks documents this as DECIMAL(10,0), which cannot preserve fractional-dollar amounts. Measure exposure on raw data and simulate that documented type explicitly; distinguish this from a live Databricks execution. DuckDB's bare NUMERIC has a different default, so a local successful dbt run cannot clear this issue.
4. **Context completeness:** compare descriptions of tips and total amounts to TLC's exclusion of cash tips. Do not infer collected cash tips from absent data. Distinguish misleading or incomplete semantics from a proven numerical error.
5. **Rule limits:** inspect charges before the start date and the distribution of charge values, but do not label every zero/negative/nonstandard charge illegal. Routes, enrollment, exemptions, corrections and validity of source records are not fully established by these public inputs. TLC explicitly does not guarantee record accuracy.

## Execution and evidence requirements

Freeze upstream commit and SHA-256 hashes of downloaded inputs. Keep source URLs and all executed SQL. Use read-only analytical queries after local preparation. Reuse upstream SQL and dbt definitions unchanged wherever possible; separately disclose every local adapter/configuration change. Disable the default 100-row development limit explicitly. Run a full refresh for the local reproduction; this does not validate incremental behavior.

The full source project lacks an identified license in its checkout. Do not vendor its code into Sophon; fetch the pinned public commit on reproduction and save its hash inventory instead. Store runtime databases and downloads outside tracked files. Publish our review code, evidence and source links.

Report observed issues, aligned elements and unresolved questions. Ordinary dbt tests passing does not establish contractual alignment, and failure does not automatically establish a governing-rule violation. No detection percentage, no unsupported production loss estimate, and no legal-compliance certification.

## What this can establish

A successful execution supports the feasibility of an agent deriving and grounding an alignment investigation using an independently authored analytics stack and real records. It cannot establish accuracy across unseen contracts, production connectivity, automatically discovered document authority, customer value, or unattended amendment propagation into Omni/Hex/other agents.
