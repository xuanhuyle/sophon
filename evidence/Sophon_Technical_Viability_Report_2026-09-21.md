# SOPHON — Consolidated Technical Viability Report
## Status after semantic-compiler experiments and authority-kernel tests K1–K6
**Date:** 21 September 2026

---

# 1. Executive conclusion

## Technical viability verdict

**Yes — Sophon has a technically viable path, but only under a narrower architecture than the original “natural-language rules automatically become correct executable authority” thesis.**

The evidence does **not** support the strong claim that Sophon can take an arbitrary body of contracts, policies, procedures or rulebooks and autonomously compile them into correct executable controls with negligible human semantic review.

The evidence **does** support a narrower and more defensible product thesis:

> **Sophon can be built as a proof-carrying normative control plane for AI agents: human-written rules, authorized interpretations and organizational authority are versioned and traceable; everything safely determinable is compiled into executable controls; unresolved semantics explicitly reduce authority; and the exact authorized action is independently mediated at execution time.**

The core technical path is therefore:

```text
Authoritative documents
        ↓
Source representation + provenance
        ↓
Semantic propositions / open standards / conflicts
        ↓
Human or authoritative settlement where required
        ↓
Versioned normative authority graph
        ↓
Deterministic authorization kernel
        ↓
Execution-bound clearance
        ↓
Trusted gateway / adapter
        ↓
Tool or API
```

The key architectural insight is that **semantic correctness and normative authority are not the same problem**.

Sophon does not need to prove that every human interpretation is the uniquely correct linguistic meaning of a rule. It needs to prove:

1. what source the interpretation refers to;
2. who issued it;
3. whether that person had authority to issue that kind of interpretation;
4. what exact operational effect was approved;
5. which source version it applies to;
6. when it became effective;
7. how later amendments, conflicts, revocations and precedents affect it;
8. and whether the exact authorized action is what ultimately executes.

This is a technically coherent architecture.

The largest remaining technical uncertainty is no longer the deterministic authority kernel. It is **semantic compilation economics**:

> Can Sophon turn enough real organizational rules and human judgments into reusable executable authority with materially less effort than manually building and maintaining a conventional policy engine?

That is now the most important falsifiable question.

---

# 2. How the Sophon thesis evolved

Sophon started from a much stronger concept:

> “Can an LLM understand a contract or rulebook and make an AI agent comply with it?”

That framing proved too vague.

The project progressively decomposed the problem into distinct technical layers.

The thesis evolved roughly as follows:

1. **Can an LLM understand a credit agreement?**
2. **Can an AI comply with rules?**
3. **Can rules automatically become machine-enforceable authority?**
4. **Can authority be separated from agent orchestration?**
5. **Can AI agents gain broader autonomy while authority remains externally controlled and auditable?**
6. **Can human interpretations and precedents become reusable executable authority without pretending they are machine-proven semantic truths?**
7. **Can every authorized action carry a proof all the way to the execution boundary?**

The current architecture is best described as:

> **a compiler + normative version-control system + deterministic authorization runtime + execution gateway.**

The root invariant became stronger over time.

Initial:

> **Never silently wrong.**

Current:

> **No authority may appear, change, or execute silently.**

That includes both unauthorized permissions and unauthorized restrictions.

---

# 3. The fundamental product insight: rules are not only documents

One of the most important conclusions from the work is that organizational authority is not contained exclusively in formal written policies.

Real organizations operate through a hierarchy of normative objects:

```text
Foundational authority
    ↓
Policies / contracts / formal rules
    ↓
Implementation rules
    ↓
Authorized interpretations
    ↓
Exceptions / waivers
    ↓
Individual decisions
    ↓
Review / appeal decisions
    ↓
Precedents / settled practices
```

The analogy with legal systems is useful:

```text
Constitution
    ↓
Law
    ↓
Decree / regulation
    ↓
Circular / administrative interpretation
    ↓
Administrative acts
    ↓
Court decisions / jurisprudence
```

The important point is not the French legal hierarchy itself. It is the **structural pattern**:

> A rule acquires operational meaning through later authoritative acts, and those acts have different normative force.

This led to a potentially important product direction:

> **Sophon can make “unspoken rules” explicit without pretending they were already written in the original source.**

For example:

Source policy:

> “Hotel expenses must be reasonable.”

Authorized CFO interpretation:

> “For Paris, reasonable means no more than €350/night.”

Sophon should not rewrite history and say:

> “The policy always meant €350.”

Instead it should record:

```text
Source:
Travel Policy §7.3

Source semantic status:
OPEN STANDARD

Normative act:
AUTHORIZED INTERPRETATION

Issuer:
CFO

Authority basis:
Interpretive authority over Travel Policy §7.3

Operational effect:
Paris hotel rate <= €350

Effective from:
2026-10-01

Source version:
hash abc123

Semantic claim:
NOT mechanically entailed by source

Normative status:
AUTHORITATIVE CONSTRUCTION
```

This is closer to Git than to a conventional policy engine.

The value proposition is therefore not necessarily:

> “Sophon is always right.”

It may be:

> **“Sophon makes the evolution of organizational authority explicit, reviewable, versioned, executable and auditable.”**

That can be more valuable in practice than pretending semantic ambiguity does not exist.

---

# 4. The strongest negative result: automatic semantic compilation is not solved

Before the K1–K6 authority-kernel work, multiple real-rulebook experiments attacked the semantic front end.

The consistent pattern was important.

## Synthetic end-to-end test

A controlled synthetic test showed that the architecture could work when the source truth and expected interpretation were known.

Results included:

- correct classification of direct / refinement / residual rules;
- zero mismatches in large deterministic runtime tests;
- successful amendment propagation.

But this was only controlled feasibility.

It did **not** prove reliable semantic extraction from arbitrary real documents.

---

# 5. Real-corpus semantic experiments

Several increasingly strict tests were run on public policies and regulations.

The exact documents varied, but the conclusion was stable.

## Stanford

A frozen first-pass compiler produced 90 controls.

Post-freeze audit found:

- 27 omitted controls;
- 18 material omissions;
- internal recall roughly 77%.

Main lesson:

> A plausible-looking compiled rulebook can still silently omit material governance.

---

## Yale

A forward-construction plus coverage-search architecture still missed:

- 32 controls;
- 24 material controls.

Approximate internal recall was roughly 71%.

Lesson:

> A second “coverage model” does not solve the problem if both models share the same semantic blind spots.

---

## Yale structural ledger

A structural source ledger improved traceability but failed to preserve:

- table semantics;
- row-level mappings;
- cross-reference bindings.

Lesson:

> Sentence-level atomicity is insufficient.

---

## Minnesota

Clause/conjunct-level atomization materially improved coverage.

But post-freeze audit still found:

- omitted propositions;
- state/modality atomization errors.

This led to the stronger invariant:

> **Every material modal proposition expressed by the supplied corpus must have an explicit disposition before autonomous clearance.**

---

## Cornell

A deterministic lexical/deontic parser failed on cases such as:

- “No … may …”;
- coordination;
- embedded modality;
- negative reimbursement language;
- subordinate “can” clauses.

Lesson:

> Regex/deontic splitting is not safe for authority compilation.

---

## University of Washington

A semantic splitter still lost:

- fallback branches;
- table mappings;
- modifiers;
- role scope;
- routing semantics.

Lesson:

> “One source atom → one or more propositions” is still insufficient if semantic clause structure itself is incomplete.

---

## Washington State University

A clause-certified architecture initially appeared complete because every compiler-known clause mapped into IR.

Audit revealed that the clause inventory itself was incomplete.

This exposed a circular certificate problem.

Resulting requirement:

```text
Closure 0:
raw source → structural leaves

Closure 1:
structural leaves → semantic clauses

Closure 2:
semantic clauses → governance IR
```

All three closures matter.

---

## FAR test

The FAR test improved raw-source closure by using the regulation's explicit hierarchy.

Post-freeze audit still found material defects:

- inherited agency scope lost;
- open standards falsely determinized;
- required record-field enumeration collapsed;
- hidden residual semantics.

This drove the typed AST model:

```text
ACTOR / SCOPE
    ↓
DEONTIC MODALITY
    ↓
ACTION
    ↓
AND / OR / IF / ONLY_IF / UNLESS / EXCEPT
    ↓
MODIFIER / EVIDENCE / EFFECT
    ↓
OPEN_STANDARD / BINDING
```

The crucial conclusion was:

> **Runtime enforcement is comparatively easy. Reliable semantic compilation is the load-bearing problem.**

That conclusion remains valid after K1–K6.

---

# 6. The resulting semantic architecture

Sophon should therefore not treat LLM output as authority.

The safe architecture is:

```text
DOCUMENT
   ↓
SOURCE TREE
   ↓
PROPOSED SEMANTIC AST
   ↓
coverage / adversarial verification
   ↓
unresolved disagreement exposed
   ↓
AUTHORIZED RATIFICATION
   ↓
GOVERNANCE IR
   ↓
DETERMINISTIC RUNTIME
```

An AI-generated interpretation should initially be:

```text
PROPOSED
```

never:

```text
AUTHORITATIVE
```

unless one of the following is established:

- direct source entailment;
- explicit authoritative binding;
- properly authorized human interpretation;
- properly authorized precedent;
- properly authorized amendment / exception / implementation rule.

This separates:

```text
model confidence
```

from:

```text
normative authority
```

They must never be collapsed.

---

# 7. K1–K6: the authority kernel

The K1–K6 program deliberately stopped testing natural-language extraction and instead asked:

> If we already have structured normative objects, can Sophon reason about authority correctly and carry it all the way to execution?

This program produced much stronger results.

---

# 8. K1 — Proof-carrying, non-inflationary authority

## Question

Can Sophon prove that a normative act derives from a legitimate authority chain without authority silently expanding through delegation?

## Initial failure

The first version passed 50,000 randomized cases but post-freeze audit found:

- retroactive approvals;
- retroactive delegations;
- NaN numeric bypass;
- incorrect `GLOBAL` scope handling;
- duplicate-ID collision risk.

## Repair

The hardened kernel introduced:

- mandatory issuance time;
- no retroactive authority by default;
- strict finite numeric validation;
- typed scope semantics;
- globally unique immutable IDs;
- authority snapshot hashing;
- exact action hashes;
- independent chain reconstruction.

## Result

Repaired K1:

- 100,000 randomized cases;
- zero false-valid authority proofs;
- zero false-invalid proofs;
- zero mutation escapes.

## Lesson

A normative act needs a **proof of legitimacy**, not merely a field such as:

```text
issuer_competence = true
```

---

# 9. K2 — Authorization sufficiency

## Question

Even if every approval is legitimate, is the complete set of approvals sufficient?

## Initial failure

K2 exposed several existential problems:

- an unmodeled action could clear because no rule applied;
- deleting a rule could increase authority;
- authority labels such as `BOARD_PURCHASE` were not proof-bound;
- identity aliases could defeat separation of duties.

## Repair

K2 introduced:

### Closed authorization surface

Unknown action family:

```text
REQUEST_AUTHORITY
```

not:

```text
CLEAR
```

### Normative authorization formulas

Requirements themselves became authority objects.

### Canonical principal identity

Different usernames for the same person cannot satisfy two-person review.

### Proof-bound semantic authority tags

The authority capability used by K2 is carried from K1.

### Leaf-addressed satisfaction proof

Example:

```text
FINANCE_APPROVAL <- approval A3
PROCUREMENT_APPROVAL <- approval A4
DISTINCT_PRINCIPALS <- [A3, A4]
```

## Result

Repaired K2:

- 100,000 randomized cases;
- zero mismatches;
- zero unauthorized clearances;
- zero proof omissions.

## Lesson

> **“Every known requirement is satisfied” is not enough. Sophon must know that the applicable authorization surface is closed.**

---

# 10. K3 — Normative precedence, conflict and time

## Question

When multiple legitimate norms exist, which one actually governs?

## Tested situations

- superior vs inferior norms;
- binding vs nonbinding guidance;
- implementation rules;
- authorized interpretations;
- competing interpretations;
- review decisions;
- amendments;
- supersession;
- individual decisions;
- historical checkout;
- independent authority branches.

## Initial failures

Post-freeze audit found:

- lower interpretations could falsely claim supersession;
- stale review decisions could erase still-valid rules;
- circular normative dependencies could authorize themselves;
- exception semantics were incomplete.

## Repair

K3 made precedence relations first-class normative acts:

```text
SUPERSEDES
OVERRIDES
EXCEPTION_TO
```

They themselves require authority.

It also introduced:

- lineage validation before displacement;
- dependency-cycle detection;
- exact action-bound exceptions;
- historical time reconstruction;
- separation between action-level decision and latent normative inconsistency.

## Result

Final repaired K3:

- 50,000 randomized cases;
- zero unsafe permits inside the tested typed fragment.

## Lesson

> **Sophon must never invent precedence. Every displacement, exception, override or supersession needs its own authoritative basis.**

---

# 11. K4 — Interpretation integrity and normative power type

K4 produced one of the most important conceptual results.

## Question

If a person is authorized to interpret a rule, how do we know that what they just did is actually an interpretation rather than an amendment, exception or new policy?

## Fundamental discovery

Suppose:

```text
Source:
amount <= 500

CFO “interpretation”:
amount <= 1
```

The new rule is safer for the agent.

But it is not semantically equivalent to the source.

It creates a new restriction.

Therefore:

> **Narrower ≠ legitimate interpretation.**

This separates two dimensions:

```text
SAFETY RELATION
Does the proposal increase or reduce freedom?

NORMATIVE LEGITIMACY
Did the actor possess authority to make this kind of change?
```

These are independent.

## Normative-effect powers

K4 evolved authority from coarse labels:

```text
may INTERPRET
```

to effect-specific capabilities:

```text
INTERPRET_OPEN_STANDARD
ADD_CONSTRAINT
CREATE_OBLIGATION
RELAX_CONSTRAINT
REMOVE_OBLIGATION
AMEND_SOURCE
```

And then to bounded capabilities:

```text
target source
source hash/version
permitted predicate
permitted output type
threshold range
allowed exception predicate
persistence across amendments
```

## Human interpretation result

For an open rule such as:

> “reasonable”

an authorized human can settle it operationally.

But Sophon records:

```text
AUTHORIZED_CONSTRUCTION
```

not:

```text
SOURCE_ENTAILMENT
```

## Result

The final K4 implementation completed:

- 100,000 randomized cases;
- zero mismatches;
- zero unsafe accepts;

inside the deliberately small typed semantic fragment.

## Lesson

> **Sophon must never silently change the normative order — even in a conservative direction.**

---

# 12. K5 — Human ratification and Git-like lifecycle

K5 directly tested the AI-native workflow.

## Target workflow

```text
AI proposal
    ↓
human review/edit
    ↓
authority verification
    ↓
semantic + normative diff
    ↓
ratification
    ↓
effective date
    ↓
merged authority artifact
    ↓
later amendment / revocation / rollback
```

## Core invariant

> An AI proposal acquires no normative force merely because a model created it or a caller changed its status.

Authority must arise from an explicit human normative act.

## Major failures discovered and repaired

K5 found:

- upstream K4 proof was not originally carried into K5;
- reviews could predate the proposal;
- reviews could come from the future;
- review-policy versions were not pinned;
- revocation could disappear when the issuer later lost authority;
- nonexistent successors could supersede live authority;
- changed review rules could retroactively make old reviews sufficient;
- reviewer authority could disappear between review and final merge;
- a successor could be authentic but already revoked.

All of these were fixed.

The final K5 exit patch added:

### Merge-time reviewer-power revalidation

At merge:

```text
proposal.transformation ∈ current capability
proposal.effect_grant   ∈ current capability
```

### Live-successor requirement

A replacement can supersede current authority only if:

```text
effective_status(replacement, supersession_time) == EFFECTIVE
```

with recursive, cycle-safe lifecycle evaluation.

## Final patch result

- 9/9 explicit acceptance cases;
- 50,000 merge regression cases;
- 50,000 lifecycle regression cases;
- zero errors.

## Important architectural outcome

A merged Sophon authority artifact is conceptually similar to a governance commit.

It contains or binds:

```text
source version
proposal
semantic transformation
K4 bounded-effect proof
review formula
human approvals
reviewer authority proofs
ratification time
effective time
amendment / rollback / supersession provenance
```

This directly supports the Git-like product thesis.

---

# 13. K6 — Execution-bound authority

K6 was the final synthetic kernel test.

## Question

Even if an action is perfectly authorized, how do we know that the exact authorized action is what actually executes?

## V1 failures

The first version passed 100,000 randomized cases.

Post-freeze audit then found five dangerous defects:

1. concurrent actions could bypass cumulative limits;
2. tools could be called around the gateway;
3. authority could change after the last check but before the irreversible effect;
4. provider could commit then timeout, causing external/local divergence;
5. the effect contract was hashed but actual effects were not validated.

## R1

Introduced:

- atomic reservations;
- durable execution journal;
- adapter-only provider credentials;
- fresh authority/binding/tool checks;
- explicit execution linearization;
- signed execution permits;
- provider idempotency;
- reconciliation;
- exactly-once local obligation creation.

R1 still failed audit because:

- the same provider idempotency key could be reused for a different Sophon action;
- effect types matched but effect values could differ;
- prepared reservations could leak;
- permits could be replayed indefinitely.

## R2

Final K6 introduced:

### Sophon-level idempotency binding

```text
idempotency key → exact canonical action hash
```

before dispatch.

### Exact effect equivalence

Receipt/effect must match:

- vendor;
- bank account;
- amount;
- currency;
- idempotency key;
- debit cardinality;
- credit cardinality;
- exact debit amount;
- exact credit amount;
- exact vendor;
- no extra effect type.

### PREPARED lease

Pre-linearization crashes can be safely reaped.

### One-shot execution permit

Permit is consumed by the adapter before the irreversible call.

### Execution linearization point

```text
PREPARED
    ↓
COMMITTED_TO_EXECUTE
```

At this point:

- action is frozen;
- cumulative capacity is reserved;
- authority/control-plane state is rechecked;
- bindings are rechecked;
- tool contract is checked;
- execution permit is issued.

A revocation before this point blocks execution.

A revocation after it does not retroactively invalidate an irreversible action already committed.

## Final result

R2:

- 100,000 randomized cases;
- zero errors;
- zero unsafe executions;
- zero duplicate-effect errors.

## Remaining trust boundary

A provider can still lie.

Example:

Authorized payment:

```text
€10k
```

External provider actually debits:

```text
€15k
```

Sophon can detect the receipt mismatch and return:

```text
EFFECT_CONTRACT_VIOLATION
```

but it cannot undo the external €15k debit.

Therefore:

> **External effect truth is an explicit trusted-computing boundary.**

Sophon requires either:

- trustworthy tool/API semantics;
- or a sufficiently controlled adapter/sandbox capable of constraining effects.

This is not another authority-graph bug. It is a real system boundary.

---

# 14. What has actually been demonstrated

The work supports the technical feasibility of the following capabilities.

## A. Structured authority representation

Sophon can model:

- actors;
- delegations;
- authority scope;
- normative act types;
- review formulas;
- exceptions;
- amendments;
- precedents;
- effective dates;
- revocations;
- supersession;
- obligations.

---

## B. Proof-carrying authority

An authorization can include reconstructable evidence of:

- who had authority;
- through which delegation chain;
- under which source/version;
- using which approvals;
- under which review formula;
- at which point in time.

---

## C. Human-on-the-loop semantic settlement

Human judgment can become executable authority without making humans approve every individual transaction.

The intended amortization model is:

```text
ambiguous rule
    ↓
distinguishing cases
    ↓
authorized human interpretation
    ↓
versioned operational rule
    ↓
reusable deterministic execution
```

The key metric should eventually be:

> **coverage growth per human interpretation.**

---

## D. Fail-closed behavior

Unknowns can explicitly produce:

```text
REQUEST_FACT
REQUEST_AUTHORITY
SEMANTIC_REVIEW
CONFLICT
BLOCK
```

rather than becoming implicit permission.

---

## E. Stateful and trajectory-sensitive enforcement

The runtime can enforce:

- cumulative limits;
- state transitions;
- prior-action constraints;
- obligations;
- stale tokens;
- amendments;
- exact-action bindings.

---

## F. Git-like normative history

The architecture can preserve:

- source commits;
- interpretations;
- human edits;
- reviews;
- ratification;
- effective dates;
- amendments;
- rollback;
- supersession;
- historical checkout.

This is technically credible.

---

## G. Execution mediation

The architecture can carry the normative proof through to a tool boundary using:

- clearance tokens;
- action hashes;
- state snapshots;
- authority hashes;
- binding hashes;
- execution journals;
- one-shot permits;
- idempotency;
- reconciliation.

---

# 15. What has NOT been demonstrated

This distinction is essential.

## 1. Fully automatic natural-language compilation

Not demonstrated.

The real-corpus tests repeatedly found material omissions and semantic distortions after apparently successful compilation.

Strong thesis:

> “Upload a rulebook and Sophon automatically generates a complete, correct executable authority model.”

**Current verdict: NO-GO.**

---

## 2. Near-zero human semantic review

Not demonstrated.

A core commercial risk remains:

> If building the authoritative semantic model requires almost as much human effort as manually authoring policies in a conventional policy engine, Sophon's differentiation weakens materially.

---

## 3. Automatic discovery of every organizational predicate/data binding

Not demonstrated.

Many rules refer to concepts such as:

- reasonable;
- necessary;
- strategic;
- ordinary course;
- material;
- authorized supplier;
- critical system;
- current approval;
- customer consent.

Sophon still needs to discover and bind the required external predicates.

Caller attestation can provide facts.

It cannot repair a predicate that Sophon never discovered.

---

## 4. Proof that the supplied corpus is globally complete

By product assumption, the organization supplies the authoritative corpus.

Sophon can prove coverage **within the supplied corpus/action surface**.

It cannot prove that an undisclosed policy or side agreement does not exist.

That assumption must remain explicit.

---

## 5. Safety against malicious external systems with hidden side effects

Not demonstrated and probably impossible for Sophon alone.

The execution theorem is conditional on observable/enforceable tool semantics.

---

## 6. Production distributed-systems correctness

The synthetic tests did not test:

- production databases;
- network partitions;
- distributed transactions;
- key custody;
- HSMs;
- multi-region replication;
- real authentication infrastructure;
- high-scale concurrency;
- external provider SLAs.

Those are engineering tasks, not yet validated product claims.

---

# 16. The technical viability theorem Sophon can reasonably claim

A defensible version is:

> **Given:**
>
> 1. an explicitly supplied authoritative governance corpus;
> 2. a bounded action surface;
> 3. structured/ratified semantic propositions sufficient for the contemplated action;
> 4. observable required external facts;
> 5. complete mediation of the relevant tool/action boundary;
> 6. reliable tool-effect semantics;
>
> **Sophon can construct a proof-carrying authority state and independently determine whether the exact contemplated action is authorized, blocked, missing facts, missing authority, semantically unresolved or conflicted; and can prevent execution through a compatible gateway unless the authorization proof remains valid at the execution boundary.**

That is a meaningful technical claim.

It is much narrower than “AI understands policy.”

But it is also much stronger and more testable.

---

# 17. Proposed production architecture

The foundational product should be decomposed into the following components.

## 17.1 Source repository

Immutable/document-versioned source model with stable IDs for:

- document;
- section;
- paragraph;
- sentence;
- list;
- item;
- table;
- row;
- cell;
- footnote;
- cross-reference.

Each source unit should retain exact text and provenance.

---

## 17.2 Semantic AST

Typed nodes such as:

```text
Actor
Scope
DeonticModality
Predicate
Action
And
Or
Xor
Not
If
OnlyIf
Unless
Except
Modifier
TemporalConstraint
EvidenceRequirement
Effect
CrossReference
BindingReference
OpenStandard
Ambiguous
```

Modalities must remain distinct:

```text
MUST
MUST_NOT
MAY
SHOULD
SHOULD_NOT
NOT_REQUIRED
```

`SHOULD_NOT` must never silently become `MUST_NOT`.

---

## 17.3 Governance IR

Each rule should record:

- stable ID;
- source provenance;
- semantic AST provenance;
- modality;
- actor/scope;
- applicability;
- effect;
- required facts;
- bindings;
- temporal dependencies;
- state dependencies;
- lifecycle state;
- version.

Lifecycle states may include:

```text
PROPOSED
RATIFIED
COMPILED
REFINEMENT_REQUIRED
SEMANTIC_RESIDUAL
CONFLICT
STALE
RETIRED
```

---

## 17.4 Authority graph

This is the K1–K5 layer.

It contains:

- root authority;
- delegations;
- normative-power type;
- bounded effect grants;
- interpretations;
- implementation rules;
- amendments;
- exceptions;
- review decisions;
- precedents;
- supersession;
- revocation;
- effective time.

---

## 17.5 Binding registry

Maps normative predicates to:

- action fields;
- organizational configuration;
- external facts;
- state;
- approvals;
- authoritative interpretations;
- other rules.

Missing binding should yield:

```text
REQUEST_FACT
```

or:

```text
REQUEST_AUTHORITY
```

never implicit permission.

---

## 17.6 Deterministic runtime

Possible decisions:

```text
CLEAR
BLOCK
REQUEST_FACT
REQUEST_AUTHORITY
SEMANTIC_REVIEW
CONFLICT
```

Only `CLEAR` may proceed to execution.

---

## 17.7 Execution gateway

Execution requires:

```text
exact action hash
authority artifact hash
policy version
state version
binding snapshot
effect contract
expiry
idempotency key
```

The gateway performs:

```text
preclear
→ reserve
→ revalidate
→ linearize
→ one-shot permit
→ adapter
→ tool
→ receipt validation
→ local state commit
→ obligations
```

---

# 18. The AI-native user experience

The likely differentiated UI is not simply a policy dashboard.

It is a **normative repository**.

Think:

```text
GitHub for organizational authority
+
compiler
+
policy runtime
+
execution gateway
```

A user could see:

```text
Travel Policy §7.3
"Hotel expenses must be reasonable."

Status:
OPEN_STANDARD

AI proposal:
"Paris: <= €350/night"

Impact:
1,842 historical transactions
93% of current Paris hotel bookings
changes 4 existing manual-review cases

Semantic relation:
not mechanically entailed

Required authority:
CFO interpretation authority

Reviewer:
General Counsel

Current status:
UNDER REVIEW
```

After ratification:

```text
MERGED

Effective:
1 Oct 2026

Authority commit:
AUTH-98ad3...

Source:
Travel Policy v14

Interpretation:
Paris <= €350/night

Issuer:
CFO

Review:
GC approved

Effect:
deterministic rule generated

Dependencies:
Expense workflow
Travel booking agent
Expense reimbursement agent
```

That interaction is more credible than “the AI read the policy and knows what it means.”

---

# 19. Why Git-like traceability may matter more than perfect semantic correctness

A key product hypothesis emerged during the work:

> **In governance, traceability may be more valuable than pretending to achieve perfect interpretation.**

A conventional AI agent can make a decision and later explain itself.

That is weaker than Sophon if Sophon can show:

```text
which source existed at the time
which interpretation existed
who authorized it
under what delegated power
which review formula applied
what changed
what was superseded
which exact authority commit cleared the action
what executed
```

This turns governance from:

```text
"Why did the model do this?"
```

into:

```text
"Which normative state authorized this action?"
```

That is a qualitatively different audit model.

---

# 20. The commercial/technical risks that remain existential

The deterministic kernel no longer looks like the main existential risk.

The following do.

## Risk 1 — semantic-human effort is not sufficiently amortized

If every open rule requires bespoke human policy engineering, Sophon becomes an expensive policy-management UI.

The crucial economic test is:

> How many future actions become deterministic after one human interpretation?

---

## Risk 2 — too little enterprise authority is machine-observable

Rules may depend on facts that are:

- unavailable;
- subjective;
- hidden in conversations;
- spread across systems;
- not available before action time.

If too much authority remains externally unobservable, autonomous clearance coverage may remain low.

---

## Risk 3 — complete mediation is operationally expensive

Sophon only controls what passes through its boundary.

If agents can call tools directly, enforcement is optional.

Integrating every relevant tool may be costly.

---

## Risk 4 — organizations do not want explicit normative accountability

A Git-like authority model makes ambiguity visible.

That may be valuable.

It may also make organizations uncomfortable because it forces them to specify:

- who really has authority;
- who owns ambiguous rules;
- which “customary” decisions are actually policy;
- when undocumented precedent became binding.

This is partly a product-adoption risk, not merely technical.

---

## Risk 5 — incumbent policy engines absorb the easy portion

If Sophon's value is only:

```text
natural language → deterministic rule
```

existing policy engines can add LLM-assisted authoring.

The deeper differentiation must be:

- document-derived provenance;
- normative hierarchy;
- authorized interpretation lifecycle;
- semantic residuals;
- amendment propagation;
- proof-carrying action authority;
- agent execution mediation.

---

# 21. Is Sophon technically viable?

## Short answer

**Yes, conditionally.**

## More precise answer

### Strong autonomous compiler thesis

> Arbitrary natural-language rulebook → correct executable authority with minimal human semantic review.

**Not technically demonstrated. Current evidence argues against treating this as the starting product promise.**

### Narrow proof-carrying governance thesis

> Supplied governing corpus + structured/ratified interpretation + external facts + observable action → independently enforced, traceable authority boundary.

**Technically viable based on the work completed.**

The deterministic pieces are conceptually tractable and survived repeated adversarial hardening.

The semantic front end must therefore be designed as:

```text
AI proposes
humans settle where needed
Sophon records authority
deterministic runtime enforces
```

rather than:

```text
AI interprets
AI declares itself correct
runtime executes
```

---

# 22. Recommended next phase: one real workflow

The synthetic test program should stop here.

No K7.

The next experiment should test the product thesis rather than another kernel invariant.

Choose **one bounded workflow** with:

- meaningful but manageable authority;
- real human interpretations;
- observable actions;
- clear external facts;
- a tool boundary Sophon can mediate;
- enough historical decisions to test amortization.

The key metrics should be:

### Semantic conversion

- number of source provisions;
- number directly compilable;
- number requiring human settlement;
- number remaining semantic residual;
- time per human settlement;
- percentage reused across future cases.

### Operational coverage

- % actions deterministically clearable;
- % `REQUEST_FACT`;
- % `REQUEST_AUTHORITY`;
- % `CONFLICT`;
- % requiring human semantic judgment.

### Maintenance

- time to process amendments;
- number of derived rules invalidated;
- number of historical authorities affected;
- number of stale decisions caught.

### User value

- reviewer time saved;
- audit reconstruction time;
- clarity of responsibility/authority;
- reduction in repeated interpretation questions.

### Integration

- number of tool actions requiring mediation;
- complexity per adapter;
- rate of actions outside the closed action surface;
- reconciliation burden.

---

# 23. Best first real workflow characteristics

The first workflow should **not** be a broad contract like an entire credit agreement or employee handbook.

It should have:

- 20–50 meaningful governance propositions;
- one or two action families;
- 2–4 authority roles;
- some deterministic thresholds;
- some open standards;
- at least one amendment/exception;
- stateful limits;
- actual human judgment currently repeated in practice;
- a tool or simulated tool that can be fully mediated.

Good examples could include:

- employee recognition / expense approvals;
- limited procurement approvals;
- vendor onboarding exception workflow;
- narrow access-control exception process;
- travel-expense policy with delegated interpretation.

The important part is not the domain.

It is whether the workflow lets us test:

> **Does one human normative decision create reusable future autonomy?**

---

# 24. Recommended foundational build

A greenfield repo remains appropriate.

Suggested name:

```text
sophon-engine
```

Do not turn the previous research repository into the product.

The research repo should remain the evidence/laboratory record.

The product repo should embody only the surviving architecture.

Recommended stack:

```text
Python 3.12
Pydantic v2
pytest
SQLite initially
CLI first
FastAPI later
```

No LLM dependency is needed in the trusted runtime.

The initial product kernel should implement:

```text
source/
semantics/
governance/
authority/
bindings/
runtime/
gateway/
amendments/
audit/
compiler/
```

The compiler can remain partially untrusted:

```text
LLM output -> PROPOSED
```

The runtime should accept only:

```text
RATIFIED / COMPILED authority
```

---

# 25. Final architectural position

The strongest version of Sophon is no longer:

> “AI that reads rules.”

It is closer to:

> **An authority layer that lets organizations progressively turn written rules, human interpretations and precedents into versioned executable constraints on AI agents.**

The AI assists with:

- source decomposition;
- candidate interpretation;
- conflict discovery;
- impact analysis;
- precedent retrieval;
- semantic diff;
- proposal generation.

Humans retain authority over:

- normative settlement;
- new policy;
- exceptions;
- amendments;
- delegated interpretation.

The deterministic kernel owns:

- identity;
- version;
- provenance;
- authority;
- state;
- time;
- arithmetic;
- dependency;
- clearance;
- execution.

This separation is the core technical path.

---

# 26. Final verdict

## Technical path

**VIABLE — CONDITIONAL GO**

The current evidence supports building a prototype.

## What should be built

Not:

> “Upload 500 pages and receive a complete autonomous policy engine.”

Build:

> **A versioned authority repository + ratification workflow + deterministic authorization runtime + execution gateway, with AI acting as a semantic proposal and analysis layer rather than the final authority.**

## What would falsify Sophon next

The project should be abandoned or materially reframed if the real workflow shows that:

1. human interpretation effort is approximately equal to manual policy coding;
2. human interpretations have low reuse/amortization;
3. too few actions become deterministically clearable;
4. required facts are rarely observable at action time;
5. complete mediation is too expensive or operationally unacceptable;
6. organizations see little value in the audit/version history;
7. existing policy engines can deliver essentially the same outcome with less complexity.

## What would validate Sophon

Strong positive evidence would be:

1. one human interpretation resolves many future cases;
2. authority coverage increases over time;
3. changes propagate automatically and safely;
4. reviewers prefer the explicit diff/provenance workflow;
5. a meaningful share of agent actions can execute autonomously because authority is externally enforced;
6. audit reconstruction is dramatically easier than with ordinary agent logs;
7. the cost of adding a new governed action falls as the authority repository compounds.

---

# 27. One-paragraph handoff for a new conversation

**Sophon is an AI-native normative control plane for agents. The original strong thesis — automatically compile arbitrary natural-language rulebooks into correct executable controls — failed repeated real-corpus tests because material rules, branches, scopes and open standards were still missed or falsely determinized. The viable narrower thesis is a proof-carrying authority system: supplied documents are represented with provenance; AI proposes semantic interpretations but cannot create authority; authorized humans can ratify interpretations, implementation rules, exceptions and amendments; those acts form a versioned Git-like normative graph; a deterministic kernel verifies legitimacy, authorization sufficiency, precedence, power type and lifecycle; and an execution gateway binds the exact authorized action/state/policy/tool-effect contract to the actual tool call. K1–K6 adversarial tests hardened this architecture through authority legitimacy, sufficiency, precedence, interpretation integrity, human ratification and execution/TOCTOU. The deterministic kernel now has a technically credible path. The unresolved existential question is economic rather than purely technical: can human interpretation be sufficiently amortized, and can enough real enterprise authority be made observable and executable to create material autonomous-agent coverage? The next step is one real bounded workflow, not more synthetic kernel tests.**

---

# 28. Recommended question for the next conversation

A useful next-conversation prompt is:

> **“Using the attached Sophon technical viability report as the current source of truth, help me choose and design the first real-world workflow experiment. The goal is not to prove the kernel again, but to falsify the business-critical thesis: that authorized human interpretations can be amortized into reusable executable authority and materially expand autonomous agent scope at lower governance effort than manual policy engineering. Be adversarial and define the experiment, instrumentation, success/failure thresholds, workflow choice and minimal prototype.”**
