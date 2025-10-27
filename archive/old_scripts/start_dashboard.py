#!/usr/bin/env python3
# 🕒 2025-08-25-19-30-00
# start_dashboard.py
# Author: R. A. Carucci  
# Purpose: Startup script for Enterprise Chunker Web Dashboard

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        "Flask==2.3.3",
        "Flask-SocketIO==5.3.6",
        "python-socketio==5.8.0",
        "python-engineio==4.7.1",
        "psutil==5.9.5",
        "Werkzeug==2.3.7"
    ]
    
    print("🔍 Checking dependencies...")
    
    for package in required_packages:
        package_name = package.split("==")[0]
        try:
            importlib.import_module(package_name.lower().replace("-", "_"))
            print(f"✅ {package_name} already installed")
        except ImportError:
            print(f"📦 Installing {package_name}...")
            if install_package(package):
                print(f"✅ {package_name} installed successfully")
            else:
                print(f"❌ Failed to install {package_name}")
                return False
    
    return True

def check_directories():
    """Check and create necessary directories"""
    directories = [
        "02_data",
        "03_archive", 
        "04_output",
        "05_logs",
        "06_config",
        "templates",
        "static/css",
        "static/js"
    ]
    
    print("📁 Checking directories...")
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def check_config():
    """Check if config.json exists and create default if needed"""
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("📝 Creating default config.json...")
        default_config = {
            "watch_folder": "C:/_chunker/02_data",
            "output_dir": "C:/_chunker/04_output",
            "archive_dir": "C:/_chunker/03_archive",
            "supported_extensions": [".txt", ".md", ".json", ".csv"],
            "chunk_size": 800,
            "overlap": 50,
            "min_chunk_size": 100,
            "max_chunk_size": 1500,
            "file_filter_mode": "all",
            "file_patterns": ["_full_conversation", "_conversation", "_chat"],
            "exclude_patterns": ["_draft", "_temp", "_backup"],
            "parallel_workers": 4,
            "database_enabled": True,
            "notification_enabled": False,
            "cloud_repo_root": None,
            "log_level": "INFO",
            "log_rotation": True,
            "max_log_size": 5242880,
            "backup_count": 3,
            "session_cleanup_interval": 3600,
            "summary_auto_generate": False,
            "summary_min_chunks": 5
        }
        
        import json
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print("✅ Created default config.json")
    else:
        print("✅ config.json exists")

def check_existing_files():
    """Check if required files exist"""
    required_files = [
        "web_dashboard.py",
        "chunker_db.py", 
        "notification_system.py",
        "watcher_splitter.py"
    ]
    
    print("📄 Checking required files...")
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            missing_files.append(file)
            print(f"❌ {file} missing")
    
    if missing_files:
        print(f"\n⚠️  Warning: Missing files: {', '.join(missing_files)}")
        print("Some features may not work properly.")
        return False
    
    return True

def start_dashboard():
    """Start the web dashboard"""
    print("\n🚀 Starting Enterprise Chunker Web Dashboard...")
    print("=" * 50)
    
    try:
        # Import and run the dashboard
        from web_dashboard import app, socketio
        
        print("✅ Dashboard imported successfully")
        print(f"📊 Dashboard: http://localhost:5000")
        print(f"🔧 API Base: http://localhost:5000/api")
        print(f"📁 Watch Folder: {app.config.get('WATCH_FOLDER', '02_data')}")
        print(f"📤 Output Folder: {app.config.get('OUTPUT_DIR', '04_output')}")
        print("\n💡 Tips:")
        print("   - Use Ctrl+C to stop the dashboard")
        print("   - Check the logs for any errors")
        print("   - Upload files through the web interface")
        print("=" * 50)
        
        # Start the dashboard
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("Make sure all required files are present.")
        return False
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False

def main():
    """Main startup function"""
    print("🏢 Enterprise Chunker Web Dashboard Startup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Check directories
    check_directories()
    
    # Check config
    check_config()
    
    # Check existing files
    if not check_existing_files():
        print("⚠️  Some files are missing, but continuing...")
    
    # Start dashboard
    return start_dashboard()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
