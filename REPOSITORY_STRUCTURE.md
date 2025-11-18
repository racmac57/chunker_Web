# Chunker_Web Repository - Comprehensive Overview

## Current Date
November 18, 2025

## Repository Status
- **Git Branch**: claude/add-chunking-tagging-019PWmdzbLnESaP1pqs3gcmb
- **Status**: Clean (no uncommitted changes)
- **Recent Commits**: 
  - 7782faf chore: protection smoke test (#9)
  - d20adcf ci: fix header and enable workflow_dispatch (#8)

---

## 1. DIRECTORY STRUCTURE

```
/home/user/chunker_Web/
├── 01_scripts/                          # Legacy/initialization scripts
│   └── new_chunker_project/
├── 02_data/                             # INPUT: Watch folder for files to process
├── 03_archive/                          # Archived original files post-processing
│   ├── legacy/
│   ├── failed/                          # Files that failed processing
│   ├── skipped_files/                   # Files too small (<100 bytes)
│   └── backups/
├── 04_output/                           # Generated chunks and metadata
├── 05_logs/                             # Application and maintenance logs
├── 06_config/                           # Configuration files
├── 99_doc/                              # Documentation and archives
├── archive/                             # Old/deprecated scripts
├── chroma_db/                           # ChromaDB vector database storage
├── claude_gui_package/                  # GUI components
├── docs/                                # Release and operational docs
├── grok_review_package/                 # Review/reference materials
├── scripts/                             # PowerShell/batch scripts for operations
├── source/                              # Pre-chunked text files (1000+ items)
├── static/                              # Web assets
├── templates/                           # HTML templates
├── tests/                               # Pytest test suites
├── tools/                               # Utility scripts
├── .claude/                             # Claude Code specific configs
├── .github/workflows/                   # CI/CD workflows
├── .gitignore                           # Git ignore rules
├── config.json                          # Main configuration file
├── package.json                         # Node.js package metadata
├── requirements.txt                     # Core Python dependencies
├── requirements_rag.txt                 # RAG/vector DB dependencies
├── requirements_api_gui.txt             # FastAPI/Streamlit dependencies
└── pytest.ini                           # Pytest configuration
```

---

## 2. PROJECT STATISTICS

### File Counts
- **Total Python files**: 99
- **Total config/code/doc files**: 1,871
- **Total project files**: 1,900+

### Largest Python Modules (by LOC)
1. **watcher_splitter.py** (1,816 lines) - Main file watcher & chunker
2. **celery_tasks.py** (1,291 lines) - Celery async task queue integration
3. **backfill_knowledge_base.py** (1,253 lines) - RAG knowledge base loading
4. **chunker_cleanup.py** (897 lines) - Deduplication & cleanup utilities
5. **rag_integration.py** (865 lines) - RAG search & embedding integration
6. **enhanced_watchdog.py** (793 lines) - Advanced file system watching
7. **file_processors.py** (664 lines) - Multi-format file parsing
8. **comprehensive_eval.py** (649 lines) - RAG evaluation metrics
9. **gui_app.py** (630 lines) - Streamlit web GUI
10. **chromadb_crud.py** (610 lines) - Vector database CRUD operations

---

## 3. CORE DEPENDENCIES

### Main Requirements (requirements.txt)
```
pytest>=7.0.0
psutil>=5.9.0
```

### RAG & Vector Database (requirements_rag.txt)
- **Text Processing**: nltk 3.9.1+, pandas 2.2.3+, scikit-learn 1.7.2+
- **Embeddings**: sentence-transformers 3.1.1+, ollama 0.3.3+
- **Vector Stores**: faiss-cpu 1.8.0+, langchain 0.3.1+, langsmith 0.1.129+
- **File Parsing**: openpyxl 3.1.5+, pypdf2 3.0.1+, python-docx 1.2.0+, pyyaml 6.0.2+, lxml 4.9.0+
- **Evaluation**: rouge-score 0.1.2+, bert-score 0.3.13+
- **Monitoring**: watchdog 3.0.0+, schedule 1.2.0+
- **Optional**: pdfminer.six, pymupdf

### API & GUI (requirements_api_gui.txt)
- **Framework**: fastapi 0.104.0+, uvicorn 0.24.0+, streamlit 1.28.0+
- **Security**: python-jose, passlib with bcrypt
- **Utilities**: pydantic 2.5.0+, python-multipart 0.0.6+

---

## 4. CONFIGURATION SYSTEM

### Main Config File (config.json)
**Location**: `/home/user/chunker_Web/config.json`

#### Core Chunking Settings
| Setting | Default | Purpose |
|---------|---------|---------|
| watch_folder | %OneDriveCommercial%\KB_Shared\02_data | Input directory |
| output_dir | %OneDriveCommercial%\KB_Shared\04_output | Output chunks |
| archive_dir | %OneDriveCommercial%\KB_Shared\03_archive | Archive processed files |
| chunk_size | 800 | Sentences per chunk |
| overlap | 50 | Sentence overlap between chunks |
| min_chunk_size | 100 | Minimum characters per chunk |
| max_chunk_size | 1500 | Maximum characters per chunk |
| supported_extensions | [.txt, .md, .csv, .json, .py, .m, .dax, .ps1, .sql] | File types to process |

#### Feature Toggles
- **rag_enabled**: true (Retrieval-Augmented Generation)
- **database_enabled**: true (SQLite tracking)
- **metadata_enrichment**: enabled, max_key_terms=6
- **deduplication**: enabled, auto_remove=false
- **celery_enabled**: false (Async task queue)
- **enable_json_sidecar**: true (Metadata sidecar files)
- **enable_block_summary**: true (Python block extraction)

#### Parallel Processing
- **parallel_workers**: 8
- **enable_parallel_processing**: true
- **batch_size**: 50
- **database_batch_size**: 10
- **backfill_batch_size**: 750
- **backfill_multiprocessing**: true

#### Monitoring & Backups
- **monitoring.enabled**: true
- **backup.enabled**: true
- **backup.keep_backups**: 7
- **query_cache.enabled**: true
- **query_cache.ttl_seconds**: 600

---

## 5. EXISTING CHUNKING & TEXT PROCESSING CODE

### Main Chunking Algorithm (watcher_splitter.py:578-635)

**Function**: `chunk_text_enhanced(text, limit, department_config)`

**Algorithm**:
1. Tokenizes text into sentences using NLTK (with LRU caching)
2. Applies department-specific redaction rules (SSN, phone, address, email)
3. Accumulates sentences into chunks respecting:
   - Sentence count limit (department-specific)
   - Character limit: `max_chunk_chars` (default 30,000)
   - Minimum chunk size: 100 characters
4. Validates chunk content (min 50 chars, 10+ words, 70%+ content ratio)
5. Returns list of validated chunks

**Key Features**:
- Sentence-based chunking (semantic units)
- Department-specific configurations (police/legal/admin)
- Automatic sensitive data redaction
- Chunk validation with configurable thresholds
- LRU-cached tokenization for performance
- Session statistics tracking

### File Processors (file_processors.py:40-60)

**Function**: `read_file_with_fallback(file_path) -> Tuple[str, str]`

**Approach**:
1. Attempts UTF-8, UTF-16, Latin-1, CP1252 encodings in sequence
2. Falls back to binary read with error replacement on all failures
3. Returns (content, encoding_used) tuple
4. Handles OS-level errors gracefully (locked files, missing files)

**Supported Formats**:
- Plain text (.txt, .md)
- Code files (.py, .sql, .ps1, .dax, .m)
- Structured data (.csv, .json)
- Office documents (Excel, Word, PDF - optional)
- YAML configuration files

### Chunk Output Writers (watcher_splitter.py:388-450)

**Function**: `write_chunk_files(doc_id, chunks, out_root) -> List[str]`

**Output Structure**:
```
04_output/{source_basename}/
├── {basename}_chunk_001.txt
├── {basename}_chunk_002.txt
├── ...
├── {basename}.manifest.json       # Metadata sidecar
├── {basename}.transcript.txt      # Concatenated chunks
└── {basename}.summary.txt         # Auto-generated summary (optional)
```

### Metadata Enrichment (metadata_enrichment.py)

**Features**:
- Key term extraction (up to 6 per chunk)
- Python block parsing (classes, functions, docstrings)
- Origin tracking with `.origin.json` files
- Chunk tagging and categorization
- JSON sidecar generation with comprehensive metadata

### Deduplication (deduplication.py)

**Strategy**:
- SHA-256 content hashing
- Configurable normalization (lowercase, whitespace collapsing)
- Hash registry in vector DB (ChromaDB with hnswlib)
- Optional auto-removal of duplicates
- Batch processing for efficiency

### Vector Database Integration (chromadb_crud.py)

**Operations**:
- **Create**: Add chunks with embeddings and metadata
- **Read**: Retrieve chunks by ID or semantic search
- **Update**: Modify chunk text or metadata
- **Delete**: Remove chunks from knowledge base
- **Batch Operations**: Bulk insert/delete with configurable sizes
- **Cleanup**: Remove old chunks (>30 days)

**Vector Index Configuration**:
- Default `ef_search`: 64 (configurable from config.json)
- HNSW parameters: M=32, ef_construction=512
- Collection name: "chunker_knowledge_base"

---

## 6. KEY UTILITY MODULES

### Database & Tracking (chunker_db.py)
- SQLite-based tracking database
- Session logging with retry logic
- Department statistics aggregation
- Error logging with exponential backoff
- 60-second connection timeouts
- WAL (Write-Ahead Logging) pragmas for resilience

### Monitoring System (monitoring_system.py)
- Real-time CPU/memory/disk monitoring
- Processing rate tracking (files/minute)
- Vector DB connection health checks
- Alert thresholds (disk: 88%/95%, processing rate: 0.1/0.02 files/min)
- Email notifications (optional)
- 60-second rate limiting on repeated alerts

### Backup Manager (backup_manager.py)
- Incremental backup scheduling
- Configurable retention (default: 7 backups)
- Automatic backup of chroma_db, 04_output, config.json
- Scheduled intervals (default: 24 hours)

### Incremental Updates (incremental_updates.py)
- File version tracking with SHA-256 hashing
- Prevents re-processing unchanged files
- Chunk ID generation with version encoding
- Manifest management

### Notification System (notification_system.py)
- Multi-channel alerts (email, webhook, etc.)
- Rate limiting and filtering
- Async notification dispatch
- Error handling with graceful degradation

### Enhanced Watchdog (enhanced_watchdog.py)
- Celery-based async file watching
- Advanced file system event handling
- Debouncing with configurable windows (default: 2 seconds)
- `.part` staging file support
- `.ready` signal file support

---

## 7. RAG & VECTOR SEARCH FEATURES

### RAG Integration (rag_integration.py)
**Components**:
- **Embedding Model**: sentence-transformers (nomic-embed-text via Ollama)
- **Vector Store**: ChromaDB with FAISS fallback
- **LLM Backend**: Ollama (local) with API fallback
- **Search**: Hybrid semantic + keyword search
- **Context Assembly**: Ranked result merging with configurable window

### RAG Search (rag_search.py)
**Capabilities**:
- Semantic similarity search
- Keyword matching
- Metadata filtering
- Top-K result ranking
- Query result caching (600s TTL, 512 entries)

### Evaluation Metrics (rag_evaluation.py, comprehensive_eval.py)
**Metrics**:
- Precision@K, Recall@K, Mean Reciprocal Rank
- ROUGE scores (1/2/L variations)
- BertScore semantic similarity
- Faithfulness scoring
- Response quality assessment

### LangSmith Integration (langsmith_integration.py)
- Tracing and observability
- Evaluation harness setup
- Feedback collection
- Project configuration

---

## 8. ASYNC TASK PROCESSING

### Celery Tasks (celery_tasks.py)
**Task Queue**:
- Redis broker integration (optional)
- Priority queues (high/normal)
- Task timeouts: 300s hard limit, 240s soft limit
- Worker pool: 4 concurrent workers (configurable)

**Available Tasks**:
- `process_file_task`: Chunking with metadata
- `add_to_rag_task`: Vector DB insertion
- `evaluate_query_task`: RAG quality assessment
- `deduplicate_task`: Content deduplication
- Scheduled tasks (hourly cleanup, daily backfill)

### Orchestrator (orchestrator.py)
- Unified Celery service startup
- Health monitoring
- Graceful shutdown handling
- Flower dashboard integration (port 5555)

---

## 9. WEB INTERFACES

### FastAPI Server (api_server.py)
**Endpoints**:
- `GET /health` - System health check
- `GET /chunks` - List/search chunks
- `GET /chunk/{id}` - Get specific chunk
- `POST /query` - RAG semantic search
- `POST /process` - Manual file processing
- `GET /stats` - System statistics

**Features**:
- Authentication support (optional)
- Rate limiting
- CORS enabled
- Error handling with detailed responses

### Streamlit GUI (gui_app.py)
**Features**:
- Interactive chunk browser
- Semantic search interface
- Statistics dashboard
- Configuration editor
- Real-time status monitoring
- File upload and processing

**Launch**: `streamlit run gui_app.py`

---

## 10. TESTING & QUALITY ASSURANCE

### Test Coverage
- **test_query_cache.py**: 14+ cases for caching logic
- **test_incremental_updates.py**: 6+ cases for version tracking
- **test_backup_manager.py**: 3+ cases for backup operations
- **test_monitoring_system.py**: 3+ cases for monitoring
- **test_processing_workflow.py**: Full pipeline integration tests
- **conftest.py**: Shared pytest fixtures (excludes 99_doc/legacy)

### Pytest Configuration
```ini
[pytest]
# Root-level pytest.ini with proper path exclusions
```

### Development Tools
- **Linting**: flake8, black (code formatting)
- **Type Checking**: mypy
- **Testing**: pytest with coverage reporting

---

## 11. EXISTING CHUNKING APPROACHES

### Sentence-Based Chunking (Primary)
- **Method**: NLTK sentence tokenization
- **Overlap**: Configurable cross-chunk word overlap
- **Boundaries**: Sentence breaks preserved
- **Ideal For**: Natural language documents

### Size-Based Chunking (Secondary)
- **Method**: Character/word count limits
- **Constraints**: min_chunk_size (100), max_chunk_size (1500)
- **Batching**: 50 chunks per batch to vector DB
- **Ideal For**: Structured data, code

### Department-Specific Chunking
- **Police/Legal**: Smaller chunks (75-100 sentences), full redaction
- **Admin**: Medium chunks (150 sentences), basic validation
- **Default**: 800 sentences, light validation

---

## 12. SYSTEM CAPABILITIES

### Processing Features
- Parallel file processing (8 workers default)
- Multi-encoding file reading with fallback
- Automatic format detection
- Streaming for large files
- Progress tracking per file

### RAG Features
- 2,907+ enriched chunks in knowledge base
- Semantic search with relevance ranking
- Metadata filtering (source, date, tags)
- Caching for query performance
- Batch embedding generation (750 chunks/batch)

### Reliability Features
- Database locking prevention (60s timeouts)
- Automatic retry with exponential backoff
- Failed file quarantining
- Incremental change tracking
- Comprehensive logging and monitoring

### Data Organization
- Automatic folder structures by source type
- Archive organization by department
- Manifest tracking with `.origin.json`
- Consolidated legacy snapshots
- Transactional chunk writing

---

## 13. CURRENT CONFIGURATION HIGHLIGHTS

### Processing Performance
- **Chunk Size**: 800 sentences with 50-sentence overlap
- **Parallel Workers**: 8 concurrent threads
- **Batch Operations**: 50 chunks batched for vector DB
- **File Stability**: 2-second wait before processing
- **Encoding Detection**: 5-encoding fallback chain

### RAG Settings
- **Enabled**: Yes
- **Vector DB**: ChromaDB (chroma_db/ directory)
- **Batch Size**: 750 chunks per RAG insertion
- **Query Cache**: 600s TTL, max 512 entries
- **Search EF**: 64 (HNSW parameter)

### Data Safety
- **Backup**: Enabled, 7 retained (24-hour intervals)
- **Move to Archive**: Yes (not copy)
- **Deduplication**: Enabled (log-only mode)
- **Incremental Tracking**: Disabled (can be enabled)
- **Database**: Enabled with SQLite backend

---

## 14. SUPPORTED FILE FORMATS

### Text Files
- `.txt` - Plain text
- `.md` - Markdown
- `.csv` - CSV data

### Code Files
- `.py` - Python
- `.sql` - SQL
- `.ps1` - PowerShell
- `.dax` - DAX (Power BI)
- `.m` - MATLAB/M-code

### Structured Data
- `.json` - JSON
- `.xlsx` - Excel (openpyxl)
- `.pdf` - PDF (PyPDF2, pdfminer)
- `.docx` - Word documents
- `.yaml`/`.yml` - YAML configuration

---

## 15. RECENT IMPROVEMENTS (v2.1.8+)

### November 2025 Enhancements
1. **Tiny File Archiving**: Auto-archive <100 bytes to `03_archive/skipped_files/`
2. **Manifest Safety**: Skips files with `.origin.json` in name
3. **Chunk Writer Hardening**: Consolidated write helper, UTF-8 encoding, defensive logging
4. **Parallel Queue Handling**: Optional multiprocessing.Pool for large backlogs
5. **Tokenizer Optimization**: LRU caching for sentence tokenization
6. **SQLite Resilience**: 60s timeouts, WAL pragmas, integrity checks at startup
7. **Pytest Guardrails**: Root conftest.py with legacy exclusions
8. **Database Lock Monitoring**: `MONITOR_DB_LOCKS.md` with alert thresholds (2x baseline)

### ChromaDB Rebuild (v2.1.8)
- Upgraded to chromadb 1.3.4
- Recreated vector collection
- Backfilled 2,907 enriched chunks
- Fixed hnswlib compatibility issues

---

## 16. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    File Input (02_data/)                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Watchdog System │ (watchdog 3.0.0)
                    │  File Monitoring │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼──────┐            ┌────────▼────────┐
        │  File Processor   │      │  Encoding Detector │
        │ (read_with_      │      │ (UTF-8/16/Latin-1) │
        │  fallback)       │      └────────┬────────┘
        └─────┬──────┘                     │
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼──────────┐
                    │  Sentence Tokenizer │ (NLTK + LRU cache)
                    │  chunk_text_enhanced │
                    └────────┬──────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼──────┐            ┌────────▼────────┐
        │ Chunk      │            │ Metadata         │
        │ Validation │            │ Enrichment       │
        │            │            │ (Key terms, tags) │
        └─────┬──────┘            └────────┬────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼──────┐            ┌────────▼────────┐
        │ File Writer │            │ Deduplication   │
        │ (chunks,    │            │ (SHA-256 hashing) │
        │  manifest)  │            └────────┬────────┘
        └─────┬──────┘                     │
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼──────────┐
                    │  Vector Database   │
                    │  (ChromaDB + FAISS) │
                    │  Embedding Gen     │
                    │  (sentence-        │
                    │   transformers)    │
                    └────────┬──────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        ┌─────▼──────┐            ┌────────▼────────┐
        │ RAG Search │            │ Database Logging │
        │ (semantic) │            │ (SQLite tracking) │
        └─────┬──────┘            └────────┬────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼──────────┐
                    │  Web Interfaces    │
                    │  (API + GUI)       │
                    │  (FastAPI/Streamlit) │
                    └────────────────────┘
```

---

## 17. QUICK START EXAMPLES

### Basic Chunking
```bash
python watcher_splitter.py
# Monitors 02_data/, outputs chunks to 04_output/
# Archives originals to 03_archive/
```

### RAG Search
```bash
python rag_search.py
# Semantic search on chunked knowledge base
# Requires: ollama pull nomic-embed-text
```

### Web GUI
```bash
streamlit run gui_app.py
# Browser-based search and management
# Launches on http://localhost:8501
```

### FastAPI Server
```bash
python api_server.py
# RESTful API on http://localhost:8000
# Documentation on http://localhost:8000/docs
```

### Async Processing
```bash
python orchestrator.py
# Starts Celery workers + Redis + Flower
# Dashboard on http://localhost:5555
```

---

## 18. CONFIGURATION EXAMPLES

### Enable Incremental Tracking
```json
{
  "incremental_updates": {
    "enabled": true,
    "version_file": "06_config/file_versions.json",
    "hash_algorithm": "sha256",
    "move_unchanged_to_archive": true
  }
}
```

### Tune Vector Search
```json
{
  "default_ef_search": 128,
  "backfill_batch_size": 1000,
  "backfill_num_workers": 16
}
```

### Configure Monitoring
```json
{
  "monitoring": {
    "enabled": true,
    "interval_minutes": 5,
    "disk_thresholds": {"warning": 88, "critical": 95},
    "processing_rate": {
      "enabled": true,
      "min_files_per_minute": 0.1
    }
  }
}
```

---

## SUMMARY

This is a **production-grade enterprise chunking system** with:

- **Mature text processing pipeline** using NLTK sentence tokenization
- **Comprehensive RAG capabilities** with ChromaDB vector store and semantic search
- **Robust error handling** with retry logic, database locking prevention, and incremental tracking
- **Multiple interfaces** (CLI, web API, Streamlit GUI, Celery async tasks)
- **Enterprise features**: monitoring, notifications, backup management, audit logging
- **99 Python modules** totaling ~18,700 lines of well-organized code
- **Advanced functionality**: deduplication, metadata enrichment, department-specific configs
- **Testing & validation**: comprehensive pytest coverage, evaluation metrics, quality assurance

Perfect foundation for adding new chunking/tagging/processing enhancements!

