# Changelog

All notable changes to the Enterprise Chunker system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Tiny File Archiving**: Files under 100 bytes are now automatically archived to `03_archive/skipped_files/` along with their manifests to prevent repeated processing warnings (watcher_splitter.py:677-703).
- **Database Lock Monitoring**: Created `MONITOR_DB_LOCKS.md` with comprehensive monitoring commands, alert thresholds, and 24-48 hour review schedule for tracking SQLite contention patterns.
- **Windows UTF-8 Troubleshooting**: Updated README/SUMMARY with steps for switching PowerShell to UTF-8 to avoid Unicode logging failures on emoji filenames.
- **Streamlit GUI Doc**: Added `streamlit run gui_app.py` workflow to README and SUMMARY so users can launch the browser-based search interface.
- **Chunker Bridge Compatibility**: Watcher now understands `.part` staging files and optional `.ready` markers produced by upstream bridges, keeping them off the work queue until the final rename is complete.
- **Batched Vector Ingest**: `ChromaRAG.add_chunks_bulk()` accepts batches (configurable via `batch.size`) and skips null embeddings while refreshing `hnsw:search_ef` from `search.ef_search`.

### Changed
- **Small File Handling**: Changed log level from WARNING to INFO for small file archiving since this is now expected behavior rather than an error condition.
- **Archive Organization**: Added `skipped_files/` subfolder in archive directory to separate tiny/invalid files from successfully processed files.
- **Watcher Retry Safety**: All sequential and parallel processing paths funnel through `process_with_retries()`, quarantining persistent failures to `03_archive/failed` after exponential backoff and copying any associated `.ready` files.
- **Configuration Defaults**: New keys `debounce_window`, `use_ready_signal`, `failed_dir`, `batch.{size,flush_every,mem_soft_limit_mb}`, and `search.ef_search` expose watcher deferrals and vector-store tuning directly in `config.json`.

### Analysis & Documentation
- **DB Lock Error Analysis**: Detailed breakdown showing 11 `log_processing()` errors vs 1 `_update_department_stats()` error over 8-minute test period (1.5 errors/min baseline, down 68% from previous baseline).
- **Retry Logic Review**: Documented current retry configuration (get_connection: 3 retries, dept_stats: 5 retries with 1.5x backoff), identified that `log_processing()` lacks retry wrapper as potential future improvement.
- **Monitoring Plan**: Established alert thresholds (> 3 errors/min = 2x baseline) and pattern analysis commands for time-based clustering, processing volume correlation, and error duration tracking.

### Fixed
- **Repeated Warnings**: Eliminated log spam from files that don't meet minimum size threshold by archiving them on first detection instead of skipping repeatedly.
- **Log Clutter**: Reduced noise in watcher logs by moving tiny files out of the watch folder automatically.

### Planned
- Additional performance optimizations
- Enhanced error recovery mechanisms
- Consider adding retry wrapper to `log_processing()` if monitoring shows sustained > 3 errors/minute

---

## [v2.1.8] - 2025-11-07 - ChromaDB Rebuild & Release Automation

### Added
- **Release Helper Script**: `scripts/release_commit_and_tag.bat` automates doc staging, backups, commit/tag creation, and pushes with logging and rotation.
- **Documentation**: `docs/RELEASE_WORKFLOW.md` describes the release flow, logging, and cleanup steps.
- **Comprehensive Tests**: Replaced placeholder suites with 52-case pytest coverage for QueryCache, VersionTracker, BackupManager, and Monitoring modules.
- **Watcher Hardening Docs**: `FIXES_APPLIED_SUMMARY.md`, `DATABASE_IMPROVEMENTS.md`, and `VERIFICATION_REPORT.md` capture the November 2025 stability fixes and validation results.

### Changed
- **ChromaDB Maintenance**: Upgraded to `chromadb 1.3.4`, recreated the collection, and re-ran the backfill to repopulate 2,907 enriched chunks.
- **Deduplication**: `deduplication.py` now resolves legacy HNSW compatibility issues so auto-remove runs succeed.
- **RAG Integration**: `rag_integration.py` guards against missing `hnswlib.Index.file_handle_count`, ensuring compatibility across wheels.
- **Watcher Stability (Nov 2025)**: `watcher_splitter.py` now skips manifest/archived/output files, sanitises output folder names, replaces Unicode log arrows, adds safe archive moves, and avoids manifest recursion & WinError 206 failures.
- **SQLite Robustness (Nov 2025)**: Extended connection timeout to 60 s and layered exponential-backoff retries in `chunker_db.py`, dramatically reducing “database is locked” noise during concurrent processing.

### Testing & Validation
- `python -m pytest tests/`
- Dry-run of `scripts/release_commit_and_tag.bat` in a clean clone plus live execution for tag `v2.1.8`.
- Watcher burn-in processing real data feeds, validating cleanup scripts, log tailing, and DB contention mitigation.

### Links
- Full diff: https://github.com/racmac57/chunker_Web/compare/v2.1.7...v2.1.8

---

## [v2.2.1] - 2025-11-06 - Operational Enhancements & Caching

### Added
- **Query Cache**: In-memory LRU + TTL cache for RAG searches with optional memory guard, stats API (`GET /api/cache/stats`), and config defaults under `query_cache`.
- **Incremental Updates**: Thread-safe `VersionTracker` shared by watcher/backfill to hash inputs, skip untouched sources, and clean up stale chunk IDs.
- **Metadata Enrichment Workflow**: Shared heuristics module powering manifest, sidecar, and ChromaDB tagging with tag-aware chunk filenames.
- **Backup Manager**: Scheduled tar.gz lifecycle (`backup_manager.py`) with watcher integration and CLI support.
- **Monitoring System**: Disk/throughput/Chroma checks feeding the notification pipeline with configurable thresholds and cooldowns.

### Changed
- **watcher_splitter.py**: Unified feature initialization, version tracking, enriched manifest/sidecar writes, duplicate skipping, and automated backup scheduling.
- **backfill_knowledge_base.py**: Respects incremental tracker state, merges enrichment payloads, and records dedup/query cache metadata for Chroma ingestion.
- **rag_integration.py** / **api_server.py**: Cache-aware search path with stats surfacing plus resilience improvements for repeated lookups.
- **config.json**: Expanded with `query_cache`, `incremental_updates`, `monitoring`, and `backup` sections (all disabled by default for backwards compatibility).

### Documentation
- `README.md`: Refreshed Feature Toggles section with query cache metrics, incremental update behavior, and backup/monitoring guidance.
- `docs/METADATA_SCHEMA.md`: Documented enrichment schema, tag rules, and ChromaDB metadata fields.
- `CHANGELOG.md`: Captures integrated feature set and testing steps.

### Testing
- `pytest tests/test_query_cache.py`
- `pytest tests/test_incremental_updates.py`
- `pytest tests/test_backup_manager.py`
- Targeted watcher/backfill dry runs with feature toggles (metadata enrichment, dedup, incremental updates, query cache, backup, monitoring) enabled.

---

## [v2.2.0] - 2025-11-06 - Feature Toggle Integration & QA

### Added
- **Metadata Enrichment Pipeline** gated by `metadata_enrichment.enabled`, producing tags, summaries, and manifest enrichment.
- **Incremental Updates** with `VersionTracker` support across watcher and backfill for hash-based skip + artifact cleanup.
- **Monitoring System Integration** wiring runtime health checks into the watcher loop with optional alerts.
- **Backup Scheduler Hooks** to start/stop `BackupManager` from the watcher when enabled.
- **End-to-End Tests** in `tests/test_enhancements.py` covering metadata sidecars, incremental skips, and dedup stubs.

### Changed
- **watcher_splitter.py**: Refactored feature initialization, optional metadata flow, incremental cleanup, and dedup stats.
- **backfill_knowledge_base.py**: Added incremental filtering/recording and shared dedup + metadata handling improvements.
- **config.json**: Introduced `metadata_enrichment` and `incremental_updates` sections (defaults disabled) and aligned toggle defaults.
- **rag_integration.py**: Query cache now respects config defaults (already present, documented).

### Documentation
- `README.md`: New “Feature Toggles & Setup” section covering metadata tagging, monitoring, dedup, caching, incremental updates, and backups.
- `docs/METADATA_SCHEMA.md`: Serves as canonical schema reference for enriched sidecars/manifests.
- `CHANGELOG.md`: Updated with integration release notes.

### Testing
- `pytest tests/test_enhancements.py` validates metadata sidecar generation, incremental skip behaviour, and dedup statistics.
- Verification scripts (`verify_chunk_completeness.py`, dedup cleanup) executed to ensure regression safety.

---

## [v2.1.6] - 2025-11-05 - RAG Backfill Optimization and Multiprocessing

### Added
- **Multiprocessing Support**: Parallel file reading and metadata extraction with 4-8 workers
- **Parallel ChromaDB Inserts**: Separate ChromaDB connections per process for concurrent inserts
- **Empty Folder Logging**: Comprehensive logging of folders without chunk files
- **Count Discrepancy Alerts**: Warnings when expected vs actual chunk counts differ
- **Chunk Existence Verification**: Pre-insertion checks to avoid duplicate processing
- **CPU Saturation Monitoring**: Real-time CPU usage tracking with alerts (>90% threshold)
- **Performance Profiling**: Optional cProfile integration for bottleneck identification
- **Batch Size Optimization**: Configurable batch sizes (500-1000 chunks) for ChromaDB efficiency
- **Verification Scripts**: `verify_backfill.py` and `verify_chunk_completeness.py` for validation

### Changed
- **backfill_knowledge_base.py**: Complete rewrite with multiprocessing and optimization
  - Parallel file processing with Pool workers
  - Separate ChromaDB connections per worker process
  - Batch size optimized to 750 chunks (from 1000)
  - Enhanced error handling and retry logic
- **rag_integration.py**: HNSW parameter configuration fixed
  - Correct parameter names: `hnsw:construction_ef` and `hnsw:search_ef`
  - Proper collection creation with `get_collection()` first, then `create_collection()`
  - HNSW settings: M=32, ef_construction=512, ef_search=200
- **config.json**: Added backfill configuration options
  - `backfill_batch_size`: 750 (optimized for ChromaDB)
  - `backfill_multiprocessing`: true
  - `backfill_num_workers`: null (auto-detects 4-8)
  - `backfill_profile`: false
  - `expected_chunk_count`: null (for discrepancy alerts)

### Fixed
- **HNSW Parameter Errors**: Fixed "Failed to parse hnsw parameters" by using correct metadata keys
- **ChromaDB Collection Creation**: Fixed collection initialization to handle existing collections
- **Duplicate Detection**: Enhanced duplicate checking before insertion
- **File Existence Verification**: Added checks before processing chunk files

### Performance
- **Throughput**: Increased from ~5 chunks/second to 100-200+ chunks/second with multiprocessing
- **Processing Time**: Reduced from ~10 minutes to 2-3 minutes for 3,200 chunks
- **Memory Efficiency**: Optimized batch processing reduces peak memory usage
- **CPU Utilization**: Better CPU core utilization with parallel processing

### Documentation
- Updated version references to 2.1.6
- Added comprehensive verification procedures
- Enhanced error logging and troubleshooting guides

---

## [2025-11-01] - System Recovery & Move Workflow Testing

### Added
- **System Recovery**: Successfully recovered from crash and restored `watcher_splitter.py`
- **Enhanced Archive Integration**: Integrated `archive_processed_file()` from `celery_tasks.py` into watcher
- **Automated Testing**: Added `--auto` flag to `manual_process_files.py` for non-interactive processing
- **Recovery Documentation**: Complete recovery summary in `RECOVERY_SUCCESS.md`

### Changed
- **watcher_splitter.py**: Enhanced to use new archive function with fallback logic
- **manual_process_files.py**: Added command-line arguments for automated testing
- **TASK_PROGRESS_REPORT.md**: Updated with recovery status and testing results

### Fixed
- **Processing Workflow**: Watcher now functional without Celery dependency
- **Archive Operations**: Full MOVE workflow with retry logic operational
- **Manifest Preservation**: `.origin.json` files correctly moved to archive

### Testing
- ✅ End-to-end workflow test: 4 markdown files processed successfully
- ✅ Enhanced archive function verified with MOVE operations
- ✅ Manifest validation confirmed
- ✅ Zero data loss verified

### Results
- Files processed: 4 markdown files
- Archive operations: 4 successful MOVE operations
- Manifest tracking: All origin files preserved
- Performance: ~3 seconds per file processing time

---

## [2025-10-31] - Git Setup & Directory Maintenance

### Added
- **Git Repository**: Initialized version control for the project
- **GitHub Integration**: Connected to remote repository `racmac57/chunker_Web`
- **Comprehensive .gitignore**: Excludes processed docs, archives, logs, databases, and virtual environments

### Changed
- Directory cleanup and normalization
- Documentation moved to `99_doc/` structure
- Legacy snapshot pruning (kept latest per project)
- Removed development cruft and temporary files
- Updated documentation with Git workflow information

### Removed
- Temporary processing scripts (simple_process.py, test_fail_file.py, enhanced_process.py, etc.)
- Redundant documentation files
- Legacy project artifacts (after snapshot consolidation)

### Metrics
- Items scanned: 16595
- Files moved: 7
- Items deleted: 627
- Snapshots pruned: 0
- Files committed to Git: 128 files (171,244 insertions, 102,346 deletions)

### Git Status
- **Repository**: Successfully initialized and connected to GitHub
- **Remote**: `https://github.com/racmac57/chunker_Web.git`
- **Branch**: `main`
- **Latest Commit**: `c1e4283` - "Cleanup: remove temporary scripts, organize structure, and update .gitignore"

**Maintenance Log:** `05_logs/maintenance/2025_10_31_19_16_35/`



All notable changes to the Enterprise Chunker system will be documented in this file.
## Version 2.1.3 - 2025-10-29 - Project Consolidation & Legacy Snapshots

### 🔄 Consolidation
- Unified older Chunker/ClaudeExportFixer iterations under `C:\_chunker`
- Migrated historical outputs to `C:\_chunker\04_output\<ProjectName>_<timestamp>`
- Collected legacy docs/config/logs/db into:
  - `99_doc\legacy\<ProjectName>_<timestamp>`
  - `06_config\legacy\<ProjectName>_<timestamp>`
  - `05_logs\legacy\<ProjectName>_<timestamp>`
  - `03_archive\legacy\<ProjectName>_<timestamp>`

### 📦 Script Backups
- Backed up project scripts with timestamp-prefix to
  `C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\backup_scripts\<ProjectName>\`
- Excludes virtualenvs, site-packages, node_modules, and .git

### 🧹 Snapshot Policy
- Keep only the latest legacy snapshot per project (older snapshots pruned)
- Now-empty old project folders archived then removed after verification

### 📁 Updated Documentation
- `README.md` updated with consolidation notes and locations
- `ENTERPRISE_CHUNKER_SUMMARY.md` updated with unified structure and snapshot policy

### 🧩 File Type Support
- Added support for `.xlsm` (Excel macro-enabled) files via openpyxl

### 🧾 Sidecar & Code Block Summaries
- Added optional JSON sidecar per processed file (enabled by default)
- For Python files, extract class/function blocks with spans and signatures
- Optional transcript appendix “Code Blocks Summary” for .py files (enabled by default)
- New config flags: `enable_json_sidecar`, `enable_block_summary`, `enable_grok`

## Version 2.1.4 - 2025-10-30 - Watcher Robustness & Write-back

### 🔍 Discovery Improvements
- Case-insensitive extension matching using `Path.iterdir()` with lowercased suffix
- Enhanced debug logging for include/exclude decisions
- Startup log now shows Celery status

### 🧾 Sidecar & Write-back
- Sidecar JSON written next to transcript and copied to `source/` when enabled
- Enhanced origin metadata in sidecar (paths, sizes, timestamps)

### 🖱️ Windows SendTo + Origin Manifests
- Added optional Windows SendTo helper (`SendTo/Chunker.ps1` + `Chunker.bat`) to copy files/folders into `02_data`
- Per-file manifest `<file>.origin.json` captures original path, times, size, SHA-256; watcher uses this to populate sidecar origin
- Optional HMAC verification with key in `06_config/manifest_hmac.key` (best-effort, non-blocking)

### ⚙️ Defaults & Config
- `celery_enabled` default set to `false` for direct processing unless explicitly enabled
- Confirmed flags enabled by default:
  - `enable_json_sidecar`, `enable_block_summary`, `copy_sidecar_to_source`

### 📝 Documentation
- README and Enterprise Summary updated with discovery changes, sidecar write-back, and config notes


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 2.1.2 - 2025-10-27 - Critical Loop Fix & Performance Optimization

### 🚨 Critical Fixes
- **Processing Loop Resolution**: Fixed infinite processing loops by ensuring failed files are moved to archive
- **File Archive Management**: Unreadable files → `03_archive/failed/`, too-short files → `03_archive/skipped/`, no-chunk files → `03_archive/no_chunks/`
- **Database Locking**: Resolved frequent "database is locked" errors with batch operations
- **File Stability**: Reduced stability check times (1s min, 15s max) for faster processing

### ⚡ Performance Enhancements
- **Dynamic Parallel Workers**: Up to 12 workers for large batches (50+ files), 8 for smaller batches
- **Batch Processing**: Process large file sets in configurable batches with delays to prevent system overload
- **Optimized Database Operations**: Batch logging reduces database locking and improves throughput
- **Enhanced Monitoring**: Real-time performance metrics including files/minute, avg processing time, peak CPU/memory

### 🔧 Technical Improvements
- **Source Folder Copying**: Configurable copying of processed chunks/transcripts back to source folders
- **Enhanced Error Handling**: Comprehensive error logging with automatic file archiving
- **Speed Optimizations**: Reduced file stability checks, faster database operations, improved parallel processing
- **Production Stability**: System now handles 500+ files efficiently without loops or crashes

### 📁 Updated Files
- `watcher_splitter.py` - Loop fix, performance enhancements, source copying, batch operations
- `config.json` - Added performance settings (parallel_workers, batch_size, database_batch_size)
- `CHANGELOG.md` - Version 2.1.2 documentation

### 🎯 Performance Results
**✅ MASSIVE PERFORMANCE IMPROVEMENT**:
- ✅ **No more processing loops** - Files properly archived when failed
- ✅ **8-12x faster processing** - Dynamic parallel workers and batch operations
- ✅ **Database stability** - Batch logging eliminates locking issues
- ✅ **500+ file capability** - System now handles large volumes efficiently
- ✅ **Real-time monitoring** - Enhanced performance metrics and tracking

## Version 2.1.1 - 2025-10-27 - Production Hardening

### 🔒 Security Enhancements
- **Flower Authentication**: Added basic auth with environment variable support
- **Credential Management**: Secure password generation with production warnings
- **Access Control**: Protected monitoring dashboard from unauthorized access

### 🚀 Reliability Improvements
- **Redis Fallback**: Automatic fallback to multiprocessing.Queue if Redis unavailable
- **Priority Processing**: High-priority queues for legal/police departments (priority=9)
- **Enhanced Error Handling**: Comprehensive Redis failure detection and recovery
- **Task Timeout Management**: Improved timeout handling with graceful degradation

### 🧪 Testing & Monitoring
- **Extended Test Coverage**: Added Redis failure, high-volume, timeout, and priority tests
- **Edge Case Validation**: Comprehensive testing of production scenarios
- **Health Monitoring**: Enhanced health checks with fallback detection
- **Production Readiness**: All critical gaps addressed

### 📁 Updated Files
- `orchestrator.py` - Redis fallback, Flower authentication
- `celery_tasks.py` - Priority task processing, enhanced routing
- `test_celery_integration.py` - Extended test coverage for edge cases
- `README.md` - Security features, priority queues, environment variables
- `CHANGELOG.md` - Version 2.1.1 documentation

### 🎯 Production Status
**✅ PRODUCTION READY** - All identified gaps addressed:
- ✅ Redis dependency management with fallback
- ✅ Flower security with authentication
- ✅ Task prioritization for urgent departments
- ✅ Comprehensive edge case testing
- ✅ Enhanced monitoring and health checks

## Version 2.1.0 - 2025-10-27 - Celery Integration

### 🚀 New Features
- **Celery Task Queue Integration**: Advanced async processing with Redis broker
- **Task Chains**: Process → RAG → Evaluate workflow with automatic retries
- **Flower Dashboard**: Web-based monitoring at http://localhost:5555
- **Enhanced Orchestrator**: Automated service management with health checks
- **Graceful Fallback**: System continues working if Celery/Redis unavailable
- **Rate Limiting**: Configurable task rate limits (10/m processing, 20/m RAG)
- **Task Timeouts**: 300s hard limit, 240s soft limit with retries
- **Health Monitoring**: Automated health checks every minute

### 🔧 Enhancements
- **Advanced Error Handling**: Network failure retries (3 attempts)
- **Task Routing**: Separate queues for processing, RAG, evaluation, monitoring
- **Comprehensive Logging**: Task start/completion/failure tracking
- **Backward Compatibility**: Existing functionality preserved
- **Configuration**: Celery settings in config.json

### 📁 New Files
- `celery_tasks.py` - Task definitions and chains
- `enhanced_watchdog.py` - Celery-integrated file monitoring
- `orchestrator.py` - Service orchestration with Flower dashboard
- `advanced_celery_config.py` - Advanced Celery configuration

### 🔄 Updated Files
- `watcher_splitter.py` - Celery integration with fallback
- `config.json` - Added Celery configuration options
- `requirements_rag.txt` - Added celery, redis, flower dependencies
- `README.md` - Celery usage instructions and monitoring guide

## [Version 1.2.1] - 2025-10-27 - Enhanced RAG Implementation

### Fixed
- **Redundant file opens**: Fixed processors to use passed text instead of reopening files
- **Encoding handling**: Changed from 'ignore' to 'replace' for better data preservation
- **NLTK import issues**: Added proper stopwords handling with fallback
- **LangSmith integration**: Cleaned up unused imports and improved error handling

### Enhanced
- **Modular file processors**: Created `file_processors.py` module for better organization
- **Security redaction**: Added PII redaction for sensitive data in RAG chunks
- **Config validation**: Added startup validation for configuration parameters
- **Error handling**: Improved graceful degradation when RAG components unavailable
- **Performance**: Better memory handling for large files

### Added
- **Automated testing**: `rag_test.py` for comprehensive RAG evaluation
- **Type hints**: Added type annotations throughout RAG modules
- **Comprehensive docstrings**: Improved documentation for all functions
- **Dependency checking**: Runtime checks for file processor dependencies
- **RAG query examples**: Added usage examples to README

### Technical Improvements
- **File processing**: Streamlined file reading with appropriate processors
- **Error recovery**: Better error handling without breaking main processing
- **Code organization**: Separated concerns into dedicated modules
- **Testing framework**: Automated test suite with threshold validation
- **Documentation**: Enhanced examples and usage instructions

## [Version 1.2.0] - 2025-10-27 - RAG Integration Complete

### Added
- **RAG Integration**: Comprehensive retrieval-augmented generation system with ChromaDB
- **Vector Database**: ChromaDB integration for semantic search and knowledge base management
- **Faithfulness Scoring**: Advanced evaluation of answer grounding in source context
- **Expanded File Type Support**: Added processors for .xlsx, .pdf, .py, .docx, .sql, .yaml, .xml, .log
- **RAG Evaluation Metrics**: Precision@K, Recall@K, MRR, nDCG, ROUGE, BLEU scores
- **LangSmith Integration**: Tracing, feedback collection, and quality assurance capabilities
- **Hybrid Search**: Combined semantic and keyword-based retrieval
- **Advanced Metadata Extraction**: Enhanced metadata for all file types including formulas, imports, docstrings

### Implementation Files
- `rag_integration.py`: ChromaDB RAG system with faithfulness scoring
- `rag_evaluation.py`: Comprehensive evaluation metrics and pipeline
- `rag_search.py`: Interactive search interface and command-line tool
- `install_rag_dependencies.py`: Automated dependency installation script
- `test_queries.json`: Test queries for evaluation
- `GROK_IMPLEMENTATION_GUIDE.md`: Complete guide for Grok implementation
- Updated `config.json` with RAG and LangSmith configuration
- Updated `requirements.txt` with all necessary dependencies
- Updated `watcher_splitter.py` with RAG integration and file type processors
- Updated `README.md` with RAG usage documentation

### Technical Details
- Integrated ChromaDB vector database with automatic chunk indexing
- Added file type processors for Excel, PDF, Python, Word, YAML, XML, SQL, and log files
- Implemented faithfulness scoring using sentence transformers
- Added comprehensive RAG evaluation metrics (retrieval and generation)
- Created interactive search interface with command-line support
- Added automated dependency installation script
- Integrated RAG processing into existing watcher pipeline

### Usage
- Enable RAG: Set `"rag_enabled": true` in config.json
- Install dependencies: `python install_rag_dependencies.py`
- Search knowledge base: `python rag_search.py`
- Process files: `python watcher_splitter.py` (automatically adds to ChromaDB)

## [Version 1.1.0] - 2025-10-27

### Added
- **Timestamp-prefixed output folders**: Output folders now include `YYYY_MM_DD_HH_MM_SS_` prefix for better chronological organization
- **Enhanced file organization**: Processed files are now organized by processing timestamp, making it easier to track when files were processed
- **Robust chunking logging**: Added detailed logging for chunking operations including text length, sentence count, chunk parameters, and processing statistics
- **Directory cleanup and organization**: Moved old scripts to archive, organized documentation in 99_doc folder

### Fixed
- **Critical Fix**: Resolved Unicode filename processing issues that prevented files with special characters (emojis, symbols) from being processed correctly
- **Enhanced filename sanitization**: Improved regex-based cleaning to handle problematic characters while preserving readable filenames
- **Unicode encoding errors**: Fixed console logging issues with special characters that caused processing failures
- **Directory creation failures**: Resolved "No such file or directory" errors when creating output folders for files with special characters
- **Windows path length limits**: Fixed directory name length issues by reducing filename limit to 50 characters to account for timestamp prefixes

### Technical Details
- Added enhanced filename sanitization using regex pattern `[^\w\s-]` to remove special characters
- Implemented safe filename logging with ASCII encoding fallback to prevent console encoding errors
- Added filename length limits (100 characters) to prevent Windows path length issues
- Improved error handling for directory creation and file writing operations

### Impact
- Files with emojis, special symbols, and Unicode characters now process successfully
- Eliminated processing failures that previously required manual filename changes
- Improved system reliability for diverse file naming conventions
- Maintained backward compatibility with existing filename formats

## [Previous Versions]

### Initial Release
- Enterprise-grade chunker with database tracking
- Parallel processing capabilities
- Department-specific configurations
- Comprehensive logging and monitoring
- Automatic file archiving and organization
