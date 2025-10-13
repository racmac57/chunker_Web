# 🚀 Enterprise Chunker - Quick Reference

## ⚡ Start System
```bash
python start_dashboard.py
```
**Access**: http://localhost:5000

## 📁 File Flow
```
02_data/ → [PROCESSING] → 04_output/ (results)
                ↓
            03_archive/ (originals)
```

## 🎯 Key Commands

### Start/Stop
```bash
# Start system
python start_dashboard.py

# Check if running
netstat -ano | findstr :5000

# Force stop
taskkill /f /im python.exe
```

### Troubleshooting
```bash
# Check logs
type logs\watcher.log

# Reset database
del chunker_tracking.db && python web_dashboard.py

# Check dependencies
pip install -r requirements.txt
```

## 🌐 Dashboard Pages
- **Dashboard** (`/`) - System overview
- **Upload** (`/upload`) - File upload
- **Files** (`/files`) - Download results
- **Analytics** (`/analytics`) - Statistics
- **Settings** (`/settings`) - Configuration

## ⚙️ Quick Settings
```json
{
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "parallel_workers": 4,
  "filter_mode": "all"
}
```

## 🚨 Emergency
1. **System won't start**: Check Python version (3.8+)
2. **Files not processing**: Verify `02_data/` folder exists
3. **Dashboard error**: Check port 5000 availability
4. **Database issues**: Delete `chunker_tracking.db` and restart

## 📊 Monitor
- **CPU/Memory/Disk**: Dashboard status cards
- **Processing Queue**: Real-time job status
- **Recent Activity**: Latest processing events
- **System Alerts**: Error notifications

## 📞 Support Files
- **Logs**: `05_logs/` and `logs/watcher.log`
- **Config**: `config.json`
- **Database**: `chunker_tracking.db`
- **Main Script**: `web_dashboard.py`

---
*Quick Reference v2.0 - Enterprise Chunker System*
