#!/usr/bin/env python3
"""
Script to process existing files in the 02_data folder
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from watcher_splitter import process_file_enhanced
from chunker_db import ChunkerDatabase

def process_existing_files():
    """Process all existing files in the 02_data folder"""
    
    # Load configuration
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found!")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    watch_folder = Path(config.get("watch_folder", "02_data"))
    output_dir = Path(config.get("output_dir", "04_output"))
    archive_dir = Path(config.get("archive_dir", "03_archive"))
    
    print(f"🔍 Scanning folder: {watch_folder}")
    print(f"📤 Output directory: {output_dir}")
    print(f"📦 Archive directory: {archive_dir}")
    
    # Ensure directories exist
    output_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)
    
    # Get list of files to process
    if not watch_folder.exists():
        print(f"❌ Watch folder {watch_folder} does not exist!")
        return
    
    files_to_process = []
    supported_extensions = config.get("supported_extensions", [".txt", ".md", ".json", ".csv"])
    
    print(f"🔍 Looking for files with extensions: {supported_extensions}")
    
    for file_path in watch_folder.iterdir():
        print(f"   Checking: {file_path.name} (suffix: {file_path.suffix.lower()})")
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files_to_process.append(file_path)
            print(f"   ✅ Added to processing list: {file_path.name}")
        else:
            print(f"   ❌ Skipped: {file_path.name}")
    
    if not files_to_process:
        print("✅ No files found to process in the watch folder.")
        return
    
    print(f"📄 Found {len(files_to_process)} files to process:")
    for file_path in files_to_process:
        print(f"   - {file_path.name}")
    
    # Initialize database
    db = ChunkerDatabase()
    
    # Process each file
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n🔄 Processing file {i}/{len(files_to_process)}: {file_path.name}")
        
        try:
            # Process the file using the enhanced processing function
            result = process_file_enhanced(
                str(file_path),
                str(output_dir),
                str(archive_dir),
                config,
                db
            )
            
            if result.get("success"):
                print(f"✅ Successfully processed: {file_path.name}")
                print(f"   📊 Chunks created: {result.get('chunk_count', 0)}")
                print(f"   📄 Transcript created: {result.get('transcript_created', False)}")
            else:
                print(f"❌ Failed to process: {file_path.name}")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
    
    print(f"\n🎉 Processing complete! Check {output_dir} for results.")

if __name__ == "__main__":
    process_existing_files()
