# Measurement V0 — decision

**Task outcome: `MEASURED_BASELINE`.** There is one externally grounded, reproducible baseline observation: baseline-A on PolicyEngine-US PRE `5152b5f7` against 7 CFR 273.10(e)(2)(ii)(A) and 7 U.S.C. 2017(a) scored **`BASELINE_CORRECT` (`DETECTED_MISMATCH`)**. It took 4 min 53 s with no human effort in the run.

## Recommendation: KEEP the method, REVISE two instrument details, STOP this experiment

- **KEEP** the measurement procedure:
  - a pinned public governing source and an independently authored implementation with a real historical defect;
  - an oracle built from source arithmetic plus native execution, frozen before the run;
  - a fresh, repo-less, transcript-audited Claude Code session as the conventional baseline.

  It produced a scoreable observation in under 20 minutes of total setup, it is replayable, and it can fail.
- **REVISE before any reuse:**
  1. Fix the scorer's POST rule ordering so a `CONFORMS` finding outranks a `STATE_OPTION_DEPENDENT` label when the report states the options are equivalent. Add that pattern as a control. Do this only on a new protocol, not retroactively here.
  2. Use paired negative controls whose visible history does not narrate the fix.
- **STOP** here. Do not add a Sophon arm, an E6 or a second case to this PR.

## What this changes

- It is evidence against assuming that a conventional AI-assisted workflow cannot *assess* a narrow, explicitly posed governing-rule/implementation alignment. On this case it can, quickly.
- Any future Sophon-vs-baseline comparison must therefore target something this baseline did *not* get for free:
  - discovering *which* requirement–implementation pairs to check after a source or code change, without a pre-scoped question;
  - harder, cross-referenced contractual meaning;
  - durable, replayable traceability across revisions.

  That is a hypothesis for the engineering lead's review. It is not authorized work.

## Strongest contrary consideration

The case is easy and arithmetic, and the question was narrowly scoped. A harder, real contractual case might defeat the same baseline. One observation cannot distinguish "the baseline is generally strong" from "this case was easy".

**Condition that would reverse the KEEP:** an independent reviewer finds leakage in the transcripts, an oracle error (for example, an amendment to (e)(2)(ii)(A) effective before 2026-01), or that the baseline's finding did not rest on its own evidence.

## Next increment (not started)

If the engineering lead wants a next increment, it is a preregistered comparison on a *separately held-out* external case, chosen before either arm runs. It is not an enlargement of this experiment.

**STOP for independent engineering-lead review.**
