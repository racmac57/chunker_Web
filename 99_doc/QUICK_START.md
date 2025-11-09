// 2025-10-31-03-48-33
# Enterprise_Chunker/QUICK_START.md
# Author: R. A. Carucci
# Purpose: Quick start guide for Enterprise Chunker directory cleanup - get running in 5 minutes

# Quick Start: Enterprise Chunker Cleanup

## 🚀 Get Running in 3 Steps

### Step 1: Backup (2 minutes)
```bash
# Quick backup of critical data
mkdir C:\_chunker_backup
xcopy C:\_chunker\config.json C:\_chunker_backup\ /Y
xcopy C:\_chunker\02_data C:\_chunker_backup\02_data\ /E /I
xcopy C:\_chunker\06_config C:\_chunker_backup\06_config\ /E /I
```

### Step 2: Dry Run (1 minute)
```bash
cd C:\_chunker
python chunker_cleanup.py
```
**What happens:** Scans everything, creates plan, makes NO changes

### Step 3: Review & Execute (2 minutes)
```bash
# Open the report
start 05_logs\maintenance\<latest_folder>\maintenance_report.md

# If it looks good:
# 1. Edit chunker_cleanup.py
# 2. Change DRY_RUN = False
# 3. Run again
python chunker_cleanup.py
```

---

## 📋 What Gets Changed

### ✅ Keeps (Never Touches)
- All 18+ Python files (enhanced_watchdog.py, RAG files, tests)
- config.json, requirements*.txt
- 02_data, archive, 05_logs, 06_config folders
- README, CHANGELOG, ENTERPRISE_CHUNKER_SUMMARY

### 📦 Moves (Organizes)
- Documentation → 99_doc/
- Transcripts → 99_doc/notes/

### 🗑️ Deletes (Cleans Up)
- Virtualenvs (venv, .venv)
- Cache folders (__pycache__)
- Test cruft (test_*, tmp_*, scratch_*)
- _chunker.code-workspace
- Old snapshots (keeps latest only)

---

## ⚠️ Safety Checklist

Quick checks before running:
- [ ] Backups done
- [ ] Nothing using chunker files
- [ ] DRY_RUN = True first time
- [ ] Reviewed reports before DRY_RUN = False

---

## 📊 Expected Results

### Before
```
C:\_chunker/
├── Many scattered .md files
├── venv/ (300+ MB)
├── __pycache__/ folders everywhere
├── Multiple config backups
├── Old test scripts
└── _chunker.code-workspace
```

### After
```
C:\_chunker/
├── 02_data/ ✅
├── 05_logs/
│   └── maintenance/<timestamp>/ 📊 Reports here
├── 06_config/ ✅
├── 99_doc/ 📚 All docs organized
│   └── notes/ 📝 Transcripts
├── archive/ ✅
├── 18+ .py files ✅
├── config.json ✅
├── requirements*.txt ✅
├── README.md ✅ (updated)
├── CHANGELOG.md ✅ (updated)
└── ENTERPRISE_CHUNKER_SUMMARY.md ✅ (updated)
```

---

## 🔍 Files You Created

1. **chunker_cleanup.py** - Main cleanup script
2. **CLEANUP_GUIDE.md** - Detailed execution guide
3. **GROK_UPDATES_SUMMARY.md** - Changes from Grok
4. **PRE_FLIGHT_CHECKLIST.md** - Comprehensive checklist
5. **QUICK_START.md** - This file

---

## 📝 Console Output Example

### Dry Run
```
================================================================================
Enterprise Chunker Directory Cleanup
================================================================================
Root: C:\_chunker
Mode: DRY RUN
Timestamp: 2025_10_31_03_48_33
================================================================================

Scanning C:\_chunker...
Scanned 437 items

Found 3 duplicate groups

Classifying items...
Classification complete

=== DRY RUN MODE - NO CHANGES WILL BE MADE ===

Items to move: 12
Items to delete: 67

================================================================================
SUMMARY
================================================================================
Items scanned:     437
Items kept:        358
Items moved:       0
Items deleted:     0
Snapshots pruned:  12
Duplicate groups:  3
================================================================================

*** DRY RUN COMPLETE - Review reports in 05_logs/maintenance/2025_10_31_03_48_33/
*** Set DRY_RUN=False and run again to execute cleanup
```

### Execute Run
```
================================================================================
Enterprise Chunker Directory Cleanup
================================================================================
Root: C:\_chunker
Mode: EXECUTE
Timestamp: 2025_10_31_03_50_15
================================================================================

Scanning C:\_chunker...
Scanned 437 items
...
=== EXECUTING CLEANUP ===

Items to move: 12
Items to delete: 67
Moved: some_doc.md -> 99_doc
Moved: transcript.md -> 99_doc/notes
Deleted (to recycle bin): venv
Deleted (to recycle bin): __pycache__
...
================================================================================
SUMMARY
================================================================================
Items scanned:     437
Items kept:        358
Items moved:       12
Items deleted:     67
Snapshots pruned:  12
Duplicate groups:  3
================================================================================

*** CLEANUP COMPLETE

Reports: C:\_chunker\05_logs\maintenance\2025_10_31_03_50_15
```

---

## 🆘 Troubleshooting

### "Permission denied"
→ Close editors, run as admin

### "Can't find module"
→ Ensure Python 3.7+ installed

### "Too many files to delete"
→ Review actions_plan.json, verify rules

### "Missing files after"
→ Check recycle bin, archive/trash/, moved_files.csv

---

## 📞 Need Help?

1. **Check reports:** 05_logs/maintenance/<timestamp>/
2. **Review logs:** Look for ERROR messages in console
3. **Restore from backup:** Use C:\_chunker_backup
4. **Contact:** R. A. Carucci

---

## 🎯 Quick Decision Tree

```
Start here → Backups done? 
    ↓ Yes
Run DRY RUN → python chunker_cleanup.py
    ↓
Review reports → Look good?
    ↓ Yes
Change DRY_RUN=False → Run again
    ↓
Verify results → All good?
    ↓ Yes
✅ DONE!
```

---

**Time Investment:** 5 minutes + review time  
**Risk Level:** Low (dry run first, recycle bin, backups)  
**Benefit:** Clean, organized, maintainable directory structure

**Last Updated:** 2025-10-31  
**Author:** R. A. Carucci
