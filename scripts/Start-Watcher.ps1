param(
  [string]$RepoRoot = "$PSScriptRoot\.."
)

Set-Location $RepoRoot
$env:PYTHONUNBUFFERED = "1"
$pidFile = Join-Path $RepoRoot "watcher_pid.txt"

$mutex = New-Object System.Threading.Mutex($false, "Global\KB_Chunker_Watcher")
if (-not $mutex.WaitOne(0, $false)) {
  Write-Host "Watcher already running on this machine."
  exit 0
}

if (Test-Path $pidFile) {
  $pid = Get-Content $pidFile | Select-Object -First 1
  if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
    Write-Host "Watcher already running. PID=$pid"
    $mutex.ReleaseMutex() | Out-Null
    exit 0
  }
}

Start-Process -FilePath "python" -ArgumentList "watcher_splitter.py" -WorkingDirectory $RepoRoot -NoNewWindow
Start-Sleep -Seconds 2
$proc = Get-Process python | Where-Object { $_.Path -like "*python*" } | Sort-Object StartTime -Descending | Select-Object -First 1
if ($null -ne $proc) {
  $proc.Id | Out-File -Encoding ascii -FilePath $pidFile -Force
  Write-Host "Watcher started. PID=$($proc.Id)"
} else {
  Write-Host "Watcher process not found after start attempt."
}

Register-EngineEvent PowerShell.Exiting -Action {
  try {
    if ($null -ne $Event.MessageData.Mutex) {
      $Event.MessageData.Mutex.ReleaseMutex() | Out-Null
    }
  } catch {
  }
} -MessageData @{ Mutex = $mutex } | Out-Null

