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
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import sent_tokenize
import json
import psutil
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from chunker_db import ChunkerDatabase
from notification_system import NotificationSystem
import re
import openpyxl
import PyPDF2
import ast
import docx
import yaml
# Graceful RAG imports with error handling
try:
    from rag_integration import ChromaRAG, extract_keywords
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG components not available: {e}")
    print("Continuing with core chunking functionality...")
    RAG_AVAILABLE = False
    ChromaRAG = None
    extract_keywords = None

# Graceful Celery imports with error handling
try:
    from celery_tasks import process_file_with_celery_chain, app as celery_app
    CELERY_AVAILABLE = True
    print("Celery integration available")
except ImportError as e:
    print(f"Celery components not available: {e}")
    print("Continuing with direct processing...")
    CELERY_AVAILABLE = False
    process_file_with_celery_chain = None
    celery_app = None
from file_processors import get_file_processor, check_processor_dependencies, redact_sensitive_data, extract_python_blocks

# Graceful RAG imports with error handling
try:
    from langchain_rag_handler import LangChainRAGHandler, graceful_rag_handler, check_rag_dependencies
    RAG_DEPENDENCIES_AVAILABLE = True
except ImportError:
    # Logger not yet defined, use print for now
    print("LangChain RAG handler not available - using basic RAG only")
    RAG_DEPENDENCIES_AVAILABLE = False

def validate_config(config):
    """Validate configuration parameters"""
    errors = []
    
    # Check required fields
    required_fields = ["watch_folder", "output_dir", "archive_dir"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Check data types
    if "rag_enabled" in config and not isinstance(config["rag_enabled"], bool):
        errors.append("rag_enabled must be boolean")
    
    if "chunk_size" in config and not isinstance(config["chunk_size"], int):
        errors.append("chunk_size must be integer")
    
    if "chroma_persist_dir" in config and not isinstance(config["chroma_persist_dir"], str):
        errors.append("chroma_persist_dir must be string")
    
    # Check LangSmith config
    if "langsmith" in config:
        langsmith_config = config["langsmith"]
        if not isinstance(langsmith_config, dict):
            errors.append("langsmith config must be dictionary")
        else:
            if "project" in langsmith_config and not isinstance(langsmith_config["project"], str):
                errors.append("langsmith.project must be string")
    
    if errors:
        logger.error("Configuration validation errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    logger.info("Configuration validation passed")
    return True

def safe_chroma_add(chunk, metadata, config):
    """Safely add chunk to ChromaDB with error handling"""
    try:
        if not config.get("rag_enabled", False):
            return None
        
        if not RAG_AVAILABLE:
            logger.warning("RAG is enabled in config but ChromaDB is not available. Skipping RAG integration.")
            return None
        
        chroma_rag = ChromaRAG(persist_directory=config.get("chroma_persist_dir", "./chroma_db"))
        chunk_id = chroma_rag.add_chunk(chunk, metadata)
        logger.debug(f"Added chunk to ChromaDB: {chunk_id}")
        return chunk_id
        
    except ImportError as e:
        logger.warning(f"ChromaDB not available: {e}")
        logger.info("Continuing without RAG functionality")
        return None
    except Exception as e:
        logger.error(f"Failed to add chunk to ChromaDB: {e}")
        return None

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
    "session_start_time": time.time(),
    "files_processed": 0,
    "chunks_created": 0,
    "zero_byte_prevented": 0,
    "errors": 0,
    "total_sentences_processed": 0,
    "total_bytes_created": 0,
    "parallel_jobs_completed": 0,
    "department_breakdown": {},
    "performance_metrics": {
        "avg_processing_time": 0,
        "peak_memory_usage": 0,
        "peak_cpu_usage": 0,
        "files_per_minute": 0
    }
}

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
    logger.info(f"Starting chunking process - Text length: {len(text)} chars, Chunk limit: {limit} sentences")
    
    if not text or len(text.strip()) < 10:
        logger.warning("Text too short for chunking - skipping")
        return []
    
    try:
        sentences = sent_tokenize(text)
        logger.info(f"Tokenized text into {len(sentences)} sentences")
        
        if not sentences:
            logger.warning("No sentences found in text - skipping")
            return []
        
        # Apply department-specific chunking rules
        original_sentence_count = len(sentences)
        if department_config.get("enable_redaction"):
            sentences = apply_redaction_rules(sentences)
            logger.info(f"Applied redaction rules - {original_sentence_count} -> {len(sentences)} sentences")
        
        chunks = []
        max_chars = department_config.get("max_chunk_chars", CONFIG.get("max_chunk_chars", 30000))
        logger.info(f"Chunking parameters - Max chars per chunk: {max_chars}, Target sentences per chunk: {limit}")
        
        current_chunk = []
        current_length = 0
        chunk_count = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed limits
            if (len(current_chunk) >= limit or 
                current_length + sentence_length > max_chars) and current_chunk:
                
                chunk_text = " ".join(current_chunk)
                if len(chunk_text.strip()) > 0:
                    chunks.append(chunk_text)
                    chunk_count += 1
                    logger.debug(f"Created chunk {chunk_count}: {len(current_chunk)} sentences, {len(chunk_text)} chars")
                
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
                chunk_count += 1
                logger.debug(f"Created final chunk {chunk_count}: {len(current_chunk)} sentences, {len(chunk_text)} chars")
        
        session_stats["total_sentences_processed"] += len(sentences)
        logger.info(f"Chunking complete - Created {len(chunks)} chunks from {len(sentences)} sentences (avg: {len(sentences)/len(chunks):.1f} sentences/chunk)")
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

def process_file_with_celery(file_path: Path, config: dict) -> bool:
    """
    Process file using Celery task queue with fallback to direct processing.
    
    Args:
        file_path: Path to the file to process
        config: Configuration dictionary
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        if CELERY_AVAILABLE and config.get("celery_enabled", True):
            # Use Celery task chain for advanced processing
            logger.info(f"Queuing file for Celery processing: {file_path}")
            
            task_id = process_file_with_celery_chain(
                str(file_path),
                None,  # dest_path
                "watcher",  # event_type
                config
            )
            
            logger.info(f"File queued for Celery processing: {file_path} (task_id: {task_id})")
            
            # For immediate feedback, we'll return True and let Celery handle the rest
            # The actual processing will be handled by Celery workers
            return True
            
        else:
            # Fallback to direct processing
            logger.info(f"Using direct processing (Celery not available): {file_path}")
            return process_file_enhanced(file_path, config)
            
    except Exception as e:
        logger.error(f"Error in Celery processing: {e}")
        # Fallback to direct processing
        logger.info(f"Falling back to direct processing: {file_path}")
        return process_file_enhanced(file_path, config)

def process_file_enhanced(file_path, config):
    """Enhanced file processing with comprehensive tracking"""
    start_time = time.time()
    department_config = get_department_config(file_path)
    department = department_config.get("department", "default")
    
    # Safe filename logging to avoid encoding issues
    safe_filename = file_path.name.encode('ascii', 'replace').decode('ascii')
    logger.info(f"Processing file: {safe_filename} (Department: {department})")
    
    try:
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

        # Read file with multiple attempts using appropriate processor
        text = None
        original_size = 0
        file_type = file_path.suffix.lower()
        
        for attempt in range(3):
            try:
                # Read file content first
                if file_type in [".txt", ".md", ".json", ".csv", ".sql", ".yaml", ".xml", ".log", ".py"]:
                    with open(file_path, "r", encoding="utf-8", errors='replace') as f:
                        text = f.read()
                elif file_type in [".xlsx", ".xlsm", ".pdf", ".docx"]:
                    # Binary files - use processors directly
                    processor = get_file_processor(file_type)
                    text = processor(file_path)
                else:
                    # Default to text reading
                    with open(file_path, "r", encoding="utf-8", errors='replace') as f:
                        text = f.read()
                
                # Process text content if needed
                if text and file_type in [".py", ".yaml", ".xml", ".log", ".sql"]:
                    processor = get_file_processor(file_type)
                    text = processor(text)
                
                original_size = len(text.encode('utf-8'))
                break
            except Exception as e:
                logger.warning(f"Read attempt {attempt+1} failed for {file_path.name}: {e}")
                if attempt < 2:
                    time.sleep(1)
        
        if not text:
            error_msg = f"Could not read {file_path.name} after 3 attempts"
            logger.error(error_msg)
            if db:
                try:
                    db.log_error("FileReadError", error_msg, filename=str(file_path))
                except Exception as db_error:
                    logger.warning(f"Failed to log read error to database: {db_error}")
            
            # Move unreadable file to archive to prevent processing loop
            try:
                archive_dir = Path(config.get("archive_dir", "processed")) / "failed"
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_path = archive_dir / file_path.name
                shutil.move(str(file_path), str(archive_path))
                logger.info(f"Moved unreadable file to archive: {archive_path}")
            except Exception as move_error:
                logger.error(f"Failed to move unreadable file to archive: {move_error}")
            
            return False

        # Validate input text
        min_size = department_config.get("min_file_size_bytes", 100)
        if len(text.strip()) < min_size:
            error_msg = f"File too short ({len(text)} chars), skipping: {file_path.name}"
            logger.warning(error_msg)
            if db:
                try:
                    db.log_processing(str(file_path), original_size, 0, 0, 
                                    time.time() - start_time, False, error_msg, department)
                except Exception as db_error:
                    logger.warning(f"Failed to log processing to database: {db_error}")
            
            # Move too-short file to archive to prevent processing loop
            try:
                archive_dir = Path(config.get("archive_dir", "processed")) / "skipped"
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_path = archive_dir / file_path.name
                shutil.move(str(file_path), str(archive_path))
                logger.info(f"Moved too-short file to archive: {archive_path}")
            except Exception as move_error:
                logger.error(f"Failed to move too-short file to archive: {move_error}")
            
            return False

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
            
            # Move file with no valid chunks to archive to prevent processing loop
            try:
                archive_dir = Path(config.get("archive_dir", "processed")) / "no_chunks"
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_path = archive_dir / file_path.name
                shutil.move(str(file_path), str(archive_path))
                logger.info(f"Moved file with no valid chunks to archive: {archive_path}")
            except Exception as move_error:
                logger.error(f"Failed to move file with no valid chunks to archive: {move_error}")
            
            return False

        # Prepare output with organized folder structure
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        
        # Enhanced filename sanitization
        import re
        clean_base = Path(file_path.name).stem
        # Remove or replace problematic characters
        clean_base = re.sub(r'[^\w\s-]', '', clean_base)  # Remove special chars except word chars, spaces, hyphens
        clean_base = clean_base.replace(" ", "_")  # Replace spaces with underscores
        clean_base = re.sub(r'_+', '_', clean_base)  # Replace multiple underscores with single
        clean_base = clean_base.strip('_')  # Remove leading/trailing underscores
        
        # Ensure the name isn't too long (Windows path limit)
        # Account for timestamp prefix (19 chars) + separators + chunk files
        max_filename_length = 50  # Reduced to account for timestamp prefix
        if len(clean_base) > max_filename_length:
            clean_base = clean_base[:max_filename_length]
        
        output_folder = config.get("output_dir", "output")
        
        # Create folder named after the source file with timestamp prefix
        timestamp_prefix = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_output_folder = Path(output_folder) / f"{timestamp_prefix}_{clean_base}"
        os.makedirs(file_output_folder, exist_ok=True)
        
        chunk_files = []
        valid_chunks = 0
        total_chunk_size = 0

        # Write chunks with validation
        for i, chunk in enumerate(chunks):
            if validate_chunk_content_enhanced(chunk, department_config=department_config):
                chunk_file = file_output_folder / f"{timestamp}_{clean_base}_chunk{i+1}.txt"
                try:
                    with open(chunk_file, "w", encoding="utf-8") as cf:
                        cf.write(chunk)
                    # Verify file was written correctly
                    written_size = os.path.getsize(chunk_file)
                    if written_size > 0:
                        chunk_files.append(chunk_file)
                        valid_chunks += 1
                        total_chunk_size += written_size
                        logger.info(f"Created chunk: {chunk_file.name} ({len(chunk)} chars, {written_size} bytes)")
                    else:
                        logger.warning(f"Zero-byte chunk prevented: {chunk_file.name}")
                        session_stats["zero_byte_prevented"] += 1
                        os.remove(chunk_file)
                except Exception as e:
                    logger.error(f"Failed to write chunk {i+1} for {file_path.name}: {e}")
                    if db:
                        try:
                            db.log_error("ChunkWriteError", str(e), traceback.format_exc(), str(file_path))
                        except Exception as db_error:
                            logger.warning(f"Failed to log chunk write error to database: {db_error}")
            else:
                logger.warning(f"Invalid chunk {i+1} skipped for {file_path.name}")

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
            except Exception as e:
                logger.error(f"Failed to create final transcript for {file_path.name}: {e}")

        # Emit JSON sidecar and optional block summary for Python files
        try:
            if CONFIG.get("enable_json_sidecar", True):
                sidecar = {
                    "file": str(file_path),
                    "processed_at": datetime.now().isoformat(),
                    "department": department,
                    "type": file_type,
                    "output_folder": str(file_output_folder),
                    "transcript": str(transcript_file) if 'transcript_file' in locals() else None,
                    "chunks": [
                        {
                            "filename": cf.name,
                            "path": str(cf),
                            "size": (os.path.getsize(cf) if os.path.exists(cf) else None),
                            "index": i + 1,
                        } for i, cf in enumerate(chunk_files)
                    ],
                }
                # For Python files, include code blocks extracted via AST
                if file_type == ".py":
                    blocks = extract_python_blocks(text or "")
                    sidecar["code_blocks"] = blocks

                sidecar_path = file_output_folder / f"{timestamp}_{clean_base}_blocks.json"
                with open(sidecar_path, "w", encoding="utf-8") as jf:
                    json.dump(sidecar, jf, indent=2)
                logger.info(f"Sidecar JSON written: {sidecar_path.name}")

            # Append Code Blocks Summary to transcript for Python files if enabled
            if CONFIG.get("enable_block_summary", True) and file_type == ".py" and 'transcript_file' in locals():
                blocks = extract_python_blocks(text or "")
                if blocks:
                    try:
                        with open(transcript_file, "a", encoding="utf-8") as tf:
                            tf.write("\n\n## Code Blocks Summary\n")
                            for b in blocks:
                                label = "Class" if b.get("type") == "class" else "Function"
                                tf.write(f"- {label}: {b.get('name')} (lines {b.get('start_line')}–{b.get('end_line')})\n")
                                tf.write(f"  - Signature: {b.get('signature')}\n")
                                doc = b.get('docstring')
                                if doc:
                                    tf.write(f"  - Docstring: {doc.splitlines()[0][:160]}\n")
                    except Exception as e:
                        logger.warning(f"Failed to append block summary: {e}")
        except Exception as e:
            logger.warning(f"Sidecar/summary step failed: {e}")

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
            
            # Move file with no valid chunks to archive to prevent processing loop
            try:
                archive_dir = Path(config.get("archive_dir", "processed")) / "no_chunks"
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_path = archive_dir / file_path.name
                shutil.move(str(file_path), str(archive_path))
                logger.info(f"Moved file with no valid chunks to archive: {archive_path}")
            except Exception as move_error:
                logger.error(f"Failed to move file with no valid chunks to archive: {move_error}")
            
            return False

        # RAG Integration - Add chunks to ChromaDB vector database
        if config.get("rag_enabled", False):
            try:
                logger.info(f"Adding {len(chunks)} chunks to ChromaDB for {file_path.name}")
                
                chunks_added = 0
                for i, chunk in enumerate(chunks):
                    # Apply security redaction if enabled
                    if department_config.get("enable_redaction", False):
                        chunk = redact_sensitive_data(chunk)
                    
                    metadata = {
                        "file_name": file_path.name,
                        "file_type": file_path.suffix,
                        "chunk_index": i + 1,
                        "timestamp": datetime.now().isoformat(),
                        "department": department,
                        "keywords": extract_keywords(chunk) if extract_keywords else [],
                        "file_size": file_path.stat().st_size,
                        "processing_time": time.time() - start_time
                    }
                    
                    chunk_id = safe_chroma_add(chunk, metadata, config)
                    if chunk_id:
                        chunks_added += 1
                        logger.debug(f"Added chunk {i+1} to ChromaDB: {chunk_id}")
                
                if chunks_added > 0:
                    logger.info(f"Successfully added {chunks_added}/{len(chunks)} chunks to ChromaDB")
                else:
                    logger.warning("No chunks were added to ChromaDB")
                
            except Exception as e:
                logger.error(f"RAG integration failed: {e}")
                # Don't fail the entire process if RAG fails
                if db:
                    try:
                        db.log_error("RAGError", str(e), traceback.format_exc(), str(file_path))
                    except Exception as db_error:
                        logger.warning(f"Failed to log RAG error to database: {db_error}")

        # Cloud copy with retry
        cloud_success = False
        if config.get("cloud_repo_root"):
            cloud_dir = Path(config["cloud_repo_root"]) / clean_base
            for attempt in range(3):
                if copy_to_cloud_enhanced(chunk_files, cloud_dir, department_config):
                    logger.info(f"Cloud sync successful: {cloud_dir}")
                    cloud_success = True
                    break
                logger.warning(f"Cloud sync attempt {attempt+1} failed for {file_path.name}")
                time.sleep(2)

        # Copy processed files back to source folder
        source_copy_success = False
        if config.get("copy_to_source", False) and chunk_files:
            source_folder = Path(config.get("source_folder", "source"))
            try:
                # Create source folder if it doesn't exist
                source_folder.mkdir(parents=True, exist_ok=True)
                
                files_copied = 0
                
                # Copy chunks if enabled
                if config.get("copy_chunks_only", True):
                    for chunk_file in chunk_files:
                        dest_file = source_folder / chunk_file.name
                        shutil.copy2(chunk_file, dest_file)
                        files_copied += 1
                        logger.info(f"Copied chunk to source: {dest_file.name}")
                
                # Copy transcript if enabled
                if config.get("copy_transcript_only", False) and 'transcript_file' in locals():
                    dest_transcript = source_folder / transcript_file.name
                    shutil.copy2(transcript_file, dest_transcript)
                    files_copied += 1
                    logger.info(f"Copied transcript to source: {dest_transcript.name}")
                
                if files_copied > 0:
                    source_copy_success = True
                    logger.info(f"Successfully copied {files_copied} files to source folder: {source_folder}")
                else:
                    logger.warning("No files were copied to source folder")
                    
            except Exception as e:
                logger.error(f"Failed to copy files to source folder: {e}")
                if db:
                    try:
                        db.log_error("SourceCopyError", str(e), traceback.format_exc(), str(file_path))
                    except Exception as db_error:
                        logger.warning(f"Failed to log source copy error to database: {db_error}")

        # Move to processed
        move_success = move_to_processed_enhanced(file_path, config.get("archive_dir", "processed"), department)
        
        processing_time = time.time() - start_time
        
        # Update performance metrics with enhanced tracking
        if session_stats["files_processed"] > 0:
            current_avg = session_stats["performance_metrics"]["avg_processing_time"]
            session_stats["performance_metrics"]["avg_processing_time"] = (
                (current_avg * session_stats["files_processed"] + processing_time) / 
                (session_stats["files_processed"] + 1)
            )
        else:
            session_stats["performance_metrics"]["avg_processing_time"] = processing_time
        
        # Track processing speed
        if not hasattr(session_stats["performance_metrics"], "files_per_minute"):
            session_stats["performance_metrics"]["files_per_minute"] = 0
        
        # Calculate files per minute
        elapsed_time = time.time() - session_stats.get("session_start_time", time.time())
        if elapsed_time > 0:
            session_stats["performance_metrics"]["files_per_minute"] = (
                session_stats["files_processed"] * 60 / elapsed_time
            )
        
        if move_success:
            session_stats["files_processed"] += 1
            logger.info(f"File processing complete: {file_path.name} -> {valid_chunks} chunks ({processing_time:.2f}s)")
            
        # Batch database operations to reduce locking
        if db and config.get("database_batch_size", 10) > 1:
            # Store processing data for batch logging
            if not hasattr(session_stats, 'pending_db_operations'):
                session_stats['pending_db_operations'] = []
            
            session_stats['pending_db_operations'].append({
                'file_path': str(file_path),
                'original_size': original_size,
                'valid_chunks': valid_chunks,
                'total_chunk_size': total_chunk_size,
                'processing_time': processing_time,
                'success': move_success,
                'department': department
            })
            
            # Process batch when it reaches the limit
            if len(session_stats['pending_db_operations']) >= config.get("database_batch_size", 10):
                try:
                    for op in session_stats['pending_db_operations']:
                        db.log_processing(op['file_path'], op['original_size'], 
                                        op['valid_chunks'], op['total_chunk_size'],
                                        op['processing_time'], op['success'], 
                                        None, op['department'], department_config)
                    session_stats['pending_db_operations'] = []
                    logger.debug(f"Batch logged {config.get('database_batch_size', 10)} operations to database")
                except Exception as db_error:
                    logger.warning(f"Failed to batch log to database: {db_error}")
                    session_stats['pending_db_operations'] = []
        else:
            # Individual database logging (fallback)
            if db:
                try:
                    db.log_processing(str(file_path), original_size, valid_chunks, total_chunk_size,
                                    processing_time, True, None, department, department_config)
                except Exception as db_error:
                    logger.warning(f"Failed to log processing to database: {db_error}")
        
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
    """Process multiple files in parallel with optimized settings"""
    if not file_list:
        return []
    
    # Use more workers for large batches, fewer for small batches
    batch_size = config.get("batch_size", 50)
    if len(file_list) >= batch_size:
        max_workers = min(12, multiprocessing.cpu_count() * 2, len(file_list))
    else:
        max_workers = min(8, multiprocessing.cpu_count(), len(file_list))
    
    logger.info(f"Processing {len(file_list)} files with {max_workers} workers (batch size: {batch_size})")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs (use Celery if available, otherwise direct processing)
        if CELERY_AVAILABLE and config.get("celery_enabled", True):
            # Use Celery for processing
            logger.info(f"Using Celery for processing {len(file_list)} files")
            for file_path in file_list:
                try:
                    success = process_file_with_celery(file_path, config)
                    results.append(success)
                    session_stats["parallel_jobs_completed"] += 1
                except Exception as e:
                    logger.error(f"Celery processing failed for {file_path}: {e}")
                    results.append(False)
        else:
            # Use direct processing with ThreadPoolExecutor
            future_to_file = {
                executor.submit(process_file_enhanced, file_path, config): file_path 
                for file_path in file_list
            }
        
            # Collect results with timeout (only for direct processing)
            for future in future_to_file:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per file
                    results.append(result)
                    session_stats["parallel_jobs_completed"] += 1
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.error(f"Parallel processing failed for {file_path}: {e}")
                    if db:
                        try:
                            db.log_error("ParallelProcessingError", str(e), traceback.format_exc(), str(file_path))
                        except Exception as db_error:
                            logger.warning(f"Failed to log parallel processing error to database: {db_error}")
                    results.append(False)
    
    successful = sum(1 for r in results if r)
    logger.info(f"Parallel processing complete: {successful}/{len(file_list)} files successful")
    return results

def wait_for_file_stability(file_path, min_wait=1, max_wait=15):
    """Enhanced file stability check with faster processing"""
    file_size = 0
    stable_count = 0
    wait_time = 0
    
    try:
        initial_size = os.path.getsize(file_path)
        if initial_size < 1000:
            target_stable = 1  # Reduced from 2
            check_interval = 0.3  # Reduced from 0.5
        else:
            target_stable = 2  # Reduced from 3
            check_interval = 0.5  # Reduced from 1
    except:
        target_stable = 1  # Reduced from 2
        check_interval = 0.5  # Reduced from 1
    
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
    """Enhanced file moving with department organization"""
    try:
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
        
        shutil.move(str(file_path), str(dest_path))
        logger.info(f"Moved file to processed/{department}: {dest_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to move {file_path.name}: {e}")
        if db:
            try:
                db.log_error("FileMoveError", str(e), traceback.format_exc(), str(file_path))
            except Exception as db_error:
                logger.warning(f"Failed to log file move error to database: {db_error}")
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
                if metric == "files_per_minute":
                    logger.info(f"  {metric}: {val:.1f}")
                elif metric == "avg_processing_time":
                    logger.info(f"  {metric}: {val:.2f}s")
                else:
                    logger.info(f"  {metric}: {val}")
        else:
            logger.info(f"{key}: {value}")

def main():
    """Enhanced main loop with enterprise features"""
    watch_folder = CONFIG.get("watch_folder", "C:/Users/carucci_r/Documents/chunker")
    
    # Validate configuration
    if not validate_config(CONFIG):
        logger.error("Configuration validation failed. Exiting.")
        return
    
    # Check processor dependencies
    processor_deps = check_processor_dependencies()
    missing_deps = [dep for dep, available in processor_deps.items() if not available]
    if missing_deps:
        logger.warning(f"Missing file processor dependencies: {', '.join(missing_deps)}")
        logger.info("Some file types may not be processed correctly")
    
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
    logger.info(f"RAG enabled: {CONFIG.get('rag_enabled', False)}")
    
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
                
                new_files = filtered_files
                
                if new_files:
                    logger.info(f"Found {len(new_files)} new files to process")
                    
                    # Process files in parallel if multiple files
                    if len(new_files) > 1 and CONFIG.get("enable_parallel_processing", True):
                        # For large batches, process in chunks to avoid memory issues
                        batch_size = CONFIG.get("batch_size", 50)
                        if len(new_files) > batch_size:
                            logger.info(f"Processing {len(new_files)} files in batches of {batch_size}")
                            all_results = []
                            for i in range(0, len(new_files), batch_size):
                                batch = new_files[i:i + batch_size]
                                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} files")
                                batch_results = process_files_parallel(batch, CONFIG)
                                all_results.extend(batch_results)
                                # Small delay between batches to prevent system overload
                                time.sleep(0.5)
                            results = all_results
                        else:
                            results = process_files_parallel(new_files, CONFIG)
                        for i, result in enumerate(results):
                            if result:
                                processed_files.add(new_files[i].name)
                    else:
                        # Process files sequentially
                        for file_path in new_files:
                            try:
                                if process_file_enhanced(file_path, CONFIG):
                                    processed_files.add(file_path.name)
                                    logger.info(f"Successfully processed: {file_path.name}")
                                else:
                                    logger.error(f"Failed to process: {file_path.name}")
                            except Exception as e:
                                logger.exception(f"Error processing {file_path.name}: {e}")
                                if db:
                                    try:
                                        db.log_error("ProcessingError", str(e), traceback.format_exc(), str(file_path))
                                    except Exception as db_error:
                                        logger.warning(f"Failed to log processing error to database: {db_error}")
                
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