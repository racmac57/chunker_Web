#!/usr/bin/env python3
"""
Final migration script to move current working scripts to C:\_chunker
and properly archive existing files.
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def archive_existing_files():
    """Move existing files from C:\_chunker to 03_archive"""
    
    base_dir = Path("C:/_chunker")
    archive_dir = base_dir / "03_archive"
    
    print("Archiving existing files in C:/_chunker...")
    
    if not base_dir.exists():
        print("[INFO] C:/_chunker does not exist - nothing to archive")
        return
    
    # Get all files and directories in C:\_chunker
    for item in base_dir.iterdir():
        # Skip 03_archive directory itself
        if item.name == "03_archive":
            continue
            
        # Create archive path
        archive_path = archive_dir / item.name
        if archive_path.exists():
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = archive_dir / f"{item.name}_{timestamp}"
        
        try:
            if item.is_file():
                shutil.move(str(item), str(archive_path))
                print(f"[OK] Archived file: {item.name}")
            elif item.is_dir():
                shutil.move(str(item), str(archive_path))
                print(f"[OK] Archived directory: {item.name}")
        except Exception as e:
            print(f"[ERROR] Could not archive {item.name}: {e}")

def move_current_scripts():
    """Move current working scripts to C:\_chunker"""
    
    current_dir = Path("C:/_chunker/01_scripts/new_chunker_project")
    target_dir = Path("C:/_chunker")
    
    print("Moving current working scripts...")
    
    # Files to move
    files_to_move = [
        "watcher_splitter.py",
        "chunker_db.py", 
        "notification_system.py",
        "test_fixes.py",
        "test_filter_modes.py",
        "chunker_tracking.db"
    ]
    
    # Directories to move
    dirs_to_move = [
        "logs"
    ]
    
    # Move individual files
    for file in files_to_move:
        src = current_dir / file
        dst = target_dir / file
        if src.exists():
            try:
                shutil.copy2(src, dst)
                print(f"[OK] Moved file: {file}")
            except Exception as e:
                print(f"[ERROR] Could not move {file}: {e}")
    
    # Move directories
    for dir_name in dirs_to_move:
        src = current_dir / dir_name
        dst = target_dir / dir_name
        if src.exists():
            try:
                if dst.exists():
                    # Copy contents if destination exists
                    for item in src.iterdir():
                        if item.is_file():
                            shutil.copy2(item, dst / item.name)
                else:
                    shutil.copytree(src, dst)
                print(f"[OK] Moved directory: {dir_name}")
            except Exception as e:
                print(f"[ERROR] Could not move {dir_name}: {e}")

def create_directories():
    """Create necessary directories"""
    
    base_dir = Path("C:/_chunker")
    directories = [
        "02_data",
        "03_archive", 
        "04_output",
        "05_logs",
        "06_config"
    ]
    
    print("Creating directory structure...")
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"[OK] Created directory: {dir_name}")

def update_config():
    """Update configuration with new paths"""
    
    config_file = Path("C:/_chunker/config.json")
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update paths
            config["watch_folder"] = "C:/_chunker/02_data"
            config["output_dir"] = "C:/_chunker/04_output"
            config["archive_dir"] = "C:/_chunker/03_archive"
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"[OK] Updated config.json with new paths")
        except Exception as e:
            print(f"[ERROR] Could not update config.json: {e}")

def create_readme():
    """Create README file"""
    
    readme_content = f"""# Chunker Project - Final Migration

This project has been migrated to C:/_chunker on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

## Directory Structure

- **C:/_chunker** - Main project directory with scripts
- **02_data/** - Input files to be processed (watch folder)
- **03_archive/** - Archived original files and processed source files
- **04_output/** - Generated chunks and transcripts (organized by source file)
- **05_logs/** - Application logs and tracking
- **06_config/** - Configuration files

## Quick Start

1. Place files to process in `02_data/` folder
2. Run the watcher: `python watcher_splitter.py`
3. Check `04_output/` for processed chunks and transcripts
4. Original files are moved to `03_archive/` after processing

## Features

- [x] Organized output by source file name
- [x] Admin files output as .md with headers
- [x] All other files output as .txt
- [x] Automatic file organization and archiving
- [x] Database tracking and logging

## Configuration

Edit `config.json` to customize:
- File filter modes (all, patterns, suffix)
- Supported file extensions
- Chunk sizes and processing options
- Notification settings
"""
    
    readme_file = Path("C:/_chunker/README.md")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("[OK] Created README.md")

def main():
    """Main migration function"""
    
    print("=== Final Migration Script ===")
    print("Moving current scripts to C:/_chunker\n")
    
    # Step 1: Archive existing files
    archive_existing_files()
    print()
    
    # Step 2: Create directory structure
    create_directories()
    print()
    
    # Step 3: Move current scripts
    move_current_scripts()
    print()
    
    # Step 4: Update configuration
    update_config()
    print()
    
    # Step 5: Create README
    create_readme()
    print()
    
    print("=== Migration Complete ===")
    print("Project successfully moved to C:/_chunker")
    print("\nNext steps:")
    print("1. Place files to process in 02_data/ folder")
    print("2. Run: python watcher_splitter.py")
    print("\nYour original files are safely archived in 03_archive/")

if __name__ == "__main__":
    main()
