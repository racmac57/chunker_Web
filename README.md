# Chunker Project - Final Migration

This project has been migrated to C:/_chunker on 2025-08-25 18:58:28.

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
