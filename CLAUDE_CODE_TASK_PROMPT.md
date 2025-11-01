# Claude Code Task Prompt - Phase 1 Completion & Testing

## Context
You are Claude Code assisting with the Enterprise Chunker project. Grok has provided recommendations for moving from a copy-based to a move-based file workflow to reduce storage bloat and OneDrive sync overhead by 50-60%. Core Phase 1 implementation is complete; remaining tasks need testing and validation.

## Repository Status
- **Location**: `C:\_chunker`
- **Remote**: https://github.com/racmac57/chunker_Web
- **Recent Commits**: 10 commits implementing Grok recommendations
- **Status**: Core implementation complete, testing needed

## Completed Work
✅ SendTo script optimized (`Chunker_MoveOptimized.ps1`)  
✅ Archive function enhanced (`celery_tasks.py`)  
✅ Configuration updated (`config.json`)  
✅ Documentation created (5 new markdown files)  
✅ Git repository synchronized

## Remaining Tasks

### Priority 1: Testing & Validation (CRITICAL)

#### Task 1.1: End-to-End Workflow Test
**Objective**: Verify the complete move-based workflow from SendTo through archiving

**Steps**:
1. Create a test markdown file: `test_move_workflow.md` with sample content
2. Place it in OneDrive (or simulate OneDrive location)
3. Right-click → Send To → Chunker (using optimized script)
4. Verify:
   - ✅ File removed from source (MOVE successful)
   - ✅ File appears in `02_data/`
   - ✅ `.origin.json` manifest created with correct data
   - ✅ Watcher processes the file
   - ✅ Output created in `04_output/`
   - ✅ File MOVED to `03_archive/{department}/`
   - ✅ Manifest attached to archive
   - ✅ No errors in logs

**Expected Output**: All verifications pass with INFO-level success logs

**Validation Commands**:
```powershell
# Check file locations
Test-Path "C:\_chunker\02_data\test_move_workflow.md"
Test-Path "C:\_chunker\02_data\test_move_workflow.md.origin.json"
Test-Path "C:\_chunker\03_archive\admin\test_move_workflow_*.md"
Get-ChildItem "C:\_chunker\04_output\*\test_move_workflow*" -Recurse

# Check logs for errors
Get-Content "C:\_chunker\05_logs\*.log" | Select-String -Pattern "ERROR|WARNING" | Select-Object -Last 20
```

---

#### Task 1.2: Retry Logic Test
**Objective**: Verify MOVE retry and fallback behavior

**Steps**:
1. Create a locked/copy-protected test file
2. Attempt to process it through SendTo
3. Verify:
   - ✅ 3 retry attempts logged
   - ✅ Fallback to COPY if all MOVE attempts fail
   - ✅ Warning messages generated
   - ✅ File eventually processed

**Validation**: Check logs for retry attempts and fallback

---

#### Task 1.3: Manifest Validation Test
**Objective**: Test manifest handling in various scenarios

**Scenarios**:
1. **Valid manifest**: Create proper `.origin.json`, verify loading
2. **Invalid manifest**: Corrupt JSON, verify graceful handling
3. **Missing manifest**: Process file without manifest, verify defaults used
4. **Department detection**: Verify correct department from manifest

**Validation**: All scenarios handled without crashes

---

#### Task 1.4: OneDrive Sync Impact Test
**Objective**: Measure sync bandwidth reduction

**Steps**:
1. Monitor OneDrive Activity Center before/after implementation
2. Process 10 sample files
3. Measure:
   - Sync bandwidth used
   - Sync duration
   - Any conflicts or errors

**Expected**: Significant reduction in sync activity

---

### Priority 2: Source Folder Consolidation

#### Task 2.1: Analyze Source Folder
**Objective**: Understand what files are in `source/` folder

**Steps**:
```powershell
# Get statistics
Get-ChildItem "C:\_chunker\source" -Recurse -File | Measure-Object -Property Length -Sum
Get-ChildItem "C:\_chunker\source" -Recurse -File | Group-Object -Property Extension | Sort-Object Count -Descending

# Check for duplicates
Get-ChildItem "C:\_chunker\source" -Recurse -File | 
    Group-Object -Property Name, @{E={$_.Length}} | 
    Where-Object {$_.Count -gt 1}
```

#### Task 2.2: Migrate Source Files to 04_output
**Objective**: Move files from `source/` to `04_output/` organized structure

**Steps**:
1. Create script to identify orphaned files in `source/`
2. Match them to corresponding outputs in `04_output/`
3. Organize by processing timestamp/project
4. Update any references

**Risks**: Ensure no data loss, maintain traceability

---

### Priority 3: Advanced Features

#### Task 3.1: Git Integration Testing
**Objective**: Verify optional Git commits work correctly

**Steps**:
1. Enable `"git_enabled": true` in config.json
2. Process test file
3. Verify:
   - ✅ Git commit created
   - ✅ Commit message format correct
   - ✅ Archive file committed
   - ✅ No blocking errors

#### Task 3.2: Manifest Validation Hooks
**Objective**: Add JSON schema validation for `.origin.json`

**Requirements**:
- Create JSON schema for manifest
- Add validation function in Python
- Optional: Pre-commit Git hook for validation

**Reference**: See Grok document lines 260-275 for schema

---

### Priority 4: Documentation & README Updates

#### Task 4.1: Update README.md
**Objective**: Document new move-based workflow

**Changes Needed**:
- Update file flow diagram
- Add new configuration options
- Include testing instructions
- Reference Grok recommendations

#### Task 4.2: Create Testing Guide
**Objective**: Document testing procedures

**Contents**:
- Test scenarios
- Validation commands
- Expected results
- Troubleshooting

---

## Testing Checklist

Use this checklist to track progress:

### Phase 1 Testing
- [ ] Basic file move workflow
- [ ] Retry logic (3 attempts)
- [ ] Fallback to COPY
- [ ] Manifest validation
- [ ] Department organization
- [ ] Git integration (optional)
- [ ] OneDrive sync impact

### Phase 2 Consolidation
- [ ] Source folder analysis
- [ ] File migration plan
- [ ] Data validation
- [ ] Reference updates

### Phase 3 Advanced
- [ ] Git hooks
- [ ] Manifest encryption
- [ ] Performance testing
- [ ] Scalability (1000+ files)

---

## Key Files to Reference

**Core Implementation**:
- `celery_tasks.py` - Enhanced archive function (lines 916-1014)
- `config.json` - Updated configuration
- `Chunker_MoveOptimized.ps1` - Optimized SendTo script
- `enhanced_watchdog.py` - Watcher that uses archive function

**Documentation**:
- `MOVE_WORKFLOW_IMPLEMENTATION.md` - Complete technical details
- `GROK_SIMPLIFICATION_RECOMMENDATIONS.md` - Grok's analysis
- `IMPLEMENTATION_STATUS.md` - Current progress tracker
- `GROK_REFERENCE_PACKAGE.md` - Required files list

**Original Analysis**:
- `99_doc/2025_10_31_20_47_35_Grok-File Verification and Cleanup Process.md`

---

## Configuration Reference

Current `config.json` key settings:
```json
{
  "move_to_archive": true,           // Enable MOVE workflow
  "consolidate_outputs": true,       // Merge source into output
  "git_enabled": false,              // Optional Git commits
  "copy_to_source": false,           // Disabled
  "copy_chunks_only": false,         // Disabled
  "copy_transcript_only": false,     // Disabled
  "copy_sidecar_to_source": false,   // Disabled
  "source_folder": null,             // Deprecated
  "archive_dir": "C:/_chunker/03_archive",
  "output_dir": "C:/_chunker/04_output",
  "watch_folder": "C:/_chunker/02_data"
}
```

---

## Log Analysis

Key log patterns to monitor:

**Success Indicators**:
```
[INFO] Successfully moved to archive: filename.md
[INFO] Git commit successful: Archive filename.md - 20251031_153000
[INFO] Validated manifest for: filename.md
```

**Warning Indicators**:
```
[WARNING] MOVE attempt 1 failed for filename.md
[WARNING] Used COPY fallback for archive: filename.md
[WARNING] Failed to load manifest for filename.md
```

**Error Indicators**:
```
[ERROR] All MOVE attempts failed, falling back to COPY: filename.md
[ERROR] COPY fallback also failed: ...
[ERROR] Error archiving file filename.md: ...
```

---

## Success Criteria

**Minimum Viable Testing**:
- ✅ At least 5 files processed successfully
- ✅ All MOVE operations logged properly
- ✅ Retry logic triggers on simulated failures
- ✅ Fallback to COPY works
- ✅ Zero data loss
- ✅ No crashes or hangs

**Full Testing**:
- ✅ 50+ files processed
- ✅ Various file types tested (.md, .txt, .pdf, etc.)
- ✅ Department organization correct
- ✅ Manifest validation working
- ✅ Git integration optional
- ✅ Performance within 10% of baseline
- ✅ OneDrive sync impact quantified

---

## Rollback Plan

If issues discovered:
1. Disable `move_to_archive: false` in config.json
2. Revert to old SendTo script
3. All features have fallback mechanisms
4. Data preserved in archive folder

---

## Next Actions

**Immediate (Today)**:
1. Run end-to-end workflow test
2. Verify retry logic
3. Check manifest validation
4. Monitor OneDrive sync

**Short-term (This Week)**:
1. Complete all Phase 1 testing
2. Analyze source folder
3. Document testing results
4. Update README

**Long-term (Next 2 Weeks)**:
1. Consolidate source folder
2. Implement advanced features
3. Performance benchmarking
4. User acceptance testing

---

## Questions or Issues?

Reference documentation:
- Implementation details: `MOVE_WORKFLOW_IMPLEMENTATION.md`
- Grok's recommendations: `GROK_SIMPLIFICATION_RECOMMENDATIONS.md`
- Status tracking: `IMPLEMENTATION_STATUS.md`

Expected behavior documentation in each file.

---

**Ready to begin testing? Start with Task 1.1: End-to-End Workflow Test**

