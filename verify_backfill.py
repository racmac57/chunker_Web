"""Verify backfill completeness"""
from pathlib import Path
from collections import defaultdict
from rag_integration import ChromaRAG

# Check output directory
output_dir = Path("04_output")
folders = [f for f in output_dir.iterdir() if f.is_dir()]

print("=" * 60)
print("Backfill Verification Report")
print("=" * 60)

# Count chunks per folder
folder_chunks = defaultdict(list)
total_chunks_in_files = 0

for folder in folders:
    chunks = list(folder.glob("*_chunk*.txt"))
    if chunks:
        folder_chunks[folder.name] = chunks
        total_chunks_in_files += len(chunks)

print(f"\nFolder Statistics:")
print(f"  Total folders: {len(folders)}")
print(f"  Folders with chunks: {len(folder_chunks)}")
print(f"  Folders without chunks: {len(folders) - len(folder_chunks)}")
print(f"  Total chunk files found: {total_chunks_in_files}")

# Check ChromaDB
try:
    rag = ChromaRAG()
    kb_count = rag.collection.count()
    print(f"\nKnowledge Base Statistics:")
    print(f"  Chunks in KB: {kb_count}")
    print(f"  Chunks found in files: {total_chunks_in_files}")
    print(f"  Difference: {total_chunks_in_files - kb_count}")
    
    if kb_count == total_chunks_in_files:
        print(f"  [OK] All chunks are in the knowledge base!")
    elif kb_count < total_chunks_in_files:
        print(f"  [WARNING] {total_chunks_in_files - kb_count} chunks are missing from KB")
    else:
        print(f"  [INFO] KB has {kb_count - total_chunks_in_files} more chunks than files")
except Exception as e:
    print(f"  [ERROR] Error checking KB: {e}")

# Sample folders
print(f"\nSample folders with chunks (first 10):")
for i, (folder_name, chunks) in enumerate(list(folder_chunks.items())[:10]):
    print(f"  {folder_name}: {len(chunks)} chunks")

print("\n" + "=" * 60)

