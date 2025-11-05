"""
Backfill Knowledge Base Script
Adds all existing processed files (chunks) to the ChromaDB knowledge base
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/backfill_kb.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from config.json"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    import re
    from collections import Counter
    
    try:
        # Import NLTK stopwords
        import nltk
        from nltk.corpus import stopwords
        
        # Download stopwords if not available
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            stop_words = set(stopwords.words('english'))
            
    except ImportError:
        # Fallback if NLTK not available
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
    
    # Remove special characters and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Return most common keywords
    counter = Counter(keywords)
    return [word for word, _ in counter.most_common(max_keywords)]


def parse_chunk_filename(filename: str) -> Dict[str, Any]:
    """
    Parse chunk filename to extract metadata
    
    Format: YYYY_MM_DD_HH_MM_SS_{base_name}_chunk{N}.txt
    
    Returns:
        Dictionary with parsed metadata
    """
    # Extract chunk number
    chunk_match = re.search(r'_chunk(\d+)', filename)
    chunk_index = int(chunk_match.group(1)) if chunk_match else 0
    
    # Extract timestamp
    timestamp_match = re.search(r'(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})', filename)
    timestamp_str = timestamp_match.group(1) if timestamp_match else datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    
    # Extract base name (remove timestamp and chunk info)
    base_name = filename.replace(timestamp_str, "").replace(f"_chunk{chunk_index}", "").replace(".txt", "").strip("_")
    
    return {
        "chunk_index": chunk_index,
        "timestamp": timestamp_str,
        "base_name": base_name,
        "file_name": filename
    }


def find_chunk_files(output_dir: Path) -> List[Dict[str, Any]]:
    """
    Find all chunk files in the output directory
    
    Args:
        output_dir: Path to output directory
        
    Returns:
        List of dictionaries with chunk file info
    """
    chunk_files = []
    
    logger.info(f"Scanning output directory: {output_dir}")
    
    # Walk through all subdirectories
    for folder_path in output_dir.iterdir():
        if not folder_path.is_dir():
            continue
            
        # Look for chunk files in this folder
        for file_path in folder_path.glob("*_chunk*.txt"):
            try:
                file_info = parse_chunk_filename(file_path.name)
                file_info.update({
                    "file_path": file_path,
                    "folder_name": folder_path.name,
                    "file_size": file_path.stat().st_size
                })
                chunk_files.append(file_info)
            except Exception as e:
                logger.warning(f"Error parsing chunk file {file_path.name}: {e}")
                continue
    
    logger.info(f"Found {len(chunk_files)} chunk files")
    return chunk_files


def read_chunk_content(chunk_file: Path) -> Optional[str]:
    """
    Read chunk file content
    
    Args:
        chunk_file: Path to chunk file
        
    Returns:
        File content or None if error
    """
    try:
        with open(chunk_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().strip()
            if len(content) < 10:  # Skip very short chunks
                return None
            return content
    except Exception as e:
        logger.error(f"Failed to read chunk file {chunk_file}: {e}")
        return None


def get_department_from_folder(folder_name: str) -> str:
    """
    Determine department from folder name
    
    Args:
        folder_name: Name of the folder
        
    Returns:
        Department name
    """
    # Check for department indicators
    folder_lower = folder_name.lower()
    
    if any(keyword in folder_lower for keyword in ['admin', 'administrative', 'general']):
        return "admin"
    elif any(keyword in folder_lower for keyword in ['police', 'cad', 'rms', 'incident', 'arrest']):
        return "police"
    elif any(keyword in folder_lower for keyword in ['legal', 'court', 'summons']):
        return "legal"
    else:
        return "admin"  # Default


def backfill_to_knowledge_base(chunk_files: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add all chunks to ChromaDB knowledge base
    
    Args:
        chunk_files: List of chunk file dictionaries
        config: Configuration dictionary
        
    Returns:
        Statistics dictionary
    """
    if not config.get("rag_enabled", False):
        logger.error("RAG is not enabled in config.json! Set 'rag_enabled': true")
        return {"status": "error", "message": "RAG not enabled"}
    
    try:
        from rag_integration import ChromaRAG
    except ImportError:
        logger.error("Failed to import ChromaRAG. Make sure rag_integration.py exists.")
        return {"status": "error", "message": "Import failed"}
    
    # Initialize ChromaDB
    chroma_persist_dir = config.get("chroma_persist_dir", "./chroma_db")
    chroma_rag = ChromaRAG(persist_directory=chroma_persist_dir)
    
    logger.info(f"Initialized ChromaDB. Existing chunks: {chroma_rag.collection.count()}")
    
    stats = {
        "total_chunks": len(chunk_files),
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "errors": []
    }
    
    # Process each chunk file
    for i, chunk_info in enumerate(chunk_files, 1):
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{len(chunk_files)} chunks processed ({stats['successful']} successful)")
        
        chunk_file = chunk_info["file_path"]
        
        # Read chunk content
        chunk_text = read_chunk_content(chunk_file)
        if not chunk_text:
            stats["skipped"] += 1
            continue
        
        # Prepare metadata
        department = get_department_from_folder(chunk_info["folder_name"])
        keywords = extract_keywords(chunk_text)
        
        # Convert timestamp to ISO format
        timestamp_parts = chunk_info["timestamp"].split("_")
        if len(timestamp_parts) == 6:
            try:
                timestamp_iso = f"{timestamp_parts[0]}-{timestamp_parts[1]}-{timestamp_parts[2]}T{timestamp_parts[3]}:{timestamp_parts[4]}:{timestamp_parts[5]}"
            except:
                timestamp_iso = datetime.now().isoformat()
        else:
            timestamp_iso = datetime.now().isoformat()
        
        chunk_metadata = {
            "file_name": chunk_info["base_name"],
            "file_type": ".txt",
            "chunk_index": chunk_info["chunk_index"],
            "timestamp": timestamp_iso,
            "department": department,
            "keywords": keywords,
            "file_size": chunk_info["file_size"],
            "processing_time": 0,
            "source_folder": chunk_info["folder_name"]
        }
        
        # Add to ChromaDB
        try:
            chunk_id = chroma_rag.add_chunk(chunk_text, chunk_metadata)
            stats["successful"] += 1
            if i % 50 == 0:
                logger.debug(f"Added chunk {i}: {chunk_id}")
        except Exception as e:
            stats["failed"] += 1
            error_msg = f"Failed to add chunk {chunk_file.name}: {e}"
            stats["errors"].append(error_msg)
            logger.error(error_msg)
    
    # Final statistics
    final_count = chroma_rag.collection.count()
    logger.info(f"\n{'='*60}")
    logger.info(f"Backfill Complete!")
    logger.info(f"{'='*60}")
    logger.info(f"Total chunks processed: {stats['total_chunks']}")
    logger.info(f"  ✅ Successful: {stats['successful']}")
    logger.info(f"  ❌ Failed: {stats['failed']}")
    logger.info(f"  ⏭️  Skipped: {stats['skipped']}")
    logger.info(f"Total chunks in KB: {final_count}")
    logger.info(f"{'='*60}")
    
    return {
        "status": "success",
        "stats": stats,
        "final_kb_count": final_count
    }


def main():
    """Main function"""
    logger.info("="*60)
    logger.info("Knowledge Base Backfill Script")
    logger.info("="*60)
    
    # Load configuration
    config = load_config()
    
    # Check if RAG is enabled
    if not config.get("rag_enabled", False):
        logger.warning("⚠️  RAG is not enabled in config.json")
        response = input("Do you want to enable RAG now? (y/n): ").strip().lower()
        if response == 'y':
            config["rag_enabled"] = True
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            logger.info("✅ RAG enabled in config.json")
        else:
            logger.error("Cannot proceed without RAG enabled. Exiting.")
            return
    
    # Get output directory
    output_dir = Path(config.get("output_dir", "04_output"))
    if not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}")
        return
    
    # Find all chunk files
    logger.info("Scanning for chunk files...")
    chunk_files = find_chunk_files(output_dir)
    
    if not chunk_files:
        logger.warning("No chunk files found!")
        return
    
    # Confirm before proceeding
    logger.info(f"\nFound {len(chunk_files)} chunk files to add to knowledge base")
    response = input("Proceed with backfill? (y/n): ").strip().lower()
    if response != 'y':
        logger.info("Backfill cancelled by user")
        return
    
    # Perform backfill
    result = backfill_to_knowledge_base(chunk_files, config)
    
    if result.get("status") == "success":
        logger.info("✅ Backfill completed successfully!")
        logger.info(f"Knowledge base now contains {result['final_kb_count']} chunks")
    else:
        logger.error(f"❌ Backfill failed: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    main()

