# Execute the authorized 20-call Jev memory probe — no feature additions

**Owner approved paid execution on 2026-10-14 in Sophon conversation.** The approved budget is EXACTLY 20 Jev provider requests (10 source excerpts x COLD/LEARNED). No Anthropic, no stronger-model comparisons, no new reviewers, no access to any unapproved account. Use the existing runnable `prototype/jev_memory_causal_probe_v0/probe.py` and no alternate harness.

**Target:** `xuanhuyle/sophon`, existing **draft PR #22**, branch `research/classification-library-headroom-2026-10-14`. Do not merge; do not start the follow-up stage. Read `SOPHON_CHARTER.md`, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md`, `prototype/jev_memory_causal_probe_v0/README.md` and the live Python code. Independently flag any real blocker before spending money; do not use this instruction to create more architecture.

## Hard facts / interpretability limit

- This prototype does **NOT** autonomously segment and classify sub-provisions. `CASES` contains **manually chosen** source excerpts, and each receives 10 **multi-label** Jev Noul questions. There are also two **full compound-provision passages**. None of the output labels is attached by Jev to an independently discovered internal span. Do **NOT** claim automatic sub-provision classification.
- This is one provisional GitHub -> Google library transfer; **not a demonstration of cumulative self-improvement across multiple contracts**.
- The 16 source-quoted positive probes are engineering-selected, not independent legal-function truth. Probabilities and quote anchors do not validate entire legal interpretations.
- Same Jev model, same questions, same source/context. **Only** `prior_provision_skeletons` differs between COLD and LEARNED. Neither the model nor the taxonomy may be changed mid-run.

## Run this exact bounded sequence in the user's local authorized environment

The user previously ran real Jev calls locally; do not assume Claude Code's remote session has `TYPESAFE_API_KEY`. Never search the user's whole machine for keys, print the key, upload it to GitHub, or put credentials in chat/logs. Use a local PowerShell session where the key is *already* configured. If the key is not present, **STOP with `BLOCKED_NO_TYPESAFE_KEY` and provide the local command for the user**, rather than a fake execution.

```powershell
cd C:\Claude\sophon
git fetch origin
git switch research/classification-library-headroom-2026-10-14
git pull --ff-only
python prototype/jev_memory_causal_probe_v0/probe.py preflight
python -m unittest discover -s prototype/jev_memory_causal_probe_v0 -p 'test_*.py' -v

# The user has already authorized up to 20 calls. Do not run this twice.
if (-not $env:TYPESAFE_API_KEY) { throw "BLOCKED_NO_TYPESAFE_KEY (configure it privately in this shell)" }
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
