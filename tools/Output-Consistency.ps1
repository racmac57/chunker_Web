param(
  [string]$OD = $env:OneDriveCommercial,
  [string]$Name = "consistency_test.md"
)

$watch = Join-Path $OD "KB_Shared\02_data"
$outputRoot = Join-Path $OD "KB_Shared\04_output"

if (-not (Test-Path $watch)) {
  Write-Host "Watch folder missing: $watch"
  exit 1
}

if (-not (Test-Path $outputRoot)) {
  Write-Host "Output folder missing: $outputRoot"
  exit 1
}

$content = "output consistency smoke"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace "-"

Write-Host "Content SHA256: $hash"

$target = Join-Path $watch $Name
$content | Set-Content -Encoding UTF8 $target
Start-Sleep -Seconds 5

$matchingBefore = Get-ChildItem $outputRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*$Name*" }
$latest = Get-ChildItem $outputRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3

Write-Host "First drop complete. Matching artifacts: $($matchingBefore.Count)"
if ($latest) {
  Write-Host "Latest output folders:"
  $latest | Select-Object Name, LastWriteTime | Format-Table | Out-String | Write-Host
}

# Ensure identical content still exists
$content | Set-Content -Encoding UTF8 $target
Start-Sleep -Seconds 5
$content | Set-Content -Encoding UTF8 $target
Start-Sleep -Seconds 5

$matchingAfter = Get-ChildItem $outputRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*$Name*" }

[pscustomobject]@{
  Hash            = $hash
  OutputCountBefore = $matchingBefore.Count
  OutputCountAfter  = $matchingAfter.Count
  Delta             = $matchingAfter.Count - $matchingBefore.Count
} | Format-Table | Out-String | Write-Host

if ($matchingAfter.Count -gt $matchingBefore.Count) {
  Write-Host "Duplicate outputs detected for identical content."
  exit 1
}

Write-Host "Consistency check passed."

