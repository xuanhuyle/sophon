# Sophon V3 optional STRONG_LLM_CONTEXT baseline - operator runbook. NOT RUN by Claude Code.
# Run in a NEW PowerShell window outside Claude Code. -PreflightOnly makes zero network calls.
# Live phase: at most 8 logical Anthropic calls (one per heldout case in the secondary repaired set).
#
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V3_LLM_BASELINE.ps1 -PreflightOnly
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V3_LLM_BASELINE.ps1
param([switch] $PreflightOnly)
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$dotenv = Join-Path $repoRoot ".env"
if (Test-Path -LiteralPath $dotenv -PathType Leaf) {
    foreach ($rawLine in [System.IO.File]::ReadAllLines($dotenv)) {
        $line = $rawLine.Trim()
        if (-not $line -or $line.StartsWith("#")) { continue }
        $parts = $line -split "=", 2
        if ($parts.Count -ne 2) { continue }
        $key = $parts[0].Trim()
        if ($key -ne "ANTHROPIC_API_KEY") { continue }
        $value = $parts[1].Trim().Trim('"').Trim("'")
        if ($value -and -not [Environment]::GetEnvironmentVariable($key, "Process")) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

python -m unittest test_v3
if ($LASTEXITCODE -ne 0) { throw "Offline tests failed; nothing was sent." }
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
New-Item -ItemType Directory -Force -Path "live_runs" | Out-Null
$pre = "live_runs/llm_preflight_$stamp.json"
python llm_baseline.py --mode preflight | Tee-Object -FilePath $pre
$preExit = $LASTEXITCODE
if ($PreflightOnly) { if ($preExit -ne 0) { exit 2 }; Write-Host "Preflight only; no provider calls made."; exit 0 }
if ($env:CLAUDECODE) { throw "This shell is inside Claude Code. Open a new terminal and rerun." }
if ($preExit -ne 0) { throw "Preflight reported blockers; nothing was sent." }
$plan = (Get-Content $pre -Raw | ConvertFrom-Json)
if (-not $plan.credentials_present) { throw "ANTHROPIC_API_KEY missing; nothing was sent." }
Write-Host "About to make $($plan.planned_logical_calls) logical calls to $($plan.model) (cap 8). Estimated cost about USD $($plan.cost_estimate_usd) (estimate only; V2's real cost was ~2.7x its estimate)."
Write-Host "Only structural LABELS are sent (no contract text, URLs or issuers)."
if ((Read-Host "Type YES to authorize (anything else aborts)") -ne "YES") { throw "Not authorized; nothing was sent." }
$live = "live_runs/llm_$stamp.json"
python llm_baseline.py --mode live --allow-external-calls --output $live
python llm_baseline.py --mode score --recorded $live | Tee-Object -FilePath "live_runs/llm_score_$stamp.json"
Get-ChildItem live_runs -Filter "*$stamp*" | ForEach-Object { "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), $_.Name } | Out-File -Encoding utf8 "llm_receipts_$stamp.txt"
Write-Host "Done. Commit only llm_receipts_$stamp.txt and a written summary; live_runs/ stays local."
