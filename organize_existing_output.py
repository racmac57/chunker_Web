#!/usr/bin/env python3
"""
Script to organize existing output files into proper folder structure
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import re

def organize_existing_output():
    """Organize existing output files into proper folder structure"""
    
    output_dir = "04_output"
    
    if not Path(output_dir).exists():
        print(f"❌ Output directory {output_dir} does not exist!")
        return
    
    print(f"🔄 Organizing existing files in {output_dir}...")
    
    # Get all files in output directory
    files = list(Path(output_dir).glob("*"))
    
    # Group files by base name (before _chunk_ or _transcript)
    file_groups = {}
    
    for file_path in files:
        if file_path.is_file():
            filename = file_path.name
            
            # Extract base name (remove _chunk_XXX or _transcript)
            if "_chunk_" in filename:
                base_name = filename.split("_chunk_")[0]
                file_type = "chunk"
            elif "_transcript" in filename:
                base_name = filename.split("_transcript")[0]
                file_type = "transcript"
            else:
                # Skip files that don't match our pattern
                continue
            
            if base_name not in file_groups:
                file_groups[base_name] = {"chunks": [], "transcripts": []}
            
            if file_type == "chunk":
                file_groups[base_name]["chunks"].append(file_path)
            else:
                file_groups[base_name]["transcripts"].append(file_path)
    
    print(f"📊 Found {len(file_groups)} file groups to organize")
    
    # Process each group
    for base_name, files in file_groups.items():
        print(f"\n🔄 Processing group: {base_name}")
        
        # Create project folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_folder = f"{output_dir}/{base_name}_{timestamp}"
        chunks_folder = f"{project_folder}/chunks"
        transcripts_folder = f"{project_folder}/transcripts"
        
        Path(project_folder).mkdir(exist_ok=True)
        Path(chunks_folder).mkdir(exist_ok=True)
        Path(transcripts_folder).mkdir(exist_ok=True)
        
        print(f"📁 Created project folder: {project_folder}")
        
        # Move chunks
        for chunk_file in files["chunks"]:
            try:
                # Extract chunk number
                match = re.search(r'_chunk_(\d+)\.', chunk_file.name)
                if match:
                    chunk_num = match.group(1)
                    new_name = f"chunk_{chunk_num.zfill(3)}.txt"
                    new_path = Path(chunks_folder) / new_name
                    shutil.move(str(chunk_file), str(new_path))
                    print(f"✅ Moved chunk: {new_name}")
            except Exception as e:
                print(f"❌ Error moving chunk {chunk_file.name}: {e}")
        
        # Move transcripts
        for transcript_file in files["transcripts"]:
            try:
                new_name = "complete_transcript.txt"
                new_path = Path(transcripts_folder) / new_name
                shutil.move(str(transcript_file), str(new_path))
                print(f"✅ Moved transcript: {new_name}")
            except Exception as e:
                print(f"❌ Error moving transcript {transcript_file.name}: {e}")
        
        # Create project summary
        summary_file = f"{project_folder}/project_summary.json"
        try:
            summary = {
                "project_name": base_name,
                "timestamp": timestamp,
                "total_chunks": len(files["chunks"]),
                "total_transcripts": len(files["transcripts"]),
                "chunks_folder": chunks_folder,
                "transcript_folder": transcripts_folder,
                "organization_date": datetime.now().isoformat(),
                "original_files": {
                    "chunks": [f.name for f in files["chunks"]],
                    "transcripts": [f.name for f in files["transcripts"]]
                }
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Created project summary: {summary_file}")
        except Exception as e:
            print(f"❌ Error creating summary: {e}")
    
    print(f"\n🎉 Organization complete!")
    print(f"📁 Check {output_dir} for organized project folders")

if __name__ == "__main__":
    organize_existing_output()
