# ClaudeExportFixer - Desktop Setup Instructions

## ✅ Confirmed: Repository is on GitHub

**Repository Name**: `ClaudeExportFixer`  
**GitHub URL**: https://github.com/racmac57/ClaudeExportFixer  
**Current Version**: v1.5.0 (with incremental updates)

---

## 🖥️ Setting Up on Your Desktop Computer

### Prerequisites
- Git installed on your desktop
- Python 3.8+ installed
- Internet connection

---

## Step-by-Step Setup

### 1️⃣ Clone the Repository

Open **Command Prompt** or **PowerShell** on your desktop and run:

```powershell
# Navigate to where you want the project
cd C:\Dev

# Clone from GitHub
git clone https://github.com/racmac57/ClaudeExportFixer.git

# Navigate into the project
cd ClaudeExportFixer
```

**Alternative location** (if you prefer a different path):
```powershell
cd C:\Users\YourUsername\Documents
git clone https://github.com/racmac57/ClaudeExportFixer.git
cd ClaudeExportFixer
```

---

### 2️⃣ Install Python Dependencies

```powershell
# Install core dependencies
pip install ijson

# Install knowledge base dependencies (optional but recommended)
pip install nltk sentence-transformers numpy
```

**Note**: The knowledge base features require additional packages. If you only need the basic Claude export fixer, just `ijson` is sufficient.

---

### 3️⃣ Download NLTK Data (For Knowledge Base)

If you installed `nltk`, run this once:

```powershell
python -c "import nltk; nltk.download('punkt')"
```

---

### 4️⃣ Verify Installation

```powershell
# Check version
python patch_conversations.py --version

# Run tests (optional)
pytest
```

Expected output:
```
ClaudeExportFixer v1.5.0
```

---

## 🚀 Quick Start Usage

### GUI Mode (Recommended)
```powershell
python patch_conversations.py --gui
```

### CLI Mode
```powershell
# Fix a Claude export
python patch_conversations.py "path\to\your\claude-export.zip" "path\to\output-fixed.zip"

# With incremental updates (much faster for subsequent exports)
python patch_conversations.py "new-export.zip" "output-fixed.zip" --incremental
```

---

## 📚 Knowledge Base Features

### Build Knowledge Base
```powershell
# First time (full build)
python claude_knowledge_base.py "claude-export-fixed.zip"

# Incremental update (87-90% faster!)
python claude_knowledge_base.py "new-export-fixed.zip" --incremental
```

### Query Knowledge Base
```powershell
# Interactive mode
python claude_kb_query.py

# Direct query
python claude_kb_query.py --query "How do I process crime data in Python?"

# Semantic search
python claude_kb_query.py --query "arcpy automation" --semantic
```

### Analytics Dashboard
```powershell
# Generate HTML dashboard
python claude_kb_analytics.py --dashboard

# View statistics
python claude_kb_analytics.py --overview
```

---

## 📁 Project Structure

```
ClaudeExportFixer/
├── patch_conversations.py      # Main fixer script
├── gui.py                       # Tkinter GUI
├── claude_knowledge_base.py    # KB builder
├── claude_kb_query.py          # Query tool
├── claude_kb_analytics.py      # Analytics suite
├── incremental_utils.py        # Incremental update logic
├── requirements.txt            # Python dependencies
├── tests/                      # Test suite (24 tests)
├── docs/                       # Documentation
│   ├── QUICK_START.md
│   ├── KNOWLEDGE_BASE_GUIDE.md
│   ├── GROK_EXPORT_ANALYSIS.md
│   └── prompts/                # AI collaboration prompts
└── archive/                    # Archived files (not in Git)
```

---

## 🔄 Keeping Your Desktop Sync'd

### Pull Latest Changes
```powershell
cd C:\Dev\ClaudeExportFixer
git pull origin main
```

### Check for Updates
```powershell
git fetch origin
git status
```

If it says "Your branch is behind", run:
```powershell
git pull origin main
```

---

## 🛠️ Troubleshooting

### Issue: `git` command not found
**Solution**: Install Git from https://git-scm.com/download/win

### Issue: `python` command not found
**Solution**: 
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"

### Issue: `pip install` fails with permission error
**Solution**: Use `--user` flag:
```powershell
pip install --user ijson nltk sentence-transformers numpy
```

### Issue: NLTK punkt download fails
**Solution**: Download manually:
```powershell
python
>>> import nltk
>>> nltk.download('punkt', download_dir='C:/Users/YourUsername/nltk_data')
>>> exit()
```

### Issue: Large files not downloading
**Solution**: This is normal. Large files (like `archive/old_exports`) are excluded from Git via `.gitignore`. They're only stored locally on your laptop.

---

## 📝 Usage Examples

### Example 1: Fix Claude Export
```powershell
python patch_conversations.py ^
  "C:\Users\YourName\Downloads\claude-export-2025-10-28.zip" ^
  "C:\Users\YourName\Documents\claude-fixed.zip"
```

### Example 2: Build Knowledge Base
```powershell
# First time
python claude_knowledge_base.py ^
  "C:\Users\YourName\Documents\claude-fixed.zip"

# Creates: claude_knowledge_base.db
```

### Example 3: Search Your Conversations
```powershell
python claude_kb_query.py --query "Power BI DAX measures" --limit 5
```

### Example 4: Export Analytics
```powershell
python claude_kb_analytics.py ^
  --dashboard ^
  --output "C:\Users\YourName\Documents\claude-analytics.html"
```

---

## 🎯 What This Project Does

### Core Features (v1.5.0)
1. **Export Fixer**: Makes Claude exports compatible with osteele's viewer
   - Fixes missing `created_at`, `model`, `index`, `model_slug` fields
   - Merges file references correctly
   - Filters unsupported content types

2. **Knowledge Base**: Searchable database of your conversations
   - Semantic chunking (NLTK)
   - Vector embeddings (sentence-transformers)
   - Full-text search (SQLite FTS5)
   - **Incremental updates** (87-90% time savings)

3. **Analytics Suite**: Insights into your conversations
   - Timeline analysis (daily/weekly/monthly)
   - Code extraction by language
   - Technology stack detection
   - Topic summaries
   - HTML dashboard generation

4. **GUI**: User-friendly interface
   - Drag-and-drop support
   - Progress indicators
   - "Open Output" button

---

## 📊 Performance

| Operation | Time (401 conversations) |
|-----------|--------------------------|
| Full export fix | ~5 seconds |
| Full KB build | ~10-12 seconds (batch optimized) |
| Incremental KB update | ~1-2 seconds (87-90% savings) |
| Semantic search | <1 second |
| Analytics dashboard | ~2-3 seconds |

---

## 🔗 Additional Resources

- **GitHub Repository**: https://github.com/racmac57/ClaudeExportFixer
- **osteele Viewer**: https://tools.osteele.com/claude-chat-viewer
- **CHANGELOG**: See `CHANGELOG.md` for version history
- **Knowledge Base Guide**: See `docs/KNOWLEDGE_BASE_GUIDE.md`

---

## 📞 Support

If you encounter issues:
1. Check `docs/` folder for guides
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Check Python version: `python --version` (needs 3.8+)

---

**Last Updated**: 2025-10-28  
**Current Version**: v1.5.0  
**Repository**: https://github.com/racmac57/ClaudeExportFixer

