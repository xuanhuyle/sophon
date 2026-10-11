# Sophon — Governance Integrity Lifecycle Experiment (execution prompt)

Date: 2026-10-11
Status: executable research instruction; **not** a product specification.
Owner's decision: build and verify the smallest real, useful technical capability before pursuing customer adoption.

## 0. MANDATE — execute, do not simply propose

Work inside this Sophon repository. Read the prior evidence first, select and freeze a valid public-world benchmark, build the smallest testable mechanism if the evidence permits it, run a strong baseline and a controlled comparison, audit the outputs, and record a falsifiable decision. Run tests and commit reproducible artifacts.

Do not return a proposal or another endless research plan. Do not wait for private enterprise access. Public materials must suffice. If a critical dataset or independent oracle is unavailable, report an explicit **inconclusive evidence gate** instead of fabricating it. You may still implement a clearly labelled *non-scored engineering smoke test*; never promote it to evidence of the thesis.

**This is not an instruction to demonstrate that Claude can read contracts, edit YAML, or generate SQL.** Those are already plausible capabilities.

The one hypothesis to test is:

> On a real, versioned governing corpus linked to an organization's pre-existing semantic layer (which already connects to the data systems), can a minimal persistent, evidence-backed governance mechanism improve the correctness and cost of **bidirectional transposition, verification, traceability, and historical audit**, across successive changes, compared with Claude Code + existing native engineering/governance tools?

This is a *bounded kernel* hypothesis, not general enterprise compliance or product-market fit.

## 1. Non-negotiable architecture

Only this canonical boundary:

  authoritative governing corpus (contracts, law, approved policy, amendments)
                  <--> Sophon
                  <--> **organization's existing semantic layer**
                  <--> existing data systems / downstream BI and AI consumers

Sophon must **not** invent a replacement semantic layer, independently reverse-engineer the entire raw data estate, or independently synchronize application code. For semantic requirements, consume and (in a safe branch) propose changes to the *existing* semantic layer; verify results by executing its real semantic interface and the data it already exposes.

Do not equate a generic SQL transformation, a Publicodes rule engine, a YAML file with the word "semantic", or a dbt staging/mart project with a deployed dbt MetricFlow semantic layer. Report the precise interface. A proxy can support a limited engineering test but not full architectural validation.

The original Sophon scope has FOUR inseparable obligations:
1. **TRANSPOSE** authoritative governing changes into correctly proposed semantic-model changes; approvals and deployment remain with authorized humans.
2. **TRACE** each source provision and approved interpretation to the affected semantic object/version, downstream dependencies *that are actually observable*, relevant tests and evidence.
3. **VERIFY** semantic-to-governance alignment when *either side* changes, with reproducible data-backed counterexamples and explicit unknown/partial coverage.
4. **AUDIT** reconstruct as-of governing text, recorded approvals where genuinely present, semantic code/manifest commit, test inputs/results, and why an action was or was not justified. An LLM narrative alone is never evidence.

Distinguish: a model being configured correctly; a verified executed result; and the claim that every downstream agent follows it. An agent consuming a governed metric is an optional thin observability check; do NOT build a new agent runtime or imply downstream behavioral compliance from a passing semantic test.

## 2. Read repo and prevent a repeat of earlier failed experiments

Before implementing anything, read at minimum:
- README.md
- docs/REPORT.md
- docs/DECISION.md
- docs/OWNER_REQUEST.md
- Claude_Code_Sophon_Amendment_Impact_Experiment_Prompt_2026-10-04.md
- docs/jev_assessment/JEV_IMPACT_ASSESSMENT.md
- docs/market_discovery/MARKET_DISCOVERY.md

Inspect whether any later artifacts from the **2026-10-04 blind amendment impact experiment** actually exist (repo, branches, local files); do not claim it ran merely because a prompt exists.

The 2026-09-21 audit showed *no decision-quality advantage* of a custom authority ledger over a disciplined policy-as-code baseline over 138,240 compared decisions. Some earlier tests could not fail. The October 4 prompt isolates **impact discovery**, not the complete transposition / traceability / audit lifecycle.

Write a concise, falsifiable delta vs previous tests in experiments/governance_integrity/PRIOR_EVIDENCE.md. If the earlier experiment already convincingly resolves the current claim, reuse the result rather than duplicate work.

## 3. Evidence acquisition — hard gate before building the scored experiment

Find ONE public-world **matched system**, ideally maintained by the *same* organization, that provides:
A. authentic, dated governing requirements (binding external legal documents or actually approved internal business/metric policy);
B. existing and relevant *real* semantic definitions / metric models;
C. the data or execution interface needed to run the semantic layer, plus at least some downstream consumption evidence if available;
D. authentic historical changes in governing requirements and/or semantic model, with dated commits / PRs / issues;
E. enough independent facts to verify at least some behavior without trusting the same model's generated answers.

Prefer true dbt MetricFlow semantics, or an actual Snowflake/Databricks semantic interface if publicly reproducible. Keep the original semantic model as-is. No fixture authored after reading its future change may masquerade as a historical pre-change implementation. Historical version pinning matters.

Investigate at most THREE credible candidate systems. Starting leads (NOT pre-approved complete matches):
- https://github.com/kina2711/green-sm-nyc-mobility-intelligence — verified dbt SQL + docs/METRICS.md governance procedure; **NOT** yet verified to have an actual dbt Semantic Layer or legal-to-semantic history. Do not silently upgrade it.
- https://github.com/behramkorkut/Governed-Analytics-Agent — explicitly claims actual dbt + MetricFlow + downstream AI agent; source data are *synthetic*, and a matched legally authoritative corpus/history is **NOT** established.
- https://github.com/betagouv/mon-entreprise — authentic law-to-Publicodes model and real historical changes; **Publicodes is not a dbt/BI semantic layer**. Relevant reform: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; PRs https://github.com/betagouv/mon-entreprise/pull/4101 and /pull/4119, subsequent issue /issues/4294. This is a narrower legal-to-executable-rules transfer case, NOT direct proof of the semantic-layer hypothesis.

Further leads are permitted within the three-system limit, but only if demonstrably stronger. Review primary files/commits rather than project marketing. Do not combine two unrelated organizations' artifacts and call the result one authentic matched governance system.

Write experiments/governance_integrity/EVIDENCE_GATE.md with a five-column checklist A–E, source URLs, exact immutable git SHAs / original document dates, available temporal episodes, licensing/usage constraints, and every missing element.

**Gate outcomes:**
- **MATCHED / GO:** A–E available for at least one material change and a defensible as-of replay. Proceed to full experimental workflow; multiple independent changes are required before any broad maintenance advantage is claimed.
- **PARTIAL / LIMITED:** Genuine but missing key requirements (e.g. internal metric policy instead of external law, only one change, no real semantic runtime, no independent truth). Build only the narrow capability that can genuinely be checked; label result limited and ineligible for full-thesis CONTINUE.
- **NO MATCH / INCONCLUSIVE:** No authentic, independently assessable pair. No scored Sophon claim. Deliver a specific evidence gap and, at most, a minimal non-scored integration smoke test. Do not spend the budget creating a giant fictional enterprise.

A missing private governance corpus is NOT a reason to ask the owner for data. Work with public material and declare exactly what can/cannot be concluded.

## 4. Preregister before solutions or labels are seen

Write experiments/governance_integrity/PROTOCOL.md BEFORE coding or viewing subsequent changes used as answers. Commit and hash its content. Specify:
- frozen historical dates and input commit SHAs (normative corpus and semantic layer);
- evidence available to each arm at decision time (no hindsight);
- authentic change episodes and which originate from governing corpus vs semantic implementation;
- held-out unknown, irrelevant/no-op, time-dependent, exception, and missing-evidence cases; synthetic perturbations MUST be segregated as robustness diagnostics;
- allowed tools, prompts, model/version, budgets, and number of runs;
- independent reference/oracle construction and how disagreements or legal ambiguity are labelled UNRESOLVED;
- outcome metrics and stopping rule.

The observed code fixes in historical PRs are **not** infallible legal gold: distinguish contractual/statutory meaning, historically merged code, tests, and subsequent bug reports.

Never let one model write the legal interpretation, the code, and the only tests and then pronounce itself correct. An independently defined reference should use genuine dated primary texts + manually checkable deterministic assertions or pre-existing tests with stated limitations. If independently assessable correctness cannot be established, score *evidence integrity and uncertainty*, not legal compliance.

Do not manufacture fake approvals. A merged PR is a recorded engineering merge, not by itself a legal sign-off.

Prevent leakage: separate build, solver and scoring contexts / worktrees. If you cannot guarantee isolation within one session, prepare sealed inputs and fresh-session scripts and mark scored runs **NOT EXECUTED** until they genuinely run. Hidden labels must be inaccessible to both solver arms, not merely politely hidden by instruction.

## 5. Experimental arms: same tools, one clearly isolated intervention

A — **Strong baseline:** Claude Code with governing corpus, same historical semantic model, Git history available up to t0, native semantic/dbt tooling, tests, documented business definitions, ordinary markdown/JSON records of its choosing. Allow it to maintain its own persistent documentation through changes. Do not handicap it with one-shot prompting.

B — **Sophon kernel:** Same model, inputs, tools, budget and ability to iterate; add ONLY a tiny mechanism preserving evidence-backed, versioned requirement <-> semantic-object dependencies and triggering reassessment when either side changes. Capture setup + validation + ongoing maintenance cost.

Before implementation specify the one thing B can do that A does not do as reliably or as cheaply. If that cannot be articulated concretely, do not create a new component; record **NO JUSTIFIED DIFFERENTIATOR**.

Do not allow extra LLM calls, hidden ground truth, prefilled correct mappings, or extra human judgments for B without counting them. Compare using identical authorized read access. Only semantic-model edits in disposable branches, NEVER production or upstream.

## 6. Required tasks in sequence (same matched system)

T0. **INITIAL BINDING:** Discover candidate provision-to-semantic dependencies, separate VERIFIED / INFERRED / UNKNOWN; capture source location, git SHAs and approval provenance (or explicitly absent).

T1. **FORWARD TRANSPOSITION:** Replay a genuine dated governing change. Propose an appropriate change to the existing semantic definition; run its native syntax/build checks and executable checks on data; show changed outputs and reference expectations or abstain. Capture source -> change -> tests -> evidence.

T2. **REVERSE CHECK:** Replay a genuine semantic-layer change with unchanged governing text. Determine whether it is a harmless refactor, mismatch, legitimate independent policy change, or unresolved. Don't report all diffs as violations.

T3. **CHANGE MAINTENANCE:** After at least one more authentic independent change, assess whether persistent validated links stay accurate, go stale, or cost more to maintain than rediscovery. If not enough genuine sequential changes exist, label the maintenance thesis **UNTESTED**.

T4. **AS-OF ADVERSARIAL AUDIT:** Independently attempt to reconstruct a randomly selected historical requirement's source version, interpretation status, semantic commit/version, derived dependencies, tests/results and known limits using only each arm's preserved artifacts. Include one missing-approval or missing-source case: the correct answer is "no evidence recorded," never a fabricated authorization. Verify evidence by checking file content/hash and replaying checks; do not credit mere citation-shaped text.

Also record COVERAGE: enumerate material governing requirements in the bounded selected corpus and classify FULLY_OBSERVABLE / PARTIALLY_OBSERVABLE / NOT_OBSERVABLE via this semantic layer. Do not cherry-pick only fully representable rules to claim broad governance.

T5. **OPTIONAL THIN CONSUMER:** If an actual downstream BI/agent consumer is present and simple to run, demonstrate it consumes the newly governed metric through the existing semantic interface and receives the expected value after an approved change. This is NOT proof of all agent behavior.

## 7. Minimum code, no platform construction

If the evidence gate passes, implement a disposable CLI or scripts under experiments/governance_integrity/ ONLY, with:
- a very small, plain JSON/SQLite provenance store keyed by primary source/version and semantic object/commit;
- one adapter to read the source semantic catalog/manifest and invoke the *actual* semantic runtime;
- diff-driven revalidation for linked objects on corpus OR semantic changes;
- an evidence report and "as-of" audit report;
- tests that tampering with cited evidence, changing effective dates, removing approvals, or changing semantic logic correctly invalidates/fails checks.

Use existing parsers, Git, dbt/MetricFlow where appropriate. No new DSL, ontology, graph DB, agents, web UI, policy gateway, or enterprise connector suite. A hash proves the content is unchanged, **not** that it is correct, complete or authorized.

An LLM may PROPOSE semantic links and edits. Critical claims must be independently supported by executable reference checks or clearly marked as unverified. Requirements outside the semantic layer's scope must remain out-of-scope/unknown.

## 8. Success and failure criteria — no post-hoc threshold changes

Do not pretend 3–5 public cases establish statistical reliability or production safety. Report exact numerator/denominator and case-by-case errors, not inflated percentages.

A *meaningful bounded positive* requires **all**:
1. at least one authentic forward episode **and** one authentic reverse or independently documented implementation-origin episode in one matched system; no future-data leakage;
2. no confidently false material legal/semantic conclusions in scored episodes; unknown explicitly used when necessary;
3. correct reproducible transposition for scored deterministic requirements, or clear abstention on unresolved meaning;
4. an auditable evidence chain for every claimed verified link, including valid historical date/version and accurate representation of missing authorization;
5. the preserved-link mechanism improves **a predeclared** outcome (fewer material misses / better evidenced audit / lower total measured human+model setup/maintenance cost) vs the competent baseline on held-out authentic changes;
6. real native semantic execution against data, not just textual matching or yaml validation.

If any key evidence item is absent, output PARTIAL / INCONCLUSIVE; do not declare thesis victory.

**STOP the differentiated kernel** if a valid, informative comparison shows the competent baseline performs equally well or better after full costs, or maintained links cause stale false assurances. A failed integration setup or inadequate public benchmark is NOT a negative verdict on the global thesis.

Record separately:
- material impact recall / false-safe cases and abstention;
- source grounding/evidence integrity and audit reconstruction;
- forward semantic execution vs independent expected behavior;
- time/cost for initial linking, later changes, correction, evidence production and audit;
- native tooling vs B advantage;
- unassessed corpus surface;
- real vs synthetic cases.

If no independent human timing is available, report measurable work proxies (calls, tokens, files reviewed, wall-clock for machine execution) **without** claiming a reduction in human labor.

## 9. Outputs, stop conditions, time discipline

Deliver under experiments/governance_integrity/:
- PRIOR_EVIDENCE.md
- EVIDENCE_GATE.md
- PROTOCOL.md and its SHA256
- SOURCES.json (origin URLs, hashes, snapshot dates, licenses)
- README.md with commands to reproduce (PowerShell-friendly)
- inputs/ (only legally distributable, immutable scored inputs)
- src/ and tests/ (if applicable)
- baseline/ and sophon/ frozen outputs
- AUDIT_REPORT.md (evidence-backed, includes absence of approval)
- RESULTS.md (observed / inferred / assumed; case-level table; resource use)
- DECISION.md (one of **CONTINUE_BOUNDED**, **STOP_KERNEL**, **INCONCLUSIVE_EVIDENCE**)

Use worktrees/fresh contexts as required. Preserve the existing Sophon audit, historical experimental outputs and all prior evidence without overwriting them. Start a feature branch for actual code, commit reproducible checkpoints. Never push to third-party repositories. Never expose credentials or private data.

Constrain work: read prior artifacts; inspect at most 3 candidates; choose one; one minimal mechanism; one strong baseline; one blinded evaluation. No 20-agent literature sweeps, no lengthy market search, no new architecture manifesto. If public evidence does not clear the gate, stop scoring and say precisely why.

Final answer in Claude Code must give:
1. Selected real-world corpus and semantic system with immutable versions (or exact gate failure).
2. What is demonstrably working (commands actually run, exact outputs).
3. Baseline vs Sophon comparison, with explicit independence/leakage status.
4. Transposition, traceability, verification and audit — pass/fail/untested separately.
5. What cannot be claimed about downstream agent compliance or a business.
6. One of the three decisions and a concise engineering next action.
7. The commits and paths of delivered artifacts.

**Do the work, test it and write the results. Do not optimize to keep Sophon alive.**
