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
from datetime import datetime, timedelta
from pathlib import Path
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
from incremental_updates import VersionTracker, build_chunk_id
from chunker_db import ChunkerDatabase
from notification_system import NotificationSystem
from monitoring_system import MonitoringSystem
from backup_manager import BackupManager
from file_processors import read_file_with_fallback

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
with open(os.path.join(base_path, "config.json")) as f:
    CONFIG = json.load(f)

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

# Department-specific configurations
DEPARTMENT_CONFIGS = {
    "police": {
        "chunk_size": 75,
        "enable_redaction": True,
        "audit_level": "full",
        "priority": "high"
    },
    "admin": {
        "chunk_size": 150,
        "enable_redaction": False,
        "audit_level": "basic",
        "priority": "normal"
    },
    "legal": {
        "chunk_size": 100,
        "enable_redaction": True,
        "audit_level": "full",
        "priority": "high"
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
    file_str = str(file_path)

    # Skip manifest files (.origin.json) - catch both exact suffix and embedded patterns
    if file_path.name.endswith('.origin.json') or '.origin.json.' in file_path.name:
        logger.debug(f"Skipping manifest file: {file_path.name}")
        return False

    # Skip files in archive directory
    if '03_archive' in file_str or '\\03_archive\\' in file_str:
        logger.debug(f"Skipping archived file: {file_path.name}")
        return False

    # Skip files in output directory
    if '04_output' in file_str or '\\04_output\\' in file_str:
        logger.debug(f"Skipping output file: {file_path.name}")
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


def get_department_config(file_path):
    """Determine department configuration based on file path or content"""
    dept = CONFIG.get("default_department", "admin")
    
    # Check file path for department indicators
    path_str = str(file_path).lower()
    for department in DEPARTMENT_CONFIGS.keys():
        if department in path_str:
            dept = department
            break
    
    # Merge default config with department-specific settings
    dept_config = DEPARTMENT_CONFIGS.get(dept, {})
    merged_config = CONFIG.copy()
    merged_config.update(dept_config)
    merged_config["department"] = dept
    
    return merged_config

def log_system_metrics():
    """Log comprehensive system metrics"""
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
        
        # Log to database with retry
        if db:
            try:
                db.log_system_metrics(cpu_percent, memory.percent, 
                                     (disk.used / disk.total) * 100, active_processes)
            except Exception as e:
                logger.warning(f"Failed to log system metrics to database: {e}")
        
        logger.info(f"System metrics - CPU: {cpu_percent}%, Memory: {memory.percent}%, "
                   f"Disk: {(disk.used / disk.total) * 100:.1f}%, Processes: {active_processes}")
        
        # Send alerts if thresholds exceeded
        if cpu_percent > 90:
            notifications.send_threshold_alert("CPU Usage", f"{cpu_percent}%", "90%", "critical")
        elif cpu_percent > 80:
            notifications.send_threshold_alert("CPU Usage", f"{cpu_percent}%", "80%", "warning")
        
        if memory.percent > 90:
            notifications.send_threshold_alert("Memory Usage", f"{memory.percent}%", "90%", "critical")
        elif memory.percent > 80:
            notifications.send_threshold_alert("Memory Usage", f"{memory.percent}%", "80%", "warning")
            
    except Exception as e:
        logger.error(f"Failed to log system metrics: {e}")

def chunk_text_enhanced(text, limit, department_config):
    """Enhanced chunking with department-specific rules"""
    if not text or len(text.strip()) < 10:
        logger.warning("Text too short for chunking")
        return []
    
    try:
        sentences = sent_tokenize(text)
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
            try:
                db.log_error("ChunkingError", str(e), traceback.format_exc())
            except Exception as db_error:
                logger.warning(f"Failed to log chunking error to database: {db_error}")
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
                try:
                    db.log_error("FileStabilityError", error_msg, filename=str(file_path))
                except Exception as db_error:
                    logger.warning(f"Failed to log stability error to database: {db_error}")
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
                try:
                    db.log_error("FileReadError", error_msg, filename=str(file_path))
                except Exception as db_error:
                    logger.warning(f"Failed to log read error to database: {db_error}")
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
                try:
                    db.log_processing(str(file_path), original_size, 0, 0,
                                    time.time() - start_time, True, error_msg, department)
                except Exception as db_error:
                    logger.warning(f"Failed to log processing to database: {db_error}")
            return True  # Successfully handled (archived)

        if content_hash:
            manifest_data["last_content_hash"] = content_hash

        # Chunk the text
        sentence_limit = department_config.get("chunk_size", 100)
        chunks = chunk_text_enhanced(text, sentence_limit, department_config)
        
        if not chunks:
            error_msg = f"No valid chunks created for {file_path.name}"
            logger.error(error_msg)
            if db:
                try:
                    db.log_processing(str(file_path), original_size, 0, 0, 
                                    time.time() - start_time, False, error_msg, department)
                except Exception as db_error:
                    logger.warning(f"Failed to log processing to database: {db_error}")
            return False

        # Prepare output with organized folder structure
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        # Sanitize to prevent path length issues and remove .origin.json artifacts
        raw_base = Path(file_path.name).stem.replace(" ", "_")
        clean_base = sanitize_folder_name(raw_base, max_length=60)
        output_folder = config.get("output_dir", "output")

        # Create folder named after the source file
        file_output_folder = Path(output_folder) / clean_base

        # Safety check: ensure total path length is reasonable
        if len(str(file_output_folder)) > 200:
            logger.warning(f"Path too long ({len(str(file_output_folder))}), truncating: {file_output_folder}")
            clean_base = sanitize_folder_name(raw_base, max_length=40)
            file_output_folder = Path(output_folder) / clean_base
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
        os.makedirs(file_output_folder, exist_ok=True)
        
        chunk_files: List[Path] = []
        valid_chunks = 0
        total_chunk_size = 0
        chunk_records: List[Dict[str, Any]] = []
        artifacts_for_distribution: List[Path] = []
        sidecar_path: Optional[Path] = None
        generated_chunk_ids: List[str] = []

        # Write chunks with validation and deduplication
        for i, chunk in enumerate(chunks):
            chunk_index = i + 1

            if not validate_chunk_content_enhanced(chunk, department_config=department_config):
                logger.warning(f"Invalid chunk {chunk_index} skipped for {file_path.name}")
                continue

            if METADATA_ENABLED:
                chunk_metadata = enrich_chunk(chunk, enrichment.tags)
                chunk_tags = chunk_metadata.get("tags", [])
                tag_suffix = tag_suffix_for_filename(chunk_tags)
            else:
                chunk_metadata = {
                    "tags": [],
                    "key_terms": [],
                    "summary": "",
                    "char_length": len(chunk),
                }
                chunk_tags = []
                tag_suffix = ""

            chunk_filename_base = f"{timestamp}_{clean_base}_chunk{chunk_index}"
            if tag_suffix:
                chunk_filename = f"{chunk_filename_base}_{tag_suffix}.txt"
            else:
                chunk_filename = f"{chunk_filename_base}.txt"

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

            try:
                with open(chunk_file, "w", encoding="utf-8") as cf:
                    cf.write(chunk)
                # Verify file was written correctly
                written_size = os.path.getsize(chunk_file)
                if written_size > 0:
                    chunk_files.append(chunk_file)
                    artifacts_for_distribution.append(chunk_file)
                    valid_chunks += 1
                    total_chunk_size += written_size
                    logger.info(f"Created chunk: {chunk_file.name} ({len(chunk)} chars, {written_size} bytes)")
                    if dedup_manager and dedup_hash_value:
                        dedup_manager.add_hash(dedup_hash_value, chunk_dedup_id)
                    chunk_record = {
                        "chunk_id": chunk_id,
                        "chunk_index": chunk_index,
                        "file": chunk_file.name,
                        "tags": chunk_tags,
                        "key_terms": chunk_metadata.get("key_terms", []),
                        "summary": chunk_metadata.get("summary", ""),
                        "char_length": chunk_metadata.get("char_length", len(chunk)),
                        "byte_length": written_size,
                    }
                    chunk_records.append(chunk_record)
                    generated_chunk_ids.append(chunk_id)
                    if METADATA_ENABLED:
                        update_session_tag_counts(chunk_tags)
                else:
                    logger.warning(f"Zero-byte chunk prevented: {chunk_file.name}")
                    session_stats["zero_byte_prevented"] += 1
                    os.remove(chunk_file)
            except Exception as e:
                logger.error(f"Failed to write chunk {chunk_index} for {file_path.name}: {e}")
                if db:
                    try:
                        db.log_error("ChunkWriteError", str(e), traceback.format_exc(), str(file_path))
                    except Exception as db_error:
                        logger.warning(f"Failed to log chunk write error to database: {db_error}")

        if generated_chunk_ids:
            manifest_data["chunk_ids"] = generated_chunk_ids

        manifest_copy_path = file_output_folder / f"{timestamp}_{clean_base}.origin.json"
        try:
            dump_json(manifest_data, manifest_copy_path)
            artifacts_for_distribution.append(manifest_copy_path)
        except Exception as manifest_copy_error:  # noqa: BLE001
            logger.warning(
                "Failed to write manifest copy for %s: %s",
                file_path.name,
                manifest_copy_error,
            )

        if chunk_records and config.get("enable_json_sidecar", True):
            sidecar_filename = f"{timestamp}_{clean_base}{SIDECAR_SUFFIX}"
            sidecar_path = file_output_folder / sidecar_filename
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
            # Use .md extension for admin files, .txt for others
            if department == "admin":
                transcript_file = file_output_folder / f"{timestamp}_{clean_base}_transcript.md"
            else:
                transcript_file = file_output_folder / f"{timestamp}_{clean_base}_transcript.txt"
            
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
                try:
                    db.log_processing(str(file_path), original_size, 0, 0, 
                                    time.time() - start_time, False, error_msg, department)
                except Exception as db_error:
                    logger.warning(f"Failed to log processing to database: {db_error}")
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
            
            # Log to database with retry
            if db:
                try:
                    db.log_processing(str(file_path), original_size, valid_chunks, total_chunk_size,
                                    processing_time, True, None, department, department_config)
                except Exception as db_error:
                    logger.warning(f"Failed to log processing to database: {db_error}")

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
        
        # Log to database and send alert with retry
        if db:
            try:
                db.log_error("ProcessingError", str(e), traceback.format_exc(), str(file_path))
            except Exception as db_error:
                logger.warning(f"Failed to log processing error to database: {db_error}")
        
        try:
            notifications.send_error_alert(error_msg, str(file_path), traceback.format_exc())
        except Exception as notify_error:
            logger.warning(f"Failed to send error alert: {notify_error}")
        
        # Update department breakdown
        department = get_department_config(file_path).get("department", "default")
        if department not in session_stats["department_breakdown"]:
            session_stats["department_breakdown"][department] = {"files": 0, "chunks": 0, "errors": 0}
        session_stats["department_breakdown"][department]["errors"] += 1
        
        session_stats["errors"] += 1
        return False

def process_files_parallel(file_list, config):
    """Process multiple files in parallel"""
    if not file_list:
        return []
    
    global monitoring
    max_workers = min(4, multiprocessing.cpu_count(), len(file_list))
    logger.info(f"Processing {len(file_list)} files with {max_workers} workers")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_file = {
            executor.submit(process_with_retries, file_path, config): file_path
            for file_path in file_list
        }
        
        # Collect results with timeout
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
                    try:
                        db.log_error("ParallelProcessingError", str(e), traceback.format_exc(), str(file_path))
                    except Exception as db_error:
                        logger.warning(f"Failed to log parallel processing error to database: {db_error}")
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
    
    successful = sum(1 for r in results if r)
    logger.info(f"Parallel processing complete: {successful}/{len(file_list)} files successful")
    return results

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
            try:
                db.log_error("CloudSyncError", str(e), traceback.format_exc())
            except Exception as db_error:
                logger.warning(f"Failed to log cloud sync error to database: {db_error}")
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
            try:
                db.log_error("FileMoveError", str(e), traceback.format_exc(), str(file_path))
            except Exception as db_error:
                logger.warning(f"Failed to log file move error to database: {db_error}")
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
    filter_mode = CONFIG.get("file_filter_mode", "all")
    logger.info(f"File types: {', '.join(supported_extensions)} files")
    logger.info(f"Filter mode: {filter_mode}")
    if filter_mode == "patterns":
        patterns = CONFIG.get("file_patterns", ["_full_conversation"])
        logger.info(f"Required patterns: {', '.join(patterns)}")
    elif filter_mode == "suffix":
        logger.info("Required suffix: _full_conversation")
    logger.info(f"Parallel processing: {min(4, multiprocessing.cpu_count())} workers")
    logger.info(f"Database tracking: Enabled")
    logger.info(f"Notifications: {'Enabled' if notifications.config.get('enable_notifications') else 'Disabled'}")
    
    processed_files = set()
    loop_count = 0
    last_cleanup = datetime.now()
    last_report = datetime.now()
    
    # Send startup notification
    notifications.send_email(
        notifications.config["admin_emails"],
        "🚀 Chunker System Started",
        f"Enterprise Chunker system started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Monitoring: {watch_folder}\n"
        f"File types: {', '.join(supported_extensions)} files\n"
        f"Filter mode: {filter_mode}\n"
        f"Parallel workers: {min(4, multiprocessing.cpu_count())}\n"
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
        while True:
            try:
                # Look for files with supported extensions
                all_files = []
                supported_extensions = CONFIG.get("supported_extensions", [".txt", ".md"])
                for ext in supported_extensions:
                    all_files.extend(list(Path(watch_folder).glob(f"*{ext}")))
                
                # Filter files based on configuration
                excluded_files = {"watcher_splitter.py", "test_chunker.py", "chunker_db.py", "notification_system.py"}
                
                # Apply file filtering based on mode
                filter_mode = CONFIG.get("file_filter_mode", "all")
                file_patterns = CONFIG.get("file_patterns", ["_full_conversation"])
                exclude_patterns = CONFIG.get("exclude_patterns", [])
                
                filtered_files = []
                for f in all_files:
                    if f.name in processed_files or not f.is_file() or f.name in excluded_files:
                        continue

                    # CRITICAL: Skip manifest files and archives to prevent recursion
                    if not should_process_file(f):
                        continue

                    # Check exclude patterns first
                    if any(pattern in f.name for pattern in exclude_patterns):
                        logger.debug(f"Skipping file with exclude pattern: {f.name}")
                        continue

                    # Apply filter mode
                    if filter_mode == "all":
                        filtered_files.append(f)
                    elif filter_mode == "patterns":
                        if any(pattern in f.name for pattern in file_patterns):
                            filtered_files.append(f)
                        else:
                            logger.debug(f"Skipping file without required pattern: {f.name}")
                    elif filter_mode == "suffix":
                        # Only process files with _full_conversation suffix
                        if "_full_conversation" in f.name:
                            filtered_files.append(f)
                        else:
                            logger.debug(f"Skipping file without _full_conversation suffix: {f.name}")

                eligible_files = []
                for f in filtered_files:
                    if f.suffix.lower() == ".part":
                        logger.debug(f"Skipping partial file awaiting final rename: {f.name}")
                        continue

                    if use_ready_signal:
                        ready_marker = Path(f"{f}.ready")
                        if not ready_marker.exists():
                            logger.debug(f"Waiting for ready signal for {f.name}")
                            continue

                    eligible_files.append(f)

                new_files = eligible_files
                
                if new_files:
                    logger.info(f"Found {len(new_files)} new files to process")
                    
                    # Process files in parallel if multiple files
                    if len(new_files) > 1 and CONFIG.get("enable_parallel_processing", True):
                        results = process_files_parallel(new_files, CONFIG)
                        for i, result in enumerate(results):
                            if result:
                                processed_files.add(new_files[i].name)
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
                                    try:
                                        db.log_error(
                                            "ProcessingError",
                                            str(e),
                                            traceback.format_exc(),
                                            str(file_path),
                                        )
                                    except Exception as db_error:
                                        logger.warning(
                                            f"Failed to log processing error to database: {db_error}"
                                        )
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
                    try:
                        db.log_error("MainLoopError", str(e), traceback.format_exc())
                    except Exception as db_error:
                        logger.warning(f"Failed to log main loop error to database: {db_error}")
                try:
                    notifications.send_error_alert(f"Critical main loop error: {str(e)}", stack_trace=traceback.format_exc())
                except Exception as notify_error:
                    logger.warning(f"Failed to send error alert: {notify_error}")
                time.sleep(10)
                
    finally:
        # Final statistics and cleanup
        log_session_stats()
        if backup_manager:
            backup_manager.stop_scheduled_backups()
        if monitoring and monitoring.enabled:
            monitoring.stop_monitoring()
        
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