# 🏢 Enterprise Chunker System - Enhanced Edition

A comprehensive document processing and chunking system with web dashboard, real-time monitoring, and enterprise-grade features.

## 🚀 Quick Start

### 1. Start the Web Dashboard
```bash
python start_dashboard.py
```

### 2. Access the Dashboard
Open your browser and go to: **http://localhost:5000**

### 3. Upload and Process Files
- Use the web interface to upload files
- Monitor processing in real-time
- Download processed chunks and transcripts

## ✨ New Features

### 🌐 Web Dashboard
- **Real-time monitoring** of system status and processing queue
- **Drag-and-drop file upload** with batch processing
- **Live progress tracking** with WebSocket updates
- **Interactive charts** and analytics
- **File management** with download capabilities
- **Settings management** through web interface

### 📊 Enhanced Analytics
- **Processing statistics** with visual charts
- **Department-based analytics** and reporting
- **Error tracking** and system alerts
- **Performance metrics** and optimization insights

### 🔧 Advanced Configuration
- **Web-based settings** management
- **Real-time configuration** updates
- **Validation and testing** of settings
- **Default configuration** restoration

### 📁 Improved File Management
- **Organized output structure** by source file
- **Batch download** capabilities (ZIP files)
- **File preview** and metadata display
- **Processing history** and status tracking

## 📋 System Requirements

- **Python 3.7+**
- **Windows 10/11** (tested on Windows)
- **4GB RAM** (recommended)
- **500MB disk space**

## 🛠️ Installation

### Automatic Installation
The startup script will automatically:
1. Check Python version
2. Install required dependencies
3. Create necessary directories
4. Set up default configuration
5. Start the web dashboard

```bash
python start_dashboard.py
```

### Manual Installation
If you prefer manual installation:

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Create Directories**
```bash
mkdir -p 02_data 03_archive 04_output 05_logs 06_config templates static/css static/js
```

3. **Start Dashboard**
```bash
python web_dashboard.py
```

## 📁 Directory Structure

```
C:/_chunker/
├── 02_data/              # Input files to be processed
├── 03_archive/           # Archived original files (by department)
├── 04_output/            # Processed chunks and transcripts
├── 05_logs/              # System logs
├── 06_config/            # Configuration files
├── templates/            # Web dashboard templates
├── static/               # Web assets (CSS, JS)
├── web_dashboard.py      # Main web dashboard
├── watcher_splitter.py   # Core processing engine
├── chunker_db.py         # Database management
├── notification_system.py # Email notifications
├── config.json           # System configuration
└── start_dashboard.py    # Startup script
```

## 🌐 Web Dashboard Features

### 📊 Dashboard Page
- **System Status Cards**: CPU, Memory, Disk, Active Jobs
- **Processing Queue**: Real-time queue management
- **Live Charts**: Processing statistics visualization
- **Recent Activity**: System activity feed
- **System Alerts**: Error and warning notifications

### 📤 Upload Page
- **Drag-and-Drop**: Easy file upload interface
- **Batch Upload**: Process multiple files at once
- **File Validation**: Automatic file type checking
- **Progress Tracking**: Real-time upload progress
- **Supported Formats**: .txt, .md, .json, .csv

### 📁 Files Page
- **File Browser**: Browse processed files
- **Download Options**: Individual files or batch downloads
- **File Metadata**: Size, creation date, chunk count
- **Search and Filter**: Find specific files quickly

### 📈 Analytics Page
- **Processing Statistics**: Success rates, processing times
- **Department Breakdown**: Performance by department
- **Error Analysis**: Common error patterns
- **Trend Charts**: Processing over time

### ⚙️ Settings Page
- **File Processing**: Chunk size, overlap, limits
- **File Filtering**: Pattern matching and exclusions
- **Performance**: Parallel workers, polling intervals
- **Directories**: Watch, output, and archive folders
- **Notifications**: Email settings and alerts
- **System**: Logging and maintenance settings

## 🔧 API Endpoints

### Health and Status
- `GET /api/health` - System health check
- `GET /api/stats` - System statistics
- `GET /api/queue` - Processing queue status

### File Management
- `POST /api/upload` - Upload file for processing
- `GET /api/files` - List processed files
- `GET /api/download/<filename>/<type>` - Download files
- `POST /api/process/<job_id>` - Process specific job

### Analytics
- `GET /api/analytics` - Processing analytics
- `GET /api/analytics/departments` - Department statistics
- `GET /api/analytics/errors` - Error reports

### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings
- `POST /api/settings/test` - Test configuration

## 📊 Configuration

### File Processing Settings
```json
{
  "chunk_size": 800,
  "overlap": 50,
  "min_chunk_size": 100,
  "max_chunk_size": 1500
}
```

### File Filtering
```json
{
  "file_filter_mode": "all",
  "file_patterns": ["_full_conversation", "_conversation", "_chat"],
  "exclude_patterns": ["_draft", "_temp", "_backup"]
}
```

### Performance Settings
```json
{
  "parallel_workers": 4,
  "polling_interval": 5
}
```

## 🔄 Processing Workflow

1. **File Upload**: Files uploaded via web interface or placed in `02_data/`
2. **Queue Management**: Files added to processing queue with priority
3. **Processing**: Files processed in parallel with real-time progress
4. **Output Generation**: Chunks and transcripts created in `04_output/`
5. **Archive**: Original files moved to `03_archive/{department}/`
6. **Notification**: Completion notifications sent (if enabled)

## 📈 Performance Features

### Parallel Processing
- **Multi-threaded processing** for faster file handling
- **Configurable worker count** based on system resources
- **Queue management** with priority levels

### Real-time Monitoring
- **WebSocket connections** for live updates
- **System resource monitoring** (CPU, Memory, Disk)
- **Processing queue visualization**

### Error Handling
- **Automatic retry mechanisms** for failed processing
- **Error categorization** and reporting
- **Graceful degradation** when services unavailable

## 🔒 Security Features

### File Validation
- **File type checking** before processing
- **Size limits** to prevent resource exhaustion
- **Content validation** for processing safety

### Access Control
- **Local network access** by default
- **Configurable host binding** for security
- **Input sanitization** for all user inputs

## 🚨 Troubleshooting

### Common Issues

**Dashboard won't start:**
- Check Python version (3.7+ required)
- Verify all dependencies are installed
- Check if port 5000 is available

**Files not processing:**
- Verify file types are supported
- Check file naming patterns
- Review log files in `05_logs/`

**Upload failures:**
- Check file size limits (100MB default)
- Verify file permissions
- Ensure disk space is available

### Log Files
- **Application logs**: `05_logs/watcher.log`
- **Web dashboard logs**: Console output
- **Database logs**: `chunker_tracking.db`

### Debug Mode
Enable debug mode for detailed logging:
```bash
python web_dashboard.py --debug
```

## 🔄 Migration from Old System

### File Locations
- **Old**: Files went to `admin/` folder
- **New**: Files organized in `04_output/{filename}/`

### Configuration
- **Old**: Hard-coded settings
- **New**: Web-based configuration management

### Processing
- **Old**: Command-line only
- **New**: Web interface with real-time monitoring

## 📞 Support

### Getting Help
1. Check the troubleshooting section
2. Review log files for error details
3. Verify configuration settings
4. Test with sample files

### Reporting Issues
Include the following information:
- Python version
- Operating system
- Error messages from logs
- Steps to reproduce the issue

## 🔮 Future Enhancements

### Planned Features
- **Cloud storage integration** (AWS S3, Google Cloud)
- **Advanced analytics** with machine learning
- **API rate limiting** and authentication
- **Mobile-responsive** interface
- **Multi-language support**

### Performance Improvements
- **Database optimization** for large datasets
- **Caching layer** for faster responses
- **Background job processing** with Redis
- **Horizontal scaling** support

## 📄 License

This project is proprietary software. All rights reserved.

---

**Enterprise Chunker System v2.0** - Enhanced with Web Dashboard and Real-time Monitoring
