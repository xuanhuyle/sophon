# Claude Code — Sophon E3: Does a Minimal Formal Governance IR Actually Add Guarantees?

**Date:** 12 October 2026
**Status:** SECOND SEQUENTIAL TASK. Execute **only after** the E1 expressibility erratum has been completed and its native derivation confirmed. E3 must have its own worktree, protocol and draft PR.
**Governing:** SOPHON_CHARTER.md v1.1, CLAUDE.md, AGENTS.md and SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md.
**Prior evidence:** E0 PR #4, E1 PR #5, E2 PR #6, plus newly completed PR from `Claude_Code_Sophon_E1_Expressibility_Erratum_2026-10-12.md`.
**Primary uncertainty R4:** Can a small, typed, target-independent governance intermediate representation (IR) preserve the difference between **approved meaning**, **technically executable native behavior**, and **unresolved meaning/evidence**—and mechanically prevent a false "verified" promotion?

## 0. Non-negotiable separation of concepts

Sophon is not writing law and is not replacing the customer's semantic layer.

- **Authoritative text**: what the governing source actually requires; in this E3 experiment all clauses remain LAB_AUTHORED, with no external organizational approval.
- **Interpretation**: one candidate understanding of the source, potentially ambiguous or awaiting authorized judgment.
- **Normative specification**: formal conditions, units, scope, date and dependencies expressing an APPROVED interpretation.
- **Binding**: where a named business concept is represented in an existing semantic model or source data, including conditional derivations and physical lineage.
- **Execution**: real native MetricFlow queries/results, which can run correctly even if the interpretation/binding is wrong.
- **Evidence / status**: precise coverage and bounded checks; "verified" never means legally compliant or deployed.

An LLM may propose anything but **cannot grant its own authorization**. An executing query never authorizes a semantic equivalence. A lab-simulated approval only authorizes a **declared hypothetical meaning** in the lab; it does NOT prove authentic field meaning, legal interpretation or sign-off.

**NO proprietary language, parser, compiler, autonomous policy reader, policy graph, new event store, multi-agent system, dashboard, or production deployment.** Begin with plain JSON and JSON Schema or Pydantic; choose one simple implementation. Do not write a novel language syntax. Reuse E0 native adapter; reuse E1/E2 oracle and lineage/provenance helpers where appropriate.

## 1. Read evidence, status and branch dependencies

Read in full:
- origin/main:`SOPHON_CHARTER.md`, `CLAUDE.md`, `AGENTS.md`, `SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md`.
- origin/main:`Claude_Code_Sophon_E3_Formal_Governance_IR_2026-10-12.md` (this file).
- E0/E1/E2 PROTOCOL.md, RESULTS.md, DECISION.md, relevant source/semantic evidence and implementation, including E2 H3/H6 score, its **frozen reference flaw**, and E1 B1's original **dimension-only expressibility flaw**.
- The actual `experiments/E1_expressibility_erratum/{ERRATUM,PROTOCOL,DECISION}.md` and evidence from the erratum branch. Confirm a genuine native reproduction and an independently evidenced positive-quantity / line-grain guard.

**Gate before any E3 implementation:** If the erratum does not have `CONFIRMED_E1_ERRATUM`, do not assume that B1's derived expression is sound. **STOP/BLOCK E3** (or propose a narrower separate protocol) rather than silently declaring this premise valid.

Check `git status`, worktrees and PR #4/#5/#6/erratum state. Protect all uncommitted user work and existing experimental history. Create a new isolated worktree/branch:
`experiment/e3-governance-ir-2026-10-12`
from `origin/experiment/e1-expressibility-erratum-2026-10-12` (unless already merged, then verify the landed head and document the changed topology).

Open a **draft stacked PR**, targeting the erratum branch if unmerged. Work **only** under `experiments/E3_formal_ir/`; never edit earlier frozen protocols/results, prior PRs, the charter or the original broad G1 instructions. The recent prompts on main can be read with `git show origin/main:...` even though stacked experiment branches may precede prompt commits.

## 2. Concrete requirements to represent (not a language design exercise)

Use the same pinned public MIT upstream:
`behramkorkut/Governed-Analytics-Agent` at `312e97ad192dcef02f688e31edc0a08c6cf4345f`, native MetricFlow/DuckDB, synthetic rows. Pin hashes, package versions and metric definitions. Each scenario is a distinct bounded laboratory specification, not a new commercial use case.

**S1 — Mathematically derived, not directly exposed (E1 B1):**
"Completed-order revenue, counting only lines with charged unit price >= 100."

- Requirement includes quantity, price, revenue, completed status, year and threshold.
- `unit_price` is not a directly exposed semantic dimension, but the E1 erratum may demonstrate a **native metric-filter derivation** from revenue and quantity at sales-line grain.
- IR must distinguish `DIRECT_NATIVE_EXPOSURE` from `DERIVED_NATIVE_EXPRESSION` and capture derivation dependencies, entity grain, mathematical guard `quantity > 0`, data/source calculation assumptions, native compiled query reference, test evidence, and any unsupported scope.
- A derivation without a validated guard is **NOT_VERIFIED**, even if the expression executes. It must not be approved for arbitrary zero/negative quantity rows just because it works in this synthetic dataset.
- Check actual native MetricFlow result against an independent raw-data oracle. Success is **bounded expressibility + verification**, not proof of general equivalence.

**S2 — Normative ambiguity (E2 H3):**
"Revenue from completed orders attributable to the French market."

- Technically plausible bindings: French customer country vs French store country, yielding different valid native results.
- Until one reading is explicitly chosen and hypothetically authorized, the IR must preserve both alternatives as candidates and mark `UNRESOLVED_INTERPRETATION`, **even if each executable query works**.
- Add a **SIMULATED approval event** scoped to requirement version, exact selected reading, approver role, observed/approved time and effective time. Under a lab-declared authority roster, validate the approval record and choice; separately verify the *chosen* native interpretation against independent expected data.
- The choice cannot auto-approve itself; invalid approver, wrong scope, missing approval or conflicting simultaneous choices must block promotion. Approval of one choice must not rewrite the alternative as historically false.

**S3 — Candidate data field, unjustified meaning equivalence (E2 H6):**
"Number of online orders from customers whose country of **residence** is France."

- Native `customer__country` exists and computes a matching numeric query, but the pinned source calls it just `country`, **not authoritatively 'country of residence'**.
- IR must represent `CANDIDATE_BINDING` + `NOT_ESTABLISHED_SEMANTIC_EQUIVALENCE` separately from the known native query and data lineage.
- Under no approval, disallow `VERIFIED` despite a successful query; permit "technically executable with unresolved meaning".
- A lab-authorized explicit equivalence (`customer.country := residence country`), with *simulated, correctly scoped authorization*, may enable **VERIFIED_FOR_LAB_ASSUMPTIONS_AND_SPECIFIED_CHECKS** only if native results and independent raw-row calculation agree.
- Merely changing a status field from pending to approved without a valid external-to-the-candidate approval record must fail. Explicitly state that a simulated choice is NOT evidence the upstream field genuinely means residence in any real deployment.

**S4 — Missing required authoritative source (E1 B2 / E2 H1):**
"Completed-order revenue for orders independently confirmed settled by a payment processor."

- No designated payment-settlement fact in the bounded upstream estate.
- A simulated approval of a guessed binding (`status='completed'`) cannot convert that into independent settlement evidence.
- Neither type validity, native execution, nor a business person's *approval of an interpretation* is sufficient to manufacture an absent data source. IR must stay `MISSING_REQUIRED_FACT` / `UNVERIFIED` unless source coverage genuinely changes (which is out of scope).

All statements about business "authority" use a tiny **LAB_SIMULATED** roster and explicit externally supplied approval objects. There are no actual legal interpretations or signatories.

## 3. Small IR shape and validation behavior

Build an explicit, versioned **typed JSON record** with only fields demanded by S1–S4:

- `governing_source`: source ID, content hash, requirement clause ID/version, `observed_at`, `effective_from` and provenance label `LAB_AUTHORED`.
- `requirement`: typed atoms with units, value, population, exceptions and grain (only operators used here). Preserve original text and each atom's span.
- `interpretation`: `PROPOSED`, `UNRESOLVED_INTERPRETATION` or `LAB_APPROVED`; chosen reading and alternative references; list of unresolved questions.
- `semantic_binding`: candidate native object(s), semantic and physical lineage refs, `DIRECT` / `DERIVED` / `CANDIDATE_EQUIVALENCE` / `MISSING`, source authority designation with evidence, and derivation/assumptions/guards when needed.
- `approval_evidence`: separate lab-external approval object scoped to **source hash, requirement version, exact interpretation/binding claim, approver role, known_at and effective_at**. Proposed records cannot approve themselves. Avoid real-person data, mock signatures or claims of actual identity verification.
- `verification`: source/semantic revision, native query reference and recorded output, independent expected-behavior reference, coverage, missing predicates, observed status; status is a **computed output**, NOT an arbitrary untrusted input flag.

Avoid writing a general expression interpreter. The structured operators need only represent the small arithmetic/Boolean cases and reference existing native MetricFlow behavior. Formalize *what was approved* before binding it.

**Validate two different things**:
1. **Structural consistency:** schema/type checks, source/binding identity, unresolved alternatives, missing fields, dimensional/unit compatibility, source hash/version dates, approval scope and actor against the simulated roster, positive-quantity guard for S1.
2. **Bounded behavioral evidence:** native MetricFlow query (or trusted fresh receipt with hashes as explicitly declared) matches independently computed expected outcomes **for the selected, approved lab meaning**.

If only (1) holds, never label substantive behavior VERIFIED. If only (2) holds, never label authorized meaning established. If either lacks evidence, fail closed with reason and missing coverage, not "compliant".

Enforce **known_at versus effective_at** as separate fields (no impossible future-known approval in an as-of evaluation); no historic event database or generic bitemporal engine is required. For two-time-axis tests use frozen records and an explicit evaluation timestamp.

## 4. Concrete preregistered test cases (the decisive part)

Freeze `PRIOR.md`, `PROTOCOL.md`, a small case/approval fixture set with expected outcomes, source/oracle hashes and test plan **before** implementing the E3 validator or scored checks. Freeze commit SHA + file hashes; protocol file cannot contain its own commit hash. This is a controlled mechanistic test informed by past failures, **not blinded legal interpretation**.

Mandatory tests:
1. **S1 positive:** existing MetricFlow-derived filter + proven quantity>0 and correct line grain + stable source identity + independent raw-row oracle gives bounded VERIFIED status.
2. **S1 invalid guards:** remove positive-quantity evidence or corrupt the derived expression/lineage; execution alone cannot yield verified. Include a zero/negative quantity counterexample or direct numeric disproof outside the proven scope.
3. **S2 no approval:** both distinct native French-market readings technically execute; no full verification without one authorized interpretation.
4. **S2 valid simulated approval:** approved reading for this clause+revision+effective window, actual native query and independent oracle match; only that reading becomes *verified for lab assumptions*, not legal approval.
5. **S2 approval attacks:** approve the wrong clause/version/source hash, choose two conflicting readings, approver not in roster, or use an approval not yet known at the claimed historical time; all must block.
6. **S3 no equivalence evidence:** correct numeric query for France but field meaning unestablished → NOT_VERIFIED.
7. **S3 scoped LAB approval:** a simulated externally provided equivalence record allows bounded status promotion **only with native/independent evidence**. Revoke/remove approval and immediately withdraw the promotion.
8. **S4 missing settlement source:** a fake approval or `status='completed'` proxy cannot override unavailable independent settlement evidence. The machine-readable list of uncovered predicates is non-empty.
9. **IR structural negatives:** mismatched units; nonexistent semantic object; undefined predicate; invalid temporal ordering/source version; altered source hash; missing mandatory approval evidence. Must return precise machine-readable failures.
10. **Native and oracle negative control:** change an underlying value or recorded query to plausible-but-wrong result; independent check must reject.
11. **No history rewriting:** old unresolved record and later simulated approval record remain distinguishable; querying as-of the earlier `known_at` cannot see future simulated approval.
12. **Independent fresh-process replay:** from committed fixtures, schema, native/independent receipts and no Claude conversation context, recompute the case statuses and explicit rejection reasons; disclose the trust limits of any cached receipt.

Crucial **comparison against E1/simple untyped recording**: Provide **at least three concrete, previously possible false promotions or invalid states** that ordinary unvalidated prose/JSON could store (e.g., metric executed ⇒ legal claim approved; missing approval ⇒ “approved”; wrong source revision ⇒ “verified”), and demonstrate that the E3 typed validator mechanically rejects them. This tests *incremental enforceable value* beyond another set of attractive documentation fields. It is not a claim that no existing validation library or implementation could enforce the same invariants.

Where E1 already detects a class of failure, say so clearly; do NOT claim the same guarantee is unique to E3.

## 5. Strict E3 decision gates

Report one exact conclusion:

- **PASS_IR_GUARD_VALUE:** all four scoped scenarios behave as preregistered; guard/approval/source-history mutation controls reject every invalid promotion; native/independent results substantiate bounded VERIFIED statuses; at least three material invariants are mechanically enforced and E1 comparisons honestly distinguish new from reused guarantees; fresh process reproduces outcomes.
- **PARTIAL_IR_GUARD_VALUE:** some useful invariants are demonstrated but a declared scenario is unsupported, *without* any false verified promotion; specify the smallest missing property.
- **FAIL_UNSAFE_IR:** an unresolved governing meaning, unsupported semantic equivalence, missing required source, invalid scoped approval or failed numeric check is labelled verified.
- **FAIL_NO_INCREMENTAL_VALUE:** after implementation the IR only stores free-text/flags or duplicates E1 checks, providing no consequential additional enforceable property on scoped cases.
- **BLOCKED:** prerequisite erratum failed, native stack cannot run, or required source/oracle is unavailable under the minimal setup budget.
- **INCONCLUSIVE:** frozen reference, approval fixture integrity or independent oracle is not credible.

These are scoped engineering verdicts, not proof that a proprietary language, general contractual interpretation or a business will work.

## 6. Scope discipline, deliverables, stop

- Use a **single typed JSON representation**, a **small read-only validator** and minimal test fixtures. Prefer ordinary Python + JSON Schema/Pydantic + native MetricFlow. Avoid creating a general rules engine or abstract syntax tree library. Reuse pinned upstream and E0/E1/E2 read-only helpers.
- One environment, four cases, the listed adversarial controls. No paid LLM calls, no agent scaffolding, no more exploratory research. **Do not automatically solve S2/S3 business meaning**.
- E3 may *record* a manually supplied hypothetical approval for a controlled test, but cannot initiate, certify or infer a real one.
- No change to dbt/MetricFlow definitions. No forward transposition, no reverse change lifecycle and no production audit store in E3; E4–E8 remain separate.

Work only under `experiments/E3_formal_ir/`:
1. `PRIOR.md` — E0/E1/E2 + erratum evidence, observed/inferred/assumed and what E3 cannot prove.
2. `PROTOCOL.md` — frozen inputs, exact invariants, acceptance gates, control cases and hashes, with protocol commit before scored evaluation.
3. `schema/` or `models.py` — minimal typed IR; `cases/` — four fixtures and mutation variants; `src/` — validator and run/replay.
4. `evidence/` — native query receipts, source/semantic fingerprints, independent expectations, guard checks, actual validation output and full test logs.
5. `RESULTS.md` — table of states before/after simulated approvals, including explicit **meaning vs computability vs evidence** distinctions and any deviations.
6. `DECISION.md` — one verdict and smallest next technical experiment, E4 independent behavioral verification, only if E3 passes.
7. `README.md` — runnable reproduction commands actually executed; mark Windows UNTESTED unless run.

Push protocol freeze first, then committed execution evidence and test results. Open draft **stacked PR** targeting erratum branch unless it was merged. Do not merge automatically.

Report to owner: exact base/head branch and PR, freeze and final SHAs, IR field names / type constraints, S1–S4 before/after cases and failures, numerical/native proof scope, one gate verdict, and one next step.

**STOP AFTER E3. A formal IR earns its place only by enforcing a guarantee that can fail—never by being a neat new abstraction.**
