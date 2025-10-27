#!/usr/bin/env python3
"""
Simple script to process the specific file
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def simple_process_file():
    """Process the specific file using basic chunking"""
    
    # File to process
    input_file = "02_data/2025_08_25_21_12_06_updated_chunker_cursor_file_processing_script_behavior.md"
    output_dir = "04_output"
    archive_dir = "03_archive"
    
    print(f"🔄 Processing: {input_file}")
    
    # Ensure directories exist
    Path(output_dir).mkdir(exist_ok=True)
    Path(archive_dir).mkdir(exist_ok=True)
    
    # Read the file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Read file: {len(content)} characters")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Simple chunking (split by headers)
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    
    for line in lines:
        if line.startswith('#') and current_chunk:
            # Save current chunk
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    # Add the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    print(f"📊 Created {len(chunks)} chunks")
    
    # Save chunks
    base_name = Path(input_file).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, chunk in enumerate(chunks, 1):
        chunk_file = f"{output_dir}/{base_name}_chunk_{i:03d}.txt"
        try:
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            print(f"✅ Saved chunk {i}: {chunk_file}")
        except Exception as e:
            print(f"❌ Error saving chunk {i}: {e}")
    
    # Create transcript
    transcript_file = f"{output_dir}/{base_name}_transcript.txt"
    try:
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"# Transcript: {base_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total chunks: {len(chunks)}\n\n")
            
            for i, chunk in enumerate(chunks, 1):
                f.write(f"## Chunk {i}\n")
                f.write(chunk)
                f.write("\n\n" + "="*50 + "\n\n")
        
        print(f"✅ Created transcript: {transcript_file}")
    except Exception as e:
        print(f"❌ Error creating transcript: {e}")
    
    # Move original to archive
    try:
        archive_file = f"{archive_dir}/{Path(input_file).name}"
        shutil.move(input_file, archive_file)
        print(f"✅ Moved original to archive: {archive_file}")
    except Exception as e:
        print(f"❌ Error moving to archive: {e}")
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 Check {output_dir} for results")

if __name__ == "__main__":
    simple_process_file()
