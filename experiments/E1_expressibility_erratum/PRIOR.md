# E1 expressibility erratum: prior evidence and scope

Written 2026-10-12, before the erratum reproduction. **This is a retrospective replication, not a blind
experiment.** E2 (PR #6, `E2_blind_discovery/PRIOR.md`) already reported the native witness and its values. The
orchestrator who wrote E0, E1 and E2 also wrote this erratum. The expected outcome is therefore known, and the
erratum can only show whether that outcome reproduces and whether its mathematical preconditions hold.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** SOPHON_CHARTER.md v1.1 §2 says Sophon binds through the existing semantic
   layer and tracks requirements that cannot be represented. §3 TRACE/VERIFY say a binding claim must be
   evidenced. This sits in Stage 1 (feasibility). Plan risks R2/R3: whether known bindings, and the boundary of
   what the semantic layer can express, can be classified correctly.
2. **Smallest uncertainty.** Is E1's B1 requirement ("completed-order revenue, lines with charged unit price
   ≥ 100") natively expressible in the pinned MetricFlow layer by combining existing metrics at sales-line
   grain? If so, under exactly which mathematical preconditions, and are those preconditions true of the pinned
   rows?
3. **Semantic layer and data.** Same as E0–E2:
   - upstream `behramkorkut/Governed-Analytics-Agent` @ `312e97ad192dcef02f688e31edc0a08c6cf4345f` (MIT);
   - dbt + MetricFlow 0.211.0 (`mf`, dbt-metricflow 0.13.0) on DuckDB;
   - seeded **synthetic** retail data (seed 42).
4. **Consistency with the architecture.** Correcting how "exposed" is decided is a prerequisite for any later
   validator (E3) that reuses E1's exposure logic. Nothing is proposed to or written into the semantic layer.
5. **Prior results built on.** Listed below. All are unmerged stacked drafts with no CI and no reviews.

## Branch topology (resolved before branching)

| PR | Branch | Head | Base |
|---|---|---|---|
| #4 (E0) | `experiment/e0-native-metricflow-2026-10-12` | `a84c855ab2fa75cf4697b4b2be28c5b1d055d727` | `main` |
| #5 (E1) | `experiment/e1-known-binding-2026-10-12` | `e0dd4741e3adf0ac096cebc5707c46ad014b7ea5` | E0 branch |
| #6 (E2) | `experiment/e2-blind-discovery-2026-10-12` | `39491cf55d9be16c49cb61ad40aec2ee18eb8670` | E1 branch |

`origin/main` is at `7c116c41ddf90aefcbad77321f518313aed6b08c`. None of the three PRs had merged when this
erratum started.

This erratum's branch, `experiment/e1-expressibility-erratum-2026-10-12`, was created from the E2 head
`39491cf`. It is a **chronological erratum to E1** that sits after E2 in the PR stack.

## The original E1 claim (commit `e0dd474`; files unchanged on this branch)

| File (sha256) | Line | Statement |
|---|---|---|
| `E1_predicate_binding/PROTOCOL.md` (`34557fbffa9d40a6…`) | 17 | hypothesis: B1 is `PRESENT_IN_SOURCE_NOT_EXPOSED` |
| same | 55, 74 | §3.1.4: a binding whose dimension is not in the native dimension list becomes `PRESENT_IN_SOURCE_NOT_EXPOSED`; the native probe is a **dimension** filter |
| same | 112 | PASS requires that "B1 native probe rejected" |
| `E1_predicate_binding/RESULTS.md` (`cbfcc57c0af30667…`) | 15 | P_UNIT_PRICE_GE_100: "native probe `--where "{{ Dimension('sales__unit_price') }} >= 100.00"` **rejected by MetricFlow (exit 1)**" → `PRESENT_IN_SOURCE_NOT_EXPOSED` |
| `E1_predicate_binding/DECISION.md` (`396515eb89266a3a…`) | 3 | **PASS_KNOWN_BINDING** |
| same | 10 | "B1 correctly classified from real source and catalog evidence" |
| same | 14 | "Not PARTIAL: B1 was genuinely available." |
| `E1_predicate_binding/evidence/run/case_results.json` (`521c99b087187524…`) | — | probe receipt: `mf query --metrics completed_revenue --where "{{ Dimension('sales__unit_price') }} >= 100.00"`, exit 1 |
| `E1_predicate_binding/evidence/b1_raw_diagnostic.json` (`da18fdaf30056027…`) | — | raw-CSV diagnostic for B1: 2024 1634542.08, 2025 1400232.75, 2026 752191.54 |

The code path that produced the classification is `E1_predicate_binding/src/evaluator.py` (`14a083e41171721b…`),
lines 213–230. When the bound dimension name is missing from `mf list dimensions`, it does two things:
- scans the catalog for a dimension or measure **whose expr is the physical column**;
- probes with a **Dimension** filter.

It never tries to express the predicate through metric filters, so "not a declared dimension" was read as "not
expressible natively".

## The competing evidence (E2, commit `39491cf`)

`E2_blind_discovery/PRIOR.md` (`c4efc7d883aaa30f…`), section "New finding about E1", records that this native
query ran (OBSERVED by the orchestrator while designing E2, before the E2 freeze):

```
mf query --metrics revenue --group-by metric_time__year \
  --where "{{ Metric('revenue', group_by=['sales']) }} >= 100 * {{ Metric('quantity_sold', group_by=['sales']) }} AND {{ Dimension('sales__status') }} = 'completed'"
```

It returned 2024 1 634 542.08, 2025 1 400 232.75 and 2026 752 191.54, equal to E1's raw diagnostic. Grouping by
the `sales` entity was noted to give 5 526 line-level rows. E2's RESULTS §5.4 and DECISION record this as an E1
erratum candidate. A comment on PR #5 (id `6120312648`) flagged it.

E2 did **not** record:
- the compiled SQL;
- any check of the mathematical preconditions;
- any negative control.

Those are what this erratum adds.

## Known before freezing (disclosed)

These facts are known from E0–E2 work. They are not new observations and are re-measured after the freeze:
- `fact_sales.revenue = cast(quantity * unit_price as decimal(12,2))`;
- `unit_price` is `DECIMAL(10,2)` cast from the CSV;
- `quantity` is INTEGER;
- the generator draws `quantity = randint(1, 5)`;
- dbt tests on `quantity` are `not_null` only; there is **no positivity test**;
- `revenue` and `quantity_sold` are simple sum metrics with no filter;
- `sales` is the primary entity of the `sales` semantic model (`sales_id` = `order_item_id`);
- about 4 050 of 5 526 lines have unit price ≥ 100.

## Mathematical claim to be tested

For a single line with integer quantity `q`, two-decimal unit price `u` and revenue `r = q·u` computed exactly:
- if `q > 0`, then `r ≥ 100·q ⇔ u ≥ 100`;
- if `q = 0`, then `r ≥ 100·q` holds for every `u`, so membership diverges, although a revenue *sum* is
  unaffected;
- if `q < 0`, the inequality reverses and both membership and the sum diverge.

The equivalence also needs three more things:
- each `Metric(..., group_by=['sales'])` value must equal that single line's own value, which needs `sales_id`
  to be unique;
- `r` must equal `q·u` exactly, with no rounding;
- the comparison must be exact, not floating point.

## Scope

In scope: this one pattern (a per-line unit-price threshold derived from line-grain revenue and quantity
metrics) on this pinned estate.

Out of scope:
- any general "derivable predicate" planner;
- changes to the E0 adapter, the E1 evaluator or its fixtures, or E2's scoring;
- re-scoring E1;
- E3.
