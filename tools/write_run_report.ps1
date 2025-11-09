param(
  [string]$RepoRoot = "$PSScriptRoot\..",
  [string]$OD = $env:OneDriveCommercial
)

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $RepoRoot ("run_reports\run_" + $ts + ".txt")
New-Item -ItemType Directory -Force -Path (Split-Path $report) | Out-Null

$health = & "$RepoRoot\scripts\KB-Health.ps1" -RepoRoot $RepoRoot -OD $OD | Out-String
$smoke  = & "$RepoRoot\scripts\Smoke-Test.ps1" -OD $OD | Out-String

@"
=== KB RUN REPORT $ts ===
Health:
$health

Smoke Test:
$smoke
"@ | Out-File -Encoding utf8 $report

Write-Host "Report saved to $report"

