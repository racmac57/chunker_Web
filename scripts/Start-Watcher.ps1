param(
  [string]$RepoRoot = "$PSScriptRoot\.."
)

Set-Location $RepoRoot
$env:PYTHONUNBUFFERED = "1"
$pidFile = Join-Path $RepoRoot "watcher_pid.txt"

if (Test-Path $pidFile) {
  $pid = Get-Content $pidFile | Select-Object -First 1
  if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
    Write-Host "Watcher already running. PID=$pid"
    exit 0
  }
}

Start-Process -FilePath "python" -ArgumentList "watcher_splitter.py" -WorkingDirectory $RepoRoot -NoNewWindow
Start-Sleep -Seconds 2
Get-Process python | Where-Object { $_.Path -like "*python*" } | Sort-Object StartTime -Descending | Select-Object -First 1 | ForEach-Object {
  $_.Id | Out-File -Encoding ascii -FilePath $pidFile -Force
  Write-Host "Watcher started. PID=$($_.Id)"
}

