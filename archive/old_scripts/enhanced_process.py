#!/usr/bin/env python3
"""
Enhanced script to process files with organized folder structure
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def enhanced_process_file():
    """Process files with organized folder structure"""
    
    # File to process
    input_file = "02_data/2025_08_25_21_12_06_updated_chunker_cursor_file_processing_script_behavior.md"
    output_dir = "04_output"
    archive_dir = "03_archive"
    
    print(f"🔄 Processing: {input_file}")
    
    # Ensure base directories exist
    Path(output_dir).mkdir(exist_ok=True)
    Path(archive_dir).mkdir(exist_ok=True)
    
    # Create organized folder structure
    base_name = Path(input_file).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create project folder
    project_folder = f"{output_dir}/{base_name}_{timestamp}"
    chunks_folder = f"{project_folder}/chunks"
    transcripts_folder = f"{project_folder}/transcripts"
    
    Path(project_folder).mkdir(exist_ok=True)
    Path(chunks_folder).mkdir(exist_ok=True)
    Path(transcripts_folder).mkdir(exist_ok=True)
    
    print(f"📁 Created project folder: {project_folder}")
    
    # Read the file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Read file: {len(content)} characters")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Enhanced chunking (split by headers with better logic)
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    
    for line in lines:
        # Start new chunk on major headers (# or ##)
        if (line.startswith('# ') or line.startswith('## ')) and current_chunk:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    # Add the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    print(f"📊 Created {len(chunks)} chunks")
    
    # Save chunks in organized folder
    for i, chunk in enumerate(chunks, 1):
        chunk_file = f"{chunks_folder}/chunk_{i:03d}.txt"
        try:
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            print(f"✅ Saved chunk {i}: {chunk_file}")
        except Exception as e:
            print(f"❌ Error saving chunk {i}: {e}")
    
    # Create enhanced transcript
    transcript_file = f"{transcripts_folder}/complete_transcript.txt"
    try:
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"# Complete Transcript: {base_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total chunks: {len(chunks)}\n")
            f.write(f"Original file: {input_file}\n")
            f.write(f"Project folder: {project_folder}\n\n")
            f.write("="*80 + "\n\n")
            
            for i, chunk in enumerate(chunks, 1):
                f.write(f"## Chunk {i:03d}\n")
                f.write(f"File: {chunks_folder}/chunk_{i:03d}.txt\n")
                f.write(f"Length: {len(chunk)} characters\n\n")
                f.write(chunk)
                f.write("\n\n" + "="*80 + "\n\n")
        
        print(f"✅ Created transcript: {transcript_file}")
    except Exception as e:
        print(f"❌ Error creating transcript: {e}")
    
    # Create project summary
    summary_file = f"{project_folder}/project_summary.json"
    try:
        summary = {
            "project_name": base_name,
            "timestamp": timestamp,
            "original_file": input_file,
            "total_chunks": len(chunks),
            "total_characters": len(content),
            "chunks_folder": chunks_folder,
            "transcript_file": transcript_file,
            "processing_date": datetime.now().isoformat(),
            "chunk_details": []
        }
        
        for i, chunk in enumerate(chunks, 1):
            summary["chunk_details"].append({
                "chunk_number": i,
                "file_name": f"chunk_{i:03d}.txt",
                "character_count": len(chunk),
                "line_count": len(chunk.split('\n'))
            })
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Created project summary: {summary_file}")
    except Exception as e:
        print(f"❌ Error creating summary: {e}")
    
    # Move original to archive
    try:
        archive_file = f"{archive_dir}/{Path(input_file).name}"
        shutil.move(input_file, archive_file)
        print(f"✅ Moved original to archive: {archive_file}")
    except Exception as e:
        print(f"❌ Error moving to archive: {e}")
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 Project folder: {project_folder}")
    print(f"📄 Chunks: {chunks_folder}")
    print(f"📋 Transcript: {transcript_file}")
    print(f"📊 Summary: {summary_file}")

if __name__ == "__main__":
    enhanced_process_file()
