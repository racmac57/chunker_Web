#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for origin tracking and write-back enhancements.

This script checks if all three enhancements are properly implemented:
1. Enhanced sidecar with origin metadata
2. Better front matter with origin info
3. Sidecar copy to source in write-back

Usage:
    python verify_enhancements.py

Author: R. A. Carucci
Date: 2025-10-30
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors='replace')


def check_config():
    """Verify config.json has the new setting."""
    print("\n=== Checking Configuration ===")

    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found")
        return False

    with open(config_path) as f:
        config = json.load(f)

    # Check for new config option
    if config.get("copy_sidecar_to_source"):
        print("✅ copy_sidecar_to_source: enabled")
    else:
        print("⚠️  copy_sidecar_to_source: not set (will default to True)")

    print(f"✅ copy_to_source: {config.get('copy_to_source', False)}")
    print(f"✅ enable_json_sidecar: {config.get('enable_json_sidecar', False)}")
    print(f"✅ source_folder: {config.get('source_folder', 'not set')}")

    return True


def find_latest_sidecar():
    """Find the most recent sidecar JSON file."""
    print("\n=== Searching for Recent Sidecar Files ===")

    output_dir = Path("04_output")
    if not output_dir.exists():
        print("❌ Output directory not found")
        return None

    # Find all *_blocks.json files
    sidecar_files = list(output_dir.rglob("*_blocks.json"))

    if not sidecar_files:
        print("⚠️  No sidecar files found yet")
        print("   Run the watcher to process test files first")
        return None

    # Get the most recent one
    latest = max(sidecar_files, key=lambda p: p.stat().st_mtime)
    print(f"✅ Found: {latest}")

    return latest


def verify_sidecar_structure(sidecar_path):
    """Verify the sidecar JSON has enhanced origin tracking."""
    print("\n=== Verifying Sidecar Structure ===")

    with open(sidecar_path) as f:
        sidecar = json.load(f)

    # Check for enhanced origin object
    if "origin" in sidecar:
        print("✅ Enhanced 'origin' object found")

        origin = sidecar["origin"]
        required_fields = [
            "source_path",
            "source_directory",
            "source_filename",
            "archive_path",
            "received_at",
            "file_size",
            "original_size"
        ]

        missing = []
        for field in required_fields:
            if field in origin:
                print(f"   ✅ {field}: {origin[field]}")
            else:
                print(f"   ❌ {field}: MISSING")
                missing.append(field)

        if missing:
            print(f"\n⚠️  Missing fields: {', '.join(missing)}")
            return False
        else:
            print("\n✅ All origin fields present")
            return True
    else:
        print("❌ Enhanced 'origin' object NOT FOUND")
        print("   Sidecar only has basic metadata")
        return False


def find_latest_transcript():
    """Find the most recent transcript file."""
    print("\n=== Searching for Recent Transcript Files ===")

    output_dir = Path("04_output")
    if not output_dir.exists():
        return None

    # Find all transcript files
    transcripts = list(output_dir.rglob("*_transcript.md"))
    transcripts.extend(output_dir.rglob("*_transcript.txt"))

    if not transcripts:
        print("⚠️  No transcript files found yet")
        return None

    # Get the most recent one
    latest = max(transcripts, key=lambda p: p.stat().st_mtime)
    print(f"✅ Found: {latest}")

    return latest


def verify_front_matter(transcript_path):
    """Verify the transcript has enhanced front matter."""
    print("\n=== Verifying Transcript Front Matter ===")

    with open(transcript_path, encoding="utf-8") as f:
        content = f.read(2000)  # Read first 2000 chars

    # Check for enhanced fields
    required_phrases = [
        "Source Path:",
        "Archive Location:",
        "Output Folder:",
        "Original Size:",
        "Department:"
    ]

    found = []
    missing = []

    for phrase in required_phrases:
        if phrase in content:
            print(f"   ✅ {phrase} found")
            found.append(phrase)
        else:
            print(f"   ❌ {phrase} NOT FOUND")
            missing.append(phrase)

    if missing:
        print(f"\n⚠️  Missing front matter fields: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All front matter fields present")
        return True


def check_source_folder():
    """Check if sidecar files are copied to source folder."""
    print("\n=== Checking Source Folder Write-Back ===")

    source_dir = Path("source")
    if not source_dir.exists():
        print("⚠️  Source folder doesn't exist yet")
        print("   It will be created when files are processed")
        return None

    # Look for sidecar JSON files in source
    sidecar_files = list(source_dir.glob("*_blocks.json"))

    if sidecar_files:
        print(f"✅ Found {len(sidecar_files)} sidecar file(s) in source folder:")
        for sf in sidecar_files[:5]:  # Show first 5
            print(f"   - {sf.name}")
        return True
    else:
        print("⚠️  No sidecar files in source folder yet")
        print("   Process test files to verify write-back")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Origin Tracking & Write-Back Enhancement Verification")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run checks
    results = {
        "config": check_config(),
    }

    # Check for processed files
    sidecar = find_latest_sidecar()
    if sidecar:
        results["sidecar_structure"] = verify_sidecar_structure(sidecar)
    else:
        results["sidecar_structure"] = None

    transcript = find_latest_transcript()
    if transcript:
        results["front_matter"] = verify_front_matter(transcript)
    else:
        results["front_matter"] = None

    results["source_writeback"] = check_source_folder()

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for check, result in results.items():
        if result is True:
            print(f"✅ {check}: PASS")
        elif result is False:
            print(f"❌ {check}: FAIL")
        else:
            print(f"⚠️  {check}: NOT YET TESTABLE")

    # Instructions
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)

    if None in results.values():
        print("\n📝 To complete verification:")
        print("   1. Copy test files to 02_data/:")
        print("      - test_origin_tracking.md")
        print("      - test_origin_tracking.py")
        print("   2. Run the watcher: python watcher_splitter.py")
        print("   3. Run this verification script again")
    else:
        all_passed = all(v for v in results.values() if v is not None)
        if all_passed:
            print("\n🎉 All enhancements verified successfully!")
        else:
            print("\n⚠️  Some enhancements need attention (see failures above)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
