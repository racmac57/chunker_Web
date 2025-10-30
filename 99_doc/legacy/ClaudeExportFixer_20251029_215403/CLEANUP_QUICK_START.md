# Quick Start: Cleanup with Claude Code

## 🎯 What This Does

Safely consolidates 8+ scattered chunker directories into the new unified `ClaudeExportFixer` v2.0.0 system.

## 📋 Directories to Clean Up

1. `C:\_chunker`
2. `C:\Claude_Archive`
3. `C:\Dev\chat_log_chunker_v1`
4. `C:\Users\carucci_r\chat_log_chunker_v1`
5. `C:\Users\carucci_r\Documents\chat_log_chunker`
6. `C:\Users\carucci_r\Documents\chat_watcher`
7. `C:\Users\carucci_r\Documents\chunker`

**Keep:** `C:\Dev\ClaudeExportFixer` (v2.0.0 - The new unified system)

## 🚀 How to Use with Claude Code

### Step 1: Point Claude Code to the Right Directory
```
C:\Dev\ClaudeExportFixer
```

### Step 2: Give Claude Code the Prompt
Open and copy this file:
```
C:\Dev\ClaudeExportFixer\docs\prompts\CLAUDE_CODE_CLEANUP_CONSOLIDATION_PROMPT.md
```

Paste it into Claude Code.

### Step 3: Let Claude Code Run Phase 1 (Discovery)
Claude Code will:
- Scan all directories
- Create an inventory CSV
- Show you what's in each directory
- **NOT delete anything yet!**

### Step 4: Review the Inventory
Claude Code will show you:
- Which directories have processed output
- Where unprocessed files are waiting
- Which are Git repositories
- Database files found
- Total sizes

### Step 5: Approve Next Steps
Based on the inventory, you'll decide:
- What to preserve
- What to archive
- What can be deleted (after 30-60 days)

## ⚡ Expected Timeline

- **Phase 1 (Discovery):** 2-5 minutes
- **Phase 2 (Analysis):** 2-3 minutes
- **Phase 3 (Preservation):** 5-10 minutes
- **Phase 4 (Archiving):** 5-15 minutes (depending on sizes)
- **Phase 5 (Verification):** 2-3 minutes

**Total:** 15-35 minutes for complete cleanup

## 🎯 What You'll Get

### Files Created
1. `CLEANUP_INVENTORY_[timestamp].csv` - Complete scan results
2. `CLEANUP_ANALYSIS_REPORT.md` - Recommendations
3. `CLEANUP_SUMMARY_REPORT.md` - Final summary
4. `docs/legacy_chunker/` - Preserved docs, configs, databases

### Directories Moved
- All old chunker directories → `C:\OldChunkerProjects_Archive_[timestamp]\`
- Keep archive for 30-60 days, then delete

### End Result
- ✅ Only ONE active directory: `C:\Dev\ClaudeExportFixer`
- ✅ All important data preserved
- ✅ No data loss
- ✅ Clean, organized system

## 🛡️ Safety Features

- ✅ Discovery phase runs FIRST (no deletions)
- ✅ Everything moves to archive (not deleted)
- ✅ You approve each phase
- ✅ Backups created before moving
- ✅ 60-day retention before final deletion

## 📞 If Something Goes Wrong

The archive folder has EVERYTHING. You can restore any directory:
```powershell
# Example: Restore C:\_chunker
$archiveFolder = "C:\OldChunkerProjects_Archive_[timestamp]"
Copy-Item "$archiveFolder\_chunker" -Destination "C:\_chunker" -Recurse -Force
```

## 🎓 Why This Approach?

1. **No Data Loss** - Everything preserved in archive first
2. **Informed Decisions** - See what's there before moving
3. **Reversible** - Can restore from archive
4. **Organized** - Dated archive folder for easy tracking
5. **Safe** - 60-day retention period

---

## 🚦 Ready to Start?

1. Open Claude Code
2. Point to: `C:\Dev\ClaudeExportFixer`
3. Copy/paste: `CLAUDE_CODE_CLEANUP_CONSOLIDATION_PROMPT.md`
4. Let it run Phase 1
5. Review and approve

**Let's clean up your system! 🧹**

