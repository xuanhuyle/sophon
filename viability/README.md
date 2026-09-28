# Test: governing agreement → existing BI metric → warehouse records

This tests the architecture Xuân described: reuse a data team's analytical models and inspect their definitions, dependency code and actual records against a governing source. It does not build a replacement semantic layer or an authorization kernel.

## What is real and what is controlled

- Existing analytical project: dbt Labs' public **Jaffle Shop Classic**, pinned in `vendor/PROVENANCE.json`. Its original staging/order models, metadata, data tests and 113 payment records are retained in `vendor/jaffle/` with the upstream Apache 2.0 license.
- Executed warehouse: DuckDB, built by dbt. The selected metric queries `SUM(orders.amount)` in AUD. Five dependencies lead from that order model to its underlying order/payment tables.
- Governing agreement: a **synthetic test overlay**, supplied in the frozen protocol. It is not an agreement signed by dbt Labs. The original project is a teaching example, not a customer production system.
- BI client: a concrete SQL metric query, not an Omni/Hex UI session. No Snowflake/Databricks connector has been tested.

The clean case uses the existing SQL unchanged. Mutations are created in isolated case directories. Negative controls include a correctly applied amendment, a meaning-preserving documentation edit and an unrelated downstream change.

## Reproduce the integration gate

Python 3.12 was used. From the Sophon repository root:

```sh
python -m venv .venv-viability
.venv-viability/bin/pip install -r viability/requirements.txt
.venv-viability/bin/python -B -m viability.run
.venv-viability/bin/python -B -m unittest viability.test_boundary -v
```

This creates `viability/runs/integration/` with nine isolated dbt builds, manifests, logs, databases, review packets, reference plans and query receipts. The summary is written to `viability/evidence/integration_results.json`. The runner refuses to overwrite a previous run: archive the existing run directory or use a fresh checkout before rerunning.

The integration gate uses **explicitly authored reference SQL**. It tests data access, lineage, arithmetic, classification of failure types, evidence capture and controlled changes. It does not show that an agent can discover the correct contractual interpretation or generate those queries.

## Run the separate autonomous-agent gate

Configure an OpenAI API credential through your normal secret mechanism and explicitly select a model available to that account:

```sh
.venv-viability/bin/python -B -m viability.run --model YOUR_MODEL_ID
```

This sends the governing text, metric definition, dependency SQL, physical schemas and a few sample rows to the chosen model. Case names, mutations, expected results and reference probes are withheld from its prompt. The model proposes SQL checks; the restricted adapter executes them; a separate scorer compares observed classifications with the frozen case expectations. Full model plans and counterexample rows are retained for adjudication.

The provider API uses structured output and `store: false`. No credential is stored in the repository. The schema and prompt are in `checks.py` and `reviewer.md`. The live adapter is **not yet tested against a real model endpoint** in this environment. No accuracy claim should be inferred from its presence.

Case-status agreement alone cannot establish correct reasoning: inspect whether each cited rule and returned counterexample actually support the finding. This is a developmental challenge set authored alongside the implementation; a separate reviewer must create/adjudicate unseen cases before independent reliability claims.

## Checks and boundaries

`warehouse.py` discovers transitive ancestors of the selected dbt model, captures code and documentation, reads actual schemas and fingerprints selected table/view contents. A downstream customer model is outside the selected dependency set. Snapshot generation reads full tables because this dataset is small; production volumes need a different profiling/snapshot strategy.

`Warehouse.query()` permits one SELECT, opens the database read-only, disables external access, bounds returned rows and applies time/memory limits. It preserves nulls. The adapter is a local test boundary, not a production SQL security service or a table/row authorization layer.

The existing dbt tests are run independently of the governing-rule probes. A correct model may still expose data that violates the governing source. Conversely, a schema-valid model may misrepresent that source. Results keep these two failure types separate.

The governing text, metric definition, dependency representations and data fingerprints form a snapshot ID. Changed input invalidates an old plan. The live path rechecks the snapshot after the model call. These are local consistency controls, not a guarantee of transactional isolation in a live warehouse.

## Decision

The protocol distinguishes three outcomes: integration feasibility, autonomous semantic performance and actual platform compatibility. Until all relevant gates run successfully, this cannot confirm the complete Sophon proposition.

A strong next result would be an independently reviewed agent correctly identifying both inserted failures and clean controls, with useful counterexample rows, before any integration into a production semantic layer. No automatic remediation is implemented.

An interactive review can also run within this conversation without an API credential. `python -B -m viability.interactive_amendment_review` replays the amendment checks derived in that follow-up and writes `evidence/interactive_amendment_review.json`. This is a known-fixture demonstration, not an independent accuracy test or a fresh model invocation. See `RESULTS.md` for the findings and limits.
