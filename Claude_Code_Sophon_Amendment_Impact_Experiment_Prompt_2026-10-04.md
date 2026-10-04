# Sophon — Blind Amendment-to-Semantic-Impact Experiment

**Date:** 4 October 2026  
**Status:** execution prompt  
**Purpose:** test the current Sophon kernel, not build a product.

---

# 0. Operating instruction

Treat the current Sophon project as a hypothesis that may deserve to die.

Do **not** optimize for a successful demo.

Do **not** preserve prior architecture, terminology, code, or product direction unless the evidence requires it.

Do **not** build a control plane, normative graph, authorization runtime, agent registry, UI, remediation system, Snowflake/Databricks integration, or production infrastructure.

The sole objective is to answer one question:

> **Given an unseen real governing-document amendment and an existing semantic/dbt layer, can a system identify the materially affected semantic definitions without being told which definitions are affected?**

The answer must be obtained by a blinded, pre-registered experiment against a credible baseline.

If the result is negative, say so and recommend stopping the current autonomous-alignment thesis.

---

# 1. Read the existing evidence before doing anything

Start by reading the relevant repository evidence and decision material, at minimum:

- `README.md`
- `docs/REPORT.md`
- `docs/DECISION.md`
- `docs/jev_assessment/JEV_IMPACT_ASSESSMENT.md`
- `docs/market_discovery/MARKET_DISCOVERY.md`
- `evidence/Sophon_Technical_Viability_Report_2026-09-21.md`

Also inspect any later Sophon experiment/review artifacts available in the working environment concerning:

- the 27 September 2026 dbt/DuckDB contract-binding experiment;
- the 28 September 2026 repository review.

Reconstruct the evidence chain before coding.

The working prior is:

1. the original autonomous natural-language-to-authority compiler thesis did not survive real-corpus testing;
2. the bespoke authority-kernel thesis was weakened by parity with a disciplined policy-as-code baseline;
3. a manually supplied contract-to-dbt binding can be represented, versioned, checked and made to fail closed;
4. **what has not been shown is autonomous discovery of which semantic definitions a real amendment affects.**

Do not allow evidence from (3) to count as evidence for (4).

Write a concise reconstruction to:

`experiments/amendment_impact_blind/STATUS.md`

before implementation.

---

# 2. The kernel

The experiment tests exactly this proposition:

> **Given an unseen real governing-document amendment, the pre-amendment governing document, and a frozen semantic/dbt project, Sophon can identify the materially affected semantic objects without being given a source-to-model mapping or the location of the inconsistency.**

This is the only kernel under test.

The experiment is **not** testing:

- automatic remediation;
- downstream agent synchronization;
- production authorization;
- whether a graph can represent provenance;
- whether hashes detect changed files;
- whether dbt can run;
- whether LLMs can summarize amendments;
- whether a human-authored binding can be monitored.

If the experiment drifts toward any of those questions, stop and return to the kernel.

---

# 3. Pre-register the decision rule before seeing outcomes

Before executing the benchmark, create:

`experiments/amendment_impact_blind/PROTOCOL.md`

Freeze and hash it.

The primary success gates are:

1. **Material-impact recall >= 90%.**
2. **False-safe rate <= 5%.**
   - A false-safe error is an actually affected object explicitly classified as `UNAFFECTED`.
   - `NEEDS_REVIEW` is not a false-safe answer.
3. **Precision on `AFFECTED` >= 80%.**
4. Against the generic same-model baseline, Sophon must achieve at least one of:
   - **>= 15 percentage points absolute F1 improvement**, or
   - **>= 50% fewer false-safe errors**.
5. No contract-specific hand-authored source-to-dbt mapping may be supplied to the solver.
6. No per-case prompt engineering after results are visible.

The current thesis **fails** if any of the following occurs:

- material-impact recall < 80%;
- repeated false-safe errors on materially affected objects;
- Sophon does not materially outperform the generic baseline;
- success depends on hand-authored contract-specific mappings;
- success depends on modifying the method after inspecting the hidden labels.

Outcomes between the success and failure bands are **INCONCLUSIVE**, not success.

Do not move the thresholds after execution.

---

# 4. Benchmark design

Construct a benchmark of approximately **12–15 amendment cases** with roughly **60–100 candidate object-level decisions** in total.

Use real public governing-document amendments wherever possible.

Preferred sources:

- SEC-filed commercial agreements and amendments;
- public licenses, distribution agreements, royalty agreements, supply agreements, financing agreements, or other contractual documents where amendments visibly alter operational terms.

Prefer amendments affecting objectively testable dimensions such as:

- rates;
- thresholds;
- eligibility;
- product/category scope;
- geography;
- channel;
- effective dates;
- deductions;
- payment conditions;
- calculation bases;
- reporting definitions.

Avoid a benchmark dominated by trivial string substitutions.

For each case, create a pre-amendment semantic/dbt representation that contains:

- objects genuinely affected by the later amendment;
- plausible downstream objects that should remain unaffected;
- enough semantic description and lineage to resemble a competent analytics project;
- no explicit leakage such as object names that state “affected_by_amendment_X”.

The semantic/dbt side may be synthetic if necessary, but it must be constructed **only from the pre-amendment governing state** and frozen before the solver sees the amendment.

Do not use the existing 27 September royalty fixture as a scored holdout case. It may be used only as a smoke test because the project has already seen it.

---

# 5. Blinding and context separation

This is critical.

The same model context must not both create the gold answer and solve the case.

Use isolated roles/subagents/processes.

## Role A — Benchmark builder

Role A may read:

- original governing documents;
- amendments;
- the semantic/dbt fixtures it constructs.

Role A produces:

- the case inputs;
- hidden gold labels;
- evidence for each gold label;
- a benchmark manifest;
- hashes.

Gold labels must live under:

`experiments/amendment_impact_blind/held_out/`

Role A must not provide the solver with a summary revealing which objects are affected.

## Role B — Sophon solver

Role B receives only:

- the pre-amendment governing document;
- the amendment;
- normal semantic/dbt artifacts;
- the frozen task specification.

Role B must **not** read:

- `held_out/`;
- scoring code containing labels;
- builder notes identifying affected objects.

If tool permissions can enforce this, enforce it.

Otherwise implement a clean export directory containing only allowed inputs and run Role B against that directory.

## Role C — Generic baseline

Use the **same underlying model family** as the Sophon solver if technically possible.

Give Role C the same allowed input artifacts.

Use a simple one-shot instruction such as:

> Review the amendment and the semantic/dbt project. Identify which semantic objects are materially affected, which are unaffected, and which require review. Cite the relevant amendment evidence.

Do not give the baseline Sophon-specific decomposition, search procedure, graph, or prior mapping.

## Role D — Scorer

Only after both arms have frozen their predictions may Role D read:

- predictions;
- hidden labels;
- gold evidence.

Role D computes metrics mechanically.

If perfect context isolation is impossible in one Claude Code session, **do not fake blindness**.

Instead:

1. prepare and freeze the benchmark;
2. write exact commands for fresh solver sessions;
3. stop before executing the scored solver;
4. state that a new context is required.

Methodological validity is more important than completing everything in one run.

---

# 6. Minimum Sophon method

Build the smallest method that could plausibly express Sophon's current hypothesis.

It may use:

- structural parsing of the amendment;
- extraction of changed normative/business propositions;
- retrieval over dbt model SQL, YAML, descriptions, tests, metrics and lineage;
- semantic comparison between changed propositions and candidate semantic objects;
- evidence-backed classification;
- explicit abstention.

It must output, for every candidate object:

```json
{
  "object_id": "...",
  "classification": "AFFECTED | UNAFFECTED | NEEDS_REVIEW",
  "materiality": "MATERIAL | NON_MATERIAL | UNCERTAIN",
  "source_evidence": ["..."],
  "semantic_evidence": ["..."],
  "reason": "...",
  "confidence": 0.0
}
```

Do not build anything beyond what is required to generate this output and score it.

The method may be multi-step.

The generic baseline should remain one-shot.

---

# 7. Anti-leakage requirements

Actively test for benchmark leakage.

At minimum verify:

- object names do not encode gold labels;
- descriptions do not quote post-amendment language unless that language genuinely existed pre-amendment;
- file paths do not identify the target object;
- affected objects are not always the only objects sharing vocabulary with the amendment;
- distractors are semantically plausible;
- some amendments affect multiple objects through indirect consequences;
- some high-overlap objects are actually unaffected;
- some low-overlap objects are affected through dependencies or business meaning.

Create at least one adversarial leakage check and record the result.

---

# 8. Error taxonomy

For every error, classify it as one of:

- amendment change not detected;
- change detected but business meaning misunderstood;
- correct semantic change but wrong candidate retrieval;
- direct object found but downstream affected object missed;
- over-broad lexical match;
- effective-date/version error;
- table/cross-reference/scope loss;
- ambiguity incorrectly forced into a definite answer;
- evidence unsupported;
- benchmark/gold ambiguity.

Do not repair errors before recording the frozen first result.

---

# 9. Evaluation

Report separately:

- affected-object recall;
- affected-object precision;
- F1;
- false-safe count and rate;
- `NEEDS_REVIEW` rate;
- per-case exact-set accuracy;
- direct vs indirect impact performance;
- Sophon vs generic-baseline delta;
- model/API cost;
- runtime;
- setup effort.

Also report confidence intervals where sensible given the small sample.

Do not hide failure behind aggregate F1 if there are serious false-safe errors.

The primary safety metric is false-safe behavior.

---

# 10. Sanity checks

Before scoring the real benchmark:

1. run one trivial smoke case;
2. run one adversarial distractor case;
3. verify that swapping or deleting the amendment changes predictions;
4. verify that replacing the dbt project with an unrelated project materially changes predictions;
5. verify that the solver does not rely on filenames or gold-adjacent metadata.

These are sanity checks, not evidence for the thesis.

---

# 11. What counts as an uninformative experiment

Do not interpret the result as a thesis failure if the benchmark itself is invalid.

Flag the benchmark as **UNINFORMATIVE** if:

- reviewers materially disagree on gold impact;
- the dbt fixtures trivially echo amendment wording;
- almost every case is a simple number substitution;
- affected objects can be identified from names alone;
- the supposed unaffected objects are implausible distractors;
- the semantic fixtures are so artificial that impact reasoning is tautological.

If the benchmark is uninformative, fix the benchmark once while labels remain hidden from the solver, then rerun.

Do not iteratively tune on scored results.

---

# 12. Deliverables

Create only the artifacts needed to reproduce the experiment:

```text
experiments/amendment_impact_blind/
  STATUS.md
  PROTOCOL.md
  README.md
  benchmark_manifest.json
  inputs/
  held_out/
  src/
  baseline/
  predictions/
  results/
  RESULTS.md
  DECISION.md
  FAILURE_MODES.md
  REPRODUCE.md
```

Keep `held_out/` inaccessible to solver roles.

`RESULTS.md` must clearly separate:

- observed;
- inferred;
- assumed.

`DECISION.md` must end with exactly one project decision:

- **CONTINUE**
- **STOP**
- **INCONCLUSIVE — BENCHMARK FAILURE**

Do not use `PIVOT` to avoid a negative result.

A negative result kills the **current autonomous amendment-to-semantic-impact thesis**. A future unrelated idea can be evaluated separately.

---

# 13. Decision interpretation

## CONTINUE

Use only if all primary success gates pass and the benchmark is informative.

Even then, conclude only:

> autonomous amendment-to-semantic impact discovery deserves a Level-1 / real-world follow-up.

Do **not** conclude product-market fit, production readiness, or economic value.

## STOP

Use if the explicit failure condition is crossed.

If Sophon performs roughly like the generic baseline, that is a STOP for the current differentiated technical thesis.

Do not rescue it by adding:

- more agents;
- persistent memory;
- a graph;
- a control plane;
- manual mappings;
- human review at every object;
- new product positioning.

## INCONCLUSIVE — BENCHMARK FAILURE

Use only when the benchmark cannot fairly resolve the claim.

Explain specifically why.

---

# 14. Repository discipline

Before making changes:

- inspect the current branch and working tree;
- do not overwrite prior evidence;
- preserve existing experiment artifacts;
- isolate all new work under `experiments/amendment_impact_blind/`.

Commit meaningful checkpoints.

Do not refactor unrelated code.

Do not rewrite historical decision documents to make the new result look continuous with prior Sophon work.

---

# 15. Final report

At the end, answer exactly these questions:

1. What did the experiment actually test?
2. Was the benchmark genuinely blinded?
3. What was Sophon's frozen first-pass performance?
4. What was the generic baseline's performance?
5. Where did each arm fail?
6. Did Sophon materially outperform the generic baseline?
7. Did it meet the pre-registered gates?
8. What capability, if any, has now actually been demonstrated?
9. What remains storytelling?
10. Should the current Sophon thesis CONTINUE or STOP?

End with:

> **If this were your own time and money, would you spend another week on the current Sophon thesis?**

Answer only **YES** or **NO**, then justify in no more than three paragraphs.

---

# 16. Execution principle

Do not help Sophon survive.

Run the cheapest experiment capable of killing it.
