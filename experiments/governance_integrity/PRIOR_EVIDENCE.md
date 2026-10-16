# Prior evidence and the falsifiable delta of this experiment

Written 2026-10-11 before any protocol, code or solver run for the governance-integrity experiment.
Everything below was read in this session from the repository at `main` (`311007c`) and from the
unmerged branch `origin/codex/alignment-review-agent` (`d57328c`, PR #2). File paths are given so each
claim can be checked.

## 1. What exists, dated

| Date | Artifact | Where | Status |
|---|---|---|---|
| 2026-09-21 | Architecture investigation: authority ledger vs policy-as-code, 48 lab cases, 20 probes, 46 IPSA reviews coded twice, recurrence study | `docs/REPORT.md`, `docs/DECISION.md`, `lab/`, `results/` | **Ran.** Committed on `main`. |
| 2026-09-21 | Jev impact assessment | `docs/jev_assessment/` | Analysis only; no code. On `main`. |
| 2026-09-21 | Market discovery (15 clusters, ~100 workflows) | `docs/market_discovery/` | Research only; web quota exhausted mid-sweep. On `main`. |
| 2026-09-28 | Warehouse alignment viability test: Jaffle Shop Classic (dbt) + DuckDB + a **synthetic** governing agreement, 9 controlled cases | `viability/` on PR #2 branch | **Ran** (integration gate 9/9 with hand-authored reference SQL). Autonomous-agent gate **NOT RUN**. Not merged to `main`. |
| 2026-09-28 | Public-source alignment review: NYC TLC data dictionary + `bISTP/nyc-taxi-databricks-dbt` + January 2025 yellow-taxi Parquet | `viability/public_nyc/` on PR #2 branch | **Ran**, conversationally, not blinded, not adjudicated. Found a 39% row-loss and a DECIMAL(10,0) precision issue. Context-propagation simulation passed 4 assertions. Not merged. |
| 2026-09-28 | Alignment reviewer prototype over the lab's fictional expense policy | `alignment/` on PR #2 branch | Prototype; 13 workflow tests; **no accuracy measurement**. Not merged. |
| 2026-10-04 | Blind amendment-to-semantic-impact experiment prompt | `Claude_Code_Sophon_Amendment_Impact_Experiment_Prompt_2026-10-04.md` | **Prompt only. Never executed.** No `experiments/amendment_impact_blind/` directory exists on any local or remote ref (`main`, `codex/alignment-review-agent`, `refs/pull/1`, `refs/pull/2`); no stash; no file in the repository mentions `amendment_impact`. |
| 2026-10-11 | This prompt | `Claude_Code_Sophon_Governance_Integrity_Experiment_Prompt_2026-10-11.md` | Being executed here. |

The 2026-10-04 prompt also refers to a "27 September 2026 dbt/DuckDB contract-binding experiment" and a
"28 September 2026 repository review". The only artifacts matching those descriptions are the ones on the
PR #2 branch dated 2026-09-28 (`viability/PROTOCOL.md` is dated 28 September 2026). Nothing dated 27
September exists in the repository.

## 2. What the prior work established (and did not)

**Established, with runnable code:**

1. A purpose-built authority ledger and a disciplined policy-as-code baseline give identical decisions on all
   138,240 compared case decisions, and both pass all 20 adversarial probes once five conventions are added
   (`docs/REPORT.md` §6, `results/lab_results.json`). Several of the packet's own tests could not fail
   (`docs/REPORT.md` §4.2–4.3).
2. A manually supplied governing-rule-to-dbt binding can be represented, executed against a real DuckDB build of
   an existing dbt project, versioned by content hash, and made to fail closed on tampering, missing data and
   changed snapshots (`viability/RESULTS.md`: 9/9 integration cases; 11 boundary tests). The governing agreement
   was **synthetic** and the reference SQL was **hand-written by the same author** who wrote the cases.
3. A conversational reviewer, given an independently authored dbt project and real public data, can find real
   semantic defects (`viability/public_nyc/README.md`). This was **not blinded, not scored, not repeated**.

**Not established by anything in the repository:**

4. Autonomous discovery of which semantic objects an unseen real amendment affects (the 2026-10-04 question).
   The prompt exists; no run exists.
5. Any **lifecycle** property: whether persistent, evidence-backed requirement-to-semantic links stay correct
   across **successive** real changes, whether they are cheaper to maintain than rediscovery, and whether they
   improve an as-of audit. No prior experiment had more than one change episode, and none had an authentic
   governing corpus with its own dated history.
6. Any comparison against a **competent Claude Code baseline** allowed to keep its own notes. The 2026-09-21
   comparison was between two deterministic kernels; the 2026-09-28 tests had no baseline arm at all.

## 3. Falsifiable delta of this experiment versus the prior tests

| Dimension | 2026-09-21 lab | 2026-09-28 viability | This experiment |
|---|---|---|---|
| Governing corpus | Fictional draft expense policy | Synthetic agreement (Jaffle); public data dictionary (NYC) | Authentic consolidated French law (Code de la sécurité sociale) with dated article versions, redistributed from DILA's LEGI base |
| Semantic implementation | None (authority decisions) | dbt teaching project; third-party demo dbt project | The rule-owner's own executable rule library (`modele-social`, Publicodes), published as immutable npm versions |
| Change history | None | None (mutations authored by the experimenter) | Genuine dated commits, PRs, bug reports and npm releases over 2024–2026 |
| Independent oracle | None (same author wrote both arms and probes) | None (same author wrote cases and reference SQL) | A second organisation's encoding of the same law (OpenFisca-France parameters) plus the consolidated article text; disagreements labelled UNRESOLVED |
| Baseline | Policy-as-code kernel | None | Claude Code with native tools and its own persistent notes |
| What can fail | Probes (mechanism properties) | Integration cases (mechanism properties) | Whether a persisted link mechanism beats rediscovery on predeclared outcomes over held-out authentic changes |

**The one claim this experiment can falsify that no prior test could:** on an authentic corpus with several
dated changes on both sides, a tiny persistent store of verified requirement-to-rule links, revalidated on every
diff, yields *measurably* better or cheaper transposition, verification and as-of audit than a competent Claude
Code baseline that rediscovers links each time and keeps ordinary notes. If the baseline does as well after full
costs, or the stored links go stale and give false assurance, the kernel thesis stops.

## 4. Results that are reused rather than repeated

- The authority-kernel-vs-policy-as-code parity (2026-09-21) is taken as settled. No authorization mechanism
  is built or tested here.
- The fail-closed properties of a hash-pinned binding (2026-09-28, `viability/test_boundary.py`) are taken as
  demonstrated for that fixture. This experiment re-tests only the subset that matters for an as-of audit
  (tampered evidence, changed effective date, removed approval, changed rule logic), against authentic inputs.
- The 2026-10-04 impact-discovery question is **not** answered here. This experiment's T0 (initial binding)
  touches it only as a by-product and is scored on evidence integrity, not on recall of hidden labels.

## 5. Constraints carried forward from the prior decisions

- `docs/DECISION.md`: do not build a semantic compiler, normative graph, precedence engine or authorization
  kernel. Nothing of that kind is built here.
- `viability/RESULTS.md`: "A data team could add the same assertions to ordinary dbt. This is not evidence of a
  proprietary detection advantage." The same caution applies to anything the Sophon arm does here that the
  baseline arm could do with a markdown file.
- The 2026-10-04 prompt: no evidence from "a manually supplied binding can be monitored" may count as evidence
  for "autonomous discovery". The protocol separates the two.
