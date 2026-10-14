# V4 sequential run on authentic SEC EDGAR credit agreements. Operator-local (SEC must be reachable).
# 0 provider calls. Raw exhibits and bodies stay in .\raw and .\local_hidden (gitignored).
# Usage (PowerShell, repo checkout of PR #18 branch):
#   $env:SEC_USER_AGENT = "<your name> <contact email>"     # SEC fair-access policy; not stored in the repo
#   .\RUNBOOK_V4.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not $env:SEC_USER_AGENT) { throw "Set SEC_USER_AGENT first" }
python -m unittest test_v4 -v                                   # synthetic plumbing tests only
python v4_corpus.py fetch --raw-dir raw                          # frozen content-blind selection -> data/source_manifest.json
python v4_corpus.py build --raw-dir raw                          # views (committed) + local hidden bodies
python v4_sequential.py run                                      # refuses if frozen files changed
python v4_sequential.py replay                                   # must print replay_identical_sealed_predictions: true
git add data results
git commit -m "V4: first sequential run on authentic EDGAR credit agreements (0 provider calls)"
git push origin HEAD:experiment/jev-v4-sequential-provision-learning-2026-10-13
