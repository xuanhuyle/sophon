# E5: prior and task entry statement (written before the freeze)

Branch `experiment/e5-forward-transposition-2026-10-12`, created from E4's head `d6fe13d` (draft PR #10,
PASS_INDEPENDENT_VERIFICATION_SIGNAL). Governing documents read in full from `origin/main` (`1beb70a`):
`SOPHON_CHARTER.md` v1.1, `CLAUDE.md`, `AGENTS.md`, `SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md` and the E5
prompt `Claude_Code_Sophon_E5_Forward_Governed_Transposition_2026-10-12.md`. There have been no governing
amendments since E4.

## Task entry gate (CLAUDE.md)

1. **Charter section and stage.** Charter §2 (governance through the existing semantic layer), §3 TRANSPOSE (with
   VERIFY and AUDIT evidence), §4 and §4A. Plan §5 E5, risk R6. Stage: **feasibility, with a narrow reliability
   signal**. This is not operational usefulness or adoption.
2. **Smallest uncertainty under test.** Holding the approved interpretation and the native binding fixed, can one
   approved amendment (P1 threshold 100 → 120, effective 2025-01-01) be turned **mechanically** into the correct
   minimal in-place edit of an existing native MetricFlow metric? Can that edit be independently verified, with
   history preserved and an unrelated metric (P2) untouched?
3. **Semantic layer, data and provenance.**
   - **Semantic layer (genuine):** the public MIT upstream `behramkorkut/Governed-Analytics-Agent` @ `312e97ad`,
     dbt + MetricFlow 0.211.0 on DuckDB.
   - **Data (synthetic):** the upstream generator, plus one E5 control fixture (BOUNDARY120).
   - **Metrics (lab-added):** the native metrics `premium_completed_revenue` (E4 M6B) and `french_market_revenue`
     (E4 M2). They are **not** organically maintained enterprise metrics.
   - **Governing sources (LAB_AUTHORED):** the v1 policy (E3) and the v2 amendment (E5).
   - **Approvals (LAB_SIMULATED).**
   - **Not proved:** legal accuracy, real authority, customer value, production deployment, downstream BI/agent
     behaviour, transfer to authentic or unseen contracts.
4. **Architecture consistency.**
   - The change is made **in the organisation's existing executable semantic layer** (a MetricFlow YAML edit)
     and executed natively.
   - The edit is proposed, never deployed.
   - Verification reuses E4's independent native candidate execution and row comparison.
   - No DSL, compiler, agent fleet, event store or deployment orchestration.
5. **Prior results kept as they are:**
   - E1's original B1 PASS was withdrawn by the erratum.
   - E2 was PARTIAL.
   - E3 and E3.1 passed. E3.1's limitations remain.
   - E4 passed, but every E4 example was designer-authored, and detection depends on registered snapshots.

## Prior expectations (before any transposer exists)

- **Mechanical difficulty is low.** One threshold literal in one filter, with the binding fixed. The risk in E5 is
  not that the edit is hard. It is that the experiment becomes tautological, in one of three ways:
  - the "transposer" copies a known answer;
  - the checker certifies whatever was proposed;
  - "history" is shown by querying a single new metric over all years.
  The design targets those three failure modes.
- **Expected outcome.** I expect the transposer to emit the in-place edit, the generated revision to conform to v2
  on 2025+ rows, the baseline to fail v2 with rows priced in [100, 120), and P2 to be identical.
- **Where it could fail:**
  - MetricFlow refusing the edited filter (unlikely: E4 M3 used `> 100` on the same dimension);
  - the time-window `where` used for version routing behaving differently from the oracle's order-date window
    (pre-freeze feasibility: it compiles to `metric_time__day >= '2025-01-01'`);
  - a subtle oracle/normalisation disagreement on the new boundary values.
- **Biases declared.**
  - One researcher wrote the amendment, the IR, the packet, the oracle, the fixture, the negative controls, the
    transposer and the scorer.
  - The packet is an **engineered hold-out**. The author knows the answer; the transposer process is merely
    prevented from reading the reference.
  - Independence here is **mechanical** (separate code, separate process, frozen truth), not organisational.

## Pre-freeze feasibility (OBSERVED, `evidence/prefreeze_feasibility/`, not scored)

**The combined baseline works natively.** The E4 M6B patch plus the E4 M2 patch, applied to the pinned project:
- loads, passes `dbt build` and `dbt parse`;
- semantic manifest `3532b0e6…`;
- both metrics query through genuine `mf`.

| Query | 2024 | 2025 | 2026 | Lines |
|---|---|---|---|---|
| P1 `premium_completed_revenue` | 1 634 542.08 | 1 400 232.75 | 752 191.54 | 3 305 |
| P2 `french_market_revenue` | 310 780.14 | 261 972.06 | 155 221.02 | — |

Both equal E4's frozen values.

**Version routing is expressible.** The windowed queries (`{{ TimeDimension('metric_time', 'day') }} >= '2025-01-01'`
and `< '2025-01-01'`) execute, and their year totals split exactly.

**The pinned data alone already distinguishes v1 from v2:**
- 69 completed 2025+ lines are priced in [100, 120);
- 10 lines are priced in [119, 120), so `>= 119` is caught on PINNED;
- **no** line is priced exactly 120, so `> 120` would agree by accident on PINNED. BOUNDARY120 adds line 22 at
  120.00.

**No unforeseen expressibility limitation was found.**
