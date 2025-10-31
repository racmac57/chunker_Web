# Enterprise Chunker System - Summary & Cheat Sheet

**Version 2.1.2** - Critical Performance Optimizations & Loop Fix

## 🚀 Quick Start Guide

### 1. Start the System
```bash
# Start the watcher (monitors 02_data for new files)
python watcher_splitter.py
```

### 2. Process Files
- **Input**: Drop files into `02_data/` directory
- **Output**: Processed files appear in `04_output/` with timestamp prefixes
- **Archive**: Original files moved to `03_archive/admin/` after processing
- **Logs**: Check `logs/watcher.log` for processing details

---

## 📁 File Structure & Flow

### Directory Organization
```
C:\_chunker\
├── 02_data/          # 📥 INPUT: Place files to be processed here
├── 03_archive/       # 📦 ARCHIVE: Organized by status
│   ├── failed/       # Files that couldn't be read
│   ├── skipped/      # Files too short to process
│   └── no_chunks/    # Files with no valid chunks
├── 04_output/        # 📤 OUTPUT: Processed chunks and transcripts
├── 05_logs/          # 📋 LOGS: System logs and error tracking
├── 06_config/        # ⚙️ CONFIG: Configuration files
├── source/           # 📂 SOURCE: Copied processed files (configurable)
├── templates/        # 🌐 WEB: HTML templates for dashboard
├── static/           # 🎨 WEB: CSS, JS, and assets
└── logs/             # 📊 LOGS: Watcher and processing logs
```

### Consolidation Notes (2025-10-29)
- Unified older iterations under `C:\_chunker`.
- Legacy snapshots (latest only) per project live in:
  - `99_doc\legacy\<Project>_<timestamp>`
  - `06_config\legacy\<Project>_<timestamp>`
  - `05_logs\legacy\<Project>_<timestamp>`
  - `03_archive\legacy\<Project>_<timestamp>`
- Historical outputs migrated to `04_output\<Project>_<timestamp>`.
- Timestamp‑prefixed script backups: `C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\backup_scripts\<Project>\`.

### JSON Sidecar Feature
- Enabled by default via `enable_json_sidecar` in `config.json`.
- For every processed file, a sidecar `<timestamp>_<base>_blocks.json` is written in the output folder containing:
  - file metadata, transcript path, chunk list
  - for Python files: `code_blocks` with class/function spans and signatures
- If `enable_block_summary` is true, Python transcripts append a “Code Blocks Summary” section.

### Watcher Discovery & Defaults (2025-10-30)
- Case-insensitive extension matching and clearer include/exclude logging
- Startup logs show Celery availability; default `celery_enabled: false` for direct processing
- When enabled, sidecar is also copied to `source/` (`copy_sidecar_to_source: true`)

### SendTo Integration & Origin Manifests
- Optional Windows SendTo helper drops files/folders into `02_data` and writes `<file>.origin.json`
- Manifest fields: original_full_path, original_directory, original_filename, sent_at, integrity (sha256, size, mtime, ctime), optional hmac_sha256
- Watcher loads manifest if present and sets sidecar.origin accordingly; falls back if absent or invalid

### File Processing Flow
1. **Input**: Files placed in `02_data/`
2. **Processing**: System chunks and processes files with dynamic parallel workers
3. **Archive**: Originals moved to `03_archive/` (organized by status)
4. **Output**: Results saved to `04_output/`
5. **Source Copy**: Optional copying back to source folder

---

## ⚡ Performance Features (v2.1.2)

### 🚨 Critical Fixes
- ✅ **No More Processing Loops**: Failed files automatically archived
- ✅ **Database Stability**: Batch operations eliminate locking issues
- ✅ **Smart File Management**: Organized archive folders by failure type
- ✅ **8-12x Speed Improvement**: Dynamic parallel processing

### 🚀 Performance Enhancements
- ✅ **Dynamic Workers**: Up to 12 workers for large batches (50+ files)
- ✅ **Batch Processing**: Configurable batch sizes with system protection
- ✅ **Real-time Metrics**: Files/minute, avg processing time, peak CPU/memory
- ✅ **500+ File Capability**: Handles large volumes efficiently
- ✅ **Source Folder Copying**: Configurable copying of processed files

---

## 🎯 Core Features

### Web Dashboard Features
- ✅ **Real-time Monitoring**: Live system stats (CPU, Memory, Disk)
- ✅ **File Upload**: Drag & drop interface for batch processing
- ✅ **Processing Queue**: View and manage active jobs
- ✅ **Analytics**: Processing statistics and trends
- ✅ **Settings Management**: Web-based configuration
- ✅ **File Browser**: Download processed results

### Processing Capabilities
- ✅ **Smart Chunking**: NLTK-based intelligent text splitting
- ✅ **Department Filtering**: Configurable file filtering modes
- ✅ **Parallel Processing**: Multi-threaded file handling
- ✅ **Error Recovery**: Automatic retry and logging
- ✅ **Notifications**: Email alerts for errors/completion

---

## 🔧 Configuration

### Key Settings (`config.json`)
```json
{
  "watch_folder": "02_data",
  "output_dir": "04_output", 
  "archive_dir": "03_archive",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "filter_mode": "all",
  "parallel_workers": 4,
  "notification_email": "your-email@domain.com"
}
```

### Filter Modes
- `"all"`: Process all files
- `"txt_only"`: Process only .txt files
- `"md_only"`: Process only .md files
- `"custom"`: Use custom file extensions

---

## 🌐 Web Dashboard Navigation

### Main Pages
1. **Dashboard** (`/`): System overview and real-time stats
2. **Upload** (`/upload`): File upload interface
3. **Files** (`/files`): Browse processed results
4. **Analytics** (`/analytics`): Processing statistics
5. **Settings** (`/settings`): System configuration

### Key Dashboard Elements
- **System Status Cards**: CPU, Memory, Disk usage
- **Processing Queue**: Active jobs and progress
- **Recent Activity**: Latest processing events
- **System Alerts**: Error notifications and warnings

---

## 📊 API Endpoints

### System Information
- `GET /api/health` - System health check
- `GET /api/stats` - Real-time system statistics
- `GET /api/queue` - Processing queue status

### File Operations
- `POST /api/upload` - Upload files for processing
- `GET /api/files` - List processed files
- `GET /api/download/<filename>/<file_type>` - Download results

### Analytics
- `GET /api/analytics` - Processing statistics
- `GET /api/analytics/departments` - Department-specific stats
- `GET /api/analytics/errors` - Error history

### Configuration
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings
- `POST /api/settings/test` - Test notification settings

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. Dashboard Won't Start
```bash
# Check Python version (requires 3.8+)
python --version

# Install dependencies
pip install -r requirements.txt

# Check if port 5000 is available
netstat -ano | findstr :5000
```

#### 2. Files Not Processing
- ✅ Check `02_data/` folder exists
- ✅ Verify file permissions
- ✅ Check `config.json` settings
- ✅ Review logs in `05_logs/` or `logs/`

#### 3. Database Issues
```bash
# Check database file
dir chunker_tracking.db

# Reset database (if corrupted)
del chunker_tracking.db
python web_dashboard.py  # Will recreate database
```

#### 4. Notification Problems
- ✅ Verify email settings in `config.json`
- ✅ Check internet connection
- ✅ Test notifications via dashboard settings page

---

## 📈 Performance Optimization

### Recommended Settings
```json
{
  "parallel_workers": 4,        // Adjust based on CPU cores
  "chunk_size": 1000,           // Optimal for most documents
  "chunk_overlap": 200,         // 20% overlap for context
  "max_file_size": 10485760     // 10MB limit
}
```

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: Multi-core processor
- **Storage**: Sufficient space for processed files
- **Network**: For email notifications

---

## 🔄 Migration from Old System

### File Locations
- **Old**: Files processed to `admin/` folder
- **New**: Files processed to `04_output/` folder
- **Archive**: Originals moved to `03_archive/`

### Configuration Migration
1. Copy old `config.json` settings
2. Update paths to new directory structure
3. Test with small files first

---

## 📋 Daily Operations

### Starting the System
```bash
cd C:\_chunker
python start_dashboard.py
```

### Monitoring
1. Open http://localhost:5000
2. Check system status cards
3. Monitor processing queue
4. Review recent activity

### File Processing
1. Place files in `02_data/`
2. Watch dashboard for processing status
3. Download results from `Files` page
4. Check `Analytics` for processing trends

### Maintenance
- **Weekly**: Review logs in `05_logs/`
- **Monthly**: Clean old database entries
- **As Needed**: Update configuration via dashboard

---

## 🚨 Emergency Procedures

### System Crash Recovery
```bash
# 1. Stop any running processes
taskkill /f /im python.exe

# 2. Check for corrupted files
dir 02_data\
dir 04_output\

# 3. Restart system
python start_dashboard.py
```

### Data Recovery
- **Original files**: Check `03_archive/`
- **Processed files**: Check `04_output/`
- **Database**: `chunker_tracking.db` contains processing history

---

## 📞 Support Information

### Log Files
- **System Logs**: `05_logs/` directory
- **Watcher Logs**: `logs/watcher.log`
- **Database**: `chunker_tracking.db`

### Key Files
- **Main Dashboard**: `web_dashboard.py`
- **Processing Engine**: `watcher_splitter.py`
- **Database**: `chunker_db.py`
- **Configuration**: `config.json`
- **Startup Script**: `start_dashboard.py`

### Version Information
- **System**: Enterprise Chunker v2.0
- **Web Dashboard**: Flask-based interface
- **Database**: SQLite with analytics
- **Processing**: NLTK-powered intelligent chunking

---

## 🎯 Quick Commands Reference

```bash
# Start system
python start_dashboard.py

# Check system status
netstat -ano | findstr :5000

# View logs
type logs\watcher.log

# Check database
python -c "import sqlite3; print(sqlite3.connect('chunker_tracking.db').execute('SELECT COUNT(*) FROM processing_history').fetchone()[0])"

# Reset system (emergency)
taskkill /f /im python.exe && python start_dashboard.py
```

---

*Last Updated: January 2025*
*System Version: Enterprise Chunker v2.0*


## 🔄 Version Control & Backup

### Git Repository
- **Repository**: Initialized and active
- **Remote**: `https://github.com/racmac57/chunker_Web.git`
- **Branch**: `main`
- **Status**: ✅ Connected and regularly backed up

### Git Workflow
```bash
# Regular backup
git add -A
git commit -m "Backup: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin main
```

### Excluded from Git
- Processed documents (`99_doc/`, `04_output/`)
- Archived files (`03_archive/`)
- Database files (`*.db`, `*.sqlite`)
- Log files (`logs/`, `*.log`)
- Virtual environments (`.venv/`, `venv/`)

For complete Git setup details, see `GIT_SETUP_STATUS.md`.

## Documentation Locations

- **Root Documentation:** README.md, CHANGELOG.md, ENTERPRISE_CHUNKER_SUMMARY.md, GIT_SETUP_STATUS.md
- **Additional Docs:** `99_doc/` - All supporting documentation and notes
- **Notes & Transcripts:** `99_doc/notes/` - Conversation transcripts and analysis notes
- **Maintenance Logs:** `05_logs/maintenance/` - Directory cleanup and health reports

## Snapshot Policy

Legacy snapshots are stored in `**/legacy/` folders and follow a naming convention of `ProjectName_YYYY_MM_DD_HH_MM_SS`. 

**Policy:** Only the latest snapshot per project is retained. Older snapshots are automatically pruned during directory maintenance.

**Config Backups:** Files matching `config.json.backup_*` follow the same policy - only the most recent backup is kept.
