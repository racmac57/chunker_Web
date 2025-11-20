# Handoff Prompt for Claude Code - _chunker Project

## Project Overview

**Enterprise Chunker v2.1.9** is a production-ready file processing system with RAG (Retrieval-Augmented Generation) capabilities. It processes diverse file types (text, code, office documents), extracts chunks, generates transcripts, enriches metadata, and maintains a searchable knowledge base using ChromaDB vector database.

**Primary Location**: `C:\_chunker`  
**OneDrive Location**: `C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared`  
**GitHub Repository**: `https://github.com/racmac57/chunker_Web.git`

## Current System State (2025-11-19)

### Processing Status
- **Watcher Status**: ✅ Running and processing files correctly
- **Recent Processing**: 0 errors in current logs (last checked ~20:56 EST)
- **Files Remaining in 02_data**: 43 files (all correctly excluded or unsupported)
  - 31 files excluded (backup/temp files matching exclude patterns)
  - 3 files with unsupported extensions (.xlsx, .pdf)
  - 9 manifest files (.origin.json) - metadata only
  - 0 files should be processed (watcher waiting for new files)

### Failed Files Situation
- **Local Failed Directory**: `C:\_chunker\03_archive\failed` contains **4,432 files**
- **OneDrive Failed Directory**: `C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\03_archive\failed` contains **1 file**
- **Key Finding**: The 4,432 failed files are **NOT from current processing**. They were moved to failed during previous processing attempts (August-October 2025), before recent code updates.
- **Most Recent Failed File**: November 18, 2025 (1.2 days ago, 28.8 hours old)
- **No files failed today** when parallel/multicore processing was enabled
- **Current logs show 0 errors** - processing is working correctly

### Important Finding
The 4,432 files in `C:\_chunker\03_archive\failed` were **not moved** by the updated `watcher_splitter` when parallel/multicore processing was enabled. They are from historical processing attempts and need to be reviewed separately.

## Recent Changes (v2.1.9 - 2025-11-18)

### Performance Improvements
1. **Batch Processing**: Configurable batch size (default 100 files per cycle) prevents system overload
2. **Stability Skip Optimization**: Files older than `stability_skip_minutes` (default 10) bypass expensive stability checks, dramatically reducing processing time for large backlogs
3. **Enhanced Parallel Processing**: 
   - Default: Thread-based parallelism (8 workers)
   - Optional: Multiprocessing mode with automatic fallback to sequential on errors
   - Fixed hardcoded worker limit (was 4, now uses config value)
4. **Performance Results**: 6,500 files processed in ~53 minutes (down from 3.5 hours) - 90% improvement

### Department Configuration Refactoring
- Replaced generic departments (police, admin, legal) with 18 domain-specific departments:
  - Code domains: `python`, `powershell`, `sql`, `dax`, `mcode`
  - System domains: `cad`, `rms`, `arcgis`, `scrpa`
  - Content domains: `claude`, `data-cleaning`, `data-export`, `documentation`, etc.
- Each department has tailored settings:
  - `chunk_size`: Domain-appropriate chunk sizes
  - `enable_redaction`: Based on sensitive content
  - `audit_level`: `basic`, `enhanced`, or `full`
  - `priority`: Processing priority during batch operations
- Enhanced `get_department_config()` uses multi-source detection (file extension, filename/path keywords, metadata tags)

### Archive Reprocessing
- New script: `reprocess_output.py` 
- Reprocesses files from OneDrive `04_output` and `03_archive`
- Enhanced transcript reconstruction: Concatenates all `*.txt` chunks in sorted order
- Edge case handling: Skips empty sessions, warns on large sessions, handles corrupted sidecars
- Marker-based reprocessing detection to avoid duplicates
- Auto-cleanup of old markers (default 180 days)

### OneDrive Migration
- Script: `migrate_to_onedrive.py`
- Safely migrates local `04_output` and `03_archive` to OneDrive
- Windows MAX_PATH handling: Pre-checks paths >240 characters and skips with tracking
- Conflict resolution: Atomic moves with `os.replace()` and version suffixes
- Successfully migrated 15,612 files (4.55 GB) with 99.3% success rate

### Auto-Archival
- Optional weekly archival of old output sessions (>90 days) to `03_archive/consolidated/YYYY/MM/`
- Configurable via `archive_old_outputs` and `archive_after_days` in config.json

### Long Path Handling
- Automatic path shortening for Windows MAX_PATH limits (>240 characters)
- Uses hash-based shortened session names when paths exceed limit

### Version Conflict Resolution
- Automatic `_v2`, `_v3` suffix handling for sidecars and manifests to prevent overwrites

## Directory Structure

```
C:\_chunker\
├── 01_scripts/              # Utility scripts (chunk_and_tag.py, etc.)
├── 02_data/                 # Watch folder for input files
│   └── .reprocessed_sources/  # Marker directory for reprocessing
├── 03_archive/              # Archived original files (MOVE-based workflow)
│   ├── failed/              # Failed processing attempts (4,432 files)
│   ├── skipped_files/       # Files too small to process (< 100 bytes)
│   └── consolidated/        # Old output sessions (>90 days)
├── 04_output/               # Local output (deprecated - use OneDrive)
├── 05_logs/                 # Application logs and tracking
│   └── watcher.log          # Main watcher log
├── 06_config/               # Configuration files
│   ├── config.json          # Main configuration
│   ├── reprocess_config.json  # Reprocessing configuration
│   └── file_versions.json   # Incremental update tracking
├── chroma_db/               # ChromaDB vector database storage
├── watcher_splitter.py      # Main file processing watcher ⭐
├── reprocess_output.py      # Archive reprocessing script
├── migrate_to_onedrive.py   # OneDrive migration script
├── metadata_enrichment.py   # Metadata tagging and enrichment
├── README.md                # Comprehensive documentation
├── SUMMARY.md               # Project summary
└── CHANGELOG.md             # Version history

OneDrive: C:\Users\carucci_r\OneDrive - City of Hackensack\KB_Shared\
├── 02_data/                 # Watch folder (future - currently local)
├── 03_archive/              # Archived files (migrated from local)
│   └── failed/              # Failed directory (1 file)
├── 04_output/               # Processed chunks and transcripts ⭐
└── [department folders]/    # Department-organized archives
```

## Key Configuration Files

### `config.json` (Main Configuration)
```json
{
  "watch_folder": "C:\\_chunker\\02_data",
  "output_dir": "%OneDriveCommercial%\\KB_Shared\\04_output",
  "archive_dir": "%OneDriveCommercial%\\KB_Shared\\03_archive",
  "supported_extensions": [".txt",".md",".csv",".json",".py",".m",".dax",".ps1",".sql"],
  "exclude_patterns": ["_draft", "_temp", "_backup"],
  "parallel_workers": 8,
  "enable_parallel_processing": true,
  "batch_size": 100,
  "stability_skip_minutes": 10,
  "use_multiprocessing": false,
  "multiprocessing_fallback": true,
  "enable_file_level_dedup": true,
  "archive_old_outputs": true,
  "archive_after_days": 90,
  "rag_enabled": true,
  "metadata_enrichment": { "enabled": true, "max_key_terms": 6 },
  "deduplication": { "enabled": true, "auto_remove": false, "log_only": true }
}
```

### `reprocess_config.json` (Reprocessing Configuration)
```json
{
  "watch_folder": "C:\\_chunker\\02_data",
  "output_dir": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\KB_Shared\\04_output",
  "archive_dir": "C:\\Users\\carucci_r\\OneDrive - City of Hackensack\\KB_Shared\\03_archive",
  "marker_dir": "C:\\_chunker\\02_data\\.reprocessed_sources",
  "process_archive": true,
  "process_output": false,
  "cleanup_markers_days": 180,
  "dry_run": true,
  "skip_marked": false
}
```

## Main Scripts and Their Purposes

### `watcher_splitter.py` ⭐ (Main Entry Point)
- **Purpose**: Monitors `02_data` folder, processes files, generates chunks, enriches metadata
- **Key Functions**:
  - `process_file_enhanced()`: Main file processing pipeline
  - `write_chunk_files()`: Writes chunks with deduplication checks
  - `get_department_config()`: Domain-aware department detection
  - `quarantine_failed_file()`: Moves failed files to `03_archive/failed`
  - `process_with_retries()`: Retries failed processing (3 attempts)
  - `is_effectively_stable()`: Skips stability checks for old files (>10 minutes)
  - `_process_batch_multiproc()`: Multiprocessing batch processing with fallback
- **Key Features**:
  - Batch processing (100 files per cycle)
  - Stability skip optimization
  - File-level deduplication (streaming hash comparison)
  - Long path handling (Windows MAX_PATH)
  - Conflict resolution (version suffixes)
  - Auto-archival of old outputs

### `reprocess_output.py`
- **Purpose**: Reprocesses archived files with enhanced tagging
- **Key Functions**:
  - `reprocess_session()`: Reprocesses a single session
  - `get_original_text()`: Reconstructs full transcript from chunks
  - `is_already_reprocessed()`: Checks markers and sidecars to avoid duplicates
- **Usage**: `python reprocess_output.py --execute` (remove `--dry-run` from config first)

### `migrate_to_onedrive.py`
- **Purpose**: Migrates local archives to OneDrive
- **Key Features**: MAX_PATH handling, conflict resolution, atomic moves

### `metadata_enrichment.py`
- **Purpose**: Tag generation and metadata enrichment
- **Key Features**:
  - Regex-based tag patterns (60+ categories)
  - Keyword extraction
  - Summary generation
  - Source metadata tracking

## Processing Workflow

1. **File Placement**: Files added to `C:\_chunker\02_data` (via Send To or manual copy)
2. **Manifest Creation**: `.origin.json` manifest created (if using Send To script)
3. **Watcher Detection**: `watcher_splitter.py` polls directory every 5 seconds
4. **Stability Check**: 
   - Files >10 minutes old → treated as stable (skip expensive check)
   - Files <10 minutes old → full stability check
5. **Batch Processing**: Up to 100 files per cycle (configurable)
6. **Parallel Processing**: 
   - Default: ThreadPoolExecutor (8 workers)
   - Optional: Multiprocessing pool (with fallback to sequential on errors)
7. **File Processing**:
   - Read file content
   - Extract text (handles multiple file types)
   - Determine department (domain-aware detection)
   - Generate chunks (department-specific sizes)
   - Enrich metadata (tags, keywords, summaries)
   - Write chunks to OneDrive `04_output/{session_folder}/`
   - Create sidecar JSON with metadata
   - Move original to OneDrive `03_archive/{department}/`
8. **Deduplication**: 
   - File-level: Streaming hash comparison against existing chunks
   - Content-level: ChromaDB duplicate detection
9. **Error Handling**: 
   - 3 retry attempts with exponential backoff
   - Failed files moved to `03_archive/failed/`
   - Database logging of errors

## Known Issues and Findings

### Failed Files (Historical)
- **4,432 files** in `C:\_chunker\03_archive\failed` from August-October 2025
- These are **reprocess files** (all have "reprocess" in filename)
- They failed during previous processing attempts, before recent code updates
- **No action needed** for current processing (they're correctly quarantined)
- **Optional**: Review and manually reprocess if needed

### Configuration Inconsistency
- `failed_dir` in `watcher_splitter.py` defaults to `"03_archive/failed"` (relative path)
- This resolves to `C:\_chunker\03_archive\failed` instead of OneDrive path
- **Recommendation**: Update config.json to explicitly set `failed_dir` to OneDrive path if desired

### Orphaned Manifest Files
- Previously had 4,487 orphaned `.origin.json` files in `02_data`
- These were cleaned up (deleted) as they had no corresponding source files
- Future: Consider cleanup script or watcher enhancement to prevent accumulation

## Performance Metrics

### Recent Performance (v2.1.9)
- **6,500 files**: ~53 minutes (with batch processing and stability skip)
- **Previous**: ~3.5 hours for same workload
- **Improvement**: 90% faster

### Processing Throughput
- **Normal operation**: 100-200 chunks/second
- **Batch size**: 100 files per cycle (default)
- **Parallel workers**: 8 (threads) or configurable multiprocessing

## Important Code Sections

### Stability Skip (Performance Optimization)
```python
def is_effectively_stable(path: Path, config: dict) -> bool:
    """Skip expensive stability checks for old files."""
    skip_minutes = config.get("stability_skip_minutes", 10)
    age_min = _age_minutes(path)
    if age_min > skip_minutes:
        return True  # Old file → assume settled
    # Fall back to original stability check for recent files
    stability_timeout = config.get("file_stability_timeout", 2)
    return file_is_settled(path, seconds=stability_timeout)
```

### File-Level Deduplication
```python
def check_file_exists_and_compare(content: str, file_path: Path) -> Tuple[bool, bool]:
    """Streaming hash comparison to prevent OOM errors."""
    # Fast path: check file size first
    if file_path.exists() and file_path.stat().st_size != len(content.encode('utf-8')):
        return True, False  # Different sizes → different content
    # Streaming hash comparison
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    existing_hash = file_hash(file_path)  # Streaming read
    return True, new_hash == existing_hash
```

### Department Detection (Domain-Aware)
```python
def get_department_config(file_path):
    """Multi-source detection: file extension → filename → metadata tags."""
    # Priority 1: File extension match
    # Priority 2: Filename/path keywords
    # Priority 3: Metadata tags from sidecar
    # Returns department-specific config with chunk_size, redaction, audit_level, priority
```

## Next Steps / Areas for Improvement

### Immediate (Optional)
1. **Review Failed Files**: Investigate why 4,432 files failed (historical - not blocking)
2. **Configure Failed Directory**: Update `failed_dir` in config.json to use OneDrive path if desired
3. **Reprocess Failed Files**: Optionally reprocess with updated `watcher_splitter.py`

### Future Enhancements
1. **Automated Failed File Review**: Script to analyze failed files and suggest fixes
2. **Better Failed File Organization**: Organize failed files by failure reason/date
3. **Performance Monitoring Dashboard**: Real-time metrics visualization
4. **Enhanced Error Recovery**: Automatic retry with different settings for specific failure types

## Testing and Validation

### How to Test Watcher
```bash
# Start watcher
python watcher_splitter.py

# Check logs
Get-Content logs\watcher.log -Wait | Select-String -Pattern "ERROR|Failed|Successfully processed"

# Verify processing
# Files should appear in OneDrive 04_output/{session_folder}/
# Originals should move to OneDrive 03_archive/{department}/
```

### How to Test Reprocessing
```bash
# Edit reprocess_config.json: Set "dry_run": false
python reprocess_output.py --execute

# Check markers
ls C:\_chunker\02_data\.reprocessed_sources\
```

## Support Files and Documentation

- **README.md**: Comprehensive documentation with usage examples
- **SUMMARY.md**: Project overview and key points
- **CHANGELOG.md**: Detailed version history
- **MONITOR_DB_LOCKS.md**: Database lock monitoring documentation

## Environment Variables

- `%OneDriveCommercial%`: Resolves to `C:\Users\carucci_r\OneDrive - City of Hackensack`
- Used in config.json for OneDrive paths

## Key Technologies

- **Python 3.13**: Core runtime
- **ChromaDB 1.3.4**: Vector database for RAG
- **NLTK**: Natural language processing
- **psutil**: System resource monitoring
- **multiprocessing**: Parallel processing support
- **watchdog**: File system monitoring (optional)

---

## Questions to Address

1. Should failed files be moved to OneDrive failed directory?
2. Should we investigate why the 4,432 files failed originally?
3. Should we create a script to automatically reprocess failed files with updated code?
4. Any specific performance optimizations needed?
5. Are there any new file types or processing requirements?

---

**Last Updated**: 2025-11-19 20:56 EST  
**Status**: ✅ System operational, processing correctly, 0 errors in current logs

