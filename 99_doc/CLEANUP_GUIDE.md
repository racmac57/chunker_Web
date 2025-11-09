// 2025-10-31-03-48-33
# Enterprise_Chunker/CLEANUP_GUIDE.md
# Author: R. A. Carucci
# Purpose: Step-by-step execution guide for Enterprise Chunker directory cleanup with Grok's verified rules

# Enterprise Chunker Cleanup - Execution Guide

## Pre-Flight Checklist

### 1. Verify Configuration
- [ ] ROOT path is correct: `C:\_chunker`
- [ ] Backup critical data (02_data, 06_config)
- [ ] Close all applications using files in the directory
- [ ] Review the updated rules below

### 2. Updated Rules (Grok's Corrections)

#### KEEP (Never Delete/Move)
**Core Python Files:**
- celery_tasks.py, orchestrator.py, chunker_db.py
- file_processors.py, advanced_celery_config.py
- enhanced_watchdog.py (current watcher)

**RAG & Integration:**
- automated_eval.py, chromadb_crud.py, comprehensive_eval.py
- embedding_helpers.py, install_rag_dependencies.py
- langchain_rag_handler.py, langsmith_integration.py
- manual_process_files.py, notification_system.py
- ollama_integration.py, rag_evaluation.py, rag_integration.py
- rag_search.py, simple_rag_test.py

**Testing:**
- performance_test.py, rag_test.py, test_celery_integration.py
- test_origin_tracking.py, test_python_demo.py

**Configs & Docs:**
- config.json, requirements*.txt
- README.md, CHANGELOG.md, ENTERPRISE_CHUNKER_SUMMARY.md

**Folders:**
- 02_data, archive, 05_logs, 06_config
- source, templates, static, 99_doc

#### REMOVED FROM KEEP (Non-Existent)
- ~~watcher_splitter.py~~
- ~~web_dashboard.py~~
- ~~start_dashboard.py~~
- ~~03_archive~~ (now 'archive')
- ~~04_output, logs, SendTo~~ (absent)

#### MOVE TO 99_doc/notes
- 2025_10_30_02_39_58_c_drive_clean_cursor_process_input_folder_monitor_scr.md

#### DELETE
- _chunker.code-workspace (VS Code workspace file)
- All virtualenvs, caches, build artifacts
- Test scripts matching patterns (test_*, tmp_*, scratch_*, etc.)
- Empty directories

#### SNAPSHOT POLICY
- Keep only **latest** per project in legacy folders
- **Config backups:** config.json.backup_* → keep latest only
- Older snapshots → deleted (after move to archive/trash)

## Execution Steps

### Phase 1: DRY RUN (REQUIRED FIRST)

```python
# In chunker_cleanup.py, ensure:
ROOT = Path(r"C:\_chunker")
DRY_RUN = True
```

```bash
cd C:\_chunker
python chunker_cleanup.py
```

**Expected Output:**
- Scan summary (file counts)
- Classification results
- No actual changes made
- Reports in: `05_logs/maintenance/<timestamp>/`

### Phase 2: Review Plan

Review these files:
1. **maintenance_report.md** - Summary and preview
2. **actions_plan.json** - Complete action list
3. **inventory.csv** - All items with classifications
4. **duplicates.csv** - Duplicate files found
5. **proposed_moves.csv** - Files to be moved
6. **proposed_deletes.csv** - Files to be deleted

**Critical Checks:**
- [ ] No KEEP files in delete list
- [ ] Documentation moves look correct
- [ ] Snapshot pruning preserves latest versions
- [ ] Config backups properly handled

### Phase 3: Execute (Only After Review)

```python
# In chunker_cleanup.py, change to:
DRY_RUN = False
```

```bash
python chunker_cleanup.py
```

**Expected Actions:**
- Create 99_doc and 99_doc/notes
- Move documentation files
- Prune old snapshots (keep latest)
- Delete cruft (to recycle bin if possible)
- Update README, SUMMARY, CHANGELOG
- Generate final reports

### Phase 4: Verify Results

Check:
- [ ] Core .py files still in root
- [ ] Documentation in 99_doc/
- [ ] Transcript in 99_doc/notes/
- [ ] Latest snapshots preserved
- [ ] Config backups (only latest remains)
- [ ] Clean directory structure

Review final reports in:
`05_logs/maintenance/<timestamp>/`

## Safety Features

### Built-In Protections
1. **KEEP rules override DELETE** - No core files deleted
2. **Windows recycle bin** - Deleted files recoverable
3. **Fallback trash folder** - archive/trash/<timestamp>/
4. **Duplicate detection** - SHA-256 hash checking
5. **Conflict handling** - Auto-rename on collision

### Recovery Options
If something goes wrong:
1. Check recycle bin (Windows)
2. Check archive/trash/<timestamp>/
3. Review moved_files.csv for original locations
4. Restore from backup (02_data, 06_config)

## Expected Results

### Directory Structure After Cleanup
```
C:\_chunker/
├── 02_data/                    # Untouched
├── 05_logs/
│   └── maintenance/
│       └── <timestamp>/        # Cleanup reports
├── 06_config/                  # Config + latest backup only
├── 99_doc/                     # All documentation
│   └── notes/                  # Transcripts
├── archive/                    # Preserved
├── source/                     # Preserved
├── templates/                  # Preserved  
├── static/                     # Preserved
├── *.py                        # All core Python files
├── config.json                 # Current config
├── requirements*.txt           # Dependencies
├── README.md                   # Updated with health info
├── CHANGELOG.md                # New maintenance entry
└── ENTERPRISE_CHUNKER_SUMMARY.md  # Updated structure info
```

### Files Removed
- Virtualenvs (venv, .venv, etc.)
- Cache folders (__pycache__, etc.)
- Test cruft (test_*, tmp_*, etc.)
- VS Code workspace file
- Old snapshots (except latest per project)
- Old config backups (except latest)
- Empty directories

### Metrics Example
```
Items scanned:     450
Items kept:        380
Items moved:       12
Items deleted:     58
Snapshots pruned:  8
```

## Troubleshooting

### Issue: Permission Denied
**Solution:** Run as administrator or close apps using files

### Issue: Can't Find ROOT
**Solution:** Verify path in script: `ROOT = Path(r"C:\_chunker")`

### Issue: Too Many Deletions
**Solution:** Review classification logic, adjust DELETE rules

### Issue: Missing Files After Cleanup
**Solution:** Check moved_files.csv, recycle bin, archive/trash/

## Post-Cleanup

### Immediate Actions
1. Test core functionality (watcher, processing)
2. Verify config.json intact
3. Check documentation accessibility
4. Review maintenance_report.md

### Ongoing Maintenance
- Run cleanup quarterly or after major changes
- Keep DRY_RUN=True until confident
- Review reports before executing
- Update rules as needed

## Contact
For issues or questions: R. A. Carucci
Last Updated: 2025-10-31

---

## Quick Command Reference

```bash
# Dry run (safe, no changes)
python chunker_cleanup.py

# After review, execute cleanup
# (Edit script: DRY_RUN = False)
python chunker_cleanup.py

# View reports
cd 05_logs/maintenance/<timestamp>
# Open maintenance_report.md
```
