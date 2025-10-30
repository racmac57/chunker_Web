# 📁 Workflow Guide - Drag-and-Drop Processing

## ✨ New! Simplified Folder Structure

Instead of typing commands, just **drag files into folders**!

```
ClaudeExportFixer/
├── 01_input/           👈 DROP YOUR FILES HERE
├── 02_output/          👈 FIXED FILES APPEAR HERE
├── 03_knowledge_base/  👈 DATABASE CREATED HERE
└── process_workflow.py 👈 RUN THIS TO PROCESS
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Drop Your File

1. Download your Claude export from https://claude.ai/settings/export
2. **Drag the ZIP file into `01_input/` folder**
3. That's it! Ready to process.

### Step 2: Process the File

**Option A - Double-click the batch file:**
```
scripts\windows\process_workflow.bat
```

**Option B - Run from command line:**
```cmd
python process_workflow.py
```

**Option C - Process + Build Knowledge Base:**
```cmd
python process_workflow.py --build-kb --incremental
```

### Step 3: Use Your Fixed Files

- **Fixed exports**: Check `02_output/` folder
- **Upload to viewer**: Drag fixed file to https://tools.osteele.com/claude-chat-viewer
- **Query knowledge base**: `python claude_kb_query.py`

---

## 📂 Folder Details

### 📥 `01_input/` - Input Files

**What to put here:**
- Claude export ZIP files (e.g., `data-2025-10-28-abcd1234.zip`)
- Claude JSON files (e.g., `conversations.json`)

**Example:**
```
01_input/
├── data-2025-10-28-abcd1234.zip
├── conversations-backup.json
└── README.md
```

---

### 📤 `02_output/` - Processed Files

**What you'll find:**
- Fixed ZIP files ready for osteele viewer
- Filenames have `-FIXED-[timestamp]` suffix
- Upload these to the viewer

**Example:**
```
02_output/
├── data-2025-10-28-FIXED-20251028-161000.zip  ✅ Ready!
├── conversations-backup-FIXED-20251028-161030.zip
└── README.md
```

**Verify:** Should load without errors at https://tools.osteele.com/claude-chat-viewer

---

### 🗄️ `03_knowledge_base/` - Database Files

**What you'll find:**
- `claude_knowledge_base.db` - Your searchable conversation database
- `claude_knowledge_base.db-journal` - SQLite journal (temporary)

**Query it:**
```cmd
# Interactive mode
python claude_kb_query.py

# Direct query
python claude_kb_query.py --query "Power BI DAX measures"

# Semantic search
python claude_kb_query.py --query "data visualization" --semantic

# Export results as HTML
python claude_kb_query.py --query "Python examples" --export results.html
```

**Analytics:**
```cmd
# Generate dashboard
python claude_kb_analytics.py --dashboard

# View statistics
python claude_kb_analytics.py --overview

# Extract code
python claude_kb_analytics.py --code-by-language python
```

---

## 🔄 Workflow Examples

### Example 1: First Time Processing

```cmd
# Step 1: Drop file in 01_input/
# (Drag data-2025-10-28.zip into 01_input/)

# Step 2: Process it
python process_workflow.py --build-kb

# Step 3: Query your conversations
python claude_kb_query.py --query "How do I use arcpy?"
```

---

### Example 2: Monthly Update (Incremental)

```cmd
# Step 1: Drop new export in 01_input/
# (Drag data-2025-11-28.zip into 01_input/)

# Step 2: Process with incremental update (87-90% faster!)
python process_workflow.py --build-kb --incremental

# Step 3: Query updated database
python claude_kb_query.py
```

**Incremental mode**: Only processes new/changed conversations!

---

### Example 3: Multiple Files

```cmd
# Drop multiple files in 01_input/:
01_input/
├── export-jan.zip
├── export-feb.zip
├── export-mar.zip

# Process all at once
python process_workflow.py

# All fixed files appear in 02_output/:
02_output/
├── export-jan-FIXED-20251028-120000.zip
├── export-feb-FIXED-20251028-120030.zip
├── export-mar-FIXED-20251028-120100.zip
```

---

## 🎯 Command Reference

### Process Workflow

```cmd
# Basic processing (all files in 01_input/)
python process_workflow.py

# Process + build knowledge base
python process_workflow.py --build-kb

# Process + incremental KB update (faster!)
python process_workflow.py --build-kb --incremental

# Show version
python process_workflow.py --version
```

### Manual Processing (Advanced)

```cmd
# Single file (specify paths)
python patch_conversations.py "01_input\my-export.zip" "02_output\fixed.zip"

# With GUI
python patch_conversations.py --gui
```

### Knowledge Base Operations

```cmd
# Build from scratch
python claude_knowledge_base.py "02_output\fixed-export.zip"

# Incremental update
python claude_knowledge_base.py "02_output\new-export.zip" --incremental

# Show what changed
python claude_knowledge_base.py "02_output\new-export.zip" --show-changes
```

### Query Knowledge Base

```cmd
# Interactive REPL
python claude_kb_query.py

# Direct query
python claude_kb_query.py --query "your question"

# Limit results
python claude_kb_query.py --query "Python" --limit 10

# Semantic search
python claude_kb_query.py --query "data analysis" --semantic

# Export as HTML
python claude_kb_query.py --query "examples" --export output.html
```

### Analytics

```cmd
# Overview statistics
python claude_kb_analytics.py --overview

# Timeline analysis
python claude_kb_analytics.py --timeline daily
python claude_kb_analytics.py --timeline weekly
python claude_kb_analytics.py --timeline monthly

# Code extraction
python claude_kb_analytics.py --code-by-language python
python claude_kb_analytics.py --code-by-language javascript

# Technology stack
python claude_kb_analytics.py --tech-stack

# Related conversations
python claude_kb_analytics.py --related "conversation-uuid-here"

# Full HTML dashboard
python claude_kb_analytics.py --dashboard --output "dashboard.html"
```

---

## 💡 Pro Tips

### Tip 1: Keep Input Files as Backups
The `01_input/` folder is perfect for keeping your original Claude exports as backups. The script doesn't delete them after processing.

### Tip 2: Use Incremental Mode
When you get a new Claude export each month:
```cmd
python process_workflow.py --build-kb --incremental
```
This is **87-90% faster** than rebuilding from scratch!

### Tip 3: Batch File Shortcut
Create a desktop shortcut to `scripts\windows\process_workflow.bat` for one-click processing.

### Tip 4: Git Ignores Your Data
The workflow folders are in `.gitignore`, so your personal conversation data stays local and won't be pushed to GitHub.

### Tip 5: Clean Up Old Outputs
Periodically clean up the `02_output/` folder if it gets cluttered:
```cmd
# Keep only the most recent 5 files
Get-ChildItem "02_output\*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 5 | Remove-Item
```

---

## 📊 Performance

| Task | Time (401 conversations) | Mode |
|------|--------------------------|------|
| Fix export | ~5 seconds | Normal |
| Build KB (first time) | ~10-12 seconds | Full |
| Update KB | ~1-2 seconds | Incremental (87-90% savings!) |
| Query KB | <1 second | Both |
| Generate dashboard | ~2-3 seconds | Both |

---

## 🆘 Troubleshooting

### No files found in 01_input/
**Solution**: Make sure you dropped a `.zip` or `.json` file (not a folder) into `01_input/`

### Output file already exists
**Solution**: The script adds timestamps to avoid conflicts. Each run creates a new file.

### Knowledge base is locked
**Solution**: Close any programs using the database (like DB Browser for SQLite).

### Import error: No module named 'X'
**Solution**: Install dependencies:
```cmd
pip install ijson nltk sentence-transformers numpy
```

---

## 🔗 Related Documentation

- **README.md** - Main project documentation
- **DESKTOP_SETUP_INSTRUCTIONS.md** - Initial setup guide
- **KNOWLEDGE_BASE_GUIDE.md** - Detailed KB features
- **CHANGELOG.md** - Version history

---

**Created**: 2025-10-28  
**Version**: 1.0.0  
**Compatible with**: ClaudeExportFixer v1.5.0+

