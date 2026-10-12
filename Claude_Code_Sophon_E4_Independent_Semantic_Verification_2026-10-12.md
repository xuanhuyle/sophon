# Claude Code — Sophon E4: Independently Catch Wrong-but-Plausible Semantic Implementations

**Date:** 12 October 2026
**Status:** QUEUED, NOT TO BE EXECUTED YET. **Execute only after a separate E3.1 branch/PR proves PASS_INTEGRITY_HARDENING.** One worktree/branch for E4, one frozen protocol, STOP after E4.
**Governing:** SOPHON_CHARTER.md v1.1 (especially bidirectional alignment, native semantic layer and honest verification), CLAUDE.md, AGENTS.md, SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md § E4.
**What E4 tests:** Given a **specified and LAB-authorized governing interpretation** and a real native semantic calculation, can Sophon independently detect that a semantically plausible implementation does NOT meet the approved requirement, with an inspectable counterexample? This is **implementation→governance independent verification**. It does not yet test the full forward change lifecycle (E5), reverse drift automation (E6) or persistent audit (E7).

## 0. Gate from E3.1 — do not ignore it

Before any experiment setup, read E3.1's actual `PROTOCOL.md`, `RESULTS.md`, `DECISION.md`, executable evidence and tests from its PR, and check the exact gate. If the outcome is **not PASS_INTEGRITY_HARDENING**, STOP: do NOT build E4 on a verifier known to make false promotions. Report why and the smallest remaining correction. Do not pretend E3's original 54/54 closed temporal applicability or forged-receipt vulnerabilities.

The proprietary programming language is NOT a goal. Keep existing Pydantic/JSON IR and actual dbt/MetricFlow. Reuse E3.1 fresh verifier and its source/semantic trust boundary; do not develop a DSL, compiler, "agent governance platform", signing system or workflow orchestrator.

## 1. Read the repo, preserve earlier data and branch correctly

Read fully from origin/main:
- SOPHON_CHARTER.md, CLAUDE.md, AGENTS.md;
- SOPHON_ENGINEERING_DERISKING_PLAN_2026-10-12.md;
- this E4 prompt.

Read the bounded prior evidence from E0 PR #4, E1 PR #5 with erratum PR #7, E2 PR #6, E3 PR #8, and completed E3.1 PR. In particular:
- E1 B1 is **natively derivable** only with quantity/line-grain assumptions; E1's old substantive PASS was withdrawn.
- E2 discovery was PARTIAL with zero severe errors on six LAB cases; H3 ambiguity and H6 field meaning show why approval/actual authority matters.
- E3 introduced a small typed IR and simulated authorization, but original cached-receipt validator admitted not-yet-effective requirements and self-consistent forged native/oracle receipts.
- E3.1 must have corrected both within its explicit trust boundary.

Check `git status`, existing worktrees and PR heads/merge state. Create `experiment/e4-independent-semantic-verify-2026-10-12` in an isolated worktree from `origin/experiment/e3-1-integrity-2026-10-12` (if still an unmerged draft); otherwise branch from whichever actual commit contains E3.1, and document the change. Work solely in `experiments/E4_independent_verification/`; no E0/E1/E2/erratum/E3/E3.1 history rewritten, no production mutation. Open a **draft stacked PR** targeting E3.1 branch if unmerged.

Pinned third-party source remains `behramkorkut/Governed-Analytics-Agent` @ `312e97ad192dcef02f688e31edc0a08c6cf4345f` (MIT). Rebuild with E0's locked upstream/dependencies. Real metric queries must run through installed `mf` against actual DuckDB rows. Dummy, manually invented query output or plain SQL standing in for native MetricFlow is prohibited.

## 2. The exact question and most dangerous tautology to avoid

We want to test the gap between:
- **WHAT IS REQUIRED:** an approved LAB specification, grounded independently in source clauses and explicit simulated approvals.
- **WHAT IS IMPLEMENTED:** an actual native MetricFlow metric, filter, semantic model or proposed native query using dbt lineage and rows.
- **WHAT THE INDEPENDENT REFERENCE EXPECTS:** computed from source rows by a separate formula, using the frozen approved business meaning, not blindly derived from the candidate implementation.

**Never generate the oracle by parsing the candidate's query, copying its result, or accepting its own claim about approved meaning.** The reference meaning + expected behavior must be frozen BEFORE candidate mutants are evaluated. The candidate cannot alter the approval/authority roster, trusted source hash, expected clause interpretation or evaluator's reference execution.

This is a tiny software-engineering check of **bounded semantic conformance**, not proof of real legal/regulatory compliance, true customer data, security against the verifier being compromised, or correctness outside tested populations.

## 3. Two frozen LAB-authorized policies, no new contract interpretation

Reuse only E3 lab policy records S1 and S2 and their simulated *valid* approvals, as clarified by E3.1. The approved readings must be fixed, separately hashed from the candidate implementation and not selected by an LLM:

**P1 — Derived line-price threshold:** Eligible yearly revenue sums completed order lines where *charged unit price >= 100*; source time = order date. Existing correct native witness via MetricFlow metrics at sales-line grain. The equality is valid only with proven guards (quantity positive; revenue=q×unit price exactly; line id unique; exact types and line-grain comparison). Do not silently accept a derivation when guards are absent or fail.

**P2 — French-market revenue:** Eligible yearly revenue from completed orders assigned to *customer* country = France, **not store country**, under explicit LAB_SIMULATED interpretation. The differing store-country reading is an intentionally plausible wrong binding. Do not pretend a real policy owner selected this meaning in an actual company.

Each approved spec should list exact normative predicates, comparison operators, time grain, source provenance/approval identifiers, valid data population, and expected independently computed results. Baseline native MetricFlow should reproduce the E3 S1/P2 independent row-based oracles, subject to fresh identity and E3.1 guards. A passing number without correct population/row membership is insufficient.

## 4. Minimal precommitted mutation matrix

Prepare a short **frozen** set of *at least SIX* variants: two correct controls, at least three plausible wrong implementations, and one observational/authority control. Keep changes in disposable copies of a pinned dbt project, semantic YAML, native query specs and/or source data. At least **TWO wrong variants must alter the actual executable native semantic configuration or dbt model** and be exercised through rebuilt dbt/MetricFlow—not merely change a JSON label, result CSV or mocked query receipt.

Examples to choose and validate **before freeze**:
- **M1 correct P1:** original line-grain derivation with guards and native query.
- **M2 correct P2:** customer-country approved reading, native query.
- **M3 P1 wrong boundary:** `> 100` instead of `>= 100`. A random source dataset might have no exact-100 price, so **pre-register and create a controlled disposable raw-row boundary fixture with actual `unit_price=100.00` and positive quantity**, rebuild the native warehouse from these inputs, and independently recompute the row oracle. Do not claim a failure detectable if no data distinguishes the predicates.
- **M4 P1 wrong filter:** a plausible status substitution (`status != 'cancelled'` vs `status = 'completed'`) or missing status, so returned orders inflate the amount. Modify an actual native semantic YAML metric filter or native implemented query in a disposable project; verify rows change and record counterexamples.
- **M5 P2 wrong country:** store-country instead of approved customer-country, both producing valid native results on the pinned data. Prefer a disposable semantic binding/model alteration where feasible; if only a query/spec mutation is possible, label it transparently.
- **M6 innocuous equivalent refactor:** rearranged but truly equivalent native query/semantic expression (or benign no-op metadata edit) should NOT be labelled a substantive violation if actual meaning/behavior remains equal. Require an actual native execution and independent source comparison, not just accept a cosmetically changed SQL string.
- **M7 optional negative:** missing/untested required input, stale source/semantic version, absent approval or wrong effective-time context yields NOT_VERIFIED/NOT_APPLICABLE rather than an incorrectly asserted implementation mismatch or VERIFIED.

Do not pad the test suite with 50 copies of the same error. Include **at least one wrong implementation whose total agrees accidentally on the original dataset** yet differs under an independently introduced discriminating dataset or row-level membership check. This forces evidence beyond convenient headline-year totals.

**If a specific YAML/dbt mutation cannot be run natively on the pinned stack**, report the limitation and choose a different genuine executable native mutation; do not pretend an untested mutation executed. Use at most one alternative mutation per failed candidate before marking a blocker/partial.

**Counterexample requirements:** for every scored wrong variant, record at least one specific offending source line or order ID, input field values, expected inclusion/amount, actual native behavior and source-to-native lineage. For a wrong binding with plausible numeric totals, verify on row-grain IDs or a controlled discriminating row dataset rather than relying on aggregate comparison alone.

## 5. Freeze procedure before scoring

Before implementing the E4 detector or running scored mutations:
1. Inventory E3.1 approved source/IR and native semantic capabilities; document baseline.
2. Freeze `PRIOR.md`, `PROTOCOL.md`, a readable `REFERENCE.json` grounded in raw sources and approved lab interpretation, variant list and frozen expected decision gates in `VARIANTS.json`, oracle method and discriminator-fixture construction. Log exact source provenance.
3. Commit and push protocol + reference hashes before scoring; capture freeze commit and file hashes, avoiding self-referential commit files.
4. Clearly distinguish **pre-freeze feasibility checks** from scored candidate execution. If a selected mutation cannot exercise native semantics, replace it before freezing and document selection bias.
5. Only after freeze write minimal checker/scoring wrapper and run the candidates. No changes to expected classifications after observing output. Keep first failures and all corrections separate.

The same engineer is designing references and mutations, so this is **not independent case authorship**. Independence means *separate frozen approved reference / oracle from candidate implementation*, not third-party adjudication.

## 5A. CRITICAL E3.1→E4 integration trap: baseline replay is not candidate inspection

E3.1's `src/e31.py::fresh_check` explicitly calls `trusted_reading(...)` and runs **the trusted reference reading's native query on a rebuilt pristine warehouse**, then compares a candidate's *recorded receipts*. This is correct for E3.1's purpose (detect poisoned receipts), but **it does not inspect an altered actual MetricFlow implementation**. An E4 harness that simply calls E3.1's fresh verifier and claims it detected a wrong implementation has not performed E4.

For E4, the **implementation under inspection must be independently instantiated from the actual mutated semantic YAML/dbt code and genuinely executed by MetricFlow on its own controlled warehouse/semantic manifest**. The approved interpretation and independent raw-data oracle must remain anchored to the original LAB governing source and explicitly frozen authority. These may have different hashes: an altered candidate semantic manifest is *expected*, not by itself evidence of business nonconformance.

Therefore:
- Run and record the **candidate** metric/query against the **candidate** native semantic stack; record the compiled SQL, manifest fingerprint, actual results and lineage. Prove the mutations were really effective. Separately run the **reference** calculation from source rows and approved meaning.
- Do not call a mismatch of candidate manifest hash versus the pristine E3.1 manifest a substantive `NONCONFORMING_IMPLEMENTATION` finding. That mismatch can indicate a changed version or an unverifiable provenance claim; only an independently demonstrated behavioral/semantic mismatch with an identified source-row counterexample establishes substantive nonconformance.
- If a candidate metric is renamed or its declared filters change, do not quietly substitute the E3 trusted query in place of the candidate. Conversely, changes that preserve approved behavior should not be rejected solely because their semantic artifact hash differs.
- For the **two mandatory native YAML/dbt mutations**, inspect the actual resulting compiled native SQL and source-row membership. If the candidate executor cannot run separately from the pinned pristine verifier, return PARTIAL/BLOCKED according to the frozen rules, **never PASS**.
- Treat E3.1 as a source/authority/time/receipt **foundation**, not the semantic conformance detector itself. A candidate implementation is not "verified" simply because its pristine predecessor was.

## 6. Verification process and abstention

For every variant:
- Load the **trusted, approved LAB IR** and source identity. Enforce source applicability and known_at/effective_at separately, via E3.1.
- Evaluate meaning, scope, units, mathematical guards, native semantic identities and the exact implementation being checked. Do not silently import the correct query from reference into the candidate being tested (that would conceal a wrong implementation).
- Read native metric definitions/lineage, execute actual candidate via `mf` in its independently instantiated disposable environment, collect query, compiled SQL, actual rows, run hashes and exit code.
- Recompute **approved intended result from source rows independently**, using frozen oracle code/logic without depending on candidate semantic transformations. Verify the source snapshot's identity and version.
- Compare totals AND row populations/membership at the appropriate grain where possible. If a metric cannot expose the necessary grain, disclose what cannot be observed and return PARTIALLY_VERIFIED/UNVERIFIABLE, **not** a false VERIFIED.
- A wrong-but-native-executable result should produce `NONCONFORMING_IMPLEMENTATION` with a concrete counterexample; a correct baseline should produce `VERIFIED_FOR_LAB_CHECKS`; a benign refactor should produce `NO_MATERIAL_DRIFT_FOR_CHECKS`; unobservable/missing evidence should produce `NOT_VERIFIED` or `INCONCLUSIVE`.
- Separately report **execution failure**, **provenance/approval failure**, **data guard failure**, **numeric/membership mismatch**. No generic "contract violated" from a failed CLI command. Do not equate a metric's output with actual downstream BI/agent consumption.

The checker must not award a PASS by loading the expected status field from `VARIANTS.json`; frozen expectations are for the independent scorer. Do not silently modify the candidate implementation or gold data to make it pass.

## 7. Mandatory adversarial checks

- **Wrong metric but plausible amount:** revenue vs gross profit / units vs orders chosen as an extra control only if it is non-redundant.
- **Wrong filter with same baseline total:** independently discriminating fixture must expose difference; passing aggregates alone cannot imply identity.
- **Wrong customer/store join:** must detect with actual source row counterexample, not merely name mismatch.
- **Source/historical context mismatch:** wrong governing version or stale source snapshot cannot be verified.
- **Approval is not code evidence:** even an approved reading with successful query must fail if actual native implementation deviates from the approved logic.
- **Native result poisoning:** a rehashed, self-consistent false pair of stored receipts cannot produce a verified status; inherit E3.1 independent re-execution.
- **No false drift:** semantically equivalent harmless implementation changes must be accepted within measured coverage.

## 8. Frozen E4 decision gate

Report exactly one:

- **PASS_INDEPENDENT_VERIFICATION_SIGNAL:** E3.1 prerequisite PASS; correct baseline and harmless refactor accepted **only for recorded checks**; all preregistered wrong executable native implementations detected with independently grounded counterexamples (including > vs >= at exact 100, completed vs not cancelled, customer vs store); at least **two actual native semantic/dbt model mutations**, with rebuilt compiled SQL/rows; no wrongly verified corrupted/proxy/unknown/snapshot-mismatched case; fresh-process independent rerun matches; protocol unmodified.
- **PARTIAL_INDEPENDENT_VERIFICATION:** at least one significant wrong native implementation is independently detected, and no unsafe false verification occurs, but coverage/refactor controls, native mutation quota or counterexamples are incomplete. State what is missing.
- **FAIL_FALSE_ASSURANCE:** a wrong-but-plausible implementation is falsely reported VERIFIED/NO_MATERIAL_DRIFT in a scored distinguishing case, or a missing approval / source fact is promoted through execution alone.
- **FAIL_FALSE_ALARM:** the declared semantically equivalent control is incorrectly classified as NONCONFORMING with confidence, when independent baseline evidence shows it is equivalent for the tested scope. If simultaneously unsafe false assurance occurs, FAIL_FALSE_ASSURANCE takes precedence.
- **BLOCKED:** verified pinned runtime or independent raw-data oracle cannot execute under the bounded attempts, or E3.1 did not pass.
- **INCONCLUSIVE:** preregistered truth/counterexamples, source identity, required approvals or evaluator independence are compromised; a replay of cached receipts alone is not proof.

Do not generalize from half a dozen lab variants to production detection rates, legal compliance, novelty, real customer value, or "AI-native defensibility."

## 9. Budget / deliverables / stop

ONE pinned environment and controlled copies, TWO lab-approved clauses, about 6–8 meaningful variants, no paid AI calls, no rewriting other experiment directories, no general DSL and no production lifecycle. If native semantic mutation turns out to require a major framework overhaul, STOP/PARTIAL rather than build it.

Under `experiments/E4_independent_verification/`:
- `PRIOR.md` / `PROTOCOL.md` / `REFERENCE.json` / `VARIANTS.json` and freeze manifest.
- Minimal native mutation/data-fixture and comparison scripts plus tests; preserve independently computed source-row oracle.
- `evidence/`: original and mutated YAML/dbt diffs, compiled SQL and actual MetricFlow receipts, source versions, independently computed output, ID-level counterexamples, negative/benign controls and fresh-process reproduction.
- `RESULTS.md` / `DECISION.md` / `README.md` (exact actually executed commands; Windows UNTESTED unless run).

Commit freeze before scored mutants, then implementation/results. Push and open a draft PR stacked on E3.1's branch. Do not merge automatically.

Final user report: E3.1 prerequisite verification, actual stacked branch/PR, protocol/result commits, approved lab clauses, which wrong native implementations were caught, concrete counterexamples, false assurances/false alarms, one verdict, and one cheapest technically justified next experiment (E5 forward governed change only if E4 supports continuing).

**STOP AFTER E4.** E4 independently checks actual semantics against the approved LAB reference; it does not propose, approve, deploy or audit a governed lifecycle.
