# Prepare Grok Review Package
# Creates a folder with all files needed for Grok to review the project

param(
    [string]$OutputPath = "grok_review_package"
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Preparing Grok Review Package" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (Test-Path $OutputPath) {
    Write-Host "[!] Directory $OutputPath already exists. Removing..." -ForegroundColor Yellow
    Remove-Item -Path $OutputPath -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
Write-Host "[+] Created directory: $OutputPath" -ForegroundColor Green

# Define files to copy (Priority order)
$filesToCopy = @(
    # Core Python Scripts (Priority 1)
    @{Path="watcher_splitter.py"; Category="Core Scripts"; Priority="Critical"},
    @{Path="backfill_knowledge_base.py"; Category="Core Scripts"; Priority="Critical"},
    @{Path="manual_process_files.py"; Category="Core Scripts"; Priority="High"},
    @{Path="celery_tasks.py"; Category="Core Scripts"; Priority="High"},
    
    # RAG/Knowledge Base Scripts
    @{Path="rag_integration.py"; Category="RAG Scripts"; Priority="High"},
    @{Path="rag_search.py"; Category="RAG Scripts"; Priority="High"},
    @{Path="langchain_rag_handler.py"; Category="RAG Scripts"; Priority="Medium"},
    
    # Supporting Infrastructure
    @{Path="chunker_db.py"; Category="Infrastructure"; Priority="Medium"},
    @{Path="file_processors.py"; Category="Infrastructure"; Priority="Medium"},
    @{Path="enhanced_watchdog.py"; Category="Infrastructure"; Priority="Medium"},
    @{Path="orchestrator.py"; Category="Infrastructure"; Priority="Low"},
    
    # Configuration
    @{Path="config.json"; Category="Configuration"; Priority="Critical"},
    
    # Documentation (Priority 1)
    @{Path="README.md"; Category="Documentation"; Priority="Critical"},
    @{Path="ENTERPRISE_CHUNKER_SUMMARY.md"; Category="Documentation"; Priority="Critical"},
    @{Path="MOVE_WORKFLOW_IMPLEMENTATION.md"; Category="Documentation"; Priority="Critical"},
    @{Path="GROK_SIMPLIFICATION_RECOMMENDATIONS.md"; Category="Documentation"; Priority="Critical"},
    @{Path="GROK_REVIEW_PACKAGE.md"; Category="Documentation"; Priority="Critical"},
    
    # Documentation (Priority 2)
    @{Path="TASK_PROGRESS_REPORT.md"; Category="Documentation"; Priority="High"},
    @{Path="IMPLEMENTATION_STATUS.md"; Category="Documentation"; Priority="High"},
    @{Path="FINAL_STATUS.md"; Category="Documentation"; Priority="High"},
    @{Path="CHANGELOG.md"; Category="Documentation"; Priority="High"},
    
    # Documentation (Priority 3)
    @{Path="CLAUDE_CODE_TASK_PROMPT.md"; Category="Documentation"; Priority="Medium"},
    @{Path="QUICK_START_PROMPT.md"; Category="Documentation"; Priority="Medium"},
    @{Path="RECOVERY_SUCCESS.md"; Category="Documentation"; Priority="Medium"},
    
    # PowerShell Scripts
    @{Path="Chunker_MoveOptimized.ps1"; Category="Scripts"; Priority="High"},
    
    # Requirements
    @{Path="requirements.txt"; Category="Dependencies"; Priority="Medium"},
    @{Path="requirements_rag.txt"; Category="Dependencies"; Priority="Medium"}
)

# Copy files
$copied = 0
$failed = 0
$missing = 0

foreach ($file in $filesToCopy) {
    $sourcePath = $file.Path
    $category = $file.Category
    $priority = $file.Priority
    
    if (Test-Path $sourcePath) {
        try {
            # Create category subdirectory if needed
            $categoryDir = Join-Path $OutputPath $category
            if (-not (Test-Path $categoryDir)) {
                New-Item -ItemType Directory -Path $categoryDir -Force | Out-Null
            }
            
            # Copy file
            Copy-Item -Path $sourcePath -Destination $categoryDir -Force
            $copied++
            Write-Host "[+] Copied: $sourcePath ($priority)" -ForegroundColor Green
        }
        catch {
            $failed++
            Write-Host "[-] Failed to copy: $sourcePath - $_" -ForegroundColor Red
        }
    }
    else {
        $missing++
        Write-Host "[!] Missing: $sourcePath" -ForegroundColor Yellow
    }
}

# Create README for the package
$packageReadme = @"
# Grok Review Package
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Package Contents

This package contains all files needed for Grok to review and collaborate on the Enterprise Chunker v2.1.5 project.

### Statistics
- Total Files: $($filesToCopy.Count)
- Successfully Copied: $copied
- Failed: $failed
- Missing: $missing

### Directory Structure
- **Core Scripts/** - Main Python processing scripts
- **RAG Scripts/** - Knowledge base and RAG integration
- **Infrastructure/** - Supporting infrastructure code
- **Configuration/** - Configuration files
- **Documentation/** - Project documentation
- **Scripts/** - PowerShell scripts
- **Dependencies/** - Requirements files

## How to Use This Package

1. **Start with Documentation**
   - Read `Documentation/README.md` first
   - Then `Documentation/ENTERPRISE_CHUNKER_SUMMARY.md`
   - Review `Documentation/GROK_REVIEW_PACKAGE.md` for specific review areas

2. **Review Core Scripts**
   - `Core Scripts/watcher_splitter.py` - Main processing engine
   - `Core Scripts/backfill_knowledge_base.py` - KB backfill (NEW)
   - `Core Scripts/manual_process_files.py` - Manual processing

3. **Check Configuration**
   - `Configuration/config.json` - Current system settings

## Key Questions for Grok

1. Review `backfill_knowledge_base.py` for correctness and performance
2. Implement multi-cloud support (OneDrive + Google Drive)
3. Code quality improvements
4. Architecture recommendations
5. Performance optimizations

## Current System State

- **Processed Files**: 908 files
- **Chunk Files**: 5,462 chunks in 04_output/
- **RAG Status**: Disabled (needs enabling)
- **Cloud Sync**: Disabled (needs Google Drive path)
- **Version**: 2.1.5

See `Documentation/GROK_REVIEW_PACKAGE.md` for complete context.
"@

$packageReadme | Out-File -FilePath (Join-Path $OutputPath "README.txt") -Encoding UTF8

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Package Creation Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Package Location: $OutputPath" -ForegroundColor Yellow
Write-Host "[+] Files Copied: $copied" -ForegroundColor Green
Write-Host "[!] Missing Files: $missing" -ForegroundColor Yellow
Write-Host "[-] Failed: $failed" -ForegroundColor Red
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review the package contents" -ForegroundColor White
Write-Host "2. Share with Grok for review" -ForegroundColor White
Write-Host "3. Use README.txt as starting point" -ForegroundColor White
Write-Host ""

# Optionally create ZIP
$createZip = Read-Host "Create ZIP archive? (y/n)"
if ($createZip -eq "y") {
    $zipPath = "$OutputPath.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    Compress-Archive -Path $OutputPath -DestinationPath $zipPath -Force
    Write-Host "Created ZIP: $zipPath" -ForegroundColor Green
}

