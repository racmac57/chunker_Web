# Project Summary

## ClaudeExportFixer v2.0.0 - UNIFIED SYSTEM

### Purpose
**Unified file processing system:** Fix, validate, search, and build knowledge bases from Claude.ai chat history PLUS intelligent semantic chunking for ANY file type. Merged functionality from two projects into one powerful system. Ensures full compatibility with the osteele chat viewer while providing advanced analytics, semantic search, HTML dashboards, **incremental updates** (87-90% time savings), **automatic file monitoring**, **intelligent chunking** (NLTK sentence-aware), and **smart categorization** for daily Power BI, Python, and ArcGIS workflows.

### Core Components

#### 1. Export Fixer (`patch_conversations.py`)
Normalizes Claude exports for osteele viewer compatibility:
- **Schema Compliance**: Adds all required fields (`content`, `model`, `index`, `model_slug`)
- **Rich Attachments**: Merges and preserves file metadata with `extracted_content`
- **Format Support**: Handles both list and dict conversation formats
- **ZIP Processing**: Streaming support for large exports with `ijson`
- **GUI Mode**: Optional Tkinter interface (`--gui` flag)

#### 2. Knowledge Base Builder (`claude_knowledge_base.py`)
Converts exports to searchable SQLite database:
- **Semantic Chunking**: NLTK sentence-aware chunking (150 words max)
- **Vector Embeddings**: 384D semantic search (sentence-transformers)
- **Auto-Tagging**: Tech keywords, date-based, content-type tags
- **Full-Text Search**: FTS5 indexing across all conversations
- **File Indexing**: Attachment `extracted_content` searchable
- **40% Performance Boost**: Batch processing optimizations (v1.2.0)

#### 3. Query Tool (`claude_kb_query.py`)
Interactive and CLI search interface:
- **Three Search Modes**: Keyword (FTS5), Semantic (vector), Hybrid (combined)
- **Tag & Date Filters**: Refine searches by metadata
- **Context Viewer**: Show surrounding messages
- **Export Formats**: Markdown, JSON, CSV, HTML
- **Beautiful HTML**: Syntax highlighting, responsive design

#### 4. Analytics Suite (`claude_kb_analytics.py`) **NEW!**
Advanced analytics and insights:
- **Overview Statistics**: Database metrics, conversation counts
- **Timeline Analysis**: Monthly/weekly/daily trends with top topics
- **Code Extraction**: Filter by language, minimum line counts
- **Tech Stack Analysis**: Auto-detect 30+ technologies
- **Related Conversations**: Tag-based similarity recommendations
- **HTML Dashboards**: Beautiful analytics reports with charts

#### 5. Unified Watchdog Service (`start_watchdog.py`) **v2.0.0 - MAJOR UPGRADE!**
Automatic file monitoring and processing with intelligent routing:
- **Continuous Monitoring**: Watches `01_input/` folder for new files
- **13 File Formats**: `.zip`, `.json`, `.md`, `.xlsx`, `.xls`, `.csv`, `.py`, `.txt`, `.pdf`, `.docx`, `.sql`, `.yaml`, `.toml`, `.xml`, `.log`
- **Intelligent Routing**: 
  - Claude exports (`.zip`/`.json`) → Schema fixing + Knowledge base
  - General files → Semantic chunking + Categorization
- **Smart Categorization**: Automatically organizes into chat_logs, scripts, data, documents
- **Organized Output**: Structured folders with easy access
- **Background Operation**: Runs as daemon service
- **Knowledge Base Integration**: Optional auto-build with incremental updates
- **Thread-Safe**: Handles multiple files simultaneously
- **Real-Time Feedback**: Shows processing status and results

#### 6. Chunking Engine (`chunker_engine.py`) **NEW in v2.0.0!**
Semantic chunking for any file type:
- **NLTK Tokenization**: Sentence-aware splitting
- **Configurable Chunks**: 150 sentences/30K chars default
- **Content Validation**: Quality checks for meaningful chunks
- **File Stability**: Waits for complete writes
- **Performance**: Processes 4 files → 90 chunks in ~2 seconds

#### 7. File Processors (`file_processors.py`) **NEW in v2.0.0!**
Multi-format file handlers:
- **Excel**: `.xlsx`, `.xls` with corruption handling
- **PDF**: Text extraction with PyPDF2
- **Word**: `.docx` paragraph extraction
- **Python**: `.py` AST-based code analysis
- **Structured**: YAML, XML, SQL parsers
- **Factory Pattern**: Automatic processor selection

### Technology Stack
- **Language**: Python 3.13+
- **Core Dependencies**:
  - `ijson` (≥3.2) - Streaming JSON parser
  - `pytest` (≥8.4) - Testing framework
  - `nltk` (≥3.8) - Sentence tokenization for chunking
  - `sentence-transformers` (≥2.2.0) - Vector embeddings for semantic search
  - `numpy` (≥1.24.0) - Similarity calculations
  - `watchdog` (≥2.1.0) - File system monitoring for automatic processing
- **Optional**:
  - `pyinstaller` (≥6.0) - Build executables

### Key Features

#### Export Processing
- ✅ Full osteele viewer schema compliance (analyzed from viewer source code)
- ✅ Rich attachment handling with metadata preservation
- ✅ Both top-level list `[...]` and dict `{"conversations": [...]}` formats
- ✅ Streaming mode for 1000+ conversation exports
- ✅ Projects.json linking support
- ✅ Pretty-printed JSON output

#### Knowledge Base
- 🔍 Semantic text chunking (sentence-aware, configurable size)
- 🤖 Vector embeddings with sentence-transformers (384D all-MiniLM-L6-v2)
- 🏷️ Automatic tag extraction (30+ tech keywords, date tags, content analysis)
- 📊 Full-text search with SQLite FTS5
- 📁 File/attachment content indexing
- ⚡ 40% performance boost with batch processing
- 🎯 Integration with C:\_chunker enterprise chunking logic

#### Analytics
- 📈 Timeline analysis (monthly/weekly/daily trends)
- 💻 Code extraction by language (Python, SQL, JavaScript, etc.)
- 🔧 Technology stack analysis (30+ detected technologies)
- 🔗 Related conversation finder (tag-based similarity)
- 📊 Topic deep-dive with sample messages
- 🎨 HTML dashboard generator (beautiful charts & stats)

#### GUI & Automation
- 🖥️ Optional Tkinter GUI (stdlib only, no deps)
- 🐕 **Watchdog Service** - Automatic file monitoring and processing
- ⚡ Windows batch scripts for all common tasks
- 🏗️ PyInstaller support for standalone .exe builds
- 🔔 Real-time processing logs

### Project Structure
```
ClaudeExportFixer/ (v1.5.1)
├── Core Scripts
│   ├── patch_conversations.py (650 lines) - Main export fixer
│   ├── start_watchdog.py (200+ lines) - 🆕 Automatic file monitoring
│   ├── claude_knowledge_base.py (460 lines) - KB builder (v1.2.0)
│   ├── claude_kb_query.py (580 lines) - Query tool with HTML export
│   ├── claude_kb_analytics.py (500+ lines) - Analytics suite
│   └── gui.py (620 lines) - Optional Tkinter interface
│
├── Tests (24 passing ✅)
│   ├── test_merge_rich_attachments.py (11 tests) - Rich attachment validation
│   ├── test_smoke.py - Basic functionality
│   ├── test_gui_*.py (4 files) - GUI component tests
│   └── test_print_logging_bridge.py - Logging validation
│
├── Utils (20+ tools 🔍)
│   ├── comprehensive_verification.py - Complete validation
│   ├── verify_v120_fix.py - v1.2.0 field verification
│   ├── check_common_schema_issues.py - Schema validation
│   ├── strict_validator.py - osteele schema enforcement
│   └── (16+ more analysis scripts)
│
├── Documentation (Complete 📚)
│   ├── README.md (250 lines) - User guide
│   ├── CHANGELOG.md (150 lines) - Version history
│   ├── SUMMARY.md (this file)
│   ├── LICENSE - MIT
│   ├── SECURITY.md - Vulnerability reporting
│   └── .gitattributes - Line ending config
│
├── GitHub Integration
│   ├── workflows/ (ci.yml, release.yml)
│   ├── ISSUE_TEMPLATE/ (bug_report, feature_request)
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CONTRIBUTING.md
│
└── Sample Data
    ├── conversations.example.json
    └── projects.example.json
```

### Getting Started

**Quick Setup (Windows):**
```bat
cd C:\Dev\ClaudeExportFixer
scripts\windows\create_venv.bat
```

**Fix Export:**
```bat
python patch_conversations.py export.zip -o fixed.zip --zip-output --pretty
```

**Build Knowledge Base:**
```bat
python claude_knowledge_base.py export.zip my_kb.db
```

**Query Conversations:**
```bat
python claude_kb_query.py my_kb.db "power bi dax" --export results.html
```

**Generate Analytics:**
```bat
python claude_kb_analytics.py my_kb.db --dashboard analytics.html
```

**Run GUI:**
```bat
python patch_conversations.py --gui
```

### Current Status
- **Version**: 1.5.1 (Released 2025-10-28)
- **Status**: Production-ready with incremental updates and automatic file monitoring
- **Tests**: 38/38 passing ✅ (14 new incremental tests)
- **License**: MIT
- **Real-World Validation**: 
  - ✅ Tested on 401 conversations, 10,369 messages
  - ✅ 100% schema compliance (all required fields)
  - ✅ Rich metadata preserved (2,830 files with file_uuid + file_name)
  - ✅ **Incremental updates**: 5-10 min (vs 60+ min) for typical monthly exports
  - ✅ **Embedding reuse**: 95%+ for unchanged conversations
  - ✅ Vector embeddings: 384D all-MiniLM-L6-v2 semantic search
  - ✅ Analytics: 8 major features, HTML dashboards, code extraction

### Recent Changes (v1.5.1)

#### Added - Watchdog Service (MAJOR FEATURE)
- **Automatic File Monitoring**: `start_watchdog.py` monitors `01_input/` folder continuously
- **Drag-and-Drop Processing**: Files process automatically when dropped
- **Background Operation**: Runs as daemon service with `--daemon` flag
- **Knowledge Base Integration**: Optional auto-build with `--build-kb` flag
- **Incremental Updates**: Uses `--incremental` for 87-90% faster KB updates
- **Thread-Safe Processing**: Handles multiple files simultaneously
- **Real-Time Feedback**: Shows processing status and results
- **Windows Integration**: `scripts/windows/start_watchdog.bat` for easy launching
- **Dependency**: Added `watchdog>=2.1.0` to requirements.txt

#### Previous Changes (v1.5.0)

#### Added - Incremental Updates (MAJOR FEATURE)
- **Export Fixer Incremental Mode**: 80-90% time savings
  - `--incremental --previous FILE` flags
  - Change detection (timestamps + SHA256 hashing)
  - `--dry-run` for previewing changes
  - Smart merging of new/modified conversations
  
- **Knowledge Base Incremental Mode**: 87-90% time savings (5-10 min vs 60+ min)
  - **Embedding reuse** for unchanged conversations (95%+ reuse rate)
  - Auto-detects existing database
  - `processing_manifest` table tracks hashes, timestamps, model versions
  - `--show-changes` for dry run, `--force-rebuild` for full rebuild
  
- **Incremental Utils Module** (`incremental_utils.py`):
  - Content hashing with SHA256
  - Change detection (new/modified/unchanged/deleted)
  - Time estimation and progress reporting
  - Clock skew handling
  - 14+ utility tests

#### Previous Features (v1.4.0)
- **Analytics Suite**: 8 major features with HTML dashboards
- **Performance**: 40% faster KB builds with batch processing
- **HTML Export**: Beautiful styled output

#### Enhanced (v1.3.0)
- **Vector Embeddings**: Semantic search with sentence-transformers
- **Query Tool**: Interactive REPL with keyword/semantic/hybrid search
- **Export Formats**: Markdown, JSON, CSV, HTML

#### Previous Critical Fixes
- **Content Type Filtering**: Removed unsupported `token_budget` items (v1.2.2)
- **Schema Compliance**: All osteele viewer required fields (v1.2.0)
- **File Timestamps**: `created_at` on all file objects (v1.1.2)
- **Rich Attachments**: Metadata preservation with deduplication (v1.1.1)

### Known Limitations
- **osteele Viewer**: Some conversations may fail validation
  - All required schema fields present (100% compliance)
  - Most common issues now resolved (content filtering, file schema)
  - Remaining issues may be conversation-specific edge cases
- **Embedding Generation**: CPU-intensive (~20 min for 401 conversations)
  - Future: Optional GPU acceleration with CUDA/MPS
- **Analytics**: Currently CLI-only (no web dashboard yet)

### Roadmap

#### v1.5.0 (Future)
- [ ] GPU-accelerated embedding generation
- [ ] Web-based analytics dashboard (Flask/FastAPI)
- [ ] Conversation clustering with k-means
- [ ] Topic modeling with LDA/NMF
- [ ] Export to Power BI dataset format

#### v2.0.0 (Vision)
- [ ] Multi-user knowledge base (team collaboration)
- [ ] Real-time sync with Claude.ai
- [ ] Custom embedding models (domain-specific)
- [ ] Advanced visualizations (D3.js, Plotly)

### Maintainer Notes
- **CHANGELOG.md**: Update for every version with [Keep a Changelog](https://keepachangelog.com/) format
- **Tests**: Run `pytest -q` before committing (must be 100% passing)
- **Line Endings**: `.bat` files require CRLF (enforced by `.gitattributes`)
- **Dependencies**: Keep `requirements.txt` minimal (only runtime deps)
- **Utils**: All analysis tools go in `utils/` with clear naming
- **Grok Collaboration**: See `GROK_KNOWLEDGE_BASE_PROMPT.md` for AI enhancement guide
- **Security**: Report issues via SECURITY.md guidelines

### Integration Notes
- **C:\_chunker Project**: Knowledge base leverages enterprise chunking patterns
  - NLTK sentence tokenization
  - SQLite tracking database design
  - Parallel processing patterns (not yet implemented)
  - Tag extraction logic
- **osteele Viewer**: Source code at `claude-chat-viewer-main/` for schema reference
- **Real Data**: Sample 401-conversation export in OneDrive for testing

### Useful Commands
```bat
# Create virtual environment
scripts\windows\create_venv.bat

# Run all tests
scripts\windows\run_tests.bat

# Fix export for viewer
python patch_conversations.py export.zip -o fixed.zip --zip-output --pretty

# Build knowledge base
python claude_knowledge_base.py export.zip my_kb.db

# Query conversations
python claude_kb_query.py my_kb.db

# Generate analytics dashboard
python claude_kb_analytics.py my_kb.db --dashboard report.html

# Launch GUI
scripts\windows\run_gui.bat

# Build executables
scripts\windows\build_exe.bat        # CLI only
scripts\windows\build_exe_gui.bat    # GUI (no console)

# Verify v1.2.0 compliance
python utils\verify_v120_fix.py

# Run strict validation
python utils\strict_validator.py conversations.json
```

### Support & Contribution
- **Issues**: [GitHub Issues](https://github.com/racmac57/ClaudeExportFixer/issues)
- **Contributing**: See `.github/CONTRIBUTING.md`
- **Security**: See `SECURITY.md` for vulnerability reporting
- **License**: MIT (see `LICENSE`)

---

**Last Updated**: 2025-10-28 (v1.5.1)
