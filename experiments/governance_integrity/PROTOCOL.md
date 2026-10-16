# Preregistered protocol: governance-integrity lifecycle test on a law-to-rules system

Status: **frozen before any kernel code, sealed-input build, solver run or reference table existed.**
Written 2026-10-11 after `EVIDENCE_GATE.md` (gate outcome PARTIAL / LIMITED). The SHA-256 of this file is
recorded in `PROTOCOL.sha256` and in the commit that adds both. Any later edit to this file is a protocol
violation unless it only corrects a typo and is listed in `RESULTS.md` with the new hash.

Everything below is phrased so it can fail. Thresholds are fixed here and are not moved afterwards.

## 1. Hypothesis under test, and the one thing arm B does that arm A does not

**Hypothesis (bounded kernel).** On an authentic, versioned governing corpus linked to the rule owner's own
executable rule library, a tiny persistent store of evidence-backed, versioned requirement-to-rule links that is
revalidated on every diff improves the correctness and the cost of (a) forward transposition, (b) reverse
checks, (c) maintenance across successive changes and (d) as-of audit, compared with Claude Code using native
tools and its own notes.

**The single predeclared differentiator.** Arm B's store performs, without any model call, a deterministic
*diff-driven revalidation*: given a new governing snapshot or a new rule snapshot, it enumerates which stored
links are touched (by article version id and text hash on one side, rule file hash and rule name on the other),
re-executes each link's stored executable check against the native rule engine, and emits the affected set with
statuses, plus an as-of report assembled from stored hashes. Arm A can only approximate this by re-reading
inputs or by trusting its own notes without re-execution.

**Forecast (so that the comparison can be read without hindsight).** B will have equal or higher material
impact recall and fewer false-safe calls at T3 (maintenance) with fewer tool calls, and more hash-verified fields
at T4 (audit). If A matches B on T3 and T4 after costs, the differentiator is not justified and the kernel stops.

**Primary outcome (one):** T3 material impact recall and false-safe count on the two sequential governing
changes M1 and M2, with the no-op M0, together with the tool-call cost of producing them.
**Secondary outcomes:** T4 audit reconstruction (verified fields, correct handling of missing approval and
missing source), T1 transposition correctness on scored numeric requirements, evidence integrity, and the
presence of stale assurance.

## 2. Matched system and frozen inputs

System: `betagouv/mon-entreprise` rule libraries (`modele-social`, later `modele-ti`) executed by `publicodes`,
governed by the French Code de la sécurité sociale (CSS). Identifiers, dates, hashes and licences are in
`SOURCES.json`; the sealed copies and their hashes will be in `inputs/MANIFEST.json`.

### 2.1 Bounded governing corpus (the article set)

CSS articles L131-6, L136-3, L613-7, D131-6-1, D136-5, D613-4, D613-5, D613-6, D621-2, D632-1, D633-3, D756-5,
taken from `@socialgouv/legi-data` snapshots. Each article record keeps: `num`, `id` (LEGIARTI version id),
`cid`, `etat`, `dateDebut`, `dateFin`, plain text, `articleVersions`, `lienModifications`. Nothing outside this
set is scored; requirements that depend on other articles are classified NOT_OBSERVABLE or UNRESOLVED.

Snapshots (legi-data version → publish date): S0 2.360.0 (2024-05-25), S1 2.361.0 (2024-06-01), S2 2.375.0
(2024-07-01), S3 2.381.0 (2024-07-17), S4 2.384.0 (2024-09-01), S5 2.385.0 (2024-10-19), S6 2.464.0
(2025-09-01), S7 2.469.0 (2025-10-01), S8 2.489.0 (2026-01-01), S9 2.514.0 (2026-03-31), S10 2.572.0 (latest).

Verified before this protocol was frozen (text hashes of every bounded article): S6 and S7 are identical on the
whole set; S4 and S5 are identical on D613-4, D613-6, D756-5; S7 → S8 changes only D613-4 and D613-6; S8 → S9
changes only D131-6-1.

### 2.2 Bounded semantic model (the rule set) and its runtime

Rule files (Publicodes YAML) from the `betagouv/mon-entreprise` git tree at pinned commits:

| Pin | Commit | Tree date | In-tree `modele-social` version | Files |
|---|---|---|---|---|
| G0 | `d9242882f96bda5b4418b7c1c3ff46b0e2a1c5ce` | 2024-05-15 | 2.1.0 | `modele-social/règles/dirigeant/auto-entrepreneur/*.publicodes`, `dirigeant/dirigeant.publicodes`, `dirigeant/exonérations.publicodes`, `dirigeant/indépendant.publicodes`, `période.publicodes`, `base.publicodes` and every other file under `modele-social/règles/` needed to build the engine |
| G1 | `2a0e452617fc33b955096f4bb7f7f305ec0670ad` | 2024-07-16 | 2.1.0 | same layout |
| G2 | `3a4091ae1cafdd4572bfd10d6352fd04db8da419` | 2024-10-10 | 2.4.0 | same layout |
| G3 | `d6c37427172707b4c0fa64d9e6f18ea67f9f67b4` | 2025-12-30 | 10.0.0 | same layout, `dirigeant/indépendant/` is a directory |
| G4 | `a61b72947fec1e1383e07b3278424593dc296ba2` | 2026-03-03 | 10.0.1 | same layout |

The whole `modele-social/règles/` tree at each pin is sealed (the engine needs all rules to build), but the
*bounded rule set* for scoring is: every rule whose dotted name starts with
`dirigeant . auto-entrepreneur . cotisations et contributions`, `dirigeant . auto-entrepreneur . DROM`,
`dirigeant . exonérations . ACRE`, `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE`,
`dirigeant . indépendant . cotisations et contributions`, `dirigeant . indépendant . assiette minimale`.

Runtime: `publicodes@1.10.4` (npm, pinned by integrity). Rules are loaded from the sealed YAML files with a small
loader (`src/publicodes_eval.mjs`) that reproduces the project's build (merge all `.publicodes` files into one
rule object). Published packages `modele-social@2.1.0`, `@2.3.0`, `@2.4.0`, `@10.0.0`, `@10.0.1`, `@11.1.0` and
`modele-ti@0.1.0` are sealed as tarballs for cross-checks and for T5; they are not the scored object.

Pre-existing tests: `site/test/regressions/auto-entrepreneur.yaml` and its `__snapshots__/*.snap` at each pin,
and `api/source/test-e2e/index.test.ts` at each pin, sealed as read-only context (same-organisation evidence).

Git history available to the arms: `git log --format='%H %ci %an %s'` restricted to `modele-social/règles/` up to
the pin's date, plus the full diff of commits inside the bounded rule set up to the pin's date. No commit after the
pin's date is included.

### 2.3 Independent reference material (scorer only)

- The article texts themselves (deterministic numbers and dates).
- OpenFisca-France parameter files at `16b2e69633e840fdf5f39b74f96dfd2382898dd5` for the micro-social rates
  (`cotisations_prestations/service.yaml`, `cipav.yaml`) and the retirement rate (`ret_ac/.../tout_salaire.yaml`).
- The maintainers' later commits are sealed **for the scorer only** as "what the maintainers did"; they are not
  gold. Where the maintainers and the article text disagree, the article text wins; where the text is ambiguous,
  the item is UNRESOLVED and not scored for correctness.

## 3. Episodes, tasks and decision-time evidence

Each task is run once per arm, in a fresh model context, with exactly the sealed inputs listed. "Law" is the
legi-data snapshot given; "rules" is the git pin given. Nothing dated after the task's decision date is given.
The arm's own persistent directory (A: `baseline/notes/`; B: `sophon/store/` plus `sophon/notes/`) is carried
forward from task to task, in this order: T0, T1a, T1b, T2 (R1–R5), T3 (M0, M1, M2). T4 is performed by the
auditor on the arms' artifacts. T5 is optional and non-scored.

| Task | Decision date | Law | Rules | Origin of change | What the arm must produce |
|---|---|---|---|---|---|
| T0 initial binding | 2024-05-25 | S0 | G0 | none | Candidate links rule → (article num, version id, quoted value/date), each labelled VERIFIED (backed by an executed check: evaluate the rule at a date and compare with the number in the text), INFERRED (textual link, no executable check) or UNKNOWN; source location; approval provenance ("none recorded" is the only truthful value here). |
| T1a forward (E1) | 2024-06-01 | S1 | G0 | governing (Décret 2024-484: D613-4 and D613-6 new versions dated 2024-07-01, 2025-01-01, 2026-01-01) | Affected rules; proposed YAML edits in a disposable copy; native build; evaluations at 2024-06-01, 2024-07-01, 2025-01-01, 2026-01-01 for the four global rates and the category-e répartition; or explicit abstention per item. |
| T1b forward (E3) | 2024-07-17 | S3 | G1 | governing (LFSS 2024 art. 18 already in L136-3 III and L131-6; Décret 2024-688: D136-5, D621-2, D633-3 new versions in force 2024-07-07, for contributions from 2025-01-01) | Affected rules in `dirigeant . indépendant . cotisations et contributions`; proposed edits or abstention for: 26 % abattement, floor 1,76 % PASS, ceiling 130 % PASS, applicability from 2025-01-01, D621-2 constants (T1 1,5 %, T2 4 %, thresholds 20/40/60/110 % PSS, 3 PSS), D633-3 rates (17,15 %, 0,72 %); native build and evaluations. |
| T2 reverse R1 | 2024-07-17 | S3 | G1 diff `2a0e45261` (dead reference links replaced) | semantic, documentation only | One label from {HARMLESS_REFACTOR, MISMATCH, LEGITIMATE_INDEPENDENT_CHANGE, UNRESOLVED} with confidence {high, medium, low} and evidence; executable before/after comparison where possible. |
| T2 reverse R2 | 2024-09-02 | S4 | G1→ diff `1932d654c` (rule made public, metadata) | semantic, metadata only | same |
| T2 reverse R3 | 2024-10-19 | S5 | G2 diff `9bb43d710` (DROM rate rules re-nested so that `remplace` applies; values unchanged) | semantic, implementation fix | same; D756-5 (fractions 1/6, 1/3, 1/2, 2/3 of the D613-4 rates, rounded up to the tenth of a percent) is in the bounded set, so the arm can compute whether the DROM values match the law in force. |
| T2 reverse R4 | 2026-03-31 | S9 | G4 diff `d3e0cfe0f` (retirement base formula replaced by the URSSAF method) | semantic, documented deliberate choice | same |
| T2 reverse R5 | 2026-10-05 | S10 | HEAD diff `c14ee26d0` (no floor/ceiling of the abattement in Mayotte) | semantic, exception | same; the legal basis for Mayotte is outside the bounded set. |
| T3 maintenance M0 | 2025-10-01 | S6 → S7 | G3 | none (verified no-op on the bounded set) | List of links touched by the snapshot change and the actions taken; the correct output is "no bounded article changed; nothing to revalidate" plus whatever stale items the arm already knew about. |
| T3 maintenance M1 | 2026-01-01 | S7 → S8 | G3 | governing (D613-4 → `LEGIARTI000052218738`, 2026 BNC rate 25,6 %; D613-6 → `LEGIARTI000052218747`, new 2026 répartition for all categories) | Affected rules; proposed edits; evaluations at 2026-01-01; abstention where the text does not settle the value. |
| T3 maintenance M2 | 2026-03-31 | S8 → S9 | G4 | governing (D131-6-1 → `LEGIARTI000053451315`, Décret 2026-69, exemption reduced to a quarter of the contributions below 3/4 PSS, formula changed) | Affected rules (Acre rules for auto-entrepreneurs and indépendants); proposed edits or abstention; note that the article's own dateDebut is 2026-01-01 while the decree was published 2026-02-08. |
| T4 as-of audit | after all runs | S0–S10 | G0–G4 | — | Performed by the auditor, see §6. |
| T5 thin consumer | after all runs | — | published packages | — | Optional, non-scored: evaluate the published package as the mon-entreprise API does, before and after a proposed change. |

Held-out case types, by design: **unknown** (R4, R5: outside or ambiguous in the bounded set), **no-op**
(M0, R1, R2), **time-dependent** (every D613-4/D613-6 item has three effective dates; M2's dateDebut vs
publication), **exception** (R5 Mayotte), **missing evidence** (T4 items 2 and 3; every rule whose `références`
point to URSSAF pages that cannot be fetched).

Synthetic perturbations exist only in `tests/` (tamper tests on the kernel) and are reported as robustness
diagnostics, never as episodes.

## 4. Arms

Same model (the model serving this session, recorded in `RESULTS.md` from `get_session`), same tools (Bash,
file read/write/edit/glob/grep, node and python in the sealed environment), same budget (at most 80 tool calls
per task; the run is cut at that point and scored as is), same sealed inputs, same task prompts
(`inputs/prompts/<task>.md`, frozen and hashed), same number of runs (exactly one per arm per task; a second
run, if any, is a labelled robustness diagnostic and never the headline).

**Arm A (baseline).** Claude Code with the inputs above and a persistent directory `baseline/notes/` it may
organise as it likes (markdown, JSON, scripts). It is told it will face later tasks on the same system and is
encouraged to keep whatever it finds useful. It is not restricted to one shot.

**Arm B (Sophon kernel).** Identical, plus the CLI under `src/` (`sophon.py` and `publicodes_eval.mjs`) with
its usage document, and the instruction to record links and run revalidation through it. The store is plain
JSON under `sophon/store/`. No prefilled links, no hidden ground truth, no extra model calls: every model call
B makes is a call A could make.

Both arms receive the same note: approvals do not exist in this corpus; writing "no approval recorded" is the
correct behaviour; inventing one is scored as fabrication.

## 5. Reference construction and scoring rules

The reference table `held_out/REFERENCE.json` is built by the orchestrator **after this protocol is committed and
before any solver run**, from the article texts in §2.1 and the OpenFisca values in §2.3 only. It lists, per
scored requirement: article num, version id, in-force date, the literal number, the rule(s) it binds to (by
dotted name as of the relevant pin), the evaluation situation and date, the expected engine value, and the
OpenFisca value where one exists. Items where the text and OpenFisca disagree, or where the binding to a rule is
not mechanical, are labelled UNRESOLVED and excluded from correctness scoring (they still count for abstention).

Scored requirement families (expected counts are approximate until the table is built; exact N is reported):
D613-4 rows a, b, d, e at three dates (12 values); D613-6 category-e répartition at 2024-07-01 and all
categories at 2026-01-01; D136-5 floor and ceiling; L136-3 III 26 %; D621-2 constants; D633-3 two rates; D756-5
fractions applied to D613-4 (12 derived values); D131-6-1 new quarter factor.

Scoring is mechanical where it can be: the arm's proposed rule files are loaded into the engine by the scorer and
evaluated at the reference situation and date; equality within 1e-9 on the percentage is "correct".

Labels for T2: the acceptable set per case is fixed here. R1: {HARMLESS_REFACTOR}. R2: {HARMLESS_REFACTOR}.
R3: {MISMATCH with the computed law-conformant DROM values, or UNRESOLVED citing D756-5's reference to the
renumbered D131-6-1}; HARMLESS_REFACTOR is wrong because the fix changes outputs; "aligned with the law in force"
is wrong because the values derive from the pre-2024-07 base rates. R4: {LEGITIMATE_INDEPENDENT_CHANGE,
UNRESOLVED}. R5: {LEGITIMATE_INDEPENDENT_CHANGE, UNRESOLVED}. A high-confidence label outside the acceptable set
is a **confidently false conclusion**.

T3 reference affected sets are derived mechanically from which bounded articles changed and which sealed rules
cite or implement them (the binding list in the reference table). M0: empty. M1: the auto-entrepreneur global
rate rules and the répartition rules. M2: the Acre rules.

## 6. T4 as-of audit procedure

The auditor is a fresh context that receives only: each arm's persistent directory, the sealed inputs, and the
three audit questions. It may not read `held_out/`. It reconstructs, for each question and each arm, the fields
{source article version id, in-force date, snapshot used, interpretation status, rule file hash or commit,
executable check and its result, approval record}. The scorer then verifies every field against the sealed
inputs by hash or by re-running the check, and marks it VERIFIED, UNVERIFIED (asserted, not checkable from the
arm's artifacts) or WRONG. Citation-shaped text without a verifiable anchor is UNVERIFIED.

Questions: (1) the scored requirement whose index is `int(PROTOCOL.sha256[:8], 16) mod N` in the reference
table's ordered list, asked "as of" its in-force date; (2) missing source: "what primary source supports the
DROM override values and is it preserved?" (correct: the rules cite an URSSAF PDF that is not preserved and not
retrievable; D756-5 and D613-4 are preserved); (3) missing approval: "who approved the 2026 rate change and
when?" (correct: no approval evidence exists in the preserved artifacts; only a commit and a snapshot).

## 7. Leakage controls

- Sealed inputs contain only artifacts dated before each task's decision date. The clones of
  `mon-entreprise` and `openfisca-france`, the legi-data snapshots after the task date, and `held_out/` are
  moved into an encrypted archive (AES-256, key file outside the working tree) before any solver run and restored
  only for scoring.
- `held_out/REFERENCE.json` is encrypted at rest during solver runs with the same key.
- Solver and auditor transcripts are audited for any read outside the sealed input directory and the arm's own
  directory, and for any network command (`git clone`, `git fetch`, `curl`, `wget`, `npm view`, `npm install`,
  `pip`, `fetch`). A run with such an access is marked CONTAMINATED and excluded; the contamination is reported.
- Limit that cannot be removed: the solver agents share the operating-system user with the orchestrator, so the
  protection is against accidental access and search, not against a deliberately adversarial solver. The
  model's pretraining very likely includes the public history of `mon-entreprise`; this inflates absolute
  correctness for both arms equally and is declared in `RESULTS.md`. It does not affect the A-versus-B
  comparison, which is the object of the primary outcome.
- The orchestrator has read the maintainers' later diffs while building the evidence gate (unavoidable: the gate
  required inspecting primary commits). The orchestrator therefore never acts as a solver; solvers are fresh
  contexts.

## 8. Metrics (exact definitions) and the stopping rule

For each task and arm, with exact numerators and denominators:

- **IR** material impact recall = |reference-affected rules flagged AFFECTED| / |reference-affected rules|.
- **FS** false-safe = number of reference-affected rules the arm explicitly labelled UNAFFECTED or "aligned".
- **OF** over-flag = rules flagged AFFECTED that are not in the reference set.
- **TC** transposition correctness = correct / (correct + incorrect + abstained), reported as three counts.
- **EI** evidence integrity = verified cited tuples / cited tuples; **FAB** fabricated citations (id not in the
  snapshot, or quoted value not in the text) counted separately.
- **AR** audit reconstruction = VERIFIED fields / all fields per question; the missing-approval and
  missing-source questions pass only with "no evidence recorded" / "not preserved".
- **SA** stale assurance = number of links or reports asserting VERIFIED/aligned for a rule that the reference
  marks affected by the current snapshot change, or whose stored check fails when re-run.
- **CFC** confidently false conclusions = high-confidence labels or values contradicted by the reference.
- **COST** tool calls and wall-clock per task, taken from transcripts; tokens where the harness reports them;
  files read. Human time is not measured and no reduction in human labour is claimed.

Decision mapping (fixed):

- **STOP_KERNEL** if any of: (i) B's IR ≤ A's IR and B's FS ≥ A's FS on M1 and M2 while B's COST ≥ A's COST;
  (ii) SA ≥ 1 for B; (iii) B's AR ≤ A's AR on all three audit questions and B is not better on the primary
  outcome; (iv) the differentiator in §1 turns out to add nothing A's notes did not already achieve.
- **CONTINUE_BOUNDED** only if all of: B strictly better than A on the primary outcome (higher IR or lower FS on
  M1 or M2, with COST not higher by more than 25 %) or strictly better on AR with equal primary outcome; SA = 0
  for B; CFC = 0 for B in scored episodes; at least one forward (T1a or T1b) and one reverse (R3) episode scored;
  TC for B shows no incorrect value on D613-4 items; EI ≥ 0.9 for B; every VERIFIED link has a hash-anchored
  evidence chain. Even then the conclusion is limited to law-to-executable-rules systems and the full
  semantic-layer thesis remains untested.
- **INCONCLUSIVE_EVIDENCE** if the reference table cannot be built for M1 or M2, if a solver run is
  CONTAMINATED and cannot be re-run cleanly, or if the native runtime fails on the sealed inputs.

Stopping rule for execution: the sequence in §3 is run once. No task is re-run after seeing scores. If an
infrastructure failure (not a model failure) aborts a run before any model output, that single run is restarted
once and the restart is logged.

## 9. Coverage

Before scoring, every material requirement in the bounded article set (each numbered row, rate, threshold,
date or formula) is enumerated in `held_out/COVERAGE.json` and classified FULLY_OBSERVABLE (a rule evaluates it
directly), PARTIALLY_OBSERVABLE (a rule depends on it but the effect is not isolable by evaluation) or
NOT_OBSERVABLE (no rule in the bounded set implements it). The scored requirements are a subset of
FULLY_OBSERVABLE and the fraction is reported.

## 10. What will not be claimed

Nothing here measures downstream agent or BI compliance, human labour, legal compliance of mon-entreprise, or
the semantic-layer architecture on a warehouse. A positive result would say only: on one public law-to-rules
system with five authentic change episodes, a persisted-link kernel did or did not beat a competent baseline on
the outcomes above.
