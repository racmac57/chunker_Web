# Chunk 3 Summary

# Verify file was written correctly
if os.path.getsize(chunk_file) > 0:
    chunk_files.append(chunk_file)
    valid_chunks += 1
    logger.info(f"Created chunk: {chunk_file.name} ({len(chunk)} chars)")
else:
    logger.warning(f"Zero-byte chunk prevented: {chunk_file.name}")
    session_stats["zero_byte_prevented"] += 1
    os.remove(chunk_file)  # Clean up
# 🕒 2025-06-27-22-45-30
# chunker/watcher_splitter.py  
# Author: R. A. Carucci
# Purpose: Enhanced chat log chunker with zero-byte prevention and robust file handling

import os
import sys
import time
import shutil
import logging
from datetime import datetime
from pathlib import Path
import nltk
from nltk.tokenize import sent_tokenize
import json

# Resolve config path (supports PyInstaller .exe)
if getattr(sys, 'frozen', False):
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

with open(os.path.join(base_path, "config.json")) as f:
    CONFIG = json.load(f)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=CONFIG.get("log_file", "logs/watcher.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Session statistics
session_stats = {
    "files_processed": 0,
    "chunks_created": 0,
    "zero_byte_prevented": 0,
    "errors": 0
}

def chunk_text(text, limit):
    """Enhanced chunking with validation"""
    if not text or len(text.strip()) < 10:
        logger.warning("Text too short for chunking")
        return []
    
    try:
        sentences = sent_tokenize(text)
        if not sentences:
            logger.warning("No sentences found in text")
            return []
        
        chunks = []
        for i in range(0, len(sentences), limit):
            chunk = " ".join(sentences[i:i + limit])
            if len(chunk.strip()) > 0:  # Prevent empty chunks
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {len(sentences)} sentences")
        return chunks
        
    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        return []

def wait_for_file_stability(file_path, min_wait=2, max_wait=30):
    """Enhanced file stability check"""
    file_size = 0
    stable_count = 0
    wait_time = 0
    
    # Determine wait strategy based on file size
    try:
        initial_size = os.path.getsize(file_path)
        if initial_size < 1000:  # Small files
            target_stable = 2
            check_interval = 0.5
        else:  # Larger files
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
                    logger.info(f"File stable after {wait_time}s: {file_path.name}")
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
    return True  # Proceed anyway

def validate_chunk_content(chunk, min_length=50):
    """Validate chunk before writing"""
    if not chunk or len(chunk.strip()) < min_length:
        return False
    
    # Check for reasonable content
    word_count = len(chunk.split())
    if word_count < 10:
        return False
    
    return True

def copy_to_cloud(chunk_files, cloud_dir):
    """Enhanced cloud copy with validation"""
    try:
        os.makedirs(cloud_dir, exist_ok=True)
        successful_copies = 0
        
        for file_path in chunk_files:
            if os.path.getsize(file_path) > 0:  # Only copy non-empty files
                shutil.copy(file_path, cloud_dir)
                successful_copies += 1
            else:
                logger.warning(f"Skipped zero-byte file: {file_path}")
        
        logger.info(f"Copied {successful_copies}/{len(chunk_files)} files to cloud")
        return successful_copies > 0
        
    except Exception as e:
        logger.exception(f"Cloud copy failed: {e}")
        return False

def move_to_processed(file_path, processed_folder):
    """Enhanced file moving with retry logic"""
    for attempt in range(3):
        try:
            os.makedirs(processed_folder, exist_ok=True)
            dest_path = Path(processed_folder) / file_path.name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                dest_path = Path(processed_folder) / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.move(str(file_path), str(dest_path))
            logger.info(f"Moved file to processed: {dest_path}")
            return True
            
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}: failed to move {file_path.name}: {e}")
            time.sleep(1)
    
    logger.error(f"All retries failed moving {file_path.name}")
    session_stats["errors"] += 1
    return False

def process_file(file_path, config):
    """Enhanced file processing with comprehensive validation"""
    logger.info(f"Processing file: {file_path.name}")
    
    # Wait for file stability
    if not wait_for_file_stability(file_path):
        logger.error(f"File not stable, skipping: {file_path.name}")
        session_stats["errors"] += 1
        return False

    # Read file with multiple attempts
    text = None
    for attempt in range(3):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            break
        except Exception as e:
            logger.warning(f"Read attempt {attempt+1} failed for {file_path.name}: {e}")
            time.sleep(1)
    
    if not text:
        logger.error(f"Could not read {file_path.name} after 3 attempts")
        session_stats["errors"] += 1
        return False

    # Validate input text
    if len(text.strip()) < 100:
        logger.warning(f"File too short ({len(text)} chars), skipping: {file_path.name}")
        session_stats["errors"] += 1
        return False

    # Chunk the text
    sentence_limit = config.get("chunk_size", 100)
    chunks = chunk_text(text, sentence_limit)
    
    if not chunks:
        logger.error(f"No valid chunks created for {file_path.name}")
        session_stats["errors"] += 1
        return False

    # Prepare output
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    clean_base = Path(file_path.name).stem.replace(" ", "_")
    output_folder = config.get("output_dir", "output")
    chunk_files = []
    valid_chunks = 0

    # Write chunks with validation
    for i, chunk in enumerate(chunks):
        if validate_chunk_content(chunk):
            chunk_file = Path(output_folder) / f"{timestamp}_{clean_base}_chunk{i+1}.txt"
            try:
                os.makedirs(output_folder, exist_ok=True)
                with open(chunk_file, "w", encoding="utf-8") as cf:
                    cf.write(chunk)
                
                # Verify file was written correctly
                if os.path.getsize(chunk_file) > 0:
                    chunk_files.append(chunk_file)
                    valid_chunks += 1
                    logger.info(f"Created chunk: {chunk_file.name} ({len(chunk)} chars)")
                else:
                    logger.warning(f"Zero-byte chunk prevented: {chunk_file.name}")
                    session_stats["zero_byte_prevented"] += 1
                    os.remove(chunk_file)  # Clean up
                    
            except Exception as e:
                logger.error(f"Failed to write chunk {i+1} for {file_path.name}: {e}")
                session_stats["errors"] += 1
        else:
            logger.warning(f"Invalid chunk {i+1} skipped for {file_path.name}")

    session_stats["chunks_created"] += valid_chunks
    
    if not chunk_files:
        logger.warning(f"No valid chunks created for {file_path.name}")
        session_stats["errors"] += 1
        return False

    # Cloud copy
    cloud_dir = Path(config["cloud_repo_root"]) / f"{timestamp}_{clean_base}"
    cloud_success = False
    
    for attempt in range(3):
        if copy_to_cloud(chunk_files, cloud_dir):
            logger.info(f"Cloud sync successful: {cloud_dir}")
            cloud_success = True
            break
        logger.warning(f"Cloud sync attempt {attempt+1} failed")
        time.sleep(2)

    # Move to processed
    move_success = move_to_processed(file_path, config.get("archive_dir", "processed"))
    
    if move_success:
        session_stats["files_processed"] += 1
        logger.info(f"File processing complete: {file_path.name} → {valid_chunks} chunks")
    
    return move_success

def log_session_stats():
    """Log session statistics"""
    logger.info("=== SESSION STATISTICS ===")
    for key, value in session_stats.items():
        logger.info(f"{key}: {value}")

def main():
    """Enhanced main loop with better error handling"""
    watch_folder = CONFIG.get("watch_folder", "C:/Users/carucci_r/Documents/chunker")
    os.makedirs(CONFIG.get("output_dir", "output"), exist_ok=True)
    os.makedirs(CONFIG.get("archive_dir", "processed"), exist_ok=True)

    logger.info(f"Enhanced watcher started - monitoring: {watch_folder}")
    logger.info(f"Target pattern: *_full_conversation.txt")
    
    processed_files = set()
    loop_count = 0
    
    while True:
        try:
            # Look for conversation files
            all_files = list(Path(watch_folder).glob("*_full_conversation.txt"))
            new_files = [f for f in all_files if f.name not in processed_files]
            
            if new_files:
                logger.info(f"Found {len(new_files)} new files to process")
                
            for file_path in new_files:
                try:
                    if process_file(file_path, CONFIG):
                        processed_files.add(file_path.name)
                        logger.info(f"Successfully processed: {file_path.name}")
                    else:
                        logger.error(f"Failed to process: {file_path.name}")
                except Exception as e:
                    logger.exception(f"Error processing {file_path.name}: {e}")
                    session_stats["errors"] += 1
            
            # Periodic status logging
            loop_count += 1
            if loop_count % 12 == 0:  # Every minute at 5s intervals
                log_session_stats()
            
            time.sleep(CONFIG.get("polling_interval", 5))
            
        except KeyboardInterrupt:
            logger.info("Watcher stopped by user")
            log_session_stats()
            break
        except Exception as e:
            logger.exception("Critical error in main loop")
            session_stats["errors"] += 1
            time.sleep(10)  # Longer wait on critical error

if __name__ == "__main__":
    main()
ChatGPT said:
No — you do not need to add that code block (if os.path.getsize(chunk_file) > 0:) again — it's already implemented correctly in your watcher_splitter.py script. ✅ Current Implementation Status
This portion of your script:

# Verify file was written correctly
if os.path.getsize(chunk_file) > 0:
    chunk_files.append(chunk_file)
    valid_chunks += 1
    logger.info(f"Created chunk: {chunk_file.name} ({len(chunk)} chars)")
else:
    logger.warning(f"Zero-byte chunk prevented: {chunk_file.name}")
    session_stats["zero_byte_prevented"] += 1
    os.remove(chunk_file)  # Clean up
Already does all of the following:

Verifies the chunk file was written and has content. Logs a warning if the chunk file is zero bytes.
