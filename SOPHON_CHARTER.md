# SOPHON CHARTER

**Version:** 1.1 — 12 October 2026  
**Status:** Owner-approved strategic clarification of the product direction in v1.0. Binding project instructions for assistants and contributors; technical feasibility, operational value, competitive differentiation and commercial prospects remain **unproven** unless demonstrated.

## 1. Mission

**Sophon is AI-native enterprise governance infrastructure.**

Its purpose is to maintain a **persistent, traceable, verifiable and auditable relationship** between an organization's authoritative governing requirements and the **existing semantic layer** through which its data systems are understood and consumed.

The objective is not to invent a smarter LLM or outperform the best coding agent at one-off document review. A powerful LLM can propose interpretations, discover discrepancies and generate changes **inside** Sophon. It is a replaceable reasoning component, not the competing product that Sophon must beat in reasoning accuracy.

The infrastructure should continue functioning when the model, prompt, chat session or operator changes.

**Product proposition, not proven product value:** enterprises may benefit from making governing-to-semantic alignment a continuous organizational capability, rather than relying on occasional analyses and informal institutional memory. Sophon's sellable result, if validated, is a **completed, controlled and auditable governance transition**—not merely an LLM answer, a policy-to-metric link, a dashboard or a new collection of features. Whether customers lack that end-to-end outcome, whether Sophon can deliver it reliably, and whether they will choose it over existing solutions remain to be demonstrated.

**Competitive framing:** Sophon need not invent a capability unavailable from Claude Code, Git, dbt, Snowflake, Databricks or governance products. A valuable software product can integrate existing components into an outcome organizations would rather buy than assemble and operate. Conversely, the theoretical ability of incumbents to build that workflow is not evidence customers will pay for Sophon; some already may have satisfactory solutions. **An outcome gap is a hypothesis requiring direct evidence, not a gap inferred from feature lists or startup analogies.**

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

**System-of-record boundary:** the contracting/legal/business authority retains ownership of its governing source and approvals; the data team and native platform retain ownership of executable semantic definitions, tests and deployment. Sophon owns the durable **cross-system reconciliation workflow and its relationship/evidence state**, subject to enterprise permissions. It should link to, not silently replace, systems of record. It may preserve independently verifiable snapshots/receipts as required for auditability. A workflow may be embedded as a native-platform extension rather than installed as a competing universal governance suite.

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

## 4A. Product logic: the customer's outcome gap, not a feature gap

**Atomic unit of value: one governed transition.** A governing requirement or an existing semantic implementation changes. Sophon carries it from detection to an explicitly dispositioned, source-grounded outcome:

1. **Intake:** identify the changed governing source (or semantic object), source owner, publication/observation and effective dates.
2. **Scope:** identify relevant existing semantic definitions and dependencies, unaffected objects, incomplete coverage and questions requiring authoritative interpretation.
3. **Decision:** propose interpretations and semantic-layer changes, recording whether an authorized person approved, rejected or left them unresolved.
4. **Implementation:** use the native semantic stack and the customer's deployment/review process to propose or apply only authorized changes.
5. **Verification:** independently run bounded semantic calculations/tests on identified data; retain counterexamples, uncertainty and verification limits.
6. **Closure and history:** record what was implemented, what remains blocked, who is accountable and exactly what an independent auditor can reconstruct at either historical knowledge-time or effective-time.

**Closure is not automatic compliance certification.** A transition may close as *implemented and verified for specified checks*, *correctly unchanged*, *rejected*, or *blocked/unresolved with an accountable owner*. A proposed patch is not a deployment, and a verified semantic definition is not proof of downstream operational behavior. Do not force every event to an apparently successful "compliant" result.

**What customers would buy (hypothesis):** faster and more complete implementation of authoritative changes, lower cross-functional coordination effort, fewer missed or unjustified semantic impacts, and cheaper reconstruction of trusted evidence. The infrastructure is valuable insofar as it repeatedly delivers those outcomes. A passive policy graph or audit database alone is not a sufficient product positioning.

**Build with incumbents rather than against an imaginary feature vacuum.** Native semantic catalogs, lineage, Git/CI, policy/data contracts, access controls, approval systems and high-quality LLMs are available components. Existing enterprise platforms may already solve much of the complete workflow. Sophon's differentiation is **not** presumed because it connects those components: it must demonstrate reduced customer work, time, risk or integration burden compared with a realistic configured incumbent or internal implementation. Being a vendor-neutral integration layer is a possible benefit only where customers actually face heterogeneity or cross-system ownership issues.

**Competitive red lines:** do not claim a proprietary reasoning kernel, cryptographic hash, simple agent wrapper, or policy-to-metric link as a moat. Do not dismiss Snowflake, Databricks, dbt, Collibra/Atlan or internal workflows based only on missing marketing features. Equally, do not declare NO-GO solely because a platform *could* implement the outcome. Investigate **what customers still do manually, how reliably they do it, and whether they would switch or buy**.

**Poetic and analogous startups are inspiration, not evidence.** Their emergence in existing software categories illustrates that end-to-end execution may matter more than a unique underlying primitive. It does *not* validate Sophon's demand, performance, funding prospects or competitive advantage.

## 5. Four different questions and evidence standards

| Stage | Question | What evidence permits us to conclude |
|---|---|---|
| 1. Infrastructure feasibility | Does the actual governance-to-existing-semantic-layer lifecycle work, persist and audit independently? | Reproducible working code, real native semantic execution, correct change/history/integrity tests |
| 2. Reliability and scope | Does the mechanism remain correct across challenging, unseen, authentic changes and known unknowns? | Independent oracles, correct chronology, adversarial controls, measured errors and missing coverage |
| 3. Operational usefulness | Does it solve a real recurring organizational governance problem with tolerable maintenance? | Real usage and observed operational results; not just a compelling demo |
| 4. Adoption / business | Do teams repeatedly choose, rely on and potentially pay for it rather than alternatives? | Actual customer behavior and economics, not customer interviews alone |

**Do not substitute one validation for another.** A failed algorithmic novelty test is not a failure of basic infrastructure feasibility. A working toy integration is not proof of reliability, adoption or commercial viability. Evidence of LLM parity is not proof that organizations need no governance infrastructure; equally, the need for recordkeeping is not proof they need Sophon instead of available tools.

Conventional alternatives (Git/CI, dbt tests, catalogs, policy-as-code, data contracts, lineage and AI agents) are legitimate building blocks **and** potential substitutes. Evaluate the build-vs-buy / integration trade-off honestly at the appropriate stage.

## 5A. Market-entry hypotheses and measurable differentiation

The charter's scope is enterprise governance expressed and tested **through existing semantic layers**. The **first customer segment, governing domain, buyer and specific platform are not yet owner-approved commitments**. Choose them based on validated operational outcomes, not a generic assertion that "trusted AI data" is in demand.

A strong initial wedge is more likely where:

- authoritative business requirements are genuinely maintained **outside** the semantic implementation (e.g. a separately approved commercial or finance policy, contractual schedule or amended regulatory calculation);
- changes recur and impose identifiable material risk, elapsed time or coordination effort;
- the relevant obligation is observably representable and testable through existing semantic definitions, without pretending to verify every operational consequence;
- distinct accountable teams own the authoritative interpretation and the semantic implementation;
- incumbent tools are available but a demonstrable **last-mile workflow problem** remains.

**Candidate, not decision:** commercial/wholesale agreements, partner remuneration, revenue sharing, contractual KPI calculations, or finance-controlled metrics. Telecom is a plausible discovery beachhead given the founder's experience; none is a proven buyer, mandatory vertical or established product-market fit. A policy whose semantic definition is itself the only authoritative source may have little additional value for Sophon; test the actual cross-system boundary.

Before choosing a wedge, observe at least one real **before/after** customer workflow and ask: which amendment arrived, who noticed, how was its impact identified, which changes and approvals happened, what evidence survived, what went wrong, and what do existing tools already do? Obtain customer permission and handle contractual materials appropriately. For technical feasibility, a clearly labelled lab policy remains acceptable; it must not be portrayed as market evidence.

**Measure the result, not the architecture:** elapsed amendment-to-reviewed-change time; time to verified implementation; human review/integration effort; missed material impacts and false alerts; proportion with owner-approved interpretation; coverage accurately reported as unverified/out-of-scope; time and effort to reproduce the audit; cost of operating the full workflow. Measure baseline customer practice and a realistic incumbent/configuration alternative, not a deliberately weak LLM-only control.

**Commercial kill conditions (hypotheses to test):** buyers already achieve the complete outcome at acceptable cost and risk; the valuable obligations cannot be tested through the semantic layer; changes are too rare to justify ongoing infrastructure; approvals/authority cannot be obtained or integrated; or adoption requires replacing too many existing systems. Explicit evidence of these should reduce enthusiasm even if the technical demonstration succeeds.

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
6. **Check the end-to-end outcome:** if claiming product differentiation, compare the actual governed-transition workflow, including approvals, maintenance and evidence retrieval, against the customer's real practice and appropriately configured alternatives. Technical feature-parity is neither automatic success nor automatic failure.

### Anti-drift checklist — stop and surface a conflict if a plan:

- Reframes the core goal as **outperforming an LLM** or inventing a new technical primitive.
- Substitutes direct control of arbitrary downstream applications for governance **through the existing semantic layer**.
- Equates a one-off policy-vs-SQL comparison with persistent traceability and auditability.
- Calls hashes, Git diffs, model-produced text or CI output substantive verification without inspecting their meaning.
- Promotes unapproved interpretations, inferred bindings or missing evidence to authoritative, complete or verified.
- Treats missing customer interviews as a prerequisite for testing technical feasibility, or regards customer interviews alone as business validation.
- Silently changes the product thesis in response to a benchmark outside its scope.
- Reduces the product to a generic AI governance dashboard, policy graph, a one-off LLM comparison or a standalone semantic catalog without an operational transition.
- Assumes a competitive moat because no vendor mentions a feature, or declares the opportunity dead because an incumbent could assemble the same features.
- Treats an impressive startup in an adjacent crowded market (e.g. Poetic) as proof of Sophon's demand.
- Commits the owner to a specific sector, buyer, deployment model, or contract-only domain without evidence and explicit owner approval.

### Change history

- **v1.0 — 11 October 2026:** Owner-defined purpose, integration boundary, four capabilities, infrastructure evidence standard and safeguards against conceptual drift.
- **v1.1 — 12 October 2026 (explicit owner request):** Reframed value around the full governed-change outcome rather than a missing technical feature; clarified existing systems of record, incumbent complement/substitution risk, measurable customer outcomes and candidate initial wedges. Preserves v1.0 architecture and every historical negative result; **does not** claim demand, differentiation or a specific vertical has been validated.

### Authority and changes to this charter

This charter records the **owner's established product decisions**. An assistant may challenge any assumption with concrete evidence, but **must not silently redefine it** or use an experiment to replace it.

A material change to purpose, the semantic-layer boundary, the four capabilities or the success criteria requires an **explicit owner decision** documented in a new dated charter revision/decision record. Experiments may challenge hypotheses; they do not themselves rewrite these decisions. The owner's subsequent explicit instructions take precedence; preserve version history.

If an older README, prompt, report, feature branch or agent instruction conflicts with this file, treat the older text as **historical context** and surface the discrepancy. Do not erase the prior evidence. The charter governs **new work**, but it is not an assertion that the proposed design has been empirically validated.
