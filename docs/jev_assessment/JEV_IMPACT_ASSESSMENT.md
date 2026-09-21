# Jev and Sophon: does a System One model change the conclusion?

21 September 2026. Written against the repository at `main` (`c8359ea`) and the public record on TypeSafe's Jev six days after its launch. Sophon facts below come from `docs/REPORT.md`, `docs/DECISION.md`, `lab/`, `results/` and `evidence/`. Jev facts carry a tag on first use: [V] TypeSafe's own claim, [I] independently measured by a third party, [S] second-hand summary of a page that could not be fetched, [U] unverified community listing. The evidence base is in the appendices beside this file.

Method: five independent analyses (problems A to D and the moat), each attacked by two adversarial refuters; three architecture designs under different lenses; prosecution, defence and judge for each strategic hypothesis; an experiment design with two hostile reviews; and a 17-agent verified sweep of the Jev record. Where a refuter overturned a claim, the claim is not carried here.

---

## 1. Executive conclusion

**Different, not more viable. Jev changes one narrow place and leaves the conclusion where the investigation put it. It removes the last argument that any AI component of Sophon could be differentiating, and it puts a price on the one open technical question without answering it.**

The standing decision stands: do not build the control plane; buy Cedar or OPA behind a gateway; if anything is built, build the thin ledger of typed dated grants and the escalation-to-settlement workflow; and commit to nothing until a real workflow shows escalation classes recur and the policy owner settles them prospectively.

Why Jev cannot move that decision:

- The decision was reached without any model in the built path. The semantic compiler was rejected on the packet's own audit. The kernel was shown equivalent to a disciplined policy-as-code baseline on all 138,240 compared decisions. Approach E was chosen over B for a workflow reason, not a technical one. Jev is a model. It cannot lower a component already priced at zero.
- The existential question is economic. It is whether settlements recur and whether owners settle prospectively. The recurrence tables lean against, and the 113-person Yan study found people chose "ask me" for 114 of 140 rules. Jev supplies no evidence on either.
- Where Jev is relevant, the fact layer, the measured record points the wrong way for autonomy. Jev answers from priors when the state lacks the information, does not abstain unless handed an explicit option, is steerable by text in the state, is not deterministic on borderline items, and returns no rationale or span. Under convention 7 a model reading cannot raise a fact above the provenance of its source.

One amendment follows. Convention 7, facts carry provenance and grants say what provenance they need, is currently a sentence in `DECISION.md` that the lab does not exercise. Every surviving branch of the recommendation needs it as code: the settlement loop, the decision-log wedge, and any use of a model to read facts. It should be the first deliverable, ahead of the ledger.

The owner's seven questions, answered directly:

1. Solves a problem that looked fundamental: no. It touches problem B and leaves it open.
2. Invalidates an architectural decision: no. Two additions, not reversals: REQUEST_FACT gains a sub-reason, and three act kinds are added to the ledger (declare predicate, bind evaluator, adopt calibration). Any evaluator in the slot would require them.
3. Makes components commodity: yes, the predicate evaluator, which was never going to be built anyway.
4. Enables a simpler architecture: no. The simplest safe architecture was already approach E, and Jev adds a slot that may be empty.
5. Weakens the opportunity: negligibly. Cheaper typed judgment lowers the cost of the ask-and-audit alternatives that E must beat, by 1.4 to 1.7 times a per-decision cost that was already near zero [I].
6. Strengthens it with a better primitive: no. Cheaper, yes; more trustworthy where Sophon needs trust, no.
7. Changes the moat: it removes candidates rather than adding one. See section 5.

---

## 2. What Jev actually changes

"Before Jev" states what the investigation concluded on 21 September, not the original Sophon thesis.

| Sophon problem or component | Before Jev | With Jev | Material impact? |
|---|---|---|---|
| **A. Authoritative text to executable semantics** | Rejected. Approach A failed the packet's own real-corpus audits: about 77% self-audited recall on one rulebook and about 71% for a forward-construction plus coverage-search pipeline, neither reproduced, with open standards falsely determinized and inherited scope lost. A4 is false: policy text states conditions and prohibitions, not sufficiency, so autonomy comes from explicit grants. An AI interpretation is PROPOSED, never AUTHORITATIVE. | Unchanged. Jev generates no propositions, quotes no span, cannot chain, and answers at chance with mean confidence 0.74 [I] when the deciding rule is absent from its state. At most an additive recall flagger at ingest that may add a candidate clause to a human queue and never remove one. That role is worth little because the recommendation already hand-ratifies grants rather than compiling text. | **No.** Slightly reinforces the rejection. |
| A sub-items: implicit conditions, exceptions, priority, scope, effective dates, ambiguity, missing rules, organisational interpretation, approval power | Handled by ledger acts and conventions 1 to 3 and 5, or by a person. Davies weighed a later rule on an earlier claim; Pound and McDonagh treated past practice oppositely in one year. | Same. Asking Jev any of these manufactures a determinate number for a question the text does not settle. | **No.** Dangerous if attempted. |
| **B. Fuzzy factual predicates** (assumption A6, criterion S5, open question 3) | Open, and named the weakest point of every deterministic design. The lab pre-digests the judgment into a clean column: `transport_alternative_available` has no clause (R12) and is blank in 36 of 48 cases. Convention 7 unexercised. | A cheap zero-shot proposer of a fact the system may not trust. Ties Claude Haiku 4.5 after decomposition (95.0% vs 93.2%, McNemar p = 0.063) [I], loses to it holistic (62.6% vs 81.3%) [I], is beaten by a 4B model fine-tuned on 1,000 labels (97.4%, ECE 0.010) [I] and by a small embedding model plus logistic regression on every dataset tested [I]. A probability of 1.00 is wrong routinely: 129 rows at 1.00 were 76.7% accurate [I]. Cannot raise provenance. Makes A6 measurable for cents. | **Partial.** Confirms the evaluator is a rented slot; does not close A6. |
| **C. Deterministic policy execution** | Settled. Buy Cedar or OPA behind a gateway; the ledger and a disciplined baseline agree on 138,240 decisions and both pass 20 of 20 probes. | Unchanged, and consistent with TypeSafe's own guidance: code owns composition, thresholds and side effects; do arithmetic and date comparison in code; the model is not a security boundary [V]. A thresholded-questions engine cannot see adoption time, issuer power, single-use consumption or version pinning, because those are ledger facts, not text. | **No.** |
| **D. Missing evidence and uncertainty** | Six-valued outcome vocabulary already exists in the lab: BLOCK, REQUEST_FACT, REQUEST_AUTHORITY, CONFLICT, SEMANTIC_REVIEW, CLEAR. 16 of 46 IPSA outcomes relied on facts gathered after the original decision. S2 met by as-of queries. | Marginal. With an explicit "cannot be determined" option Jev abstains on 95% of genuinely unanswerable items [I]; without one, on 0 of 30 [I]; on missing-link inference, 0 of 6 even with the option [I]. Confidence is distribution concentration, indistinguishable from entropy [I]. Jev cannot detect discretion, which is a property of the rule. It raises the decision-time capture requirement because it returns no rationale and is not deterministic. | **No.** A fail-closed evidence-presence pre-filter is the only candidate role, untested on this domain. |
| **Grant ledger and settlement loop** (approach E) | The one part not found in a shipping product, about 65% confidence. Conditional on S3. | Untouched. SEMANTIC_REVIEW and REQUEST_FACT are deterministic ledger-state outcomes in `lab/ledger_arm.py`, not classifier outputs, so Jev does not make them cheaper for Ramp or AWS to add. | **No.** |
| **Economics** (S3, S4, recurrence, owner willingness) | Leans against. L3 settlements 47.5% never reused; G5 86% of classes seen once; Yan 114 of 140 "ask me". Needs a design partner. | Untouched. Cost per decision was never the binding constraint; human minutes and recurrence are. | **No.** |
| **Moat** | None beyond the settlement loop; otherwise conventions worth publishing. | Model-adjacent candidates visibly commodity. Two separate facts: about 28 wire-compatible open implementations of the interface within six days [I/U]; and on JevBench v1.2 open systems within one point of Jev on a composite that weights speed and cost at half, where Jev is fifth on intelligence alone and keeps a hard-tier zero-shot lead of 74.1 versus 69.5 [I/U]. The interface and the price are commodity; hard-tier zero-shot accuracy is not yet. One small new component appears: a registry of evaluator bindings per predicate. | **Partial.** Weakens further. |
| **Enforcement, gateway, decision log** | Buy. Bedrock AgentCore Policy and Ramp's suggestion loop verified; Microsoft, Auth0 and Permit.io reported. | Buy. | **No.** |
| **The 48-case lab** | Do not extend; its metrics cannot separate architectures and its reuse ceiling is 8 of 24. | Still do not. Jev cannot be tested on pre-digested columns. | **No.** |

### 2a. Problem A, item by item

Jev operates strictly after semantics are specified. It consumes a predicate a person wrote and never produces one. Per item:

| Sub-item | What settles it in Sophon | Can Jev help? |
|---|---|---|
| Implicit versus explicit conditions | The reading table (`lab/READING.md`) written by a person; the FAR audit found hidden residual semantics that compilers missed | No. Jev scores a stated proposition; it cannot surface an unstated one |
| Exceptions | Ledger acts: CASE_EXCEPTION, RELAX_CONSTRAINT; 18 of 46 disputes were discretionary | No. Applying an exception is an act of a person with power |
| Priority between conflicting rules | Effective dating in code, or a person; Davies, Pound, McDonagh | Dangerous. Answers from priors with no channel to say the text is silent |
| Scope | An open term (R4x: does approval extend beyond travel) settled by interpretation | Flag only. It can say a clause is ambiguous about scope; a reader found three such gaps by hand |
| Effective dates | Convention 1; whether "applies from" reaches expenses incurred or decisions made (R13) is interpretive | No. Date ordering is code; the reach of a date is a ruling |
| Ambiguous language and open standards | SEMANTIC_REVIEW until a settlement is in force | Flag only, additive, never removing a candidate |
| Missing rules | Closed surface (convention 5); R0 and R12 | No. Absence is undetectable from text, and Jev does not abstain without an explicit option [I] |
| Organisational interpretation | The settlement loop; proposal to a ratifier with replay | No. Jev consumes it, never derives it |
| Who may approve an interpretation | Typed ownership (convention 2), checked at record time | No. No identity channel; not a security boundary [V] |

### 2b. Problem B, dimension by dimension

| Dimension | What Jev offers | Measured | Consequence for Sophon |
|---|---|---|---|
| Typed outputs | Noul probability; Choice of up to 255; Score on 2 to 10 levels [V] | Probabilities quantized to 0.01, often exactly 0 or 1 [I]; Noul and two-option Choice framings of one predicate differ by 0.125 mean [I] | Framing is a versioned artefact; type safety is not correctness |
| Bounded answer space | The model cannot emit an option it was not offered [I] | Schema errors zero across tens of thousands of calls [I] | Removes parsing, not error; a wrong option at high confidence is routine [I] |
| Probability and confidence | A per-option distribution plus a confidence [V] | Confidence is indistinguishable from normalized entropy [I]; formula unpublished and reportedly drifts across versions [V, second-hand] | Never a proxy for evidence presence |
| Calibration | "Calibrated" by an undisclosed method [V] | Raw ECE 0.08 to 0.15 on new tasks [I]; per-type sign flips [I]; isotonic reached 0.008 with about 5,000 labels, most of the gain by about 200 [I]; under 100 labels cannot fit a threshold [I] | Per-predicate calibration is a labelling programme, and the labels train a specialist that beats Jev |
| Latency | 70 to 500 ms [V] | About 3 times a properly constrained small LLM; parity with fast open models; slower than a local encoder [I] | Immaterial at Sophon's volumes |
| Cost | $0.042 per million input tokens [V] | 1.4 to 7 times cheaper than cheap chat models; 12 to 323 times cheaper than frontier list price [I] | Immaterial; human minutes are the cost |
| Determinism | Implied by "typed decisions" [V] | 50 identical requests gave 15 distinct answer sets; 2.2% label flips between passes; borderline items cross a cutoff [I] | Store the probability as the fact of record; re-runs are checks with tolerance bands, not reconstruction |
| Auditability | None: no rationale, span or citation [V] | Confirmed in every independent run [I] | The record holds model id, question hash, state hash and a number; the why needs a human or a generative model |
| Versioning | Pinnable ids; aliases move [V] | `jev-latest` drift is an open issue; a gateway hides the version; no customer fine-tuning [I/V] | A vendor release is an external event that suspends every binding it does not list as surviving |
| Failure modes | Distracting context, indirection, adversarial state [V] | Drift of 0.42 at about 12,600 tokens; buried conflicts found 1 of 6 and 0 of 6; answers from priors with the state removed; a self-asserting comment skews a compliance judgment [I] | State stripped to the artifact and capped far below 32k; a prior-answer control before any predicate is bound |

### 2c. Problem D, the six states

A predicate that contains a normative term is two things: a fact (was the service running) and a standard ("reasonably"), and only the fact can be read from evidence. The standard is settled by a ratifier or routed to one.

| Owner's state | Sophon outcome | Detected by | Owned by | Jev |
|---|---|---|---|---|
| FALSE | BLOCK, or a clause unmet with its evidence recorded | Deterministic evaluation over facts of admissible provenance | The engine | May supply a value that routes; never one that clears alone |
| UNKNOWN, predicate not evaluable from the record | REQUEST_FACT, sub-reason missing | The predicate declaration lists required evidence; the check is structural | The requester | No. Confidence does not fall when the deciding information is absent [I] |
| Insufficient evidence, a required item absent | REQUEST_FACT, sub-reason missing or class too low | Evidence-presence gate and provenance check | The requester or an attester | Partially: an explicit evidence-presence question abstains on genuinely absent items [I], not on missing inference [I]; fail-closed only |
| Conflicting evidence | REQUEST_FACT, sub-reason conflict; CONFLICT already exists for two in-force settlements that disagree | Deterministic comparison of facts of equal class | A person | Weak: buried conflicts found 1 of 6 and 0 of 6 [I] |
| Low-confidence classification | REQUEST_FACT, sub-reason abstained | Abstention band in the evaluation contract | A person, then the label set | Yes, this is the one state a calibrated band is for |
| Genuinely discretionary | REQUEST_AUTHORITY or SEMANTIC_REVIEW | A property of the rule, fixed in the reading table at adoption | The role the rule names | No. A number over an open term is false determinization |

**H1**, "Jev makes the AI part less valuable but makes the governed layer more clearly the product": first half trivially true, second half unsupported. The AI part was priced at zero before Jev. "More clearly the product" is not "a product". That still turns on S3, and Jev supplies no evidence on S3.

**H2**, "if Jev works there may not be enough proprietary technology to justify an independent product": the consequent was already true on 21 September, and Jev is not the cause. `REPORT.md` says that if the settlement workflow does not matter, Sophon is a set of conventions worth publishing. Proprietary technology was never the right test for this product. The right test is whether the settlement loop is used and amortizes.

---

## 3. What Jev does not solve

- **Sufficiency.** Policy text does not say when an action is allowed. No reader of any quality changes that. Autonomy is the union of explicit grants.
- **Discretion.** 18 of 46 IPSA disputes turned primarily on discretionary relief or an exception. A number over an open term at run time is false determinization. The reading table routes open terms to SEMANTIC_REVIEW before any model is consulted.
- **Rule meaning and priority.** 12 of 46 turned on the meaning of a rule. Which rule wins, and whether past practice binds, are exercised by a person with power to do so. Jev answers such questions from priors.
- **Who holds what power.** Typed ownership is checked at record time against bounded delegations. A classifier has no identity channel and TypeSafe says it is not a security boundary [V].
- **Fact provenance.** A model reading of a claimant's narrative inherits the claimant's tier and adds extractor error. It cannot become system-observed. Whether it may satisfy a grant is a ratifier's decision per predicate, not a property of the model.
- **Facts that arrive later.** 16 of 46 outcomes relied on facts gathered after the original decision. No extractor at decision time recovers a fact not yet in the record.
- **Recurrence and amortization.** Jev changes neither the recurrence tables nor whether an owner will settle prospectively. This is the existential question and it stays open until a design partner is instrumented.
- **Long documents.** No independent test of Jev on a 100-page contract exists [I]. Discrimination already degrades at about 12,600 tokens: later items drifted by 0.42 in probability and 159 of 360 fell into the 0.3 to 0.7 band [I]; conflicting records buried mid-state were found 1 of 6 and 0 of 6 times [I]. The cap is about 32k tokens for state plus the longest question [V].
- **Adversarial state.** TypeSafe documents that text arguing for its own classification can move the answer [V]. A code comment asserting compliance skewed a compliance judgment [I]. Every fuzzy predicate in a governed workflow is evaluated over text an interested party wrote.
- **Auditability.** A number without a rationale or span. Any audited outcome needs a generative model on top, or a human.
- **Determinism and versioning.** 50 byte-identical requests produced 15 distinct answer sets [I]; 2.2% of labels flipped between passes [I]; aliases move silently and the confidence formula is unpublished and reportedly drifts across versions [V, second-hand].
- **Enterprise handling of governed data.** Hosted only, US-hosted, no on-premises or VPC option now or planned, zero-data-retention on the enterprise tier only, no public SLA [V/S]. Open reproductions remove this dependency, and should.

---

## 4. Revised architecture

Design principle: approach E on bought enforcement, with convention 7 made mechanical. Jev occupies exactly one optional slot and may be empty. If the slot is empty every model-read predicate falls back to human attestation and the architecture still works.

### Stages

```text
S0  SYSTEMS OF RECORD + GATEWAY (bought)
    every tool call mediated, default-deny, fresh check at execution
        |
S1  POLICY INGEST + READING TABLE (human; optional LLM drafting assistant, PROPOSED only)
    clauses, open terms, dispositions per clause, effective time reach
        |
S2  GRANT LEDGER (built, core)
    append-only typed acts: adopt · interpret · relax/add constraint · case exception ·
    delegate · amend · revoke; issuer, power, policy version, recorded-at, effective-from
        |
S3  PREDICATE DECLARATION + EVALUATOR BINDING (built, core; both are ledger acts)
    predicate id, clause it derives from, required evidence items, provenance tier a grant
    requires, outcome on absence; evaluator id pinned by version, question text hash,
    calibration table version, thresholds, abstention band, label source
        |
S4  FACT ACQUISITION: every fact has a SOURCE CLASS and a READER
    source class, ordered by who could have authored the content:
      SYSTEM (amount, payee, approver identity, running totals)   <- SoR integration
      ATTESTED (an accountable person under a declaration)          <- human
      THIRD-PARTY DOCUMENT (receipt, ticket, resolution)
      COUNTERPARTY (a claimant's narrative)
      AGENT (the agent's own assertion)                              <- never clears alone
    reader: a system field, a person, or a model binding  [JEV SLOT, optional, swappable]
    a reader never raises the source class; a grant states the minimum class it accepts
    and whether a model reader is admissible for that predicate
        |
S5  EVALUATION CONTRACT (deterministic software)
    counting, sums, dates in code; evidence-presence gate; calibrated probability;
    abstention band -> REQUEST_FACT; typed result: value | UNDETERMINED
        |
S6  POLICY ENGINE (bought: Cedar or OPA) compiled from ledger state
    six outcomes: CLEAR · BLOCK · REQUEST_FACT · REQUEST_AUTHORITY · CONFLICT · SEMANTIC_REVIEW
    REQUEST_FACT carries a sub-reason: missing · class too low · conflict · abstained
        |                                  |
     CLEAR -> S8                    anything else -> S7
        |
S7  ESCALATION + SETTLEMENT (built, core)
    default: single-use permit for this exact action
    optional: "this should be a rule" -> proposal -> replay over past cases -> ratifier with power
        |
S8  EXECUTION RECEIPT + DECISION LOG (bought store; built schema)
    permit, facts with tier and supplier, evaluator version, question hash, raw distribution,
    calibration version, policy version, as-of queryable
```

### Component table

| Component | Role | Classification | Jev? |
|---|---|---|---|
| Gateway and tool mediation | Default-deny, fresh check at execution, receipt capture | Third-party commodity | No |
| Policy engine (Cedar or OPA) | Evaluates compiled grants | Third-party commodity | No |
| Ledger-to-engine compiler | Pure function of ledger state to engine language | Deterministic software | No |
| Reading table for a rulebook | Clause dispositions and open terms, adopted by the owner | Human governance | No |
| Optional drafting assistant | Proposes clause lists and predicate wordings, PROPOSED only | AI-model inference (frontier LLM with spans) | No |
| Grant ledger of typed dated acts | Power checked at record time; effective dating; version pinning | **Sophon proprietary core** | No |
| Predicate declaration and evaluator binding | Convention 7 as code; the only thing that makes a model-read fact safe to consume | **Sophon proprietary core** | Referenced |
| System-of-record adapters | SYSTEM-class facts: amounts, identities, totals | System-of-record integration | No |
| Attestation capture | ATTESTED-class facts from an accountable person | Human governance | No |
| Model reader, bound per predicate | Reads THIRD-PARTY DOCUMENT or COUNTERPARTY sources; zero-label bootstrap | AI-model inference, optional, swappable (Jev, open reproduction, fine-tuned specialist, frontier LLM with spans) | **Yes, only here** |
| Evaluation contract | Calibration table, thresholds, abstention band, code arithmetic | Deterministic software | No |
| Six-outcome adapter | Maps engine and contract results to outcomes | Deterministic software | No |
| Escalation and settlement workflow | Single-use default; proposal to ratifier; replay | **Sophon proprietary core** | No |
| Replay of a proposed rule | Deterministic re-decision over recorded cases | Deterministic software | No |
| Rationale for audited outcomes | Spans and prose for a human reviewer | AI-model inference (frontier LLM) or human | No |
| Decision log store | Hash-chained, as-of queryable | Third-party commodity; schema is Sophon's | No |
| Ratifier and case-resolver roles | Different people, different powers | Human governance | No |

### Where Jev sits and the rules that bind it

One slot: a model reader at S4, admitted per predicate by an evaluator binding recorded as a ledger act with issuer, effective time and a pinned model id. The rules:

- The state is stripped to the artifact and capped well below the 32k limit, because discrimination degraded at about 12,600 tokens [I] and bouncer caps its state at 4KB [I].
- Counting, sums and date comparison are done in code. An evidence-presence question accompanies every value question. The question text and its framing are hashed and locked, since Noul and Choice framings of one predicate differ by 0.125 mean [I].
- Before a predicate is bound, a prior-answer control: score the labelled set with the artifact removed. If accuracy exceeds chance by more than a declared margin, the predicate is being answered from world knowledge, as Jev does at 0.38 to 0.46 against 0.15 chance [I], and it cannot be bound.
- The model id is pinned; `jev-latest` and gateways that hide the version are forbidden in a decision path. A vendor release is an external event that suspends every binding it does not list as surviving, convention 3 applied to evaluators.
- The calibration table is fitted per predicate on attested answers to REQUEST_FACT, which are the only legitimate labelled set. Most of the isotonic gain arrives by about 200 labels and fewer than about 100 cannot fit a threshold [I]. The table is a release-gated artefact. The label flywheel is a by-product of the settlement workflow, and it will run mostly on predicates that were never the hard ones.
- The abstention band routes to REQUEST_FACT with the sub-reason abstained. The stored probability is the fact of record; a re-run is a check with a tolerance band, since 50 identical requests gave 15 answer sets [I].
- A model-read value never raises the source class. It can never clear an action alone unless the ratifier's declaration for that predicate says so, and never when the source is COUNTERPARTY or AGENT.

Jev has no role at S1, S2, S3, S6, S7 or S8. It is never asked which rule wins, whether an action is sufficiently permitted, whether a person holds a power, or whether an open standard is met.

### Delete, simplify, outsource, stop treating as differentiating

| Component | Action | Reason |
|---|---|---|
| Semantic compiler, normative graph, precedence engine, purpose-built kernel | Delete | Already excluded; 138,240-decision equivalence; Jev cannot enumerate clauses or quote |
| Jev at ingest as an interpretation tool | Delete | A4 false; no span; second reader shares blind spots; adversarial text moves it [V] |
| Model confidence as the insufficiency signal | Delete | Confidence is entropy [I]; abstention needs an explicit option and an evidence-presence gate |
| Precedent retrieval, LLM judge with memory, similarity over past cases | Delete | "Paid before" rejected in 15 of 24 disputes; Pound versus McDonagh |
| Escalation triage classifier | Delete | Where escalations repeat a deterministic key covers them; where they do not, nothing does |
| The 48-case lab as an evaluation vehicle | Delete | Reuse ceiling 8 of 24; pre-digested judgments |
| Gateway, mediation, receipt capture, hash-chained log | Outsource | Shipped |
| Policy engine | Outsource | Cedar or OPA |
| Escalation inbox and approval UI | Outsource | Render the act types inside an existing approval channel |
| Rationale generation | Outsource | Commodity frontier-LLM call; the evidence record, not the prose, reconstructs the decision |
| Predicate evaluator (Jev or any typed-decision model) | Stop treating as differentiating | Open reproductions within one point [I/U]; specialists beat it once labels exist [I]; TypeSafe's own adapter runs the interface over OpenAI and Anthropic [I] |
| Predicate library as an asset | Stop treating as differentiating | A wording plus 200 labels is cheap to reproduce; the value is decomposition discipline, which is public method |
| Per-predicate calibration harness | Simplify | Isotonic or Platt refit is a few lines; keep it as deterministic software inside the contract |
| Ledger-to-engine compiler and outcome adapter | Simplify | Keep to the size of the lab arm |
| Grant ledger; predicate declaration and binding; settlement workflow | Keep as core | The only unshipped parts; convention 7 as code |

### The buy-everything delta

A customer with AgentCore Policy, Cedar, Ramp-style policy suggestion, Jev and a frontier LLM can assemble S0, S1, S4 to S6 and S8 today. What they cannot buy is S2, S3 and S7: typed dated acts with issuer power, the declaration that binds a predicate to its clause and its admissible evaluator, and the case-only versus propose-a-rule fork with replay. That delta is small in code, about the 246 lines of the lab ledger plus the binding registry and one workflow screen. Whether it is a product depends on whether anyone uses the fork. The investigation said so before Jev; Jev has not changed it.

---

## 5. Revised moat

Assume Jev-like models are broadly available, semantic classification is cheap, frontier models keep improving, and enterprise systems expose agent interfaces. All four are already true in September 2026.

| Candidate | Defensible? | Verdict | Why a competitor could or could not reproduce it |
|---|---|---|---|
| Model intelligence | No | Commodity | Open systems within one point of Jev on the JevBench v1.2 composite, which weights speed and cost at half [I/U]; Jev keeps a hard-tier zero-shot lead of 74.1 versus 69.5 [I/U], and frontier models are ahead on intelligence and calibration [I]; nothing in Jev's surface lacks published precedent [I/U] |
| Policy extraction | No | Not solved by anyone | Bedrock converts single plain-English rules to Cedar; document-to-rules over a real rulebook is approach A, self-audited at 71 to 77%. An unsolved problem is not a moat and not a commodity |
| Semantic compilation | No | Rejected | Same. Jev cannot compile; it scores |
| Predicate libraries | No | Table stakes | A wording plus about 200 labels reproduces any predicate [I]; the customer holds the labels and can run an open model on them |
| Interpretation graphs | No | Rejected | No probe of 20 needed one |
| Provenance | No | Necessary, not differentiating | Convention 7 is a data-model rule; a platform can adopt it in a release once named. Its value is that someone names it first |
| Authority and governance | Unproven | Component, not moat | Typed ownership and bounded delegation exist in XACML's administrative profile, KeyNote and SPKI. The unshipped part is the case-versus-rule fork with issuer provenance, a design lead measured in quarters at most, not a defensible position |
| Versioned institutional semantics | Unproven | Conditional | Only compounds if settlements are reused. L3 settlements 47.5% never reused with flat quarterly coverage; G5 86% seen once. Predicates recur across claim classes, claim classes do not, so the asset is smaller than the thesis assumed |
| Historical decisions and corrections | No | Liability as precedent, asset as log | "Paid before" is rejected two times in three; learning from approvals inherits that. As a provenance-bearing decision log it is portable JSON the customer will insist stays portable |
| Evidence graphs | No | Commodity | Object storage plus hashes plus a schema |
| Workflow integrations | No | Commodity | Owned by the gateway and system-of-record vendors |
| Auditability | Unproven | Table stakes, possible wedge | If a partner's pain is reconstruction after the fact, the product is the log and the settlement loop is secondary |
| Human approval processes | No | Commodity | Auth0 and Permit.io ship bound approvals [reported]; the act types are Sophon's, the channel is not |
| Accumulated customer-specific knowledge | No | Weak | Accrues to the customer running an open model on their own labels, not to a vendor |

One new component appears because of Jev: a registry of evaluator bindings per predicate, ratified by the same power as the grant, because changing a threshold changes what a grant means. It is real, small, and a feature.

**What is defensible, ranked.** (1) The settlement loop with issuer provenance and replay: a design lead, conditional on S3. (2) The predicate declaration and evaluator binding as ledger acts: a component. (3) The decision log with provenance: a wedge if the framing-is-wrong branch turns out to be right. Nothing else.

**Business model this implies.** Either publish the seven conventions, the 20 probes and a Cedar or OPA reference implementation as an open specification with a design-partner services practice; or build the settlement loop as a per-workflow feature for one high-cost-of-error workflow and plan for acquisition by the gateway or system-of-record vendor. Gate the second on the `DECISION.md` thresholds measured at a design partner.

---

## 6. Kill criteria

Building on `DECISION.md`. Numbers are proposals to fix before measuring.

| # | Finding | How it would be established |
|---|---|---|
| K1 | Under 1 in 5 escalations leads to a reusable settlement within a quarter, or a settlement decides a median of fewer than about 10 later actions | Design partner instrumented for S3 to S5 against approach B for one quarter |
| K2 | The policy owner cannot or will not settle prospectively: fewer than 1 in 10 case answers marked "this should be a rule", or fewer than 1 in 5 of those ratified within the quarter. The only field prior, IPSA's 4 of 17 recommendations committed, is 23.5% and sits just above that bar | Same instrumentation, counts by person and power |
| K3 | Wrong clearances traced to wrong facts are at least as common as an LLM judge's wrong clearances on the same cases | The partner's first 100 escalated cases with a reviewer-built fact sheet, on a corpus that contains both outcomes; the IPSA reviews cannot measure this because 45 of 46 are refusals |
| K4 | No primitive reaches an abstention-recall lower bound of 0.6 on facts absent at submission, while more than half of the partner's escalated cases need narrative facts | Stage 2 of section 7, plus the Stage 1 fact inventory |
| K5 | In the partner's workflow the refusal rate is under about 1% and actions are reversible, so checking before acting cannot pay | Base rates from the partner's own decision log over one quarter, computed before any instrumentation |
| K6 | AWS, Microsoft, Ramp or PolicyLayer ships case-versus-rule settlement with issuer provenance | Quarterly re-read of product documentation, source re-read not summarised |
| K7 | A buy-everything rebuild reproduces all 20 probes and the six outcomes on AgentCore plus Cedar in under a week of glue, and the partner never uses the case-only versus propose-a-rule distinction | Run the rebuild in parallel with the partner; count Sophon-specific lines and uses of each settlement type |
| K8 | The partner's real pain is audit reconstruction after the fact, not autonomy before it | Partner interviews plus a log of reconstruction queries versus pre-action decisions |
| K9 | Human minutes per settlement exceed minutes per case-by-case review at the partner, so S3 has no denominator in Sophon's favour | Timed settlements and timed case reviews during the quarter; nothing in the investigation measures minutes today |
| K10 | Buyers accept an untyped loop, such as Ramp's suggested policy edits published by a permitted admin, and will not pay for typed, dated, issuer-tagged settlement | Prospect interviews in Stage 1 of section 7; a pilot quote refused on that ground |

K4, K5, K9 and K10 are new. K4 is technical and Jev-era: the fact layer cannot be trusted to fail closed. K5 is the packet's open question 1 turned into a number. K9 gives S3 a cost denominator. K10 is the more likely market failure than K6: not that a vendor ships the typed version, but that nobody pays for the typing.

---

## 7. Highest-value next experiment

The first candidate, a fact-extraction fidelity test on the 46 IPSA reviews, was rejected by both hostile reviews, and the rejection holds. All 45 reviews are of refusals, so a pipeline that emits REQUEST_FACT on any absent fact has zero wrong clearances by construction, the artefact `REPORT.md` section 4.3 exposed in the packet's replay. The decision-time state would be a reviewer's hindsight summary, sliced by the same engineer who then scores abstention on it. And 95% versus 90% cannot be told apart at 20 to 35 items per predicate. That design would have produced numbers, not a decision.

What survives is narrower and answers the question Jev actually raised: is the model-read fact slot on the critical path at all?

**Name.** Fact-observability screen, with a gated grounding-and-abstention test.

**Hypothesis.** In at least one candidate workflow where checking before acting pays, at least 80% of the facts its grants require are system-observed or attested at decision time. If true, the model-read slot is empty by design and the design-partner quarter runs on approach B with no model in the path. If false for every candidate, narrative facts are on the critical path, and the gated test decides whether any evaluator may fill the slot.

**Input data.** Stage 1: for two of the candidate workflows named in `REPORT.md` section 8 (refunds and credits above a threshold, access grants, payment release, contract concessions, outbound data sharing), at two prospective partners each, so four decision-log exports, recruited in the week before the experiment starts. A failure to recruit is itself a data point for K10. Per workflow: one quarter of decision-log base rates computed exactly as the 1,000-row IPSA join was; the governing policy and delegated-authority matrix; the schemas of the systems of record the actions touch; and a structured interview with the policy owner on who may write a rule after an escalation and how often that happens. Stage 2, only if triggered: the partner's most recent 100 escalated cases with their submission-time records, a fact sheet built by the partner's own reviewer rather than the experimenter, and a second annotator on 10 cases.

**Implementation.** Stage 1, days 1 to 5, no model calls. Per workflow: refusal rate and reversibility from the log; the grants the policy would need, written as sufficiency statements per convention 6; an inventory of every fact each grant requires, tagged T0 system-observed, T1 attested or T2 narrative by checking whether a system field or an attestation step supplies it; the interview answers for K2. Stage 2, days 6 to 10, only for a workflow that cleared the economics and failed the 80% observability bar. Pre-register and hash before any call: predicates limited to the T2 facts the grants consume; three-level absence coding (never mentioned; mentioned but underdetermined; absent at submission); one primary question form per primitive fixed in advance, with an explicit "cannot be determined from this record" option and an evidence-presence gate; primitives Jev pinned as `jev-1.13.0`, one frontier LLM by exact id with structured outputs, one NLI encoder pinned by commit hash with paragraph chunking; a state-removed control run, because Jev scores 0.38 to 0.46 with the supporting state removed against 0.15 chance [I]; a leakage control that strips any sentence stating the decision; median paraphrase reported, best never used. No calibration arm: 100 cases cannot fit a threshold [I].

**Comparison baselines.** Stage 1 is a measurement and has none. Stage 2: the frontier LLM and the encoder against the partner's fact sheet; the second annotator's agreement as the ceiling; the state-removed run as the floor.

**Metrics.** Stage 1: refusal rate; share of refused actions that are irreversible; share of grant-required facts at each tier per workflow; count of escalation classes the owner says they would settle prospectively. Stage 2: accuracy on present facts with Wilson intervals; abstention recall and precision per absence level, recall being the safety number; state-removed accuracy; coverage, the share of cases decided rather than routed, reported beside wrong facts so the pipeline can fail.

**Pass and fail.** Stage 1 passes for a workflow if the refusal rate is at least 1%, refused actions are costly or irreversible, and T0 plus T1 facts cover at least 80% of grant requirements. It fails outright if no workflow clears the first two conditions. Stage 2 passes if the Wilson lower bound of abstention recall on absent-at-submission items exceeds 0.8 for some primitive at precision 0.7, and state-removed accuracy is within 10 points of chance. It fails if no primitive's lower bound exceeds 0.6. All numbers fixed before any data is collected.

**Decision by result.**

- Stage 1 finds a workflow that passes: run the design-partner quarter there on approach B with S3 to S5 instrumentation. The Jev slot stays empty. Jev is irrelevant to Sophon's decision.
- Stage 1 finds no workflow where checking pays: K5 fires. Stop. Publish the conventions.
- Stage 1 passes on economics, facts are mostly narrative, and Stage 2 passes: admit model-read facts as a provenance class for the passing predicates only, on the partner's own records, then run the quarter.
- Stage 2 fails: models manufacture facts when the record is silent. Convention 7 stays as written. Autonomous coverage is bounded by T0 and T1 facts, and the product question becomes whether REQUEST_FACT can be pushed to the requester at submission, where Sophon's delta over a policy agent is small.

**Cost and time.** One week of recruiting, then two weeks for one engineer, most of it partner conversations and schema reading. Stage 2 model spend under 50 dollars.

**What it cannot decide.** Whether settlements amortize and whether owners settle in practice. Those need the quarter. No branch of this experiment changes the standing recommendation. It decides where the quarter runs and which fact provenance it admits.

---

**Sophon should now be built as a published convention pack and nothing more until one real workflow passes the base-rate screen and shows escalations that recur and are settled prospectively, because Jev changes neither the technical conclusion nor the economic one.**
