param(
  [ValidateSet("dedupe_on","dedupe_off","incr_on","incr_off")]
  [string]$Mode,
  [string]$Cfg = "config.json"
)

if (!(Test-Path $Cfg)) {
  Write-Host "Config file not found: $Cfg"
  exit 1
}

$cfg = Get-Content $Cfg -Raw | ConvertFrom-Json

switch ($Mode) {
  "dedupe_on" { $cfg.deduplication.enabled = $true }
  "dedupe_off" { $cfg.deduplication.enabled = $false }
  "incr_on" { $cfg.incremental_updates.enabled = $true }
  "incr_off" { $cfg.incremental_updates.enabled = $false }
}

$cfg | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $Cfg
Write-Host "Updated: $Mode"

