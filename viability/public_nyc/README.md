# Public-source alignment experiment

**Result:** a conversational agent used independently authored dbt code, official source definitions and actual records to identify a material semantic mismatch and quantify its effect. No defects were planted. A separate local simulation shows how a new governing source can invalidate dependent agent contexts and distribute updated context while retaining unresolved findings.

This is stronger evidence of a feasible inspection workflow than the previous synthetic cases. It is not a reliability benchmark, a real contract audit, or a live Databricks/BI integration.

## Inputs and authority

The [upstream project](https://github.com/bISTP/nyc-taxi-databricks-dbt/tree/b79ecaefb12ae4a7e42314a3a2cee9645d401791) is an independently authored Databricks/dbt demonstration with a monthly BI revenue mart. Its README identifies 2025 TLC records as its data source. We used the official January releases: **3,475,226 yellow records** and 48,326 green records. The rule investigation concerns yellow taxis; green data enabled the existing union pipeline to build. Twenty-two yellow records have pickup timestamps outside January, so counts below refer to the January release, not exclusively January-dated trips.

The governing sources are the [TLC data dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf), [official publication notes](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), and [NYC311 fare-program description](https://portal.311.nyc.gov/article/?kanumber=KA-03612). They establish public dataset meaning and describe a fare-rule change; they are not a signed customer contract. The [Databricks numeric-type specification](https://docs.databricks.com/aws/en/sql/language-manual/data-types/decimal-type) supplies the platform semantics.

The scope and hypotheses were frozen in `PROTOCOL.md` before querying the data. The reviewer chose the pair and then read the code; this was not blinded or independently adjudicated. No expected numerical answer or clause-to-column mapping was supplied by the user. The assistant performed that interpretation interactively and wrote the checks. Replaying the Python files executes those recorded checks, not a new model review.

## Findings

| Finding | Evidence | Conclusion |
|---|---|---|
| Unsupported trip identity | Staging retains one row per provider/pickup timestamp. 3,475,226 input rows become 2,110,427 rows. All input rows are value-distinct; 850,717 key groups contain different trip content. | **1,364,799 distinct records discarded, or 39.27%.** A provider identifier cannot establish unique trip identity. This is confirmed record loss, not proof that every source row is a valid separate journey. |
| Fractional fee cannot survive target cast | Upstream monetary casts use bare `numeric`. Databricks defines this as DECIMAL(10,0). The documented type maps 0.75 to 1 in an explicit local type simulation. | **Target-dialect precision mismatch.** 2,246,495 raw records contain +0.75, and 6,553 contain -0.75. The issue affects representation, not demonstrated passenger billing. No Databricks cluster was executed. |
| New fee is propagated | The existing staging, fact and monthly mart all carry the CBD fee. The local fact and mart each sum to 997,608.750 for the retained yellow records. | **Aligned propagation**, conditional on the preceding record-loss and precision findings. The source change is not simply missing from the pipeline. |
| Tip and total descriptions lose scope | Metadata describes all tips and amounts paid without explaining the source's cash-tip exclusion; total charges are not independently verified collections. | **Context clarification needed.** Neither complete cash tips nor cash collection can be inferred from these records. |
| Apparent early charges require timing review | 401 positively charged records have pickup timestamps before 5 January; 397 finish on or after the start date. Four finish before it. | A pickup-only rule would flag many boundary-crossing trips without sufficient evidence. The remaining four are review candidates, not certified violations. |

The row-loss result is not an estimate based on a sample. The checks scanned the whole yellow release, and the distinct-row check found no fully identical rows. Counterexamples in `evidence/audit_results.json` show simultaneous records from the same provider with different locations, times, distances and charges. There is no source trip identifier that licenses the current deduplication assumption. We do not prescribe a replacement business key without additional source knowledge.

The local reproduction used DuckDB, whose default NUMERIC is DECIMAL(18,3), preserving 0.75. Therefore its successful build cannot validate the target platform's numeric behavior. On this reproduction's retained rows, explicitly simulating DECIMAL(10,0) changes the recorded CBD-fee sum from 997,608.75 to 1,330,145.00. That **332,536.25 representation difference is a simulation**, not a measured production revenue loss. Selection among colliding rows has no tie-breaker, so these retained-row monetary totals can vary on rerun; the collision counts are the more robust result.

All **22 existing dbt tests passed**, along with five models and one seed. The uniqueness test passes after rows have already been discarded. This does not imply that dbt cannot catch the issue: a data team could add the same semantic assertions. Sophon's potential contribution is deriving and maintaining their governing-source connection.

The field-type issue and record loss have different status from raw-data anomalies. TLC does not guarantee record accuracy. The public records cannot establish complete route traversal, plan enrollment, exemptions, corrections or every charge's applicability. In particular, negative fees were not labeled violations merely because of their sign.

## Context update experiment

`CONTEXT_PROTOCOL.md` defines a separate controlled replay. Starting with registered dictionary context, it introduces the retrieved NYC311 rate source and uses the actual dbt dependency graph to recompute three simulated consumers' contexts.

- Monthly-BI and trip-review consumers reject their previous contexts as stale and accept replacements containing the new source and outstanding findings.
- The unrelated zone-reference consumer's context remains unchanged.
- Replaying the same event produces the same contexts.
- Refreshed context remains `REVIEW_REQUIRED`; source freshness does not certify correctness.

All four assertions passed. The semantic interpretation and source-field binding came from this conversational review and were supplied explicitly to the propagation mechanism. This proves only local mechanics with registered dependencies. The initial state is a constructed arrival replay, not an authentic historical deployment. There is no watcher, real downstream agent, production transport, or Omni/Hex integration.

## Reproduce

From the Sophon repository root, in Python 3.12:

```bash
python -m venv .venv-public-review
.venv-public-review/bin/pip install -r viability/requirements.txt
.venv-public-review/bin/python -B -m viability.public_nyc.prepare
.venv-public-review/bin/python -B -m viability.public_nyc.audit
.venv-public-review/bin/python -B -m viability.public_nyc.context_event
```

Preparation needs Git and network access to the pinned public repository, dbt package registry and the listed public inputs. It refuses to replace an existing prepared project. Public inputs can change at their URLs; compare SHA-256 values in the new provenance file to the saved run before calling it an exact reproduction. Downloads and runtime databases stay in `viability/runs/public_nyc/`, excluded from Git. Active database writes use a native temporary directory; allow disk space for roughly 3.5 million records, dbt products and intermediate SQL work.

Upstream model SQL, YAML and macros are unchanged. Adaptations are the local connection profile, January-only input, a full refresh, and disabling the development 100-row limit. There is no verified license file in the upstream checkout, so its code is fetched at the pinned commit rather than copied into Sophon.

The initial workspace-hosted database and a checkpoint retry failed on stale WAL replay before dbt model execution. Moving the checkpointed database copy to native temporary storage resolved that environment issue. Counts and two row-hash aggregates matched both downloaded Parquet sources afterward. Failed and successful logs are retained. No governing check was tuned to manufacture the reported findings.

## Evidence and decision

- `evidence/provenance.json`: URLs, input SHA-256 hashes, upstream commit/file hashes, local adaptations and source-data verification.
- `evidence/audit_results.json`: every executed SELECT, returned records, timings, result fingerprints, dbt outcomes and lineage.
- `evidence/dbt_local_disk.log`: successful upstream dbt build with all 22 tests passing.
- `evidence/context_event.json`: context versions, source arrival, simulated-consumer outcomes and assertions.

**Supported:** a useful read-only reviewer can be built on existing dbt work. In this case the agent grounded its findings in external definitions, inspected the implementation, queried actual data, recognized correctly propagated fields, and qualified uncertain findings. Registered dependencies can support deterministic context invalidation and replacement.

**Not established:** reliable interpretation across arbitrary contracts; independent precision/recall; authority and applicability discovery; end-to-end unattended amendment handling; live platform compatibility; or commercial differentiation from well-maintained internal tests. This experiment justifies developing a narrowly scoped source-to-metric reviewer. It does not justify claiming fully autonomous contractual compliance.
