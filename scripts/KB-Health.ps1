param(
  [string]$RepoRoot = "$PSScriptRoot\..",
  [string]$OD = $env:OneDriveCommercial
)

$watch = Join-Path $OD "KB_Shared\02_data"
$arc   = Join-Path $OD "KB_Shared\03_archive"
$out   = Join-Path $OD "KB_Shared\04_output"
$pidFile = Join-Path $RepoRoot "watcher_pid.txt"

$watcher = if (Test-Path $pidFile) {
  $pid = Get-Content $pidFile | Select-Object -First 1
  if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
    "Running (PID=$pid)"
  } else {
    "Not running"
  }
} else {
  "Not running"
}

$chromadb = Test-Path (Join-Path $RepoRoot "chroma_db")
$offline  = Test-Path $watch -and Test-Path $arc -and Test-Path $out

[pscustomobject]@{
  Watcher     = $watcher
  OneDriveOK  = $offline
  ChromaDB    = $chromadb
  WatchFolder = $watch
  Archive     = $arc
  Output      = $out
}

