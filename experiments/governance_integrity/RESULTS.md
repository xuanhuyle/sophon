# Results

Sections 1–3 were written before scoring (commit `e31bbf7`) and are kept as written, with the one pending cell
of the §3 table filled in. Sections 4–7 were written after `src/score.py` (second pass), `src/verify_audit.py`
and `src/stale_assurance.py` ran. Every number below is in `results/` and can be regenerated with the commands in
`README.md`; the re-score from the rehydrated frozen outputs gave identical scores for all 22 (arm, task) cells.

## 1. What ran (observed)

- Model for every solver and auditor context: `claude-fable-5-1` (recorded from the session before the first run).
- Arms: A (Claude Code, native tools, free-form persistent notes) and B (identical plus `src/sophon.py`, a
  plain-JSON hash-chained link store with executable checks). Same sealed inputs, same prompts except the one tool
  paragraph, same budget (80 tool calls per task; the largest run used 43).
- Sequence per arm (fresh context each time, `work/` carried forward): T0, T1a, T1b, R1, R2, R3, R4, R5, M0, M1, M2.
  Dates, snapshots, pins, agent ids, tool-call counts and wall-clock per run are in `RUN_LOG.md`.
- Leakage audit: every transcript was scanned for network commands, git commands, reads outside the staging
  directory and any reference to the held-out material. Two kinds of false positives were found and documented
  (the word "git" in heredoc prose; the agent reading its own oversized shell output through the harness's
  tool-results file). After review, **no run is contaminated**. During all solver runs the reference tables, the
  OpenFisca oracle files, the maintainers' later commits and the upstream clones were AES-256 encrypted with a key
  outside the working tree.

## 2. Limitations fixed before scoring (assumed and inferred)

1. **Task order leaks 2026 texts into the maintenance tasks.** PROTOCOL.md §3 runs R4 (S9, 2026-03-31) and R5
   (S10, 2026-10-05) before M0, M1, M2 (2025-10-01, 2026-01-01, 2026-03-31). Each arm's `work/` therefore held
   the 2026 article texts when it faced the maintenance tasks. This is a preregistration error, symmetric across
   arms, and was not corrected after the fact. Consequence: M1 and M2 cannot be read as tests of *discovery*; they
   remain tests of *impact classification, transposition and cost on an already-partly-known change*. M0 (no-op)
   is unaffected in substance (the arms had to say nothing changed, and both did).
2. **Pretraining.** The public history of `mon-entreprise` is very likely in the model's training data. Both arms
   share this; absolute correctness is inflated, the A-versus-B comparison is not.
3. **Future versions have no text.** legi-data ships only the version in force. At T1a (S1) the arms could see
   that D613-4 and D613-6 would change on 2024-07-01, 2025-01-01 and 2026-01-01, but not the new values. The
   protocol's abstention clause covers this; T1a therefore tests impact flagging and abstention discipline, not
   numeric transposition.
4. **Engine quirks found by both arms independently** (recorded in their notes): the engine's `durée` rules read
   the real wall clock rather than the situation date (both arms pinned durations in situations); rules placed under
   an unknown body key are dropped silently (this is what the R3 fix repaired); a replaced rule's value can depend
   on evaluation order within one engine instance (arm A, R2).
5. **n = 1 per cell.** One run per arm per task. Case-level results only; no statistical claim is made.

## 3. Case-level observations recorded before scoring (observed from the arms' reports and files)

| Task | Arm A | Arm B |
|---|---|---|
| T0 | 34 links (26 VERIFIED, 5 INFERRED, 3 UNKNOWN); found the D632-1 floor mismatch; built a proposal fixing it | 55 links (34 VERIFIED, 10 INFERRED, 8 UNKNOWN, 3 FAILED recorded); store verified; same D632-1 finding plus two more executable mismatches |
| T1a | Found the S0→S1 delta; 4 AFFECTED, 6 NEEDS_REVIEW (incl. DROM), 25 UNAFFECTED; abstained on all future values | Same delta; rate rules NEEDS_REVIEW rather than AFFECTED; abstained on all future values; revalidation report produced |
| T1b | 20 AFFECTED, 35 evaluations, 9 abstentions; proposal builds | 22 AFFECTED / 20 NEEDS_REVIEW; 15 transposed constants; 9 abstentions; revalidation flagged D136-5 as unlinked |
| R1 | HARMLESS_REFACTOR (high) | HARMLESS_REFACTOR (high) |
| R2 | HARMLESS_REFACTOR (high) | HARMLESS_REFACTOR (high) |
| R3 | MISMATCH (high), law-conformant values derived | MISMATCH (high), same values |
| R4 | LEGITIMATE_INDEPENDENT_CHANGE (medium) | LEGITIMATE_INDEPENDENT_CHANGE (high) |
| R5 | UNRESOLVED (medium) | UNRESOLVED (medium) |
| M0 | 0 AFFECTED, 33 NEEDS_REVIEW, 14 UNAFFECTED; said no in-force change | 8 AFFECTED (rules with unsupported hard-coded 2026 branches), 64 NEEDS_REVIEW, 304 UNAFFECTED |
| M1 | 31 AFFECTED / 29 UNAFFECTED / 1 NEEDS_REVIEW; BNC 25,6 % and splits transposed | 56 AFFECTED / 4 NEEDS_REVIEW / 316 UNAFFECTED; same transposition plus DROM Cipav fix |
| M2 | 13 AFFECTED / 6 NEEDS_REVIEW / 57 UNAFFECTED; 25 % Acre share transposed | 18 AFFECTED / 15 NEEDS_REVIEW / 43 UNAFFECTED; 25 % Acre share transposed; 56 links added (filled after the run; was "pending" in the pre-scoring draft) |

Both arms converged on every reverse-check label. Both abstained where the protocol expected abstention. Both
reported "none recorded" for every approval. Neither produced a value for a future version whose text was absent.

## 4. Score tables

Source: `results/SCORES.md`, `results/scores.json` (second pass). The first pass (`results/SCORES_firstpass.*`)
is kept; its differences from the second pass are scorer corrections listed in §4.7, none of them a threshold.

### 4.1 Primary outcome: maintenance tasks M0, M1, M2

"Strict" uses the preregistered reference sets (rules that cite or implement a changed article, derived by
pattern from the binding list). "Value-corrected" removes from the required set rules whose implemented value the
new text does not alter (M1: the Cipav invalidité-décès share, 1,40 % in both versions; M2: the Acre eligibility
question and the prorata rule, which the new D131-6-1 version leaves unchanged); those rules move to the optional
set. Both counts are given because the preregistered rule is the one the decision mapping names, and the
correction is a post-hoc judgement, documented and applied identically to both arms.

| Task | Arm | changed articles found | IR strict | FS strict (high) | IR value-corrected | FS value-corrected | over-flag (AFFECTED outside reference + optional) | TC on the reference (correct / incorrect / not transposed) | proposal builds | tool calls |
|---|---|---|---|---|---|---|---|---|---|---|
| M0 | A | 0/0 (none changed) | — | 0 | — | 0 | 0 | — | yes | 32 |
| M0 | B | 0/0 | — | 0 | — | 0 | 8 | — | yes | 27 |
| M1 | A | 2/2 | 20/21 | 1 (1) | 20/20 | 0 | 10 | 21 / 0 / 0 | yes | 32 |
| M1 | B | 2/2 | 20/21 | 1 (1) | 20/20 | 0 | 34 | 21 / 0 / 0 | yes | 32 |
| M2 | A | 1/1 | 7/9 | 2 (2) | 7/7 | 0 | 6 | 1 / 0 / 0 | yes | 43 |
| M2 | B | 1/1 | 7/9 (1 NEEDS_REVIEW) | 1 (1) | 7/7 | 0 | 11 | 1 / 0 / 0 | yes | 39 |

- M1 TC is a reference-driven replay of the proposal trees at 01/01/2026: the BNC global rate (25,6 %) and all
  twenty D613-6 split rules (each category evaluated under the situation that activates it; the maladie line is
  the sum of the maladie and prestations-en-espèces lines, the Cipav retraite de base line the sum of its two
  lines). Both proposals give the twenty-one reference values exactly.
- M2 TC replays the indépendant Acre share rule for a 2026 creation: pin G4 gives 100 %, both proposals 25 %.
- Over-flag in M1 and M2 is mostly parents and downstream aggregates of the changed rules (e.g. `cotisations`,
  `répartition . maladie-maternité`, Acre BNC rate, RCI revenu cotisé); B's 34 in M1 are the per-category
  `répartition` aggregates for all four categories. These are not errors; the reference set contains leaf rules
  only. M0 B's 8 over-flags are the rules carrying hard-coded 2026 branches that no sealed text supported (A put
  the same rules in NEEDS_REVIEW).
- The one strict false-safe per arm in M1 is the same rule (`service BNC Cipav . répartition . invalidité-décès`),
  whose value 1,40 % is unchanged between the 2025 and 2026 versions of D613-6; both arms' UNAFFECTED label is
  correct in substance. The strict false-safes in M2 are `dirigeant . exonérations . ACRE` (the yes/no question;
  A UNAFFECTED, B NEEDS_REVIEW) and `prorata sur l'année` (both UNAFFECTED); neither is altered by the new text.

### 4.2 Forward transposition T1a, T1b

| Task | Arm | changed articles found | IR strict | FS strict | IR / FS value-corrected | TC | tool calls |
|---|---|---|---|---|---|---|---|
| T1a | A | 2/2 | 4/9 AFFECTED + 4 NEEDS_REVIEW | 1 (DROM parent) | 4+4 / 8, 0 | 9/9 rule-dates abstained, 0 unsupported values | 25 |
| T1a | B | 2/2 | 0/9 AFFECTED + 8 NEEDS_REVIEW | 1 (DROM parent) | 0+8 / 8, 0 | 9/9 abstained, 0 unsupported values | 22 |
| T1b | A | 5/5 | 9/11 | 2 | 9/10, 1 (`indemnités journalières maladie . assiette`) | 7/7 decree constants present; 28/28 of A's own evaluation rows replay on its proposal | 27 |
| T1b | B | 5/5 | 9/11 + 1 NEEDS_REVIEW | 1 | 9/10 + 1, 0 | 7/7 constants present; 15/15 rows replay | 25 |

At T1a no new value had text (§2.3); both arms abstained on all 9 rule-dates and changed no rate (checked by
replaying the proposal trees at 2024-07-01, 2025-01-01 and 2026-01-01 against the pin). B chose NEEDS_REVIEW
where A chose AFFECTED for the four global-rate rules; under the §8 definition only AFFECTED counts toward IR, so
A's strict IR is higher at T1a (4/9 vs 0/9) with no false-safe difference. T1a is a secondary outcome. At T1b the
value-corrected set drops the deprecated `maladie . réduction supplémentaire` (applicable only before 2022). A's
remaining false-safe is real: it labelled `indemnités journalières maladie . assiette` UNAFFECTED (high) because
the rule's structure is unchanged, while its own evidence line records that the rule's value follows the reformed
base (200 → 148 €/an on its test situation); B labelled the same rule AFFECTED (medium). This is the one
false-safe in the whole experiment that is a labelling error rather than a reference artefact, and it is A's. The D633-3 constants
appear in the library as one first-tranche rate (17,15 + 0,72 = 17,87 %); both proposals carry it.

### 4.3 Reverse checks R1–R5

| Task | Acceptable labels | Arm A | Arm B | CFC |
|---|---|---|---|---|
| R1 | HARMLESS_REFACTOR | HARMLESS_REFACTOR (high) | HARMLESS_REFACTOR (high) | 0 / 0 |
| R2 | HARMLESS_REFACTOR | HARMLESS_REFACTOR (high) | HARMLESS_REFACTOR (high) | 0 / 0 |
| R3 | MISMATCH (with derived values) or UNRESOLVED | MISMATCH (high), BNC 3,9/11,6/15,4, Cipav 7,8/11,6/15,5 | MISMATCH (high), same values | 0 / 0 |
| R4 | LEGITIMATE_INDEPENDENT_CHANGE or UNRESOLVED | LEGITIMATE_INDEPENDENT_CHANGE (medium) | LEGITIMATE_INDEPENDENT_CHANGE (high) | 0 / 0 |
| R5 | LEGITIMATE_INDEPENDENT_CHANGE or UNRESOLVED | UNRESOLVED (medium) | UNRESOLVED (medium) | 0 / 0 |

Ten of ten labels acceptable; CFC = 0 for both arms. Tool calls R1–R5: A 124, B 130.

### 4.4 Initial binding T0

| Arm | links | by status | VERIFIED checks that hold on replay | reference rule families bound | quotations found | approvals claimed | tool calls |
|---|---|---|---|---|---|---|---|
| A | 34 | 26 VERIFIED, 5 INFERRED, 3 UNKNOWN | 25 / 26 | 8/9 (missed `auto-entrepreneur . DROM`) | 34/34 | none recorded | 31 |
| B | 55 | 34 VERIFIED, 10 INFERRED, 8 UNKNOWN, 3 FAILED | 34 / 34 | 9/9 | 55/55 | none recorded | 26 |

A's one non-holding VERIFIED check records the expected value in €/an (46 368) while the engine reports the
capped assiette in €/mois (3 864); A's own note says so. It is counted as a fail under the mechanical rule.

### 4.5 Evidence integrity (EI, FAB)

Every quote-like string in the arms' answers (link quotes, evidence quotes, evaluation quote fields) was searched
in the normalised text and nota of every article staged for that arm up to that task (the arm's `work/`
legitimately carries earlier snapshots). A: 123 quotations, 123 found, FAB 0 (48 strings in quote fields are
the arm's own notes, such as version references or "notification only"; the classifier counted one of them as not
found). B: 438 quotations, 438 found (10 with B's annotation appended after the quote), FAB 0.

### 4.6 Stale assurance (SA) and the hash-anchored chain (arm B's store, 356 links)

`src/stale_assurance.py`: hash chain intact 356/356; for all 224 VERIFIED links the article text sha256, the
quote at its stored offset and the rule-file sha256 were recomputed with 0 mismatches; all 224 stored checks
re-run against the rules snapshot each link names: 224 hold, 0 fail. Under the strict §8 reading ("VERIFIED for
a rule the reference marks affected by the current snapshot change") SA = 3: link L0243 (D613-6 Cipav
invalidité-décès 1,40 % on pin G3 at 2026-01-01, also STILL_VERIFIED in the M1 revalidation of S8 × G3) and
link L0304 (D131-6-1 Acre share for R > PSS, 0 % on pin G4). Both assert values the new text also gives; B
recorded the values the new text contradicts (26,1 % at 2026; 100 % for 2026 creations) as FAILED. Under a
value reading SA = 0.

The differentiator itself ran as specified: B's M1 revalidation of S8 against G3 classified 216 prior links as
87 REASSESS_LAW_CHANGED, 67 BROKEN, 20 REASSESS_RULE_CHANGED, 34 RULE_CHANGED_CHECK_STILL_PASSES, 5
STILL_VERIFIED and 3 UNVERIFIED_NO_CHECK, and listed 68 rules to reassess; the M2 as-of report for D131-6-1
reproduced the version history from stored hashes. The auditor recomputed these records (§5). None of this
changed B's scored answers relative to A's.

### 4.7 Scorer corrections between the first and the second pass

First-pass artefacts, all visible in `results/SCORES_firstpass.md`: (a) quotations were searched only in the
current task's snapshot, with raw whitespace and apostrophes, so annotated quotes and quotes from earlier
snapshots counted as not found; (b) `LEGIARTI…` version references and the arms' notes in quote fields were
counted as fabricated citations; (c) derived euro amounts in evaluation rows were counted as unsupported values;
(d) transposition correctness was read from arm-specific fields instead of replayed; (e) the répartition rules were
evaluated under one situation, so sixteen of twenty returned null; (f) the D633-3 17,15 % constant was searched
literally although the library stores 17,87 %. No threshold, metric definition, acceptable-label set or
reference value was changed; the value-corrected sets are reported alongside the strict ones, never instead.

## 5. T4 audit

`AUDIT_REPORT.md` in full. Summary: the fresh-context auditor (50 tool calls, no leakage flags) reconstructed
REQ 158 (D131-6-1 `LEGIARTI000053451315`, in force 2026-01-01, "le quart") correctly from both arms' artefacts:
9 of 9 fields VERIFIED or correctly ABSENT for A and for B; both arms pass the missing-source and
missing-approval questions with truthful "not preserved" / "none recorded" answers; no WRONG element in either
arm. The orchestrator's `verify_audit.py` confirmed every path, version id and digest the auditor cited. The
difference is in kind: B's records are recomputable from stored hashes; A's are verbatim copies and engine
result files that the auditor could verify only because it held the sealed inputs.

## 6. Cost

| | Arm A | Arm B |
|---|---|---|
| tool calls, 11 tasks | 314 | 301 |
| tool calls, T3 (M0 + M1 + M2) | 107 | 98 |
| assistant turns | 538 | 640 |
| wall-clock (s) | 11 180 | 12 927 |
| cache-read tokens (harness usage fields, summed) | 55.29 M | 74.48 M |
| cache-creation tokens | 7.29 M | 7.70 M |
| largest single run (tool calls) | 43 (M2) | 39 (M2) |

B used 4 % fewer tool calls over all tasks and 8 % fewer on T3, but 19 % more turns, 16 % more wall-clock and
35 % more cache-read tokens (the store's commands and reports lengthen each context). No human time was measured.

## 7. Decision inputs

Primary outcome: IR and FS equal on M1 and M2 under the value-corrected reading; under the strict reading B's
M2 false-safe count is lower by one rule whose UNAFFECTED label is correct in substance, and B's strict SA is 3.
Secondary: AR equal (9/9, pass, pass); CFC 0 both; EI 100 % both; TC on the reference 22/22 both; SA strict 3,
value 0; chain 224/224. Cost: B slightly fewer tool calls, more tokens and wall-clock. The mapping in
PROTOCOL.md §8 is applied condition by condition in `DECISION.md`; both readings lead to STOP_KERNEL, and §1's
forecast fixed the tie case in advance.
