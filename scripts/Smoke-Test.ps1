param(
  [string]$OD = $env:OneDriveCommercial,
  [string]$Name = "smoke_test.md"
)

$watch = Join-Path $OD "KB_Shared\02_data"
$arc   = Join-Path $OD "KB_Shared\03_archive"
$out   = Join-Path $OD "KB_Shared\04_output"
$new   = Join-Path $watch $Name

"smoke test $(Get-Date -Format s)" | Set-Content -Encoding UTF8 $new

$archivedPath = Join-Path $arc $Name
$archived = $false
for ($i = 0; $i -lt 15; $i++) {
  if (Test-Path $archivedPath) {
    $archived = $true
    break
  }
  Start-Sleep -Seconds 1
}

$latestOut = @()
if (Test-Path $out) {
  $latestOut = Get-ChildItem $out -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
}

[pscustomobject]@{
  Dropped    = $new
  Archived   = $archived
  OutputTop3 = ($latestOut | Select-Object Name, LastWriteTime | Out-String).Trim()
}

