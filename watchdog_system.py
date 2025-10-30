"""
Watchdog Monitoring System for Chunker_v2
Real-time file monitoring with debouncing and event handling
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent, FileCreatedEvent

logger = logging.getLogger(__name__)

class ChunkerEventHandler(FileSystemEventHandler):
    """
    Custom event handler for chunker file monitoring.
    """
    
    def __init__(self, config: Dict[str, Any], process_callback: Callable):
        """
        Initialize event handler.
        
        Args:
            config: Configuration dictionary
            process_callback: Callback function for processing files
        """
        self.config = config
        self.process_callback = process_callback
        self.debounce_window = config.get("debounce_window", 1.0)  # seconds
        self.max_workers = config.get("max_workers", 4)
        self.failed_dir = config.get("failed_dir", "03_archive/failed")
        self.default_source_folder = config.get("default_source_folder", "02_data")
        
        # Event tracking
        self.event_queue = deque()
        self.event_timestamps = defaultdict(list)
        self.processing_files = set()
        self.worker_pool = []
        
        # Create failed directory
        os.makedirs(self.failed_dir, exist_ok=True)
        
        logger.info("Initialized ChunkerEventHandler")
    
    def on_moved(self, event: FileMovedEvent) -> None:
        """
        Handle file moved events.
        
        Args:
            event: File moved event
        """
        if event.is_directory:
            return
        
        self._handle_file_event(event.src_path, event.dest_path, "moved")
    
    def on_created(self, event: FileCreatedEvent) -> None:
        """
        Handle file created events.
        
        Args:
            event: File created event
        """
        if event.is_directory:
            return
        
        self._handle_file_event(event.src_path, None, "created")
    
    def _handle_file_event(self, src_path: str, dest_path: Optional[str], event_type: str) -> None:
        """
        Handle file events with debouncing.
        
        Args:
            src_path: Source file path
            dest_path: Destination file path (for moved events)
            event_type: Type of event (moved, created)
        """
        try:
            file_path = Path(src_path)
            
            # Skip if not a supported file type
            if not self._is_supported_file(file_path):
                return
            
            # Skip if already processing
            if str(file_path) in self.processing_files:
                return
            
            # Skip symlinks
            if file_path.is_symlink():
                logger.debug(f"Skipping symlink: {file_path}")
                return
            
            # Add to event queue with debouncing
            self._add_to_queue(file_path, dest_path, event_type)
            
        except Exception as e:
            logger.error(f"Error handling file event: {e}")
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """
        Check if file is supported for processing.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported, False otherwise
        """
        supported_extensions = self.config.get("supported_extensions", [".txt", ".md"])
        return file_path.suffix.lower() in supported_extensions
    
    def _add_to_queue(self, file_path: Path, dest_path: Optional[str], event_type: str) -> None:
        """
        Add file to processing queue with debouncing.
        
        Args:
            file_path: Path to file
            dest_path: Destination path (for moved events)
            event_type: Type of event
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
            self.event_queue.append({
                "file_path": file_path,
                "dest_path": dest_path,
                "event_type": event_type,
                "timestamp": current_time
            })
            logger.debug(f"Added to queue: {file_path} ({event_type})")
    
    def process_queue(self) -> None:
        """
        Process files in the event queue.
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
                
                # Check if file is still stable
                if not self._is_file_stable(file_path):
                    logger.debug(f"File not stable, requeuing: {file_path}")
                    self.event_queue.append(event_data)
                    time.sleep(0.5)
                    continue
                
                # Process file
                self._process_file(file_path, dest_path, event_type)
                
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                time.sleep(1)
    
    def _is_file_stable(self, file_path: Path) -> bool:
        """
        Check if file is stable (not being written to).
        
        Args:
            file_path: Path to file
            
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
    
    def _process_file(self, file_path: Path, dest_path: Optional[str], event_type: str) -> None:
        """
        Process a file.
        
        Args:
            file_path: Path to file
            dest_path: Destination path (for moved events)
            event_type: Type of event
        """
        try:
            # Mark as processing
            self.processing_files.add(str(file_path))
            
            logger.info(f"Processing file: {file_path} ({event_type})")
            
            # Call processing callback
            success = self.process_callback(file_path, dest_path, event_type)
            
            if success:
                logger.info(f"Successfully processed: {file_path}")
            else:
                logger.error(f"Failed to process: {file_path}")
                self._handle_failed_file(file_path)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            self._handle_failed_file(file_path)
        
        finally:
            # Remove from processing set
            self.processing_files.discard(str(file_path))
    
    def _handle_failed_file(self, file_path: Path) -> None:
        """
        Handle failed file processing.
        
        Args:
            file_path: Path to failed file
        """
        try:
            # Move to failed directory
            failed_path = Path(self.failed_dir) / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.name}"
            file_path.rename(failed_path)
            logger.info(f"Moved failed file to: {failed_path}")
            
        except Exception as e:
            logger.error(f"Failed to move failed file: {e}")

class WatchdogMonitor:
    """
    Watchdog-based file monitoring system.
    """
    
    def __init__(self, config: Dict[str, Any], process_callback: Callable):
        """
        Initialize watchdog monitor.
        
        Args:
            config: Configuration dictionary
            process_callback: Callback function for processing files
        """
        self.config = config
        self.process_callback = process_callback
        self.watch_folder = config.get("watch_folder", "02_data")
        self.observer = None
        self.event_handler = None
        self.queue_thread = None
        self.running = False
        
        logger.info("Initialized WatchdogMonitor")
    
    def start(self) -> None:
        """
        Start the watchdog monitor.
        """
        try:
            # Create event handler
            self.event_handler = ChunkerEventHandler(self.config, self.process_callback)
            
            # Create observer
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.watch_folder, recursive=True)
            
            # Start observer
            self.observer.start()
            
            # Start queue processing thread
            self.queue_thread = threading.Thread(target=self.event_handler.process_queue, daemon=True)
            self.queue_thread.start()
            
            self.running = True
            logger.info(f"Started watchdog monitor for: {self.watch_folder}")
            
        except Exception as e:
            logger.error(f"Failed to start watchdog monitor: {e}")
            raise
    
    def stop(self) -> None:
        """
        Stop the watchdog monitor.
        """
        try:
            self.running = False
            
            if self.observer:
                self.observer.stop()
                self.observer.join()
            
            logger.info("Stopped watchdog monitor")
            
        except Exception as e:
            logger.error(f"Error stopping watchdog monitor: {e}")
    
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
        
        return {
            "queue_size": len(self.event_handler.event_queue),
            "processing_files": len(self.event_handler.processing_files),
            "watch_folder": self.watch_folder,
            "running": self.running,
            "observer_alive": self.observer.is_alive() if self.observer else False
        }

def create_watchdog_monitor(config: Dict[str, Any], process_callback: Callable) -> WatchdogMonitor:
    """
    Create watchdog monitor instance.
    
    Args:
        config: Configuration dictionary
        process_callback: Callback function for processing files
        
    Returns:
        WatchdogMonitor instance
    """
    return WatchdogMonitor(config, process_callback)

def process_file_callback(file_path: Path, dest_path: Optional[str], event_type: str) -> bool:
    """
    Example file processing callback.
    
    Args:
        file_path: Path to file
        dest_path: Destination path (for moved events)
        event_type: Type of event
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing {event_type} event for: {file_path}")
        
        # Simulate processing
        time.sleep(1)
        
        # For moved events, copy outputs back to source folder
        if event_type == "moved" and dest_path:
            logger.info(f"File moved from {file_path} to {dest_path}")
            # TODO: Implement copy back logic
        
        return True
        
    except Exception as e:
        logger.error(f"Processing callback failed: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        "watch_folder": "02_data",
        "debounce_window": 1.0,
        "max_workers": 4,
        "failed_dir": "03_archive/failed",
        "default_source_folder": "02_data",
        "supported_extensions": [".txt", ".md", ".json", ".csv", ".xlsx", ".pdf", ".py", ".docx", ".sql", ".yaml", ".xml", ".log"]
    }
    
    # Create monitor
    monitor = create_watchdog_monitor(config, process_file_callback)
    
    try:
        # Start monitoring
        monitor.start()
        
        # Keep running
        while monitor.is_running():
            time.sleep(1)
            
            # Print stats every 10 seconds
            if int(time.time()) % 10 == 0:
                stats = monitor.get_stats()
                logger.info(f"Monitor stats: {stats}")
    
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        monitor.stop()
    
    print("Watchdog monitor test completed successfully!")
