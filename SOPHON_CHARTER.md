# SOPHON CHARTER

**Version:** 1.2 — 13 October 2026  
**Status:** Owner-approved clarification of the normative semantic-layer thesis (v1.2). Binding project instructions for assistants and contributors; technical feasibility, operational value, competitive differentiation and commercial prospects remain **unproven** unless demonstrated.

## 1. Mission

**Sophon is a normative semantic layer for organizations.** Just as an enterprise BI semantic layer resolves the meaning of data for human and machine consumers, Sophon makes the meaning of governing documents **shared, versioned, source-grounded, reusable and inspectable** across humans, AI agents, BI and operational workflows.

The source of governing meaning may be a contract, amendment, regulation, approved policy or authoritative decision. Sophon does not create legal authority by interpreting a document. It preserves which source governs, its scope and dates, the interpretation's status, explicit qualifications and unresolved questions. Different customers, contracts, dates or jurisdictions may require **different applicable meanings**; sharing a normative layer does not flatten genuine differences.

**The product is the shared layer and its ongoing reconciliation, not any one consumer or reasoning technique.** Agent configuration, legal-workflow assistance, clause classification, and BI metric checking are possible activities at its edges, not alternative definitions of Sophon. LLMs and Jev can propose and challenge interpretations; neither their agreement nor a plausible explanation makes a proposal authoritative.

The four inseparable capabilities remain **TRANSPOSE, TRACE, VERIFY and AUDIT**. A model, chat session, prompt, contributor or consumer should be replaceable without losing the organization's recorded governing meaning or evidence history.

**Value and demand remain hypotheses.** Customers may benefit from reliable, repeated transitions from changed governing meaning to the semantics actually used by people and software, with less manual reconciliation and stronger audit evidence. Whether Sophon can provide that outcome reliably, whether organizations need it, and whether they would choose it over configured incumbent tools are **not proven**. A valuable product need not invent a proprietary reasoning primitive; an outcome gap must be measured rather than inferred from absent vendor features or startup analogies.

**Initial operating constraint:** design feasible small slices for a solo founder using existing tools, adapters and a narrow corpus. Do not require a universal legal ontology, a new DSL, every enterprise integration or automated authorization as a prerequisite. Narrow experiments do not narrow the product thesis.

## 2. Canonical architecture and integration boundary

```text
 AUTHORITATIVE GOVERNING CORPUS                 ENTERPRISE DATA & SYSTEMS
 Contracts | policies | amendments              Operational sources | warehouses
 Regulations | decisions | interpretations                 |
                  |                                          v
                  v                              EXISTING BI SEMANTIC LAYER
        SOPHON: NORMATIVE SEMANTIC LAYER         Metrics | dimensions | data meaning
 Governing concepts | definitions | conditions              |
 Exceptions | applicability | dates | evidence              |
                  |                                          |
                  +<------ scoped, versioned links -------->+
                  |                                          |
                  +-------------------+----------------------+
                                      v
                      HUMAN AND MACHINE CONSUMERS
                 BI/reporting | AI agents | applications
                  Operational workflows | human decisions
```

The two layers solve **different and complementary disambiguation problems**:
- **BI/data semantic layer:** What do enterprise records, metrics and relationships mean?
- **Sophon/normative semantic layer:** What do the applicable governing documents require, permit, prohibit, define or leave unresolved?
- **Their intersection:** Do the business semantics, calculations or decisions used by a consumer align with the applicable governing meaning?

**Important correction to v1.1:** An existing executable BI semantic layer is a **first-class integration and verification surface**, not Sophon's universal integration boundary, prerequisite or sole destination. Some provisions govern metrics; others govern agent actions, approvals, communications, deadlines, data handling or human workflows. Preserve the same shared normative meaning across those surfaces while making no claim that all can be expressed in BI semantics.

**One meaning, multiple scoped bindings:** register source-backed governing concepts and determinations once, then link them to relevant existing semantic objects, agent capability declarations, instructions, policies, workflow settings and human-facing views. Each binding must identify its actual system, version, scope, authorized owner and verification limits. Do not create disconnected ad hoc interpretations separately for each agent. A customer-specific term or a later amendment may legitimately produce a distinct scoped version.

**System-of-record boundaries:** legal/contractual authorities own source documents and approved interpretations. Data/platform teams own executable BI definitions; application and agent owners own their deployments and runtime controls. Sophon owns the **durable normative representation and cross-system relationships/evidence**, subject to permission and approval. It should not silently replace any source of authority, BI semantic layer, agent runtime, warehouse or operational system.

**Integration discipline:**
- Prefer native semantic APIs and compiled/executed behavior for BI claims (e.g. dbt/MetricFlow, Snowflake or Databricks equivalents). SQL snippets, fabricated YAML and passing hashes alone do not prove semantic alignment.
- Prefer native, explicitly permitted configuration/guard interfaces for agents and applications. Updating a prompt does **not** prove enforcement, and detecting a governing rule does not prove it can be configured automatically.
- For human consumers, provide scoped, source-linked meaning and qualifications; do not invent binding legal advice, permissions or approvals.
- Track non-expressible and unobservable requirements as **UNRESOLVED / PARTIALLY_OBSERVABLE / OUT_OF_SCOPE**. Differentiate interpretation, authorized deployment and observed runtime conduct.
- New integrations may be proposed, but must not quietly convert Sophon into a generic legal chatbot, a replacement BI layer, a universal policy gateway or an agent-management product.

**Two-sided maintenance:** governing-source changes trigger impact assessment of linked interpretations and implementations; changes to BI metrics, agent configurations and other linked implementations trigger checks against still-applicable governing meaning. Changes should not be pushed without appropriate authorization.

## 3. The four inseparable capabilities

### TRANSPOSE — governing meaning to consumable semantics

Ingest and version a governing source; identify applicable provisions, definitions, conditions, exceptions and cross-references; propose a **shared structured normative representation** with exact source anchors, dates, authority status, uncertainty and qualification. Discover affected downstream consumers and propose **scoped bindings or native configuration changes**. Where the consumer is BI, bind to pre-existing semantic objects and test their meaning. Where it is an agent or workflow, bind to its actual capabilities and controls.

The interpretation and mapping may be AI-proposed. **Proposal is not legal approval, deployment or demonstrated compliance.** A source may be insufficient to produce safe executable instructions; hold the unresolved part and preserve everything known.

### TRACE — durable source-to-consumer relationships

Keep persistent, versioned and inspectable connections between:
1. exact governing provision, document revision, authority and provenance;
2. known-at/publication dates and effective/applicability dates, including supersession;
3. structured normative meaning, accepted interpretations, conflicting claims and open questions;
4. impacted BI semantic identities, agent capabilities, workflow settings and human-facing representations **where actually mapped**;
5. proposed, approved and implemented revisions, relevant data/decisions, tests and downstream consumption **where actually observable**.

A predicted mapping is not a verified binding. Preserve historical versions, selective impact analysis and unaffected consumers, without demanding that every consumer be integrated.

### VERIFY — independently challenge alignment in both directions

- **Governance → implementations:** changes to a contract, policy or authoritative decision trigger impact analysis and revalidation of affected bindings, logic and configurations.
- **Implementations → governance:** independent changes in a BI semantic definition, agent setting or operational workflow trigger reassessment against the still-applicable approved meaning.
- For BI, inspect actual native query/compile behavior and underlying data when possible. For agents, distinguish configuration tests, action-gate tests and observed behavior; do not imply one from another. For human-facing outputs, verify cited source/version and explicit qualifications rather than pretending to enforce human conduct.
- Separate semantic errors, omitted exceptions, wrong binding, missing facts, harmless changes, data noncompliance, unsupported coverage and uncertain legal interpretation. Use independent oracles and counterexamples where correctness is claimed.
- A model's explanation, another model's assent, a content hash or green CI is **not** independent substantive verification.

### AUDIT — reconstructable process and history

An independent reviewer must be able to reconstruct the governing document and version, the applicable scope and knowledge-time, what interpretation was proposed or approved, what each model actually output, which consumers were linked, what was deployed, what tests/observations ran and what remained unknown—**without trusting an LLM's retrospective explanation or the original chat session**.

Preserve original evidence or independently retrievable immutable references, prompts/model versions and raw outcomes when relevant, deterministic reconciliation rules, authorized approvals, execution receipts, counterexamples and missing evidence. Integrity evidence is not correctness evidence.

Keep the states distinct: **PROPOSED; APPROVED_BY_AUTHORITY; CONFIGURED/DEPLOYED; LINKED/TRACEABLE; VERIFIED_FOR_SPECIFIED_CHECKS; UNVERIFIED/UNKNOWN**. Do not turn a held decision into a false claim of compliance.

## 4. Smallest meaningful working product

The first build should prove a **shared normative meaning can be reused and maintained**, not that a large legal/agent/BI platform can be built. A feasible solo-founder vertical slice is:

1. Register **one** authentic, authorized-for-use governing document, or explicitly labelled LAB_AUTHORED agreement, with exact source, known-at and effective dates and bounded applicability.
2. Derive a source-anchored, explicitly provisional or approved normative representation. No assumption that every clause has an executable translation.
3. Connect one relevant governing concept to **two different pre-existing consumers**, ideally one real executable BI semantic definition and one small agent or workflow with an actual configuration boundary. A human-facing source-linked view may inspect the same record.
4. Show that an amendment produces **one shared versioned normative change**, selective impact analysis and proposed consumer changes—without independently prompting each consumer to reinterpret the original contract.
5. Apply only authorized changes through the consumers' real interfaces. Verify the actual semantics or controls in each integrated surface and state what cannot be observed.
6. Change one consumer-side implementation, including a harmless/no-op control, and demonstrate reverse checking against the still-applicable governing meaning.
7. Restart the process and reconstruct the prior as-of state, proposals, approvals, changes, evidence and unresolved items; catch tampering, missing authority and future-information leakage.

**Success at Stage 1 (§5):** two different consumers demonstrably use the same correctly scoped, recorded governing interpretation; source or consumer changes produce appropriately bounded reassessment and reproducible evidence. It is **not** proof that the interpretation is legally correct, that autonomous transposition works for unfamiliar clauses, or that the product has buyer demand.

**Scope and cost:** one document, one material amendment and two deliberately simple adapters are enough. Reuse Git, SQLite, JSON Schema and existing BI/agent infrastructure; no proprietary DSL, generalized legal workflow engine or large multi-agent architecture is required. If a real interface is unavailable, record a prerequisite or blocker instead of quietly replacing it with a fabricated stand-in. A focused Jev/LLM clause pilot can test an upstream component but cannot pass this end-to-end bar.

## 4A. Product logic: the customer's outcome gap, not a feature gap

**Atomic unit of product value: one governed change propagated to relevant consumers with evidence.** A governing source, approved interpretation or linked implementation changes. Sophon maintains a shared normative meaning, identifies impacted bindings and records an accountable disposition:

1. **Intake and applicability:** source authority, revisions, publication/observation time, effective time, contract/customer/jurisdiction scope and conflicts.
2. **Interpretation:** source-grounded structured meaning, missing facts, exceptions and review/approval status; disagreements are recorded, not averaged into certainty.
3. **Impact:** trace which BI definitions, agent capabilities, workflows or human-facing views depend on the affected meaning; mark unlinked or unobservable consumers honestly.
4. **Change:** propose native adjustments for impacted integrations; record who accepted/rejected them; execute only within explicit existing permissions.
5. **Verification:** independently inspect bounded behavior or semantics on each connected surface; retain counterexamples and limits, without claiming to control unintegrated systems.
6. **Closure and history:** persist deployed/blocked/unchanged outcomes, accountable owner, verified checks, unresolved issues and reconstructable as-of evidence.

**A correctly unresolved transition is not compliance certification.** An LLM proposal does not imply legal authority. A BI test does not demonstrate agent conduct, and a configured agent does not prove it followed its instructions. A traceable but incorrect interpretation remains incorrect.

**Hypothesized buyer outcome:** fewer manual reinterpretations across consumers, faster and less error-prone contractual/policy changes, lower coordination effort, less semantic drift and cheaper independent audit. Demonstrate it against a **competent alternative**: configured BI semantic governance, existing catalogs/lineage, Git/CI, legal operations, agent policy infrastructure and LLM tools. An LLM-only answer is not an adequate competitor for the end-to-end system, and documentation alone is not a complete product.

**No presumed moat:** hashing, a policy graph, Jev classification or model agreement are not differentiators by themselves. Native products might already solve much of the work; an integrated outcome gap is a **testable hypothesis**. Poetic and analogous startups are inspiration, not customer evidence.

## 5. Four different questions and evidence standards

| Stage | Question | What evidence permits us to conclude |
|---|---|---|
| 1. Infrastructure feasibility | Can shared governing meaning be created, consumed by two different real surfaces, changed and independently reconstructed? | Reproducible native integrations, scoped shared meaning, real BI/agent checks as applicable, correct change/history/integrity tests |
| 2. Reliability and scope | Does the mechanism remain correct across challenging, unseen, authentic changes and known unknowns? | Independent oracles, correct chronology, adversarial controls, measured errors and missing coverage |
| 3. Operational usefulness | Does it solve a real recurring organizational governance problem with tolerable maintenance? | Real usage and observed operational results; not just a compelling demo |
| 4. Adoption / business | Do teams repeatedly choose, rely on and potentially pay for it rather than alternatives? | Actual customer behavior and economics, not customer interviews alone |

**Do not substitute one validation for another.** A failed algorithmic novelty test is not a failure of basic infrastructure feasibility. A working toy integration is not proof of reliability, adoption or commercial viability. Evidence of LLM parity is not proof that organizations need no governance infrastructure; equally, the need for recordkeeping is not proof they need Sophon instead of available tools.

Conventional alternatives (Git/CI, dbt tests, catalogs, policy-as-code, data contracts, lineage and AI agents) are legitimate building blocks **and** potential substitutes. Evaluate the build-vs-buy / integration trade-off honestly at the appropriate stage.

## 5A. Market-entry hypotheses and measurable differentiation

**The product scope is a normative semantic layer for governing documents and its connections to BI, humans, agents and operational systems.** The initial customer size, vertical, authority source, buyer and consumer pair are not preselected. A solo founder signing contractual commitments and configuring AI-native operations is a useful **product-design scenario**, not evidence of validated demand or a mandate to build only for startups.

Good first wedges likely have independently authoritative documents, changing requirements, multiple consumers that would otherwise interpret requirements differently, and a real configuration/verification boundary. Consider:
- customer SLAs and service-credit definitions shared by BI, support and billing;
- commercial terms, remuneration or contractual KPI calculations that intersect an existing BI semantic layer;
- approved operating policies that govern agent capabilities and human approval workflows.

Telecom is a plausible discovery area given founder experience, **not** a product boundary. An entirely internal metric definition already maintained correctly in one system may provide little normative-layer value. Conversely, an obligation that cannot be tested through BI may still be in scope if another genuine, verifiable consumer binding exists.

For engineering feasibility, clearly labelled lab terms are acceptable; never present self-authored fixtures as independent legal or customer evidence. For operational usefulness and business value, obtain permission to examine real before/after workflows: how a document change arrived, which interpretations diverged, who updated which consumers, whether the change took effect, what errors remained and which evidence survived.

**Measure the change outcome:** time and human effort to identify affected consumers, configure them and verify the result; missed conditions, wrong impacts and false positives; coverage and abstention; divergence among agents/humans/BI; reproducibility of audit; recurring cost per governed change. Compare against the customer's real process and credible native-tool setups rather than an intentionally weak chat-only baseline.

**Commercial failure conditions:** the supposed gap is already solved adequately; meaningful requirements cannot be bound reliably in the proposed initial integrations; heterogeneity is too low to justify a shared layer; the semantic source is not authoritative or interpretable in context; integration, approval or maintenance costs exceed observed gains; or buyers do not adopt it. These are hypotheses to investigate, not a predetermined NO-GO.

## 6. Prior results: preserve boundaries of inference

- **21 September 2026 authority/control-plane audit:** bespoke authorization/authority logic showed parity with disciplined policy-as-code in the tested setting. Do not resurrect the extra control plane without a different, evidenced need. See `docs/REPORT.md` and `docs/DECISION.md`. Those reports describe an **earlier iteration** of the project; they do not override this charter.
- **28 September 2026 dbt/DuckDB viability (PR #2, `codex/alignment-review-agent`):** existing data-team definitions could be inspected and governed checks executed; some real public-data discrepancies were identified. Legal-policy matching, autonomous accuracy, native BI semantic-layer execution and enterprise reliability were **not proven**.
- **11 October 2026 governance-integrity test (PR #3, `experiment/governance-integrity-2026-10-11`):** `STOP_KERNEL` **for a specialized persistent-link store claimed as a performance/accuracy differentiator over Claude Code with conventional notes/tools in a Publicodes law-to-rule benchmark**. That store worked as infrastructure but did not change the scored primary answers and had higher token/time cost. The experiment used **Publicodes, not an enterprise BI semantic layer**. A preregistered nonchronological task order exposed future 2026 texts to earlier maintenance tasks; post-hoc scorer/reference corrections were recorded. Its findings do **not** constitute a verdict that persistence, governance infrastructure or Sophon's intended architecture is unnecessary.

Historical reports, decision files and rejected hypotheses must remain accessible, even when they conflict with the current direction.

## 7. How assistants and contributors must prevent conceptual drift

**Mandatory invariant before substantial advice, design, code or Claude Code prompts:**

> Sophon is a **shared normative semantic layer for governing documents**. It is analogous and complementary to the existing **BI semantic layer for enterprise data**. It serves **humans and AI agents**, can connect to BI and other real implementation boundaries, and must preserve **TRANSPOSE / TRACE / VERIFY / AUDIT** with explicit authority, scope, chronology, uncertainty and evidence.

**Required task-entry check:**
1. State the governing-source input, the proposed shared normative artifact, the real consumer/interface under test and the relevant validation stage (§5). If the task isolates one component, label it upstream or partial.
2. Name the smallest falsifiable uncertainty, authentic vs lab provenance, the current baseline, and the success/failure/inconclusive criteria. For claims about BI, name the **native semantic runtime and data**; for agent claims, name the real configuration/enforcement boundary.
3. Show how evidence and versioned links would survive the model/chat session, and what an independent reviewer can check. Use independent correctness oracles when scoring interpretations; keep formatting validity, semantic accuracy, safety holds and actual deployment separate.
4. Preserve first-run outputs, contrary historical results, costs and correction histories. Enforce monotonic knowledge-time chronology across persistent state and do not leak future evidence into earlier decisions.
5. Conclude **OBSERVED / INFERRED / ASSUMED**, limited to the stage and integrated surfaces actually tested; don't generalize a negative Jev, Publicodes, MetricFlow or agent-adapter experiment to the entire product.
6. For differentiation claims, measure the **full governed-change outcome** against realistic internal or incumbent solutions, not a one-off LLM answer.

**Anti-drift stops — explicitly surface a conflict if a plan:**
- Redefines Sophon as merely an LLM/contract classifier, autonomous lawyer, legal workflow engine, agent configuration tool, BI compliance checker, policy graph or new data semantic layer.
- Treats the existing BI semantic layer as **mandatory for every governing requirement**, or treats it as irrelevant. It is first-class and complementary, not the universal destination.
- Lets every agent independently reinterpret the governing corpus instead of reusing one scoped, versioned meaning; or assumes updating prompts guarantees agent behavior.
- Focuses only on Jev versus LLM accuracy, reviewer abstention or syntactic validity while forgetting persistent meaning, cross-consumer use, traceability and verification.
- Conflates model-generated interpretation with authorized meaning, a semantic patch with deployment, a passed test with legal correctness, or a configured agent with observed compliance.
- Adds direct application-level enforcement, a proprietary DSL, broad integrations or a legal-operations platform as default architecture without evidence and a scoped design decision.
- Rewrites product direction because of a narrow experimental result or an appealing startup analogy; erases contrary evidence; assumes an incumbent's theoretical capability alone settles customer demand.
- Selects a contract-only, enterprise-only, startup-only, telecom-only or specific platform wedge as the product thesis without explicit owner approval.

### Change history

- **v1.0 — 11 October 2026:** Owner-defined governance purpose, semantic-layer integration boundary, four capabilities and evidence safeguards.
- **v1.1 — 12 October 2026 (owner request):** Governed-change outcome, systems-of-record discipline, alternatives and measurable customer value. BI remained the mandatory integration boundary.
- **v1.2 — 13 October 2026 (explicit owner clarification in conversation):** Corrects v1.1's BI-only boundary: **Sophon itself is the normative semantic layer**, complementary to the enterprise data/BI semantic layer and reusable by humans and agents. BI remains a first-class native integration, not a mandatory intermediary. Adds cross-consumer versioned meaning and solo-founder-sized experiment requirements. Preserves earlier experiment evidence without retroactively changing it.

### Authority and changes to this charter

This charter records the **owner's established product decisions**. An assistant may challenge any assumption with concrete evidence, but **must not silently redefine it** or use an experiment to replace it.

A material change to purpose, the semantic-layer boundary, the four capabilities or the success criteria requires an **explicit owner decision** documented in a new dated charter revision/decision record. Experiments may challenge hypotheses; they do not themselves rewrite these decisions. The owner's subsequent explicit instructions take precedence; preserve version history.

If an older README, prompt, report, feature branch or agent instruction conflicts with this file, treat the older text as **historical context** and surface the discrepancy. Do not erase the prior evidence. The charter governs **new work**, but it is not an assertion that the proposed design has been empirically validated.
