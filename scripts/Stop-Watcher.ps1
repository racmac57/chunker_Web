param(
  [string]$RepoRoot = "$PSScriptRoot\.."
)

$pidFile = Join-Path $RepoRoot "watcher_pid.txt"
if (!(Test-Path $pidFile)) {
  Write-Host "No PID file."
  exit 0
}

$pid = Get-Content $pidFile | Select-Object -First 1
if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
  Stop-Process -Id $pid -Force
  Write-Host "Stopped watcher PID=$pid"
}

Remove-Item $pidFile -ErrorAction SilentlyContinue

