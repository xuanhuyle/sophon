# Jev memory probe v0 — live run status

**Status: `BLOCKED_NETWORK_POLICY_DENIES_API_TYPESAFE_AI`. 0 of 20 authorized Jev calls made. No results exist.**

The owner has authorized 20 Jev calls (10 cases × COLD/LEARNED; `tasks/2026-10-14_approved_jev_memory_probe_run.md`). No classification result exists, so there is **no evidence that the library improved, degraded or left unchanged the measured behaviour**.

## Attempt 2 — Claude Code cloud session, 2026-10-15

| Check | Result |
|---|---|
| `TYPESAFE_API_KEY` in the process environment | **Present**: 108 characters. The value was never displayed. No `.env` file is used in this runtime. |
| `probe.py preflight` | `READY_FOR_OPTIONAL_PROVIDER_RUN_NOT_LEGAL_ORACLE`: 10 cases, 20 planned calls, 16 positive probes. Hashes below. |
| Probe unit tests / context guard | Pass / `SOPHON_CONTEXT_GUARD_OK` |
| Existing recording `live_runs/jev_memory_20261014_approved_001.json` | None. |
| Reachability of `api.typesafe.ai:443` | **Denied.** The environment's egress proxy answered `403 Forbidden` to `CONNECT`, and the proxy logged a policy denial (10:56:26Z). The check was a tunnel request only: no HTTP request reached the API and nothing was billed. |

**Why `live` was not started.** The first request could not reach the API. Starting `live` would only have created an empty `INCOMPLETE` recording. Under the runbook's no-repeat rule, that file would then block the real run. No provider call, retry or fallback was attempted.

**Unblock.** Add `api.typesafe.ai` to the cloud environment's **Allowed domains** under Network access (keep "Allow package managers" ticked), or choose a broader access level. Then run the two runbook commands once in a new session. The local Windows PowerShell fallback in the runbook also remains valid.

Frozen plan (unchanged since attempt 1):
- `plan_sha256` `e52eb9e007bb0bf5c04f597cd0ff86ac9efad361e33ed5c4c75cc4189fd9989e`
- `questions_sha256` `eebc825204636d4cacfcdf99375f474cb70c41c5b644a16abafb70858a30ef08`
- `library_sha256` `bc8086d73116ba9460f3c0cca10a6ed011b69878368402dae56574780518fc45`

## Attempt 1 — 2026-10-14

`BLOCKED_NO_TYPESAFE_KEY`: the key was absent from the container, and 0 calls were made. In the same session, a relative `--output` path was found to be rejected by the `live_runs/` guard. `probe.py` now resolves the path before the check.

Whenever results do exist, they must be reported as `MANUALLY_CURATED_SOURCE_EXCERPTS`, `MULTI_LABEL_PER_EXCERPT` and `AUTOMATIC_SUBPROVISION_SEGMENTATION_NOT_IMPLEMENTED`, not as legal accuracy.
