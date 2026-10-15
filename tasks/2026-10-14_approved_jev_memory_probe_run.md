# Execute the authorized 20-call Jev memory probe — no feature additions

**Owner approved paid execution on 2026-10-14 in Sophon conversation.** The approved budget is EXACTLY 20 Jev provider requests (10 source excerpts x COLD/LEARNED). No Anthropic, no stronger-model comparisons, no new reviewers, no access to any unapproved account. Use the existing runnable `prototype/jev_memory_causal_probe_v0/probe.py` and no alternate harness.

**Target:** `xuanhuyle/sophon`, existing **draft PR #22**, branch `research/classification-library-headroom-2026-10-14`. Do not merge; do not start the follow-up stage. Read `SOPHON_CHARTER.md`, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md`, `prototype/jev_memory_causal_probe_v0/README.md` and the live Python code. Independently flag any real blocker before spending money; do not use this instruction to create more architecture.

## Hard facts / interpretability limit

- This prototype does **NOT** autonomously segment and classify sub-provisions. `CASES` contains **manually chosen** source excerpts, and each receives 10 **multi-label** Jev Noul questions. There are also two **full compound-provision passages**. None of the output labels is attached by Jev to an independently discovered internal span. Do **NOT** claim automatic sub-provision classification.
- This is one provisional GitHub -> Google library transfer; **not a demonstration of cumulative self-improvement across multiple contracts**.
- The 16 source-quoted positive probes are engineering-selected, not independent legal-function truth. Probabilities and quote anchors do not validate entire legal interpretations.
- Same Jev model, same questions, same source/context. **Only** `prior_provision_skeletons` differs between COLD and LEARNED. Neither the model nor the taxonomy may be changed mid-run.

## Run in the UPDATED Claude Code cloud environment (preferred as of 2026-10-15)

The owner reports having configured the TypeSafe API credential in the Claude Code cloud environment. **Start a NEW cloud session attached to that UPDATED environment**: editing an environment does not necessarily inject new secrets into an already-running container. Do not assume the credential is accessible merely because it was saved in settings.

Verify only **presence**, NEVER the credential's value:

```bash
git fetch origin
git switch research/classification-library-headroom-2026-10-14
git pull --ff-only
python -c "import os; print('TYPESAFE_API_KEY available:', bool(os.environ.get('TYPESAFE_API_KEY')))"
python prototype/jev_memory_causal_probe_v0/probe.py preflight
python -m unittest discover -s prototype/jev_memory_causal_probe_v0 -p 'test_*.py' -v
```

If key presence is false, check whether the setting was saved under **environment variables** (the Python client needs `TYPESAFE_API_KEY`), rather than only a Network secret or a configuration on a different cloud environment. Report a blocker rather than querying/printing secrets; do not attempt a paid call yet. The API hostname `api.typesafe.ai` must be reachable. A cloud Network secret not surfaced to the process as `TYPESAFE_API_KEY` is insufficient for this existing Python client.

If key is present, preflight and tests pass, and there is no existing `prototype/jev_memory_causal_probe_v0/live_runs/jev_memory_20261014_approved_001.json`, **perform the owner's already-authorized 20-call experiment once**:

```bash
python prototype/jev_memory_causal_probe_v0/probe.py live --confirm-paid-calls YES --output prototype/jev_memory_causal_probe_v0/live_runs/jev_memory_20261014_approved_001.json
python prototype/jev_memory_causal_probe_v0/probe.py score --recorded prototype/jev_memory_causal_probe_v0/live_runs/jev_memory_20261014_approved_001.json
```

If a recording exists, inspect its non-secret metadata and progress first; **never repeat paid calls** or discard a partial recording without permission. The script checkpoints responses after each successful call. Follow reporting and STOP rules below.

## Local Windows PowerShell fallback



**Credential fix (2026-10-14):** the owner has already provided API credentials in a local `.env` file. `probe.py live` now reads `TYPESAFE_API_KEY` automatically from the existing process environment, or `<repo-root>/.env`, or `prototype/jev_memory_causal_probe_v0/.env` in that order **only after** the explicit paid-call confirmation. No `python-dotenv` package or manual PowerShell export is necessary. These `.env` files are gitignored and the key is never printed. Do **not** ask for it again.

**Location boundary:** a Claude Code cloud container has a different filesystem from the owner's Windows machine. It cannot see the owner's local `.env` unless the file is actually present there. Run the following from the owner's local PowerShell in the repository checkout, where `.env` already exists; alternatively the user can configure `TYPESAFE_API_KEY` as a cloud-environment secret. Do not copy the .env into the Git repository, chat, PR, or CI. If neither the environment nor either existing eligible `.env` in the current runtime has the key, report `BLOCKED_NO_TYPESAFE_KEY_IN_THIS_RUNTIME`; do not conduct searches for secrets.

```powershell
cd C:\Claude\sophon
git fetch origin
git switch research/classification-library-headroom-2026-10-14
git pull --ff-only
python prototype/jev_memory_causal_probe_v0/probe.py preflight
python -m unittest discover -s prototype/jev_memory_causal_probe_v0 -p 'test_*.py' -v

# The user has already authorized up to 20 calls. Do not run this twice.
# No environment-variable export required; probe.py safely reads the existing .env.
# This check shows existence ONLY, not the secret's contents:
Write-Host "Local repo .env exists: $(Test-Path .\.env)"
$record = "prototype/jev_memory_causal_probe_v0/live_runs/jev_memory_20261014_approved_001.json"
if (Test-Path $record) { throw "Record already exists; do not rerun without checking it" }
python prototype/jev_memory_causal_probe_v0/probe.py live --confirm-paid-calls YES --output $record
python prototype/jev_memory_causal_probe_v0/probe.py score --recorded $record
```

The script caps at 20 calls, uses no silent retries or alternative providers and writes each returned raw response to a gitignored local file. If interrupted, STOP. Do not relaunch a complete 20-call run without inspecting that file and obtaining new authorization for any additional calls. On invalid provider schema (e.g. unsupported Noul shape or state content), STOP at first failure; do not silently swap model/prompt.

## Post-run report, evidence, stop

In **this same PR**, create a short `prototype/jev_memory_causal_probe_v0/LIVE_RESULTS.md` summarizing only what was **actually observed** (call counts, actual model version, arm input parity and hashes, key per-case outcome, positive probes newly detected/lost, any unsupported transfer, cost/latency if metadata supports it, and why these cannot be treated as certified legal accuracy). Commit a raw-run SHA-256 receipt but **do not commit the raw provider recording, keys, user paths or unredacted model prompts**. Note incomplete runs as incomplete; do not manufacture results.

Critical distinctions: `MANUALLY_CURATED_SOURCE_EXCERPTS`, `MULTI_LABEL_PER_EXCERPT`, `AUTOMATIC_SUBPROVISION_SEGMENTATION_NOT_IMPLEMENTED`. No signal or ceiling is an **INCONCLUSIVE** result, not an arbitrary global STOP for Sophon.

Run tests/CI, push to existing PR #22, and **STOP**. Do not add an automatic segmentation system in this paid-call task; plan it as a separately justified follow-up only after inspecting evidence. Do not ask the owner for further permission for these 20 specifically authorized calls; do ask before **any** additional paid or outside-scope calls.
