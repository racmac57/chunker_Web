# 🕒 2025-06-28-01-55-30
# chunker/watcher_splitter_enterprise.py
# Author: R. A. Carucci  
# Purpose: Enterprise-grade chunker with database tracking, notifications, and parallel processing

import os
import sys
import time 
import shutil
import logging
import traceback
import threading
import random
import queue
import sqlite3
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from functools import lru_cache
import nltk
from nltk.tokenize import sent_tokenize
import json
import psutil
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from typing import Iterable, Tuple, Optional, Dict, Any, List
from metadata_enrichment import (
    EnrichmentResult,
    enrich_metadata,
    enrich_chunk,
    build_sidecar_payload,
    tag_suffix_for_filename,
    merge_manifest_metadata,
    SIDECAR_SUFFIX,
    dump_json,
)
try:
    from incremental_updates import VersionTracker, build_chunk_id
except Exception:  # noqa: BLE001
    VersionTracker = None  # type: ignore[assignment]

    def build_chunk_id(timestamp: str, base_name: str, chunk_index: int) -> str:
        """
        Fallback chunk-id generator when incremental_updates isn't available.

        Mirrors the structure produced by build_chunk_id in incremental_updates.py so
        downstream systems continue to receive stable identifiers.
        """
        safe_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") if not timestamp else timestamp
        safe_base = base_name.replace(" ", "_")
        return f"{safe_ts}:{safe_base}:{chunk_index:05d}"
from chunker_db import ChunkerDatabase
from notification_system import NotificationSystem
from monitoring_system import MonitoringSystem
from backup_manager import BackupManager
from file_processors import read_file_with_fallback
from watch_events import run_event_watcher, file_is_settled

try:
    from deduplication import DeduplicationManager
except ImportError:
    DeduplicationManager = None  # type: ignore

try:
    from incremental_updates import VersionTracker
except ImportError:
    VersionTracker = None  # type: ignore

# Resolve config path (supports PyInstaller .exe)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

# Configure local nltk_data path
nltk_path = os.path.join(base_path, "nltk_data")
nltk.data.path.append(nltk_path)

try:
    nltk.download('punkt_tab', download_dir=nltk_path, quiet=True)
except:
    nltk.download('punkt', download_dir=nltk_path, quiet=True)

# Load configuration
def load_cfg(path: str):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for k in ["watch_folder", "archive_dir", "output_dir", "failed_dir"]:
        if k in cfg:
            cfg[k] = os.path.expandvars(cfg[k])
    return cfg

CONFIG = load_cfg(os.path.join(base_path, "config.json"))

use_ready_signal = bool(CONFIG.get("use_ready_signal", False))
failed_dir = Path(CONFIG.get("failed_dir", "03_archive/failed"))
failed_dir.mkdir(parents=True, exist_ok=True)

# Feature toggle state (initialized after database/notifications are ready)
METADATA_CONFIG: Dict[str, Any] = {}
METADATA_ENABLED: bool = False
DEDUP_CONFIG: Dict[str, Any] = {}
dedup_manager = None
INCREMENTAL_CONFIG: Dict[str, Any] = {}
version_tracker = None
monitoring: Optional[MonitoringSystem] = None

# Department-specific configurations based on actual content domains
# Organized by: Software/Code, Product/System, AI/Chat, Data Operations
DEPARTMENT_CONFIGS = {
    # ========================================================================
    # SOFTWARE/CODE DOMAINS
    # ========================================================================
    "python": {
        "chunk_size": 100,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Python scripts, code, and programming content"
    },
    "sql": {
        "chunk_size": 120,
        "enable_redaction": True,  # May contain sensitive table/column names
        "audit_level": "enhanced",
        "priority": "normal",
        "description": "SQL queries and database operations"
    },
    "dax": {
        "chunk_size": 110,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Power BI DAX formulas and measures"
    },
    "mcode": {
        "chunk_size": 115,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Power Query M-code and transformations"
    },
    "powershell": {
        "chunk_size": 100,
        "enable_redaction": True,  # May contain paths, credentials
        "audit_level": "enhanced",
        "priority": "normal",
        "description": "PowerShell scripts and automation"
    },
    "repository": {
        "chunk_size": 150,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "low",
        "description": "Git repositories, version control, code management"
    },
    
    # ========================================================================
    # PRODUCT/SYSTEM DOMAINS
    # ========================================================================
    "cad": {
        "chunk_size": 90,
        "enable_redaction": True,  # CAD data may contain sensitive incident info
        "audit_level": "enhanced",
        "priority": "high",
        "description": "CAD (Computer-Aided Dispatch) system data and operations"
    },
    "rms": {
        "chunk_size": 85,
        "enable_redaction": True,  # RMS contains sensitive law enforcement data
        "audit_level": "full",
        "priority": "high",
        "description": "RMS (Records Management System) data and operations"
    },
    "arcgis": {
        "chunk_size": 100,
        "enable_redaction": False,  # GIS data typically not sensitive
        "audit_level": "basic",
        "priority": "normal",
        "description": "ArcGIS, ArcPy, and geospatial operations"
    },
    "excel": {
        "chunk_size": 130,
        "enable_redaction": True,  # Excel files may contain sensitive data
        "audit_level": "enhanced",
        "priority": "normal",
        "description": "Excel spreadsheets, formulas, and data processing"
    },
    "scrpa": {
        "chunk_size": 95,
        "enable_redaction": True,  # SCRPA is law enforcement related
        "audit_level": "full",
        "priority": "high",
        "description": "SCRPA (South County Regional Police Analytics) system"
    },
    "fire": {
        "chunk_size": 90,
        "enable_redaction": True,  # Fire department data may contain sensitive incident info
        "audit_level": "enhanced",
        "priority": "high",
        "description": "Fire department operations, incidents, and emergency response"
    },
    "ems": {
        "chunk_size": 90,
        "enable_redaction": True,  # EMS data may contain sensitive patient/incident info
        "audit_level": "enhanced",
        "priority": "high",
        "description": "Emergency Medical Services operations, incidents, and patient care"
    },
    "dashboard": {
        "chunk_size": 120,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Dashboards, visualizations, and reporting"
    },
    
    # ========================================================================
    # AI/CHAT DOMAINS
    # ========================================================================
    "claude": {
        "chunk_size": 150,  # Chat logs are typically longer
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Claude AI conversation logs and chat sessions"
    },
    "chatgpt": {
        "chunk_size": 150,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "ChatGPT conversation logs and chat sessions"
    },
    "ai-chat": {
        "chunk_size": 150,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "General AI chat logs and conversation content"
    },
    
    # ========================================================================
    # DATA OPERATIONS DOMAINS
    # ========================================================================
    "data-cleaning": {
        "chunk_size": 110,
        "enable_redaction": True,  # Cleaning operations may expose data patterns
        "audit_level": "enhanced",
        "priority": "normal",
        "description": "Data cleaning, validation, and sanitization operations"
    },
    "data-export": {
        "chunk_size": 120,
        "enable_redaction": True,  # Exports may contain sensitive data
        "audit_level": "enhanced",
        "priority": "normal",
        "description": "Data export, extraction, and output operations"
    },
    "etl": {
        "chunk_size": 115,
        "enable_redaction": True,  # ETL pipelines may process sensitive data
        "audit_level": "enhanced",
        "priority": "normal",
        "description": "ETL (Extract, Transform, Load) pipelines and workflows"
    },
    
    # ========================================================================
    # LEGACY/COMPATIBILITY DOMAINS (maintained for backward compatibility)
    # ========================================================================
    "police": {
        "chunk_size": 85,
        "enable_redaction": True,
        "audit_level": "full",
        "priority": "high",
        "description": "Legacy: Police-related content (prefer 'cad' or 'rms')"
    },
    "admin": {
        "chunk_size": 150,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Legacy: Admin content (default fallback)"
    },
    "legal": {
        "chunk_size": 100,
        "enable_redaction": True,
        "audit_level": "full",
        "priority": "high",
        "description": "Legacy: Legal content (high sensitivity)"
    },
    
    # ========================================================================
    # DEFAULT FALLBACK
    # ========================================================================
    "default": {
        "chunk_size": 150,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal",
        "description": "Default configuration for unrecognized domains"
    }
}

# Setup enhanced logging
def setup_logging():
    log_file = CONFIG.get("log_file", "logs/watcher.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Rotate log if it's too large
    if os.path.exists(log_file) and os.path.getsize(log_file) > 5 * 1024 * 1024:  # 5MB
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs/watcher_archive_{timestamp}.log"
        shutil.move(log_file, archive_name)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

metrics_executor = ThreadPoolExecutor(max_workers=1)


class NotificationRateLimiter:
    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._last_sent: Dict[str, float] = {}

    def should_send(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            last = self._last_sent.get(key, 0.0)
            if now - last >= self.window_seconds:
                self._last_sent[key] = now
                return True
            return False


notification_rate_limiter = NotificationRateLimiter()


def notify_with_rate_limit(key: str, func, *args, **kwargs) -> None:
    if not notification_rate_limiter.should_send(key):
        return
    try:
        func(*args, **kwargs)
    except Exception as notify_error:
        logger.warning("Notification send failed for %s: %s", key, notify_error)

# Initialize database and notification systems with timeout and retry
def init_database_with_retry():
    """Initialize database with retry logic to handle locking issues"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            db = ChunkerDatabase()
            logger.info("Database initialized successfully")
            return db
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
                time.sleep(2)
            else:
                logger.error(f"Database initialization failed after {max_retries} attempts: {e}")
                return None

db = init_database_with_retry()
notifications = NotificationSystem()

# Database queue for sequential DB operations to prevent locking
db_queue = queue.Queue()

def db_retry(func, max_attempts=5):
    """Retry database operations with exponential backoff and jitter"""
    for attempt in range(max_attempts):
        try:
            return func()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_attempts - 1:
                wait_time = (2 ** attempt) + random.random()
                logger.warning(f"Database locked in db_retry, retrying in {wait_time:.2f}s (attempt {attempt + 1}/{max_attempts})")
                time.sleep(wait_time)
            else:
                logger.error(f"Database operation failed after {max_attempts} attempts: {e}")
                raise
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            raise

def db_worker(q):
    """Dedicated thread to process database operations sequentially"""
    while True:
        try:
            func, args, kwargs = q.get()
            if func is None:  # Shutdown signal
                break
            try:
                db_retry(lambda: func(*args, **kwargs))
            except Exception as e:
                logger.error(f"DB queue error processing {func.__name__}: {e}")
            finally:
                q.task_done()
        except Exception as e:
            logger.error(f"DB worker error: {e}")
            q.task_done()

# Start database worker thread
if db:
    db_worker_thread = threading.Thread(target=db_worker, args=(db_queue,), daemon=True, name="DBWorker")
    db_worker_thread.start()
    logger.info("Database queue worker thread started")

# Enhanced session statistics
session_stats = {
    "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "files_processed": 0,
    "chunks_created": 0,
    "zero_byte_prevented": 0,
    "errors": 0,
    "total_sentences_processed": 0,
    "total_bytes_created": 0,
    "parallel_jobs_completed": 0,
    "department_breakdown": {},
    "skipped_unsupported": 0,
    "performance_metrics": {
        "avg_processing_time": 0,
        "peak_memory_usage": 0,
        "peak_cpu_usage": 0
    },
    "deduplication": {
        "duplicates_detected": 0,
        "chunks_skipped": 0
    },
    "file_deduplication": {
        "existing_files_found": 0,
        "files_skipped": 0,
        "content_matches": 0,
        "content_differences": 0
    },
    "incremental_updates": {
        "processed_files": 0,
        "skipped_files": 0,
        "removed_artifacts": 0,
    },
    "tag_counts": {},
}

def initialize_feature_components() -> None:
    """Refresh feature toggle dependencies (metadata, dedup, monitoring, incremental)."""
    global METADATA_CONFIG, METADATA_ENABLED
    global DEDUP_CONFIG, dedup_manager
    global INCREMENTAL_CONFIG, version_tracker
    global monitoring

    METADATA_CONFIG = CONFIG.get("metadata_enrichment", {}) or {}
    METADATA_ENABLED = bool(METADATA_CONFIG.get("enabled", False))

    DEDUP_CONFIG = CONFIG.get("deduplication", {}) or {}
    dedup_manager = None
    if DEDUP_CONFIG.get("enabled"):
        if DeduplicationManager is None:
            logger.info(
                "Deduplication disabled: ChromaDB/hnswlib not installed (optional). "
                "Install with `pip install chromadb hnswlib` to enable duplicate pruning."
            )
        else:
            try:
                dedup_manager = DeduplicationManager(
                    persist_directory=CONFIG.get("chroma_persist_dir", "./chroma_db"),
                    config=DEDUP_CONFIG,
                    preload=True,
                )
                logger.info(
                    "Deduplication initialized with %d known hashes",
                    len(dedup_manager.hash_index),
                )
            except ImportError as import_error:
                logger.info(
                    "Deduplication disabled: %s. Install with `pip install chromadb hnswlib` "
                    "to enable duplicate pruning.",
                    import_error,
                )
                dedup_manager = None
            except Exception as dedup_error:
                logger.warning(
                    "Failed to initialize deduplication manager: %s", dedup_error
                )
                dedup_manager = None

    INCREMENTAL_CONFIG = CONFIG.get("incremental_updates", {}) or {}
    version_tracker = None
    if INCREMENTAL_CONFIG.get("enabled"):
        try:
            tracker_config = dict(INCREMENTAL_CONFIG)
            tracker_config.setdefault("base_dir", base_path)
            version_tracker = VersionTracker(tracker_config, logger=logger)
            logger.info(
                "Incremental updates enabled. Tracking file: %s",
                version_tracker.version_file,
            )
        except Exception as tracker_error:
            logger.warning(
                "Failed to initialize version tracker: %s", tracker_error
            )
            version_tracker = None

    if monitoring and getattr(monitoring, "enabled", False):
        try:
            monitoring.stop_monitoring()
        except Exception as stop_error:  # noqa: BLE001
            logger.debug("Failed to stop previous monitoring thread: %s", stop_error)

    monitoring = MonitoringSystem(
        CONFIG,
        db=db,
        notification_system=notifications,
        logger=logger,
    )


def reload_feature_components() -> None:
    """Public helper for tests to reinitialize feature dependencies."""
    initialize_feature_components()


initialize_feature_components()

def load_manifest_data(file_path: Path) -> Tuple[Dict[str, Any], Path, Optional[str]]:
    """
    Load an existing .origin.json manifest if available; otherwise return an empty dict.
    """
    manifest_path = file_path.with_name(f"{file_path.name}.origin.json")
    manifest_data: Dict[str, Any] = {}
    content_hash: Optional[str] = None
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8-sig") as manifest_file:
                manifest_data = json.load(manifest_file)
            content_hash = manifest_data.get("content_hash") or manifest_data.get(
                "last_content_hash"
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning(
                "Failed to parse manifest for %s: %s",
                file_path.name,
                exc,
                exc_info=True,
            )
            manifest_data = {}
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load manifest for %s: %s", file_path.name, exc, exc_info=True
            )
            manifest_data = {}
    return manifest_data, manifest_path, content_hash


def should_process_file(file_path: Path) -> bool:
    """Check if file should be processed - skip manifests and archives"""
    name_l = file_path.name.lower()
    if ".origin.json" in name_l:
        return False
    file_str = str(file_path)

    # Skip manifest files (.origin.json) - catch both exact suffix and embedded patterns
    if file_path.name.endswith('.origin.json') or '.origin.json.' in file_path.name:
        return False

    # Skip files in archive directory
    if '03_archive' in file_str or '\\03_archive\\' in file_str:
        return False

    # Skip files in output directory
    if '04_output' in file_str or '\\04_output\\' in file_str:
        return False

    return True


def sanitize_folder_name(base_name: str, max_length: int = 60) -> str:
    """Sanitize and limit folder name length to prevent Windows path issues"""
    import re
    clean_name = base_name

    # Remove .origin.json suffixes (but not the word "origin" in general)
    # Use regex to only match the actual suffix pattern
    clean_name = re.sub(r'\.origin\.json$', '', clean_name)
    # Remove multiple .origin.json patterns that may have accumulated
    while '.origin.json' in clean_name:
        clean_name = re.sub(r'\.origin\.json', '', clean_name)

    # Remove invalid Windows path characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        clean_name = clean_name.replace(char, '_')

    # Truncate to max length - do NOT add ellipsis to folder names
    # Windows may not handle "..." in folder names reliably
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length]

    return clean_name


def file_hash(path: Path) -> str:
    """
    Calculate SHA256 hash of file content using streaming (memory-safe).
    
    Args:
        path: Path to file to hash
        
    Returns:
        SHA256 hex digest of file content
    """
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.warning(f"Error hashing file {path}: {e}")
        return ""


def check_file_exists_and_compare(content: str, file_path: Path) -> Tuple[bool, bool]:
    """
    Check if file exists and compare content using hash comparison (memory-safe).
    
    Uses streaming hash calculation to avoid OOM on large files.
    
    Args:
        content: Content to write
        file_path: Path to check
        
    Returns:
        Tuple of (file_exists, content_matches)
        If file doesn't exist, returns (False, False)
        If file exists, returns (True, True) if content matches, (True, False) if different
    """
    if not file_path.exists():
        return (False, False)
    
    try:
        # Fast path: compare file sizes first (avoids hashing if sizes differ)
        content_bytes = content.encode("utf-8") if isinstance(content, str) else str(content).encode("utf-8")
        content_size = len(content_bytes)
        existing_size = file_path.stat().st_size
        
        if content_size != existing_size:
            # Sizes differ, content must be different
            return (True, False)
        
        # Sizes match, compare hashes for content verification
        new_hash = hashlib.sha256(content_bytes).hexdigest()
        existing_hash = file_hash(file_path)
        
        if not existing_hash:
            # Could not hash existing file, assume different
            return (True, False)
        
        content_matches = new_hash == existing_hash
        return (True, content_matches)
    except Exception as e:
        logger.warning(f"Hash compare failed for {file_path}: {e}")
        # If we can't compare, assume it's different
        return (True, False)


def write_chunk_files(doc_id: str, chunks: List[str], out_root: str, 
                      check_duplicates: bool = True) -> List[str]:
    """
    Write chunk files to output directory with duplicate checking.
    
    Args:
        doc_id: Document identifier (folder name)
        chunks: List of chunk texts to write
        out_root: Output root directory
        check_duplicates: If True, check for existing files and skip duplicates
        
    Returns:
        List of written file paths
    """
    written: List[str] = []
    base = Path(out_root) / doc_id
    base.mkdir(parents=True, exist_ok=True)

    for i, text in enumerate(chunks):
        p = base / f"chunk_{i:05d}.txt"
        
        # Check for existing file if duplicate checking is enabled
        if check_duplicates:
            file_exists, content_matches = check_file_exists_and_compare(text, p)
            
            if file_exists:
                session_stats["file_deduplication"]["existing_files_found"] += 1
                
                if content_matches:
                    # File exists with identical content - skip
                    logger.debug(f"Skipping duplicate file (identical content): {p.name}")
                    session_stats["file_deduplication"]["files_skipped"] += 1
                    session_stats["file_deduplication"]["content_matches"] += 1
                    
                    # Track skipped duplicates in database for audit
                    if db:
                        try:
                            db_queue.put((
                                db.log_processing,
                                (
                                    str(p.parent.parent.name),  # source file name
                                    0,  # original_size (duplicate, so 0)
                                    0,  # chunks_created (duplicate, so 0)
                                    0,  # total_bytes (duplicate, so 0)
                                    0.0,  # processing_time (duplicate, so 0)
                                    True,  # success
                                    f"Duplicate file skipped: {p.name}",
                                    "admin"  # department
                                ),
                                {}
                            ))
                        except Exception as db_error:
                            logger.debug(f"Failed to log duplicate skip to database: {db_error}")
                    
                    written.append(str(p))  # Still return path since file "exists"
                    continue
                else:
                    # File exists but content is different - log warning but overwrite
                    logger.warning(
                        f"File exists with different content, overwriting: {p.name}"
                    )
                    session_stats["file_deduplication"]["content_differences"] += 1
        
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(text if isinstance(text, str) else str(text))
            written.append(str(p))
        except Exception as e:
            logger.exception("Chunk write failed for %s: %s", p, e)
    return written


def copy_manifest_sidecar(src_manifest: str, dst_path: str):
    try:
        dst = Path(dst_path)
        # Ensure parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Check if parent directory actually exists before trying to write
        if not dst.parent.exists():
            logger.error("Parent directory does not exist for manifest copy: %s", dst.parent)
            return
        # Check if source exists
        if not Path(src_manifest).exists():
            logger.warning("Source manifest does not exist: %s", src_manifest)
            return
        with open(src_manifest, "r", encoding="utf-8") as fsrc, open(dst, "w", encoding="utf-8") as fdst:
            fdst.write(fsrc.read())
        logger.debug("Successfully copied manifest from %s to %s", src_manifest, dst_path)
    except Exception as e:
        logger.exception("Manifest copy failed from %s to %s: %s", src_manifest, dst_path, e)


def safe_file_move(source_path: Path, dest_path: Path, max_retries: int = 3) -> bool:
    """Safely move file with retry logic and missing-file detection"""
    for attempt in range(max_retries):
        try:
            # Check if source exists BEFORE attempting move
            if not source_path.exists():
                logger.info(f"File already moved/removed (likely by another worker): {source_path.name}")
                return True  # Not an error - file is gone

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Perform the move
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved: {source_path.name} -> {dest_path}")
            return True

        except FileNotFoundError:
            # File vanished between exists() check and move()
            logger.info(f"File vanished during move (race condition): {source_path.name}")
            return True  # Success - file is gone

        except PermissionError as e:
            if attempt < max_retries - 1:
                wait_time = 0.5 * (attempt + 1)
                logger.warning(f"Move retry {attempt + 1}/{max_retries} for {source_path.name}, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                logger.error(f"Move failed after {max_retries} attempts: {e}")
                return False

        except Exception as e:
            logger.error(f"Unexpected move error: {e}")
            return False

    return False


def update_session_tag_counts(tags: Iterable[str]) -> None:
    if not tags:
        return
    for tag in tags:
        if not tag:
            continue
        session_stats["tag_counts"][tag] = session_stats["tag_counts"].get(tag, 0) + 1


def cleanup_previous_artifacts(artifact_paths: Iterable[str]) -> int:
    """Remove previously generated artifacts recorded by the version tracker."""
    removed = 0
    for artifact in artifact_paths:
        if not artifact:
            continue
        target = Path(artifact)
        try:
            if target.is_file():
                target.unlink()
                removed += 1
            elif target.is_dir():
                shutil.rmtree(target)
                removed += 1
        except FileNotFoundError:
            continue
        except Exception as cleanup_error:  # noqa: BLE001
            logger.debug("Failed to remove tracked artifact %s: %s", target, cleanup_error)
    return removed


def _age_minutes(path: Path) -> float:
    """
    Calculate file age in minutes.
    
    Args:
        path: Path to file
        
    Returns:
        Age in minutes, or float('inf') if file not found
    """
    try:
        return (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds() / 60.0
    except FileNotFoundError:
        return float("inf")


def is_effectively_stable(path: Path, config: dict) -> bool:
    """
    Check if file is effectively stable (bypass expensive checks for old files).
    
    Files older than stability_skip_minutes are treated as stable without calling
    file_is_settled() to avoid bottlenecks on large backlogs.
    
    Args:
        path: Path to file to check
        config: Configuration dictionary
        
    Returns:
        True if file is stable (or old enough to assume stable), False otherwise
    """
    skip_minutes = config.get("stability_skip_minutes", 10)
    age_min = _age_minutes(path)
    
    if age_min > skip_minutes:
        # Old file → assume settled (skip expensive stability check)
        return True
    
    # Fall back to original stability check for recently modified files
    stability_timeout = config.get("file_stability_timeout", 2)
    return file_is_settled(path, seconds=stability_timeout)


def get_department_config(file_path):
    """
    Determine department configuration based on file path, filename, or metadata tags.
    
    Detection priority:
    1. File path/filename keywords (most specific match wins)
    2. Metadata tags from sidecar/origin.json (if available)
    3. Default fallback
    
    Args:
        file_path: Path to the file being processed
        
    Returns:
        Merged configuration dictionary with department-specific settings
    """
    file_path_obj = Path(file_path)
    path_str = str(file_path_obj).lower()
    filename_lower = file_path_obj.name.lower()
    
    # Domain detection patterns with priority order (more specific first)
    # Pattern: (domain_key, [list of keywords to match], priority_score, [file_extensions])
    domain_patterns = [
        # High-priority: Specific product/system domains (check first)
        ("scrpa", ["scrpa"], 100, []),
        ("cad", ["cad", "computer-aided-dispatch", "computer aided dispatch"], 95, []),
        ("rms", ["rms", "records-management", "records management"], 95, []),
        ("fire", ["fire", "fire-department", "fire_department", "firefighter", "firefighting"], 95, []),
        ("ems", ["ems", "emergency-medical", "emergency_medical", "paramedic", "ambulance"], 95, []),
        
        # Product/system domains (check before code to prefer system over language)
        ("arcgis", ["arcgis", "arcpy", "gis", "geospatial"], 95, []),  # Higher priority than python
        
        # Code/scripting domains (check file extensions first)
        ("python", ["python"], 90, [".py"]),
        ("powershell", ["powershell"], 85, [".ps1"]),
        ("sql", ["sql"], 85, [".sql"]),
        ("dax", ["dax", "powerbi", "power_bi", "power-bi"], 85, [".dax"]),
        ("mcode", ["mcode", "m-code", "power-query", "m_query"], 85, [".m", ".pq"]),
        ("excel", ["excel", "xlsx", "spreadsheet"], 85, [".xlsx", ".xls"]),
        ("repository", ["repository", "git", "github"], 75, []),  # Don't match "repo" substring
        ("dashboard", ["dashboard", "visualization", "chart"], 75, []),  # Don't match "report" substring
        
        # Data operations (check before generic matches, but after extensions)
        ("data-cleaning", ["data-cleaning", "data_cleaning", "cleaning", "validate", "validation", "sanitize"], 90, []),
        ("data-export", ["data-export", "data_export", "export", "extract"], 90, []),  # Specific + generic
        ("etl", ["etl", "extract.*transform.*load"], 90, []),
        
        # AI/chat domains (check after code to avoid false positives)
        ("claude", ["claude"], 70, []),
        ("chatgpt", ["chatgpt"], 70, []),
        ("ai-chat", ["chat", "conversation", "chatlog", "chat_log"], 65, []),
        
        # Legacy domains (lower priority, maintained for compatibility)
        ("police", ["police", "law-enforcement", "law_enforcement"], 60, []),
        ("legal", ["legal", "attorney", "lawsuit"], 60, []),
        ("admin", ["admin", "administrative"], 50, []),
    ]
    
    # Find best matching domain based on path/filename
    best_match = None
    best_score = 0
    file_ext = file_path_obj.suffix.lower()
    
    for domain_key, keywords, priority, extensions in domain_patterns:
        # Check file extension first (highest priority)
        if extensions and file_ext in extensions:
            score = priority + 20  # Extension match gets highest priority
            if score > best_score:
                best_score = score
                best_match = domain_key
                continue
        
        # Check if any keyword matches in path or filename (whole word matching)
        for keyword in keywords:
            # Use word boundaries for more precise matching (avoid substring false positives)
            keyword_pattern = r'\b' + re.escape(keyword).replace(r'\.', r'\.') + r'\b'
            # Also check for exact matches without word boundaries for special cases
            simple_match = keyword in filename_lower or keyword in path_str
            
            if re.search(keyword_pattern, path_str, re.IGNORECASE) or simple_match:
                # Prefer exact filename matches
                score = priority + (15 if keyword in filename_lower else 0)
                if score > best_score:
                    best_score = score
                    best_match = domain_key
                    break
    
    # Try to extract department from metadata if available
    # Look for sidecar or origin.json files in the same directory
    metadata_domain = None
    if file_path_obj.parent.exists():
        # Check for .origin.json files (manifest)
        origin_files = list(file_path_obj.parent.glob("*.origin.json"))
        if not origin_files:
            # Check parent directory for sidecar
            sidecar_files = list(file_path_obj.parent.glob("*.sidecar.json"))
            if sidecar_files:
                origin_files = sidecar_files
        
        # Try to read metadata from first available file
        for meta_file in origin_files[:1]:
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                
                # Extract tags from metadata
                tags = []
                if "metadata_enrichment" in meta_data:
                    tags = meta_data["metadata_enrichment"].get("tags", [])
                elif "metadata" in meta_data:
                    tags = meta_data["metadata"].get("tags", [])
                
                # Check if any tag matches a domain
                if tags:
                    tag_str = " ".join(str(tag).lower() for tag in tags)
                    for domain_key, keywords, _ in domain_patterns:
                        for keyword in keywords:
                            if keyword in tag_str:
                                metadata_domain = domain_key
                                break
                        if metadata_domain:
                            break
                if metadata_domain:
                    break
            except Exception:
                pass
    
    # Use metadata domain if found and better than path-based match
    dept = best_match or metadata_domain or CONFIG.get("default_department", "default")
    
    # Merge default config with department-specific settings
    dept_config = DEPARTMENT_CONFIGS.get(dept, DEPARTMENT_CONFIGS.get("default", {}))
    merged_config = CONFIG.copy()
    merged_config.update(dept_config)
    merged_config["department"] = dept
    
    # Log department detection if debugging
    if CONFIG.get("log_level", "INFO") == "DEBUG":
        logger.debug(f"Department detected for {file_path_obj.name}: {dept} "
                    f"(match_type={'path' if best_match else 'metadata' if metadata_domain else 'default'})")
    
    return merged_config

def _log_system_metrics_sync():
    """Log comprehensive system metrics (synchronous worker)"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # Count active processes
        active_processes = len([p for p in psutil.process_iter() if p.is_running()])
        
        # Update session stats
        session_stats["performance_metrics"]["peak_cpu_usage"] = max(
            session_stats["performance_metrics"]["peak_cpu_usage"], cpu_percent
        )
        session_stats["performance_metrics"]["peak_memory_usage"] = max(
            session_stats["performance_metrics"]["peak_memory_usage"], memory.percent
        )
        
        # Queue database operation instead of direct call
        if db:
            db_queue.put((db.log_system_metrics,
                         (cpu_percent, memory.percent, (disk.used / disk.total) * 100, active_processes), {}))
        
        logger.info(f"System metrics - CPU: {cpu_percent}%, Memory: {memory.percent}%, "
                   f"Disk: {(disk.used / disk.total) * 100:.1f}%, Processes: {active_processes}")
        
        # Send alerts if thresholds exceeded
        if cpu_percent > 90:
            notify_with_rate_limit(
                "cpu-critical",
                notifications.send_threshold_alert,
                "CPU Usage",
                f"{cpu_percent}%",
                "90%",
                "critical",
            )
        elif cpu_percent > 80:
            notify_with_rate_limit(
                "cpu-warning",
                notifications.send_threshold_alert,
                "CPU Usage",
                f"{cpu_percent}%",
                "80%",
                "warning",
            )
        
        if memory.percent > 90:
            notify_with_rate_limit(
                "memory-critical",
                notifications.send_threshold_alert,
                "Memory Usage",
                f"{memory.percent}%",
                "90%",
                "critical",
            )
        elif memory.percent > 80:
            notify_with_rate_limit(
                "memory-warning",
                notifications.send_threshold_alert,
                "Memory Usage",
                f"{memory.percent}%",
                "80%",
                "warning",
            )
            
    except Exception as e:
        logger.error(f"Failed to log system metrics: {e}")


def log_system_metrics():
    metrics_executor.submit(_log_system_metrics_sync)

@lru_cache(maxsize=512)
def _cached_sent_tokenize(text: str) -> Tuple[str, ...]:
    return tuple(sent_tokenize(text))


def chunk_text_enhanced(text, limit, department_config):
    """Enhanced chunking with department-specific rules"""
    if not text or len(text.strip()) < 10:
        logger.warning("Text too short for chunking")
        return []
    
    try:
        sentences = list(_cached_sent_tokenize(text))
        if not sentences:
            logger.warning("No sentences found in text")
            return []
        
        # Apply department-specific chunking rules
        if department_config.get("enable_redaction"):
            sentences = apply_redaction_rules(sentences)
        
        chunks = []
        max_chars = department_config.get("max_chunk_chars", CONFIG.get("max_chunk_chars", 30000))
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed limits
            if (len(current_chunk) >= limit or 
                current_length + sentence_length > max_chars) and current_chunk:
                
                chunk_text = " ".join(current_chunk)
                if len(chunk_text.strip()) > 0:
                    chunks.append(chunk_text)
                
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text.strip()) > 0:
                chunks.append(chunk_text)
        
        session_stats["total_sentences_processed"] += len(sentences)
        logger.info(f"Created {len(chunks)} chunks from {len(sentences)} sentences")
        return chunks
        
    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        if db:
            db_queue.put((db.log_error, ("ChunkingError", str(e), traceback.format_exc()), {}))
        session_stats["errors"] += 1
        return []

def apply_redaction_rules(sentences):
    """Apply redaction rules for sensitive departments"""
    import re
    
    redaction_patterns = [
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]'),  # SSN
        (r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE-REDACTED]'),  # Phone
        (r'\b\d{1,5}\s+\w+\s+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd)\b', '[ADDRESS-REDACTED]'),  # Address
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL-REDACTED]')  # Email
    ]
    
    redacted_sentences = []
    for sentence in sentences:
        redacted = sentence
        for pattern, replacement in redaction_patterns:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        redacted_sentences.append(redacted)
    
    return redacted_sentences

def validate_chunk_content_enhanced(chunk, min_length=50, department_config=None):
    """Enhanced chunk validation with department-specific rules"""
    if not chunk or len(chunk.strip()) < min_length:
        return False
    
    word_count = len(chunk.split())
    if word_count < 10:
        return False
    
    # Check for reasonable content-to-whitespace ratio
    if len(chunk.strip()) / len(chunk) < 0.7:
        return False
    
    # Department-specific validation
    if department_config and department_config.get("audit_level") == "full":
        # Additional validation for high-security departments
        if any(pattern in chunk.lower() for pattern in ["[redacted]", "[error]", "[corrupt]"]):
            logger.warning("Chunk contains redaction or error markers")
    
    return True

def process_file_enhanced(file_path, config):
    """Enhanced file processing with comprehensive tracking"""
    # CRITICAL: Skip manifest files and archives to prevent recursion
    if not should_process_file(file_path):
        return True

    start_time = time.time()
    safe_text_extensions = set(
        config.get(
            "text_extensions",
            config.get(
                "supported_extensions",
                [".txt", ".md", ".json", ".csv", ".py", ".log"],
            ),
        )
    )
    file_extension = file_path.suffix.lower()
    if file_extension not in safe_text_extensions:
        logger.info(
            f"Skipping unsupported file type ({file_extension}): {file_path.name}"
        )
        session_stats["skipped_unsupported"] = (
            session_stats.get("skipped_unsupported", 0) + 1
        )
        return True
    department_config = get_department_config(file_path)
    department = department_config.get("department", "default")
    
    logger.info(f"Processing file: {file_path.name} (Department: {department})")
    
    try:
        content_hash: Optional[str] = None
        # Wait for file stability
        if not wait_for_file_stability(file_path):
            error_msg = f"File not stable, skipping: {file_path.name}"
            logger.error(error_msg)
            if db:
                db_queue.put((db.log_error, ("FileStabilityError", error_msg), {"filename": str(file_path)}))
            return False

        # Read file with multiple attempts
        text = None
        original_size = 0
        used_encoding: Optional[str] = None
        for attempt in range(3):
            try:
                text, used_encoding = read_file_with_fallback(file_path)
                original_size = len(text.encode("utf-8", errors="ignore"))
                break
            except Exception as e:
                logger.warning(f"Read attempt {attempt+1} failed for {file_path.name}: {e}")
                if attempt < 2:
                    time.sleep(1)
        
        if text is None:
            error_msg = f"Could not read {file_path.name} after 3 attempts"
            logger.error(error_msg)
            if db:
                db_queue.put((db.log_error, ("FileReadError", error_msg), {"filename": str(file_path)}))
            return False

        if used_encoding and used_encoding not in {"utf-8", "utf-8-sig"}:
            if used_encoding == "binary-fallback":
                logger.warning(
                    "Processed %s using binary fallback decoding; some characters may be replaced.",
                    file_path.name,
                )
            else:
                logger.info("Processed %s using %s encoding.", file_path.name, used_encoding)

        # Load manifest metadata and enrich (optional)
        manifest_data, manifest_path, stored_content_hash = load_manifest_data(file_path)
        if stored_content_hash:
            content_hash = stored_content_hash
        if METADATA_ENABLED:
            enrichment: EnrichmentResult = enrich_metadata(
                text,
                file_path,
                manifest_data=manifest_data,
            )
            manifest_data = merge_manifest_metadata(manifest_data, enrichment)
            update_session_tag_counts(enrichment.tags)
            if enrichment.tags:
                logger.info(
                    "Metadata enrichment tags for %s: %s",
                    file_path.name,
                    ", ".join(enrichment.tags),
                )
        else:
            enrichment = EnrichmentResult(tags=[], metadata={}, summaries={})

        manifest_data["last_processed_at"] = datetime.now().isoformat()

        # Prefer department inferred from enrichment/manifest when available
        if METADATA_ENABLED:
            enriched_department = (
                manifest_data.get("department")
                or enrichment.metadata.get("department")
                or department
            )
            if enriched_department and enriched_department != department:
                department = enriched_department
                department_config["department"] = enriched_department
        manifest_data["department"] = department

        try:
            dump_json(manifest_data, manifest_path)
        except Exception as manifest_error:  # noqa: BLE001
            logger.warning(
                "Failed to persist manifest metadata for %s: %s",
                file_path.name,
                manifest_error,
            )

        # Validate input text
        min_size = department_config.get("min_file_size_bytes", 100)
        if len(text.strip()) < min_size:
            error_msg = f"File too short ({len(text)} chars), archiving: {file_path.name}"
            logger.info(error_msg)

            # Archive tiny files to prevent repeated warnings
            archive_dir = Path(config.get("archive_dir", "archive"))
            skipped_folder = archive_dir / "skipped_files"
            skipped_folder.mkdir(parents=True, exist_ok=True)

            # Move file and its manifest to skipped folder
            dest_file = skipped_folder / file_path.name
            manifest_file = Path(str(file_path) + ".origin.json")
            dest_manifest = skipped_folder / manifest_file.name

            safe_file_move(file_path, dest_file)
            if manifest_file.exists():
                safe_file_move(manifest_file, dest_manifest)

            if db:
                # Queue database operation instead of direct call
                db_queue.put((db.log_processing, 
                            (str(file_path), original_size, 0, 0, time.time() - start_time, True, error_msg, department), {}))
            return True  # Successfully handled (archived)

        if content_hash:
            manifest_data["last_content_hash"] = content_hash
        elif version_tracker:
            try:
                content_hash = version_tracker.hash_content(text)
                if content_hash:
                    manifest_data["last_content_hash"] = content_hash
            except Exception:
                pass

        # Chunk the text
        sentence_limit = department_config.get("chunk_size", 100)
        chunks = chunk_text_enhanced(text, sentence_limit, department_config)
        
        if not chunks:
            error_msg = f"No valid chunks created for {file_path.name}"
            logger.error(error_msg)
            if db:
                # Queue database operation instead of direct call
                db_queue.put((db.log_processing,
                            (str(file_path), original_size, 0, 0, time.time() - start_time, False, error_msg, department), {}))
            return False

        # Prepare output with organized folder structure
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        # Sanitize to prevent path length issues and remove .origin.json artifacts
        raw_base = Path(file_path.name).stem.replace(" ", "_")
        # Calculate max length accounting for timestamp prefix (~20 chars) and path separators
        timestamp_len = len(timestamp) + 1  # +1 for underscore
        clean_base = sanitize_folder_name(raw_base, max_length=200 - timestamp_len)
        output_folder = str(config.get("output_dir", "output"))

        # Create folder named after the source file with timestamp prefix
        file_output_folder = Path(output_folder) / f"{timestamp}_{clean_base}"

        # Long path handling: ensure total path length is within Windows limits (240 chars safe threshold)
        resolved_path = file_output_folder.resolve()
        if len(str(resolved_path)) > 240:
            logger.warning(f"Path too long ({len(str(resolved_path))} chars), shortening: {file_output_folder}")
            # Create short hash-based folder name
            short_hash = hashlib.md5(clean_base.encode()).hexdigest()[:10]
            date_suffix = datetime.now().strftime("%Y%m%d")
            shortened_base = f"SHORT_{short_hash}_{date_suffix}"
            file_output_folder = Path(output_folder) / shortened_base
            logger.info(f"Shortened folder name to: {shortened_base}")
        
        # Additional safety check for base path (legacy support)
        if len(str(file_output_folder)) > 200:
            logger.warning(f"Path still too long after shortening ({len(str(file_output_folder))}), truncating base name")
            clean_base = sanitize_folder_name(raw_base, max_length=40)
            file_output_folder = Path(output_folder) / f"{timestamp}_{clean_base}"
        
        if version_tracker and file_output_folder.exists():
            try:
                shutil.rmtree(file_output_folder)
                logger.info(
                    "Incremental updates: cleared previous outputs for %s",
                    file_path.name,
                )
            except Exception as cleanup_error:  # noqa: BLE001
                logger.warning(
                    "Incremental updates: failed to clear outputs for %s: %s",
                    file_path.name,
                    cleanup_error,
                )
        
        # Create the folder and store the actual folder name for consistency
        file_output_folder.mkdir(parents=True, exist_ok=True)
        final_folder_name = file_output_folder.name  # Use this for all subfiles to ensure consistency
        
        chunk_files: List[Path] = []
        valid_chunks = 0
        total_chunk_size = 0
        chunk_records: List[Dict[str, Any]] = []
        artifacts_for_distribution: List[Path] = []
        sidecar_path: Optional[Path] = None
        generated_chunk_ids: List[str] = []

        chunk_payloads: List[Dict[str, Any]] = []

        # Write chunks with validation and deduplication
        for i, chunk in enumerate(chunks):
            chunk_index = i + 1

            if not validate_chunk_content_enhanced(chunk, department_config=department_config):
                logger.warning(f"Invalid chunk {chunk_index} skipped for {file_path.name}")
                continue

            if METADATA_ENABLED:
                chunk_metadata = enrich_chunk(chunk, enrichment.tags)
                chunk_tags = chunk_metadata.get("tags", [])
            else:
                chunk_metadata = {
                    "tags": [],
                    "key_terms": [],
                    "summary": "",
                    "char_length": len(chunk),
                }
                chunk_tags = []

            chunk_id = build_chunk_id(timestamp, clean_base, chunk_index)
            chunk_dedup_id = chunk_id
            dedup_hash_value = None

            if dedup_manager:
                try:
                    is_duplicate, dedup_hash_value, existing_ids = dedup_manager.is_duplicate(
                        chunk,
                        chunk_id=chunk_dedup_id,
                    )
                except Exception as dedup_error:
                    logger.warning(
                        "Deduplication check failed for %s chunk %s: %s",
                        file_path.name,
                        chunk_index,
                        dedup_error,
                    )
                    is_duplicate, dedup_hash_value, existing_ids = False, None, []

                if is_duplicate:
                    session_stats["deduplication"]["duplicates_detected"] += 1
                    session_stats["deduplication"]["chunks_skipped"] += 1
                    preview = existing_ids[:3]
                    if len(existing_ids) > 3:
                        preview.append("...")
                    logger.info(
                        "Deduplication skipped duplicate chunk %s (matches: %s)",
                        chunk_dedup_id,
                        preview if preview else "existing chunk",
                    )
                    continue

            chunk_payloads.append(
                {
                    "chunk": chunk if isinstance(chunk, str) else str(chunk),
                    "chunk_metadata": chunk_metadata,
                    "chunk_tags": chunk_tags,
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_index,
                    "chunk_dedup_id": chunk_dedup_id,
                    "dedup_hash_value": dedup_hash_value,
                }
            )

        if not chunk_payloads:
            error_msg = f"No valid chunks created for {file_path.name}"
            logger.error(error_msg)
            if db:
                # Queue database operation instead of direct call
                db_queue.put((db.log_processing,
                            (str(file_path), original_size, 0, 0, time.time() - start_time, False, error_msg, department), {}))
            return False

        chunk_texts = [payload["chunk"] for payload in chunk_payloads]
        # Use final_folder_name to ensure consistency with actual created folder
        # Check config for file-level deduplication toggle
        enable_file_dedup = config.get("enable_file_level_dedup", True)
        written_paths = write_chunk_files(final_folder_name, chunk_texts, output_folder, 
                                         check_duplicates=enable_file_dedup)

        if len(written_paths) != len(chunk_payloads):
            logger.warning(
                "Chunk write mismatch for %s: expected %d, wrote %d",
                file_path.name,
                len(chunk_payloads),
                len(written_paths),
            )

        generated_chunk_ids = []

        for payload, path_str in zip(chunk_payloads, written_paths):
            chunk_path = Path(path_str)
            try:
                written_size = os.path.getsize(chunk_path)
            except OSError:
                logger.warning("Chunk file missing after write attempt: %s", chunk_path)
                continue

            if written_size <= 0:
                logger.warning(f"Zero-byte chunk prevented: {chunk_path.name}")
                session_stats["zero_byte_prevented"] += 1
                try:
                    chunk_path.unlink()
                except FileNotFoundError:
                    pass
                except Exception as unlink_error:
                    logger.debug("Failed to remove zero-byte chunk %s: %s", chunk_path, unlink_error)
                continue

            chunk_files.append(chunk_path)
            artifacts_for_distribution.append(chunk_path)
            valid_chunks += 1
            total_chunk_size += written_size
            logger.info(
                "Created chunk: %s (%d chars, %d bytes)",
                chunk_path.name,
                len(payload["chunk"]),
                written_size,
            )

            if dedup_manager and payload.get("dedup_hash_value"):
                try:
                    dedup_manager.add_hash(payload["dedup_hash_value"], payload["chunk_dedup_id"])
                except Exception as dedup_error:
                    logger.debug("Failed to register dedup hash for %s: %s", chunk_path, dedup_error)

            chunk_record = {
                "chunk_id": payload["chunk_id"],
                "chunk_index": payload["chunk_index"],
                "file": chunk_path.name,
                "tags": payload["chunk_tags"],
                "key_terms": payload["chunk_metadata"].get("key_terms", []),
                "summary": payload["chunk_metadata"].get("summary", ""),
                "char_length": payload["chunk_metadata"].get("char_length", len(payload["chunk"])),
                "byte_length": written_size,
            }
            chunk_records.append(chunk_record)
            generated_chunk_ids.append(payload["chunk_id"])
            if METADATA_ENABLED:
                update_session_tag_counts(payload["chunk_tags"])

        if generated_chunk_ids:
            manifest_data["chunk_ids"] = generated_chunk_ids

        # Use final_folder_name directly for consistency (folder already includes timestamp)
        manifest_copy_path = file_output_folder / f"{final_folder_name}.origin.json"
        try:
            if manifest_path.exists():
                # Handle version conflicts with _v2, _v3 suffixes (like migration script)
                if manifest_copy_path.exists():
                    version = 2
                    while manifest_copy_path.exists():
                        manifest_copy_path = file_output_folder / f"{final_folder_name}.origin_v{version}.json"
                        version += 1
                        if version > 10:  # Safety limit
                            logger.warning(f"Too many manifest versions, using latest: {manifest_copy_path.name}")
                            break
                    logger.info(f"Manifest conflict resolved, using version: {manifest_copy_path.name}")
                
                # Use shutil.copy for better error handling (as recommended by Grok)
                try:
                    shutil.copy(str(manifest_path), str(manifest_copy_path))
                    artifacts_for_distribution.append(manifest_copy_path)
                except OSError as copy_error:
                    logger.warning("Failed to copy manifest using shutil, trying copy_manifest_sidecar: %s", copy_error)
                    copy_manifest_sidecar(str(manifest_path), str(manifest_copy_path))
                    artifacts_for_distribution.append(manifest_copy_path)
            else:
                logger.warning("Manifest source missing for %s, skipping copy.", file_path.name)
        except Exception as manifest_copy_error:  # noqa: BLE001
            logger.warning(
                "Failed to write manifest copy for %s: %s",
                file_path.name,
                manifest_copy_error,
            )

        if chunk_records and config.get("enable_json_sidecar", True):
            # Use final_folder_name for consistency (includes timestamp prefix)
            sidecar_filename = f"{final_folder_name}{SIDECAR_SUFFIX}"
            sidecar_path = file_output_folder / sidecar_filename
            
            # Handle version conflicts with _v2, _v3 suffixes
            if sidecar_path.exists():
                version = 2
                while sidecar_path.exists():
                    sidecar_path = file_output_folder / f"{final_folder_name}_v{version}{SIDECAR_SUFFIX}"
                    version += 1
                    if version > 10:  # Safety limit
                        logger.warning(f"Too many sidecar versions, using latest: {sidecar_path.name}")
                        break
                logger.info(f"Sidecar conflict resolved, using version: {sidecar_path.name}")
            
            sidecar_payload = build_sidecar_payload(
                source_path=file_path,
                manifest_path=manifest_copy_path,
                enrichment=enrichment,
                chunk_records=chunk_records,
                timestamp=timestamp,
            )
            try:
                dump_json(sidecar_payload, sidecar_path)
                artifacts_for_distribution.append(sidecar_path)
                logger.info(
                    "Created sidecar %s with %d tags",
                    sidecar_path.name,
                    len(enrichment.tags),
                )
            except Exception as sidecar_error:  # noqa: BLE001
                logger.warning(
                    "Failed to write sidecar for %s: %s",
                    file_path.name,
                    sidecar_error,
                )

        if (
            config.get("copy_sidecar_to_source", False)
            and sidecar_path
            and sidecar_path.exists()
        ):
            try:
                dest_sidecar = file_path.parent / sidecar_path.name
                shutil.copy2(sidecar_path, dest_sidecar)
                logger.info("Copied sidecar to source directory: %s", dest_sidecar.name)
            except Exception as copy_error:  # noqa: BLE001
                logger.warning(
                    "Failed to copy sidecar %s to source: %s",
                    sidecar_path.name,
                    copy_error,
                )

        # Concatenate all chunk files into a final transcript
        if chunk_files:
            # Use final_folder_name for consistency (includes timestamp prefix)
            # Use .md extension for admin files, .txt for others
            if department == "admin":
                transcript_file = file_output_folder / f"{final_folder_name}_transcript.md"
            else:
                transcript_file = file_output_folder / f"{final_folder_name}_transcript.txt"
            
            try:
                with open(transcript_file, "w", encoding="utf-8") as tf:
                    # Add markdown header for admin files
                    if department == "admin":
                        tf.write(f"# {clean_base.replace('_', ' ').title()}\n\n")
                        tf.write(f"**Processing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        tf.write(f"**Source File:** {file_path.name}\n")
                        tf.write(f"**Total Chunks:** {len(chunk_files)}\n\n")
                        tf.write("---\n\n")
                    
                    for chunk_file in chunk_files:
                        with open(chunk_file, "r", encoding="utf-8") as cf:
                            tf.write(cf.read())
                            tf.write("\n\n")
                logger.info(f"Final transcript created: {transcript_file.name}")
                artifacts_for_distribution.append(transcript_file)
            except Exception as e:
                logger.error(f"Failed to create final transcript for {file_path.name}: {e}")

        session_stats["chunks_created"] += valid_chunks
        session_stats["total_bytes_created"] += total_chunk_size
        
        # Update department breakdown
        if department not in session_stats["department_breakdown"]:
            session_stats["department_breakdown"][department] = {
                "files": 0, "chunks": 0, "errors": 0
            }
        session_stats["department_breakdown"][department]["files"] += 1
        session_stats["department_breakdown"][department]["chunks"] += valid_chunks
        
        if not chunk_files:
            error_msg = f"No valid chunks created for {file_path.name}"
            logger.warning(error_msg)
            if db:
                # Queue database operation instead of direct call
                db_queue.put((db.log_processing,
                            (str(file_path), original_size, 0, 0, time.time() - start_time, False, error_msg, department), {}))
            return False

        # Cloud copy with retry
        cloud_success = False
        if config.get("cloud_repo_root"):
            cloud_dir = Path(config["cloud_repo_root"]) / clean_base
            for attempt in range(3):
                if copy_to_cloud_enhanced(artifacts_for_distribution, cloud_dir, department_config):
                    logger.info(f"Cloud sync successful: {cloud_dir}")
                    cloud_success = True
                    break
                logger.warning(f"Cloud sync attempt {attempt+1} failed for {file_path.name}")
                time.sleep(2)

        # Move to processed
        move_success = move_to_processed_enhanced(file_path, config.get("archive_dir", "processed"), department)
        
        processing_time = time.time() - start_time
        
        # Update performance metrics
        if session_stats["files_processed"] > 0:
            current_avg = session_stats["performance_metrics"]["avg_processing_time"]
            session_stats["performance_metrics"]["avg_processing_time"] = (
                (current_avg * session_stats["files_processed"] + processing_time) / 
                (session_stats["files_processed"] + 1)
            )
        else:
            session_stats["performance_metrics"]["avg_processing_time"] = processing_time
        
        if move_success:
            session_stats["files_processed"] += 1
            logger.info(f"File processing complete: {file_path.name} -> {valid_chunks} chunks ({processing_time:.2f}s)")
            
            # Queue database operation instead of direct call
            if db:
                db_queue.put((db.log_processing,
                            (str(file_path), original_size, valid_chunks, total_chunk_size, processing_time, True, None, department, department_config), {}))

            if version_tracker:
                try:
                    if content_hash is None:
                        content_hash = version_tracker.hash_content(text)
                    metadata_payload = {
                        "department": department,
                        "artifacts": [
                            str(path)
                            for path in artifacts_for_distribution
                            if path is not None
                        ],
                        "chunk_ids": list(generated_chunk_ids),
                        "output_folder": str(file_output_folder),
                        "sidecar": str(sidecar_path) if sidecar_path else None,
                        "manifest_copy": str(manifest_copy_path),
                        "timestamp": timestamp,
                    }
                    version_tracker.mark_processed(
                        file_path,
                        content_hash,
                        chunk_ids=generated_chunk_ids,
                        metadata=metadata_payload,
                    )
                    session_stats["incremental_updates"]["processed_files"] += 1
                except Exception as tracker_error:  # noqa: BLE001
                    logger.warning(
                        "Incremental updates: failed to persist version data for %s: %s",
                        file_path.name,
                        tracker_error,
                    )
        
        return move_success
        
    except Exception as e:
        error_msg = f"Critical error processing {file_path.name}: {str(e)}"
        logger.exception(error_msg)
        
        # Queue database operation instead of direct call
        if db:
            db_queue.put((db.log_error, ("ProcessingError", str(e), traceback.format_exc(), str(file_path)), {}))
        
        notify_with_rate_limit(
            f"processing-error:{file_path}",
            notifications.send_error_alert,
            error_msg,
            str(file_path),
            traceback.format_exc(),
        )
        
        # Update department breakdown
        department = get_department_config(file_path).get("department", "default")
        if department not in session_stats["department_breakdown"]:
            session_stats["department_breakdown"][department] = {"files": 0, "chunks": 0, "errors": 0}
        session_stats["department_breakdown"][department]["errors"] += 1
        
        session_stats["errors"] += 1
        return False

def _pool_process_entry(args: Tuple[str, Dict[str, Any]]):
    path_str, cfg = args
    try:
        return process_with_retries(Path(path_str), cfg)
    except Exception:
        logger.exception("Process pool worker failed for %s", path_str)
        return False


def process_files_parallel(file_list, config):
    """Process multiple files in parallel"""
    if not file_list:
        return []
    
    global monitoring
    use_pool = config.get("enable_process_pool", False) and len(file_list) >= 32
    results: List[bool] = []

    if use_pool:
        pool_workers = min(multiprocessing.cpu_count(), len(file_list))
        logger.info("Processing %d files with process pool (%d workers)", len(file_list), pool_workers)
        try:
            with multiprocessing.Pool(processes=pool_workers) as pool:
                args = [(str(file_path), config) for file_path in file_list]
                for result in pool.imap(_pool_process_entry, args, chunksize=32):
                    results.append(bool(result))
                    session_stats["parallel_jobs_completed"] += 1
        except Exception as pool_error:
            logger.warning("Process pool fallback due to error: %s", pool_error)
            results.clear()
            use_pool = False

    if not use_pool:
        # Use configured parallel_workers instead of hardcoded 4
        configured_workers = config.get("parallel_workers", 8)
        max_workers = min(configured_workers, multiprocessing.cpu_count(), len(file_list))
        logger.info(f"Processing {len(file_list)} files with {max_workers} workers (configured: {configured_workers})")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(process_with_retries, file_path, config): file_path
                for file_path in file_list
            }
            
            for future in future_to_file:
                try:
                    file_path = future_to_file[future]
                    result = future.result(timeout=300)  # 5 minute timeout per file
                    results.append(result)
                    session_stats["parallel_jobs_completed"] += 1
                    if monitoring and monitoring.enabled:
                        monitoring.record_processing_event(
                            bool(result),
                            {"file": file_path.name, "mode": "parallel"},
                        )
                        if not result:
                            monitoring.record_error(
                                "ProcessingFailure",
                                f"Parallel processing failed for {file_path.name}",
                            )
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.error(f"Parallel processing failed for {file_path}: {e}")
                    if db:
                        db_queue.put((db.log_error, ("ParallelProcessingError", str(e), traceback.format_exc(), str(file_path)), {}))
                    results.append(False)
                    if monitoring and monitoring.enabled:
                        monitoring.record_processing_event(
                            False, {"file": file_path.name, "mode": "parallel"}
                        )
                        monitoring.record_error(
                            "ProcessingException",
                            f"Parallel worker raised exception for {file_path.name}: {e}",
                            severity="critical",
                        )
    elif monitoring and monitoring.enabled:
        for file_path, result in zip(file_list, results):
            monitoring.record_processing_event(
                bool(result), {"file": file_path.name, "mode": "process-pool"}
            )
            if not result:
                monitoring.record_error(
                    "ProcessingFailure",
                    f"Process pool failed for {file_path.name}",
                )
    
    successful = sum(1 for r in results if r)
    logger.info(f"Parallel processing complete: {successful}/{len(file_list)} files successful")
    return results


def _process_batch_multiproc(file_list: List[Path], config: dict) -> List[bool]:
    """
    Process files using multiprocessing pool with fallback to sequential.
    
    Args:
        file_list: List of file paths to process
        config: Configuration dictionary
        
    Returns:
        List of boolean results (True for success, False for failure)
    """
    if not file_list:
        return []
    
    pool_workers = config.get("parallel_workers", 8)
    logger.info("Processing %d files with multiprocessing pool (%d workers)", len(file_list), pool_workers)
    
    try:
        pool_inst = multiprocessing.Pool(processes=pool_workers)
        try:
            args = [(str(file_path), config) for file_path in file_list]
            results = pool_inst.map(_pool_process_entry, args)
            return [bool(r) for r in results]
        finally:
            pool_inst.close()
            pool_inst.join()
    except Exception as e:
        logger.error(f"Multiprocessing failed: {e}")
        if config.get("multiprocessing_fallback", True):
            logger.warning("Falling back to sequential processing")
            results = []
            for file_path in file_list:
                try:
                    result = process_with_retries(file_path, config)
                    results.append(bool(result))
                except Exception as proc_error:
                    logger.error(f"Sequential processing failed for {file_path}: {proc_error}")
                    results.append(False)
            return results
        else:
            raise


def wait_for_file_stability(file_path, min_wait=2, max_wait=30):
    """Enhanced file stability check"""
    file_size = 0
    stable_count = 0
    wait_time = 0
    
    try:
        initial_size = os.path.getsize(file_path)
        if initial_size < 1000:
            target_stable = 2
            check_interval = 0.5
        else:
            target_stable = 3
            check_interval = 1
    except:
        target_stable = 2
        check_interval = 1
    
    while wait_time < max_wait:
        try:
            current_size = os.path.getsize(file_path)
            if current_size == file_size:
                stable_count += 1
                if stable_count >= target_stable:
                    logger.info(f"File stable after {wait_time:.1f}s: {file_path.name}")
                    return True
            else:
                file_size = current_size
                stable_count = 0
            
            time.sleep(check_interval)
            wait_time += check_interval
            
        except FileNotFoundError:
            logger.warning(f"File disappeared during stability check: {file_path}")
            return False
    
    logger.warning(f"File stability timeout after {max_wait}s: {file_path.name}")
    return True

def copy_to_cloud_enhanced(chunk_files, cloud_dir, department_config):
    """Enhanced cloud copy with department-specific handling"""
    try:
        os.makedirs(cloud_dir, exist_ok=True)
        successful_copies = 0
        
        # Create department-specific metadata
        metadata = {
            "department": department_config.get("department", "default"),
            "processing_time": datetime.now().isoformat(),
            "chunk_count": len(chunk_files),
            "audit_level": department_config.get("audit_level", "basic")
        }
        
        # Write metadata file
        metadata_file = cloud_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        for file_path in chunk_files:
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                shutil.copy(file_path, cloud_dir)
                successful_copies += 1
            else:
                logger.warning(f"Skipped zero-byte file: {file_path}")
        
        logger.info(f"Cloud sync: {successful_copies}/{len(chunk_files)} files copied")
        return successful_copies > 0
        
    except Exception as e:
        logger.exception(f"Cloud copy failed: {e}")
        if db:
            db_queue.put((db.log_error, ("CloudSyncError", str(e), traceback.format_exc()), {}))
        return False

def move_to_processed_enhanced(file_path, processed_folder, department):
    """Enhanced file moving with department organization and manifest support"""
    try:
        # Use new archive function if enabled in config
        if CONFIG.get('move_to_archive', False):
            try:
                from celery_tasks import archive_processed_file
                archive_path = archive_processed_file(file_path, CONFIG)
                if archive_path:
                    logger.info(f"Archived file using enhanced function: {archive_path}")
                    return True
                else:
                    logger.error(f"Enhanced archive failed for: {file_path.name}")
                    return False
            except ImportError:
                logger.warning("Enhanced archive function not available, using fallback")
            except Exception as e:
                logger.error(f"Enhanced archive error: {e}")
        
        # Fallback to original move logic
        # Create department-specific processed folder
        dept_processed = Path(processed_folder) / department
        os.makedirs(dept_processed, exist_ok=True)
        
        dest_path = dept_processed / file_path.name
        
        # Handle duplicate names with timestamp
        counter = 1
        while dest_path.exists():
            timestamp = datetime.now().strftime("%H%M%S")
            stem = file_path.stem
            suffix = file_path.suffix
            dest_path = dept_processed / f"{stem}_{timestamp}_{counter}{suffix}"
            counter += 1

        # Use safe_file_move with retry logic and file-gone detection
        return safe_file_move(Path(file_path), dest_path)
        
    except Exception as e:
        logger.error(f"Failed to move {file_path.name}: {e}")
        if db:
            db_queue.put((db.log_error, ("FileMoveError", str(e), traceback.format_exc(), str(file_path)), {}))
        return False

def quarantine_failed_file(file_path: Path) -> None:
    try:
        failed_dir.mkdir(parents=True, exist_ok=True)
        destination = failed_dir / file_path.name
        counter = 1
        while destination.exists():
            destination = failed_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1
        shutil.move(str(file_path), str(destination))

        ready_path = Path(f"{file_path}.ready")
        if ready_path.exists():
            try:
                ready_destination = failed_dir / ready_path.name
                shutil.move(str(ready_path), str(ready_destination))
            except Exception as ready_error:
                logger.warning(f"Failed to quarantine ready signal for {file_path.name}: {ready_error}")

        logger.error(f"Moved {file_path.name} to failed quarantine: {destination}")
    except FileNotFoundError:
        logger.warning(f"File missing during quarantine attempt: {file_path}")
    except Exception as quarantine_error:
        logger.error(f"Failed to quarantine {file_path.name}: {quarantine_error}")

def process_with_retries(file_path: Path, config, max_attempts: int = 3) -> bool:
    for attempt in range(max_attempts):
        try:
            success = process_file_enhanced(file_path, config)
            if success:
                return True
            logger.warning(
                "Processing attempt %s/%s failed for %s",
                attempt + 1,
                max_attempts,
                file_path.name,
            )
        except Exception as exc:
            logger.exception(
                "Processing attempt %s/%s raised an exception for %s: %s",
                attempt + 1,
                max_attempts,
                file_path.name,
                exc,
            )

        if attempt < max_attempts - 1:
            backoff = 2 ** attempt
            time.sleep(backoff)

    logger.error(f"Processing failed after {max_attempts} attempts for {file_path.name}")
    session_stats["errors"] = session_stats.get("errors", 0) + 1
    if Path(file_path).exists():
        quarantine_failed_file(Path(file_path))
    else:
        logger.warning(f"File already moved or missing after failures: {file_path}")
    return False


def process_one_file(path: Path) -> bool:
    """Wrapper to process a single file via the standard pipeline."""
    try:
        if not path.exists():
            logger.debug("Skipping missing file during event processing: %s", path)
            return False

        logger.info("Event watcher processing file: %s", path.name)
        result = process_with_retries(path, CONFIG)
        if result:
            logger.info("Event watcher completed: %s", path.name)
        else:
            logger.error("Event watcher failed: %s", path.name)
        return result
    except Exception as exc:
        logger.exception("Unhandled error in process_one_file for %s: %s", path, exc)
        return False

def log_session_stats():
    """Log comprehensive session statistics"""
    logger.info("=== ENHANCED SESSION STATISTICS ===")
    for key, value in session_stats.items():
        if key == "department_breakdown":
            logger.info("Department Breakdown:")
            for dept, stats in value.items():
                logger.info(f"  {dept}: {stats}")
        elif key == "performance_metrics":
            logger.info("Performance Metrics:")
            for metric, val in value.items():
                logger.info(f"  {metric}: {val}")
        elif key == "tag_counts":
            logger.info("Tag Counts:")
            sorted_tags = sorted(value.items(), key=lambda item: item[1], reverse=True)
            for tag, count in sorted_tags:
                logger.info("  %s: %s", tag, count)
        elif key == "file_deduplication":
            logger.info("File-Level Deduplication:")
            for metric, val in value.items():
                logger.info(f"  {metric}: {val}")
        else:
            logger.info(f"{key}: {value}")

def main():
    """Enhanced main loop with enterprise features"""
    watch_folder = CONFIG.get("watch_folder", "C:/Users/carucci_r/Documents/chunker")
    os.makedirs(CONFIG.get("output_dir", "output"), exist_ok=True)
    os.makedirs(CONFIG.get("archive_dir", "processed"), exist_ok=True)

    logger.info("=== ENTERPRISE CHUNKER STARTED ===")
    logger.info(f"Monitoring: {watch_folder}")
    supported_extensions = CONFIG.get("supported_extensions", [".txt", ".md"])
    suffixes = CONFIG.get("supported_extensions", [])
    stability_timeout = CONFIG.get("file_stability_timeout", 2)
    use_events = CONFIG.get("use_event_watcher", True)
    filter_mode = CONFIG.get("file_filter_mode", "all")
    logger.info(f"File types: {', '.join(supported_extensions)} files")
    logger.info(f"Filter mode: {filter_mode}")
    if filter_mode == "patterns":
        patterns = CONFIG.get("file_patterns", ["_full_conversation"])
        logger.info(f"Required patterns: {', '.join(patterns)}")
    elif filter_mode == "suffix":
        logger.info("Required suffix: _full_conversation")
    configured_workers = CONFIG.get("parallel_workers", 8)
    logger.info(f"Parallel processing: {min(configured_workers, multiprocessing.cpu_count())} workers (configured: {configured_workers})")
    logger.info(f"Database tracking: Enabled")
    logger.info(f"Notifications: {'Enabled' if notifications.config.get('enable_notifications') else 'Disabled'}")
    logger.info(f"Event-driven watcher: {'enabled' if use_events else 'disabled'}")
    
    processed_files = set()
    loop_count = 0
    last_cleanup = datetime.now()
    last_report = datetime.now()
    last_archive = datetime.now()
    
    # Send startup notification
    notifications.send_email(
        notifications.config["admin_emails"],
        "🚀 Chunker System Started",
        f"Enterprise Chunker system started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Monitoring: {watch_folder}\n"
        f"File types: {', '.join(supported_extensions)} files\n"
        f"Filter mode: {filter_mode}\n"
        f"Parallel workers: {min(configured_workers, multiprocessing.cpu_count())} (configured: {configured_workers})\n"
        f"Database: Enabled\n"
        f"Dashboard: http://localhost:5000"
    )
    
    backup_manager = None
    try:
        backup_config = CONFIG.get("backup", {})
        if backup_config.get("enabled"):
            backup_manager = BackupManager(backup_config, CONFIG, logger=logger)
            schedule_settings = backup_config.get("schedule", {}) or {}
            run_immediately = bool(schedule_settings.get("run_at_start", False))
            backup_manager.schedule_backups(run_immediately=run_immediately)
            logger.info("Automated backups enabled.")
    except Exception as backup_error:
        logger.exception("Failed to initialize backup manager: %s", backup_error)
        backup_manager = None

    if monitoring and monitoring.enabled:
        monitoring.start_monitoring()

    try:
        if use_events:
            logger.info("Starting event-driven watcher for %s", watch_folder)
            run_event_watcher(watch_folder, suffixes, worker_fn=process_one_file)
            return

        while True:
            try:
                # Look for files with supported extensions
                all_files = []
                supported_extensions = CONFIG.get("supported_extensions", [".txt", ".md"])
                for ext in supported_extensions:
                    all_files.extend(list(Path(watch_folder).glob(f"*{ext}")))
                
                if len(all_files) > 0:
                    logger.info(f"Found {len(all_files)} files with supported extensions in watch folder")
                
                # Filter files based on configuration
                excluded_files = {"watcher_splitter.py", "test_chunker.py", "chunker_db.py", "notification_system.py"}
                
                # Apply file filtering based on mode
                filter_mode = CONFIG.get("file_filter_mode", "all")
                file_patterns = CONFIG.get("file_patterns", ["_full_conversation"])
                exclude_patterns = CONFIG.get("exclude_patterns", [])
                
                filtered_files = []
                for f in all_files:
                    if f.name in processed_files:
                        logger.info(f"Skipping already processed file: {f.name}")
                        continue
                    if not f.is_file():
                        logger.info(f"Skipping non-file: {f.name}")
                        continue
                    if f.name in excluded_files:
                        logger.info(f"Skipping excluded file: {f.name}")
                        continue

                    # CRITICAL: Skip manifest files and archives to prevent recursion
                    if not should_process_file(f):
                        logger.info(f"Skipping file that should not be processed: {f.name}")
                        continue

                    # Check exclude patterns first
                    if any(pattern in f.name for pattern in exclude_patterns):
                        logger.info(f"Skipping file with exclude pattern: {f.name}")
                        continue

                    # Apply filter mode
                    if filter_mode == "all":
                        filtered_files.append(f)
                    elif filter_mode == "patterns":
                        if any(pattern in f.name for pattern in file_patterns):
                            filtered_files.append(f)
                        else:
                            logger.info(f"Skipping file without required pattern: {f.name}")
                    elif filter_mode == "suffix":
                        # Only process files with _full_conversation suffix
                        if "_full_conversation" in f.name:
                            filtered_files.append(f)
                        else:
                            logger.info(f"Skipping file without _full_conversation suffix: {f.name}")
                
                if len(filtered_files) > 0:
                    logger.info(f"After filtering: {len(filtered_files)} files remain")

                eligible_files = []
                for f in filtered_files:
                    if f.suffix.lower() == ".part":
                        logger.info(f"Skipping partial file awaiting final rename: {f.name}")
                        continue

                    if use_ready_signal:
                        ready_marker = Path(f"{f}.ready")
                        if not ready_marker.exists():
                            logger.info(f"Waiting for ready signal for {f.name}")
                            continue

                    if not is_effectively_stable(f, CONFIG):
                        logger.info("Waiting for file to settle: %s", f.name)
                        continue

                    eligible_files.append(f)
                
                if len(eligible_files) < len(filtered_files):
                    skipped = len(filtered_files) - len(eligible_files)
                    logger.info(f"Skipped {skipped} files (waiting for stability/ready signal)")

                # Apply batch size limit to avoid processing too many files per cycle
                batch_size = CONFIG.get("batch_size", 100)
                new_files = eligible_files[:batch_size]
                
                if len(eligible_files) > batch_size:
                    logger.info(f"Batch limit: processing {batch_size} of {len(eligible_files)} eligible files this cycle")
                
                if new_files:
                    logger.info(f"Found {len(new_files)} new files to process")
                    
                    # Process files in parallel if multiple files
                    if len(new_files) > 1 and CONFIG.get("enable_parallel_processing", True):
                        # Use configured processing method (threads or multiprocessing)
                        if CONFIG.get("use_multiprocessing", False):
                            results = _process_batch_multiproc(new_files, CONFIG)
                        else:
                            results = process_files_parallel(new_files, CONFIG)
                        
                        for i, result in enumerate(results):
                            if result:
                                processed_files.add(new_files[i].name)
                                if len(processed_files) > 1000:
                                    processed_files.clear()
                    else:
                        # Process files sequentially
                        for file_path in new_files:
                            try:
                                success = process_with_retries(file_path, CONFIG)
                            except Exception as e:
                                logger.exception(f"Error processing {file_path.name}: {e}")
                                if monitoring and monitoring.enabled:
                                    monitoring.record_processing_event(
                                        False,
                                        {"file": file_path.name, "mode": "sequential"},
                                    )
                                    monitoring.record_error(
                                        "ProcessingException",
                                        f"Exception while processing {file_path.name}: {e}",
                                        severity="critical",
                                    )
                                if db:
                                    db_queue.put((db.log_error,
                                                 ("ProcessingError", str(e), traceback.format_exc(), str(file_path)), {}))
                                continue

                            if monitoring and monitoring.enabled:
                                monitoring.record_processing_event(
                                    bool(success),
                                    {"file": file_path.name, "mode": "sequential"},
                                )
                                if not success:
                                    monitoring.record_error(
                                        "ProcessingFailure",
                                        f"Failed to process {file_path.name}",
                                    )

                            if success:
                                processed_files.add(file_path.name)
                                if len(processed_files) > 1000:
                                    processed_files.clear()
                                logger.info(f"Successfully processed: {file_path.name}")
                            else:
                                logger.error(f"Failed to process: {file_path.name}")

                # Periodic maintenance
                loop_count += 1
                
                # Log session stats every minute
                if loop_count % 12 == 0:  # Every minute at 5s intervals
                    log_session_stats()
                
                # Log system metrics every 5 minutes
                if loop_count % 60 == 0:
                    log_system_metrics()
                
                # Daily cleanup and reporting
                if datetime.now() - last_cleanup > timedelta(hours=24):
                    if db:
                        try:
                            db.cleanup_old_data(days=30)
                        except Exception as db_error:
                            logger.warning(f"Failed to run database cleanup: {db_error}")
                    last_cleanup = datetime.now()
                
                # Weekly auto-archival of old output sessions (>30 days old)
                if CONFIG.get("archive_old_outputs", True) and datetime.now() - last_archive > timedelta(days=7):
                    try:
                        archive_after_days = CONFIG.get("archive_after_days", 90)
                        archive_age = datetime.now() - timedelta(days=archive_after_days)
                        archive_target = Path(CONFIG.get("archive_dir", "03_archive")) / "consolidated" / datetime.now().strftime("%Y/%m")
                        archive_target.mkdir(parents=True, exist_ok=True)
                        
                        output_dir = Path(CONFIG.get("output_dir", "04_output"))
                        archived_count = 0
                        
                        if output_dir.exists():
                            for sess in output_dir.iterdir():
                                if sess.is_dir():
                                    try:
                                        # Check session age based on directory modification time
                                        sess_mtime = datetime.fromtimestamp(sess.stat().st_mtime)
                                        if sess_mtime < archive_age:
                                            # Move session to consolidated archive
                                            archive_dest = archive_target / sess.name
                                            if archive_dest.exists():
                                                # Handle duplicates with timestamp suffix
                                                timestamp = datetime.now().strftime("%H%M%S")
                                                archive_dest = archive_target / f"{sess.name}_{timestamp}"
                                            
                                            shutil.move(str(sess), str(archive_dest))
                                            archived_count += 1
                                            logger.info(f"Archived old session: {sess.name} → {archive_dest.relative_to(archive_target.parent.parent)}")
                                    except Exception as sess_error:
                                        logger.warning(f"Failed to archive session {sess.name}: {sess_error}")
                        
                        if archived_count > 0:
                            logger.info(f"Auto-archival complete: {archived_count} sessions moved to consolidated archive")
                        last_archive = datetime.now()
                    except Exception as archive_error:
                        logger.warning(f"Failed to run auto-archival: {archive_error}")
                
                # Send daily report
                if datetime.now() - last_report > timedelta(hours=24):
                    if db:
                        try:
                            analytics = db.get_analytics(days=1)
                            notifications.send_daily_summary(session_stats, analytics)
                        except Exception as db_error:
                            logger.warning(f"Failed to get analytics or send daily summary: {db_error}")
                    last_report = datetime.now()
                
                time.sleep(CONFIG.get("polling_interval", 5))
                
            except KeyboardInterrupt:
                logger.info("Watcher stopped by user")
                break
            except Exception as e:
                logger.exception("Critical error in main loop")
                if db:
                    db_queue.put((db.log_error, ("MainLoopError", str(e), traceback.format_exc()), {}))
                notify_with_rate_limit(
                    "main-loop-error",
                    notifications.send_error_alert,
                    f"Critical main loop error: {str(e)}",
                    stack_trace=traceback.format_exc(),
                )
                time.sleep(10)
                
    finally:
        # Final statistics and cleanup
        log_session_stats()
        if backup_manager:
            backup_manager.stop_scheduled_backups()
        if monitoring and monitoring.enabled:
            monitoring.stop_monitoring()
        try:
            metrics_executor.shutdown(wait=False)
        except Exception as exec_shutdown_error:
            logger.debug("Metrics executor shutdown warning: %s", exec_shutdown_error)
        
        # Shutdown database queue worker
        if db:
            try:
                db_queue.put((None, (), {}))  # Shutdown signal
                db_worker_thread.join(timeout=5)  # Wait up to 5 seconds for queue to empty
                logger.info("Database queue worker stopped")
            except Exception as db_shutdown_error:
                logger.debug("Database worker shutdown warning: %s", db_shutdown_error)
        
        # Send shutdown notification
        notifications.send_email(
            notifications.config["admin_emails"],
            "🛑 Chunker System Stopped",
            f"Enterprise Chunker system stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Session Summary:\n"
            f"Files Processed: {session_stats['files_processed']}\n"
            f"Chunks Created: {session_stats['chunks_created']}\n"
            f"Zero-byte Prevented: {session_stats['zero_byte_prevented']}\n"
            f"Errors: {session_stats['errors']}\n"
            f"Uptime: {datetime.now() - datetime.strptime(session_stats['session_start'], '%Y-%m-%d %H:%M:%S')}"
        )

if __name__ == "__main__":
    main()