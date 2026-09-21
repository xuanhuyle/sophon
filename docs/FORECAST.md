# Forecast, written before the lab was run

Recorded 2026-09-21, after both arms decided the 48 cases identically with zero settlements, and **before**
`lab/probes.py` or `lab/run_lab.py` existed or had been run. `results/forecast.sha256` holds this file's hash and
the time it was written. There is no commit to prove the ordering, because I was not asked to commit; treat the
ordering as my word plus the file timestamps.

My working conclusion going in: *the deterministic "authority kernel" is not where Sophon's novelty or risk is; a
competent policy-as-code setup plus a handful of disciplines gives the same decisions and the same safety properties.*
These are the results that would change that conclusion.

| # | Forecast | What would prove me wrong |
|---|---|---|
| F1 | Across the whole grid of possible owner settlements, the ledger arm and the baseline arm (with or without conventions) give **identical decisions on all 48 cases**. | Any disagreement. It would mark a place where the architectures differ on ordinary cases, not only on adversarial ones. |
| F2 | On the adversarial probes the ledger passes all, the baseline with all five conventions passes all, and the first-pass baseline fails **8–10 of about 17**. It fails: pre-adoption, bounded delegation, self-dealing, future effective date, version timing, amendment suspension, replay/one-shot, unknown category, mislabelled act. It passes: proposals inert, case remedy does not spread, expiry, revocation, supersession, as-of history, missing fact, non-finite amount, line-item. | The disciplined baseline failing a probe. That would be a property the conventions cannot supply, i.e. a real reason for a purpose-built kernel. |
| F3 | Each probe the first-pass baseline fails is fixed by exactly **one** convention. | A probe that needs several conventions at once, or none of them. |
| F4 | Settlements can decide at most **12 of the 24** held-out cases under any owner choices in the grid, and the count is a pure function of where thresholds sit relative to the designed amounts. Both arms report the same count for every settlement. | More than 12, or arms disagreeing on the count. |
| F5 | My own probe suite, on its first run, will leave **at least one** seeded fault in the ledger arm undetected (most likely `ignore_supersession` or `ignore_version_timing`). I hold my probes to the mutation standard I applied to the packet's guards. | Zero surviving mutants on the first run would mean I under-estimated the suite. |

Not forecast, because I had already seen the first-pass codings when I wrote this: anything about the 46-document
corpus study.
