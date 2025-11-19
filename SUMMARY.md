# Enterprise Chunker v2.1.9 - Project Summary

## Overview

Enterprise Chunker is a production-ready file processing system with RAG (Retrieval-Augmented Generation) capabilities. It processes diverse file types, extracts chunks, generates transcripts, and maintains a searchable knowledge base using the ChromaDB vector database.

## Key Directories

- **`02_data/`** - Watch folder for input files
- **`03_archive/`** - Archived original files (MOVE-based workflow)
- **`04_output/`** - Processed chunks and transcripts organized by source file
- **`05_logs/`** - Application logs and processing history
- **`06_config/`** - Configuration files (config.json)
- **`chroma_db/`** - ChromaDB vector database storage
- **`99_doc/`** - Documentation and legacy snapshots

## Entry Points

- **`watcher_splitter.py`** - Main file processing watcher
- **`backfill_knowledge_base.py`** - Backfill script for existing chunks (v2.1.6 optimized)
- **`rag_search.py`** - Interactive knowledge base search
- **`gui_app.py`** - Streamlit GUI for search, browsing results, and stats
- **`manual_process_files.py`** - Manual file processing tool
- **`verify_chunk_completeness.py`** - Verification script for backfill validation

## Changes in v2.1.9 (2025-11-18)

- **Performance Improvements**: Batch processing (100 files per cycle), stability skip for old files (>10 minutes), and enhanced parallel processing options dramatically reduce processing time for large backlogs (6,500 files: 3.5 hours → 53 minutes).
- **Archive Reprocessing**: New `reprocess_output.py` script enables reprocessing of archived files with enhanced tagging and domain-aware department detection.
- **OneDrive Migration**: `migrate_to_onedrive.py` safely migrates local archives to OneDrive with conflict resolution and Windows MAX_PATH handling.
- **Department Refactoring**: 18 domain-specific departments (python, cad, claude, data-cleaning, etc.) with tailored configurations and priority settings.
- **Auto-Archival**: Optional weekly archival of old output sessions (>90 days) to `03_archive/consolidated/YYYY/MM/`.
- **Long Path Handling**: Automatic path shortening for Windows MAX_PATH limits (>240 characters).
- **Version Conflict Resolution**: Automatic `_v2`, `_v3` suffix handling for sidecars and manifests.

## Changes in v2.1.8

- Upgraded to `chromadb 1.3.4`, rebuilt the collection, and re-ran the backfill so 2,907 enriched chunks reflect the latest pipeline.
- Hardened `deduplication.py` and `rag_integration.py` with `hnswlib` compatibility shims, enabling successful auto-remove runs.
- Added and validated `scripts/release_commit_and_tag.bat`, documenting the workflow and recording the 2025-11-07 dry run plus live execution in `docs/RELEASE_WORKFLOW.md`.
- Replaced placeholder modules with comprehensive pytest suites (52 tests) for query caching, incremental updates, backup manager, and monitoring to match production behavior.
- **Watcher Stability Hardening (2025-11-07)**: Skips manifest/archived/output files, sanitises output folder names, replaces Unicode logging arrows, and adds safe archive moves to prevent recursion and WinError 206 failures.
- **SQLite Robustness (2025-11-07)**: Extended connection timeout, layered exponential-backoff retries for department stats, and reduced "database is locked" noise during concurrent processing.

## Recent Improvements (Post-v2.1.8)

### Tiny File Handling
- **Automatic Archiving**: Files under 100 bytes (empty files, placeholders, "No measures found" messages) are now automatically moved to `03_archive/skipped_files/` along with their manifests.
- **Cleaner Logs**: Changed from repeated WARNING messages to single INFO message on archive, reducing log spam.
- **Preserved Files**: Tiny files are preserved in archive for review rather than left in watch folder or deleted.

### Chunk Writer & Manifest Hardening
- **Single Directory Pass**: Consolidated `write_chunk_files()` builds the parent folder once, writes each chunk with UTF-8 safety, and logs failures without halting the batch.
- **Manifest Copies**: `copy_manifest_sidecar()` now always prepares the destination path before cloning manifests, preventing `FileNotFoundError` in fresh OneDrive hierarchies.
- **Manifest Hygiene**: Watcher ignores any filename containing `.origin.json`, and automatically re-hashes content when manifests arrive without stored checksums so incremental tracking stays accurate.

### Database Lock Monitoring
- **Monitoring Documentation**: Created `MONITOR_DB_LOCKS.md` with real-time monitoring commands, hourly error counts, and pattern analysis scripts.
- **Alert Thresholds**: Established baseline at 1.5 errors/minute (68% reduction from previous), alert threshold at 3 errors/minute (2x baseline).
- **24-48 Hour Review Schedule**: Structured monitoring plan to identify time-based clustering, processing volume correlation, and sustained error periods.
- **Error Analysis**: Identified that 92% of lock errors occur in `log_processing()` (lacks retry wrapper) vs 8% in `_update_department_stats()` (has 5-retry backoff).
- **Error Log Retries**: `chunker_db.log_error` supports both legacy and streamlined call signatures while retrying writes with exponential backoff and a 60 s SQLite timeout, dramatically reducing `database is locked` noise.

### Queue & Metrics Optimizations
- **Tokenizer Cache**: Sentence tokenization uses an LRU cache so repeat documents avoid redundant NLTK calls.
- **Background Metrics**: System metrics run on a dedicated executor and notification bursts are rate-limited (once every 60 s per key) to keep the main watcher loop responsive.
- **Queue Handling**: Optional `multiprocessing.Pool` batches (configurable) accelerate heavy backlogs, while the `processed_files` set auto-clears past 1,000 entries to prevent lookup bloat.

### SQLite Reliability
- **Centralized Connection Helper**: `_conn()` applies 60 s timeouts and WAL pragmas across the module, and `get_connection()` delegates to it for consistency.
- **Integrity Check**: `run_integrity_check()` runs at startup, logging anomalies before work begins.

### Testing & Collection Guardrails
- **Legacy Skip Hook**: Root `conftest.py` skips `99_doc/legacy` collections to keep pytest runs focused on active suites.
- **DB Smoke Test**: `tests/test_db.py` exercises the new retry logic, ensuring locked inserts surface immediately during CI.

### Windows Console Encoding
- **UTF-8 Shell Setup**: Documented `chcp 65001` and `PYTHONIOENCODING=utf-8` steps so emoji-rich filenames no longer trigger Unicode logging errors on Windows watchers.

### Archive & Output Organisation
- `03_archive/` - Successfully processed files
- `03_archive/skipped_files/` - Files too small to process (< 100 bytes)
- Output folders pre-create manifest and chunk directories, avoiding empty `03_archive/failed` fallbacks.

## Prior Highlights (v2.1.6)

- **Multiprocessing Backfill**: Parallel processing with 4-8 workers for 20x performance improvement
- **Optimized ChromaDB Inserts**: Separate connections per process for concurrent batch operations
- **HNSW Vector Index**: Tuned parameters (M=32, ef_construction=512, ef_search=200) for large datasets
- **Comprehensive Verification**: Validation tools ensure all chunks from all folders are processed
- **CPU & Memory Monitoring**: Real-time resource tracking with saturation alerts
- **Duplicate Prevention**: Pre-insertion checks prevent duplicate chunks in knowledge base
- **Batch Optimization**: Configurable batch sizes (500-1000) optimized for ChromaDB performance

## Technology Stack

- **Python 3.13** - Core runtime
- **ChromaDB 1.3.4** - Vector database for RAG
- **NLTK** - Natural language processing and keyword extraction
- **psutil** - System resource monitoring
- **tqdm** - Progress tracking
- **multiprocessing** - Parallel processing support

## Configuration

Key settings in `config.json`:
- `rag_enabled`: true (enables RAG functionality)
- `backfill_batch_size`: 750 (optimized batch size)
- `backfill_multiprocessing`: true (enables parallel processing)
- `backfill_num_workers`: null (auto-detects 4-8 workers)
- `chroma_persist_dir`: "./chroma_db" (vector database location)

## Performance

- **Backfill Throughput**: 100-200 chunks/second (with multiprocessing)
- **Processing Time**: 2-3 minutes for 3,200 chunks
- **Memory Usage**: Optimized with batch processing and disk persistence
- **CPU Utilization**: Efficient multi-core usage with parallel workers

## Documentation

- **CHANGELOG.md** - Detailed version history and changes
- **README.md** - Comprehensive usage and feature documentation
- **SUMMARY.md** - This file (project overview and key points)

