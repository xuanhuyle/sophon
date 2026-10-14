# Jev memory probe v0 — live run status

**Status: `BLOCKED_NO_TYPESAFE_KEY`. 0 of 20 authorized Jev calls made. No results exist.**

The owner authorized 20 Jev calls (10 cases × COLD/LEARNED) on 2026-10-14 (`tasks/2026-10-14_approved_jev_memory_probe_run.md`). The execution attempt ran in Claude Code's remote cloud container, which has no `TYPESAFE_API_KEY`. Per the task, no machine-wide key search was made. Nothing was substituted, mocked or replayed in its place. No recording file exists.

## Verified offline before the attempt

- `probe.py preflight`: `READY_FOR_OPTIONAL_PROVIDER_RUN_NOT_LEGAL_ORACLE`
  - 10 cases, 20 planned calls, 16 positive probes, model requested `jev-latest`
  - `plan_sha256` `e52eb9e007bb0bf5c04f597cd0ff86ac9efad361e33ed5c4c75cc4189fd9989e`
  - `questions_sha256` `eebc825204636d4cacfcdf99375f474cb70c41c5b644a16abafb70858a30ef08`
  - `library_sha256` `bc8086d73116ba9460f3c0cca10a6ed011b69878368402dae56574780518fc45`
- Unit tests: 8/8 pass.
- `live` without a key refuses before any network call (exit 2), and no recording file is created.

## Defect fixed before any paid call

The runbook's relative `--output` path was **rejected** by the `live_runs/` guard. The guard compared an absolute directory with relative path parents, so it errored before any call. `probe.py` now resolves `--output` first. The guard itself is unchanged. The plan hash is unchanged.

## To run (unchanged budget: exactly 20 calls, once)

Run it in the owner's local PowerShell, where the key is already set, using the command block in `tasks/2026-10-14_approved_jev_memory_probe_run.md`. Alternatively, add `TYPESAFE_API_KEY` as a secret in the cloud environment settings and start a new session.

Whatever the outcome, results must be reported as `MANUALLY_CURATED_SOURCE_EXCERPTS`, `MULTI_LABEL_PER_EXCERPT` and `AUTOMATIC_SUBPROVISION_SEGMENTATION_NOT_IMPLEMENTED`, not as legal accuracy.
