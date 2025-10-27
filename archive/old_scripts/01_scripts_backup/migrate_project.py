#!/usr/bin/env python3
"""
Migration script to relocate the chunker project to C:/_chunker
and organize existing files into the archive folder.
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def check_current_state():
    """Check what's currently in C:\_chunker"""
    current_base = Path("C:/_chunker")
    
    if not current_base.exists():
        print("[OK] C:/_chunker directory does not exist - will create new structure")
        return
    
    print("Current contents of C:/_chunker:")
    try:
        for item in current_base.iterdir():
            if item.is_file():
                print(f"  [FILE] {item.name}")
            elif item.is_dir():
                print(f"  [DIR] {item.name}/")
    except Exception as e:
        print(f"⚠ Warning: Could not read C:\\_chunker contents: {e}")
    print()

def create_directory_structure():
    """Create the new directory structure"""
    base_dir = Path("C:/_chunker")
    
    # Create main directories
    directories = [
        base_dir,
        base_dir / "01_scripts",
        base_dir / "02_data", 
        base_dir / "03_archive",
        base_dir / "04_output",
        base_dir / "05_logs",
        base_dir / "06_config"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {directory}")
    
    return base_dir

def move_project_files(current_dir, new_base_dir):
    """Move the current project files to the new location"""
    
    # Files to move to 01_scripts
    script_files = [
        "watcher_splitter.py",
        "chunker_db.py", 
        "notification_system.py",
        "test_fixes.py",
        "test_filter_modes.py",
        "migrate_project.py"
    ]
    
    # Files to move to 06_config
    config_files = [
        "config.json",
        "chunking_config.json"
    ]
    
    # Move script files
    for file in script_files:
        src = current_dir / file
        dst = new_base_dir / "01_scripts" / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"[OK] Moved script: {file}")
    
    # Move config files
    for file in config_files:
        src = current_dir / file
        dst = new_base_dir / "06_config" / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"[OK] Moved config: {file}")
    
    # Move logs directory
    logs_src = current_dir / "logs"
    logs_dst = new_base_dir / "05_logs"
    if logs_src.exists():
        try:
            if logs_dst.exists():
                # Copy files from existing logs instead of removing
                for log_file in logs_src.iterdir():
                    if log_file.is_file():
                        shutil.copy2(log_file, logs_dst / log_file.name)
                print(f"[OK] Copied logs to existing directory")
            else:
                shutil.copytree(logs_src, logs_dst)
                print(f"[OK] Moved logs directory")
        except Exception as e:
            print(f"⚠ Warning: Could not move logs directory: {e}")
            # Try to copy individual files
            try:
                for log_file in logs_src.iterdir():
                    if log_file.is_file():
                        shutil.copy2(log_file, logs_dst / log_file.name)
                print(f"[OK] Copied individual log files")
            except Exception as e2:
                print(f"⚠ Warning: Could not copy log files: {e2}")
    
    # Move database file
    db_src = current_dir / "chunker_tracking.db"
    db_dst = new_base_dir / "01_scripts" / "chunker_tracking.db"
    if db_src.exists():
        shutil.copy2(db_src, db_dst)
        print(f"[OK] Moved database: chunker_tracking.db")

def archive_existing_files(current_dir, new_base_dir):
    """Move existing files from C:\_chunker to 03_archive"""
    
    archive_dir = new_base_dir / "03_archive"
    current_base = Path("C:/_chunker")
    
    # Get all files and directories in the current C:\_chunker (excluding our new structure)
    if current_base.exists():
        for item in current_base.iterdir():
            # Skip our new directory structure
            if item.name in ["01_scripts", "02_data", "03_archive", "04_output", "05_logs", "06_config"]:
                continue
                
            # Move everything else to archive
            archive_path = archive_dir / item.name
            if archive_path.exists():
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = archive_dir / f"{item.name}_{timestamp}"
            
            try:
                if item.is_file():
                    shutil.copy2(item, archive_path)
                    try:
                        item.unlink()  # Try to remove original
                        print(f"[OK] Archived and removed file: {item.name}")
                    except PermissionError:
                        print(f"[OK] Archived file (could not remove original): {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, archive_path)
                    try:
                        shutil.rmtree(item)  # Try to remove original
                        print(f"[OK] Archived and removed directory: {item.name}")
                    except PermissionError:
                        print(f"[OK] Archived directory (could not remove original): {item.name}")
            except Exception as e:
                print(f"⚠ Warning: Could not archive {item.name}: {e}")

def update_config_paths(new_base_dir):
    """Update configuration files with new paths"""
    
    config_file = new_base_dir / "06_config" / "config.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update paths to use new structure
            config["watch_folder"] = str(new_base_dir / "02_data")
            config["output_dir"] = str(new_base_dir / "04_output")
            config["archive_dir"] = str(new_base_dir / "03_archive")
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"[OK] Updated config.json with new paths")
        except Exception as e:
            print(f"⚠ Warning: Could not update config.json: {e}")

def create_readme(new_base_dir):
    """Create a README file for the new project structure"""
    
    readme_content = f"""# Chunker Project - Relocated Structure

This project has been migrated to a new organized structure on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

## Directory Structure

- **01_scripts/** - Python scripts and main application files
- **02_data/** - Input files to be processed (watch folder)
- **03_archive/** - Archived original files and processed source files
- **04_output/** - Generated chunks and transcripts (organized by source file)
- **05_logs/** - Application logs and tracking
- **06_config/** - Configuration files

## Quick Start

1. Place files to process in `02_data/` folder
2. Run the watcher: `python 01_scripts/watcher_splitter.py`
3. Check `04_output/` for processed chunks and transcripts
4. Original files are moved to `03_archive/` after processing

## Features

- [x] Organized output by source file name
- [x] Admin files output as .md with headers
- [x] All other files output as .txt
- [x] Automatic file organization and archiving
- [x] Database tracking and logging

## Configuration

Edit `06_config/config.json` to customize:
- File filter modes (all, patterns, suffix)
- Supported file extensions
- Chunk sizes and processing options
- Notification settings
"""
    
    readme_file = new_base_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print(f"[OK] Created README.md")

def main():
    """Main migration function"""
    
    print("=== Chunker Project Migration ===")
    print("Moving project to C:/_chunker with organized structure\n")
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Current location: {current_dir}")
    
    # Check current state of C:\_chunker
    print("Checking current state of C:/_chunker...")
    check_current_state()
    print()
    
    # Create new directory structure
    new_base_dir = create_directory_structure()
    print()
    
    # Archive existing files in C:\_chunker
    print("Archiving existing files...")
    archive_existing_files(current_dir, new_base_dir)
    print()
    
    # Move project files
    print("Moving project files...")
    move_project_files(current_dir, new_base_dir)
    print()
    
    # Update configuration
    print("Updating configuration...")
    update_config_paths(new_base_dir)
    print()
    
    # Create README
    print("Creating documentation...")
    create_readme(new_base_dir)
    print()
    
    print("=== Migration Complete ===")
    print(f"Project successfully moved to: {new_base_dir}")
    print("\nNext steps:")
    print("1. Navigate to the new location: cd C:/_chunker")
    print("2. Place files to process in 02_data/ folder")
    print("3. Run: python 01_scripts/watcher_splitter.py")
    print("\nYour original files are safely archived in 03_archive/")

if __name__ == "__main__":
    main()
