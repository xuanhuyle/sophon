# Sophon — Engineering De-risking Plan

**Version:** 0.1 — 12 October 2026
**Status:** Owner-requested engineering plan; not an executed experiment or a charter amendment.
**Governing document:** SOPHON_CHARTER.md v1.1.
**Relevant prior research:** xuanhuyle/rulebook, Parts I (interpretation / assurance) and IV (operationalizing written requirements); Sophon PR #2 and PR #3.
**Next executable task:** E0, described separately in Claude_Code_Sophon_E0_Native_Semantic_Adapter_2026-10-12.md.
**Relationship to the earlier broad G1 prompt:** retain Claude_Code_Sophon_Governed_Transition_Experiment_2026-10-12.md as a *deferred integration acceptance test*, **not** the immediate execution instruction. No earlier results or prompts are erased.

## 1. Mission and engineering claim

Sophon aims to maintain a persistent, traceable, independently verifiable and auditable relationship between:

1. **Authoritative governing corpus:** genuine laws, contracts, approved policies, amendments, authoritative interpretations and approvals (owned by the appropriate organization or authority).
2. **Formal governance intermediate representation (IR):** an explicit machine-readable representation of approved meaning, including predicates, calculations, exceptions, applicability, validity dates, uncertainty and data bindings. This is an **internal Sophon specification**, not a source of legal authority.
3. **Existing executable semantic layer:** independently maintained native dbt/MetricFlow, Snowflake or Databricks semantic definitions and their underlying data. Sophon must extend—not replace—this layer.

Two directions are essential:
- **Governance → implementation:** find changes in governing requirements, propose/update an approved specification, determine affected existing semantic definitions, propose native changes and verify their effects.
- **Implementation → governance:** when the semantic layer changes independently, compare actual compiled/executed behavior against the still-applicable authorized specification and record discrepancies, harmless changes and unsupported coverage.

Keep TRANSPOSE, TRACE, VERIFY and AUDIT as the four product capabilities in the charter. Individual experiments may isolate one, but their outputs must remain compatible with the other three.

**What the de-risking programme tests:** a technically credible and bounded mechanism to interpret, bind, represent, validate, translate, reverse-check and maintain these relationships. **What it does not test:** commercial demand, enterprise ROI, proprietary technological moat, all of legal compliance, arbitrary application enforcement or general-purpose autonomous legal reasoning.

A successful end-to-end workflow may consist of standard tools assembled well. No novel algorithm or feature unavailable to the incumbents is required. Product value is an unproven customer **outcome gap**, not a presumed vendor **feature gap**.

## 2. Minimal architecture and ownership

    Governing documents and amendments   [authoritative, externally owned]
                  |
                  v
    Interpretation proposal              [untrusted AI, evidence-linked]
                  |
       Authorized interpretation          [owner-approved or UNRESOLVED]
                  |
                  v
    Formal governance IR                  [typed normative specification]
       - predicates, math, exceptions, scope, dates, provenance
       - UNKNOWN, conflict, ambiguity and missing evidence
                  |
                  v
    Predicate bindings                    [separate from normative meaning]
       - semantic object identities and revisions
       - authoritative fields vs proxies vs missing data
                  |
                  v
    Sophon translation / independent verification / trace / audit
                  |                          ^
                  v                          |
    EXISTING native semantic layer ---------+
       dbt MetricFlow, later optional native equivalents
                  |
                  v
    Existing warehouse / lakehouse and BI / AI consumers

**Key design constraint:** separate the *normative model* (what should be true) from the *binding model* (where the relevant data actually lives) and the *execution model* (what the semantic layer calculates). The data binding cannot silently change governing meaning.

**Authority gate:** a syntactically valid IR or LLM-produced test does not establish legal correctness. Preserve evidence of what was proposed, which human/organization approved any interpretation, what was deployed (if anything), and exactly what was verified. Lab approvals are explicitly SIMULATED; do not call them real.

**IR design policy:** begin with typed JSON/JSON Schema, simple explicit arithmetic/Boolean constructs and precise provenance. Adopt an existing formal language/standard if it provides the required semantics. Do **not** create proprietary syntax, compiler infrastructure or a DSL until concrete tests show why conventional typed structures are inadequate.

## 3. Risk inventory and ranking

| Risk | Question | Assessment | Earliest experiment |
| --- | --- | --- | --- |
| R1 — Native access | Can we inspect and execute existing *actual* semantic metrics and underlying data? | Low–moderate integration risk; untested here | E0 |
| R2 — Predicate binding | Can requirements be mapped to the correct semantic identities, predicates and source data? | Very high, central | E1, E2 |
| R3 — Observability | Can the system detect ambiguous meaning, conflicting obligations and missing/untrustworthy data before claiming verification? | Very high | E1, E2 |
| R4 — IR value | Does explicit typed formalization detect real errors or meaning loss that ordinary prose does not? | High; proposed abstraction unproven | E3 |
| R5 — Independent correctness | Can actual semantic behavior be tested against an oracle not derived from the model's own possibly incorrect interpretation? | Very high; central | E4 |
| R6 — Native transposition | Can an authorized specification produce correct native semantic edits without changing unrelated metrics? | Moderate–high | E5 |
| R7 — Reverse reconciliation | Can implementation-originated material drift be distinguished from harmless/equivalent changes? | High | E6 |
| R8 — Chronology and audit | Can approvals, interpretations, data evidence and versions survive process loss and support true known-at/effective-at reconstruction? | Moderate; partly explored in PR #3 | E7 |
| R9 — Transfer | Do the guarantees survive independently authored authentic requirements and unknown cases? | Very high; no empirical proof yet | E8 |

Concentrate first on R2–R5, the potential thesis-breaking problems. R1 is a small prerequisite. Basic persistence does not warrant speculative architecture; reuse ordinary storage and Git.

## 4. Experimental integrity rules

Every experiment must:
- State **one primary uncertainty**, specific inputs, declared prerequisites, failure/inconclusive conditions and an explicit *non-claim*.
- Freeze its protocol, source revisions, data fingerprints and expected oracle behavior **before** reading scored outputs or changing the system under test. Preserve first-run artifacts and record corrections.
- Use a real native semantic execution interface whenever claiming semantic-layer behavior. Ordinary dbt SQL, invented YAML and Publicodes are *not* replacements for native enterprise semantic execution.
- Establish authority and independently derived correctness references separately from an LLM's proposal or self-written checks. Test that the oracle fails on intentionally wrong inputs (mutation controls).
- Distinguish LAB_AUTHORED and synthetic inputs from independently authored governing documents and customer deployments.
- Preserve **observation/knowledge time separately from effective/valid time**. No future-information leakage into earlier stage contexts or carried-forward notes; make chronology mechanically enforceable in historical evaluation.
- Report OBSERVED, INFERRED and ASSUMED separately. "Verified" means **verified for recorded checks under specified inputs**, never general legal or downstream operational compliance.
- Preserve meaningful negative outcomes. Do not relabel a blocked native runtime or missed requirement as success after substituting an easier problem.
- Use existing components wherever possible: Python, JSON Schema/Pydantic where warranted, SQLite, Git, dbt/MetricFlow and independent data-backed checks. Do not build a policy engine, custom legal DSL, microservices, graph DB or GUI just to satisfy a diagram.
- Finish with a small, independently reproducible artifact and an explicit recommendation: continue, narrow, repair or stop.

### Prior results to preserve

- Sophon September authority/control-plane study: policy-as-code parity in its tested authorization setting; do not revive that separate enforcement thesis.
- PR #2 (dbt/DuckDB): useful evidence of inspecting existing definitions and underlying real datasets, but no production native MetricFlow end-to-end integration and no blind real-contract reliability result.
- PR #3 (Publicodes): persistent links and reproducible records worked, but the added store did not outperform Claude Code with ordinary notes on the scored tasks; verdict STOP_KERNEL concerns that bounded performance differentiator, **not** Sophon's product. The task sequence revealed future texts to earlier historical maintenance contexts; avoid the chronology defect.
- Rulebook: operationalizing requirements consists of locating, interpreting, binding, choosing mechanisms, encoding, reconciling, validating, assigning ownership and maintaining. The difficult steps are not simply generating source code. Its first deployment-level census concluded INSUFFICIENT EVIDENCE for the market/authority bottleneck hypothesis.

## 5. Small experiments — scope, checks and deliverables

### E0 — Native semantic adapter

**Single question:** Can one existing native MetricFlow metric be enumerated, inspected and executed on actual warehouse rows through its own engine?

**Fixed:** No governing policy, no LLM accuracy question, no amendment, no IR, no database, no audit infrastructure.

**Environment:** Prefer existing public project behramkorkut/Governed-Analytics-Agent pinned at a verified commit (candidate 312e97ad192dcef02f688e31edc0a08c6cf4345f). Confirm license, dependency lock, metrics and source data before running; synthetic data are acceptable for this engineering gate. Pin exact dependencies/environment. An alternative is permitted only if the real native runtime remains blocked after a bounded repair and the substitution is disclosed.

**Build:** Small read-only adapter to enumerate existing metrics and associated native semantic identities, trace a selected metric to its definition/dependencies, run one native MetricFlow query, preserve the actual result/compiled SQL when available, and reproduce it. Compare the result with independent row-level arithmetic if technically possible without disguising that cross-check as a semantic query. Check whether a BI/AI consumer actually calls the same catalog; if uncertain, say so.

**PASS:** Native semantic execution works on real generated warehouse rows with reproducible result, pinned source revision and provenance.

**BLOCKED:** Native execution cannot be established; preserve exact diagnostics, do not substitute arbitrary SQL or invented semantic YAML.

**Deliverable:** Minimal reusable adapter, reproducible test/logs, exact Windows PowerShell and Linux commands, E0_DECISION.md. R1 is the only risk retired.

### E1 — Manually known binding and observability

**Single question:** Given an *authorized and supplied* interpretation, can a small model recognize which required predicates are actually represented in the semantic layer and underlying data?

**Fixed:** Exactly one metric; mapping for the fully observable case is supplied to avoid confounding the test with AI discovery. No amendments, translation or automatic approval.

**Cases:** A fully observable formula; the same kind of requirement with one genuinely missing binding; one material ambiguous requirement lacking authority. Optionally a logical conflict as a separate diagnostic if inexpensive.

**Build:** Typed record for source clause, required predicates, candidate semantic objects, fields and provenance, proxy/authoritative/missing flags, uncertainty kind and bounded executable check where complete.

**PASS:** Correctly reports A as evaluable, B as NOT_VERIFIED / MISSING_BINDING and C as UNRESOLVED / AMBIGUOUS; missing evidence never becomes "compliant". Mutate/delete one binding to prove the gate fails.

**FAIL:** Invalid binding or ambiguous governing meaning is falsely promoted to verified.

**Deliverable:** Minimal binding and observability evaluator with independent negative tests. R2/R3 under human-supplied mapping only.

### E2 — Autonomous relationship discovery

**Single question:** Without a supplied mapping, can an AI propose the correct clause→predicate→semantic-object bindings, including abstention?

**Fixed:** Same native semantic stack as E0/E1. Existing source documents and independent reference prepared before the evaluated run. No implementation writes. Small cases with relevant, irrelevant, ambiguous and missing-data possibilities.

**Measure:** Required relationships found/missed, false associations, unsupported assurances, evidence validity, human corrections and time. Keep semantic retrieval, applicability interpretation and predicate binding errors separate.

**PASS:** Bounded evidence-backed mapping and honest unknowns on preregistered cases; no materially false verified claim.

**FAIL:** Material omission or incorrect relation is represented as definitely correct; report whether a human-approval fallback remains feasible.

**Deliverable:** Relationship-discovery evaluation harness; no blanket AI reliability claim. R2/R3 with autonomous proposals.

### E3 — Minimal formal governance IR

**Single question:** Does a typed, target-independent normative representation plus a separate binding representation supply *enforceable* guarantees useful for E1/E2?

**Schema:** Provenance, requirement identity, interpretation/approval state, populations, quantities/units, simple arithmetic/Boolean operators, exceptions, effective dates, predicates, dependency references, platform-specific binding pointers and explicit UNKNOWN states.

**Negative controls:** Undefined predicate; missing required binding; incompatible units; unsupported construct; contradictory or unresolvable temporal specification; missing authority for an "approved" claim; nonexistent semantic object.

**PASS:** At least one consequential failure is mechanically detected, and the bounded requirement is expressed without discarding material meaning. Tests demonstrate rejection of misleading but superficially valid inputs.

**FAIL/NARROW:** The schema loses necessary meaning or only stores prose; constrain supported rules or evaluate an existing formalism. Never treat parser/type validity as proof the interpretation is legally correct.

**Deliverable:** JSON Schema (or small typed models), parser/validator and mutation tests. **No proprietary DSL commitment.** R4.

E2 and E3 can run in parallel once E1 establishes the relevant semantic inputs; E3 is also usable with human-approved bindings if autonomous E2 underperforms.

### E4 — Independent native semantic verification

**Single question:** Can an approved specification reject an incorrect but plausible native semantic implementation without checking only its own derived output?

**Cases:** Correct implementation, materially wrong implementation that still compiles/queries, and insufficient-evidence case.

**Reference:** Independently specified behavior/row-level expected results frozen before tests. Do not generate oracle, implementation and evaluator in a single self-affirming LLM pass.

**PASS:** Actual MetricFlow execution matches correct case, rejects wrong case with counterexample, classifies missing evidence as NOT_VERIFIED. Mutation sanity checks prove test non-vacuity.

**FAIL:** Confident false assurance for material discrepancy; stop expanding architecture and locate whether interpretation, binding, expressiveness or oracle independence failed.

**Deliverable:** Independent semantic verification prototype. **Critical Gate A** with E3. R5.

### E5 — Forward transposition

**Single question:** Holding approved interpretation and mapping fixed, can a single amended IR produce a correct proposed native semantic edit without modifying unrelated metrics?

**Scope:** One controlled amendment to E4's approved specification, one relevant metric, one unaffected control. No automatic legal approval. Work only in disposable checkout.

**PASS:** Generates or proposes actual native change, it compiles and executes, independent expected behavior matches, prior version is preserved, unrelated metric unaffected, approval/deployment not falsely claimed.

**FAIL:** Incorrect/missing effect or unsupported construct silently approximated.

**Deliverable:** First minimal IR-to-MetricFlow transposition path. R6.

### E6 — Reverse reconciliation

**Single question:** Can one still-applicable approved IR expose a material independently introduced semantic change and accept a harmless change?

**Cases:** Deliberately wrong but well-formed calculation; harmless/equivalent refactor or metadata-only modification.

**PASS:** Wrong metric is flagged with independently reproducible native evidence; harmless change generates no false misalignment; material unobservable change is reported UNKNOWN.

**FAIL:** Changes detected solely through hashes are labelled substantive drift without evidence, or materially wrong behavior receives verified status.

**Deliverable:** Native implementation-originated reconciliation. **Critical Gate B** with E5. R7.

### E7 — Persistence, historical reconstruction and approvals

**Single question:** Can an independent process reconstruct governance and semantic state after successive changes, without the originating LLM's memory?

**Build:** Minimal event history with immutable/retrievable sources, authorized-vs-proposed interpretation, approval roles, schema/binding revisions, semantic revisions, source-known-at/effective-at times, native test receipts, unresolved states and provenance anchors. Prefer small SQLite/Git integration.

**Sequence:** V1 verified → V2 received → affected links invalidated → new proposal approved (lab approval explicitly simulated) → native revision verified → reverse-side drift → fresh independent audit.

**PASS:** Evidence-backed two-time-axis reconstruction, accurate approval absence and tamper detection under a declared trust model. No retroactive use of future material.

**FAIL:** Missing earlier source, invented approval, model memory needed to audit or undetected material tampering within the claimed trust model.

**Deliverable:** Minimal durable governance history and independent audit test. R8. Preliminary persistence may be used earlier; this is the full history gate.

### E8 — Independently authored, unseen reconciliation

**Single question:** Do semantic interpretation, binding and verification work beyond lab cases the system's designer constructed?

**Inputs:** Authentically authored governing requirements and existing executable semantic definitions with independently defensible expected behaviors, dated amendments if possible, and a separate reference evaluator. Precommit, separate sources from solver, test contested interpretations/unknowns. If such evidence is unavailable, call it BLOCKED, not synthetic success.

**Cases:** Unambiguous calculations, exceptions, temporal rules, non-local definitions, missing bindings, unrelated code changes.

**Measure:** Interpretation correctness, binding errors, material misses, unsupported verified assurances, appropriate abstentions, review workload and audit reproducibility. Report each case; no production precision or safety claim from a few cases.

**PASS:** A bounded independent signal with low/zero observed confident unsupported assurances; remain explicit about sample limits.

**FAIL/NARROW:** Reliability depends on hand-authored toy cases, hidden mapping provided to solver or same-model self-confirmation. Narrow the supported fragment or stop the general reconciliation claim.

**Deliverable:** Adversarial independent feasibility report. **Critical Gate D**. R9.

## 6. Dependency order and key decisions

    E0 (native semantic access)
            |
            v
    E1 (known mapping / observability)
            |
      +-----+-----+
      |           |
      v           v
    E2 (AI)     E3 (typed IR)
      |           |
      +-----+-----+
            |
            v
    E4 (independent verification)
            |
            v
    E5 (governing -> native semantic change)
            |
            v
    E6 (native semantic -> governance check)
            |
            v
    E7 (persistent bitemporal audit)
            |
            v
    E8 (independently authored real-world cases)

**Gate A after E3–E4:** Is formalization faithful and does the IR provide independently testable structural/behavioral guarantees? If not, reuse simpler schema or narrow supported scope—do not build a DSL.

**Gate B after E5–E6:** Do both directions work against native executable semantics and independent behavioral checks? If not, localize the defect; no platform build-out.

**Gate C after E7:** Is historical assurance independently reproducible beyond conventional Git/CI? Remove redundant proprietary storage if not justified.

**Gate D after E8:** Does the core approach survive authentic, independently authored unseen requirements without confident unsupported assurances? Only then invest in broader reliability testing.

**Commercial gate (separate):** The organization experiences a concrete *outcome gap*: a recurring expensive governed-change workflow that incumbent products/internal workflows do not adequately solve, with evidence of adoption, usefulness and eventually willingness to pay. A working lab experiment provides NO such proof.

## 7. Programme repository and operational constraints

Use isolated experiment branches/worktrees, never overwrite earlier PR #2/PR #3 artifacts. Stage runnable material in directories such as:

    experiments/E0_native_adapter/
    experiments/E1_predicate_binding/
    experiments/E2_relationship_discovery/
    experiments/E3_formal_ir/
    experiments/E4_independent_verification/
    experiments/E5_transposition/
    experiments/E6_reverse_reconciliation/
    experiments/E7_persistence_audit/
    experiments/E8_independent_validation/

For each: PRIOR.md / PROTOCOL.md (pre-frozen), reproducible implementation and tests, RESULTS.md, DECISION.md, code/data provenance. Reuse E0 adapter in subsequent experiments rather than duplicating an interface.

Prefer a single pinned upstream semantic project, a single metric, and the smallest independent oracle that can fail. Do not launch multiple expensive model sub-agents, large literature sweeps or broad acceptance tests as substitutes for an executable result.

## 8. Immediate implementation scope — E0 only

**First step:** Execute Claude_Code_Sophon_E0_Native_Semantic_Adapter_2026-10-12.md. E0 retires *only* R1. It should result in a small reproducible read-only native MetricFlow adapter, or a transparent BLOCKED_NATIVE_RUNTIME verdict.

**Do not execute E1–E8 in the same Claude Code task.** E1 is a *subsequent*, separately preregistered experiment once E0's evidence is reviewed.

**Do not execute the previous broad G1 prompt yet.** It is a useful later full transition acceptance test after critical semantic mechanisms are established.

## 9. Decision discipline

The question is not whether Sophon can accumulate extensive code, architectures, agents or documentation. Those are costs until justified.

- After E0: Do we have a native semantic interface?
- After E1–E3: Is the requirement actually representable/bindable, with a useful formal IR and honest unknowns?
- After E4: Can we establish substantive correctness with independent evidence?
- After E5–E6: Can we preserve that correctness when either governance or implementation changes?
- After E7: Can others independently reconstruct who knew, approved, implemented and verified what?
- After E8: Does the mechanism still work when the requirements were not written for our demo?

**Build the smallest component that retires the next risk. Keep the negative evidence. Stop or narrow whenever a critical property cannot be established.**
