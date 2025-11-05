"""Verify all chunks from folders were processed into KB"""
from pathlib import Path
from collections import defaultdict
from rag_integration import ChromaRAG
import json

print("=" * 70)
print("Chunk Completeness Verification Report")
print("=" * 70)

# Check output directory
output_dir = Path("04_output")
folders = [f for f in output_dir.iterdir() if f.is_dir()]

print(f"\n[1] Scanning folders in {output_dir}...")

# Count chunks per folder
folder_chunk_counts = {}
folder_chunk_files = defaultdict(list)
total_chunks_in_files = 0
folders_with_chunks = 0
empty_folders = []

for folder in folders:
    chunks = list(folder.glob("*_chunk*.txt"))
    chunk_count = len(chunks)
    
    if chunk_count > 0:
        folders_with_chunks += 1
        folder_chunk_counts[folder.name] = chunk_count
        folder_chunk_files[folder.name] = [f.name for f in chunks]
        total_chunks_in_files += chunk_count
    else:
        empty_folders.append(folder.name)

print(f"  Total folders: {len(folders)}")
print(f"  Folders with chunks: {folders_with_chunks}")
print(f"  Empty folders: {len(empty_folders)}")
print(f"  Total chunk files found: {total_chunks_in_files}")

# Check ChromaDB
print(f"\n[2] Checking ChromaDB knowledge base...")
try:
    rag = ChromaRAG()
    kb_count = rag.collection.count()
    
    # Get all chunk IDs from KB
    print(f"  Retrieving all chunk IDs from KB...")
    all_kb_data = rag.collection.get()
    kb_ids = set(all_kb_data["ids"])
    
    print(f"  Chunks in KB: {kb_count}")
    print(f"  Unique IDs in KB: {len(kb_ids)}")
    
    # Compare counts
    print(f"\n[3] Comparison:")
    print(f"  Chunks in files: {total_chunks_in_files}")
    print(f"  Chunks in KB: {kb_count}")
    difference = total_chunks_in_files - kb_count
    print(f"  Difference: {difference}")
    
    if kb_count == total_chunks_in_files:
        print(f"  [OK] Counts match perfectly!")
    elif kb_count < total_chunks_in_files:
        print(f"  [WARNING] KB has {difference} fewer chunks than files")
    else:
        print(f"  [INFO] KB has {abs(difference)} more chunks than files (may include duplicates)")
    
    # Check folder-by-folder (sample)
    print(f"\n[4] Folder-by-folder breakdown (sample of first 20):")
    for i, (folder_name, chunk_count) in enumerate(list(folder_chunk_counts.items())[:20]):
        # Try to match folder names to KB metadata
        matching_ids = []
        for metadata, chunk_id in zip(all_kb_data.get("metadatas", []), all_kb_data["ids"]):
            source_folder = metadata.get("source_folder", "")
            if source_folder == folder_name:
                matching_ids.append(chunk_id)
        
        status = "OK" if len(matching_ids) == chunk_count else "CHECK"
        print(f"  {folder_name[:50]:50} Files: {chunk_count:4} | KB: {len(matching_ids):4} | {status}")
    
    if len(folder_chunk_counts) > 20:
        print(f"  ... and {len(folder_chunk_counts) - 20} more folders")
    
    # Summary statistics
    print(f"\n[5] Summary Statistics:")
    
    # Folders with perfect match
    folders_verified = 0
    folders_mismatch = []
    
    for folder_name, chunk_count in folder_chunk_counts.items():
        matching_ids = []
        for metadata, chunk_id in zip(all_kb_data.get("metadatas", []), all_kb_data["ids"]):
            source_folder = metadata.get("source_folder", "")
            if source_folder == folder_name:
                matching_ids.append(chunk_id)
        
        if len(matching_ids) == chunk_count:
            folders_verified += 1
        else:
            folders_mismatch.append((folder_name, chunk_count, len(matching_ids)))
    
    print(f"  Folders with matching counts: {folders_verified}/{folders_with_chunks}")
    print(f"  Folders with mismatches: {len(folders_mismatch)}")
    
    if folders_mismatch:
        print(f"\n  Folders needing attention:")
        for folder_name, file_count, kb_count in folders_mismatch[:10]:
            diff = file_count - kb_count
            print(f"    {folder_name[:50]:50} Files: {file_count} | KB: {kb_count} | Diff: {diff:+d}")
        if len(folders_mismatch) > 10:
            print(f"    ... and {len(folders_mismatch) - 10} more")
    
    # Overall verdict
    print(f"\n[6] Overall Verification:")
    if kb_count == total_chunks_in_files and folders_verified == folders_with_chunks:
        print(f"  [SUCCESS] All chunks verified! All {total_chunks_in_files} chunks from {folders_with_chunks} folders are in KB.")
    elif kb_count == total_chunks_in_files:
        print(f"  [PARTIAL] Total count matches, but some folders have mismatches. Check folder breakdown above.")
    else:
        print(f"  [ISSUE] Count mismatch detected. Total difference: {difference}")
        print(f"          Recommended: Review folder breakdown and re-run backfill if needed.")
    
except Exception as e:
    print(f"  [ERROR] Failed to check KB: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

