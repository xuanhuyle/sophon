# E3.1: decision

**PASS_INTEGRITY_HARDENING.**

The verdict is applied mechanically from PROTOCOL.md §6 (`src/gate.py` → `evidence/gate.json`).

## Why PASS

- **Both E3 defects were reproduced first** with the unmodified E3 validator:
  - F-TIME: a requirement not in force was VERIFIED;
  - F-FORGE: a self-consistent, re-hashed store-reading receipt pair was accepted for the approved customer
    reading.
- **All 28 frozen cases behave as expected** after the correction, with **zero false promotions**. This covers
  13 temporal and 15 evidence cases:
  - inclusive start and end boundaries;
  - the not-known and not-in-force axes, kept separate;
  - retroactive rules, as known before and after their observation;
  - consistent forgeries, fake revisions and swapped reading content;
  - an unavailable runtime and untrusted reference code;
  - forged guards on a negative-quantity estate.
- **The clean positives still verify,** using fresh native MetricFlow and fresh raw-CSV reference calculations
  in a newly rebuilt, anchor-checked estate: S1 derived, S2 customer, S3 simulated equivalence, plus the T2, T3
  and T7B boundaries.
- **An independent second verifier process** with its own rebuild reproduced the results exactly.
- **E0–E3 files are unchanged.** E3's 54/54 score and its diagnostics stand as historical results.

## What PASS does not mean

- Not tamper-proof, not a security proof and not signing. A compromised verifier, reference code, trusted
  manifest or pinned source defeats the check; the non-scored diagnostic shows this.
- Not legal applicability beyond inclusive date windows.
- Not that the data or the simulated approvals are genuine.

## Next experiment (recommended, not executed)

**E4: independent native semantic verification**, per `Claude_Code_Sophon_E4_Independent_Semantic_Verification_2026-10-12.md`.
- Start on a new branch from this PR's head.
- Reuse E3.1's applicability check, fresh verifier and trust anchors.
- Introduce wrong-but-plausible native semantic implementations in disposable dbt/MetricFlow copies. Examples:
  - `>` instead of `>=` at exactly 100;
  - `!= 'cancelled'` instead of `= 'completed'`;
  - store instead of customer country.
- Show that each one is detected with a counterexample.

One design note to carry into E4: E3.1 catches a rewritten approved reading through the trusted
reading-meaning hash. Binding approvals to that hash would make the protection explicit in the IR itself.

**STOP: E4–E8 were not started.**
