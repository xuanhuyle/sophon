# SOPHON CHARTER

**Version:** 1.0 — 11 October 2026  
**Status:** Owner-defined product direction; binding project instructions for assistants and contributors. The technical and commercial hypotheses below remain **unproven** unless cited evidence establishes them.

## 1. Mission

**Sophon is AI-native enterprise governance infrastructure.**

Its purpose is to maintain a **persistent, traceable, verifiable and auditable relationship** between an organization's authoritative governing requirements and the **existing semantic layer** through which its data systems are understood and consumed.

The objective is not to invent a smarter LLM or outperform the best coding agent at one-off document review. A powerful LLM can propose interpretations, discover discrepancies and generate changes **inside** Sophon. It is a replaceable reasoning component, not the competing product that Sophon must beat in reasoning accuracy.

The infrastructure should continue functioning when the model, prompt, chat session or operator changes.

**Product proposition, not proven product value:** enterprises may benefit from making governing-to-semantic alignment a continuous organizational capability, rather than relying on occasional analyses and informal institutional memory. Whether this is technically reliable, operationally useful and adoptable remains to be demonstrated.

## 2. Canonical architecture and integration boundary

```text
    AUTHORITATIVE GOVERNING CORPUS
    Regulations | contracts | approved organizational policies
    Amendments | authoritative interpretations | decisions
                        |
                        v
                      SOPHON
       TRANSPOSE | TRACE | VERIFY | AUDIT
                        |
                        v
             EXISTING SEMANTIC LAYER
    Business terms | metrics | semantic relationships
    Definitions | relevant business logic | versions
                        |
                       ↕
               EXISTING DATA SYSTEMS
    Warehouses | lakehouses | operational data sources
                        |
                        v
          DOWNSTREAM BI / AI CONSUMERS
```

This diagram represents **logical governance relationships**, not a promise that every system's physical dataflow follows those arrows literally. A semantic layer typically queries/models source data; it does not necessarily write back to operational databases.

**Non-negotiable product design decision:** Sophon's transposition and verification for data-governed business meaning operate **through the organization's existing semantic layer**, which is connected to its underlying data systems and serves downstream consumers. Sophon should capitalize on semantic definitions already developed and maintained by data teams (e.g. actual dbt/MetricFlow semantic objects, or Snowflake/Databricks-native equivalents).

- Do **not** redefine Sophon as a standalone policy engine, authorization gateway, new warehouse, replacement semantic layer, or a collection of direct modifications to arbitrary applications.
- Do **not** treat generic dbt transformation SQL, Publicodes, a text description or a fabricated YAML file as proof that an enterprise semantic-layer integration works.
- The semantic layer's **coverage has limits**: it does not necessarily encode approvals, human discretion, physical actions or an AI agent's runtime conduct. Explicitly distinguish **governed semantic outputs** from **verified downstream behavior**; never claim the latter merely because the former tests pass.
- Ambiguous, partially represented or non-representable governing requirements must be explicitly tracked as **UNRESOLVED / PARTIALLY_OBSERVABLE / OUT_OF_SCOPE** rather than marked compliant.
- If evidence shows the proposed boundary cannot support an important workflow, surface the architectural trade-off for the owner to decide. Do not silently introduce direct application-level enforcement as though it had always been the thesis.

## 3. The four inseparable capabilities

### TRANSPOSE — requirements to semantic implementation

Detect a new governing document, amendment, approved interpretation or policy decision; resolve which provisions are applicable and effective; discover affected **existing semantic definitions**; propose the necessary semantic-layer change; and demonstrate effects using that layer's native query/compile interface and underlying data.

Sophon can propose a change autonomously, but an LLM proposal is **not** a binding legal interpretation or an authorized production deployment. Preserve human approvals and who has authority to grant them; never invent authorization.

### TRACE — durable relationships

Keep persistent, versioned, inspectable links between:
1. precise governing source/provision and authority/provenance;
2. temporal applicability (publication/observation versus effective dates);
3. interpretation, decision, approval or unresolved question;
4. actual semantic object and revision, with known dependencies;
5. proposed/accepted implementation changes, verification checks, evidence and downstream consumption **where actually observable**.

Maintain these relationships when **either side changes**. Avoid stale assurances and unnecessary propagation to unaffected objects. A mapping suggested by an LLM is not necessarily a verified relationship.

### VERIFY — independently check alignment in both directions

- **Governing → semantic:** a new or amended requirement triggers impact analysis, proposed transposition, and revalidation.
- **Semantic → governing:** a changed metric, business rule, relationship or model triggers checking against still-applicable requirements.
- Test actual compiled/executed semantic behavior and relevant data when possible; distinguish implementation defects, data violations, harmless/equivalent refactors, ambiguous meaning, incomplete evidence and unknown coverage.
- A passed hash, a passing existing dbt test or a plausible LLM explanation **does not** by itself prove substantive compliance.

### AUDIT — reproducible, historical evidence

An independent reviewer must be able to reconstruct **what requirement was in force, what the organization knew at the time, what was implemented, who approved what (if anyone), which checks ran on which data and what remained unverified**, without the original LLM conversation.

Preserve original evidence or an independently retrievable immutable reference, semantic version, source/interpretation provenance, execution receipts, outcomes, missing evidence and approvals. Hashing verifies integrity against a trusted anchor; it is not proof of correctness or authorization.

**These states are distinct and must not be conflated:** PROPOSED, APPROVED (by genuine authority), IMPLEMENTED, LINKED/TRACEABLE, VERIFIED_FOR_RECORDED_CHECKS, and NOT_VERIFIED/UNKNOWN.

## 4. Smallest meaningful working product

A minimal vertical slice should demonstrate the **complete lifecycle**, not only a sophisticated analysis:

1. Register an authoritative-or-explicitly-lab-authored requirement with correct source, observed/publication and effective dates.
2. Link it to a real **pre-existing executable** semantic definition and its data-backed metric.
3. Accept an amendment, retain the old version and generate a proposed change **to that semantic layer**; keep approval/deployment distinct from proposal.
4. Re-execute independent semantic checks and record their results and applicable limits.
5. Introduce a semantic-originated change and show reverse governance reassessment plus a harmless/no-op control.
6. End the original model process, then reconstruct as-of state and evidence through an independent process; catch tampering, missing approvals and future-information leakage.
7. Account explicitly for policies outside the layer's observable scope.

Reusing Git, SQL/SQLite, content hashes, metadata catalogs and an off-the-shelf LLM is encouraged. Novel algorithms, proprietary DSLs, orchestration and production features are **not prerequisites** for a working slice.

An artificial but faithfully labelled policy and a working real semantic layer can establish **engineering feasibility**. Such a test cannot establish authentic legal interpretation accuracy, enterprise-wide coverage, operator behavior, customer value or competitive differentiation.

## 5. Four different questions and evidence standards

| Stage | Question | What evidence permits us to conclude |
|---|---|---|
| 1. Infrastructure feasibility | Does the actual governance-to-existing-semantic-layer lifecycle work, persist and audit independently? | Reproducible working code, real native semantic execution, correct change/history/integrity tests |
| 2. Reliability and scope | Does the mechanism remain correct across challenging, unseen, authentic changes and known unknowns? | Independent oracles, correct chronology, adversarial controls, measured errors and missing coverage |
| 3. Operational usefulness | Does it solve a real recurring organizational governance problem with tolerable maintenance? | Real usage and observed operational results; not just a compelling demo |
| 4. Adoption / business | Do teams repeatedly choose, rely on and potentially pay for it rather than alternatives? | Actual customer behavior and economics, not customer interviews alone |

**Do not substitute one validation for another.** A failed algorithmic novelty test is not a failure of basic infrastructure feasibility. A working toy integration is not proof of reliability, adoption or commercial viability. Evidence of LLM parity is not proof that organizations need no governance infrastructure; equally, the need for recordkeeping is not proof they need Sophon instead of available tools.

Conventional alternatives (Git/CI, dbt tests, catalogs, policy-as-code, data contracts, lineage and AI agents) are legitimate building blocks **and** potential substitutes. Evaluate the build-vs-buy / integration trade-off honestly at the appropriate stage.

## 6. Prior results: preserve boundaries of inference

- **21 September 2026 authority/control-plane audit:** bespoke authorization/authority logic showed parity with disciplined policy-as-code in the tested setting. Do not resurrect the extra control plane without a different, evidenced need. See `docs/REPORT.md` and `docs/DECISION.md`. Those reports describe an **earlier iteration** of the project; they do not override this charter.
- **28 September 2026 dbt/DuckDB viability (PR #2, `codex/alignment-review-agent`):** existing data-team definitions could be inspected and governed checks executed; some real public-data discrepancies were identified. Legal-policy matching, autonomous accuracy, native BI semantic-layer execution and enterprise reliability were **not proven**.
- **11 October 2026 governance-integrity test (PR #3, `experiment/governance-integrity-2026-10-11`):** `STOP_KERNEL` **for a specialized persistent-link store claimed as a performance/accuracy differentiator over Claude Code with conventional notes/tools in a Publicodes law-to-rule benchmark**. That store worked as infrastructure but did not change the scored primary answers and had higher token/time cost. The experiment used **Publicodes, not an enterprise BI semantic layer**. A preregistered nonchronological task order exposed future 2026 texts to earlier maintenance tasks; post-hoc scorer/reference corrections were recorded. Its findings do **not** constitute a verdict that persistence, governance infrastructure or Sophon's intended architecture is unnecessary.

Historical reports, decision files and rejected hypotheses must remain accessible, even when they conflict with the current direction.

## 7. How assistants and contributors must prevent conceptual drift

**Before** any substantial recommendation, experiment, code change or Claude Code task:

1. **Anchor:** read this charter, the most recent relevant experimental decision(s) and existing implementation. State which stage in §5 is being tested.
2. **Specify:** name the concrete uncertainty, smallest end-to-end capability/counterexample, real/synthetic authority, the semantic runtime to use, and what result would count as success/failure/inconclusive.
3. **Check alignment:** verify that all FOUR capabilities (§3) and the semantic-layer boundary (§2) are respected, even when the immediate experiment tests only one thin part.
4. **Execute and audit:** keep cases and reference oracles independent when correctness is at issue. Enforce **monotonic decision-time chronology across all persistent agent state**; isolate future evidence. Keep unscored diagnostics separate from blinded evaluations. Preserve first-run outcomes, costs, failures and correction history.
5. **Conclude narrowly:** label OBSERVED / INFERRED / ASSUMED. State exactly which of the four validation stages changed. Never present a narrow negative experiment as a product-wide kill or a simple technical demo as a validated business.

### Anti-drift checklist — stop and surface a conflict if a plan:

- Reframes the core goal as **outperforming an LLM** or inventing a new technical primitive.
- Substitutes direct control of arbitrary downstream applications for governance **through the existing semantic layer**.
- Equates a one-off policy-vs-SQL comparison with persistent traceability and auditability.
- Calls hashes, Git diffs, model-produced text or CI output substantive verification without inspecting their meaning.
- Promotes unapproved interpretations, inferred bindings or missing evidence to authoritative, complete or verified.
- Treats missing customer interviews as a prerequisite for testing technical feasibility, or regards customer interviews alone as business validation.
- Silently changes the product thesis in response to a benchmark outside its scope.

### Authority and changes to this charter

This charter records the **owner's established product decisions**. An assistant may challenge any assumption with concrete evidence, but **must not silently redefine it** or use an experiment to replace it.

A material change to purpose, the semantic-layer boundary, the four capabilities or the success criteria requires an **explicit owner decision** documented in a new dated charter revision/decision record. Experiments may challenge hypotheses; they do not themselves rewrite these decisions. The owner's subsequent explicit instructions take precedence; preserve version history.

If an older README, prompt, report, feature branch or agent instruction conflicts with this file, treat the older text as **historical context** and surface the discrepancy. Do not erase the prior evidence. The charter governs **new work**, but it is not an assertion that the proposed design has been empirically validated.
