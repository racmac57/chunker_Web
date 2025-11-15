# Send to Chunker - OPTIMIZED VERSION (Move-Based Workflow)
# Moves files/folders from OneDrive to chunker watch folder with origin manifest
# Reduces storage bloat and OneDrive sync overhead by 50%+

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Paths
)

# Fix path handling - Windows "Send to" may pass paths without proper quoting
# Reconstruct paths if they were split on spaces
if ($Paths.Count -gt 0) {
    $fixedPaths = @()
    $currentPath = ""
    
    foreach ($arg in $Paths) {
        if ($arg -match '^[A-Za-z]:\\.*') {
            # This looks like the start of a path
            if ($currentPath) {
                # Save previous path if it exists
                $fixedPaths += $currentPath
            }
            $currentPath = $arg
        } elseif ($currentPath) {
            # Continue building current path (handles spaces in paths)
            $currentPath += " $arg"
        } else {
            # Standalone argument
            $fixedPaths += $arg
        }
    }
    
    # Add the last path
    if ($currentPath) {
        $fixedPaths += $currentPath
    }
    
    $Paths = $fixedPaths
}

$ErrorActionPreference = 'Continue'
$script:HadErrors = $false
$script:FailedFiles = @()
$script:SkippedFiles = 0
$DestFolder = "C:\_chunker\02_data"
$KeyFile = "C:\_chunker\06_config\manifest_hmac.key"

# Ensure destination exists
if (-not (Test-Path $DestFolder)) {
    New-Item -ItemType Directory -Path $DestFolder -Force | Out-Null
}

# Load HMAC key if present
$HmacKey = $null
if (Test-Path $KeyFile) {
    try {
        $HmacKey = [System.IO.File]::ReadAllBytes($KeyFile)
    } catch {
        Write-Warning "Failed to load HMAC key: $_"
    }
}

function Get-FileSHA256 {
    param([string]$Path)
    try {
        $hash = Get-FileHash -Path $Path -Algorithm SHA256
        return $hash.Hash.ToLower()
    } catch {
        return $null
    }
}

function Get-HMACSHA256 {
    param(
        [byte[]]$Key,
        [byte[]]$Data
    )
    try {
        $hmac = New-Object System.Security.Cryptography.HMACSHA256
        $hmac.Key = $Key
        $hashBytes = $hmac.ComputeHash($Data)
        return [System.BitConverter]::ToString($hashBytes).Replace('-','').ToLower()
    } catch {
        return $null
    } finally {
        if ($hmac) { $hmac.Dispose() }
    }
}

function Process-File {
    param(
        [string]$SourcePath,
        [string]$DestPath
    )

    if (-not (Test-Path $SourcePath)) {
        Write-Warning "Source file not found: $SourcePath"
        return
    }

    $destDir = Split-Path $DestPath -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    # Get file info BEFORE move/copy
    $fileInfo = Get-Item $SourcePath
    $sha256 = Get-FileSHA256 -Path $SourcePath

    # Create manifest BEFORE moving file
    $manifest = @{
        original_full_path = $fileInfo.FullName
        original_directory = $fileInfo.DirectoryName
        original_filename = $fileInfo.Name
        sent_at = (Get-Date).ToUniversalTime().ToString("o")
        integrity_sha256 = $sha256
        size_bytes = $fileInfo.Length
        modified_time = $fileInfo.LastWriteTimeUtc.ToString("o")
        created_time = $fileInfo.CreationTimeUtc.ToString("o")
        operation = "MOVE"
        source_cleanup = "pending"
    }

    # Try to MOVE file (primary operation)
    $moveSuccess = $false
    try {
        Move-Item -Path $SourcePath -Destination $DestPath -Force -ErrorAction Stop
        $moveSuccess = $true
        Write-Host "[MOVE] Successfully moved: $($fileInfo.Name)" -ForegroundColor Green

        # Guard against OneDrive or sync clients restoring the original file immediately after move
        Start-Sleep -Milliseconds 500
        if (Test-Path $SourcePath) {
            # Retry removal up to 3 times for OneDrive files
            $removed = $false
            for ($retry = 1; $retry -le 3; $retry++) {
                try {
                    Remove-Item -Path $SourcePath -Force -ErrorAction Stop
                    Start-Sleep -Milliseconds 200
                    if (-not (Test-Path $SourcePath)) {
                        Write-Host "[CLEANUP] Removed residual source copy: $($fileInfo.Name) (attempt $retry)" -ForegroundColor DarkYellow
                        $manifest.source_cleanup = "removed_residual_copy"
                        $removed = $true
                        break
                    }
                } catch {
                    if ($retry -eq 3) {
                        Write-Warning "Residual source copy could not be removed for $($fileInfo.Name) after 3 attempts: $_"
                        Write-Warning "This may be due to OneDrive syncing. File may reappear on desktop."
                        $manifest.source_cleanup = "cleanup_failed"
                        $manifest.source_cleanup_error = $_.ToString()
                        $script:HadErrors = $true
                    } else {
                        Start-Sleep -Milliseconds 300
                    }
                }
            }
            if (-not $removed) {
                Write-Host "[WARNING] Source file still exists: $($fileInfo.Name) - OneDrive may restore it" -ForegroundColor Red
                $script:FailedFiles += $fileInfo.FullName
            }
        } else {
            $manifest.source_cleanup = "not_required"
        }
    } catch {
        $moveError = $_
        # Fallback to COPY if MOVE fails
        Write-Warning "MOVE failed for $($fileInfo.Name): $moveError"
        Write-Warning "Falling back to COPY operation"
        $manifest.operation = "COPY_FALLBACK"
        $manifest.move_error = $moveError.ToString()
        
        try {
            Copy-Item -Path $SourcePath -Destination $DestPath -Force -ErrorAction Stop
            Write-Host "[COPY] Used fallback for: $($fileInfo.Name)" -ForegroundColor Yellow
            
            # Update manifest to reflect we're using original file
            $manifest.fallback_reason = $moveError.ToString()

            Start-Sleep -Milliseconds 500
            if (Test-Path $SourcePath) {
                # Retry removal up to 3 times for OneDrive files
                $removed = $false
                for ($retry = 1; $retry -le 3; $retry++) {
                    try {
                        Remove-Item -Path $SourcePath -Force -ErrorAction Stop
                        Start-Sleep -Milliseconds 200
                        if (-not (Test-Path $SourcePath)) {
                            Write-Host "[CLEANUP] Removed source after copy fallback: $($fileInfo.Name) (attempt $retry)" -ForegroundColor DarkYellow
                            $manifest.source_cleanup = "removed_after_copy"
                            $removed = $true
                            break
                        }
                    } catch {
                        if ($retry -eq 3) {
                            Write-Warning "Failed to remove source after copy fallback for $($fileInfo.Name) after 3 attempts: $_"
                            Write-Warning "This may be due to OneDrive syncing. File may reappear on desktop."
                            $manifest.source_cleanup = "cleanup_failed_after_copy"
                            $manifest.source_cleanup_error = $_.ToString()
                            $script:HadErrors = $true
                        } else {
                            Start-Sleep -Milliseconds 300
                        }
                    }
                }
                if (-not $removed) {
                    Write-Host "[WARNING] Source file still exists: $($fileInfo.Name) - OneDrive may restore it" -ForegroundColor Red
                    $script:FailedFiles += $fileInfo.FullName
                }
            } else {
                $manifest.source_cleanup = "not_found_after_copy"
            }
        } catch {
            Write-Warning "Both MOVE and COPY failed for $SourcePath : $_"
            $manifest.operation = "FAILED"
            $manifest.copy_error = $_.ToString()
            $script:HadErrors = $true
            return
        }
    }

    if (Test-Path $DestPath) {
        $manifest.destination_status = "present"
    } else {
        Write-Warning "Destination missing after operation for $($fileInfo.Name)"
        $manifest.destination_status = "missing"
        $script:HadErrors = $true
    }

    if (Test-Path $SourcePath) {
        Write-Warning "Source still present after operation for $($fileInfo.Name)"
        if ($manifest.source_cleanup -eq "pending") {
            $manifest.source_cleanup = "source_still_present"
        }
        $script:HadErrors = $true
    } elseif ($manifest.source_cleanup -eq "pending") {
        $manifest.source_cleanup = "cleared"
    }

    # Write manifest (regardless of MOVE/COPY)
    try {
        $manifestPath = "$DestPath.origin.json"
        if (-not $manifest.ContainsKey('source_cleanup')) {
            $manifest.source_cleanup = "not_applicable"
        }
        $manifestJson = $manifest | ConvertTo-Json -Depth 10
        
        [System.IO.File]::WriteAllText($manifestPath, $manifestJson, [System.Text.Encoding]::UTF8)
        Write-Host "[MANIFEST] Created: $($fileInfo.Name).origin.json" -ForegroundColor Cyan
    } catch {
        Write-Warning "Failed to create manifest for $SourcePath : $_"
    }

    # Add HMAC if key present
    if ($HmacKey) {
        try {
            $fileBytes = [System.IO.File]::ReadAllBytes($DestPath)
            $manifestBytes = [System.Text.Encoding]::UTF8.GetBytes($manifestJson)
            $combinedBytes = $fileBytes + $manifestBytes
            $hmacHash = Get-HMACSHA256 -Key $HmacKey -Data $combinedBytes

            if ($hmacHash) {
                $manifest.hmac_sha256 = $hmacHash
                $manifestJson = $manifest | ConvertTo-Json -Depth 10
                [System.IO.File]::WriteAllText($manifestPath, $manifestJson, [System.Text.Encoding]::UTF8)
                Write-Host "[HMAC] Added integrity check" -ForegroundColor Magenta
            }
        } catch {
            Write-Warning "Failed to compute HMAC for $($fileInfo.Name): $_"
        }
    }
}

function Process-Item {
    param(
        [string]$Path
    )

    Write-Host "[DEBUG] Processing item: $Path" -ForegroundColor Gray
    
    if (-not $Path -or $Path.Trim() -eq "") {
        Write-Warning "Empty path provided"
        $script:HadErrors = $true
        return
    }

    # Skip .origin.json manifest files - these are metadata files, not source files to process
    $fileName = Split-Path -Leaf $Path -ErrorAction SilentlyContinue
    if ($fileName -and $fileName -match '\.origin\.json$') {
        Write-Host "[SKIP] Ignoring manifest file: $fileName" -ForegroundColor Yellow
        Write-Host "[INFO] Manifest files (.origin.json) are metadata and should not be processed." -ForegroundColor Cyan
        $script:SkippedFiles++
        return
    }

    # Use LiteralPath to handle spaces and special characters
    # Also try with [System.IO.File]::Exists as fallback for OneDrive files
    $pathExists = (Test-Path -LiteralPath $Path) -or [System.IO.File]::Exists($Path) -or [System.IO.Directory]::Exists($Path)

    if (-not $pathExists) {
        Write-Warning "Path not found: $Path"
        Write-Host "[DEBUG] Attempted to access: $Path" -ForegroundColor Yellow

        # Check if parent directory exists (might be OneDrive online-only file)
        $parentDir = Split-Path -Parent $Path -ErrorAction SilentlyContinue
        if ($parentDir -and (Test-Path -LiteralPath $parentDir)) {
            Write-Host "[DEBUG] Parent directory exists: $parentDir" -ForegroundColor Yellow
            $fileName = Split-Path -Leaf $Path -ErrorAction SilentlyContinue
            
            # Check if file exists but might be online-only or have special attributes
            try {
                # Use -Force to see all files including hidden, system, and OneDrive reparse points
                $allFiles = Get-ChildItem -LiteralPath $parentDir -Force -ErrorAction Stop
                $matchingFile = $allFiles | Where-Object { $_.Name -eq $fileName }

                if (-not $matchingFile) {
                    # Fallback: Try System.IO methods which may see files that Get-ChildItem misses
                    Write-Host "[DEBUG] Trying System.IO fallback for file detection..." -ForegroundColor Yellow
                    try {
                        $systemIOFiles = [System.IO.Directory]::GetFiles($parentDir)
                        $matchingPath = $systemIOFiles | Where-Object { [System.IO.Path]::GetFileName($_) -eq $fileName }
                        if ($matchingPath) {
                            Write-Host "[INFO] File found using System.IO fallback: $matchingPath" -ForegroundColor Cyan
                            $matchingFile = Get-Item -LiteralPath $matchingPath -Force
                        }
                    } catch {
                        Write-Host "[DEBUG] System.IO fallback also failed: $_" -ForegroundColor Yellow
                    }
                }

                if ($matchingFile) {
                    Write-Host "[INFO] File found. Attributes: $($matchingFile.Attributes)" -ForegroundColor Cyan

                    # Check if it's a OneDrive reparse point (cloud file)
                    if ($matchingFile.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
                        Write-Host "[INFO] File is a OneDrive cloud file (reparse point). Ensuring it's downloaded..." -ForegroundColor Cyan
                    }

                    # Try to access the file to trigger OneDrive download if needed
                    try {
                        $testContent = [System.IO.File]::ReadAllBytes($matchingFile.FullName)
                        Write-Host "[SUCCESS] File is accessible: $($matchingFile.FullName)" -ForegroundColor Green
                        $Path = $matchingFile.FullName
                    } catch {
                        Write-Warning "File exists but cannot be accessed. It may be online-only in OneDrive."
                        Write-Warning "Please ensure the file is downloaded (right-click -> Always keep on this device)"
                        Write-Warning "Error: $_"
                        $script:HadErrors = $true
                        return
                    }
                } else {
                    Write-Host "[ERROR] File '$fileName' not found in parent directory" -ForegroundColor Red
                    Write-Host "[DEBUG] Listing first 10 files in directory for reference:" -ForegroundColor Yellow
                    $allFiles | Select-Object -First 10 | ForEach-Object {
                        Write-Host "  - $($_.Name) [$($_.Attributes)]" -ForegroundColor Gray
                    }
                    if ($allFiles.Count -gt 10) {
                        Write-Host "  ... and $($allFiles.Count - 10) more files" -ForegroundColor Gray
                    }
                    $script:HadErrors = $true
                    return
                }
            } catch {
                Write-Warning "Cannot list files in parent directory: $_"
                $script:HadErrors = $true
                return
            }
        } else {
            Write-Warning "Parent directory does not exist: $parentDir"
            $script:HadErrors = $true
            return
        }
    }

    try {
        $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    } catch {
        Write-Warning "Failed to get item info for: $Path"
        Write-Warning "Error: $_"
        $script:HadErrors = $true
        return
    }

    if ($item.PSIsContainer) {
        # Process folder recursively
        Write-Host "[FOLDER] Processing recursively: $($item.Name)" -ForegroundColor Blue
        # Use -Force to ensure we get all files including hidden and OneDrive cloud files
        $files = Get-ChildItem -Path $Path -File -Recurse -Force
        foreach ($file in $files) {
            $relativePath = $file.FullName.Substring($Path.Length).TrimStart('\')
            $destPath = Join-Path $DestFolder $relativePath
            Process-File -SourcePath $file.FullName -DestPath $destPath
        }
    } else {
        # Process single file
        $destPath = Join-Path $DestFolder $item.Name
        Process-File -SourcePath $item.FullName -DestPath $destPath
    }
}

# Process all input paths
Write-Host "===============================================" -ForegroundColor White
Write-Host "Chunker Move-Optimized SendTo Script" -ForegroundColor White
Write-Host "===============================================" -ForegroundColor White
Write-Host ""

# Debug: Show received paths
Write-Host "[DEBUG] Number of paths received: $($Paths.Count)" -ForegroundColor Cyan
if ($Paths.Count -eq 0) {
    Write-Host "[ERROR] No files were selected or passed to the script!" -ForegroundColor Red
    Write-Host "[ERROR] Make sure you select files before using 'Send to'" -ForegroundColor Red
    Write-Host ""
    $script:HadErrors = $true
} else {
    Write-Host "[DEBUG] Paths received:" -ForegroundColor Cyan
    foreach ($p in $Paths) {
        Write-Host "  - $p" -ForegroundColor Cyan
    }
    Write-Host ""
}

foreach ($path in $Paths) {
    Write-Host "Processing: $path" -ForegroundColor White
    Process-Item -Path $path
    Write-Host ""
}

Write-Host "===============================================" -ForegroundColor White
Write-Host "Processing Complete" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor White

# Show summary of skipped files
if ($script:SkippedFiles -gt 0) {
    Write-Host ""
    Write-Host "SUMMARY: $($script:SkippedFiles) manifest file(s) skipped (.origin.json files)" -ForegroundColor Yellow
    Write-Host "These are metadata files created by previous runs and should not be processed." -ForegroundColor Cyan
    Write-Host "To clean up, you can delete these .origin.json files from your Desktop." -ForegroundColor Cyan
    Write-Host ""
}

if ($script:FailedFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "WARNING: The following files could not be removed from source location:" -ForegroundColor Red
    Write-Host "This is likely due to OneDrive syncing. Files may reappear on your desktop." -ForegroundColor Yellow
    Write-Host ""
    foreach ($file in $script:FailedFiles) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Files were successfully copied to: $DestFolder" -ForegroundColor Green
    Write-Host "You may need to manually delete the source files or pause OneDrive sync." -ForegroundColor Yellow
    Write-Host ""
}

if ($script:HadErrors) {
    exit 1
} else {
    exit 0
}

