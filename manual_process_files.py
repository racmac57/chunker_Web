"""
Manual File Processing Script for Chunker_v2
Process existing files in the watch folder without waiting for file events
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/manual_process.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    """Load configuration from config.json"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

def find_files_to_process(watch_folder: str, supported_extensions: List[str],
                          exclude_patterns: List[str]) -> List[Path]:
    """
    Find all files in watch folder that need processing.

    Args:
        watch_folder: Folder to scan
        supported_extensions: List of file extensions to process
        exclude_patterns: Patterns to exclude from processing

    Returns:
        List of Path objects to process
    """
    files_to_process = []
    watch_path = Path(watch_folder)

    if not watch_path.exists():
        logger.error(f"Watch folder does not exist: {watch_folder}")
        return []

    logger.info(f"Scanning folder: {watch_folder}")
    logger.info(f"Supported extensions: {supported_extensions}")
    logger.info(f"Exclude patterns: {exclude_patterns}")

    # Scan for all supported file types
    for ext in supported_extensions:
        matching_files = list(watch_path.glob(f"*{ext}"))
        logger.info(f"Found {len(matching_files)} files with extension {ext}")

        for file_path in matching_files:
            # Skip excluded patterns
            if any(pattern in file_path.name for pattern in exclude_patterns):
                logger.debug(f"Skipping excluded file: {file_path.name}")
                continue

            # Skip directories
            if file_path.is_dir():
                logger.debug(f"Skipping directory: {file_path.name}")
                continue

            # Skip system files
            if file_path.name.startswith('.'):
                logger.debug(f"Skipping hidden file: {file_path.name}")
                continue

            files_to_process.append(file_path)
            logger.info(f"  ✓ Will process: {file_path.name}")

    return files_to_process

def process_file_manually(file_path: Path, config: dict) -> bool:
    """
    Manually process a single file.

    Args:
        file_path: Path to the file
        config: Configuration dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {file_path.name}")
        logger.info(f"{'='*60}")

        # Import processing function
        from watcher_splitter import process_file_enhanced

        # Check if file exists and is readable
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False

        if not os.access(file_path, os.R_OK):
            logger.error(f"File not readable: {file_path}")
            return False

        # Get file info
        file_size = file_path.stat().st_size
        logger.info(f"File size: {file_size} bytes")
        logger.info(f"File type: {file_path.suffix}")

        # Process the file
        start_time = time.time()
        success = process_file_enhanced(file_path, config)
        processing_time = time.time() - start_time

        if success:
            logger.info(f"✓ Successfully processed in {processing_time:.2f}s")
            return True
        else:
            logger.error(f"✗ Failed to process {file_path.name}")
            return False

    except Exception as e:
        logger.exception(f"Error processing {file_path.name}: {e}")
        return False

def main(auto_confirm=False):
    """Main entry point for manual file processing"""
    logger.info("\n" + "="*80)
    logger.info("MANUAL FILE PROCESSING SCRIPT - Chunker_v2")
    logger.info("="*80 + "\n")

    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration")
    logger.info(f"Watch folder: {config['watch_folder']}")
    logger.info(f"Output folder: {config['output_dir']}")
    logger.info(f"Archive folder: {config['archive_dir']}")

    # Create directories if they don't exist
    os.makedirs(config['output_dir'], exist_ok=True)
    os.makedirs(config['archive_dir'], exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Find files to process
    files_to_process = find_files_to_process(
        config['watch_folder'],
        config.get('supported_extensions', ['.txt', '.md', '.py']),
        config.get('exclude_patterns', [])
    )

    if not files_to_process:
        logger.warning("\n⚠️  No files found to process!")
        logger.info(f"Please check:")
        logger.info(f"  1. Watch folder exists: {config['watch_folder']}")
        logger.info(f"  2. Files have supported extensions: {config.get('supported_extensions', [])}")
        logger.info(f"  3. Files are not excluded by patterns: {config.get('exclude_patterns', [])}")
        return

    logger.info(f"\n{'='*80}")
    logger.info(f"Found {len(files_to_process)} files to process")
    logger.info(f"{'='*80}\n")

    # Ask for confirmation unless auto mode
    if not auto_confirm:
        response = input(f"Process {len(files_to_process)} files? (y/n): ").strip().lower()
        if response != 'y':
            logger.info("Processing cancelled by user")
            return
    else:
        logger.info("Auto-confirm mode: Processing files automatically")

    # Process each file
    successful = 0
    failed = 0

    for i, file_path in enumerate(files_to_process, 1):
        logger.info(f"\n[{i}/{len(files_to_process)}] Processing {file_path.name}...")

        if process_file_manually(file_path, config):
            successful += 1
        else:
            failed += 1

        # Small delay between files
        if i < len(files_to_process):
            time.sleep(0.5)

    # Print summary
    logger.info(f"\n{'='*80}")
    logger.info(f"PROCESSING COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"✓ Successful: {successful}")
    logger.info(f"✗ Failed: {failed}")
    logger.info(f"Total: {len(files_to_process)}")
    logger.info(f"{'='*80}\n")

    # Show output locations
    if successful > 0:
        logger.info(f"Output files saved to: {config['output_dir']}")
        logger.info(f"Archived files moved to: {config['archive_dir']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manual file processing for Chunker_v2')
    parser.add_argument('--auto', action='store_true', help='Auto-confirm processing without prompting')
    args = parser.parse_args()
    
    try:
        main(auto_confirm=args.auto)
    except KeyboardInterrupt:
        logger.info("\n\nProcessing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
