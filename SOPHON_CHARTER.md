# SOPHON CHARTER

**Version:** 1.2 — 13 October 2026  
**Status:** Owner-approved clarification of the normative semantic-layer thesis (v1.2). Binding project instructions for assistants and contributors; technical feasibility, operational value, competitive differentiation and commercial prospects remain **unproven** unless demonstrated.

## 1. Mission

**Sophon is a normative semantic layer for organizations.** Just as an enterprise BI semantic layer resolves the meaning of data for human and machine consumers, Sophon makes the meaning of governing documents **shared, versioned, source-grounded, reusable and inspectable** across humans, AI agents, BI and operational workflows.

The source of governing meaning may be a contract, amendment, regulation, approved policy or authoritative decision. Sophon does not create legal authority by interpreting a document. It preserves which source governs, its scope and dates, the interpretation's status, explicit qualifications and unresolved questions. Different customers, contracts, dates or jurisdictions may require **different applicable meanings**; sharing a normative layer does not flatten genuine differences.

**The product is the shared normative layer and its ongoing reconciliation, not any one AI model or agent configuration. The preferred first engineering/product wedge is compliance checking of pre-existing enterprise BI semantic definitions against independently governing contractual commitments.** This intentionally leverages semantic work already performed by data teams in Databricks, Snowflake, dbt or BI tooling instead of rebuilding their definitions. A second, complementary access path exposes the same governing meaning directly to agents and humans who do not use BI. These are two consumption/integration paths for one layer, not two separate products. Legal-workflow automation, standalone clause classification and generalized agent configuration are not product definitions. LLMs and Jev can propose and challenge interpretations; neither their agreement nor a plausible explanation makes a proposal authoritative.

The four inseparable capabilities remain **TRANSPOSE, TRACE, VERIFY and AUDIT**. A model, chat session, prompt, contributor or consumer should be replaceable without losing the organization's recorded governing meaning or evidence history.

**Value and demand remain hypotheses.** Customers may benefit from reliable, repeated transitions from changed governing meaning to the semantics actually used by people and software, with less manual reconciliation and stronger audit evidence. Whether Sophon can provide that outcome reliably, whether organizations need it, and whether they would choose it over configured incumbent tools are **not proven**. A valuable product need not invent a proprietary reasoning primitive; an outcome gap must be measured rather than inferred from absent vendor features or startup analogies.

**Initial operating constraint:** design feasible small slices for a solo founder using existing tools, adapters and a narrow corpus. Do not require a universal legal ontology, a new DSL, every enterprise integration or automated authorization as a prerequisite. Narrow experiments do not narrow the product thesis.

## 2. Canonical architecture and integration boundary

\`\`\`text
 AUTHORITATIVE GOVERNING CONTRACTS / POLICIES
                      |
                      v
      SOPHON — NORMATIVE SEMANTIC LAYER
      Source-backed definitions, conditions,
      exceptions, scope, dates, evidence
                 /                 \
                /                   \
  (A) CONTRACT ↔ BI ALIGNMENT     (B) DIRECT GOVERNING CONTEXT
       Compliance checking             API / retrieval
       and impact analysis                   |
                |                            v
                v                    NON-BI AGENTS / HUMANS
   EXISTING DATA/BI SEMANTIC LAYER     Sales, procurement, support
   Databricks | dbt | Snowflake        and other workflows
   Existing metrics and definitions
                |
                v
   BI DASHBOARDS / DATA-DRIVEN AGENTS
   (where they actually use this layer)
\`\`\`\n\n
The two layers solve **different and complementary disambiguation problems**:
- **BI/data semantic layer:** What do enterprise records, metrics and relationships mean?
- **Sophon/normative semantic layer:** What do the applicable governing documents require, permit, prohibit, define or leave unresolved?
- **Their intersection:** Do the business semantics, calculations or decisions used by a consumer align with the applicable governing meaning?

**BI-first engineering rationale:** The organization's existing semantic layer is already the product of substantive data-team disambiguation. Sophon should inspect and reuse it as-is, mapping governing contract terms to real metrics, dimensions and calculations, comparing intended contractual semantics with compiled/native semantic behavior, exposing discrepancies with source evidence, and proposing reviewed corrections. This **compliance/alignment checker is the initial wedge**; avoid rebuilding existing BI definitions or claiming control over the data stack. Bidirectional checking must cover both contractual amendments and independent semantic-layer revisions.

**Direct-access extension:** Some agents act without relying on BI metrics. They should be able to retrieve Sophon's applicable governing concepts, qualifications and links directly, with appropriate permissions and traceability. This is **not** a requirement to deploy a universal policy engine, build an agent orchestration platform or automatically reconfigure every agent.

**Explicit hypothesis, not a fact:** Data-driven enterprise agents may often draw meaning from existing BI/semantic infrastructure, but this varies across organizations. Many agents use application APIs, direct SQL, RAG and other tools. Verify which agents actually use the semantic layer before claiming coverage, propagation or market opportunity.

**Correction to v1.1:** The existing executable BI semantic layer is the **preferred initial integration and verification surface**, not Sophon's universal integration boundary or the only way to consume normative meaning. Some requirements concern approvals, communications or actions that BI cannot represent. Preserve common source-backed meaning across whichever surfaces are genuinely connected.

**One meaning, two access paths:** register source-backed governing concepts and determinations once. First, link relevant terms to **existing BI semantic objects and native calculations**, providing a compliance finding and actionable impact evidence; BI consumers can continue using the organization's established semantic layer. Second, allow non-BI agents and humans to query the **same scoped, versioned normative records** directly. Additional capability/configuration bindings are optional later integrations, not MVP prerequisites. Every actual binding identifies system, version, customer/scope, responsible owner and verification limits. Never let separately prompted agents silently invent diverging governing meaning.

**System-of-record boundaries:** legal/contractual authorities own source documents and approved interpretations. Data/platform teams own executable BI definitions; application and agent owners own their deployments and runtime controls. Sophon owns the **durable normative representation and cross-system relationships/evidence**, subject to permission and approval. It should not silently replace any source of authority, BI semantic layer, agent runtime, warehouse or operational system.

**Integration discipline:**
- **Prefer a read-only BI compliance check first:** inspect native semantic definitions, identify potential contract/metric mismatch, run native compile/query/data-backed checks where permitted, record contrary evidence and propose—but do not silently deploy—fixes. SQL snippets, fabricated YAML and passing hashes alone do not prove semantic alignment.
- **For direct-access agents, start with a versioned read/query API** that returns applicable source-grounded requirements, qualifications and uncertainty. Only pursue native configuration/guard interfaces when a concrete action-control use case warrants it. A retrieved rule or updated prompt does **not** prove enforcement.
- For human consumers, provide scoped, source-linked meaning and qualifications; do not invent binding legal advice, permissions or approvals.
- Track non-expressible and unobservable requirements as **UNRESOLVED / PARTIALLY_OBSERVABLE / OUT_OF_SCOPE**. Differentiate interpretation, authorized deployment and observed runtime conduct.
- New integrations may be proposed, but must not quietly convert Sophon into a generic legal chatbot, a replacement BI layer, a universal policy gateway or an agent-management product.

**Two-sided maintenance:** governing-source changes trigger impact assessment of linked interpretations and implementations; changes to BI metrics, agent configurations and other linked implementations trigger checks against still-applicable governing meaning. Changes should not be pushed without appropriate authorization.

## 3. The four inseparable capabilities

### TRANSPOSE — governing meaning to consumable semantics

Ingest and version a governing source; identify applicable provisions, definitions, conditions, exceptions and cross-references; propose a **shared structured normative representation** with exact source anchors, dates, authority status, uncertainty and qualification. **First use it to check existing BI semantic definitions against external contractual meaning** and propose scoped corrections without rebuilding the semantic layer. Make that same normative meaning directly queryable by non-BI agents and humans. Optional downstream agent configuration comes later if an actual interface and risk case justify it.

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

**Initial proof: contract-to-existing-BI-semantic-layer checker, not a universal agent platform.** A feasible solo-founder vertical slice is:

1. Register **one** real authorized-for-use governing contract/policy (or openly labelled LAB_AUTHORED terms) with exact text, source, scope, known-at and effective dates.
2. Produce a source-anchored normative interpretation of **one substantive contractual business definition** with conditions/exceptions, authority status and explicit uncertainty.
3. Read **one real, pre-existing executable BI semantic definition** via its native interface (e.g. dbt/MetricFlow or Databricks/Snowflake-native equivalent). Do not fabricate the metric to match the contract.
4. Check semantic correspondence and **actual native behavior or data** where accessible. Show a material mismatch and a no-op/aligned control, with independent evidence. Report **PASS_FOR_DEFINED_CHECKS / MISMATCH / UNRESOLVED / UNOBSERVABLE** rather than universal compliance.
5. Introduce one contractual amendment **and** one independently introduced semantic-definition change; reassess only impacted relationships, propose (not silently deploy) necessary corrections, and preserve the old versions.
6. Expose the **same scoped normative meaning** through one minimal read-only API/query for a non-BI agent or human, confirming that access is not mediated by the BI layer. This tests accessibility, not agent action enforcement.
7. Restart the interpreter/model process; reconstruct as-of contractual applicability, mappings, raw proposals, checks, failures, approval status and evidence without relying on the model's retrospective explanation.

**Stage 1 success (§5):** a native existing BI semantic object can be compared with a distinct governing source, change impact is traceable and reproducible in both directions, and the governing context is independently retrievable directly. **Not proven:** legal correctness beyond independent scored checks, generalized autonomous contractual transposition, that most agents rely on BI, real-world runtime agent compliance, or buyer demand.

**Solo-founder limit:** one contract, one real BI metric, one simple direct query and one amendment. Reuse existing semantic tools, Git, SQLite and typed JSON. Do not require arbitrary agent adapters, a proprietary DSL or a large legal/agent workflow system. If access to a native semantic runtime is unavailable, log a blocker rather than claiming success with SQL-only substitutes.

## 4A. Product logic: the customer's outcome gap, not a feature gap

**Atomic unit of product value: a governed change assessed against existing BI meaning, with source-to-semantic evidence and direct governing context available to non-BI consumers.** A governing source, approved interpretation or linked implementation changes. Sophon maintains a shared normative meaning, identifies impacted bindings and records an accountable disposition:

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

**The product scope is a normative semantic layer for governing documents, with an explicit BI-first compliance-checking entry point and a direct-access path for non-BI agents.** The initial customer size, vertical, source of authority and buyer are not established. The early technical integration focus on an existing BI semantic layer is **intentional**, because that organization may already have done the difficult data-semantic work. A solo founder signing contractual commitments and configuring agents remains a useful **product-design scenario**, not a proven customer segment or a mandate to build only for startups.

The primary wedge hypothesis is a **contractual KPI or commercial definition conflicting with an already-maintained BI semantic metric**. Contract and semantic revisions should trigger independent, documented reassessment. Potential initial clauses include:
- customer SLAs and service-credit definitions shared by BI, support and billing;
- commercial terms, remuneration or contractual KPI calculations that intersect an existing BI semantic layer;
- requirements that cannot be represented as BI metrics but can be served through Sophon's scoped direct governing-context API (a complementary extension, not an initial generalized enforcement product).

Telecom is a plausible discovery area given founder experience, **not** a product boundary. An entirely internal metric definition already maintained correctly in one system may provide little normative-layer value. Conversely, an obligation that cannot be tested through BI may still be in scope if another genuine, verifiable consumer binding exists.

For engineering feasibility, clearly labelled lab terms are acceptable; never present self-authored fixtures as independent legal or customer evidence. For operational usefulness and business value, obtain permission to examine real before/after workflows: how a document change arrived, which interpretations diverged, who updated which consumers, whether the change took effect, what errors remained and which evidence survived.

**Measure the BI-first outcome:** time and human effort to map a contractual definition onto existing semantic objects, discover substantive mismatches, distinguish harmless changes, propose fixes and reproduce the audit; track missed conditions, false positives, coverage and abstention. Separately measure direct governing-context API usefulness to agents outside the BI stack, and verify rather than assume actual data-agent reliance on BI. Compare against the customer's real process and credible native-tool setups rather than an intentionally weak chat-only baseline.

**Commercial failure conditions:** the supposed gap is already solved adequately; meaningful requirements cannot be bound reliably in the proposed initial integrations; heterogeneity is too low to justify a shared layer; the semantic source is not authoritative or interpretable in context; integration, approval or maintenance costs exceed observed gains; or buyers do not adopt it. These are hypotheses to investigate, not a predetermined NO-GO.

## 6. Prior results: preserve boundaries of inference

- **21 September 2026 authority/control-plane audit:** bespoke authorization/authority logic showed parity with disciplined policy-as-code in the tested setting. Do not resurrect the extra control plane without a different, evidenced need. See `docs/REPORT.md` and `docs/DECISION.md`. Those reports describe an **earlier iteration** of the project; they do not override this charter.
- **28 September 2026 dbt/DuckDB viability (PR #2, `codex/alignment-review-agent`):** existing data-team definitions could be inspected and governed checks executed; some real public-data discrepancies were identified. Legal-policy matching, autonomous accuracy, native BI semantic-layer execution and enterprise reliability were **not proven**.
- **11 October 2026 governance-integrity test (PR #3, `experiment/governance-integrity-2026-10-11`):** `STOP_KERNEL` **for a specialized persistent-link store claimed as a performance/accuracy differentiator over Claude Code with conventional notes/tools in a Publicodes law-to-rule benchmark**. That store worked as infrastructure but did not change the scored primary answers and had higher token/time cost. The experiment used **Publicodes, not an enterprise BI semantic layer**. A preregistered nonchronological task order exposed future 2026 texts to earlier maintenance tasks; post-hoc scorer/reference corrections were recorded. Its findings do **not** constitute a verdict that persistence, governance infrastructure or Sophon's intended architecture is unnecessary.

Historical reports, decision files and rejected hypotheses must remain accessible, even when they conflict with the current direction.

## 7. How assistants and contributors must prevent conceptual drift

**Mandatory invariant before substantial advice, design, code or Claude Code prompts:**

> Sophon is a **shared normative semantic layer for governing documents**. **Its initial engineering wedge is to leverage and check existing BI/data semantic definitions against authoritative contracts**, rather than rebuilding data-team semantics. Data-driven agents/humans may use BI; non-BI agents/humans can retrieve the same governing context directly. Preserve **TRANSPOSE / TRACE / VERIFY / AUDIT**, source authority, scope, chronology, uncertainty and reconstructable evidence. Verify actual BI consumption rather than assuming it.

**Required task-entry check:**
1. State the governing-source input, the proposed shared normative artifact, the real consumer/interface under test and the relevant validation stage (§5). If the task isolates one component, label it upstream or partial.
2. Name the smallest falsifiable uncertainty, authentic vs lab provenance, the current baseline, and the success/failure/inconclusive criteria. For claims about BI, name the **native semantic runtime and data**; for agent claims, name the real configuration/enforcement boundary.
3. Show how evidence and versioned links would survive the model/chat session, and what an independent reviewer can check. Use independent correctness oracles when scoring interpretations; keep formatting validity, semantic accuracy, safety holds and actual deployment separate.
4. Preserve first-run outputs, contrary historical results, costs and correction histories. Enforce monotonic knowledge-time chronology across persistent state and do not leak future evidence into earlier decisions.
5. Conclude **OBSERVED / INFERRED / ASSUMED**, limited to the stage and integrated surfaces actually tested; don't generalize a negative Jev, Publicodes, MetricFlow or agent-adapter experiment to the entire product.
6. For differentiation claims, measure the **full governed-change outcome** against realistic internal or incumbent solutions, not a one-off LLM answer.

**Anti-drift stops — explicitly surface a conflict if a plan:**
- Redefines Sophon as merely an LLM/contract classifier, autonomous lawyer, agent configuration tool, passive audit graph or replacement data semantic layer. **A BI compliance checker is an intentional first wedge, but not the full normative-layer mission.**
- Fails to prioritize reuse of **existing BI semantic definitions** for the initial checker, treats BI as mandatory for every governing provision, or assumes most agents use BI without inspecting actual data flows.
- Lets every agent independently reinterpret the governing corpus instead of reusing one scoped, versioned meaning; or assumes updating prompts guarantees agent behavior.
- Focuses only on Jev versus LLM accuracy, reviewer abstention or syntactic validity while forgetting persistent meaning, cross-consumer use, traceability and verification.
- Conflates model-generated interpretation with authorized meaning, a semantic patch with deployment, a passed test with legal correctness, or a configured agent with observed compliance.
- Adds direct application-level enforcement, a proprietary DSL, broad integrations or a legal-operations platform as default architecture without evidence and a scoped design decision.
- Rewrites product direction because of a narrow experimental result or an appealing startup analogy; erases contrary evidence; assumes an incumbent's theoretical capability alone settles customer demand.
- Converts a **BI-first technical wedge** into a permanent BI-only product boundary, or selects enterprise-only, startup-only, telecom-only or a single platform as a proven commercial segment.

### Change history

- **v1.0 — 11 October 2026:** Owner-defined governance purpose, semantic-layer integration boundary, four capabilities and evidence safeguards.
- **v1.1 — 12 October 2026 (owner request):** Governed-change outcome, systems-of-record discipline, alternatives and measurable customer value. BI remained the mandatory integration boundary.
- **v1.2 — 13 October 2026 (owner clarifications, revised while PR #15 remained draft):** Sophon is the **normative semantic layer**, with an intentional **BI-first contract/metric compliance-checking wedge** that reuses data-team semantics, plus a **direct source-backed query path** for non-data agents. BI is preferred for the first integration, not a required intermediary for every governing requirement. The assumption that most organizational agents use BI is unverified and must be tested. Solo-founder feasibility, history and four capabilities retained.

### Authority and changes to this charter

This charter records the **owner's established product decisions**. An assistant may challenge any assumption with concrete evidence, but **must not silently redefine it** or use an experiment to replace it.

A material change to purpose, the semantic-layer boundary, the four capabilities or the success criteria requires an **explicit owner decision** documented in a new dated charter revision/decision record. Experiments may challenge hypotheses; they do not themselves rewrite these decisions. The owner's subsequent explicit instructions take precedence; preserve version history.

If an older README, prompt, report, feature branch or agent instruction conflicts with this file, treat the older text as **historical context** and surface the discrepancy. Do not erase the prior evidence. The charter governs **new work**, but it is not an assertion that the proposed design has been empirically validated.
