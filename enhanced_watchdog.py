"""
Enhanced Watchdog System with Celery Integration for Chunker_v2
Real-time file monitoring with async processing and race condition prevention
"""

import os
import time
import logging
import threading
import shutil
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent, FileCreatedEvent, FileDeletedEvent

# Celery integration with fallback
try:
    from celery_tasks import process_file_with_celery_chain, app as celery_app
    CELERY_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Celery integration available")
except ImportError as e:
    CELERY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Celery not available: {e}. Using fallback processing.")

logger = logging.getLogger(__name__)

class EnhancedChunkerEventHandler(FileSystemEventHandler):
    """
    Enhanced event handler with Celery integration and comprehensive event handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enhanced event handler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.debounce_window = config.get("debounce_window", 1.0)
        self.max_workers = config.get("max_workers", 4)
        self.failed_dir = config.get("failed_dir", "03_archive/failed")
        self.default_source_folder = config.get("default_source_folder", "02_data")
        self.supported_extensions = config.get("supported_extensions", [".txt", ".md"])
        
        # Event tracking
        self.event_queue = deque()
        self.event_timestamps = defaultdict(list)
        self.processing_files = set()
        self.task_coordinator = TaskCoordinator(config)
        
        # Create directories
        os.makedirs(self.failed_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_failed": 0,
            "events_ignored": 0,
            "race_conditions_prevented": 0,
            "start_time": datetime.now()
        }
        
        logger.info("Initialized EnhancedChunkerEventHandler")
    
    def on_moved(self, event: FileMovedEvent) -> None:
        """
        Handle file moved events with source path tracking.
        
        Args:
            event: File moved event
        """
        if event.is_directory:
            return
        
        self._handle_file_event(
            event.src_path, 
            event.dest_path, 
            "moved",
            source_folder=self._detect_source_folder(event.src_path)
        )
    
    def on_created(self, event: FileCreatedEvent) -> None:
        """
        Handle file created events (fallback for copy operations).
        
        Args:
            event: File created event
        """
        if event.is_directory:
            return
        
        self._handle_file_event(
            event.src_path, 
            None, 
            "created",
            source_folder=self._detect_source_folder(event.src_path)
        )
    
    def on_deleted(self, event: FileDeletedEvent) -> None:
        """
        Handle file deleted events (ignore for processing).
        
        Args:
            event: File deleted event
        """
        if event.is_directory:
            return
        
        logger.debug(f"Ignoring file deletion: {event.src_path}")
        self.stats["events_ignored"] += 1
    
    def _handle_file_event(self, src_path: str, dest_path: Optional[str], 
                          event_type: str, source_folder: Optional[str] = None) -> None:
        """
        Handle file events with comprehensive processing.
        
        Args:
            src_path: Source file path
            dest_path: Destination file path (for moved events)
            event_type: Type of event (moved, created)
            source_folder: Detected source folder
        """
        try:
            file_path = Path(src_path)
            
            # Skip if not a supported file type
            if not self._is_supported_file(file_path):
                logger.debug(f"Skipping unsupported file: {file_path}")
                self.stats["events_ignored"] += 1
                return
            
            # Skip symlinks
            if file_path.is_symlink():
                logger.debug(f"Skipping symlink: {file_path}")
                self.stats["events_ignored"] += 1
                return
            
            # Skip if already processing
            if str(file_path) in self.processing_files:
                logger.debug(f"File already being processed: {file_path}")
                self.stats["race_conditions_prevented"] += 1
                return
            
            # Check file permissions
            if not self._check_file_permissions(file_path):
                logger.warning(f"Insufficient permissions for file: {file_path}")
                self._handle_failed_file(file_path, "Permission denied")
                return
            
            # Check if file is too large for immediate processing
            if self._is_large_file(file_path):
                logger.info(f"Large file detected, will use streaming: {file_path}")
            
            # Add to event queue with debouncing
            self._add_to_queue(file_path, dest_path, event_type, source_folder)
            
        except Exception as e:
            logger.error(f"Error handling file event: {e}")
            self.stats["files_failed"] += 1
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """
        Check if file is supported for processing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if supported, False otherwise
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    def _detect_source_folder(self, file_path: str) -> Optional[str]:
        """
        Detect source folder for file operations.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected source folder or None
        """
        try:
            # Check if file is in a known source folder
            path_obj = Path(file_path)
            
            # Look for common source patterns
            for part in path_obj.parts:
                if part in ["source", "input", "data", "docs"]:
                    return part
            
            # Default to configured source folder
            return self.default_source_folder
            
        except Exception as e:
            logger.error(f"Error detecting source folder: {e}")
            return self.default_source_folder
    
    def _check_file_permissions(self, file_path: Path) -> bool:
        """
        Check if file has required permissions.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if permissions are sufficient, False otherwise
        """
        try:
            return os.access(file_path, os.R_OK)
        except Exception:
            return False
    
    def _is_large_file(self, file_path: Path) -> bool:
        """
        Check if file is considered large (> 10MB).
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if large, False otherwise
        """
        try:
            return file_path.stat().st_size > 10 * 1024 * 1024  # 10MB
        except Exception:
            return False
    
    def _add_to_queue(self, file_path: Path, dest_path: Optional[str], 
                     event_type: str, source_folder: Optional[str]) -> None:
        """
        Add file to processing queue with debouncing.
        
        Args:
            file_path: Path to the file
            dest_path: Destination path (for moved events)
            event_type: Type of event
            source_folder: Source folder
        """
        file_str = str(file_path)
        current_time = time.time()
        
        # Clean old timestamps
        cutoff_time = current_time - self.debounce_window
        self.event_timestamps[file_str] = [
            ts for ts in self.event_timestamps[file_str] if ts > cutoff_time
        ]
        
        # Add new timestamp
        self.event_timestamps[file_str].append(current_time)
        
        # If this is the first event or enough time has passed, add to queue
        if len(self.event_timestamps[file_str]) == 1:
            event_data = {
                "file_path": file_path,
                "dest_path": dest_path,
                "event_type": event_type,
                "source_folder": source_folder,
                "timestamp": current_time,
                "retry_count": 0
            }
            
            self.event_queue.append(event_data)
            logger.debug(f"Added to queue: {file_path} ({event_type})")
    
    def process_queue(self) -> None:
        """
        Process files in the event queue using Celery tasks.
        """
        while True:
            try:
                if not self.event_queue:
                    time.sleep(0.1)
                    continue
                
                # Get next file from queue
                event_data = self.event_queue.popleft()
                file_path = event_data["file_path"]
                dest_path = event_data["dest_path"]
                event_type = event_data["event_type"]
                source_folder = event_data["source_folder"]
                
                # Check if file is still stable
                if not self._is_file_stable(file_path):
                    logger.debug(f"File not stable, requeuing: {file_path}")
                    event_data["retry_count"] += 1
                    
                    if event_data["retry_count"] < 3:
                        self.event_queue.append(event_data)
                        time.sleep(0.5)
                    else:
                        logger.warning(f"File stability check failed after 3 retries: {file_path}")
                        self._handle_failed_file(file_path, "File stability check failed")
                    
                    continue
                
                # Queue Celery task for processing
                self._queue_processing_task(file_path, dest_path, event_type, source_folder)
                
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                time.sleep(1)
    
    def _is_file_stable(self, file_path: Path) -> bool:
        """
        Check if file is stable (not being written to).
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if stable, False otherwise
        """
        try:
            if not file_path.exists():
                return False
            
            # Check file size stability
            initial_size = file_path.stat().st_size
            time.sleep(0.5)
            final_size = file_path.stat().st_size
            
            return initial_size == final_size
            
        except Exception as e:
            logger.error(f"Error checking file stability: {e}")
            return False
    
    def _queue_processing_task(self, file_path: Path, dest_path: Optional[str], 
                              event_type: str, source_folder: Optional[str]) -> None:
        """
        Queue a Celery task for file processing with fallback.
        
        Args:
            file_path: Path to the file
            dest_path: Destination path (for moved events)
            event_type: Type of event
            source_folder: Source folder
        """
        try:
            # Mark as processing
            self.processing_files.add(str(file_path))
            
            if CELERY_AVAILABLE:
                # Use Celery task chain for advanced processing
                task_id = process_file_with_celery_chain(
                    str(file_path),
                    str(dest_path) if dest_path else None,
                    event_type,
                    self.config
                )
                
                logger.info(f"Queued Celery workflow for: {file_path} (task_id: {task_id})")
                
                # Monitor task completion in background
                self._monitor_celery_task_completion(file_path, task_id)
                
            else:
                # Fallback to direct processing
                logger.info(f"Using fallback processing for: {file_path}")
                self._process_file_directly(file_path, dest_path, event_type, source_folder)
            
        except Exception as e:
            logger.error(f"Error queuing processing task: {e}")
            self.processing_files.discard(str(file_path))
            self._handle_failed_file(file_path, str(e))
    
    def _monitor_celery_task_completion(self, file_path: Path, task_id: str) -> None:
        """
        Monitor Celery task completion using task ID.
        
        Args:
            file_path: Path to the file
            task_id: Celery task ID
        """
        def monitor():
            try:
                if not CELERY_AVAILABLE:
                    logger.error("Celery not available for task monitoring")
                    self.processing_files.discard(str(file_path))
                    return
                
                # Get task result with timeout
                result = celery_app.AsyncResult(task_id)
                
                # Wait for task completion with timeout
                try:
                    task_result = result.get(timeout=300)  # 5 minute timeout
                    
                    if task_result and task_result.get("status") == "success":
                        logger.info(f"Successfully processed: {file_path}")
                        self.stats["files_processed"] += 1
                    else:
                        logger.error(f"Failed to process: {file_path} - {task_result.get('message', 'Unknown error')}")
                        self.stats["files_failed"] += 1
                        self._handle_failed_file(file_path, task_result.get("message", "Processing failed"))
                
                except Exception as e:
                    logger.error(f"Task monitoring timeout or error: {e}")
                    self.stats["files_failed"] += 1
                    self._handle_failed_file(file_path, str(e))
                
            except Exception as e:
                logger.error(f"Error monitoring Celery task: {e}")
                self.stats["files_failed"] += 1
                self._handle_failed_file(file_path, str(e))
            
            finally:
                # Remove from processing set
                self.processing_files.discard(str(file_path))
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _process_file_directly(self, file_path: Path, dest_path: Optional[str], 
                              event_type: str, source_folder: Optional[str]) -> None:
        """
        Fallback direct file processing when Celery is not available.
        
        Args:
            file_path: Path to the file
            dest_path: Destination path (for moved events)
            event_type: Type of event
            source_folder: Source folder
        """
        def process():
            try:
                logger.info(f"Processing file directly: {file_path}")
                
                # Import the original processing function
                from watcher_splitter import process_file_enhanced
                
                # Process the file
                success = process_file_enhanced(file_path, self.config)
                
                if success:
                    logger.info(f"Successfully processed: {file_path}")
                    self.stats["files_processed"] += 1
                else:
                    logger.error(f"Failed to process: {file_path}")
                    self.stats["files_failed"] += 1
                    self._handle_failed_file(file_path, "Direct processing failed")
                
            except Exception as e:
                logger.error(f"Direct processing failed: {e}")
                self.stats["files_failed"] += 1
                self._handle_failed_file(file_path, str(e))
            
            finally:
                # Remove from processing set
                self.processing_files.discard(str(file_path))
        
        # Start processing in background thread
        process_thread = threading.Thread(target=process, daemon=True)
        process_thread.start()
    
    def _monitor_task_completion(self, file_path: Path, task) -> None:
        """
        Monitor Celery task completion in background thread.
        
        Args:
            file_path: Path to the file
            task: Celery task object
        """
        def monitor():
            try:
                # Wait for task completion
                result = task.get(timeout=300)  # 5 minute timeout
                
                if result.get("status") == "success":
                    logger.info(f"Successfully processed: {file_path}")
                    self.stats["files_processed"] += 1
                else:
                    logger.error(f"Failed to process: {file_path} - {result.get('message', 'Unknown error')}")
                    self.stats["files_failed"] += 1
                    self._handle_failed_file(file_path, result.get("message", "Processing failed"))
                
            except Exception as e:
                logger.error(f"Error monitoring task completion: {e}")
                self.stats["files_failed"] += 1
                self._handle_failed_file(file_path, str(e))
            
            finally:
                # Remove from processing set
                self.processing_files.discard(str(file_path))
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _handle_failed_file(self, file_path: Path, error: str) -> None:
        """
        Handle failed file processing.
        
        Args:
            file_path: Path to the failed file
            error: Error message
        """
        try:
            # Move to failed directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            failed_path = Path(self.failed_dir) / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            file_path.rename(failed_path)
            
            # Log error details
            error_log = Path(self.failed_dir) / f"{file_path.stem}_{timestamp}_error.log"
            with open(error_log, 'w') as f:
                f.write(f"File: {file_path}\n")
                f.write(f"Error: {error}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            
            logger.info(f"Moved failed file to: {failed_path}")
            
        except Exception as e:
            logger.error(f"Failed to handle failed file: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Statistics dictionary
        """
        uptime = datetime.now() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "files_processed": self.stats["files_processed"],
            "files_failed": self.stats["files_failed"],
            "events_ignored": self.stats["events_ignored"],
            "race_conditions_prevented": self.stats["race_conditions_prevented"],
            "queue_size": len(self.event_queue),
            "processing_files": len(self.processing_files),
            "processing_file_list": list(self.processing_files)
        }

class EnhancedWatchdogMonitor:
    """
    Enhanced watchdog monitor with Celery integration and comprehensive monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enhanced watchdog monitor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.watch_folder = config.get("watch_folder", "02_data")
        self.recursive = config.get("recursive_watch", True)
        self.observer = None
        self.event_handler = None
        self.queue_thread = None
        self.running = False
        
        logger.info("Initialized EnhancedWatchdogMonitor")
    
    def start(self, scan_existing: bool = True) -> None:
        """
        Start the enhanced watchdog monitor.

        Args:
            scan_existing: If True, scan and queue existing files on startup
        """
        try:
            # Create event handler
            self.event_handler = EnhancedChunkerEventHandler(self.config)

            # Create observer
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.watch_folder,
                recursive=self.recursive
            )

            # Start observer
            self.observer.start()

            # Start queue processing thread
            self.queue_thread = threading.Thread(
                target=self.event_handler.process_queue,
                daemon=True
            )
            self.queue_thread.start()

            self.running = True
            logger.info(f"Started enhanced watchdog monitor for: {self.watch_folder}")

            # Scan existing files if requested
            if scan_existing:
                self._scan_existing_files()

        except Exception as e:
            logger.error(f"Failed to start enhanced watchdog monitor: {e}")
            raise

    def _scan_existing_files(self) -> None:
        """
        Scan and queue all existing files in the watch folder on startup.
        This ensures files that were already present are processed.
        """
        try:
            logger.info(f"Scanning existing files in: {self.watch_folder}")

            watch_path = Path(self.watch_folder)
            if not watch_path.exists():
                logger.error(f"Watch folder does not exist: {self.watch_folder}")
                return

            supported_extensions = self.config.get("supported_extensions", [".txt", ".md"])
            exclude_patterns = self.config.get("exclude_patterns", [])

            files_found = 0
            files_queued = 0

            # Scan for all supported file types
            for ext in supported_extensions:
                for file_path in watch_path.glob(f"*{ext}"):
                    files_found += 1

                    # Skip if not a file
                    if not file_path.is_file():
                        continue

                    # Skip excluded patterns
                    if any(pattern in file_path.name for pattern in exclude_patterns):
                        logger.debug(f"Skipping excluded file: {file_path.name}")
                        continue

                    # Skip hidden files
                    if file_path.name.startswith('.'):
                        continue

                    # Queue file for processing using the event handler
                    logger.info(f"Queuing existing file: {file_path.name}")
                    self.event_handler._handle_file_event(
                        str(file_path),
                        None,
                        "startup_scan",
                        self.event_handler._detect_source_folder(str(file_path))
                    )
                    files_queued += 1

            logger.info(f"Startup scan complete: {files_found} files found, {files_queued} queued for processing")

        except Exception as e:
            logger.error(f"Error scanning existing files: {e}")
    
    def stop(self) -> None:
        """
        Stop the enhanced watchdog monitor.
        """
        try:
            self.running = False
            
            if self.observer:
                self.observer.stop()
                self.observer.join()
            
            logger.info("Stopped enhanced watchdog monitor")
            
        except Exception as e:
            logger.error(f"Error stopping enhanced watchdog monitor: {e}")
    
    def is_running(self) -> bool:
        """
        Check if monitor is running.
        
        Returns:
            True if running, False otherwise
        """
        return self.running and self.observer and self.observer.is_alive()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get monitoring statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.event_handler:
            return {"error": "Event handler not initialized"}
        
        stats = self.event_handler.get_stats()
        stats.update({
            "watch_folder": self.watch_folder,
            "recursive": self.recursive,
            "running": self.running,
            "observer_alive": self.observer.is_alive() if self.observer else False
        })
        
        return stats
    
    def force_process_file(self, file_path: str) -> bool:
        """
        Force process a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if queued successfully, False otherwise
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Queue processing task directly
            task = process_file_task.delay(
                str(file_path_obj),
                None,
                "manual",
                self.config
            )
            
            logger.info(f"Force queued processing for: {file_path} (task_id: {task.id})")
            return True
            
        except Exception as e:
            logger.error(f"Error force processing file: {e}")
            return False

def create_enhanced_watchdog_monitor(config: Dict[str, Any]) -> EnhancedWatchdogMonitor:
    """
    Create enhanced watchdog monitor instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        EnhancedWatchdogMonitor instance
    """
    return EnhancedWatchdogMonitor(config)

def start_celery_worker() -> None:
    """
    Start Celery worker process.
    """
    try:
        from celery_tasks import app
        app.worker_main(['worker', '--loglevel=info', '--concurrency=4'])
    except Exception as e:
        logger.error(f"Failed to start Celery worker: {e}")

# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        "watch_folder": "02_data",
        "debounce_window": 1.0,
        "max_workers": 4,
        "failed_dir": "03_archive/failed",
        "default_source_folder": "02_data",
        "recursive_watch": True,
        "supported_extensions": [".txt", ".md", ".json", ".csv", ".xlsx", ".pdf", ".py", ".docx", ".sql", ".yaml", ".xml", ".log"],
        "rag_enabled": True,
        "chroma_persist_dir": "./chroma_db",
        "output_dir": "04_output",
        "archive_dir": "03_archive"
    }
    
    # Create monitor
    monitor = create_enhanced_watchdog_monitor(config)
    
    try:
        # Start monitoring
        monitor.start()
        
        # Keep running
        while monitor.is_running():
            time.sleep(10)
            
            # Print stats every 10 seconds
            stats = monitor.get_stats()
            logger.info(f"Monitor stats: {stats}")
    
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        monitor.stop()
    
    print("Enhanced watchdog monitor test completed successfully!")
