# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-10-29

### Added - UNIFIED SYSTEM (MAJOR RELEASE) 🚀

**🎯 Goal**: Merge chunker_backup functionality into ClaudeExportFixer for a unified file processing system

This is a MAJOR architectural change that combines two separate projects into one unified system.

#### Unified Processing Architecture
- **Single watchdog service** - Handles Claude exports AND general file chunking
- **Intelligent routing** - Automatically detects file type and applies appropriate processing:
  - Claude exports (ZIP/JSON) → Schema fixing + Knowledge Base building
  - General files (TXT, MD, PY, XLSX, etc.) → Semantic chunking + Categorization
- **Organized output structure**:
  - `02_output/claude_exports/` - Fixed Claude exports
  - `02_output/chunks/` - Chunked files organized by category
  - `02_output/source/` - Flat source folder with all chunks (Grok's approach)
  - `04_archive/` - Organized archive by category

#### New Core Components
- **`chunker_engine.py`** - Extracted semantic chunking logic from watcher_splitter.py
  - NLTK sentence-aware splitting (150 sentences per chunk default)
  - Validates chunk content for quality
  - Waits for file stability before processing
  - Department-specific configuration support
  - Smart file categorization (chat_logs, scripts, data, documents)

- **`file_processors.py`** - Multi-format file handlers (copied from chunker)
  - Excel (`.xlsx`, `.xls`) - Enhanced with corruption handling
  - PDF (`.pdf`) - Text extraction with PyPDF2
  - Word (`.docx`) - Paragraph extraction
  - Python (`.py`) - AST-based code structure analysis
  - YAML/XML/SQL - Specialized processors
  - Automatic processor selection based on file type

- **`config.json`** - Unified configuration system
  - Merged settings from both projects
  - Claude export configuration
  - Chunking settings (size, overlap, organization)
  - File processing rules (13 supported extensions)
  - Performance tuning
  - Optional RAG integration settings

#### Enhanced start_watchdog.py (v2.0.0)
- **New class**: `UnifiedFileHandler` (replaces `ClaudeFileHandler`)
- **Intelligent filtering**: Implements Grok's corrected filter logic
  - Supported extensions from config
  - Exclude patterns (removed `_backup` per Grok's recommendation)
- **New methods**:
  - `should_process()` - Config-based file filtering
  - `process_and_chunk_file()` - Semantic chunking workflow
  - `simple_copy()` - Fallback for non-chunkable files
- **New CLI options**:
  - `--no-chunk` - Disable chunking (simple copy)
  - `--verbose` - Detailed logging with dependency checks
- **Automatic categorization**: Files organized into chat_logs, scripts, data, documents
- **Archive management**: Processed files moved to category-specific archive folders

#### File Processing Capabilities
Now supports **13 file formats** (up from 7):
- Text: `.txt`, `.md`, `.log`
- Code: `.py`, `.sql`, `.xml`
- Data: `.json`, `.csv`, `.xlsx`, `.xls`, `.yaml`, `.toml`
- Documents: `.pdf`, `.docx`
- Exports: `.zip` (Claude exports)

#### Output Organization (Grok's Simplified Approach)
```
02_output/
├── claude_exports/        # Fixed Claude export ZIPs
├── chunks/                # Organized by category
│   ├── chat_logs/
│   ├── scripts/
│   ├── data/
│   └── documents/
└── source/                # Flat folder for easy access
    ├── chat_logs/
    ├── scripts/
    ├── data/
    └── documents/

04_archive/                # Organized by category
├── claude_exports/
├── chat_logs/
├── scripts/
├── data/
└── documents/
```

#### Dependencies Added
- `openpyxl>=3.1.0` - Excel processing
- `PyPDF2>=3.0.0` - PDF processing
- `python-docx>=0.8.11` - Word processing
- `PyYAML>=6.0` - YAML processing

### Fixed
- **Issue 1**: Added `.xls` and `.toml` to supported extensions (Grok's recommendation)
- **Issue 2**: Removed `_backup` from exclude_patterns (was blocking valid files)
- **File stability**: Enhanced wait logic for faster small file processing

### Changed
- **Architecture**: Merged two separate projects into unified system
- **Version**: Bumped to 2.0.0 (breaking changes - new architecture)
- **Folder structure**: Added `04_archive/` for organized archival
- **Processing flow**: All files now wait for stability before processing
- **Configuration**: Centralized in `config.json` instead of hardcoded

### Deprecated
- Complex source_path tracking (Grok: "Over-engineering for current volume")
- Separate chunker watchdog (merged into `start_watchdog.py`)
- Hardcoded configuration (now in `config.json`)

### Implementation Notes
Based on Grok AI's analysis that identified:
- Over-engineering of source return tracking
- Value in unified system (single KB, shared processing)
- Benefit of organized but simple `source/` folder approach
- Files stuck due to missing extensions and overly restrictive filters

**Migration**: Existing ClaudeExportFixer functionality fully preserved - this is additive.

## [1.5.2] - 2025-10-28

### Enhanced - Multi-Format Support

**🎯 Goal**: Process various file types beyond Claude exports (ZIP/JSON)

#### Workflow Scripts Enhanced
- **`process_workflow.py`**: 
  - Added support for `.md`, `.xlsx`, `.csv`, `.py`, `.txt` file formats
  - Intelligent routing: Claude exports (ZIP/JSON) → `patch_conversations.py`, Other formats → direct copy
  - Preserves file extensions for non-export files
  - Fixed `-o` flag handling for proper output specification

- **`start_watchdog.py`**:
  - Extended file type detection to include `.md`, `.xlsx`, `.csv`, `.py`, `.txt`
  - Separate processing methods: `process_claude_export()` and `process_other_format()`
  - Smart output naming: Preserves extensions for non-export files
  - Updated help text to reflect supported formats

#### Processing Logic
- **Claude Exports** (`.zip`/`.json`): Full schema fixing with `patch_conversations.py`
- **Other Formats** (`.md`/`.xlsx`/`.csv`/`.py`/`.txt`): Direct copy with timestamp to `02_output/`
- **Output Naming**: 
  - Claude exports: `[name]-FIXED-[timestamp].zip`
  - Other formats: `[name]-PROCESSED-[timestamp].[ext]`

#### Documentation
- **Added**: `docs/SESSION_2025_10_28_SUMMARY.md` - Comprehensive session notes and decision points
- **Enhanced**: Supported formats messaging in watchdog startup

### Changed
- File extension validation expanded from 2 types to 7 types
- Processing workflow now branches based on file type
- Output file naming more flexible

## [1.5.1] - 2025-10-28

### Added - Watchdog Service (MAJOR FEATURE)

**🎯 Goal**: Provide true drag-and-drop automation - just drop files in `01_input/` and they process automatically

#### Watchdog Service (`start_watchdog.py`)
- **Automatic File Monitoring**: Monitors `01_input/` folder continuously using `watchdog` library
- **Drag-and-Drop Processing**: Files process automatically when dropped (ZIP/JSON only)
- **Background Operation**: Runs as daemon service with `--daemon` flag
- **Knowledge Base Integration**: Optional auto-build with `--build-kb` flag
- **Incremental Updates**: Uses `--incremental` for 87-90% faster KB updates
- **Thread-Safe Processing**: Handles multiple files simultaneously without conflicts
- **Real-Time Feedback**: Shows processing status, progress, and results
- **Verbose Mode**: `--verbose` flag for detailed output
- **Windows Integration**: `scripts/windows/start_watchdog.bat` for easy launching

#### Dependencies
- **Added**: `watchdog>=2.1.0` to `requirements.txt` for file system monitoring

#### Documentation
- **Enhanced**: `01_input/README.md` - Updated with watchdog service instructions
- **Enhanced**: `README.md` - Added watchdog service section with examples
- **Enhanced**: `SUMMARY.md` - Added watchdog service to core components

#### Workflow Enhancement
- **True Automation**: Drop files → Automatic processing → Output ready
- **No Manual Commands**: Eliminates need to run `process_workflow.py` manually
- **Continuous Operation**: Runs until stopped with Ctrl+C
- **Multiple Modes**: Basic monitoring, KB integration, daemon background

**Usage Examples:**
```bash
# Basic monitoring
python start_watchdog.py

# With knowledge base auto-build (recommended)
python start_watchdog.py --build-kb --incremental

# Background daemon mode
python start_watchdog.py --daemon --build-kb
```

## [1.5.0] - 2025-10-27

### Added - Incremental Updates (MAJOR FEATURE)

**🎯 Goal**: Reduce 60+ minute knowledge base updates to 5-10 minutes for typical monthly exports

#### Export Fixer (`patch_conversations.py` v1.5.0)
- **`--incremental` flag**: Process only new/modified conversations
- **`--previous FILE` argument**: Specify previous output for comparison
- **`--dry-run` flag**: Preview changes without processing
- **`--force-reprocess` flag**: Override incremental mode, force full rebuild
- **Change detection**: Timestamp-based with SHA256 content hash fallback
- **Progress reporting**: Shows new/modified/unchanged counts with time estimates
- **Time savings**: 80-90% faster for typical monthly updates (5-10 new conversations)
- **Smart merging**: Reuses processed conversations from previous export

#### Knowledge Base Builder (`claude_knowledge_base.py` v1.5.0)
- **`--incremental` flag**: Auto-detects existing database (default behavior if DB exists)
- **`--show-changes` flag**: Preview updates without modifying database
- **`--force-rebuild` flag**: Override incremental mode, rebuild from scratch
- **`--validate` flag**: Placeholder for future validation feature
- **Embedding reuse**: Preserves embeddings for unchanged conversations (CRITICAL optimization)
- **Processing manifest table**: Tracks conversation hashes, timestamps, chunk counts, embedding model
- **Automatic change detection**: Compares timestamps and content hashes
- **Model compatibility check**: Verifies embedding model hasn't changed
- **Schema versioning**: Tracks database schema version for migrations

#### Core Infrastructure (`incremental_utils.py`)
- **`compute_conversation_hash()`**: Deterministic SHA256 hash of conversation content
- **`detect_conversation_changes()`**: Categorizes conversations as new/modified/unchanged/deleted
- **`get_conversation_updated_at()`**: Extracts update timestamp with message fallback
- **`ChangeReport` dataclass**: Structured change summary with statistics
- **Time estimation**: Predicts processing time based on conversation count and embeddings
- **Clock skew handling**: Uses content hash when timestamps unreliable

### Changed
- **Default behavior preserved**: Full rebuild if `--incremental` not specified for export fixer
- **Knowledge base auto-incrementa**: Automatically uses incremental mode if database exists
- **Version bumped**: `patch_conversations.py` → v1.5.0, `claude_knowledge_base.py` → v1.5.0

### Performance
- **Incremental export fixer**: ~2s for 5 new conversations (vs ~10s full rebuild)
- **Incremental KB update**: ~5-10 minutes for 5-10 new conversations (vs 60+ minutes full)
- **Embedding reuse**: 95%+ for typical monthly updates (e.g., 394/401 conversations)
- **Time savings**: 85-90% reduction for incremental updates
- **Change detection**: <1 second for 400+ conversations

### Technical Details
- **Change detection strategy**:
  - Primary: Compare `updated_at` timestamps
  - Fallback: SHA256 content hash (handles clock skew, name-only changes)
- **Database strategy**:
  - DELETE old chunks/embeddings/messages for modified conversations
  - INSERT new data (re-generates embeddings only for changed conversations)
  - REUSE unchanged conversation data entirely
- **Content hashing**:
  - Includes: Message texts, timestamps, files/attachments
  - Excludes: Conversation name (can change without content change)
- **Compatibility checks**:
  - Embedding model version (e.g., `all-MiniLM-L6-v2`)
  - Database schema version (v1.5.0)
- **Error handling**:
  - Corrupted previous files
  - Clock skew (backward timestamps)
  - Model mismatches
  - Schema version conflicts

### New Files
- `incremental_utils.py`: Shared utilities for change detection and hashing
- `tests/test_incremental_updates.py`: Comprehensive test suite (14+ tests)

### Database Schema Changes
- **New table**: `processing_manifest`
  - Columns: `conversation_uuid`, `processed_at`, `updated_at`, `content_hash`,
    `message_count`, `chunk_count`, `embedding_model`, `embedding_dimensions`
  - Purpose: Track processed conversations for incremental updates
- **New table**: `schema_version`
  - Columns: `version`, `applied_at`
  - Purpose: Track schema version for migrations
- **New index**: `idx_manifest_updated` on `processing_manifest(updated_at)`

### Usage Examples

#### Export Fixer
```bash
# Full rebuild (current behavior, default)
python patch_conversations.py export.zip -o fixed.zip

# Incremental update (NEW)
python patch_conversations.py new_export.zip -o fixed.zip --incremental --previous fixed.zip

# Dry run (preview changes)
python patch_conversations.py new_export.zip --incremental --previous fixed.zip --dry-run

# Force reprocess everything
python patch_conversations.py export.zip -o fixed.zip --force-reprocess
```

#### Knowledge Base
```bash
# Initial build
python claude_knowledge_base.py export.zip my_kb.db

# Incremental update (auto-detects existing DB)
python claude_knowledge_base.py new_export.zip my_kb.db

# Preview changes without updating
python claude_knowledge_base.py new_export.zip my_kb.db --show-changes

# Force full rebuild
python claude_knowledge_base.py export.zip my_kb.db --force-rebuild
```

### Testing
- **Unit tests**: 14+ tests for hashing, change detection, clock skew handling
- **Test coverage**: Content hashing, timestamp comparison, UUID tracking
- **Test file**: `tests/test_incremental_updates.py`

### Future Enhancements (Not in v1.5.0)
- `--validate` mode: Compare incremental result against full rebuild
- Parallel processing for modified conversations (ThreadPoolExecutor)
- Automatic database backup before incremental updates
- Migration support for embedding model changes

### Breaking Changes
- None - fully backward compatible

### Known Limitations
- `--validate` flag not yet implemented (placeholder)
- No automatic migration for embedding model changes (requires `--force-rebuild`)
- Single-threaded processing (no parallelization yet)

## [1.4.0] - 2025-10-26

### Added - Analytics & Performance
- **NEW: `claude_kb_analytics.py`** - Advanced analytics module (500+ lines)
  - **Overview Statistics**: Comprehensive database metrics and insights
  - **Timeline Analysis**: Monthly/weekly/daily conversation trends with top topics
  - **Code Extraction**: Filter by language (Python, JavaScript, SQL, etc.), minimum lines
  - **Technology Stack Analysis**: Automatic detection of languages, databases, frameworks, tools
  - **Related Conversations**: Find similar conversations by tag overlap
  - **Topic Summaries**: Deep-dive into specific tags with stats and examples
  - **HTML Dashboard Generator**: Beautiful analytics dashboard with charts and stats
  - **CLI Interface**: All features accessible from command line with JSON output option

### Enhanced - Performance Optimization
- **`claude_knowledge_base.py` v1.2.0** - Batch processing optimizations
  - **Batch Inserts**: Use `executemany()` for chunks, search index, and files (~40% faster)
  - **Reduced Commits**: Commit per conversation instead of per message
  - **Removed Redundant Operations**: Eliminated old `process_file()` method
  - **Expected Performance**: ~10-12s for 401 conversations (down from ~17s)
  - **Memory Efficient**: Same memory footprint, better throughput

### Enhanced - Query Tool
- **`claude_kb_query.py`** - Added HTML export
  - Beautiful styled HTML output with syntax highlighting
  - Responsive design with modern UI
  - Color-coded scores and tags
  - Auto-format detection (.html extension)
  - Works in both CLI and interactive modes

### Technical Details
- **Analytics Features**:
  - Regular expressions for technology detection (30+ tech keywords)
  - Jaccard similarity for related conversations
  - Date-based filtering and aggregation
  - Sample message extraction for topic summaries
- **Performance Gains**:
  - Batch inserts reduce database roundtrips by 80%
  - Single commit per conversation vs per message = 90% fewer commits
  - Optimized JSON serialization (cache tags_json per message)

## [1.3.0] - 2025-10-26

### Added - Knowledge Base Enhancements
- **Vector Embeddings**: Added semantic search capability using sentence-transformers
  - Uses `all-MiniLM-L6-v2` model (384-dimensional embeddings)
  - Batch embedding generation for efficiency
  - Embeddings stored as JSON in SQLite for portability
  - Optional: Can disable embeddings if not needed (keyword search still works)
- **NEW: `claude_kb_query.py`** - Comprehensive query tool for knowledge bases
  - **Interactive Mode**: REPL-style interface with persistent state
  - **CLI Mode**: Single-command queries for scripting
  - **Three Search Modes**:
    - Keyword search (FTS5 full-text)
    - Semantic search (vector similarity)
    - Hybrid search (combined keyword + semantic with configurable weights)
  - **Filtering**: Tag-based and date range filters
  - **Context Viewer**: Show surrounding messages for search results
  - **Export**: Results to markdown, JSON, or CSV
  - **Statistics**: Database stats and search metrics

### Enhanced - Knowledge Base (`claude_knowledge_base.py`)
- **`ClaudeKnowledgeBase`**:
  - Added `use_embeddings` parameter (default: True)
  - Lazy loading of embedding model (only loads when needed)
  - Graceful degradation if sentence-transformers not installed
- **New Methods**:
  - `semantic_search()`: Vector-based semantic similarity search with cosine similarity
  - `hybrid_search()`: Combined keyword + semantic with configurable weighting
  - `_cosine_similarity()`: Efficient numpy-based similarity calculation
- **Performance**:
  - Batch embedding generation (encode multiple chunks at once)
  - Progress bars disabled for batch operations (less console spam)
  - Reuses embedding model across all chunks

### Changed
- Updated `requirements.txt`:
  - Added `sentence-transformers>=2.2.0` for vector embeddings
  - Added `numpy>=1.24.0` for similarity calculations
- Updated `claude_knowledge_base.py` version to 1.1.0

### Technical Details
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions, 23M parameters)
  - Fast: ~2800 sentences/second on CPU
  - High quality: 80%+ accuracy on semantic similarity tasks
  - Compact: 90MB model size
- **Storage**: Embeddings stored as JSON arrays in TEXT column (SQLite compatible)
- **Similarity**: Cosine similarity with numpy (normalized dot product)
- **Hybrid Scoring**: Weighted combination with rank-based normalization for FTS5

## [1.2.2] - 2025-10-26

### Fixed - Validation Failures Resolved
- **CRITICAL**: Fixed validation failures caused by unsupported content types
  - Added `filter_content_items()` function to remove unsupported content types from message content arrays
  - Viewer only supports: `text`, `thinking`, `voice_note`, `tool_use`, `tool_result`
  - Filters out: `token_budget` and any other unsupported types
  - Root cause: Claude exports contain `token_budget` content items that the osteele viewer schema (chat.ts) doesn't recognize
  - Result: All 401 conversations should now pass viewer validation

### Added
- `diagnose_validation.py` - Schema validation diagnostic tool
  - Checks conversations against osteele viewer schema requirements
  - Reports specific field/type validation errors
  - Identifies conversations with issues
  - Used to identify the `token_budget` root cause

### Changed
- Enhanced `process_conversation_data()` to filter content arrays
  - Automatically removes unsupported content types before viewer validation
  - Logs filtered types at DEBUG level
  - Preserves all supported content items

### Technical Details
- Analysis of osteele viewer's Zod schema (chat.ts lines 61-92) revealed ContentItemSchema union type
- Only 5 content types supported by viewer's validation
- Claude exports include additional metadata types (token_budget) for internal tracking
- These metadata types must be filtered out for viewer compatibility

## [1.2.1] - 2025-10-27

### Improved - QA Polish
- **Logging**: Enhanced `setup_logging()` to prevent duplicate handlers with `force=True`
  - Better timestamp format: `%Y-%m-%d %H:%M:%S`
  - Clearer log format with timestamps
- **GUI**: Improved `open_output()` with better error handling and logging
  - Platform-specific opening (Windows/macOS/Linux)
  - Enhanced logging for debugging
  - Better error messages
- **GUI**: Enhanced headless safety with clearer error message
- **CLI**: Added `--version` flag to show version information
- **Tests**: Fixed platform mocking in `test_gui_open_output.py`
- **Tests**: Improved logging capture in `test_print_logging_bridge.py`
- **README**: Enhanced GUI Mode and Building Executables documentation
  - Added headless environment explanation
  - Documented "Open Output" button functionality
  - Added `--windowed` flag tips and caveats

### Dependencies
- Added `nltk>=3.8` to `requirements.txt` (for knowledge base chunking)

## [1.2.0] - 2025-10-27

### Added - Knowledge Base System
- **NEW: `claude_knowledge_base.py`** - Convert Claude exports to searchable SQLite database
  - Semantic chunking with NLTK sentence tokenization (150 words max)
  - Automatic tag extraction (tech keywords, date-based, content analysis)
  - Full-text search with FTS5
  - Files/attachments indexing with extracted content
  - Conversation, message, chunk, and file tracking
  - Statistics and analytics support
- **NEW: `GROK_KNOWLEDGE_BASE_PROMPT.md`** - Collaboration prompt for Grok AI assistance
  - Vector embeddings integration guidance
  - Query interface specifications
  - Analytics feature requests
  - Integration with C:\_chunker project

### Added - Schema Compliance (osteele viewer)
- **CRITICAL**: Added `content` array to all messages (required by osteele viewer)
  - Schema analysis from github.com/osteele/claude-chat-viewer/src/schemas/chat.ts
  - Content array wraps message text: `[{"type": "text", "text": "..."}]`
  - Fixes validation errors: "Message content is required"
- Added `model` field to all conversations (defaults to `claude-sonnet-3-5-20241022`)
- Added `index` field to all messages (message sequence number)
- Added `model_slug` field to all messages (which Claude model was used)

### Changed
- Enhanced `process_conversation_data()` to add missing schema fields
  - Automatically adds `model`, `index`, `model_slug`, and `content` if missing
  - Ensures 100% compliance with osteele viewer schema requirements

### Verified
- Downloaded osteele viewer source code to `claude-chat-viewer-main/`
- Analyzed Zod schema requirements in `src/schemas/chat.ts`
- All 401 conversations now have required fields:
  - 100% have `model` field
  - 100% of messages have `index` field
  - 100% of messages have `model_slug` field
  - 100% of messages have `content` array

## [1.1.2] - 2025-10-27

### Fixed
- **CRITICAL**: Added `created_at` timestamp to file objects (required by osteele viewer)
  - File objects now inherit `created_at` from parent message
  - Viewer requires this field to validate and display conversations correctly
  - Fixes validation errors: "At 'chat_messages.X.files.Y.created_at': Required"
  - 100% of file objects now have timestamps

### Changed
- Enhanced `merge_file_references()` to accept `message_timestamp` parameter
- Updated `process_conversation_data()` to pass message timestamps to file merging

### Verified
- Real-world test: 401 conversations, 10,369 messages, 2,830 file objects
- All file objects now have `created_at` field (100%)
- osteele viewer validation: All conversations should now load successfully

## [1.1.1] - 2025-10-27

### Fixed
- **CRITICAL**: Enhanced `merge_file_references()` to properly handle Claude's rich attachment format
  - Now supports objects with `file_name`, `file_size`, `file_type`, `extracted_content` fields
  - Deduplicates by file identifier (file_name, uuid, or file_uuid)
  - Prioritizes richer attachment data over simpler file data when merging
  - Maps `file_name` and `uuid` to `file_uuid` for osteele viewer compatibility
  - Filters out empty file names
  - Maintains backward compatibility with simple UUID format
- **CRITICAL**: Fixed `process_conversation_data()` to handle Claude's list format (conversations as top-level array)
  - Now supports both `{"conversations": [...]}` and `[...]` formats
  - Ensures merge_file_references() is called for all Claude export formats
- **CRITICAL**: Fixed `link_projects()` to handle list format conversations

### Added
- `tests/test_merge_rich_attachments.py` - Comprehensive test suite for rich attachment merging (10 tests)
  - Tests backward compatibility with UUID format
  - Tests Claude's rich attachment format
  - Tests deduplication by file_name
  - Tests empty file_name handling
  - Tests mixed format support
  - Tests extracted_content preservation
- `LICENSE` - MIT License for open-source distribution
- `.gitattributes` - Line ending enforcement (LF default, CRLF for .bat files)
- `SECURITY.md` - Security policy and vulnerability reporting guidelines
- `utils/` folder - Analysis and troubleshooting utilities
  - `PROMPT_FOR_GROK.md` - Troubleshooting documentation
  - `GROK_TROUBLESHOOTING_REPORT.md` - Detailed issue analysis
  - `current_merge_function.py` - Code reference with test scenarios
  - `claude_export_sample_structure.json` - Sample Claude export format
  - `analyze_output.py` - Output validation tool
  - `check_merging.py` - Attachment merging verification tool
  - `detailed_analysis.py` - Detailed statistics analysis tool
  - `verify_fix.py` - Fix verification tool
  - `verify_rich_data.py` - Rich data preservation verification tool

### Changed
- `README.md` - Added License, Contributing sections, and utils/ folder documentation
- `SUMMARY.md` - Updated status and added utils/ folder
- Git repository initialized and configured
- Version bumped to 1.1.1

### Tested
- ✅ 23/23 tests passing (13 original + 10 new rich attachment tests)
- ✅ Successfully processed real Claude export with 401 conversations, 10,369 messages
- ✅ 0 messages with both files and attachments (100% merge success rate)
- ✅ Rich attachment data preserved (extracted_content, file_size, file_type)

## [1.1.0] - 2025-10-26

### Added
- Optional Tkinter GUI interface in `gui.py`
  - Browse input/output files with file dialogs
  - Visual checkboxes for all CLI options
  - Real-time log streaming in text area
  - Progress bar during processing
  - Auto-detection of projects.json
  - "Open Output" button to view results
  - Background threading for responsive UI
  - Headless safety with graceful error handling
- `--gui` flag in CLI to launch graphical interface
- GUI test suite:
  - `tests/test_gui_import.py` - GUI module import tests
  - `tests/test_gui_utils.py` - GUI helper function tests (`_suggest_output_path`)
  - `tests/test_gui_open_output.py` - GUI open output functionality tests (5 tests: Windows, macOS/Linux, error handling, edge cases)
  - `tests/test_print_logging_bridge.py` - Logging completeness tests
- Windows batch scripts:
  - `run_gui.bat` - Launch GUI directly
  - `build_exe_gui.bat` - Build windowed executable
- PyInstaller instructions in README for both CLI and GUI builds
- `*.log` pattern to .gitignore
- Comprehensive project structure documentation in README

### Changed
- Version bumped to 1.1.0
- README.md reorganized with GUI Mode, Building Executables, and Project Structure sections
- CLI `input` argument now optional (required only if not using --gui)
- CLI `-o/--output` argument now optional (required only if not using --gui)

## [1.0.0] - 2025-10-26

### Added
- Full implementation of patch_conversations.py
- Support for JSON and ZIP file processing
- File/attachment reference merging
- Project linking from projects.json
- ZIP metadata preservation
- Streaming support with ijson (optional)
- Comprehensive CLI with argparse
- CSV report generation
- Backup creation for ZIP files
- Typed Python code with type hints
- Multiple processing modes (streaming, strict, verbose, quiet)
- Auto-detection of projects.json
- Initial project structure
- README.md with quick start guide
- .gitignore for Python projects
- requirements.txt with ijson and pytest dependencies
- requirements-build.txt for build-specific dependencies (pyinstaller)
- Sample JSON files (conversations.example.json, projects.example.json)
- Smoke tests in tests/test_smoke.py
- Windows batch scripts for setup and execution
  - create_venv.bat - Virtual environment setup
  - run_tests.bat - Test runner
  - run_example_json.bat - JSON processing example
  - run_example_zip_stream.bat - ZIP streaming example
  - build_exe.bat - PyInstaller build script
- CHANGELOG.md for tracking project changes
- SUMMARY.md for project overview
- GitHub integration:
  - .github/workflows/ci.yml - Continuous integration workflow
  - .github/workflows/release.yml - Release automation workflow
  - .github/ISSUE_TEMPLATE/bug_report.yml - Bug report template
  - .github/ISSUE_TEMPLATE/feature_request.yml - Feature request template
  - .github/PULL_REQUEST_TEMPLATE.md - Pull request template
  - .github/CONTRIBUTING.md - Contributing guidelines

## [0.1.0] - 2025-10-26

### Added
- Initial project scaffold created

