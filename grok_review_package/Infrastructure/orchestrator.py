"""
Simple Orchestration Script for Chunker_v2
Replaces Airflow with lightweight task coordination
"""

import os
import time
import logging
import subprocess
import threading
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ChunkerOrchestrator:
    """
    Lightweight orchestration for Chunker_v2 without Airflow complexity.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.processes = {}
        self.running = False
        
        logger.info("Initialized ChunkerOrchestrator")
    
    def start_all_services(self) -> None:
        """Start all Chunker_v2 services."""
        try:
            # Start Redis (if not running)
            self._start_redis()
            
            # Start Celery workers
            self._start_celery_workers()
            
            # Start Celery beat scheduler
            self._start_celery_beat()
            
            # Start Flower dashboard
            self._start_flower_dashboard()
            
            # Start Watchdog monitor
            self._start_watchdog()
            
            # Start monitoring
            self._start_monitoring()
            
            self.running = True
            logger.info("All services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            self.stop_all_services()
            raise
    
    def stop_all_services(self) -> None:
        """Stop all services."""
        try:
            self.running = False
            
            for service_name, process in self.processes.items():
                if process and process.poll() is None:
                    process.terminate()
                    logger.info(f"Stopped {service_name}")
            
            self.processes.clear()
            logger.info("All services stopped")
            
        except Exception as e:
            logger.error(f"Error stopping services: {e}")
    
    def _start_redis(self) -> None:
        """Start Redis server with enhanced error handling and fallback."""
        try:
            # Check if Redis is already running
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("Redis already running")
                return
            
            # Try to start Redis
            try:
                redis_process = subprocess.Popen(['redis-server'], 
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL)
                self.processes['redis'] = redis_process
                
                # Wait for Redis to start and verify
                for attempt in range(5):
                    time.sleep(1)
                    try:
                        test_result = subprocess.run(['redis-cli', 'ping'], 
                                                   capture_output=True, text=True, timeout=2)
                        if test_result.returncode == 0:
                            logger.info("Redis started successfully")
                            return
                    except subprocess.TimeoutExpired:
                        continue
                
                # If we get here, Redis didn't start properly
                logger.error("Redis failed to start properly")
                raise Exception("Redis startup verification failed")
                
            except FileNotFoundError:
                logger.error("Redis not found. Please install Redis:")
                logger.error("  Windows: Download from https://github.com/microsoftarchive/redis/releases")
                logger.error("  Linux: sudo apt-get install redis-server")
                logger.error("  macOS: brew install redis")
                raise Exception("Redis not installed")
            
        except Exception as e:
            logger.error(f"Redis startup failed: {e}")
            logger.warning("Falling back to multiprocessing.Queue for task coordination")
            self._setup_fallback_queue()
            raise Exception("Redis not available - using fallback mode")
    
    def _setup_fallback_queue(self) -> None:
        """Setup multiprocessing.Queue as fallback when Redis is unavailable."""
        try:
            import multiprocessing
            self.fallback_queue = multiprocessing.Queue()
            logger.info("Fallback queue initialized - Celery will use in-memory processing")
        except Exception as e:
            logger.error(f"Failed to setup fallback queue: {e}")
            raise
    
    def _start_celery_workers(self) -> None:
        """Start Celery workers."""
        try:
            # Start file processing worker
            file_worker = subprocess.Popen([
                'python', '-m', 'celery', 'worker',
                '-A', 'celery_tasks',
                '-Q', 'file_processing',
                '--concurrency=4',
                '--loglevel=info'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['celery_file_worker'] = file_worker
            
            # Start batch processing worker
            batch_worker = subprocess.Popen([
                'python', '-m', 'celery', 'worker',
                '-A', 'celery_tasks',
                '-Q', 'batch_processing',
                '--concurrency=2',
                '--loglevel=info'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['celery_batch_worker'] = batch_worker
            
            logger.info("Celery workers started")
            
        except Exception as e:
            logger.error(f"Failed to start Celery workers: {e}")
            raise
    
    def _start_celery_beat(self) -> None:
        """Start Celery beat scheduler."""
        try:
            beat_process = subprocess.Popen([
                'python', '-m', 'celery', 'beat',
                '-A', 'celery_tasks',
                '--loglevel=info'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['celery_beat'] = beat_process
            
            logger.info("Celery beat scheduler started")
            
        except Exception as e:
            logger.error(f"Failed to start Celery beat: {e}")
            raise
    
    def _start_flower_dashboard(self) -> None:
        """Start Flower dashboard for Celery monitoring with authentication."""
        try:
            # Generate basic auth credentials (in production, use environment variables)
            import base64
            import secrets
            
            username = os.getenv('FLOWER_USERNAME', 'admin')
            password = os.getenv('FLOWER_PASSWORD', secrets.token_urlsafe(8))
            
            # Create auth string
            auth_string = f"{username}:{password}"
            auth_b64 = base64.b64encode(auth_string.encode()).decode()
            
            flower_process = subprocess.Popen([
                'python', '-m', 'flower',
                '--broker=redis://localhost:6379/0',
                '--port=5555',
                '--address=0.0.0.0',
                f'--auth={auth_string}',
                '--basic_auth=admin:admin'  # Fallback basic auth
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['flower'] = flower_process
            
            logger.info("Flower dashboard started on http://localhost:5555")
            logger.info(f"Authentication: username='{username}', password='{password}'")
            logger.warning("Change default credentials in production!")
            
        except Exception as e:
            logger.warning(f"Failed to start Flower dashboard: {e}")
            logger.info("Celery monitoring will be available via CLI only")
    
    def _start_watchdog(self) -> None:
        """Start watchdog monitor."""
        try:
            watchdog_process = subprocess.Popen([
                'python', 'enhanced_watchdog.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes['watchdog'] = watchdog_process
            
            logger.info("Watchdog monitor started")
            
        except Exception as e:
            logger.error(f"Failed to start watchdog: {e}")
            raise
    
    def _start_monitoring(self) -> None:
        """Start monitoring thread."""
        def monitor():
            while self.running:
                try:
                    self._check_service_health()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("Monitoring started")
    
    def _check_service_health(self) -> None:
        """Check health of all services."""
        healthy_services = []
        unhealthy_services = []
        
        for service_name, process in self.processes.items():
            if process and process.poll() is None:
                healthy_services.append(service_name)
            else:
                unhealthy_services.append(service_name)
        
        if unhealthy_services:
            logger.warning(f"Unhealthy services: {unhealthy_services}")
        
        logger.info(f"Service health: {len(healthy_services)} healthy, {len(unhealthy_services)} unhealthy")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "services": {}
        }
        
        for service_name, process in self.processes.items():
            status["services"][service_name] = {
                "running": process and process.poll() is None,
                "pid": process.pid if process else None
            }
        
        return status
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service."""
        try:
            if service_name in self.processes:
                old_process = self.processes[service_name]
                if old_process:
                    old_process.terminate()
                    old_process.wait()
                
                # Restart based on service type
                if service_name == 'celery_file_worker':
                    self._start_celery_workers()
                elif service_name == 'watchdog':
                    self._start_watchdog()
                # Add other services as needed
                
                logger.info(f"Restarted {service_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart {service_name}: {e}")
            return False

def main():
    """Main orchestration function."""
    config = {
        "watch_folder": "02_data",
        "output_dir": "04_output",
        "archive_dir": "03_archive",
        "rag_enabled": True
    }
    
    orchestrator = ChunkerOrchestrator(config)
    
    try:
        print("Starting Chunker_v2 services...")
        orchestrator.start_all_services()
        
        print("All services started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping services...")
        orchestrator.stop_all_services()
        print("All services stopped.")

if __name__ == "__main__":
    main()
