# Claude Code — Sophon E1: Known Predicate Binding and Observability

**Date:** 12 October 2026
**Status:** NEXT EXECUTION PROMPT. Execute **E1 only** after reviewing E0 PR #4.
**Primary uncertainty:** R2/R3 in the engineering de-risking plan: Can an explicitly supplied, unambiguous governing predicate be bound to a real semantic/data representation, with correct identification of *unavailable* or *not semantically exposed* facts, without inventing evidence?
**Charter:** SOPHON_CHARTER.md v1.1. Respect TRANSPOSE, TRACE, VERIFY and AUDIT as future architectural requirements without implementing their full workflows here.
**Predecessor:** E0 PASS_NATIVE_RUNTIME in draft PR #4, branch `experiment/e0-native-metricflow-2026-10-12`.
**Deferred:** E2 autonomous discovery, E3 formal governance IR, E4 independent substantive verification of generated specifications, E5/E6 bidirectional change lifecycle, E7 audit infrastructure, E8 transfer, and the earlier broad G1 experiment.

## 0. Goal and one strict distinction

E0 demonstrated native `mf` access to an existing `completed_revenue` metric over a pinned, independently authored dbt/MetricFlow model and seeded DuckDB data.

E1 must demonstrate the **mechanics of predicate observability and a known binding**:

> Given a LAB_AUTHORED, unambiguous business requirement whose correct interpretation and expected binding are supplied by the experimenter, can a tiny read-only evaluator (i) substantiate a bound predicate with actual native semantic/data evidence, (ii) distinguish predicates present in underlying tables but NOT exposed in the semantic catalog, from (iii) predicates for which no authoritative fact is found in the bounded inspected data estate?

**E1 does NOT test LLM interpretation or relationship discovery.** Do not infer AI correctness, interpretive authority, customer value or general legal compliance from the synthetic result. It does not test whether a formal IR is superior (E3) or autonomous mapping succeeds (E2).

Most importantly:
- `PRESENT_IN_SOURCE_NOT_EXPOSED` is **not** the same as `MISSING_SOURCE_FACT`. The first may be addressed by an approved native-semantic extension later; the second requires additional authoritative information beyond the audited estate.
- `NOT_FOUND_IN_BOUNDED_ESTATE` is not proof that the fact does not exist anywhere in the organization.
- `status=completed` must **not** be assumed equivalent to a payment clearing/settlement confirmation.
- A native query proving the *existing* `completed_revenue` calculation does NOT prove a stronger requirement containing extra unbound predicates.

Keep source/provenance, interpretation/requirement, semantic exposure, underlying field presence, field authority and executable checking as **distinct facts**.

## 1. Read before doing any work

Read in full, not from memory or summaries:
1. `origin/main:SOPHON_CHARTER.md`, `origin/main:CLAUDE.md` and `origin/main:AGENTS.md`.
2. `origin/main:SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md` (risks, E1, experiment integrity, E2–E4 separation).
3. This prompt from `origin/main:Claude_Code_Sophon_E1_Known_Predicate_Binding_2026-10-12.md`.
4. On `origin/experiment/e0-native-metricflow-2026-10-12`, `experiments/E0_native_adapter/{PRIOR.md,SOURCE_GATE.md,PROTOCOL.md,RESULTS.md,DECISION.md,README.md}`; inspect `src/mf_adapter.py`, `src/crosscheck.py`, `tests/test_e0_adapter.py`, `evidence/run/compiled_query.sql`, and source/evidence manifests.
5. The latest E0 PR #4 status, comments/CI (if present). Do not treat absent CI checks as a pass.

Record in E1/PRIOR.md E0's exact bounded achievement: PASS_NATIVE_RUNTIME (R1 only), upstream `behramkorkut/Governed-Analytics-Agent` pinned `312e97ad192dcef02f688e31edc0a08c6cf4345f`, `completed_revenue`, seeded synthetic retail data, clean native MetricFlow output agreeing with independent raw-data recomputation. E0 provides no proof about governing requirements or semantic binding. Respect earlier PR #3 STOP_KERNEL as a bounded negative differentiation result, not a project verdict.

**Do not make charter or engineering-plan edits.** If the plan's earlier E1 suggestion includes an ambiguous clause, deliberately defer it to a later interpretation experiment. E1 isolates *known* meanings and missing/exposed predicates only.

## 2. Worktree + branch: E0 is NOT merged into main

**Important dependency:** PR #4 is a draft PR, not merged into `main`, as of this prompt. E1 must **reuse its committed adapter directly**, not rebuild it and not silently assume it exists on `main`.

- Inspect local `git status`, current branches and `git worktree list`; preserve any uncommitted work.
- `git fetch origin`.
- Create an isolated worktree for branch `experiment/e1-known-binding-2026-10-12` from `origin/experiment/e0-native-metricflow-2026-10-12`. If PR #4 has since merged, prefer `origin/main` **only after verifying the E0 adapter and receipts are there unchanged**.
- Unless E0 is merged, open E1 as a **stacked draft PR** whose base is `experiment/e0-native-metricflow-2026-10-12`, not main. This keeps the diff E1-only. Clearly identify the dependency on PR #4. If PR #4 merges, adjust base/rebase carefully; do not change existing E0 evidence.
- All E1 implementation files go under `experiments/E1_predicate_binding/` and are new. Import/reuse `experiments/E0_native_adapter/src/mf_adapter.py`; **do not copy or modify** it unless a real E0 defect makes that necessary, in which case document the defect and isolate the fix for review.
- Do not commit cloned upstream code, local databases, secrets or virtual environments. Existing source is fetched at a pinned commit, not invented or modified to make tests pass.

**Execution environment:** use the pinned upstream + locked versions from E0 (Python 3.11, MetricFlow 0.211.0, dbt-metricflow 0.13.0, dbt-core 1.11.11, dbt-duckdb 1.10.1). Reproduce the E0 native metric path within the new worktree; prefer using E0's documented setup/build and reusing its adapter over new scaffolding. Linux execution is acceptable; PowerShell instructions must be provided and flagged **untested** if not run on Windows. Avoid any real API key/LLM requirement.

## 3. First perform a bounded *inventory*, then freeze inputs and scoring

Before writing E1 binding evaluator logic or looking at E1 scored outcomes:
- Inspect the pinned upstream **read-only**: source CSV header definitions and generator, `bronze` source declarations, `stg_orders`, `stg_order_items`, `stg_products`, `fact_sales`, metric YAML, semantic model YAML and actual native semantic/dbt manifests.
- Record specific relations/columns, types/constraints if evidenced, lineage, metric identities, semantic entity/dimension/measure exposure and information source. Record whether claimed facts are *authoritative for the LAB policy* versus only a proxy.
- If a proposed predicate genuinely exists in the upstream sources, do not manufacture a missing-data result by ignoring it. If a candidate is absent only from MetricFlow but available upstream, correctly classify `PRESENT_IN_SOURCE_NOT_EXPOSED`, not `MISSING_SOURCE_FACT`.
- Explicitly define the **bounded inspected estate**: the relevant data files, declared bronze sources, dbt lineage to the selected metric, any other upstream source tables inspected, and catalog at the pinned revision. Note that a scan is not a universal impossibility proof.
- Freeze `PRIOR.md`, `SOURCE_INVENTORY.md`, `PROTOCOL.md`, `FROZEN_CASES.json`, a small independently written expected-case/oracle definition, and their hashes in a **protocol commit before E1 scored execution**. Avoid self-referential commit hashes: record protocol SHA and subsequent commit SHA separately without claiming the file's own hash was recorded in the same commit. Push the freeze if feasible.
- Reference the frozen E0 executable identities and source fingerprints and declare test design bias: LAB policies are tailored to a known test stack and supplied bindings, so the cases are **not** independent discovery or real-enterprise benchmarks.

No costly data hunt or generic schema crawler. If E0's original material is irretrievable, report a bounded setup issue instead of fabricating lineage.

## 4. Predefined, small cases (ONE metric, ONE policy family)

Use **one named LAB_AUTHORED policy family** with precise clauses and a supplied interpretation. No real-world signatures or authorizations are claimed.

### Case A: Fully observable known predicate

**LAB policy A:** "Eligible revenue for calendar year Y equals the sum of order-line quantity times unit price, counting only lines belonging to orders whose **normalized source order status equals the literal `completed`**; use the source order date to assign year. No settlement or cash-collection condition is implied."

**Supplied mapping:** `completed_revenue` native metric, `sales__status` semantic dimension / `stg_orders.status` and its known source, `sales.revenue` measure / `fact_sales.revenue`, `order_date`. These are declared lab mappings, not autonomous discoveries.

**Expected result:** `FULLY_OBSERVABLE_FOR_THIS_CALCULATION` if and only if exact native metric identity and lineage are backed by pinned evidence, the required predicate/value is genuinely represented, the MetricFlow query executes, and its observed output matches an independent row-based expected value for the lab-defined calculation. The case is NOT proof that the statuses are authentic financial settlement facts.

### Case B1: Predicate in underlying data but NOT in the native semantic exposure

Use a conditional predicate **actually observed in the pinned underlying source/fact rows** but not exposed as a suitable native semantic dimension/filter/measure for `completed_revenue`. A candidate to inspect is `unit_price` on `fact_sales`: for example, "A plus order-line unit price >= 100.00", if the field is truly present but lacks a native semantic dimension/usable predicate binding.

Only choose this B1 after the inventory confirms the field, authoritative meaning for this LAB requirement and absence from the **executable native semantic exposure**, not just the absence of the name in one YAML file. A foreign-key path or unsupported direct SQL access alone does not count as native MetricFlow predicate exposure. If `unit_price` is exposed, choose another genuinely demonstrated example with the same property or report CASE_B1_UNAVAILABLE; never mutate upstream semantics to induce a misleading gap.

**Expected result:** `PRESENT_IN_SOURCE_NOT_EXPOSED` with exact physical field evidence, lineage and native catalog evidence. Do not label "fully verified" merely because custom SQL could compute the condition; also do not classify it as a missing source fact.

### Case B2: Required business fact unsupported by the inspected data

**LAB policy B2:** "Eligible revenue follows A **AND** each included order has independently recorded final payment settlement confirmation from a payment processor." This is a deliberately stronger condition: neither order `status='completed'` nor `returned` alone is proof of external financial settlement.

Search the **frozen bounded estate** for a source that actually represents authoritative settlement confirmation (not merely a column with a suggestive name). If no such source exists, the expected result is `NOT_FOUND_IN_BOUNDED_ESTATE` / `NOT_VERIFIED`, citing inspected sources and limits of the claim. If credible settlement evidence exists, report it and pre-register the appropriate `PRESENT_IN_SOURCE_NOT_EXPOSED` or `FULLY_OBSERVABLE` result instead. Do not pretend B2 is absent because the desired score says so.

**Forbidden conclusion:** "MetricFlow returned completed revenue, therefore financially settled revenue is verified."

B1 and B2 are **negative controls**, not separate expansive product scenarios. Do not add ambiguity, legal precedence, contracting, amendment, agent operations or comparison against a different platform.

## 5. Implement the smallest evaluable binding/observability mechanism

Prefer a simple Python module and short JSON records in `experiments/E1_predicate_binding/`, with **no generalized governance DSL or bespoke ontology**.

What E1 must be able to do:
- Accept the frozen lab requirement ID, list of **supplied** required predicate IDs, target semantic metric and approved-in-lab binding references.
- Validate each binding against **actual** existing native semantic model/metric identities and source/dbt lineage, not just matching a string in the fixture.
- Check source fact existence separately from semantic exposure. Distinguish recorded source authority, observed provenance and mere field presence; for synthetic lab data, "authoritative" means only **designated by the lab definition**, not authentic external business authority.
- Query through the **E0 native adapter** for A and capture source/semantic versions, native compiled query/receipt and underlying dataset fingerprint. Cross-check independently from original raw CSVs (E0's crosscheck can be reused for A), not by feeding the native output into the supposed oracle.
- **Fail closed on proof claims** when a mandatory predicate is unsupported. Return meaningful distinctions: `FULLY_OBSERVABLE_FOR_THIS_CALCULATION`, `PRESENT_IN_SOURCE_NOT_EXPOSED`, `NOT_FOUND_IN_BOUNDED_ESTATE`, `INVALID_BINDING`, `UNVERIFIED` or `INCONCLUSIVE` as appropriate. Avoid generic "COMPLIANT" / "LEGAL_APPROVED".
- Attach inspectable evidence: clause text/hash, frozen semantic identities, field/lineage locations, actual scope of inspection, native output/receipts where applicable, and a list of uncovered predicates.

**Hard constraint:** A fully observable A must require *all* required predicates; adding a mandatory unbound settlement condition to A must force NOT_VERIFIED. No text-keyword heuristic, no static "A_PASS, B_FAIL" labels, and no fixture-based status classifier. A binding existing as a raw field alone cannot become a valid native semantic exposure.

Do not add automatic binding discovery, automated interpretation, a compiler or governance persistence beyond minimal evidence files. Do not modify the upstream project or E0 result.

## 6. Mandatory non-vacuity/adversarial checks

Score tests by **behavior**, not presence of expected report strings. Include:

1. **A positive**: case A native metric and independent raw-row calculation match under frozen identities; all required predicates resolved with evidence.
2. **B1 field exposure**: demonstrate field presence physically and absence as an applicable/native semantic predicate; return the distinct `PRESENT_IN_SOURCE_NOT_EXPOSED` classification. If no genuine B1 candidate exists, classify the subcase UNAVAILABLE and adjust overall verdict honestly.
3. **B2 missing source**: demonstrate bounded inventory and no trusted settlement field; return NOT_VERIFIED / NOT_FOUND_IN_BOUNDED_ESTATE, never assert universal absence.
4. **Binding mutation**: remove or point one A required binding at an existing *but incorrect* field/semantic object; evaluator cannot return full observability.
5. **Predicate-addition mutation**: append a required settlement predicate to A without adding data; evaluator must invalidate A's full observability even though `mf query` still returns the same plausible revenue number.
6. **Untrusted proxy attack**: propose `orders.status='completed'` as evidence of external settlement; reject this fact-level equivalence without an explicitly supported authorized rule.
7. **Native identity drift**: change target metric filter/semantic identity in a disposable manifest or controlled fixture; binding validity must fail, even if a previously recorded CSV result still exists.
8. **Negative oracle sanity**: intentionally alter one expected native amount/input and show that the independent numerical check rejects it. The cross-check cannot merely quote the MetricFlow result.
9. **Fresh-process replay**: read committed receipt/snapshot and independently re-evaluate binding statuses without conversation context; declare any trust limitations.
10. **No untested environment claim**: PowerShell instructions must be runnable in principle, but mark Windows as UNTESTED unless actually executed.

If one test fails, preserve output and mark the corresponding criterion FAIL. Never repair a scored failure without recording original score, reason, amendment and rerun in separately named evidence.

## 7. Bounded decision gate

Report EXACTLY one primary verdict:

- **PASS_KNOWN_BINDING**: A verified for the specified lab calculation, B1 correctly classified from real inspected source/catalog evidence, B2 correctly classified from the bounded source inventory, and adversarial checks 4–9 do not generate unsupported full-verification results. This retires only **known binding/observability mechanics for this tiny synthetic stack**, not autonomous R2/R3 reliability.
- **PARTIAL_KNOWN_BINDING**: A works and missing-source distinction works, but B1 example is genuinely unavailable or a noncritical evidence limitation prevents the full declared contrast. Explicitly preserve what remains untested.
- **FAIL_KNOWN_BINDING**: a material nonexistent/unexposed predicate or untrusted proxy is confidently promoted as verified, or existing field/identity changes do not affect the claim when they should; inability to substantiate A also fails if E0 native access remains functional.
- **BLOCKED_RUNTIME_OR_INPUT**: the pinned native environment or adequate source inventory cannot be executed/retrieved under the bounded attempt. State the blocker; no fake metric computation.
- **INCONCLUSIVE**: the independent oracle, source authority designation or evidence integrity is invalid, so none of the above verdicts is defensible.

No percentages or model accuracy claims from three lab subcases.

Budget: one upstream, one native metric, A plus B1/B2 controls, one inventory, one frozen protocol, minimum scripts and tests, no paid LLM API. **Do not start E2–E8.** Use ordinary Python and native MetricFlow; if implementation expands into a framework, STOP and report why.

## 8. Files to leave in the E1 branch

Under `experiments/E1_predicate_binding/`:

- `PRIOR.md` — technical charter alignment, observed E0 evidence and exact non-claims.
- `SOURCE_INVENTORY.md` — pinned upstream schema/field/semantic exposure/lineage facts; boundaries and provenance.
- `PROTOCOL.md`, `FROZEN_CASES.json`, hash manifest/recorded protocol commit.
- `README.md` — exact **executed** Linux instructions, PowerShell equivalent clearly marked untested where relevant; expected native setup.
- `src/` and `tests/` — small binding validator, case runner and adversarial tests. Import the E0 adapter without modifying it.
- `evidence/` — query receipts, independent cross-check output, tested mutation results and manifest fingerprints; generated DBs remain ignored.
- `RESULTS.md` — table by predicate and case: authoritative/lab-designated? present in source? semantically exposed? actual verified scope? missing conditions? receipts? measured outputs?
- `DECISION.md` — exact gate verdict, unresolved uncertainties, cheapest next experiment. Recommend **E2 autonomous relationship discovery** only if E1 supports the basic binding/coverage mechanism; otherwise localize the failed mechanic. E3 IR remains a separate later experiment.

Commit **protocol/inventory before scored execution**, then implementation, observed results and decision. Push feature branch and open **draft stacked PR targeting E0's branch**, unless E0 has been merged. Do not merge either PR automatically.

## 9. Final report to the owner

Return concisely:
- Branch, base branch, protocol commit + final commit, draft PR link.
- The one frozen LAB policy family and its supplied mapping.
- A / B1 / B2 results with source vs semantic vs authority/proxy distinctions.
- Native query result and independent calculation; explicit E0 reuse.
- The strongest negative-control result (e.g. `completed` is not a payment-settlement oracle).
- Any unverified or incomplete evidence, original failures and actual deviations.
- One gate decision and *one* technically justified next small experiment.

**STOP AFTER E1. The objective is to test reliable known bindings and honest observability boundaries—not to start writing Sophon's proprietary governance language.**
