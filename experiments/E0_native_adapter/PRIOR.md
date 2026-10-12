# E0 — prior evidence and alignment

Written 2026-10-12, before any data generation, dbt build or MetricFlow command was run for E0.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** SOPHON_CHARTER.md v1.1 §2 (the existing semantic layer as the integration
   boundary) and §5 Stage 1, *infrastructure feasibility*. Plan: SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md
   §5 E0, risk R1 only.
2. **Smallest uncertainty.** Can one existing, independently authored dbt/MetricFlow metric be enumerated,
   inspected and executed on its warehouse rows through MetricFlow's own interface, with evidence a fresh
   process can re-check?
3. **Semantic layer and data.** `behramkorkut/Governed-Analytics-Agent` at
   `312e97ad192dcef02f688e31edc0a08c6cf4345f` (MIT): dbt project `retail_dwh` on DuckDB with pre-existing
   MetricFlow semantic models and metrics. The rows are **synthetic retail data** produced by the upstream's
   seeded generator (`SEED = 42`). There is **no governing source** in E0, genuine or LAB_AUTHORED. Not proved:
   anything about interpretation, binding, verification against requirements, Snowflake/Databricks
   compatibility, production scale, customer value.
4. **Consistency with the architecture.** The charter requires Sophon to transpose and verify *through* the
   organization's existing semantic layer. Every later experiment (E1–E8) needs a native, read-only way to list
   metrics, trace a metric to its definition and execute it. E0 builds only that access path and replaces
   nothing in the upstream project.
5. **Prior results built on.** See below; none is erased or reinterpreted.

## What earlier Sophon work established, and what it left open

| Prior result | Established | Not established (relevant to E0) |
|---|---|---|
| 21 Sep 2026 authority/control-plane audit (`docs/REPORT.md`, `docs/DECISION.md`) | Bespoke authorization logic showed parity with policy-as-code in its setting | Nothing about semantic layers; not revived here |
| 28 Sep 2026 dbt/DuckDB viability, PR #2 (`codex/alignment-review-agent`, `viability/RESULTS.md`, `viability/public_nyc/README.md`) | Existing dbt models (Jaffle Shop; NYC taxi Databricks/dbt demo) could be inspected and governed checks executed on their records; real public-data discrepancies found | **No native MetricFlow execution**: queries ran as dbt models and hand-written SQL, not through a semantic-layer interface. No live platform. |
| 11 Oct 2026 governance-integrity test, PR #3 (`experiment/governance-integrity-2026-10-11`, `DECISION.md`, `RESULTS.md`) | STOP_KERNEL for a persistent link store claimed as a *performance differentiator* over Claude Code with notes, in a Publicodes law-to-rule benchmark; the store itself worked as infrastructure | Publicodes is not an enterprise BI semantic layer. The result is a bounded former hypothesis, not a reason to abandon a native semantic integration. Its chronology defect (future texts visible to earlier tasks) is noted; E0 has no chronology because it has no governing sources. |

The gap E0 addresses is the one PR #2 left: no Sophon experiment has yet executed a metric through a native
semantic-layer engine. PR #3 contributes nothing for or against that question.

## What E0 tests and does not test

- **Tests:** native MetricFlow access only — enumerate metrics, inspect one metric's native identity and
  lineage, run one native query on actual (synthetic) warehouse rows, repeat it, show the native client rejects
  invalid input, cross-check the number from the raw rows independently, and keep evidence a fresh process can
  re-run.
- **Does not test:** TRANSPOSE, TRACE, VERIFY or AUDIT as product capabilities; any governing requirement or
  amendment; LLM accuracy; a typed IR; approvals; Claude-versus-Sophon comparison; customer outcome.
- **Compatibility with the four capabilities later.** The adapter returns the native metric identity (name,
  type, measure, filter, semantic model, dbt node) and execution receipts (argv, exit codes, compiled SQL,
  manifest and warehouse fingerprints). Those are the semantic-side anchors that later TRACE links, VERIFY
  checks and AUDIT reconstruction would reference. E0 does not build any of them.
