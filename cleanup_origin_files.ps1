# Cleanup .origin.json metadata files from Desktop
# This script removes all .origin.json files and nested .origin.json.origin.json files

$desktopPath = "C:\Users\carucci_r\OneDrive - City of Hackensack\Desktop"

Write-Host "===============================================" -ForegroundColor White
Write-Host "Cleaning up .origin.json metadata files" -ForegroundColor White
Write-Host "===============================================" -ForegroundColor White
Write-Host ""

if (-not (Test-Path $desktopPath)) {
    Write-Host "ERROR: Desktop path not found: $desktopPath" -ForegroundColor Red
    exit 1
}

# Find all files with .origin.json in the name
$originFiles = Get-ChildItem -Path $desktopPath -File -Force | Where-Object { 
    $_.Name -match '\.origin\.json' 
}

if ($originFiles.Count -eq 0) {
    Write-Host "No .origin.json files found on Desktop." -ForegroundColor Green
    Write-Host ""
    exit 0
}

Write-Host "Found $($originFiles.Count) .origin.json file(s) to remove:" -ForegroundColor Yellow
Write-Host ""

$deletedCount = 0
$errorCount = 0

foreach ($file in $originFiles) {
    try {
        Write-Host "  Removing: $($file.Name)" -ForegroundColor Gray
        Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
        $deletedCount++
    } catch {
        Write-Host "  ERROR: Could not remove $($file.Name): $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor White
Write-Host "Cleanup Complete" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor White
Write-Host "Files deleted: $deletedCount" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "Errors: $errorCount" -ForegroundColor Red
}
Write-Host ""

