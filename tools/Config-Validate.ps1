param([string]$Cfg = "config.json")

if (!(Test-Path $Cfg)) {
  Write-Host "Config file not found: $Cfg"
  exit 1
}

$cfg = Get-Content $Cfg -Raw | ConvertFrom-Json
$keys = "watch_folder","archive_dir","output_dir"
$missing = @()
Write-Host "Resolved paths:"
foreach ($k in $keys) {
  $raw = $cfg.$k
  $expanded = if ($raw) { [Environment]::ExpandEnvironmentVariables([string]$raw) } else { "" }
  Write-Host ("  {0}: {1}" -f $k, $expanded)
  if (-not $expanded -or -not (Test-Path $expanded)) {
    $missing += $k
  }
}

Write-Host ("use_event_watcher: {0}" -f $cfg.use_event_watcher)
Write-Host ("file_stability_timeout: {0}" -f $cfg.file_stability_timeout)
Write-Host ("deduplication.enabled: {0}" -f ($cfg.deduplication.enabled))
Write-Host ("incremental_updates.enabled: {0}" -f ($cfg.incremental_updates.enabled))

if ($missing.Count -gt 0) {
  exit 1
} else {
  exit 0
}

