# ClaudeExportFixer Quick Start Guide

## 🚀 Installation

```bat
cd C:\Dev\ClaudeExportFixer
scripts\windows\create_venv.bat
```

## 📋 Common Tasks

### 1. Fix Export for osteele Viewer

```bat
python patch_conversations.py export.zip -o fixed.zip --zip-output --pretty
```

**What it does:**
- Adds all required schema fields (`content`, `model`, `index`, `model_slug`)
- Merges rich attachments with metadata
- Handles both conversation formats (list/dict)
- ✅ Output ready for https://tools.osteele.com/claude-chat-viewer

### 2. Build Searchable Knowledge Base

```bat
python claude_knowledge_base.py export.zip my_knowledge_base.db
```

**What you get:**
- Searchable SQLite database with FTS5
- 18,000+ semantic chunks (sentence-aware, 150 words max)
- Auto-extracted tags (tech keywords, dates, content types)
- File/attachment content indexed
- Analytics-ready schema

**Example results (401 conversations):**
- 10,369 messages → 18,354 searchable chunks
- 31 unique tags extracted
- ~1.7M tokens indexed
- 194 MB database

### 3. Launch GUI

```bat
python patch_conversations.py --gui
# OR
scripts\windows\run_gui.bat
```

**Features:**
- Drag-and-drop file selection
- Real-time processing logs
- One-click output opening

## 🔍 What's Next?

### Query Your Knowledge Base (Coming in v1.2.1)
```python
from claude_knowledge_base import ClaudeKnowledgeBase

kb = ClaudeKnowledgeBase("my_knowledge_base.db")

# Search conversations
results = kb.search("power bi dax measures", limit=10)
for r in results:
    print(f"{r['conversation_name']}: {r['snippet']}")

# Get statistics
stats = kb.get_stats()
print(f"Total conversations: {stats['conversations']}")
```

### Current Capabilities
- ✅ Full-text search across all conversations
- ✅ Tag-based filtering
- ✅ File content search
- ✅ Date range queries (SQL)
- ⏳ Vector search (planned for v1.3.0)

## 📊 Knowledge Base Schema

The database contains:

**Tables:**
- `conversations` - Main conversation metadata (401 rows)
- `messages` - Individual messages (10,369 rows)
- `chunks` - Semantic text chunks (18,354 rows)
- `files` - Attachments with extracted content (958 rows)
- `tags` - Auto-extracted tags (31 rows)
- `search_index` - FTS5 full-text search index

**Example SQL Queries:**

```sql
-- Find conversations about Python
SELECT name, created_at FROM conversations 
WHERE tags LIKE '%python%' 
ORDER BY created_at DESC;

-- Count messages by sender
SELECT sender, COUNT(*) as count FROM messages 
GROUP BY sender;

-- Find all code-containing conversations
SELECT DISTINCT c.name FROM conversations c
JOIN messages m ON c.uuid = m.conversation_uuid
WHERE m.has_code = 1;

-- Search across all content
SELECT * FROM search_index 
WHERE search_index MATCH 'power bi'
LIMIT 10;
```

## 🛠️ Verification Tools

### Check v1.2.0 Compliance
```bat
python utils\verify_v120_fix.py
```

Shows:
- ✅ 100% of conversations have `model`
- ✅ 100% of messages have `index`, `model_slug`, `content`

### Comprehensive Validation
```bat
python utils\comprehensive_verification.py
```

Shows:
- Total conversations, messages, files
- File UUID coverage
- Rich metadata preservation
- Attachment merging status

### Strict osteele Validation
```bat
python utils\strict_validator.py conversations.json
```

Validates against osteele viewer schema requirements.

## 📦 Build Executables

### CLI Only
```bat
scripts\windows\build_exe.bat
```
Output: `dist/patch_conversations.exe`

### GUI (No Console)
```bat
scripts\windows\build_exe_gui.bat
```
Output: `dist/patch_conversations.exe --gui` (no console window)

## 🔗 Integration with Grok

See `GROK_KNOWLEDGE_BASE_PROMPT.md` for:
- Vector embeddings integration
- Query interface development
- Analytics features
- Performance optimizations

## ❓ Troubleshooting

### osteele Viewer Errors
If conversations fail to load:
1. Check browser console (F12 → Console tab)
2. Look for specific validation errors
3. Run `python utils\strict_validator.py` on your export
4. See `utils/` folder for 20+ diagnostic scripts

### Knowledge Base Issues
- **Too slow?** Try processing smaller batches or optimize chunking size
- **Missing data?** Check `claude_kb.log` for processing errors
- **Search not working?** Verify FTS5 is enabled: `SELECT * FROM search_index LIMIT 1;`

## 📚 More Resources

- **README.md** - Complete documentation
- **CHANGELOG.md** - Version history
- **SUMMARY.md** - Project overview
- **CONTRIBUTING.md** - Contribution guidelines

---

**Version**: 1.2.0  
**Last Updated**: 2025-10-27

