// Enterprise Chunker Dashboard JavaScript

class ChunkerDashboard {
    constructor() {
        this.socket = null;
        this.statsChart = null;
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.initCharts();
        this.bindEvents();
        this.startPeriodicUpdates();
        this.loadInitialData();
    }

    connectWebSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus('connected');
            this.socket.emit('request_stats');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus('disconnected');
        });

        this.socket.on('stats_update', (data) => {
            this.updateSystemStats(data);
        });

        this.socket.on('job_update', (job) => {
            this.updateJobStatus(job);
        });

        this.socket.on('status', (data) => {
            this.showNotification(data.message, 'info');
        });
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        const icon = statusElement.querySelector('.fas');
        
        statusElement.className = `navbar-text ${status}`;
        
        switch(status) {
            case 'connected':
                icon.className = 'fas fa-circle text-success';
                statusElement.textContent = ' Connected';
                break;
            case 'disconnected':
                icon.className = 'fas fa-circle text-danger';
                statusElement.textContent = ' Disconnected';
                break;
            case 'connecting':
                icon.className = 'fas fa-circle text-warning';
                statusElement.textContent = ' Connecting...';
                break;
        }
    }

    initCharts() {
        const ctx = document.getElementById('statsChart');
        if (ctx) {
            this.statsChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Queued', 'Processing', 'Completed', 'Failed'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            '#17a2b8',
                            '#ffc107',
                            '#28a745',
                            '#dc3545'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 10,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }
    }

    bindEvents() {
        // File upload handling
        const uploadBtn = document.getElementById('upload-btn');
        const fileInput = document.getElementById('file-input');
        const uploadForm = document.getElementById('upload-form');

        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.handleFileUpload());
        }

        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.previewFile(file);
                }
            });
        }

        // Drag and drop support
        const uploadArea = document.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileDrop(files[0]);
                }
            });
        }

        // Auto-refresh queue
        setInterval(() => {
            this.loadQueueData();
        }, 5000);
    }

    async handleFileUpload() {
        const fileInput = document.getElementById('file-input');
        const prioritySelect = document.getElementById('priority-select');
        const uploadBtn = document.getElementById('upload-btn');

        if (!fileInput.files[0]) {
            this.showNotification('Please select a file', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner"></span> Uploading...';

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('File uploaded successfully!', 'success');
                this.loadQueueData();
                
                // Auto-process the job
                setTimeout(() => {
                    this.processJob(result.job_id);
                }, 1000);
            } else {
                this.showNotification(result.error || 'Upload failed', 'danger');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Upload failed: ' + error.message, 'danger');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload & Process';
            fileInput.value = '';
        }
    }

    async processJob(jobId) {
        try {
            const response = await fetch(`/api/process/${jobId}`);
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Processing started', 'info');
            } else {
                this.showNotification(result.error || 'Failed to start processing', 'danger');
            }
        } catch (error) {
            console.error('Process error:', error);
            this.showNotification('Failed to start processing', 'danger');
        }
    }

    async loadQueueData() {
        try {
            const response = await fetch('/api/queue');
            const data = await response.json();
            
            this.updateQueueCounts(data);
            this.updateQueueItems(data);
            this.updateChart(data);
        } catch (error) {
            console.error('Failed to load queue data:', error);
        }
    }

    updateQueueCounts(data) {
        document.getElementById('queued-count').textContent = data.queued;
        document.getElementById('processing-count').textContent = data.processing;
        document.getElementById('completed-count').textContent = data.completed;
        document.getElementById('failed-count').textContent = data.failed;
        document.getElementById('active-jobs').textContent = data.processing;
    }

    updateQueueItems(data) {
        const queueContainer = document.getElementById('queue-items');
        if (!queueContainer) return;

        let html = '';

        // Show processing jobs
        data.processing.forEach(job => {
            html += this.createJobItem(job);
        });

        // Show queued jobs
        data.queue.forEach(job => {
            html += this.createJobItem(job);
        });

        if (html === '') {
            html = '<div class="text-center text-muted py-4">No jobs in queue</div>';
        }

        queueContainer.innerHTML = html;
    }

    createJobItem(job) {
        const statusClass = `status-${job.status}`;
        const progressBar = job.status === 'processing' ? 
            `<div class="progress mt-2">
                <div class="progress-bar" style="width: ${job.progress}%"></div>
             </div>` : '';

        return `
            <div class="queue-item ${job.status} fade-in">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${job.filename}</h6>
                        <small class="text-muted">Priority: ${job.priority}</small>
                        ${job.error ? `<br><small class="text-danger">${job.error}</small>` : ''}
                    </div>
                    <div class="text-end">
                        <span class="status-badge ${statusClass}">${job.status}</span>
                        ${progressBar}
                    </div>
                </div>
            </div>
        `;
    }

    updateChart(data) {
        if (this.statsChart) {
            this.statsChart.data.datasets[0].data = [
                data.queued,
                data.processing,
                data.completed,
                data.failed
            ];
            this.statsChart.update();
        }
    }

    updateSystemStats(stats) {
        document.getElementById('cpu-usage').textContent = `${Math.round(stats.cpu_percent)}%`;
        document.getElementById('memory-usage').textContent = `${Math.round(stats.memory_percent)}%`;
        document.getElementById('disk-usage').textContent = `${Math.round(stats.disk_percent)}%`;
        document.getElementById('active-jobs').textContent = stats.active_processes;
    }

    updateJobStatus(job) {
        // Update the specific job in the queue display
        this.loadQueueData();
        
        // Show notification for completed/failed jobs
        if (job.status === 'completed') {
            this.showNotification(`File "${job.filename}" processed successfully!`, 'success');
        } else if (job.status === 'failed') {
            this.showNotification(`File "${job.filename}" processing failed: ${job.error}`, 'danger');
        }
    }

    async loadInitialData() {
        await this.loadQueueData();
        await this.loadRecentActivity();
        await this.loadSystemAlerts();
    }

    async loadRecentActivity() {
        try {
            const response = await fetch('/api/activity');
            const data = await response.json();
            
            const container = document.getElementById('recent-activity');
            if (container) {
                let html = '';
                data.activities.forEach(activity => {
                    html += `
                        <div class="activity-item">
                            <div class="d-flex justify-content-between">
                                <div>${activity.message}</div>
                                <small class="activity-time">${this.formatTime(activity.timestamp)}</small>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html || '<div class="text-muted">No recent activity</div>';
            }
        } catch (error) {
            console.error('Failed to load activity:', error);
        }
    }

    async loadSystemAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const data = await response.json();
            
            const container = document.getElementById('system-alerts');
            if (container) {
                let html = '';
                data.alerts.forEach(alert => {
                    html += `
                        <div class="alert-item alert-${alert.level}">
                            <div class="d-flex justify-content-between">
                                <div>${alert.message}</div>
                                <small>${this.formatTime(alert.timestamp)}</small>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html || '<div class="text-muted">No system alerts</div>';
            }
        } catch (error) {
            console.error('Failed to load alerts:', error);
        }
    }

    startPeriodicUpdates() {
        this.updateInterval = setInterval(() => {
            this.loadQueueData();
        }, 5000);
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to toast container
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)}m ago`;
        } else if (diff < 86400000) { // Less than 1 day
            return `${Math.floor(diff / 3600000)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    previewFile(file) {
        // Show file preview in upload modal
        const preview = document.getElementById('file-preview');
        if (preview) {
            preview.innerHTML = `
                <div class="alert alert-info">
                    <strong>Selected File:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${this.formatFileSize(file.size)}<br>
                    <strong>Type:</strong> ${file.type || 'Unknown'}
                </div>
            `;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chunkerDashboard = new ChunkerDashboard();
});

// Export for use in other scripts
window.ChunkerDashboard = ChunkerDashboard;
