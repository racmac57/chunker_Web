# Send to Chunker - OPTIMIZED VERSION (Move-Based Workflow)
# Moves files/folders from OneDrive to chunker watch folder with origin manifest
# Reduces storage bloat and OneDrive sync overhead by 50%+

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Paths
)

$ErrorActionPreference = 'Continue'
$script:HadErrors = $false
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
        Start-Sleep -Milliseconds 300
        if (Test-Path $SourcePath) {
            try {
                Remove-Item -Path $SourcePath -Force -ErrorAction Stop
                Write-Host "[CLEANUP] Removed residual source copy: $($fileInfo.Name)" -ForegroundColor DarkYellow
                $manifest.source_cleanup = "removed_residual_copy"
            } catch {
                Write-Warning "Residual source copy could not be removed for $($fileInfo.Name): $_"
                $manifest.source_cleanup = "cleanup_failed"
                $manifest.source_cleanup_error = $_.ToString()
                $script:HadErrors = $true
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

            Start-Sleep -Milliseconds 300
            if (Test-Path $SourcePath) {
                try {
                    Remove-Item -Path $SourcePath -Force -ErrorAction Stop
                    Write-Host "[CLEANUP] Removed source after copy fallback: $($fileInfo.Name)" -ForegroundColor DarkYellow
                    $manifest.source_cleanup = "removed_after_copy"
                } catch {
                    Write-Warning "Failed to remove source after copy fallback for $($fileInfo.Name): $_"
                    $manifest.source_cleanup = "cleanup_failed_after_copy"
                    $manifest.source_cleanup_error = $_.ToString()
                    $script:HadErrors = $true
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

    if (-not (Test-Path $Path)) {
        Write-Warning "Path not found: $Path"
        return
    }

    $item = Get-Item $Path

    if ($item.PSIsContainer) {
        # Process folder recursively
        Write-Host "[FOLDER] Processing recursively: $($item.Name)" -ForegroundColor Blue
        $files = Get-ChildItem -Path $Path -File -Recurse
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

foreach ($path in $Paths) {
    Write-Host "Processing: $path" -ForegroundColor White
    Process-Item -Path $path
    Write-Host ""
}

Write-Host "===============================================" -ForegroundColor White
Write-Host "Processing Complete" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor White

if ($script:HadErrors) {
    exit 1
} else {
    exit 0
}

