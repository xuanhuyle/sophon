# Task: map governing clauses to an existing semantic layer (read-only, evidence-grounded)

You are given (below, in this single message) six short governing clauses and a read-only evidence packet describing
one existing analytics stack: a dbt project on DuckDB with a MetricFlow semantic layer, its source tables and
the scripts that produced the raw data. You have no tools; everything you may use is in this message. Do not
assume any file, table, column, system or approval that is not shown here.

The clauses are LAB_AUTHORED test requirements, not approved organizational policy. The data are synthetic.

For each clause, decide which business predicates it requires, which existing MetricFlow metric and semantic
objects (if any) can apply each predicate, which physical warehouse fields carry the underlying facts, and what
cannot be established. Abstaining or reporting a gap is an acceptable outcome when the evidence does not support a
mapping. A confident mapping that the evidence does not support is the worst possible answer.

## Bounded estate

The bounded estate is exactly what this packet shows: the semantic YAML and native MetricFlow catalog listings,
the dbt models, the warehouse schema (every relation and column), low-cardinality observed values, the raw
landing-file headers and the scripts that generated and loaded the raw data. "Not found" means not found in this
estate, never "does not exist anywhere".

## Predicate classifications (use exactly these strings)

- `BOUND_AND_EXPOSED`: the fact exists in the estate AND a native MetricFlow query can apply the predicate by
  itself: choice of metric, `group_by` items (dimensions, entities, `metric_time__<grain>`), and `where`
  filters referencing `{{ Dimension('entity__dimension') }}`, `{{ TimeDimension('entity__dimension', 'grain') }}`,
  `{{ Entity('entity') }}` or `{{ Metric('metric_name', group_by=['entity']) }}` (MetricFlow 0.211 supports
  metric filters evaluated at an entity's grain). No computation, lookup or post-processing outside MetricFlow.
- `PRESENT_IN_SOURCE_NOT_EXPOSED`: the fact exists in the estate's tables, but no native MetricFlow construct
  listed above can apply it; it would need custom SQL, an external lookup or post-processing.
- `NOT_FOUND_IN_BOUNDED_ESTATE`: no field in the estate records the required fact. Do not substitute a
  different fact.
- `UNRESOLVED_INTERPRETATION`: the clause admits materially different readings that nothing in the packet
  resolves; name the readings.
- `NOT_ESTABLISHED_AUTHORITY`: a candidate field exists, but nothing in the packet establishes that it is an
  authoritative record of the required fact.

An order lifecycle status (for example a value such as completed, returned or cancelled) is not evidence of
payment, cash collection or settlement unless the packet explicitly shows an authoritative equivalence.

## Overall verdict per clause (use exactly one)

- `VERIFIED_FOR_SPECIFIED_CHECKS`: every required predicate is BOUND_AND_EXPOSED and your native query computes
  the whole requirement.
- `PARTIAL_OR_UNKNOWN`: some predicates can be applied natively, others cannot or are unknown.
- `NOT_VERIFIABLE`: a required fact is absent from the estate, so the requirement cannot be computed or checked.
- `REQUIRES_AUTHORIZED_INTERPRETATION`: a material reading must be decided by an authorized person before any
  mapping can be accepted.

## Output: a single JSON object and nothing else

```
{
  "cases": [
    {
      "clause_id": "<H1..H6>",
      "predicates": [
        {
          "predicate_id": "<your id>",
          "text_span": "<exact phrase copied from the clause>",
          "meaning": "<what must be true>",
          "classification": "<one of the five strings>",
          "semantic_object": "<native object applying it, e.g. a metric name, Dimension('x__y'), metric_time__year, or null>",
          "value": "<literal compared, if any, else null>",
          "physical_fields": ["<schema.table.column>", "..."],
          "evidence": ["<packet file and the line or excerpt you rely on>"],
          "missing_or_open_question": "<what is missing or must be decided, else null>",
          "confidence": "<high|medium|low>"
        }
      ],
      "native_query": {"metric": "<metric name>", "group_by": ["..."], "where": ["<MetricFlow where expression>", "..."]},
      "can_establish": "<what a native query would establish>",
      "cannot_establish": "<what it cannot establish>",
      "overall_verdict": "<one of the four strings>",
      "overall_confidence": "<high|medium|low>",
      "abstain": <true|false>
    }
  ]
}
```

Rules: one entry per clause, ids H1 to H6. Split each clause into atomic predicates (one fact per predicate; a
grouping by year is a predicate). `native_query` may be null when no native query is appropriate. Use only
evidence shown in this message.
