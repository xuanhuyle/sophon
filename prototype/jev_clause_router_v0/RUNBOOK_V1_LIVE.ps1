# Sophon JEV V1 live pilot - operator runbook.
# Run in a NEW PowerShell window, NOT inside Claude Code (nested Claude Code reviewer calls are refused).
# Sends 10 short excerpts (5 LAB + 5 public GitHub SLA) to TypeSafe and to Claude. No confidential text.
#
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V1_LIVE.ps1 -Reviewer anthropic
#   powershell -ExecutionPolicy Bypass -File .\RUNBOOK_V1_LIVE.ps1 -Reviewer claude-cli   # Claude subscription login, no API key
param(
    [ValidateSet("anthropic", "claude-cli")] [string] $Reviewer = "anthropic",
    [string] $Model = "claude-opus-5-5"
)
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
if ($env:CLAUDECODE) { throw "This shell is inside Claude Code. Open a new terminal and rerun." }

function Read-Secret([string] $Prompt) {
    $secure = Read-Host $Prompt -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}
if (-not $env:TYPESAFE_API_KEY) { $env:TYPESAFE_API_KEY = Read-Secret "TypeSafe API key (not echoed)" }
if ($Reviewer -eq "anthropic" -and -not $env:ANTHROPIC_API_KEY) { $env:ANTHROPIC_API_KEY = Read-Secret "Anthropic API key (not echoed)" }

$models = @("--adversarial-model", $Model, "--backward-model", $Model, "--baseline-model", $Model)

# 1. Readiness check: no network calls, no secret values printed.
python prototype.py --mode preflight --reviewer $Reviewer @models --clauses clauses.json --clauses external_github_sla_2021.json
if ($LASTEXITCODE -ne 0) { throw "Preflight reported blockers; nothing was sent." }

# 2. Explicit authorization for the paid/quota calls.
Write-Host "About to make 40 provider calls: 10 Jev (about USD 0.001) + 30 Claude ($Model; about USD 1.6 at API list price, or subscription quota via claude-cli)."
if ((Read-Host "Type YES to proceed") -ne "YES") { throw "Not authorized; nothing was sent." }

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
New-Item -ItemType Directory -Force -Path "live_runs" | Out-Null
foreach ($pair in @(@("LAB", "clauses.json"), @("EXT", "external_github_sla_2021.json"))) {
    $tag, $corpus = $pair
    $live = "live_runs/live_${tag}_$stamp.json"
    python prototype.py --mode live --allow-external-calls --reviewer $Reviewer @models --clauses $corpus --output $live
    if ($LASTEXITCODE -ne 0) { throw "Live run $tag failed; partial evidence (if any) is in $live. Do not rerun silently; record the failure." }
    # 3. Offline replay from the stored raw outputs (zero network).
    python prototype.py --mode replay --clauses $corpus --recorded $live --output "live_runs/replay_${tag}_$stamp.json"
    if ($LASTEXITCODE -ne 0) { throw "Replay $tag failed." }
}

# 4. Mechanical A/B/C/D comparison against the frozen provisional matrix.
python compare.py "live_runs/replay_LAB_$stamp.json" "live_runs/replay_EXT_$stamp.json" --json-out "live_runs/compare_$stamp.json" | Tee-Object -FilePath "live_runs/compare_$stamp.md"
Write-Host "Done. Commit live_runs/*_$stamp.* unchanged, then fill in V1_LIVE_RESULTS.md section 'Live run'."
Remove-Item Env:TYPESAFE_API_KEY -ErrorAction SilentlyContinue
