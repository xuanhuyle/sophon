# Sophon JEV V2 library-transfer experiment - operator runbook.
# Run in a NEW PowerShell window, NOT inside Claude Code. -PreflightOnly makes zero network calls and may run anywhere.
# Live phase: at most 31 logical provider calls (9 Jev + 18 reviewer + 3 blind + 1 optional A-only synthesis),
# at most 3 HTTP attempts per call (hard cap 93 attempts). Contract A (GitHub) is NOT re-sent: its V1 recording is reused.
#
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -PreflightOnly
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -Reviewer anthropic
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V2_TRANSFER.ps1 -Reviewer anthropic -LibrarySynthesis   # +1 call
param(
    [ValidateSet("anthropic", "claude-cli")] [string] $Reviewer = "anthropic",
    [string] $Model = "claude-opus-5-5",
    [switch] $PreflightOnly,
    [switch] $LibrarySynthesis
)
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Load ignored repo-root .env if present (same allowlisted, non-executing loader as V1). Never prints values.
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$dotenv = Join-Path $repoRoot ".env"
if (Test-Path -LiteralPath $dotenv -PathType Leaf) {
    foreach ($rawLine in [System.IO.File]::ReadAllLines($dotenv)) {
        $line = $rawLine.Trim()
        if (-not $line -or $line.StartsWith("#")) { continue }
        $parts = $line -split "=", 2
        if ($parts.Count -ne 2) { continue }
        $key = $parts[0].Trim()
        if ($key -notin @("TYPESAFE_API_KEY", "ANTHROPIC_API_KEY")) { continue }
        $value = $parts[1].Trim()
        if ($value.Length -ge 2 -and
            (($value.StartsWith('"') -and $value.EndsWith('"')) -or
             ($value.StartsWith("'") -and $value.EndsWith("'")))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        if ($value -and -not [Environment]::GetEnvironmentVariable($key, "Process")) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

$synth = @()
if ($LibrarySynthesis) { $synth = @("--library-synthesis") }

# 1. Offline integrity: frozen packets, libraries, context sidecars (no network).
python transfer.py --mode validate
if ($LASTEXITCODE -ne 0) { throw "Offline validation failed; nothing was sent." }

# 2. Readiness: verifies the genuine GitHub recording, library v1 lineage, caps and cost estimate (no network).
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
New-Item -ItemType Directory -Force -Path "live_runs" | Out-Null
$pre = "live_runs/preflight_$stamp.json"
python transfer.py --mode preflight --reviewer $Reviewer --model $Model @synth | Tee-Object -FilePath $pre
$preExit = $LASTEXITCODE
if ($PreflightOnly) {
    if ($preExit -ne 0) { Write-Host "Preflight reported blockers (see $pre); no provider calls made."; exit 2 }
    Write-Host "Preflight successful; no provider calls made."
    exit 0
}
if ($env:CLAUDECODE) { throw "This shell is inside Claude Code. Open a new terminal and rerun." }
if ($preExit -ne 0) { throw "Preflight reported blockers; nothing was sent." }

# 3. Explicit authorization for the paid calls. The dollar figure is an estimate, not a guarantee; there is no enforceable spend cap.
$plan = (Get-Content $pre -Raw | ConvertFrom-Json)
$calls = $plan.planned_calls.total_logical
$usd = $plan.cost_estimate.llm_usd_est_api_list_price
Write-Host "About to make $calls logical provider calls (hard cap 31; up to $($plan.caps.max_possible_attempts) HTTP attempts incl. retries): $($plan.planned_calls.jev) Jev + $($plan.planned_calls.reviewer_llm + $plan.planned_calls.blind_llm + $plan.planned_calls.synthesis_llm) Claude ($Model)."
Write-Host "Estimated Claude cost at API list price: about USD $usd (estimate only; thinking/long outputs vary). Jev: about USD $($plan.cost_estimate.jev_usd_est)."
Write-Host "Contract A (GitHub) is reused from the V1 recording: 0 new A calls. The three Google packets will be transmitted to TypeSafe and Anthropic."
if ((Read-Host "Type YES to authorize the whole quoted ceiling (anything else aborts)") -ne "YES") { throw "Not authorized; nothing was sent." }

# 4. Live run (partial evidence is kept on failure; never rerun silently).
$live = "live_runs/live_V2_$stamp.json"
python transfer.py --mode live --allow-external-calls --reviewer $Reviewer --model $Model @synth --output $live
if ($LASTEXITCODE -ne 0) { throw "Live run failed or was budget-stopped; partial evidence (if any) is in $live. Record the failure; do not rerun silently." }

# 5. Offline replay from the stored raw outputs, then scoring against the sealed provisional checklist (zero network).
python transfer.py --mode replay --recorded $live --output "live_runs/replay_V2_$stamp.json"
if ($LASTEXITCODE -ne 0) { throw "Replay failed." }
python transfer.py --mode score --recorded "live_runs/replay_V2_$stamp.json" --output "live_runs/score_V2_$stamp.json" | Out-File -FilePath "live_runs/score_V2_$stamp.md" -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "Scoring failed. Inspect the run artifacts; do not treat this run as complete." }
Get-Content "live_runs/score_V2_$stamp.md"

# 6. SHA receipts for the raw local evidence (live_runs/ is git-ignored; commit only receipts and redacted summaries).
$receipts = @{}
foreach ($f in Get-ChildItem "live_runs" -Filter "*_$stamp.*") { $receipts[$f.Name] = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLower() }
$receipts | ConvertTo-Json | Out-File -FilePath "receipts_$stamp.json" -Encoding utf8
Write-Host "Done. Raw evidence stays in live_runs/ (ignored). Review it for sensitive data; commit receipts_$stamp.json and a redacted summary in V2_TRANSFER_RESULTS.md."
Remove-Item Env:TYPESAFE_API_KEY -ErrorAction SilentlyContinue
