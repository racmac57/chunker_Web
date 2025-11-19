#!/usr/bin/env python3
"""
Reprocess Output Script - Extract source files from 04_output for reprocessing

This script extracts original text from processed chunks in OneDrive 04_output
and queues them for reprocessing by writing to the local 02_data watch folder.

Features:
- Extracts text from transcript.md (preferred) or reconstructs from chunks
- Creates reprocess markers to avoid duplicate processing
- Configurable via reprocess_config.json
- Comprehensive unit and integration tests
- Safe dry-run mode by default
"""

import os
import sys
import json
import logging
import argparse
import tempfile
import unittest
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import subprocess

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/reprocess_output.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG_FILE = Path("reprocess_config.json")
WATCH_FOLDER = Path(os.path.expandvars(r"C:\_chunker\02_data"))
OUTPUT_DIR = Path(os.path.expandvars(r"%OneDriveCommercial%\KB_Shared\04_output"))
ARCHIVE_DIR = Path(os.path.expandvars(r"%OneDriveCommercial%\KB_Shared\03_archive"))
MARKER_DIR = WATCH_FOLDER / ".reprocessed_sources"

# Default configuration
DEFAULT_CONFIG = {
    "watch_folder": str(WATCH_FOLDER),
    "output_dir": str(OUTPUT_DIR),
    "archive_dir": str(ARCHIVE_DIR),
    "marker_dir": str(MARKER_DIR),
    "force_onedrive_sync": False,
    "onedrive_exe": r"C:\Program Files\Microsoft OneDrive\onedrive.exe",
    "dry_run": True,
    "skip_marked": True,
    "file_extension": ".txt",
    "timestamp_prefix": True,
    "max_sessions": None,  # None = process all
    "session_pattern": "*",  # Glob pattern for session folders
    "process_archive": True,  # Also process files from 03_archive
    "process_output": True,  # Process files from 04_output
}

# Global config (loaded at runtime)
CONFIG: Dict[str, Any] = {}


def load_config() -> Dict[str, Any]:
    """Load configuration from reprocess_config.json or create default."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            # Expand environment variables
            for key in ["watch_folder", "output_dir", "archive_dir", "marker_dir", "onedrive_exe"]:
                if key in cfg and cfg[key]:
                    cfg[key] = os.path.expandvars(cfg[key])
            logger.info(f"Loaded configuration from {CONFIG_FILE}")
            return {**DEFAULT_CONFIG, **cfg}
        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            return DEFAULT_CONFIG.copy()
    else:
        # Create default config file
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        logger.info(f"Created default configuration at {CONFIG_FILE}")
        return DEFAULT_CONFIG.copy()


def force_onedrive_sync():
    """Force OneDrive to sync by restarting the client."""
    if not CONFIG.get("force_onedrive_sync", False):
        return
    
    onedrive_exe = CONFIG.get("onedrive_exe", r"C:\Program Files\Microsoft OneDrive\onedrive.exe")
    logger.info("Forcing OneDrive sync...")
    
    try:
        # Stop OneDrive
        logger.info("Stopping OneDrive...")
        os.system(f'"{onedrive_exe}" /shutdown')
        import time
        time.sleep(2)
        
        # Start OneDrive
        logger.info("Starting OneDrive...")
        os.system(f'"{onedrive_exe}"')
        time.sleep(3)
        logger.info("OneDrive sync initiated")
    except Exception as e:
        logger.warning(f"Could not force OneDrive sync: {e}")


def get_original_text(session_dir: Path) -> Optional[str]:
    """
    Extract original text from a processed session directory.
    
    Priority:
    1. transcript.md (preferred - contains full original text)
    2. Reconstruct from chunk files (.txt)
    3. Return None if neither available
    
    Args:
        session_dir: Path to session directory in 04_output
        
    Returns:
        Original text content or None if not found
    """
    # Try transcript.md first (preferred)
    transcript = session_dir / "transcript.md"
    if transcript.exists():
        try:
            content = transcript.read_text(encoding='utf-8')
            logger.debug(f"Found transcript.md in {session_dir.name}")
            return content
        except Exception as e:
            logger.warning(f"Failed to read transcript.md: {e}")
    
    # Fallback: reconstruct from chunk files (concatenate all chunks in sorted order)
    chunk_files = sorted(session_dir.glob("chunk_*.txt"), key=lambda x: int(x.stem.split('_')[-1]) if x.stem.split('_')[-1].isdigit() else 0)
    if chunk_files:
        try:
            chunks = []
            for chunk_file in chunk_files:
                try:
                    chunk_text = chunk_file.read_text(encoding='utf-8', errors='replace')
                    if chunk_text.strip():  # Only add non-empty chunks
                        chunks.append(chunk_text)
                except Exception as chunk_error:
                    logger.warning(f"Failed to read chunk {chunk_file.name}: {chunk_error}")
                    continue
            
            if chunks:
                # Join with separator to clearly mark chunk boundaries
                content = "\n\n---\n\n".join(chunks)
                logger.debug(f"Reconstructed from {len(chunks)} chunks in {session_dir.name}")
                return content
            else:
                logger.warning(f"No readable chunks found in {session_dir.name}")
                return None
        except Exception as e:
            logger.warning(f"Failed to reconstruct from chunks: {e}")
            return None
    
    logger.warning(f"No extractable text found in {session_dir.name}")
    return None


def get_source_filename(session_dir: Path) -> str:
    """
    Extract or infer source filename from session directory.
    
    Args:
        session_dir: Path to session directory
        
    Returns:
        Inferred source filename
    """
    # Try to get from sidecar JSON
    sidecar_files = list(session_dir.glob("*_sidecar.json"))
    if sidecar_files:
        try:
            with open(sidecar_files[0], 'r', encoding='utf-8') as f:
                sidecar = json.load(f)
                original_path = sidecar.get("metadata", {}).get("original_path")
                if original_path:
                    return Path(original_path).name
        except Exception as e:
            logger.debug(f"Could not read sidecar: {e}")
    
    # Infer from session directory name
    # Format: YYYYMMDD_HHMMSS_original_filename_chunk001
    name = session_dir.name
    parts = name.split("_")
    
    # Skip timestamp parts (first 2 if they look like dates)
    if len(parts) >= 3:
        # Check if first two are date/time
        if len(parts[0]) == 8 and parts[0].isdigit():  # YYYYMMDD
            if len(parts[1]) == 6 and parts[1].isdigit():  # HHMMSS
                # Reconstruct filename from remaining parts
                filename_parts = parts[2:]
                # Remove chunk suffix if present
                if filename_parts and "chunk" in filename_parts[-1].lower():
                    filename_parts = filename_parts[:-1]
                return "_".join(filename_parts) if filename_parts else name
    
    # Fallback: use directory name
    return name


def create_reprocess_marker(source_filename: str) -> Path:
    """
    Create a marker file to track reprocessed sources.
    
    Args:
        source_filename: Name of source file being reprocessed
        
    Returns:
        Path to marker file
    """
    MARKER_DIR.mkdir(parents=True, exist_ok=True)
    marker = MARKER_DIR / f"{source_filename}.reprocessed"
    marker.write_text(datetime.now().isoformat())
    return marker


def is_already_reprocessed(source_filename: str, session_dir: Optional[Path] = None) -> bool:
    """
    Check if source file has already been reprocessed.
    
    Uses multiple methods:
    1. Marker file (current method)
    2. Sidecar JSON original_source_path + hash (most reliable)
    3. Check if reprocess_* file already exists in watch folder
    
    Args:
        source_filename: Name of source file being reprocessed
        session_dir: Optional session directory for sidecar lookup
        
    Returns:
        True if already reprocessed, False otherwise
    """
    if not CONFIG.get("skip_marked", True):
        return False
    
    # Method 1: Check marker file
    marker = MARKER_DIR / f"{source_filename}.reprocessed"
    if marker.exists():
        return True
    
    # Method 2: Check sidecar JSON original_source_path + hash (most reliable)
    if session_dir:
        try:
            sidecar_files = list(session_dir.glob("*_sidecar.json"))
            if sidecar_files:
                with open(sidecar_files[0], 'r', encoding='utf-8') as f:
                    sidecar = json.load(f)
                    original_path = sidecar.get("metadata", {}).get("original_path")
                    source_hash = sidecar.get("metadata", {}).get("source_hash") or sidecar.get("metadata", {}).get("content_hash")
                    
                    if original_path:
                        orig_name = Path(original_path).name
                        # Check if reprocess file exists in watch folder
                        reprocess_pattern = f"reprocess_*_{orig_name}"
                        existing = list(WATCH_FOLDER.glob(reprocess_pattern))
                        if existing:
                            logger.info(f"Already reprocessed (found {reprocess_pattern}): {orig_name}")
                            return True
                        
                        # Also check marker for original name
                        orig_marker = MARKER_DIR / f"{orig_name}.reprocessed"
                        if orig_marker.exists():
                            logger.info(f"Already reprocessed (marker exists): {orig_name}")
                            return True
        except Exception as e:
            logger.debug(f"Could not check sidecar for reprocessing status: {e}")
    
    return False


def find_session_directories(output_dir: Path) -> List[Path]:
    """
    Find all session directories in output folder.
    
    Args:
        output_dir: Path to 04_output directory
        
    Returns:
        List of session directory paths
    """
    if not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}")
        return []
    
    pattern = CONFIG.get("session_pattern", "*")
    sessions = []
    
    for item in output_dir.iterdir():
        if item.is_dir() and item.match(pattern):
            sessions.append(item)
    
    logger.info(f"Found {len(sessions)} session directories")
    return sorted(sessions)


def find_archive_files(archive_dir: Path) -> List[Path]:
    """
    Find all source files in archive directory (organized by department).
    
    Args:
        archive_dir: Path to 03_archive directory
        
    Returns:
        List of source file paths
    """
    if not archive_dir.exists():
        logger.error(f"Archive directory does not exist: {archive_dir}")
        return []
    
    archive_files = []
    supported_extensions = CONFIG.get("supported_extensions", [".txt", ".md", ".csv", ".json", ".py"])
    
    # Archive is organized by department: 03_archive/{department}/
    for dept_dir in archive_dir.iterdir():
        if dept_dir.is_dir():
            # Recursively find all files in department directory
            for file_path in dept_dir.rglob("*"):
                if file_path.is_file():
                    # Check if file has supported extension
                    if any(file_path.suffix.lower() == ext.lower() for ext in supported_extensions):
                        # Skip sidecar and marker files
                        if ".origin.json" not in file_path.name and ".reprocessed" not in file_path.name:
                            archive_files.append(file_path)
    
    logger.info(f"Found {len(archive_files)} archive files")
    return sorted(archive_files)


def reprocess_archive_file(archive_file: Path, dry_run: bool = True) -> bool:
    """
    Reprocess a single archive file (copy to watch folder).
    
    Args:
        archive_file: Path to archive file
        dry_run: If True, don't actually copy files
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Processing archive file: {archive_file.name}")
    
    # Get source filename (remove timestamp suffix if present)
    source_filename = archive_file.name
    # Remove timestamp pattern: filename_YYYYMMDD_HHMMSS.ext
    parts = source_filename.rsplit("_", 2)
    if len(parts) == 3:
        # Check if last two parts look like timestamp
        if len(parts[1]) == 8 and parts[1].isdigit() and len(parts[2].split(".")[0]) == 6:
            # Reconstruct without timestamp
            ext = archive_file.suffix
            source_filename = parts[0] + ext
    
    # Check if already reprocessed
    if is_already_reprocessed(source_filename):
        logger.info(f"Skipping {source_filename} (already reprocessed)")
        return False
    
    # Prepare output filename
    if CONFIG.get("timestamp_prefix", True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"reprocess_{timestamp}_{source_filename}"
    else:
        output_filename = f"reprocess_{source_filename}"
    
    output_path = WATCH_FOLDER / output_filename
    
    if dry_run:
        logger.info(f"[DRY RUN] Would copy: {archive_file.name} -> {output_path.name}")
        logger.info(f"[DRY RUN] Would create marker: {source_filename}.reprocessed")
        return True
    
    # Copy file to watch folder
    try:
        WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(archive_file, output_path)
        logger.info(f"Copied: {archive_file.name} -> {output_path.name}")
        
        # Create marker
        create_reprocess_marker(source_filename)
        logger.info(f"Created marker: {source_filename}.reprocessed")
        return True
    except Exception as e:
        logger.error(f"Failed to copy {archive_file.name}: {e}")
        return False


def reprocess_session(session_dir: Path, dry_run: bool = True) -> bool:
    """
    Reprocess a single session directory.
    
    Args:
        session_dir: Path to session directory
        dry_run: If True, don't actually write files
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Processing session: {session_dir.name}")
    
    # Edge case 1: Partial/failed sessions (no transcript, no chunks)
    transcript_exists = any(session_dir.glob("transcript.md")) or any(session_dir.glob("transcript.txt"))
    chunks_exist = any(session_dir.glob("chunk_*.txt")) or any(session_dir.glob("*.txt"))
    
    if not transcript_exists and not chunks_exist:
        logger.warning(f"Empty session {session_dir.name} → skipping (no transcript or chunks)")
        # Create marker to prevent retry spam
        try:
            source_filename = get_source_filename(session_dir)
            create_reprocess_marker(source_filename)
        except Exception:
            pass
        return False
    
    # Edge case 2: Very large sessions (>100MB) → warn but proceed
    try:
        total_size = sum(f.stat().st_size for f in session_dir.rglob('*') if f.is_file())
        if total_size > 100 * 1024 * 1024:  # 100 MB
            logger.warning(f"Session very large {session_dir.name} ({total_size/1024/1024:.1f}MB) → processing anyway")
    except Exception as size_error:
        logger.debug(f"Could not check session size: {size_error}")
    
    # Edge case 3: Corrupted sidecar (try to recover)
    sidecar_valid = True
    try:
        sidecar_files = list(session_dir.glob("*_sidecar.json"))
        if sidecar_files:
            with open(sidecar_files[0], 'r', encoding='utf-8') as f:
                json.load(f)  # Validate JSON
    except json.JSONDecodeError:
        logger.warning(f"Corrupted sidecar in {session_dir.name}, will infer from directory name")
        sidecar_valid = False
    except Exception:
        pass  # No sidecar is OK
    
    # Extract original text with error handling
    try:
        original_text = get_original_text(session_dir)
    except Exception as e:
        logger.error(f"Failed reading {session_dir.name}: {e}")
        # Create marker to prevent retry spam
        try:
            source_filename = get_source_filename(session_dir)
            create_reprocess_marker(source_filename)
        except Exception:
            pass
        return False
    
    if not original_text:
        logger.warning(f"Could not extract text from {session_dir.name}")
        # Create marker to prevent retry spam
        try:
            source_filename = get_source_filename(session_dir)
            create_reprocess_marker(source_filename)
        except Exception:
            pass
        return False
    
    # Get source filename
    source_filename = get_source_filename(session_dir)
    
    # Check if already reprocessed (using enhanced detection)
    if is_already_reprocessed(source_filename, session_dir):
        logger.info(f"Skipping {source_filename} (already reprocessed)")
        return False
    
    # Prepare output filename
    if CONFIG.get("timestamp_prefix", True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"reprocess_{timestamp}_{source_filename}"
    else:
        output_filename = f"reprocess_{source_filename}"
    
    # Add extension if not present
    if not output_filename.endswith(CONFIG.get("file_extension", ".txt")):
        output_filename += CONFIG.get("file_extension", ".txt")
    
    output_path = WATCH_FOLDER / output_filename
    
    if dry_run:
        logger.info(f"[DRY RUN] Would create: {output_path.name} ({len(original_text)} chars)")
        logger.info(f"[DRY RUN] Would create marker: {source_filename}.reprocessed")
        return True
    
    # Write file to watch folder
    try:
        WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
        output_path.write_text(original_text, encoding='utf-8')
        logger.info(f"Created: {output_path.name} ({len(original_text)} chars)")
        
        # Create marker
        create_reprocess_marker(source_filename)
        logger.info(f"Created marker: {source_filename}.reprocessed")
        return True
    except Exception as e:
        logger.error(f"Failed to write {output_path.name}: {e}")
        return False


def main(dry_run: bool = True):
    """Main reprocessing function."""
    global CONFIG, WATCH_FOLDER, OUTPUT_DIR, ARCHIVE_DIR, MARKER_DIR
    
    CONFIG = load_config()
    WATCH_FOLDER = Path(CONFIG["watch_folder"])
    OUTPUT_DIR = Path(CONFIG["output_dir"])
    ARCHIVE_DIR = Path(CONFIG["archive_dir"])
    MARKER_DIR = Path(CONFIG["marker_dir"])
    
    logger.info("="*70)
    logger.info("REPROCESS OUTPUT - Extract sources from 04_output and 03_archive")
    logger.info("="*70)
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'EXECUTING'}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Archive directory: {ARCHIVE_DIR}")
    logger.info(f"Watch folder: {WATCH_FOLDER}")
    logger.info(f"Marker directory: {MARKER_DIR}")
    logger.info(f"Process output: {CONFIG.get('process_output', True)}")
    logger.info(f"Process archive: {CONFIG.get('process_archive', True)}")
    
    # Force OneDrive sync if configured
    if not dry_run:
        force_onedrive_sync()
    
    # Cleanup old markers (if configured)
    if CONFIG.get("cleanup_markers_days", 180) and not dry_run:
        try:
            cleanup_days = CONFIG.get("cleanup_markers_days", 180)
            cutoff = datetime.now() - timedelta(days=cleanup_days)
            cleaned_count = 0
            
            if MARKER_DIR.exists():
                for marker in MARKER_DIR.glob("*"):
                    if marker.is_file() and marker.stat().st_mtime < cutoff.timestamp():
                        marker.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned old marker: {marker.name}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned {cleaned_count} old markers (> {cleanup_days} days)")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup markers: {cleanup_error}")
    
    total_successful = 0
    total_failed = 0
    total_skipped = 0
    
    # Process 04_output sessions
    if CONFIG.get("process_output", True):
        logger.info("\n" + "-"*70)
        logger.info("PROCESSING 04_OUTPUT SESSIONS")
        logger.info("-"*70)
        
        sessions = find_session_directories(OUTPUT_DIR)
        if sessions:
            # Limit sessions if configured
            max_sessions = CONFIG.get("max_sessions")
            if max_sessions:
                sessions = sessions[:max_sessions]
                logger.info(f"Limited to {max_sessions} sessions")
            
            # Process sessions
            for session_dir in sessions:
                try:
                    result = reprocess_session(session_dir, dry_run=dry_run)
                    if result:
                        total_successful += 1
                    else:
                        total_skipped += 1
                except Exception as e:
                    logger.error(f"Error processing {session_dir.name}: {e}")
                    # Create marker to prevent retry spam on errors
                    try:
                        source_filename = get_source_filename(session_dir)
                        create_reprocess_marker(source_filename)
                    except Exception:
                        pass
                    total_failed += 1
        else:
            logger.warning("No session directories found in 04_output")
    
    # Process 03_archive files
    if CONFIG.get("process_archive", True):
        logger.info("\n" + "-"*70)
        logger.info("PROCESSING 03_ARCHIVE FILES")
        logger.info("-"*70)
        
        archive_files = find_archive_files(ARCHIVE_DIR)
        if archive_files:
            # Limit files if configured
            max_files = CONFIG.get("max_sessions")  # Reuse same limit
            if max_files:
                archive_files = archive_files[:max_files]
                logger.info(f"Limited to {max_files} archive files")
            
            # Process archive files
            for archive_file in archive_files:
                try:
                    result = reprocess_archive_file(archive_file, dry_run=dry_run)
                    if result:
                        total_successful += 1
                    else:
                        total_skipped += 1
                except Exception as e:
                    logger.error(f"Error processing {archive_file.name}: {e}")
                    total_failed += 1
        else:
            logger.warning("No archive files found in 03_archive")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("REPROCESSING SUMMARY")
    logger.info("="*70)
    logger.info(f"Successful: {total_successful}")
    logger.info(f"Skipped: {total_skipped}")
    logger.info(f"Failed: {total_failed}")
    total_processed = total_successful + total_skipped + total_failed
    logger.info(f"Total: {total_processed}")


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestGetOriginalText(unittest.TestCase):
    """Test get_original_text function."""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: self._rmtree(self.test_dir))
    
    def _rmtree(self, path):
        import shutil
        try:
            shutil.rmtree(path)
        except:
            pass
    
    def test_transcript_priority(self):
        """Test that transcript.md is preferred over chunks."""
        sess = self.test_dir / "test_session"
        sess.mkdir()
        
        (sess / "transcript.md").write_text("transcript content")
        (sess / "chunk_00000.txt").write_text("chunk content")
        
        result = get_original_text(sess)
        self.assertEqual(result, "transcript content")
    
    def test_fallback_to_chunks(self):
        """Test fallback to chunks when transcript.md missing."""
        sess = self.test_dir / "no_transcript"
        sess.mkdir()
        
        (sess / "chunk_00000.txt").write_text("chunk1")
        (sess / "chunk_00001.txt").write_text("chunk2")
        
        result = get_original_text(sess)
        self.assertEqual(result, "chunk1\n\nchunk2")
    
    def test_no_content(self):
        """Test handling when no content available."""
        sess = self.test_dir / "empty"
        sess.mkdir()
        
        result = get_original_text(sess)
        self.assertIsNone(result)
    
    def test_chunk_ordering(self):
        """Test that chunks are processed in correct order."""
        sess = self.test_dir / "ordered"
        sess.mkdir()
        
        (sess / "chunk_00002.txt").write_text("third")
        (sess / "chunk_00000.txt").write_text("first")
        (sess / "chunk_00001.txt").write_text("second")
        
        result = get_original_text(sess)
        self.assertEqual(result, "first\n\nsecond\n\nthird")


class TestSourceFilename(unittest.TestCase):
    """Test get_source_filename function."""
    
    def test_sidecar_extraction(self):
        """Test extraction from sidecar JSON."""
        sess = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: self._rmtree(sess))
        
        sidecar = sess / "test_sidecar.json"
        sidecar.write_text(json.dumps({
            "metadata": {
                "original_path": "C:/path/to/original_file.md"
            }
        }))
        
        result = get_source_filename(sess)
        self.assertEqual(result, "original_file.md")
    
    def test_timestamp_parsing(self):
        """Test parsing from timestamp-prefixed directory name."""
        sess = Path("20251118_123456_my_document_chunk001")
        result = get_source_filename(sess)
        self.assertEqual(result, "my_document")
    
    def test_fallback_to_dirname(self):
        """Test fallback to directory name."""
        sess = Path("unusual_format_directory")
        result = get_source_filename(sess)
        self.assertEqual(result, "unusual_format_directory")
    
    def _rmtree(self, path):
        import shutil
        try:
            shutil.rmtree(path)
        except:
            pass


class TestMarkerLogic(unittest.TestCase):
    """Test marker creation and skip logic."""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.marker_dir = self.test_dir / ".reprocessed_sources"
        self.addCleanup(lambda: self._rmtree(self.test_dir))
    
    def _rmtree(self, path):
        import shutil
        try:
            shutil.rmtree(path)
        except:
            pass
    
    def test_marker_creation(self):
        """Test marker file creation."""
        global MARKER_DIR
        old_marker = MARKER_DIR
        MARKER_DIR = self.marker_dir
        
        try:
            marker = create_reprocess_marker("test_file.txt")
            self.assertTrue(marker.exists())
            self.assertTrue(marker.read_text())  # Contains timestamp
        finally:
            MARKER_DIR = old_marker
    
    def test_skip_logic(self):
        """Test skip logic when marker exists."""
        global MARKER_DIR, CONFIG
        old_marker = MARKER_DIR
        old_config = CONFIG.copy()
        
        MARKER_DIR = self.marker_dir
        CONFIG = {"skip_marked": True}
        
        try:
            # Create marker
            marker = self.marker_dir / "test_file.txt.reprocessed"
            self.marker_dir.mkdir(parents=True)
            marker.write_text("2025-11-18T12:00:00")
            
            # Check skip
            result = is_already_reprocessed("test_file.txt")
            self.assertTrue(result)
        finally:
            MARKER_DIR = old_marker
            CONFIG.clear()
            CONFIG.update(old_config)


class TestOneDriveSync(unittest.TestCase):
    """Test OneDrive sync functionality."""
    
    @patch("os.system")
    def test_force_onedrive_sync(self, mock_system):
        """Test OneDrive sync commands."""
        global CONFIG
        old_config = CONFIG.copy()
        CONFIG = {
            "force_onedrive_sync": True,
            "onedrive_exe": r"C:\Program Files\Microsoft OneDrive\onedrive.exe"
        }
        
        try:
            force_onedrive_sync()
            # Should call shutdown and start
            self.assertGreaterEqual(mock_system.call_count, 2)
        finally:
            CONFIG.clear()
            CONFIG.update(old_config)
    
    @patch("os.system")
    def test_skip_sync_when_disabled(self, mock_system):
        """Test that sync is skipped when disabled."""
        global CONFIG
        old_config = CONFIG.copy()
        CONFIG = {"force_onedrive_sync": False}
        
        try:
            force_onedrive_sync()
            mock_system.assert_not_called()
        finally:
            CONFIG.clear()
            CONFIG.update(old_config)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Integration tests with mocked OneDrive."""
    
    @patch("reprocess_output.force_onedrive_sync")
    def test_integration_flow(self, mock_sync):
        """Test full integration flow."""
        with tempfile.TemporaryDirectory() as tmp:
            watch = Path(tmp) / "02_data"
            output = Path(tmp) / "04_output"
            watch.mkdir()
            output.mkdir()
            
            # Create fake session
            sess = output / "20251118_000000_test_doc"
            sess.mkdir()
            (sess / "transcript.md").write_text("Integration test content")
            
            # Override globals
            global WATCH_FOLDER, OUTPUT_DIR, MARKER_DIR, CONFIG, CONFIG_FILE
            old_w, old_o, old_m = WATCH_FOLDER, OUTPUT_DIR, MARKER_DIR
            old_config = CONFIG.copy()
            old_config_file = CONFIG_FILE
            
            # Create temp config file
            temp_config = Path(tmp) / "reprocess_config.json"
            temp_config.write_text(json.dumps({
                "watch_folder": str(watch),
                "output_dir": str(output),
                "marker_dir": str(watch / ".reprocessed_sources"),
                "force_onedrive_sync": False,
                "skip_marked": True,
                "timestamp_prefix": True,
                "file_extension": ".txt",
            }))
            
            WATCH_FOLDER = watch
            OUTPUT_DIR = output
            MARKER_DIR = watch / ".reprocessed_sources"
            CONFIG_FILE = temp_config
            CONFIG = load_config()
            
            try:
                # Run reprocessing
                main(dry_run=False)
                
                # Verify file created
                created = list(watch.glob("reprocess_*.txt"))
                self.assertGreaterEqual(len(created), 1, f"Should create at least one file, found: {[f.name for f in created]}")
                self.assertIn("Integration test content", created[0].read_text())
            finally:
                WATCH_FOLDER, OUTPUT_DIR, MARKER_DIR = old_w, old_o, old_m
                CONFIG_FILE = old_config_file
                CONFIG.clear()
                CONFIG.update(old_config)


# ============================================================================
# END-TO-END TESTS
# ============================================================================

class TestEndToEnd(unittest.TestCase):
    """Full end-to-end tests."""
    
    def test_full_cycle(self):
        """Test complete reprocessing cycle."""
        with tempfile.TemporaryDirectory() as tmp:
            # Setup temp directories
            watch = Path(tmp) / "02_data"
            output = Path(tmp) / "04_output"
            archive = Path(tmp) / "03_archive"
            watch.mkdir()
            output.mkdir()
            archive.mkdir()
            
            # Create fake OneDrive session
            sess = output / "20251118_000000_test_document_chunk001"
            sess.mkdir()
            (sess / "transcript.md").write_text("Hello world - e2e test")
            
            # Create sidecar for filename extraction
            (sess / "test_sidecar.json").write_text(json.dumps({
                "metadata": {
                    "original_path": "C:/test/test_document.md"
                }
            }))
            
            # Create fake archive file
            admin_dir = archive / "admin"
            admin_dir.mkdir()
            archive_file = admin_dir / "test_archive_file_20251118_120000.md"
            archive_file.write_text("Archive file content - e2e test")
            
            # Override globals for test
            global WATCH_FOLDER, OUTPUT_DIR, ARCHIVE_DIR, MARKER_DIR, CONFIG, CONFIG_FILE
            old_w, old_o, old_a, old_m = WATCH_FOLDER, OUTPUT_DIR, ARCHIVE_DIR, MARKER_DIR
            old_config = CONFIG.copy()
            old_config_file = CONFIG_FILE
            
            # Create temp config file
            temp_config = Path(tmp) / "reprocess_config.json"
            temp_config.write_text(json.dumps({
                "watch_folder": str(watch),
                "output_dir": str(output),
                "archive_dir": str(archive),
                "marker_dir": str(watch / ".reprocessed_sources"),
                "force_onedrive_sync": False,
                "skip_marked": True,
                "timestamp_prefix": True,
                "file_extension": ".txt",
                "process_output": True,
                "process_archive": True,
                "supported_extensions": [".txt", ".md"],
            }))
            
            WATCH_FOLDER = watch
            OUTPUT_DIR = output
            ARCHIVE_DIR = archive
            MARKER_DIR = watch / ".reprocessed_sources"
            CONFIG_FILE = temp_config
            CONFIG = load_config()
            
            try:
                # Run real logic (no dry-run)
                main(dry_run=False)
                
                # Verify files appeared in watch folder
                created = list(watch.glob("reprocess_*.txt")) + list(watch.glob("reprocess_*.md"))
                self.assertGreaterEqual(len(created), 1, f"Should create at least one file, found: {[f.name for f in created]}")
                
                # Verify content from output
                output_files = [f for f in created if "test_document" in f.name]
                if output_files:
                    content = output_files[0].read_text()
                    self.assertIn("Hello world - e2e test", content)
                
                # Verify content from archive
                archive_files = [f for f in created if "archive_file" in f.name]
                if archive_files:
                    content = archive_files[0].read_text()
                    self.assertIn("Archive file content - e2e test", content)
                
                # Verify markers created
                markers = list(MARKER_DIR.glob("*.reprocessed"))
                self.assertGreaterEqual(len(markers), 1, "Should create markers")
                
            finally:
                # Cleanup and restore globals
                WATCH_FOLDER, OUTPUT_DIR, ARCHIVE_DIR, MARKER_DIR = old_w, old_o, old_a, old_m
                CONFIG_FILE = old_config_file
                CONFIG.clear()
                CONFIG.update(old_config)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def run_tests():
    """Run unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGetOriginalText))
    suite.addTests(loader.loadTestsFromTestCase(TestSourceFilename))
    suite.addTests(loader.loadTestsFromTestCase(TestMarkerLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestOneDriveSync))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_e2e_tests():
    """Run end-to-end tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def edit_config():
    """Open config file in default editor."""
    try:
        import click
        click.edit(filename=str(CONFIG_FILE))
        logger.info(f"Config file edited: {CONFIG_FILE}")
    except ImportError:
        # Fallback: try to open with default system editor
        try:
            import subprocess
            import platform
            if platform.system() == 'Windows':
                os.startfile(CONFIG_FILE)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(CONFIG_FILE)])
            else:
                subprocess.run(['xdg-open', str(CONFIG_FILE)])
            logger.info(f"Opened {CONFIG_FILE} in default editor")
            logger.info("Press Enter when done editing...")
            input()
        except Exception as e:
            # Final fallback: print instructions
            logger.info(f"Please edit {CONFIG_FILE} manually")
            logger.info(f"File location: {CONFIG_FILE.absolute()}")
            logger.info("Press Enter when done...")
            input()
        logger.info("Config will be reloaded on next run")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reprocess output files from 04_output to 02_data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually reprocess files (default is dry-run)"
    )
    parser.add_argument(
        "--edit-config",
        action="store_true",
        help="Edit reprocess_config.json"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run unit tests"
    )
    parser.add_argument(
        "--e2e-test",
        action="store_true",
        help="Run end-to-end tests"
    )
    
    args = parser.parse_args()
    
    # Handle test flags
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    if args.e2e_test:
        success = run_e2e_tests()
        sys.exit(0 if success else 1)
    
    # Handle config editing
    if args.edit_config:
        edit_config()
        sys.exit(0)
    
    # Run main reprocessing
    try:
        main(dry_run=not args.execute)
    except KeyboardInterrupt:
        logger.info("\n\nReprocessing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)

