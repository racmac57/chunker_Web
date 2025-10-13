# 🕒 2025-08-25-19-15-00
# web_dashboard.py
# Author: R. A. Carucci  
# Purpose: Comprehensive web dashboard and API for enterprise chunker system

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import sqlite3
import psutil
import queue
import uuid
from concurrent.futures import ThreadPoolExecutor
import traceback

# Import existing chunker modules
from chunker_db import ChunkerDatabase
from notification_system import NotificationSystem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chunker-enterprise-2025'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
processing_queue = queue.Queue()
active_processes = {}
system_stats = {
    'cpu_percent': 0,
    'memory_percent': 0,
    'disk_percent': 0,
    'active_processes': 0
}

# Initialize systems
try:
    db = ChunkerDatabase()
    notifications = NotificationSystem()
except Exception as e:
    print(f"Failed to initialize systems: {e}")
    db = None
    notifications = None

# Load configuration
try:
    with open("config.json") as f:
        CONFIG = json.load(f)
except Exception as e:
    print(f"Failed to load config: {e}")
    CONFIG = {}

# File processing queue management
class ProcessingQueue:
    def __init__(self):
        self.queue = []
        self.processing = []
        self.completed = []
        self.failed = []
        self.max_workers = CONFIG.get('parallel_workers', 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    def add_file(self, file_path, priority=1):
        """Add file to processing queue"""
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'file_path': file_path,
            'filename': Path(file_path).name,
            'priority': priority,
            'status': 'queued',
            'progress': 0,
            'started_at': None,
            'completed_at': None,
            'error': None,
            'chunks_created': 0,
            'processing_time': 0
        }
        self.queue.append(job)
        self.queue.sort(key=lambda x: x['priority'], reverse=True)
        return job_id
    
    def get_next_job(self):
        """Get next job from queue"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def update_job_status(self, job_id, status, progress=0, error=None):
        """Update job status"""
        for job in self.queue + self.processing:
            if job['id'] == job_id:
                job['status'] = status
                job['progress'] = progress
                if error:
                    job['error'] = error
                break

# Initialize processing queue
processing_queue_manager = ProcessingQueue()

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to Chunker Dashboard'})

@socketio.on('request_stats')
def handle_stats_request():
    emit('stats_update', get_system_stats())

# API Endpoints
@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'database': 'connected' if db else 'disconnected',
        'notifications': 'enabled' if notifications else 'disabled'
    })

@app.route('/api/stats')
def api_stats():
    """Get system statistics"""
    return jsonify(get_system_stats())

@app.route('/api/queue')
def api_queue():
    """Get processing queue status"""
    return jsonify({
        'queued': len(processing_queue_manager.queue),
        'processing': len(processing_queue_manager.processing),
        'completed': len(processing_queue_manager.completed),
        'failed': len(processing_queue_manager.failed),
        'queue': processing_queue_manager.queue,
        'processing': processing_queue_manager.processing
    })

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Upload file for processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        allowed_extensions = CONFIG.get('supported_extensions', ['.txt', '.md'])
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type {file_ext} not supported'}), 400
        
        # Save file to watch folder
        filename = secure_filename(file.filename)
        watch_folder = CONFIG.get('watch_folder', '02_data')
        file_path = Path(watch_folder) / filename
        
        # Handle duplicate filenames
        counter = 1
        original_filename = filename
        while file_path.exists():
            stem = Path(original_filename).stem
            suffix = Path(original_filename).suffix
            filename = f"{stem}_{counter}{suffix}"
            file_path = Path(watch_folder) / filename
            counter += 1
        
        file.save(str(file_path))
        
        # Add to processing queue
        job_id = processing_queue_manager.add_file(str(file_path))
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'filename': filename,
            'message': 'File uploaded and queued for processing'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process/<job_id>')
def api_process_job(job_id):
    """Process specific job"""
    try:
        # Find job in queue
        job = None
        for q_job in processing_queue_manager.queue:
            if q_job['id'] == job_id:
                job = q_job
                break
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Move to processing
        processing_queue_manager.queue.remove(job)
        job['status'] = 'processing'
        job['started_at'] = datetime.now().isoformat()
        processing_queue_manager.processing.append(job)
        
        # Start processing in background
        threading.Thread(target=process_file_background, args=(job,)).start()
        
        return jsonify({'success': True, 'message': 'Processing started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def api_files():
    """Get list of processed files"""
    try:
        output_dir = CONFIG.get('output_dir', '04_output')
        files = []
        
        if Path(output_dir).exists():
            for file_folder in Path(output_dir).iterdir():
                if file_folder.is_dir():
                    file_info = {
                        'name': file_folder.name,
                        'chunks': [],
                        'transcript': None,
                        'created': None
                    }
                    
                    for file_path in file_folder.iterdir():
                        if file_path.is_file():
                            if 'chunk' in file_path.name:
                                file_info['chunks'].append({
                                    'name': file_path.name,
                                    'size': file_path.stat().st_size,
                                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                })
                            elif 'transcript' in file_path.name:
                                file_info['transcript'] = {
                                    'name': file_path.name,
                                    'size': file_path.stat().st_size,
                                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                                }
                    
                    if file_info['chunks'] or file_info['transcript']:
                        files.append(file_info)
        
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>/<file_type>')
def api_download(filename, file_type):
    """Download processed file"""
    try:
        output_dir = CONFIG.get('output_dir', '04_output')
        file_folder = Path(output_dir) / filename
        
        if file_type == 'transcript':
            # Find transcript file
            for file_path in file_folder.iterdir():
                if 'transcript' in file_path.name:
                    return send_file(str(file_path), as_attachment=True)
        elif file_type == 'chunks':
            # Create zip of all chunks
            import zipfile
            import tempfile
            
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
                for file_path in file_folder.iterdir():
                    if 'chunk' in file_path.name:
                        zipf.write(str(file_path), file_path.name)
            
            return send_file(temp_zip.name, as_attachment=True, download_name=f"{filename}_chunks.zip")
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Web Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/upload')
def upload_page():
    """File upload page"""
    return render_template('upload.html')

@app.route('/files')
def files_page():
    """Processed files page"""
    return render_template('files.html')

@app.route('/analytics')
def analytics_page():
    """Analytics page"""
    return render_template('analytics.html')

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

# Background processing
def process_file_background(job):
    """Process file in background thread"""
    try:
        file_path = Path(job['file_path'])
        
        # Import processing function from watcher_splitter
        from watcher_splitter import process_file_enhanced
        
        # Update job status
        job['progress'] = 10
        socketio.emit('job_update', job)
        
        # Process file
        success = process_file_enhanced(file_path, CONFIG)
        
        if success:
            job['status'] = 'completed'
            job['progress'] = 100
            job['completed_at'] = datetime.now().isoformat()
            processing_queue_manager.completed.append(job)
        else:
            job['status'] = 'failed'
            job['error'] = 'Processing failed'
            processing_queue_manager.failed.append(job)
        
        # Remove from processing
        if job in processing_queue_manager.processing:
            processing_queue_manager.processing.remove(job)
        
        # Emit update
        socketio.emit('job_update', job)
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        job['progress'] = 0
        
        if job in processing_queue_manager.processing:
            processing_queue_manager.processing.remove(job)
        processing_queue_manager.failed.append(job)
        
        socketio.emit('job_update', job)

# System monitoring
def get_system_stats():
    """Get current system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_stats.update({
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'active_processes': len(processing_queue_manager.processing)
        })
        
        return system_stats
    except Exception as e:
        return {'error': str(e)}

def background_monitor():
    """Background system monitoring"""
    while True:
        try:
            stats = get_system_stats()
            socketio.emit('stats_update', stats)
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(10)

# Start background monitoring
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()

if __name__ == '__main__':
    print("🚀 Starting Chunker Web Dashboard...")
    print(f"📊 Dashboard: http://localhost:5000")
    print(f"🔧 API Base: http://localhost:5000/api")
    print(f"📁 Watch Folder: {CONFIG.get('watch_folder', '02_data')}")
    print(f"📤 Output Folder: {CONFIG.get('output_dir', '04_output')}")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
