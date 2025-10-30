# Claude Code: Chunker Project Cleanup & Consolidation

## Context

I have multiple chunker-related directories scattered across my Windows system that need to be consolidated. The `ClaudeExportFixer` v2.0.0 has successfully merged all chunker functionality into a unified system, making the old separate chunker directories obsolete.

## The Problem

**Multiple directories with similar names/purposes:**

### Primary Directories
1. `C:\_chunker` - Old active chunker with processed data
2. `C:\Claude_Archive` - Unknown contents
3. `C:\Dev\ClaudeExportFixer` - ✅ **THE NEW UNIFIED SYSTEM (v2.0.0)** - Keep this!
4. `C:\Dev\chat_log_chunker_v1` - Old chunker project

### User Profile Directories
5. `C:\Users\carucci_r\chat_log_chunker_v1` - Possible duplicate
6. `C:\Users\carucci_r\Documents\chat_log_chunker` - Another copy
7. `C:\Users\carucci_r\Documents\chat_watcher` - Related project
8. `C:\Users\carucci_r\Documents\chunker` - Yet another copy

## My Concerns & Blind Spots

1. **Data Loss** - Which directories have processed output I need to preserve?
2. **Unprocessed Files** - Are there files waiting to be processed in `02_data` folders?
3. **GitHub Repos** - Which are git repositories and what's their status?
4. **Knowledge Bases** - Are there SQLite `.db` files or ChromaDB stores I need?
5. **Configurations** - Any custom `config.json` files with special settings?
6. **Documentation** - `.md` files that should be preserved

## Your Mission

### Phase 1: DISCOVERY & INVENTORY (MANDATORY FIRST STEP)

**DO NOT DELETE OR MOVE ANYTHING YET!**

Create a comprehensive inventory report by analyzing each directory:

```powershell
# Run this discovery script
$dirs = @(
    "C:\_chunker",
    "C:\Claude_Archive",
    "C:\Dev\chat_log_chunker_v1",
    "C:\Users\carucci_r\chat_log_chunker_v1",
    "C:\Users\carucci_r\Documents\chat_log_chunker",
    "C:\Users\carucci_r\Documents\chat_watcher",
    "C:\Users\carucci_r\Documents\chunker"
)

$report = @()

foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        $info = [PSCustomObject]@{
            Directory = $dir
            Exists = $true
            IsGitRepo = Test-Path "$dir\.git"
            GitRemote = ""
            OutputFiles = 0
            ArchiveFiles = 0
            UnprocessedFiles = 0
            DatabaseFiles = @()
            MarkdownFiles = 0
            ConfigFiles = 0
            TotalSizeMB = 0
        }
        
        # Check git remote
        if ($info.IsGitRepo) {
            Push-Location $dir
            $info.GitRemote = (git remote get-url origin 2>$null)
            Pop-Location
        }
        
        # Count files in key directories
        $outputDir = Join-Path $dir "04_output"
        if (Test-Path $outputDir) {
            $info.OutputFiles = (Get-ChildItem $outputDir -Recurse -File -ErrorAction SilentlyContinue).Count
        }
        
        $archiveDir = Join-Path $dir "03_archive"
        if (Test-Path $archiveDir) {
            $info.ArchiveFiles = (Get-ChildItem $archiveDir -Recurse -File -ErrorAction SilentlyContinue).Count
        }
        
        $dataDir = Join-Path $dir "02_data"
        if (Test-Path $dataDir) {
            $info.UnprocessedFiles = (Get-ChildItem $dataDir -File -ErrorAction SilentlyContinue).Count
        }
        
        # Find database files
        $dbs = Get-ChildItem $dir -Filter "*.db" -Recurse -ErrorAction SilentlyContinue
        $info.DatabaseFiles = $dbs | ForEach-Object { $_.FullName }
        
        # Count markdown and config files
        $info.MarkdownFiles = (Get-ChildItem $dir -Filter "*.md" -File -ErrorAction SilentlyContinue).Count
        $info.ConfigFiles = (Get-ChildItem $dir -Filter "config.json" -Recurse -ErrorAction SilentlyContinue).Count
        
        # Calculate total size
        $totalSize = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $info.TotalSizeMB = [math]::Round($totalSize / 1MB, 2)
        
        $report += $info
    } else {
        $report += [PSCustomObject]@{
            Directory = $dir
            Exists = $false
        }
    }
}

# Output the report
$report | Format-Table -AutoSize -Wrap
$report | Export-Csv "C:\Dev\ClaudeExportFixer\docs\CLEANUP_INVENTORY_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📊 DISCOVERY COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Report saved to: C:\Dev\ClaudeExportFixer\docs\" -ForegroundColor Yellow
```

**Expected Output:** Create `CLEANUP_INVENTORY_[timestamp].csv` with the complete inventory.

### Phase 2: ANALYSIS & RECOMMENDATIONS

After running the inventory, analyze the results and provide:

1. **High-Risk Items** - Files/data that MUST be preserved
2. **Duplicate Detection** - Which directories appear to be duplicates
3. **Unprocessed Files** - List files waiting in `02_data` folders
4. **GitHub Status** - Which repos are active, which are abandoned
5. **Size Analysis** - Which directories are taking up the most space
6. **Recommendations** - What to keep, archive, or delete

Create a report: `CLEANUP_ANALYSIS_REPORT.md`

### Phase 3: PRESERVATION (If approved by me)

**For `C:\_chunker` specifically:**

1. **Process Unprocessed Files**
```powershell
# Copy unprocessed files to new unified system
$unprocessed = Get-ChildItem "C:\_chunker\02_data" -File -ErrorAction SilentlyContinue
if ($unprocessed) {
    foreach ($file in $unprocessed) {
        Copy-Item $file.FullName -Destination "C:\Dev\ClaudeExportFixer\01_input\" -Force
        Write-Host "Copied: $($file.Name)" -ForegroundColor Green
    }
    
    # Process with unified system
    cd C:\Dev\ClaudeExportFixer
    python process_workflow.py
}
```

2. **Preserve Documentation**
```powershell
# Create legacy docs folder
$legacyDocs = "C:\Dev\ClaudeExportFixer\docs\legacy_chunker"
New-Item -ItemType Directory -Path $legacyDocs -Force

# Copy from C:\_chunker
Copy-Item "C:\_chunker\99_doc\*.md" -Destination $legacyDocs -Force -ErrorAction SilentlyContinue
Copy-Item "C:\_chunker\*.md" -Destination $legacyDocs -Force -ErrorAction SilentlyContinue
Copy-Item "C:\_chunker\config.json" -Destination "$legacyDocs\legacy_config.json" -Force -ErrorAction SilentlyContinue
```

3. **Preserve Databases**
```powershell
# Copy important databases
$dbBackup = "C:\Dev\ClaudeExportFixer\docs\legacy_chunker\databases"
New-Item -ItemType Directory -Path $dbBackup -Force

Get-ChildItem "C:\_chunker" -Filter "*.db" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName -Destination $dbBackup -Force
    Write-Host "Backed up database: $($_.Name)" -ForegroundColor Cyan
}
```

### Phase 4: ARCHIVING (If approved by me)

Create dated archive for old directories:

```powershell
$archiveDate = Get-Date -Format "yyyy_MM_dd_HHmmss"
$archiveRoot = "C:\OldChunkerProjects_Archive_$archiveDate"
New-Item -ItemType Directory -Path $archiveRoot -Force

# List of directories to archive (excluding the new unified system)
$toArchive = @(
    "C:\_chunker",
    "C:\Claude_Archive",
    "C:\Dev\chat_log_chunker_v1",
    "C:\Users\carucci_r\chat_log_chunker_v1",
    "C:\Users\carucci_r\Documents\chat_log_chunker",
    "C:\Users\carucci_r\Documents\chat_watcher",
    "C:\Users\carucci_r\Documents\chunker"
)

foreach ($oldDir in $toArchive) {
    if (Test-Path $oldDir) {
        $dirName = Split-Path $oldDir -Leaf
        $destPath = Join-Path $archiveRoot $dirName
        
        Write-Host "Moving: $oldDir -> $destPath" -ForegroundColor Yellow
        Move-Item -Path $oldDir -Destination $destPath -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n✅ All old directories moved to: $archiveRoot" -ForegroundColor Green
Write-Host "⚠️  Keep this archive for 30-60 days before deleting" -ForegroundColor Yellow
```

### Phase 5: VERIFICATION & CLEANUP

Create a summary report:

```markdown
# Cleanup Summary Report

## Directories Archived
- List each directory with size and file counts

## Files Preserved
- Documentation files copied
- Database files backed up
- Unprocessed files moved and processed

## New Unified System
- Location: C:\Dev\ClaudeExportFixer
- Version: 2.0.0
- Status: Production Ready
- GitHub: racmac57/ClaudeExportFixer.git

## Archive Location
- Path: C:\OldChunkerProjects_Archive_[timestamp]
- Total Size: [size]
- Retention: Keep for 60 days
- Delete After: [date]

## Next Steps
1. Verify new unified system works with your workflows
2. Test that you have all needed documentation
3. After 30-60 days, delete the archive folder
4. Update any shortcuts/scripts pointing to old directories
```

## Safety Guidelines

### ✅ YOU MAY:
- Run the discovery script to gather information
- Create inventory reports and analysis
- Copy files to new locations
- Create backups and archives
- Move directories to a dated archive folder

### ❌ YOU MUST NOT:
- Delete any directories without my explicit approval
- Overwrite files in `C:\Dev\ClaudeExportFixer` (except in `docs/legacy_chunker/`)
- Process files without showing me what will be processed first
- Make assumptions about which data I need

### ⚠️ ASK ME FIRST BEFORE:
- Moving any directory
- Deleting any files
- Processing unprocessed files
- Modifying the new ClaudeExportFixer system

## Success Criteria

✅ **Phase 1 Complete:** Inventory CSV created and analyzed  
✅ **Phase 2 Complete:** Analysis report with recommendations  
✅ **Phase 3 Complete:** Important data preserved in ClaudeExportFixer  
✅ **Phase 4 Complete:** Old directories moved to dated archive  
✅ **Phase 5 Complete:** Summary report created  

## Deliverables

1. `CLEANUP_INVENTORY_[timestamp].csv` - Complete inventory
2. `CLEANUP_ANALYSIS_REPORT.md` - Analysis and recommendations
3. `CLEANUP_SUMMARY_REPORT.md` - Final summary of actions taken
4. `legacy_chunker/` folder in ClaudeExportFixer with preserved docs/configs/dbs
5. `C:\OldChunkerProjects_Archive_[timestamp]\` - Archived old directories

## My Questions for You (After Phase 1)

Before proceeding with archiving, I need you to help me answer:

1. Do I need the processed output from all directories or just the most recent?
2. Are there custom configurations in any old directories I should merge into v2.0.0?
3. Should unprocessed files be processed with the old system or new unified system?
4. Do I want to consolidate all knowledge bases (*.db files) into one?
5. Are there any directories that are actually current projects I'm actively using?

## Start Here

**Step 1:** Run the discovery script (Phase 1)  
**Step 2:** Show me the inventory results  
**Step 3:** Wait for my approval before proceeding to Phase 3  

Let's be methodical and safe. Data loss is unacceptable.

---

**BEGIN WITH PHASE 1: Run the discovery script and show me the inventory.**

