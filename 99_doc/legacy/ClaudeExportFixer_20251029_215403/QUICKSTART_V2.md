# Quick Start Guide - ClaudeExportFixer v2.0.0

**New to v2.0?** This unified system now processes **ALL file types**, not just Claude exports!

## 🚀 Getting Started (2 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs support for Excel, PDF, Word, YAML, and more.

### 2. Start the Watchdog

```bash
python start_watchdog.py
```

You'll see:
```
🚀 Unified File Processing Watchdog v2.0.0
👀 Watching: C:\Dev\ClaudeExportFixer\01_input
📤 Output: C:\Dev\ClaudeExportFixer\02_output
🔪 Chunking: ENABLED (150 sentences/chunk)
📝 Supported formats: .txt, .md, .json, .csv, .xlsx, .xls, .pdf, .py, .docx, .sql, .yaml, .toml, .xml, .log, .zip

🎯 Watchdog started!
```

### 3. Drop Files and Watch the Magic

Drop ANY supported file in `01_input/`:
- **Claude exports** (`.zip`/`.json`) → Fixed + Knowledge Base
- **Text files** (`.txt`/`.md`) → Chunked + Organized
- **Code files** (`.py`/`.sql`) → Analyzed + Chunked
- **Data files** (`.xlsx`/`.csv`) → Extracted + Chunked
- **Documents** (`.pdf`/`.docx`) → Text extracted + Chunked

Files are automatically:
1. ✅ Processed with the right handler
2. ✅ Chunked into semantic pieces (150 sentences each)
3. ✅ Categorized (chat_logs, scripts, data, documents)
4. ✅ Organized in output folders
5. ✅ Archived for safekeeping

## 📁 Where Are My Files?

After processing, check:

### Output
```
02_output/
├── claude_exports/          # Fixed Claude exports
├── chunks/                  # Chunked files by category
│   ├── chat_logs/
│   ├── scripts/
│   ├── data/
│   └── documents/
└── source/                  # Easy access to all chunks
    └── [same categories]
```

### Archive (Originals)
```
04_archive/
├── claude_exports/
├── chat_logs/
├── scripts/
├── data/
└── documents/
```

## 🎛️ Common Options

### Build Knowledge Base (for Claude Exports)
```bash
python start_watchdog.py --build-kb
```

### Fast Incremental Updates (87-90% faster)
```bash
python start_watchdog.py --build-kb --incremental
```

### Disable Chunking (Simple Copy)
```bash
python start_watchdog.py --no-chunk
```

### See Everything (Verbose Mode)
```bash
python start_watchdog.py --verbose
```

This shows:
- Which file processors are available
- Detailed processing steps
- Filter decisions
- Dependency status

### Combined
```bash
python start_watchdog.py --build-kb --incremental --verbose
```

## 🧪 Test It

Create a test file:

**File:** `01_input/test.txt`
```
This is a test. It has multiple sentences. The system will chunk this text.

This is another paragraph. It provides more content. The chunking engine uses NLTK.

Final paragraph to complete the test. Drop this in 01_input/ and watch it process!
```

**Expected Output:**
- Chunks in: `02_output/chunks/documents/2025_10_29_14_30_22_test/`
- Copies in: `02_output/source/documents/`
- Original moved to: `04_archive/documents/test.txt`

## 🔍 What's New in v2.0?

### Before (v1.x)
- Only Claude exports (ZIP/JSON)
- 7 file types supported

### After (v2.0)
- **ALL file types** (13 formats)
- **Intelligent chunking** (semantic sentence boundaries)
- **Smart categorization** (automatic)
- **Organized output** (by category)
- **One unified system** (no separate chunker needed)

## 🛠️ Configuration

### Quick Config: `config.json`

```json
{
  "chunking": {
    "enabled": true,
    "chunk_size": 150,        // Sentences per chunk
    "max_chunk_chars": 30000  // Max characters
  },

  "file_processing": {
    "supported_extensions": [".txt", ".md", ...],
    "exclude_patterns": ["_draft", "_temp"]
  }
}
```

### Change Chunk Size
Edit `config.json`:
```json
"chunk_size": 200  // Bigger chunks
```

### Add Custom Exclusions
```json
"exclude_patterns": ["_draft", "_temp", "_old"]
```

## 🐛 Troubleshooting

### File Not Processing?
Run with verbose:
```bash
python start_watchdog.py --verbose
```

Look for:
- `⏭️ Skipping [file]: unsupported extension`
- `⏭️ Skipping [file]: excluded by pattern`

**Fix:** Add extension to `config.json` or remove from exclude patterns

### No Chunks Created?
Check:
- File has enough text (>100 chars)
- File is readable (encoding issues?)
- Run with `--verbose` for details

### Missing Processor?
```bash
python start_watchdog.py --verbose
```

Shows:
```
📦 Checking file processor dependencies...
   ✓ openpyxl
   ✓ PyPDF2
   ✗ python-docx  ← Install this!
   ✓ PyYAML
```

**Fix:**
```bash
pip install python-docx
```

## 📚 Need More Help?

- **Full Guide:** `docs/UNIFIED_SYSTEM_GUIDE.md`
- **What Changed:** `docs/V2_IMPLEMENTATION_SUMMARY.md`
- **Version History:** `CHANGELOG.md`
- **Configuration:** `config.json` (edit directly)

## 💡 Pro Tips

### Tip 1: Watch Continuously
Leave the watchdog running! It processes files automatically as you drop them.

### Tip 2: Use Verbose for Debugging
When something's not working, `--verbose` shows exactly what's happening.

### Tip 3: Organize Source Folder
The `02_output/source/` folder has all chunks in one place - easy to copy elsewhere!

### Tip 4: Check Archives
Original files are safe in `04_archive/` - never lost!

### Tip 5: Incremental KB Updates
Always use `--incremental` for Claude exports - it's **87-90% faster**!

## 🎯 Examples

### Process Chat Logs
```bash
# Drop claude_conversation.md in 01_input/
# → Chunked in: 02_output/chunks/chat_logs/
# → Organized by: File name contains "claude"
```

### Process Code Files
```bash
# Drop my_script.py in 01_input/
# → AST analysis extracts: classes, functions, imports
# → Chunked in: 02_output/chunks/scripts/
```

### Process Excel Files
```bash
# Drop report.xlsx in 01_input/
# → Data extracted from all sheets
# → Chunked in: 02_output/chunks/data/
```

### Process Everything
```bash
# Drop multiple files at once
# → All processed in parallel
# → Each categorized correctly
# → All organized automatically
```

## ✅ You're Ready!

That's it! You now have a powerful unified file processing system.

**Next Steps:**
1. Start the watchdog: `python start_watchdog.py`
2. Drop some files in `01_input/`
3. Check the organized output in `02_output/`

**Questions?** Check the full guide: `docs/UNIFIED_SYSTEM_GUIDE.md`

---

**Version:** 2.0.0
**Updated:** October 29, 2025
