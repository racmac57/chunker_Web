# Cleanup Plan - Consolidating Chunker Projects

**Date:** October 29, 2025  
**Goal:** Consolidate multiple chunker directories into unified `ClaudeExportFixer` v2.0.0 system

---

## 🎯 Current Situation

You have **MULTIPLE** directories with similar names/purposes scattered across your system:

### Primary Directories
1. **`C:\_chunker`** - Active chunker with processed data
2. **`C:\Claude_Archive`** - Unknown contents
3. **`C:\Dev\ClaudeExportFixer`** - ✅ **THE NEW UNIFIED SYSTEM (v2.0.0)**
4. **`C:\Dev\chat_log_chunker_v1`** - Old chunker project

### User Profile Directories
5. **`C:\Users\carucci_r\chat_log_chunker_v1`** - Duplicate?
6. **`C:\Users\carucci_r\Documents\chat_log_chunker`** - Another copy?
7. **`C:\Users\carucci_r\Documents\chat_watcher`** - Related project?
8. **`C:\Users\carucci_r\Documents\chunker`** - Yet another copy?

---

## 🚨 Your Blind Spots & Key Questions

### Blind Spot #1: **Data Loss Risk**
**Question:** Which directories contain PROCESSED OUTPUT that you need to keep?
- `C:\_chunker\04_output\` - Has processed chunks
- Other directories may also have valuable processed data

### Blind Spot #2: **Unprocessed Files**
**Question:** Are there unprocessed files waiting in any `02_data` folders?
- We found 4 files in `C:\_chunker\02_data\` waiting to be processed
- Other directories might have unprocessed input files

### Blind Spot #3: **GitHub Repository Status**
**Question:** Which of these directories are Git repositories?
- `C:\_chunker` → GitHub: `racmac57/chunker_Web.git`
- `C:\Dev\ClaudeExportFixer` → GitHub: `racmac57/ClaudeExportFixer.git`
- Others: Unknown

### Blind Spot #4: **Configuration & Customizations**
**Question:** Do you have custom configurations that need to be preserved?
- Department-specific rules
- Custom exclude patterns
- Specialized file processors

### Blind Spot #5: **Knowledge Bases**
**Question:** Are there SQLite knowledge bases in these directories?
- Look for `*.db` files
- ChromaDB vector stores
- These contain searchable indexes of your conversations

---

## 📋 Recommended Cleanup Strategy

### Phase 1: **DISCOVERY** (Do this first!)

Before deleting anything, create an inventory:

```powershell
# Create inventory of all chunker-related directories
$dirs = @(
    "C:\_chunker",
    "C:\Claude_Archive",
    "C:\Dev\chat_log_chunker_v1",
    "C:\Users\carucci_r\chat_log_chunker_v1",
    "C:\Users\carucci_r\Documents\chat_log_chunker",
    "C:\Users\carucci_r\Documents\chat_watcher",
    "C:\Users\carucci_r\Documents\chunker"
)

foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "`n========== $dir ==========" -ForegroundColor Cyan
        
        # Check if it's a git repo
        if (Test-Path "$dir\.git") {
            Write-Host "   [GIT REPO]" -ForegroundColor Yellow
            cd $dir
            git remote -v | Out-String
        }
        
        # Check for important folders
        @("02_data", "04_output", "03_archive") | ForEach-Object {
            $subdir = Join-Path $dir $_
            if (Test-Path $subdir) {
                $count = (Get-ChildItem $subdir -Recurse -File -ErrorAction SilentlyContinue).Count
                Write-Host "   $_ : $count files" -ForegroundColor Green
            }
        }
        
        # Check for database files
        $dbs = Get-ChildItem $dir -Filter "*.db" -Recurse -ErrorAction SilentlyContinue
        if ($dbs) {
            Write-Host "   [DATABASES FOUND]" -ForegroundColor Magenta
            $dbs | ForEach-Object { Write-Host "      - $($_.FullName)" }
        }
        
        # Check for unprocessed files
        $dataDir = Join-Path $dir "02_data"
        if (Test-Path $dataDir) {
            $unprocessed = (Get-ChildItem $dataDir -File -ErrorAction SilentlyContinue).Count
            if ($unprocessed -gt 0) {
                Write-Host "   [UNPROCESSED FILES: $unprocessed]" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "$dir - NOT FOUND" -ForegroundColor Gray
    }
}
```

### Phase 2: **CONSOLIDATE** (After inventory)

Based on what you find, consolidate data:

#### Option A: Keep Processed Output Organized
```powershell
# Create archive directory
$archiveRoot = "C:\Chunker_Archive_2025_10_29"
New-Item -ItemType Directory -Path $archiveRoot -Force

# For each old directory, preserve processed output
foreach ($oldDir in $dirs) {
    if (Test-Path $oldDir) {
        $dirName = Split-Path $oldDir -Leaf
        $archivePath = Join-Path $archiveRoot $dirName
        
        # Copy only valuable folders
        Copy-Item -Path "$oldDir\04_output" -Destination "$archivePath\04_output" -Recurse -ErrorAction SilentlyContinue
        Copy-Item -Path "$oldDir\03_archive" -Destination "$archivePath\03_archive" -Recurse -ErrorAction SilentlyContinue
        Copy-Item -Path "$oldDir\*.db" -Destination $archivePath -ErrorAction SilentlyContinue
        
        # Copy documentation
        Copy-Item -Path "$oldDir\*.md" -Destination $archivePath -ErrorAction SilentlyContinue
        Copy-Item -Path "$oldDir\99_doc" -Destination "$archivePath\docs" -Recurse -ErrorAction SilentlyContinue
    }
}
```

#### Option B: Process Remaining Files First
```powershell
# Find all unprocessed files
$unprocessedFiles = @()
foreach ($oldDir in $dirs) {
    $dataDir = Join-Path $oldDir "02_data"
    if (Test-Path $dataDir) {
        $files = Get-ChildItem $dataDir -File -ErrorAction SilentlyContinue
        if ($files) {
            $unprocessedFiles += $files
        }
    }
}

# Copy to ClaudeExportFixer for processing
foreach ($file in $unprocessedFiles) {
    Copy-Item $file.FullName -Destination "C:\Dev\ClaudeExportFixer\01_input\"
}

# Then run the new unified system
cd C:\Dev\ClaudeExportFixer
python process_workflow.py
```

### Phase 3: **CLEAN UP** (Final step)

After consolidating data:

```powershell
# Move old directories to archive (don't delete yet!)
$trashDir = "C:\OldChunkerProjects_Archive_2025_10_29"
New-Item -ItemType Directory -Path $trashDir -Force

foreach ($oldDir in $dirs) {
    if ($oldDir -ne "C:\Dev\ClaudeExportFixer") {  # Don't archive the new system!
        if (Test-Path $oldDir) {
            $dirName = Split-Path $oldDir -Leaf
            Move-Item -Path $oldDir -Destination "$trashDir\$dirName" -Force
        }
    }
}
```

---

## 🎯 Specific Actions for `C:\_chunker`

This directory has active data. Here's what to do:

### Step 1: Process Remaining Files
```powershell
cd C:\_chunker

# Check what's waiting
Get-ChildItem 02_data -File

# Option A: Process with old chunker
python watcher_splitter.py

# Option B: Move to new system
Copy-Item 02_data\* -Destination C:\Dev\ClaudeExportFixer\01_input\
cd C:\Dev\ClaudeExportFixer
python process_workflow.py
```

### Step 2: Preserve Documentation
```powershell
# Copy docs to new system
Copy-Item C:\_chunker\99_doc\*.md -Destination C:\Dev\ClaudeExportFixer\docs\legacy_chunker\
Copy-Item C:\_chunker\*.md -Destination C:\Dev\ClaudeExportFixer\docs\legacy_chunker\
```

### Step 3: Archive Processed Output
```powershell
# Option A: Keep in place for reference
# Just leave it - disk space is cheap

# Option B: Move to dated archive
$archiveDate = Get-Date -Format "yyyy_MM_dd"
Move-Item C:\_chunker -Destination "C:\Chunker_Archive_$archiveDate"
```

---

## 💡 My Recommendation

### **SAFEST APPROACH:**

1. **DO NOT DELETE ANYTHING YET**
2. **Run the discovery script first** (see Phase 1)
3. **Review the inventory** - understand what's in each directory
4. **Process any unprocessed files** - don't lose pending work
5. **Move (don't delete) old directories** to a dated archive folder
6. **Keep the archive for 30-60 days** - verify you don't need anything
7. **Only then delete** the archive folder

### **Going Forward:**

- ✅ **Use ONLY:** `C:\Dev\ClaudeExportFixer` (v2.0.0 unified system)
- ✅ **GitHub:** Keep pushing to `racmac57/ClaudeExportFixer.git`
- ✅ **Clone on other machines** from GitHub
- ❌ **Stop using:** All other chunker directories

---

## 🤖 Should Claude Code Handle This?

**YES and NO:**

### Claude Code CAN Help With:
- ✅ Running the discovery script
- ✅ Analyzing what's in each directory
- ✅ Processing unprocessed files
- ✅ Moving documentation files
- ✅ Organizing the archive

### Claude Code SHOULD NOT:
- ❌ Delete directories without your explicit approval
- ❌ Make decisions about which data to keep
- ❌ Risk data loss

### **My Recommendation:** 
Use Claude Code to **gather information and prepare**, but YOU make the final decisions on what to archive/delete.

---

## 📊 Next Steps

1. **Run the discovery script** → Create inventory report
2. **Review the report with me** → I'll help you decide what to keep
3. **Process unprocessed files** → Don't lose pending work
4. **Consolidate valuable data** → Move to archive
5. **Clean up directories** → Move (not delete) old folders
6. **Verify for 30 days** → Make sure nothing is missing
7. **Final cleanup** → Delete old archives

---

## 🎯 Questions to Answer Before Cleanup

1. **Which directory has your most recent processed output?**
2. **Do you need the processed chunks from all directories?**
3. **Are there knowledge bases (*.db files) you want to preserve?**
4. **Do any directories have custom configurations you need?**
5. **Are there unprocessed files waiting in ANY directory?**
6. **Which GitHub repos do you want to keep active?**
7. **Do you want to consolidate all processed output into one archive?**

---

**Would you like me to run the discovery script to create an inventory?**

