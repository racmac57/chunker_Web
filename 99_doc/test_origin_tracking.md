# Origin Tracking Test Document

**Date:** 2025-10-30
**Purpose:** Test enhanced origin tracking and write-back functionality
**Author:** R. A. Carucci

## Overview

This document is designed to test the three key enhancements to the chunker system:

### Enhancement A: Enhanced Sidecar Metadata
The JSON sidecar file should now include:
- Full source path (absolute)
- Source directory
- Archive path
- File size and timestamps
- Original size vs processed size

### Enhancement B: Better Front Matter
The transcript markdown file should include:
- Source path (absolute)
- Archive location
- Output folder path
- Original file size
- Department information

### Enhancement C: Sidecar Write-Back
The system should copy:
- Individual chunk files (if enabled)
- Transcript file (if enabled)
- **JSON sidecar metadata** (new!)

## Test Data

This document contains some test content to ensure proper chunking.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Expected Results

After processing, you should find:

1. **Output Folder**: `04_output/2025_10_30_XX_XX_XX_test_origin_tracking/`
   - Chunk files: `test_origin_tracking_chunk1.txt`, etc.
   - Transcript: `test_origin_tracking_transcript.md`
   - Sidecar: `test_origin_tracking_blocks.json`

2. **Archive Folder**: `03_archive/admin/test_origin_tracking.md`
   - Original file moved here after processing

3. **Source Folder**: `source/`
   - Chunk files (if copy_chunks_only: true)
   - Transcript file (if copy_transcript_only: true)
   - **Sidecar JSON** (if copy_sidecar_to_source: true)

## Verification Steps

1. Check sidecar JSON for enhanced origin metadata
2. Check transcript front matter for complete origin information
3. Check source folder for sidecar JSON file
4. Verify all paths are absolute and correct

---

**End of Test Document**
