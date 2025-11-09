# Complete Transcript: README.md

**Generated:** 2025-08-14T17:29:20.778667
**Department:** default

## Chunk 1

# 🤖 AI Chat Log Chunker System

[! [Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[! [Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[! [Status](https://img.shields.io/badge/status-Production%20Ready-green.svg)](#)
[! [Zero-Byte Prevention](https://img.shields.io/badge/zero--byte-prevented-success.svg)](#)

A robust, production-ready system for automatically processing AI chat transcripts into manageable chunks with comprehensive error handling, cloud synchronization, and zero-byte prevention. ## 🎯 **Key Features**

- **🛡️ Zero-Byte Prevention**: Multi-layer validation prevents empty chunk files
- **📊 Auto Log Rotation**: Intelligent log management with size-based rotation
- **☁️ Cloud Sync**: Automatic OneDrive/SharePoint integration
- **🔄 File Stability**: Smart detection of complete file writes
- **📈 Session Analytics**: Detailed processing metrics and error tracking
- **🎭 Background Operation**: Runs silently as Windows service
- **💻 PowerShell Dashboard**: Real-time monitoring and system diagnostics

## 📁 **Project Structure**

```
new_chunker_project/
├── 🐍 watcher_splitter.py          # Core processing engine
├── ⚙️ config.json                  # System configuration
├── 💻 test_chunker.ps1             # PowerShell control interface
├── 🔧 setup_chunker_environment.py # New system setup script
├── 📦 chunker_hidden.spec          # Executable build spec
├── 🚀 build_and_run.bat           # One-click build/launch
├── 🤫 launch_chunker.vbs          # Silent startup launcher
├── 📤 output/                     # Generated chunk files
├── 📁 processed/                  # Archived original files
├── 📋 logs/                      # System logs with rotation
└── 🏗️ dist/                      # Built executables
```

## 🚀 **Quick Start Guide**

### **Option 1: New System (Recommended)**
```powershell
# 1. Run automated setup:
python setup_chunker_environment.py

# 2. Test the system:
.\test_chunker.ps1 -CreateTest -RunChunker

# 3. Monitor in real-time:
.\test_chunker.ps1 -MonitorOnly
```

### **Option 2: Quick Deploy**
```powershell
# 1. Create test and start chunker:
.\test_chunker.ps1 -CreateTest -RunChunker

# 2. Check results:
.\test_chunker.ps1 -CheckResults
```

## ⚙️ **Configuration**

Edit `config.json` to customize system behavior:

| Setting | Default | Purpose |
|---------|---------|---------|
| `chunk_size` | `100` | Maximum sentences per chunk |
| `max_chunk_chars` | `30000` | Character limit per chunk |
| `file_stability_debounce` | `2` | Seconds to wait for file stability |
| `cloud_repo_root` | OneDrive path | Cloud synchronization destination |
| `enable_notifications` | `true` | System notifications |
| `log_rotation_size_mb` | `5` | Auto-rotate logs after 5MB |

## 🔧 **System Requirements**

- Python 3.7+
- Windows 10/11
- OneDrive/SharePoint access (for cloud sync)
- 100MB free disk space
- PowerShell 5.0+

## 📋 **Installation Steps**

1. **Clone/Download** the project files
2. **Run Setup**: `python setup_chunker_environment.py`
3. **Configure**: Edit `config.json` for your environment
4. **Test**: Run `.\test_chunker.ps1 -CreateTest -RunChunker`
5. **Monitor**: Use `.\test_chunker.ps1 -MonitorOnly` for real-time monitoring

## 🛡️ **Security Features**

- **Encryption**: Fernet symmetric encryption for sensitive data
- **Audit Trail**: Comprehensive logging of all operations
- **Access Control**: Role-based permissions
- **Data Integrity**: Hash verification for file integrity
- **Compliance**: GDPR/CCPA ready with data redaction

## 📊 **Monitoring & Analytics**

- **Real-time Dashboard**: PowerShell-based monitoring interface
- **Performance Metrics**: CPU, memory, disk usage tracking
- **Error Analytics**: Detailed error reporting and resolution
- **Processing Statistics**: Files processed, chunks created, success rates

## 🔄 **Workflow**

1. **File Detection**: System watches designated folder for new files
2. **Stability Check**: Waits for file to be completely written
3. **Processing**: Chunks transcript into manageable segments
4. **Validation**: Ensures no zero-byte files are created
5. **Output Generation**: Creates cleaned transcripts, summaries, metadata
6. **Cloud Sync**: Uploads to OneDrive/SharePoint
7. **Archival**: Moves original files to processed folder
8. **Logging**: Records all activities in database

## 🚨 **Troubleshooting**

### Common Issues:
- **Zero-byte files**: Check file permissions and stability settings
- **Cloud sync failures**: Verify OneDrive credentials and network access
- **Memory issues**: Adjust chunk size in config.json
- **Log rotation**: Check disk space and log retention settings

### Support:
- Check logs in `logs/watcher.log`
- Run diagnostics: `.\test_chunker.ps1 -Diagnostics`
- Review database: `chunker_tracking.db`

## 📄 **License**

This project is developed for internal use by the City of Hackensack.

---

