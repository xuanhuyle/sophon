# Execute frozen Sophon V4 after SEC access is enabled

**Repository:** `xuanhuyle/sophon`  
**Starting branch:** `experiment/jev-v4-sequential-provision-learning-2026-10-13` (PR #18)  
**Expected starting HEAD:** `52d74c96ed08a4e2d446632b33e61dd729c6baf9` (or later commit adding this operational instruction only)  
**Target:** existing PR #18, NOT main.  
**Purpose:** finish the already-frozen experiment; NOT a new design or another synthetic-fixture exercise.

First fetch current remote refs, confirm exact branch/head and inspect the frozen `prototype/contract_sequential_learning_v4/PROTOCOL.md`, `frozen/freeze_receipt.json`, `RESULTS.md`, `RUNBOOK_V4.ps1`. Read current `SOPHON_CHARTER.md`, `PROJECT_STATE.json`, `ENGINEERING_WORKFLOW.md` from `origin/main`. Do not change protocol, selection rules, test target logic, source URLs or frozen code to make a result look positive. No new PR.

**Preflight:** verify the **current Claude cloud environment** has network egress to `efts.sec.gov`, `www.sec.gov`, and `data.sec.gov`. Distinguish proxy CONNECT 403 (environment allowlist), SEC HTTP 403/429 (server/fair-access), and script/API failures. If egress remains blocked, STOP with the observed error; do not author more experimental code.

`SEC_USER_AGENT` is required for SEC access. It must be provided through the environment settings using an owner-approved contact identity. Do not insert a private email in chat transcripts, a GitHub commit, script literals, or logs. If unset, report precisely that it is missing and STOP; do not invent an identity.

If network and environment variables work, execute **the existing frozen pipeline** in `prototype/contract_sequential_learning_v4/`: `python -m unittest test_v4 -v`, `python v4_corpus.py fetch --raw-dir raw`, `python v4_corpus.py build --raw-dir raw`, `python v4_sequential.py run`, `python v4_sequential.py replay`. Linux cloud sessions should use these commands directly; `RUNBOOK_V4.ps1` is for PowerShell, not required in Linux.

Require eight eligible authentic complete SEC exhibits under the frozen eligibility rule; do not hand-select replacements or include already-seen V3 docs. If insufficient, mark `BLOCKED_INSUFFICIENT_CORPUS` and STOP. Predictions MUST be sealed before revealing target body text. Never perform a new freeze/revision just because the data produce a bad result. Record any implementation defect as a separate deviation rather than silently retrofitting the frozen experiment.

Only if a valid authentic run completes: review per-contract scores, source provenance, first-run prediction receipts, honest negative/control outcomes and independent replay, then commit the **permitted derived evidence** to the current PR #18 branch. Raw contract bodies stay in `raw/` and `local_hidden/` (gitignored), not in the PR; do not add personal contact information. Clearly qualify headings/semantic labels as rule-authored provisional and text-feature regex scores as *textual proxies*, not proof of contractual understanding. Conclude `KEEP / REVISE / STOP / INCONCLUSIVE` only to the extent supported by the frozen protocol, naming the exact scope.

No paid provider calls, additional architecture, synthetic-as-evidence substitution, benchmark corpus, changes to main, or automatic new research tasks. Report the actual run/blocker, document IDs, outcome, commit SHA if changed, and STOP.
