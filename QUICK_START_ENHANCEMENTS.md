# Quick Start: Testing Origin Tracking Enhancements

## ✅ Implementation Complete!

All three enhancements have been successfully implemented:
1. Enhanced sidecar with origin tracking
2. Better front matter with origin info
3. Sidecar copy to source in write-back

---

## 🚀 Quick Test (5 Minutes)

### Step 1: Copy Test File to Watch Folder
```bash
cd C:\_chunker
cp test_origin_tracking.md 02_data/
```

### Step 2: Run the Watcher
```bash
python watcher_splitter.py
```

*The watcher will detect the file and process it within 5 seconds*

### Step 3: Verify Results
```bash
# Run automated verification
python verify_enhancements.py
```

**Expected Output:**
```
✅ config: PASS
✅ sidecar_structure: PASS
✅ front_matter: PASS
✅ source_writeback: PASS
```

---

## 📁 What to Check

### 1. Output Folder
```bash
ls 04_output/2025_10_30_*_test_origin_tracking/
```

**Should contain:**
- `*_chunk1.txt` (and more chunks)
- `*_transcript.md` (combined file)
- `*_blocks.json` (metadata sidecar)

### 2. Sidecar JSON (Enhanced Origin)
```bash
cat 04_output/2025_10_30_*_test_origin_tracking/*_blocks.json | python -m json.tool
```

**Look for the new `origin` object:**
```json
{
  "origin": {
    "source_path": "C:\\_chunker\\02_data\\test_origin_tracking.md",
    "source_directory": "C:\\_chunker\\02_data",
    "source_filename": "test_origin_tracking.md",
    "archive_path": "C:\\_chunker\\03_archive\\admin\\test_origin_tracking.md",
    "received_at": "2025-10-30T...",
    "file_size": 2048,
    "original_size": 2048,
    "modified_time": "2025-10-30T...",
    "created_time": "2025-10-30T..."
  }
}
```

### 3. Transcript Front Matter
```bash
head -20 04_output/2025_10_30_*_test_origin_tracking/*_transcript.md
```

**Look for enhanced headers:**
```markdown
# Test Origin Tracking

**Processing Date:** 2025-10-30 22:45:00
**Source File:** test_origin_tracking.md
**Source Path:** C:\_chunker\02_data\test_origin_tracking.md
**Archive Location:** C:\_chunker\03_archive\admin\test_origin_tracking.md
**Output Folder:** C:\_chunker\04_output\2025_10_30_22_45_00_test_origin_tracking
**Original Size:** 2,048 bytes
**Total Chunks:** 2
**Department:** admin

---
```

### 4. Source Folder Write-Back
```bash
ls source/*test_origin_tracking*
```

**Should contain:**
- Chunk files (if `copy_chunks_only: true`)
- Transcript (if `copy_transcript_only: true`)
- **Sidecar JSON** (if `copy_sidecar_to_source: true`) ← NEW!

---

## 🔧 Configuration

### Current Settings (config.json)
```json
{
  "copy_to_source": true,
  "source_folder": "C:/_chunker/source",
  "copy_chunks_only": true,
  "copy_transcript_only": false,
  "copy_sidecar_to_source": true,     // ← NEW!
  "enable_json_sidecar": true
}
```

### To Change Write-Back Behavior

**Copy everything to source:**
```json
{
  "copy_chunks_only": true,
  "copy_transcript_only": true,
  "copy_sidecar_to_source": true
}
```

**Only copy sidecar:**
```json
{
  "copy_chunks_only": false,
  "copy_transcript_only": false,
  "copy_sidecar_to_source": true
}
```

**Disable write-back:**
```json
{
  "copy_to_source": false
}
```

---

## 📊 Before vs After

### Old Sidecar (Before Enhancement A)
```json
{
  "file": "C:/_chunker/02_data/example.md",
  "processed_at": "2025-10-30T22:00:00",
  "department": "admin",
  "type": ".md",
  "chunks": [...]
}
```

### New Sidecar (After Enhancement A)
```json
{
  "file": "C:/_chunker/02_data/example.md",
  "processed_at": "2025-10-30T22:00:00",
  "department": "admin",
  "type": ".md",

  "origin": {                              // ← NEW!
    "source_path": "C:\\_chunker\\02_data\\example.md",
    "source_directory": "C:\\_chunker\\02_data",
    "source_filename": "example.md",
    "archive_path": "C:\\_chunker\\03_archive\\admin\\example.md",
    "received_at": "2025-10-30T22:00:00",
    "file_size": 1024,
    "original_size": 1024,
    "modified_time": "2025-10-30T21:55:00",
    "created_time": "2025-10-30T21:50:00"
  },

  "chunks": [...]
}
```

---

### Old Front Matter (Before Enhancement B)
```markdown
# Example

**Processing Date:** 2025-10-30 22:00:00
**Source File:** example.md
**Total Chunks:** 3

---
```

### New Front Matter (After Enhancement B)
```markdown
# Example

**Processing Date:** 2025-10-30 22:00:00
**Source File:** example.md
**Source Path:** C:\_chunker\02_data\example.md           ← NEW!
**Archive Location:** C:\_chunker\03_archive\admin\example.md  ← NEW!
**Output Folder:** C:\_chunker\04_output\2025_10_30_22_00_00_example  ← NEW!
**Original Size:** 1,024 bytes                             ← NEW!
**Total Chunks:** 3
**Department:** admin                                      ← NEW!

---
```

---

### Old Write-Back (Before Enhancement C)
```
source/
├── example_chunk1.txt
├── example_chunk2.txt
└── example_chunk3.txt
```

### New Write-Back (After Enhancement C)
```
source/
├── example_chunk1.txt
├── example_chunk2.txt
├── example_chunk3.txt
└── 2025_10_30_22_00_00_example_blocks.json  ← NEW!
```

---

## ✅ Verification Checklist

After running a test file:

- [ ] Sidecar JSON created in output folder
- [ ] Sidecar has `origin` object with 8+ fields
- [ ] Transcript has enhanced front matter
- [ ] Front matter shows Source Path, Archive Location, etc.
- [ ] Sidecar JSON copied to source folder (if enabled)
- [ ] Original file moved to archive
- [ ] No errors in logs

---

## 🆘 Troubleshooting

### Issue: Sidecar not created

**Check config:**
```bash
grep enable_json_sidecar config.json
```
**Should be:** `"enable_json_sidecar": true`

---

### Issue: Sidecar missing "origin" object

**Cause:** Processing old files or using old code

**Solution:**
1. Verify backups exist: `ls *.backup_*`
2. Check current code has enhancements: `grep "origin" watcher_splitter.py`
3. Process a NEW file (not an old archived one)

---

### Issue: Sidecar not copied to source

**Check both settings:**
```bash
grep -E "(copy_to_source|copy_sidecar_to_source)" config.json
```

**Should see:**
```json
"copy_to_source": true,
"copy_sidecar_to_source": true,
```

---

### Issue: Front matter not enhanced

**Note:** Only applies to **admin** department files!

**Check department:**
- Admin files: No department keywords in path
- Other departments: Path contains "police", "legal", etc.

**To force admin:**
- Drop file directly in `02_data/` (not in subdirectory)

---

## 📞 Support

### Files Created
- `verify_enhancements.py` - Automated verification
- `test_origin_tracking.py` - Python test file
- `test_origin_tracking.md` - Markdown test file
- `ENHANCEMENT_IMPLEMENTATION_SUMMARY.md` - Full documentation

### Backups
- `watcher_splitter.py.backup_20251030_223512`
- `config.json.backup_20251030_223559`

### To Rollback
```bash
cp watcher_splitter.py.backup_20251030_223512 watcher_splitter.py
cp config.json.backup_20251030_223559 config.json
```

---

## 🎯 Next Steps

1. **Test with sample file** (5 min)
2. **Review verification results**
3. **Adjust config if needed**
4. **Process real files**
5. **Monitor logs for any issues**

**Ready to test!** 🚀
