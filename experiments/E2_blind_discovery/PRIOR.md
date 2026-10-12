# E2 — prior evidence and alignment

Written 2026-10-12 before the scored solver run.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** SOPHON_CHARTER.md v1.1 §2 (bind through the existing semantic layer; track
   unresolved or non-representable requirements explicitly), §3 TRACE/VERIFY (an LLM-suggested mapping is not a
   verified relationship), §5 Stage 1 → early Stage 2 (adversarial controls on unseen cases). Plan §5 E2:
   risks R2/R3 **without supplied bindings**.
2. **Smallest uncertainty.** Given only six LAB_AUTHORED clauses and a sanitized read-only evidence packet from
   the pinned semantic stack, does a genuinely fresh AI session propose clause → predicate → native MetricFlow
   object → physical field chains that survive independent mechanical scoring, with correct abstention where
   the chain cannot be established, and no false verified claim?
3. **Semantic layer and data.** Same pinned upstream as E0/E1 (`behramkorkut/Governed-Analytics-Agent` @
   `312e97ad`, MIT), dbt + MetricFlow 0.211.0 on DuckDB, seeded **synthetic** retail data. Governing clauses are
   **LAB_AUTHORED** by the E2 orchestrator. No real authority, approval or customer.
4. **Consistency with the architecture.** Discovery of which existing semantic objects a requirement touches,
   and honest reporting of what they cannot express, is needed in both directions (governance → implementation
   and implementation → governance). E2 proposes nothing to the semantic layer and writes nothing.
5. **Prior results built on.** Below.

## E0 — PR #4, branch `experiment/e0-native-metricflow-2026-10-12`, head `a84c855` (draft, unmerged, no CI checks, no reviews)

PASS_NATIVE_RUNTIME, R1 only: native `mf` execution of `completed_revenue` on the upstream's synthetic DuckDB
rows, equal to an independent raw-CSV recomputation, reproducible. Windows commands not executed.

## E1 — PR #5, branch `experiment/e1-known-binding-2026-10-12`, head `e0dd474` (draft, stacked on #4, unmerged, no CI checks, no reviews)

PASS_KNOWN_BINDING for known-binding mechanics on the tiny synthetic stack, with **experimenter-supplied
bindings** and an **experimenter-designated authority registry**. 16 tests reported passing; no Windows run;
no external authority; the plan's ambiguous case C was deferred.

### New finding about E1, made while designing E2 (OBSERVED, 2026-10-12, before the E2 freeze)

E1's B1 case ("completed revenue, only lines with unit price ≥ 100.00") was classified
PRESENT_IN_SOURCE_NOT_EXPOSED because E1's evaluator only checked whether a **dimension** exposed
`unit_price`. MetricFlow 0.211 also supports **metric filters at an entity's grain**. The native query

```
mf query --metrics revenue --group-by metric_time__year \
  --where "{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }} AND {{ Dimension('sales__status') }} = 'completed'"
```

ran and returned 2024 1 634 542.08, 2025 1 400 232.75, 2026 752 191.54, **exactly** E1's raw-row B1 diagnostic.
B1's requirement is therefore natively expressible. E1's classification was a conservative false negative, not
a false assurance, but E1's claim that B1 was "correctly classified" does not hold. E1's PASS rested on that
contrast. E2 keeps E1 byte-identical as instructed; the owner should decide on an E1 erratum. Grouping by the
`sales` entity also returns line-level native rows (5 526 rows). E2's packet states this native capability
explicitly, and E2's not-exposed case was chosen so that neither dimensions nor metric filters can reach it.

## Earlier results preserved

PR #2 (dbt/DuckDB inspection; no native MetricFlow), PR #3 (STOP_KERNEL for a link store as a performance
differentiator in a Publicodes benchmark; not a project verdict).

## Conflicts between the plan and the E2 prompt

None material. The plan's E2 is "autonomous relationship discovery"; the E2 prompt adds strict leakage controls,
six strata and frozen gates. The prompt's directory name `experiments/E2_blind_discovery/` is used (the plan
suggested `E2_relationship_discovery/`).

## Contamination and design-bias statement

The orchestrator (this session) designed E0, E1 and E2 and knows the stack and the reference. The cases are
LAB_AUTHORED by someone who knows which strata the estate supports. The solver is the same model family
(`claude-opus-5-5`) in a separate, tool-less, fresh process; it cannot read the repository or this session's
history, but its pretraining may include the public upstream project. None of this is eliminated by isolation.
