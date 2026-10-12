# E1 — prior evidence and alignment

Written 2026-10-12 before any E1 evaluator code or scored E1 execution.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** SOPHON_CHARTER.md v1.1 §2 (semantic-layer boundary; non-representable
   requirements tracked explicitly rather than marked compliant), §3 TRACE and VERIFY (as future requirements),
   §5 Stage 1 *infrastructure feasibility*. Plan: SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md §5 E1, risks R2
   and R3 **under a human-supplied mapping only**.
2. **Smallest uncertainty.** Given a LAB_AUTHORED, unambiguous requirement and an experimenter-supplied
   interpretation and binding, can a tiny read-only evaluator (i) substantiate a bound predicate with native
   MetricFlow and data evidence, (ii) tell a predicate present in the underlying tables but not exposed by the
   semantic catalog from (iii) a fact absent from the bounded inspected estate, without promoting any of them to
   verified?
3. **Semantic layer and data.** The same pinned, independently authored dbt/MetricFlow project as E0
   (`behramkorkut/Governed-Analytics-Agent` @ `312e97ad192dcef02f688e31edc0a08c6cf4345f`), metric
   `completed_revenue`, seeded **synthetic** retail data. The governing text is **LAB_AUTHORED** by the
   experimenter (policy family LAB-REV-1); its interpretation and bindings are **supplied and SIMULATED-approved**
   by the experimenter. No real authority, signature or customer is involved.
4. **Consistency with the architecture.** Binding requirements to the organization's *existing* semantic objects,
   and reporting honestly which facts the layer does not expose or the estate does not hold, is the step between
   native access (E0) and any transposition or verification. E1 changes nothing in the upstream semantic layer.
5. **Prior results built on.** Below; none is erased or reinterpreted.

## E0 — exact bounded achievement (OBSERVED, draft PR #4, branch `experiment/e0-native-metricflow-2026-10-12`, head `a84c855`)

- Verdict **PASS_NATIVE_RUNTIME**, retiring **R1 only**.
- Native `mf query --metrics completed_revenue --group-by metric_time__year` on the upstream's DuckDB warehouse
  returned 2024 → 1 707 052.80, 2025 → 1 477 833.96, 2026 → 792 441.45, equal to the cent to an independent
  standard-library recomputation from the raw CSVs. Repeat, fresh-process re-run and clean rebuild were
  byte-identical. Invalid metric and invalid dimension were rejected natively (exit 1).
- Native identity of `completed_revenue`: simple metric, measure `revenue` (`sales`, sum, expr `revenue`), filter
  `{{ Dimension('sales__status') }} = 'completed'`, relation `gold.fact_sales`, dbt node
  `model.retail_dwh.fact_sales`. Compiled SQL `evidence/run/compiled_query.sql`.
- Reusable code: `experiments/E0_native_adapter/src/mf_adapter.py` (E1 imports it unmodified) and
  `src/crosscheck.py` (E1's oracle reuses it for case A).
- PR #4 status on 2026-10-12 before E1 work: open, draft, not merged, mergeable; **no CI checks exist** in the
  repository (absent CI is not a pass), no comments, no reviews.
- E0 proves nothing about governing requirements, interpretation or binding. Its PowerShell commands were not
  executed.
- Reproduced in the E1 worktree before the E1 freeze (setup, not an E1 result): identical package set
  (`env_freeze` sha256 `db0a13e9…`), identical raw CSV hashes, identical semantic manifest (`e8e9bfc7…`) and the
  same three native values (E0's `run_e0.py --regen`, output kept in the ignored `runs/e0_rebuild/`).

## Earlier results preserved

- **PR #2** (dbt/DuckDB viability): existing dbt definitions could be inspected and governed checks executed;
  no native MetricFlow execution, no autonomous accuracy, no live platform.
- **PR #3** (Publicodes governance-integrity): STOP_KERNEL for a persistent link store claimed as a performance
  differentiator over Claude Code with notes. A bounded negative differentiation result, not a project verdict.
  E1 does not compare against an LLM and makes no differentiation claim.

## Deviation from the de-risking plan, recorded

The plan's E1 lists a third case "C: one material ambiguous requirement lacking authority". The E1 execution
prompt (newer, explicit) instructs that ambiguity be deferred to a later interpretation experiment and that E1
isolate known meanings plus exposed/missing predicates (cases A, B1, B2). E1 follows the execution prompt.
Ambiguous or unauthorized meaning remains **untested** after E1.

## What E1 does not test

LLM interpretation; autonomous relationship discovery (E2); a formal IR (E3); independent verification of
generated specifications (E4); transposition or reverse reconciliation (E5, E6); audit persistence (E7); transfer
to authentic requirements (E8); legal compliance; settlement of any real payment; customer value. The cases are
tailored by the experimenter to a known test stack with supplied bindings, so they are **not** independent
discovery or real-enterprise benchmarks (design bias declared).
