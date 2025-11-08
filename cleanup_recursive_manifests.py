#!/usr/bin/env python3
"""Cleanup script for recursive manifest files and oversized folders"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(r"C:\_chunker")
DATA_DIR = BASE_DIR / "02_data"
OUTPUT_DIR = BASE_DIR / "04_output"
ARCHIVE_DIR = BASE_DIR / "03_archive"

def cleanup():
    print("=== Chunker Cleanup Script ===\n")

    # 1. Remove recursive .origin.json files
    print("1. Cleaning recursive manifest files...")
    recursive_manifests = list(DATA_DIR.rglob("*.origin.json.origin.json*"))
    print(f"   Found {len(recursive_manifests)} recursive manifest files")

    for file in recursive_manifests:
        print(f"   Removing: {file.name}")
        try:
            file.unlink()
        except Exception as e:
            print(f"   Error removing {file.name}: {e}")

    # 2. Remove oversized/malformed output folders
    print("\n2. Cleaning oversized/malformed output folders...")
    bad_folders = []

    if OUTPUT_DIR.exists():
        for folder in OUTPUT_DIR.iterdir():
            if folder.is_dir() and (len(folder.name) > 100 or '.origin.json' in folder.name):
                bad_folders.append(folder)

    print(f"   Found {len(bad_folders)} problematic folders")

    for folder in bad_folders:
        print(f"   Removing: {folder.name[:80]}...")
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print(f"   Error removing {folder.name[:80]}: {e}")

    # 3. Clean manifest files from archive
    print("\n3. Cleaning manifest files from archive...")
    archive_manifests = []

    if ARCHIVE_DIR.exists():
        archive_manifests = list(ARCHIVE_DIR.rglob("*.origin.json*"))

    print(f"   Found {len(archive_manifests)} manifest files in archive")

    for file in archive_manifests:
        print(f"   Removing: {file.name}")
        try:
            file.unlink()
        except Exception as e:
            print(f"   Error removing {file.name}: {e}")

    # Summary
    print("\n=== Cleanup Complete ===")
    print(f"Recursive manifests removed: {len(recursive_manifests)}")
    print(f"Bad output folders removed: {len(bad_folders)}")
    print(f"Archive manifests removed: {len(archive_manifests)}")
    print("\nIt is now safe to restart the watcher.")

if __name__ == "__main__":
    cleanup()
