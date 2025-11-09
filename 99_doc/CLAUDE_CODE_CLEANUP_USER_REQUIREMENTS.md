# Claude Code: Chunker Consolidation - User Requirements

## 🎯 User's Clear Requirements

Based on explicit user instructions, here's what needs to happen:

### Primary Decision: Keep `C:\_chunker` as the Active System

**User has decided:**
1. ✅ `C:\_chunker` has the most recent output - **KEEP THIS AS PRIMARY**
2. ✅ Need ALL processed chunks from all directories
3. ✅ Consolidate knowledge bases to `C:\_chunker`
4. ✅ Only keep `C:\_chunker` repo active
5. ✅ Consolidate all processed outputs to `C:\_chunker\04_output`

### Secondary: What to Do with ClaudeExportFixer

`C:\Dev\ClaudeExportFixer` v2.0.0 contains the NEW unified system code, but user wants to keep using `C:\_chunker` structure.

**Solution:** Merge the NEW code into `C:\_chunker` while preserving the data structure.

---

## 📋 Your Mission

### Phase 1: DISCOVERY & CONFIG ANALYSIS

#### Task 1A: Scan All Directories
```powershell
$dirs = @(
    "C:\_chunker",
    "C:\Claude_Archive",
    "C:\Dev\ClaudeExportFixer",
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
            OutputFiles = 0
            ArchiveFiles = 0
            UnprocessedFiles = 0
            DatabaseFiles = @()
            HasConfig = $false
            ConfigPath = ""
            TotalSizeMB = 0
        }
        
        # Count output files
        $outputDir = Join-Path $dir "04_output"
        if (Test-Path $outputDir) {
            $info.OutputFiles = (Get-ChildItem $outputDir -Recurse -File -ErrorAction SilentlyContinue).Count
        }
        
        # Count archive files
        $archiveDir = Join-Path $dir "03_archive"
        if (Test-Path $archiveDir) {
            $info.ArchiveFiles = (Get-ChildItem $archiveDir -Recurse -File -ErrorAction SilentlyContinue).Count
        }
        
        # Count unprocessed files
        $dataDir = Join-Path $dir "02_data"
        if (Test-Path $dataDir) {
            $info.UnprocessedFiles = (Get-ChildItem $dataDir -File -ErrorAction SilentlyContinue).Count
        }
        
        # Find databases
        $dbs = Get-ChildItem $dir -Filter "*.db" -Recurse -ErrorAction SilentlyContinue
        $info.DatabaseFiles = $dbs | ForEach-Object { $_.FullName }
        
        # Check for config.json
        $configPath = Join-Path $dir "config.json"
        if (Test-Path $configPath) {
            $info.HasConfig = $true
            $info.ConfigPath = $configPath
        }
        
        # Calculate size
        $totalSize = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $info.TotalSizeMB = [math]::Round($totalSize / 1MB, 2)
        
        $report += $info
    }
}

# Save report
$report | Export-Csv "C:\_chunker\99_doc\CLEANUP_INVENTORY_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation
$report | Format-Table -AutoSize -Wrap
```

#### Task 1B: Compare Config Files

For each directory with `config.json`, analyze the differences:

```powershell
# Get all config files
$configs = @()
foreach ($dir in $dirs) {
    $configPath = Join-Path $dir "config.json"
    if (Test-Path $configPath) {
        $configs += [PSCustomObject]@{
            Source = $dir
            Path = $configPath
            Content = Get-Content $configPath -Raw | ConvertFrom-Json
        }
    }
}

# Compare configurations
# Look for:
# - Different supported_extensions
# - Different exclude_patterns
# - Custom chunking parameters
# - Department-specific settings
# - Performance tuning differences

# Create comparison report
$configComparison = @"
# Config File Comparison Report

## Configs Found
$($configs | ForEach-Object { "- $($_.Source)" } | Out-String)

## Key Differences to Consider

[You need to analyze and document the differences here]

## Recommendation
Which config settings should be merged into C:\_chunker\config.json?
"@

$configComparison | Out-File "C:\_chunker\99_doc\CONFIG_COMPARISON_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
```

**STOP HERE AND SHOW ME:**
1. The inventory CSV results
2. The config comparison report
3. Your recommendations for config merging

---

### Phase 2: CONSOLIDATE UNPROCESSED FILES (After my approval)

Move all unprocessed files to `C:\_chunker\02_data`:

```powershell
$targetDataDir = "C:\_chunker\02_data"

foreach ($dir in $dirs) {
    if ($dir -ne "C:\_chunker") {  # Don't copy from itself
        $sourceDataDir = Join-Path $dir "02_data"
        
        if (Test-Path $sourceDataDir) {
            $files = Get-ChildItem $sourceDataDir -File -ErrorAction SilentlyContinue
            
            foreach ($file in $files) {
                $destPath = Join-Path $targetDataDir $file.Name
                
                # Handle duplicates
                if (Test-Path $destPath) {
                    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
                    $destPath = Join-Path $targetDataDir "$timestamp-$($file.Name)"
                }
                
                Copy-Item $file.FullName -Destination $destPath -Force
                Write-Host "✅ Moved unprocessed: $($file.Name) from $dir" -ForegroundColor Green
            }
        }
        
        # Also check 01_input folders (ClaudeExportFixer structure)
        $inputDir = Join-Path $dir "01_input"
        if (Test-Path $inputDir) {
            $files = Get-ChildItem $inputDir -File -ErrorAction SilentlyContinue
            
            foreach ($file in $files) {
                # Skip README files
                if ($file.Name -notlike "*README*") {
                    $destPath = Join-Path $targetDataDir $file.Name
                    
                    if (Test-Path $destPath) {
                        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
                        $destPath = Join-Path $targetDataDir "$timestamp-$($file.Name)"
                    }
                    
                    Copy-Item $file.FullName -Destination $destPath -Force
                    Write-Host "✅ Moved unprocessed: $($file.Name) from $dir/01_input" -ForegroundColor Green
                }
            }
        }
    }
}

Write-Host "`n📋 All unprocessed files consolidated to: $targetDataDir" -ForegroundColor Cyan
```

---

### Phase 3: CONSOLIDATE PROCESSED OUTPUT (After my approval)

Move all processed chunks to `C:\_chunker\04_output`:

```powershell
$targetOutputDir = "C:\_chunker\04_output"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

foreach ($dir in $dirs) {
    if ($dir -ne "C:\_chunker") {
        $sourceOutputDir = Join-Path $dir "04_output"
        
        if (Test-Path $sourceOutputDir) {
            $dirName = Split-Path $dir -Leaf
            $destSubDir = Join-Path $targetOutputDir "consolidated_$timestamp`_$dirName"
            
            Write-Host "📦 Consolidating output from: $dir" -ForegroundColor Yellow
            Copy-Item -Path $sourceOutputDir -Destination $destSubDir -Recurse -Force
            
            $fileCount = (Get-ChildItem $destSubDir -Recurse -File).Count
            Write-Host "   ✅ Copied $fileCount files" -ForegroundColor Green
        }
        
        # Also check 02_output folders (ClaudeExportFixer structure)
        $outputDir = Join-Path $dir "02_output"
        if (Test-Path $outputDir) {
            $dirName = Split-Path $dir -Leaf
            $destSubDir = Join-Path $targetOutputDir "consolidated_$timestamp`_$dirName`_02output"
            
            Write-Host "📦 Consolidating output from: $dir/02_output" -ForegroundColor Yellow
            Copy-Item -Path $outputDir -Destination $destSubDir -Recurse -Force
            
            $fileCount = (Get-ChildItem $destSubDir -Recurse -File).Count
            Write-Host "   ✅ Copied $fileCount files" -ForegroundColor Green
        }
    }
}

Write-Host "`n📋 All processed outputs consolidated to: $targetOutputDir" -ForegroundColor Cyan
```

---

### Phase 4: CONSOLIDATE KNOWLEDGE BASES (After my approval)

Move all database files to `C:\_chunker`:

```powershell
$targetKBDir = "C:\_chunker\03_knowledge_base"
New-Item -ItemType Directory -Path $targetKBDir -Force -ErrorAction SilentlyContinue

foreach ($dir in $dirs) {
    if ($dir -ne "C:\_chunker") {
        # Find all .db files
        $databases = Get-ChildItem $dir -Filter "*.db" -Recurse -ErrorAction SilentlyContinue
        
        foreach ($db in $databases) {
            $destName = "$($db.BaseName)_from_$(Split-Path $dir -Leaf)$($db.Extension)"
            $destPath = Join-Path $targetKBDir $destName
            
            Copy-Item $db.FullName -Destination $destPath -Force
            Write-Host "✅ Consolidated KB: $($db.Name) -> $destName" -ForegroundColor Green
        }
        
        # Also check for ChromaDB folders
        $chromaDir = Join-Path $dir "03_knowledge_base\chroma_db"
        if (Test-Path $chromaDir) {
            $destChroma = Join-Path $targetKBDir "chroma_db_from_$(Split-Path $dir -Leaf)"
            Copy-Item $chromaDir -Destination $destChroma -Recurse -Force
            Write-Host "✅ Consolidated ChromaDB from: $dir" -ForegroundColor Green
        }
    }
}

Write-Host "`n📋 All knowledge bases consolidated to: $targetKBDir" -ForegroundColor Cyan
```

---

### Phase 5: MERGE v2.0.0 CODE INTO C:\_chunker (After my approval)

Copy the NEW unified system code from ClaudeExportFixer to `C:\_chunker`:

```powershell
# Backup current C:\_chunker code first
$backupDir = "C:\_chunker\archive\pre_v2_upgrade_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force

# Backup current scripts
Copy-Item "C:\_chunker\*.py" -Destination $backupDir -Force -ErrorAction SilentlyContinue
Copy-Item "C:\_chunker\config.json" -Destination "$backupDir\config_backup.json" -Force -ErrorAction SilentlyContinue

Write-Host "✅ Backed up current code to: $backupDir" -ForegroundColor Green

# Copy NEW v2.0.0 components
Copy-Item "C:\Dev\ClaudeExportFixer\chunker_engine.py" -Destination "C:\_chunker\chunker_engine.py" -Force
Copy-Item "C:\Dev\ClaudeExportFixer\file_processors.py" -Destination "C:\_chunker\file_processors.py" -Force
Copy-Item "C:\Dev\ClaudeExportFixer\start_watchdog.py" -Destination "C:\_chunker\start_watchdog.py" -Force

# Copy updated requirements
Copy-Item "C:\Dev\ClaudeExportFixer\requirements.txt" -Destination "C:\_chunker\requirements_v2.txt" -Force

Write-Host "✅ Copied v2.0.0 unified system code to C:\_chunker" -ForegroundColor Green
Write-Host "⚠️  Review config.json - may need manual merge of settings" -ForegroundColor Yellow
```

---

### Phase 6: ARCHIVE OLD DIRECTORIES (After my approval)

Move all other directories to archive:

```powershell
$archiveDate = Get-Date -Format "yyyy_MM_dd_HHmmss"
$archiveRoot = "C:\OldChunkerProjects_Archive_$archiveDate"
New-Item -ItemType Directory -Path $archiveRoot -Force

$toArchive = @(
    "C:\Claude_Archive",
    "C:\Dev\chat_log_chunker_v1",
    "C:\Users\carucci_r\chat_log_chunker_v1",
    "C:\Users\carucci_r\Documents\chat_log_chunker",
    "C:\Users\carucci_r\Documents\chat_watcher",
    "C:\Users\carucci_r\Documents\chunker"
)

foreach ($oldDir in $toArchive) {
    if (Test-Path $oldDir) {
        $dirName = $oldDir -replace '[:\\]', '_'
        $destPath = Join-Path $archiveRoot $dirName
        
        Write-Host "📦 Archiving: $oldDir" -ForegroundColor Yellow
        Move-Item -Path $oldDir -Destination $destPath -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Moved to: $destPath" -ForegroundColor Green
    }
}

Write-Host "`n✅ Old directories archived to: $archiveRoot" -ForegroundColor Green
Write-Host "⚠️  Keep archive for 60 days before deleting" -ForegroundColor Yellow
```

---

### Phase 7: HANDLE ClaudeExportFixer Directory

User wants to keep `C:\_chunker` active, but ClaudeExportFixer has the GitHub repo with v2.0.0.

**Options:**

**Option A: Keep Both (Recommended)**
- `C:\Dev\ClaudeExportFixer` → Keep as GitHub repo for v2.0.0 codebase
- `C:\_chunker` → Active working directory with all data
- Periodically sync code from ClaudeExportFixer to `_chunker`

**Option B: Clone ClaudeExportFixer Repo to `_chunker`
```powershell
# Backup current C:\_chunker
Move-Item "C:\_chunker" "C:\_chunker_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Clone from GitHub
git clone https://github.com/racmac57/ClaudeExportFixer.git C:\_chunker

# Restore data folders
Copy-Item "C:\_chunker_backup_*\02_data" -Destination "C:\_chunker\02_data" -Recurse -Force
Copy-Item "C:\_chunker_backup_*\04_output" -Destination "C:\_chunker\04_output" -Recurse -Force
Copy-Item "C:\_chunker_backup_*\03_knowledge_base" -Destination "C:\_chunker\03_knowledge_base" -Recurse -Force
```

**STOP AND ASK USER:** Which option do you prefer?

---

## 📊 Final Summary Report

After completing all phases, create:

```markdown
# Consolidation Complete - Summary Report

## Actions Taken

### Phase 1: Discovery
- Scanned 8 directories
- Found [X] processed files
- Found [Y] unprocessed files
- Found [Z] knowledge bases

### Phase 2: Unprocessed Files
- Consolidated [X] files to C:\_chunker\02_data

### Phase 3: Processed Output
- Consolidated [X] files to C:\_chunker\04_output
- Organized by source directory with timestamps

### Phase 4: Knowledge Bases
- Consolidated [X] databases to C:\_chunker\03_knowledge_base

### Phase 5: Code Upgrade
- Merged v2.0.0 code into C:\_chunker
- Backed up old code

### Phase 6: Archive
- Moved [X] old directories to archive
- Archive location: [path]

## Current System Status

**Active Directory:** C:\_chunker
**GitHub Repo:** [User to decide]
**Version:** v2.0.0 (unified system)

## Directory Structure
```
C:\_chunker\
├── 02_data\          [All unprocessed files]
├── 04_output\        [All processed chunks consolidated]
├── 03_knowledge_base\ [All databases consolidated]
├── chunker_engine.py  [NEW v2.0.0]
├── file_processors.py [NEW v2.0.0]
├── start_watchdog.py  [NEW v2.0.0]
└── config.json       [Review needed]
```

## Next Steps
1. Review and update C:\_chunker\config.json
2. Install new requirements: pip install -r requirements_v2.txt
3. Test the system: python start_watchdog.py --verbose
4. Decide on GitHub repo strategy
5. After 60 days, delete archive folder
```

---

## 🚦 Execution Order

1. **Phase 1: Discovery** → Run and SHOW ME results
2. **WAIT FOR APPROVAL**
3. **Phase 2-6: Execute** → With progress reports
4. **Phase 7: User Decision** → Ask about ClaudeExportFixer/GitHub
5. **Final Report** → Summary of all actions

---

## ⚠️ Safety Rules

✅ **Always backup before overwriting**  
✅ **Copy first, then move (never delete)**  
✅ **Show me results after each phase**  
✅ **Wait for approval before major actions**  
❌ **Never delete without explicit approval**  

---

**START WITH PHASE 1: Run discovery and show me the inventory + config comparison.**

