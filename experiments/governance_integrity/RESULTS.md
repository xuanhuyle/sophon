# Results (draft skeleton; score tables are filled in by the final commit)

Status at the time of this draft: all eleven solver tasks are complete for arm A and ten of eleven for arm B;
the T4 audit, the unsealing of the reference and the mechanical scoring have not run yet. Nothing below is a
score. The sections that do not depend on scores are written now so that they are fixed before the numbers are seen.

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
| M2 | 13 AFFECTED / 6 NEEDS_REVIEW / 57 UNAFFECTED; 25 % Acre share transposed | (pending) |

Both arms converged on every reverse-check label. Both abstained where the protocol expected abstention. Both
reported "none recorded" for every approval. Neither produced a value for a future version whose text was absent.

## 4. Score tables

(filled in from `results/SCORES.md` after the reference is unsealed and `src/score.py` has run)

## 5. T4 audit

(filled in from `AUDIT_REPORT.md`)

## 6. Cost

(filled in from `RUN_LOG.md` totals and `results/scores.json` cost fields)

## 7. Decision inputs

(filled in; the mapping is fixed in PROTOCOL.md §8 and applied in `DECISION.md`)
