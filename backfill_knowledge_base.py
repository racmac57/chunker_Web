"""
Backfill Knowledge Base Script - Optimized Version
Adds all existing processed files (chunks) to the ChromaDB knowledge base
with batch operations, retries, performance tracking, and HNSW optimization.

Version: 2.1.6
Optimized for: 3,200+ chunks (updated based on actual data)
Features:
- Multiprocessing with separate ChromaDB connections per process
- Parallel file reading and metadata extraction
- Batch size optimization (500-1000 chunks)
- Duplicate detection before insertion
- CPU and memory monitoring
- Empty folder logging
- Count discrepancy alerts
"""

import hashlib
import os
import sys
import json
import logging
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union, Iterable
import re
import multiprocessing
from multiprocessing import Pool, cpu_count
from functools import partial

try:
    from incremental_updates import VersionTracker
except ImportError:
    VersionTracker = None  # type: ignore

# Setup logging first (before other imports that might use logger)
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/backfill_kb.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Performance monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - memory tracking disabled")

# Progress tracking
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    logger.warning("tqdm not available - progress bars disabled")

try:
    from deduplication import DeduplicationManager
except ImportError:
    DeduplicationManager = None  # type: ignore

from metadata_enrichment import SIDECAR_SUFFIX, MANIFEST_ENRICHMENT_KEY
from incremental_updates import VersionTracker, build_chunk_id, normalize_timestamp

# NLTK initialization (outside loop for performance)
try:
    import nltk
    from nltk.corpus import stopwords
    try:
        NLTK_STOPWORDS = set(stopwords.words('english'))
    except LookupError:
        nltk.download('stopwords', quiet=True)
        NLTK_STOPWORDS = set(stopwords.words('english'))
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    NLTK_STOPWORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json
    
    Returns:
        Configuration dictionary
    """
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}", exc_info=True)
        sys.exit(1)


def compute_content_hash(text: str) -> str:
    normalized = (text or "").strip().lower()
    normalized = " ".join(normalized.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis
    Optimized: NLTK stopwords loaded once at module level
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    from collections import Counter
    
    if not text or len(text.strip()) == 0:
        return []
    
    # Remove special characters and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words (using pre-loaded set)
    keywords = [word for word in words if word not in NLTK_STOPWORDS and len(word) > 2]
    
    # Return most common keywords
    counter = Counter(keywords)
    return [word for word, _ in counter.most_common(max_keywords)]


def dedupe_list(values: Optional[Iterable[Any]]) -> List[str]:
    """
    Deduplicate an iterable while preserving order and returning strings.
    """
    if not values:
        return []

    seen = set()
    ordered: List[str] = []
    for value in values:
        if value is None:
            continue
        value_str = str(value).strip()
        if not value_str or value_str in seen:
            continue
        seen.add(value_str)
        ordered.append(value_str)
    return ordered


def load_json_safely(path: Path) -> Dict[str, Any]:
    """
    Load JSON data from disk, returning an empty dict on failure.
    """
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load JSON from %s: %s", path, exc)
        return {}


def parse_chunk_filename(filename: str) -> Dict[str, Any]:
    """
    Parse chunk filename to extract metadata using robust regex
    
    Handles formats:
    - YYYY_MM_DD_HH_MM_SS_{base_name}_chunk{N}.txt
    - Variations with different separators
    
    Args:
        filename: Chunk filename to parse
        
    Returns:
        Dictionary with parsed metadata
    """
    # Extract chunk number (robust regex)
    chunk_match = re.search(r'_chunk(\d+)', filename)
    chunk_index = int(chunk_match.group(1)) if chunk_match else 0
    
    # Extract timestamp (robust regex for YYYY_MM_DD_HH_MM_SS)
    timestamp_match = re.search(r'(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})', filename)
    timestamp_str = timestamp_match.group(1) if timestamp_match else datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    
    # Extract base name (remove timestamp and chunk info using regex)
    base_name = re.sub(
        r'_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}_chunk\d+(?:_[^.]+)?\.txt$',
        "",
        filename,
    ).strip("_")
    
    # Fallback if regex didn't match
    if not base_name or base_name == filename:
        base_name = filename.replace(timestamp_str, "").replace(f"_chunk{chunk_index}", "").replace(".txt", "").strip("_")
    
    return {
        "chunk_index": chunk_index,
        "timestamp": timestamp_str,
        "base_name": base_name,
        "file_name": filename
    }


def find_chunk_files(output_dir: Path, expected_count: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Find all chunk files in the output directory with logging and validation
    
    Args:
        output_dir: Path to output directory
        expected_count: Expected number of chunks (for discrepancy alert)
        
    Returns:
        Tuple of (chunk_files list, statistics dictionary)
    """
    chunk_files: List[Dict[str, Any]] = []
    empty_folders: List[str] = []
    folders_with_chunks: List[str] = []
    
    logger.info(f"Scanning output directory: {output_dir}")
    
    # Walk through all subdirectories
    for folder_path in output_dir.iterdir():
        if not folder_path.is_dir():
            continue
        
        folder_chunks = list(folder_path.glob("*_chunk*.txt"))

        if not folder_chunks:
            empty_folders.append(folder_path.name)
            logger.debug(f"Empty folder (no chunks): {folder_path.name}")
            continue

        folders_with_chunks.append(folder_path.name)

        sidecar_path = next((p for p in folder_path.glob(f"*{SIDECAR_SUFFIX}")), None)
        sidecar_data: Dict[str, Any] = (
            load_json_safely(sidecar_path) if sidecar_path and sidecar_path.exists() else {}
        )

        manifest_path_candidate = next((p for p in folder_path.glob("*.origin.json")), None)
        manifest_reference: Optional[str] = None
        manifest_data: Dict[str, Any] = {}

        if manifest_path_candidate and manifest_path_candidate.exists():
            manifest_reference = str(manifest_path_candidate)
            manifest_data = load_json_safely(manifest_path_candidate)
        else:
            manifest_hint = sidecar_data.get("manifest_path")
            if isinstance(manifest_hint, str):
                manifest_reference = manifest_hint
                hint_path = Path(manifest_hint)
                if hint_path.exists():
                    manifest_data = load_json_safely(hint_path)

        manifest_enrichment = manifest_data.get(MANIFEST_ENRICHMENT_KEY, {})
        if not isinstance(manifest_enrichment, dict):
            manifest_enrichment = {}

        manifest_metadata = manifest_enrichment.get("metadata", {})
        if not isinstance(manifest_metadata, dict):
            manifest_metadata = {}

        sidecar_metadata = sidecar_data.get("metadata", {})
        if not isinstance(sidecar_metadata, dict):
            sidecar_metadata = {}

        merged_metadata = {**manifest_metadata, **sidecar_metadata}
        enrichment_version = (
            merged_metadata.get("enrichment_version")
            or manifest_enrichment.get("enrichment_version")
            or sidecar_data.get("enrichment_version")
        )
        if enrichment_version:
            merged_metadata["enrichment_version"] = enrichment_version

        sidecar_tags = sidecar_data.get("tags", [])
        if not isinstance(sidecar_tags, list):
            sidecar_tags = []
        manifest_tags = manifest_data.get("tags", [])
        if not isinstance(manifest_tags, list):
            manifest_tags = []
        combined_tags = dedupe_list([*sidecar_tags, *manifest_tags])

        source_path_value = sidecar_data.get("source_path") or manifest_data.get("source_path")
        if isinstance(source_path_value, Path):
            source_path_value = str(source_path_value)
        elif source_path_value is not None:
            source_path_value = str(source_path_value)

        chunk_metadata_map: Dict[str, Dict[str, Any]] = {}
        sidecar_chunks = sidecar_data.get("chunks", [])
        if isinstance(sidecar_chunks, list):
            for entry in sidecar_chunks:
                if isinstance(entry, dict) and entry.get("file"):
                    chunk_metadata_map[entry["file"]] = entry

        merged_summaries: Dict[str, Any] = {}
        manifest_summaries = manifest_enrichment.get("summaries")
        if isinstance(manifest_summaries, dict):
            merged_summaries.update(manifest_summaries)
        sidecar_summaries = sidecar_data.get("summaries")
        if isinstance(sidecar_summaries, dict):
            merged_summaries.update(sidecar_summaries)

        # Look for chunk files in this folder
        for file_path in folder_chunks:
            try:
                file_info = parse_chunk_filename(file_path.name)

                per_chunk_meta = chunk_metadata_map.get(file_path.name, {})
                chunk_tags = dedupe_list(per_chunk_meta.get("tags"))
                if not chunk_tags:
                    chunk_tags = combined_tags

                chunk_key_terms = dedupe_list(
                    per_chunk_meta.get("key_terms")
                    or merged_metadata.get("key_terms")
                )

                per_chunk_metadata = dict(merged_metadata)
                if chunk_key_terms:
                    per_chunk_metadata["key_terms"] = chunk_key_terms

                chunk_id = per_chunk_meta.get("chunk_id")
                if not chunk_id:
                    chunk_id = build_chunk_id(
                        file_info["timestamp"],
                        file_info["base_name"],
                        file_info["chunk_index"],
                    )

                enriched_metadata = {
                    "file_tags": combined_tags,
                    "chunk_tags": chunk_tags,
                    "key_terms": chunk_key_terms,
                    "metadata": per_chunk_metadata,
                    "chunk_summary": per_chunk_meta.get("summary", ""),
                    "file_summary": merged_summaries.get("file_summary", ""),
                }
                if enrichment_version:
                    enriched_metadata["enrichment_version"] = enrichment_version
                if per_chunk_meta.get("char_length"):
                    enriched_metadata["char_length"] = per_chunk_meta["char_length"]
                if per_chunk_meta.get("byte_length"):
                    enriched_metadata["byte_length"] = per_chunk_meta["byte_length"]

                file_info.update({
                    "file_path": file_path,
                    "chunk_id": chunk_id,
                    "folder_name": folder_path.name,
                    "file_size": file_path.stat().st_size,
                    "file_tags": combined_tags,
                    "sidecar_path": str(sidecar_path) if sidecar_path else None,
                    "manifest_path": manifest_reference,
                    "source_path": source_path_value,
                    "enriched_metadata": enriched_metadata,
                })
                chunk_files.append(file_info)
            except Exception as e:
                logger.warning(f"Error parsing chunk file {file_path.name}: {e}", exc_info=True)
                continue
    
    # Statistics
    stats = {
        "total_folders": len(empty_folders) + len(folders_with_chunks),
        "folders_with_chunks": len(folders_with_chunks),
        "empty_folders": len(empty_folders),
        "total_chunks": len(chunk_files)
    }
    
    logger.info(f"Found {len(chunk_files)} chunk files in {len(folders_with_chunks)} folders")
    
    # Log empty folders if any
    if empty_folders:
        logger.info(f"Found {len(empty_folders)} empty folders (no chunk files)")
        if len(empty_folders) <= 20:  # Log all if 20 or fewer
            logger.debug(f"Empty folders: {', '.join(empty_folders[:20])}")
        else:
            logger.debug(f"Empty folders (first 20): {', '.join(empty_folders[:20])}...")
    
    # Alert on count discrepancy
    if expected_count is not None and len(chunk_files) != expected_count:
        discrepancy = abs(len(chunk_files) - expected_count)
        logger.warning(
            f"Count discrepancy detected! "
            f"Expected: {expected_count}, Found: {len(chunk_files)}, "
            f"Difference: {discrepancy} ({'+' if len(chunk_files) > expected_count else '-'}{discrepancy})"
        )
    
    return chunk_files, stats


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
        logger.error(f"Failed to read chunk file {chunk_file}: {e}", exc_info=True)
        return None


def process_chunk_file_parallel(chunk_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process a single chunk file in parallel (for multiprocessing)
    Includes file reading, keyword extraction, and metadata preparation
    
    Args:
        chunk_info: Dictionary with chunk file information
        
    Returns:
        Dictionary with processed chunk data (id, text, metadata) or None if failed
    """
    try:
        chunk_file = Path(chunk_info["file_path"])
        
        # Verify chunk file exists before processing
        if not chunk_file.exists():
            logger.warning(f"Chunk file does not exist: {chunk_file}")
            return None
        
        if not chunk_file.is_file():
            logger.warning(f"Path is not a file: {chunk_file}")
            return None
        
        # Read chunk content
        chunk_text = read_chunk_content(chunk_file)
        if not chunk_text:
            return None
        
        enriched_metadata = chunk_info.get("enriched_metadata", {}) or {}
        file_tags = enriched_metadata.get("file_tags") or chunk_info.get("file_tags") or []
        chunk_tags = enriched_metadata.get("chunk_tags") or file_tags
        key_terms = enriched_metadata.get("key_terms")
        if key_terms:
            key_terms = dedupe_list(key_terms)
        else:
            key_terms = extract_keywords(chunk_text)

        # Prepare metadata
        department = get_department_from_folder(chunk_info["folder_name"])
        source_path = chunk_info.get("source_path")
        timestamp_iso = normalize_timestamp(chunk_info["timestamp"])
        chunk_id = (
            chunk_info.get("expected_chunk_id")
            or chunk_info.get("chunk_id")
            or build_chunk_id(
                chunk_info["timestamp"],
                chunk_info["base_name"],
                chunk_info["chunk_index"],
            )
        )
        
        # Prepare ChromaDB metadata
        chroma_metadata = {
            "file_name": chunk_info["base_name"],
            "file_type": ".txt",
            "chunk_index": str(chunk_info["chunk_index"]),
            "timestamp": timestamp_iso,
            "department": department,
            "keywords": json.dumps(key_terms),
            "key_terms": json.dumps(key_terms),
            "file_size": str(chunk_info.get("file_size", 0)),
            "processing_time": "0",
            "source_folder": chunk_info.get("folder_name", ""),
            "content_hash": compute_content_hash(chunk_text),
        }

        if chunk_tags:
            chroma_metadata["tags"] = json.dumps(chunk_tags)
        if file_tags:
            chroma_metadata["file_tags"] = json.dumps(file_tags)

        metadata_payload = enriched_metadata.get("metadata")
        if isinstance(metadata_payload, dict):
            for meta_key, meta_value in metadata_payload.items():
                if meta_value is None:
                    continue
                if isinstance(meta_value, (list, dict)):
                    chroma_metadata[meta_key] = json.dumps(meta_value)
                else:
                    chroma_metadata[meta_key] = str(meta_value)

        if enriched_metadata.get("chunk_summary"):
            chroma_metadata["chunk_summary"] = enriched_metadata["chunk_summary"]
        if enriched_metadata.get("file_summary"):
            chroma_metadata.setdefault("file_summary", enriched_metadata["file_summary"])
        if enriched_metadata.get("enrichment_version"):
            chroma_metadata["enrichment_version"] = str(enriched_metadata["enrichment_version"])

        char_length = enriched_metadata.get("char_length") or len(chunk_text)
        chroma_metadata["char_length"] = str(char_length)

        byte_length = enriched_metadata.get("byte_length")
        if byte_length:
            chroma_metadata["byte_length"] = str(byte_length)

        manifest_path = chunk_info.get("manifest_path")
        if manifest_path:
            chroma_metadata["manifest_path"] = manifest_path
        sidecar_path = chunk_info.get("sidecar_path")
        if sidecar_path:
            chroma_metadata["sidecar_path"] = sidecar_path
        if source_path:
            chroma_metadata["source_path"] = source_path
        
        return {
            "id": chunk_id,
            "text": chunk_text,
            "metadata": chroma_metadata,
            "source_path": source_path,
        }
    except Exception as e:
        logger.error(f"Failed to process chunk {chunk_info.get('file_path', 'unknown')}: {e}", exc_info=True)
        return None


def insert_chunk_batch_parallel(batch_data: Tuple[List[str], List[Dict[str, Any]], List[str], str]) -> int:
    """
    Insert a batch of chunks into ChromaDB using separate connection per process
    This function is called by multiprocessing workers for parallel inserts
    
    Args:
        batch_data: Tuple of (texts, metadatas, ids, persist_directory)
        
    Returns:
        Number of chunks successfully inserted
    """
    texts, metadatas, ids, persist_directory = batch_data
    
    try:
        # Each process creates its own ChromaDB client (thread-safe)
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection(name="chunker_knowledge_base")
        
        # Verify chunks don't already exist before adding
        existing_ids = set()
        try:
            existing = collection.get(ids=ids)["ids"]
            existing_ids.update(existing)
        except Exception:
            pass  # If get fails, assume all are new
        
        if not existing_ids:
            # All chunks are new, insert all
            new_texts = texts
            new_metadatas = metadatas
            new_ids = ids
        else:
            # Filter to only new chunks
            new_ids = [id for id in ids if id not in existing_ids]
            if not new_ids:
                return 0  # All chunks already exist
            
            indices = [i for i, id in enumerate(ids) if id in new_ids]
            new_texts = [texts[i] for i in indices]
            new_metadatas = [metadatas[i] for i in indices]
        
        # Insert batch
        collection.add(
            documents=new_texts,
            metadatas=new_metadatas,
            ids=new_ids
        )
        
        return len(new_ids)
        
    except Exception as e:
        # Log error but don't raise (multiprocessing compatibility)
        import logging
        logging.error(f"Batch insert failed: {e}", exc_info=True)
        return 0


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


def add_with_retry(
    collection,
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    ids: List[str],
    retries: int = 3
) -> bool:
    """
    Add chunks to ChromaDB with retry logic
    
    Args:
        collection: ChromaDB collection object
        documents: List of document texts
        metadatas: List of metadata dictionaries
        ids: List of chunk IDs
        retries: Number of retry attempts
        
    Returns:
        True if successful, False otherwise
    """
    for attempt in range(retries):
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Failed to add batch after {retries} attempts: {e}", exc_info=True)
                return False
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Batch add failed (attempt {attempt + 1}/{retries}), retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
    return False


def backfill_to_knowledge_base(
    chunk_files: List[Dict[str, Any]],
    config: Dict[str, Any],
    batch_size: int = 1000,
    use_multiprocessing: bool = True,
    num_workers: Optional[int] = None,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Add all chunks to ChromaDB knowledge base using batch operations
    
    Features:
    - Batch processing (500-1000 chunks per batch, optimized for ChromaDB)
    - Multiprocessing for parallel file reading and metadata extraction (4-8 workers)
    - Precomputed keywords in batches
    - Retry logic with exponential backoff
    - Performance benchmarking (time, memory, throughput)
    - Progress tracking with tqdm
    
    Args:
        chunk_files: List of chunk file dictionaries
        config: Configuration dictionary
        batch_size: Number of chunks per batch (500-1000 recommended)
        use_multiprocessing: Enable parallel processing (default: True)
        num_workers: Number of parallel workers (default: min(8, cpu_count))
        force: Reindex even if version tracker reports no changes
        
    Returns:
        Statistics dictionary with performance metrics
    """
    if not config.get("rag_enabled", False):
        logger.error("RAG is not enabled in config.json! Set 'rag_enabled': true")
        return {"status": "error", "message": "RAG not enabled"}
    
    try:
        from rag_integration import ChromaRAG
    except ImportError:
        logger.error("Failed to import ChromaRAG. Make sure rag_integration.py exists.", exc_info=True)
        return {"status": "error", "message": "Import failed"}
    
    chunk_files = list(chunk_files)

    # Initialize ChromaDB
    chroma_persist_dir = config.get("chroma_persist_dir", "./chroma_db")
    chroma_rag = ChromaRAG(persist_directory=chroma_persist_dir)
    
    initial_count = chroma_rag.collection.count()
    logger.info(f"Initialized ChromaDB. Existing chunks: {initial_count}")

    dedup_config = config.get("deduplication", {}) or {}
    dedup_manager = None
    if dedup_config.get("enabled"):
        if DeduplicationManager is None:
            logger.warning(
                "Deduplication enabled in config but module unavailable. Skipping dedup checks."
            )
        else:
            try:
                dedup_manager = DeduplicationManager(
                    persist_directory=chroma_persist_dir,
                    config=dedup_config,
                    preload=True,
                )
                logger.info(
                    "Deduplication manager initialized with %d known hashes",
                    len(dedup_manager.hash_index),
                )
            except Exception as exc:
                logger.warning("Failed to initialize deduplication manager: %s", exc)
                dedup_manager = None

    incremental_config = config.get("incremental_updates", {}) or {}
    version_tracker: Optional[VersionTracker] = None
    source_chunk_id_map: Dict[str, List[str]] = {}
    incremental_skip_count = 0

    if incremental_config.get("enabled"):
        try:
            tracker_config = dict(incremental_config)
            tracker_config.setdefault("base_dir", str(Path.cwd()))
            version_tracker = VersionTracker(tracker_config, logger=logger)
            logger.info(
                "Backfill incremental tracking enabled using %s",
                version_tracker.version_file,
            )
        except Exception as tracker_error:
            logger.warning(
                "Incremental updates: failed to initialize version tracker: %s",
                tracker_error,
            )
            version_tracker = None

    if version_tracker:
        filtered_chunk_files: List[Dict[str, Any]] = []
        grouped_infos: Dict[str, Dict[str, Any]] = {}

        for info in chunk_files:
            chunk_id_value = info.get("chunk_id") or build_chunk_id(
                info["timestamp"],
                info["base_name"],
                info["chunk_index"],
            )
            info["expected_chunk_id"] = chunk_id_value
            source_path = info.get("source_path")
            if source_path:
                source_key = str(source_path)
                group = grouped_infos.setdefault(source_key, {"infos": [], "ids": []})
                group["infos"].append(info)
                group["ids"].append(chunk_id_value)
            else:
                filtered_chunk_files.append(info)

        skipped_sources: Dict[str, int] = {}
        for source_path, data in grouped_infos.items():
            if force or version_tracker.needs_indexing(source_path, data["ids"]):
                source_chunk_id_map[source_path] = data["ids"]
                filtered_chunk_files.extend(data["infos"])
            else:
                incremental_skip_count += len(data["infos"])
                skipped_sources[source_path] = len(data["infos"])

        if skipped_sources:
            logger.info(
                "Incremental updates: skipping %d chunks across %d unchanged sources",
                incremental_skip_count,
                len(skipped_sources),
            )
        elif force:
            logger.info("Incremental updates: forced reindex enabled for backfill run.")

        chunk_files = filtered_chunk_files
    elif incremental_config.get("enabled"):
        logger.info(
            "Incremental updates configured but tracker unavailable; processing all chunks."
        )
        version_tracker = None
    
    # Performance tracking
    start_time = time.time()
    process = psutil.Process(os.getpid()) if PSUTIL_AVAILABLE else None
    initial_memory = process.memory_info().rss if process else 0
    
    stats = {
        "total_chunks": len(chunk_files),
        "successful": 0,
        "failed": 0,
        "skipped": incremental_skip_count,
        "dedup_skipped": 0,
        "incremental": {
            "skipped": incremental_skip_count,
            "recorded": 0,
        },
        "errors": [],
        "batches_processed": 0,
        "batches_failed": 0,
        "performance": {
            "start_time": start_time,
            "initial_memory_mb": initial_memory / (1024 * 1024) if initial_memory else 0,
            "peak_memory_mb": 0,
            "total_time_seconds": 0,
            "throughput_chunks_per_second": 0,
        },
    }
    
    # Determine number of workers for multiprocessing
    if use_multiprocessing and num_workers is None:
        num_workers = min(8, max(4, cpu_count()))
    elif not use_multiprocessing:
        num_workers = 1
    
    logger.info(f"Processing {len(chunk_files)} chunks with batch_size={batch_size}, workers={num_workers}")
    
    # Process chunks in parallel (file reading + keyword extraction + metadata prep)
    processed_chunks: List[Dict[str, Any]] = []
    
    if use_multiprocessing and num_workers > 1:
        logger.info(f"Using multiprocessing with {num_workers} workers")
        with Pool(processes=num_workers) as pool:
            # Process chunks in parallel with progress bar
            if TQDM_AVAILABLE:
                results = list(tqdm(
                    pool.imap(process_chunk_file_parallel, chunk_files),
                    total=len(chunk_files),
                    desc="Processing chunks (parallel)",
                    unit="chunk"
                ))
            else:
                results = pool.map(process_chunk_file_parallel, chunk_files)
            
            # Filter out None results (failed chunks)
            processed_chunks = [r for r in results if r is not None]
            stats["skipped"] = len(chunk_files) - len(processed_chunks)
    else:
        # Sequential processing (fallback)
        logger.info("Using sequential processing")
        iterator = tqdm(chunk_files, desc="Processing chunks", unit="chunk") if TQDM_AVAILABLE else chunk_files
        for chunk_info in iterator:
            result = process_chunk_file_parallel(chunk_info)
            if result:
                processed_chunks.append(result)
            else:
                stats["skipped"] += 1
    
    logger.info(f"Processed {len(processed_chunks)} chunks successfully, {stats['skipped']} skipped")
    
    # Verify chunks don't already exist (check in batches for efficiency)
    existing_ids = set()
    if processed_chunks:
        logger.info("Checking for existing chunks in KB...")
        check_batch_size = min(1000, len(processed_chunks))
        for i in range(0, len(processed_chunks), check_batch_size):
            batch_ids = [chunk_data["id"] for chunk_data in processed_chunks[i:i+check_batch_size]]
            try:
                existing = chroma_rag.collection.get(ids=batch_ids)["ids"]
                existing_ids.update(existing)
            except Exception:
                pass  # If get fails, assume all are new
    
    if existing_ids:
        logger.info(f"Found {len(existing_ids)} chunks already in KB, skipping duplicates")
        stats["skipped"] += len(existing_ids)
    
    # Prepare batches for parallel ChromaDB insertion
    batches_for_insertion: List[Tuple[List[str], List[Dict[str, Any]], List[str]]] = []
    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    ids: List[str] = []
    
    # Filter out existing chunks and prepare batches
    for chunk_data in processed_chunks:
        chunk_id = chunk_data["id"]
        chunk_text = chunk_data["text"]
        chunk_metadata = chunk_data.get("metadata") or {}

        # Skip if already exists
        if chunk_id in existing_ids:
            continue

        chunk_hash = compute_content_hash(chunk_text)
        
        if dedup_manager:
            try:
                is_duplicate, dedup_hash, existing_hash_ids = dedup_manager.is_duplicate(
                    chunk_text,
                    chunk_id=chunk_id,
                )
            except Exception as dedup_error:
                logger.warning(
                    "Deduplication check failed for chunk %s: %s",
                    chunk_id,
                    dedup_error,
                )
                is_duplicate = False
                existing_hash_ids = []
                dedup_hash = chunk_hash
            else:
                if dedup_hash:
                    chunk_hash = dedup_hash
                    if isinstance(chunk_metadata, dict):
                        chunk_metadata["content_hash"] = chunk_hash

            if dedup_manager and is_duplicate:
                stats["dedup_skipped"] += 1
                stats["skipped"] += 1
                preview = existing_hash_ids[:3]
                if len(existing_hash_ids) > 3:
                    preview.append("...")
                logger.info(
                    "Deduplication skipped chunk %s (matches: %s)",
                    chunk_id,
                    preview if preview else "existing chunk",
                )
                continue
        
        # Ensure unique IDs within batch
        if chunk_id in ids:
            new_chunk_id = f"{chunk_id}_{uuid.uuid4().hex[:8]}"
            logger.debug("Adjusted duplicate chunk ID %s -> %s", chunk_id, new_chunk_id)
            chunk_id = new_chunk_id
        
        if isinstance(chunk_metadata, dict):
            chunk_metadata = dict(chunk_metadata)
            chunk_metadata["content_hash"] = chunk_hash
        else:
            chunk_metadata = {"content_hash": chunk_hash}
        
        if dedup_manager:
            dedup_manager.add_hash(chunk_hash, chunk_id)
        
        # Add to batch
        texts.append(chunk_text)
        metadatas.append(chunk_metadata)
        ids.append(chunk_id)
        
        # Create batch when it reaches batch_size (500-1000 recommended)
        if len(texts) >= batch_size:
            batches_for_insertion.append(
                (texts.copy(), metadatas.copy(), ids.copy())
            )
            texts.clear()
            metadatas.clear()
            ids.clear()
    
    # Add final batch if any remain
    if texts:
        batches_for_insertion.append(
            (texts.copy(), metadatas.copy(), ids.copy())
        )
    
    logger.info(f"Prepared {len(batches_for_insertion)} batches for ChromaDB insertion")
    if dedup_manager:
        logger.info(
            "Deduplication skipped %d chunk(s) during preparation",
            stats["dedup_skipped"],
        )
    
    # Monitor CPU usage
    cpu_percentages = []
    if PSUTIL_AVAILABLE:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_percentages.append(cpu_percent)
        logger.info(f"Initial CPU usage: {cpu_percent:.1f}%")
        stats["performance"]["initial_cpu_percent"] = cpu_percent
    
    # Insert batches - use parallel insertion if multiprocessing enabled
    use_parallel_inserts = (
        use_multiprocessing
        and num_workers > 1
        and len(batches_for_insertion) > 1
    )
    if use_parallel_inserts:
        logger.info(f"Using parallel ChromaDB insertion with {min(num_workers, len(batches_for_insertion))} workers")
        
        # Prepare batch data with persist directory for separate connections
        batch_data_with_dir = [
            (texts, metadatas, ids, chroma_persist_dir)
            for texts, metadatas, ids in batches_for_insertion
        ]
        
        # Use multiprocessing for parallel inserts with separate connections per process
        with Pool(processes=min(num_workers, len(batches_for_insertion))) as pool:
            if TQDM_AVAILABLE:
                results = list(tqdm(
                    pool.imap(insert_chunk_batch_parallel, batch_data_with_dir),
                    total=len(batch_data_with_dir),
                    desc="Inserting to ChromaDB (parallel)",
                    unit="batch"
                ))
            else:
                results = pool.map(insert_chunk_batch_parallel, batch_data_with_dir)
            
            # Sum results
            for result in results:
                if result > 0:
                    stats["successful"] += result
                    stats["batches_processed"] += 1
                else:
                    stats["batches_failed"] += 1
    else:
        # Sequential insertion (fallback)
        logger.info("Using sequential ChromaDB insertion")
        iterator = (
            tqdm(batches_for_insertion, desc="Adding to ChromaDB", unit="batch")
            if TQDM_AVAILABLE
            else batches_for_insertion
        )
        
        for texts, metadatas, ids in iterator:
            success = add_with_retry(chroma_rag.collection, texts, metadatas, ids)
            if success:
                stats["successful"] += len(texts)
                stats["batches_processed"] += 1
            else:
                stats["failed"] += len(texts)
                stats["batches_failed"] += 1
                stats["errors"].append(f"Batch {stats['batches_processed'] + stats['batches_failed']} failed")
            
            # Update memory and CPU tracking
            if process:
                current_memory = process.memory_info().rss / (1024 * 1024)  # MB
                stats["performance"]["peak_memory_mb"] = max(
                    stats["performance"]["peak_memory_mb"],
                    current_memory
                )
            
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_percentages.append(cpu_percent)
                # Alert if CPU saturation (>90%)
                if cpu_percent > 90:
                    logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
    
    # Calculate average CPU usage
    if cpu_percentages:
        avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
        max_cpu = max(cpu_percentages)
        stats["performance"]["avg_cpu_percent"] = avg_cpu
        stats["performance"]["max_cpu_percent"] = max_cpu
        logger.info(f"CPU usage - Avg: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%")
    
    # Calculate performance metrics
    total_time = time.time() - start_time
    stats["performance"]["total_time_seconds"] = total_time
    if total_time > 0:
        stats["performance"]["throughput_chunks_per_second"] = stats["successful"] / total_time
    
    if process:
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        stats["performance"]["peak_memory_mb"] = max(
            stats["performance"]["peak_memory_mb"],
            final_memory
        )
        stats["performance"]["final_memory_mb"] = final_memory
    
    # Final statistics
    final_count = chroma_rag.collection.count()
    logger.info(f"\n{'='*60}")
    logger.info(f"Backfill Complete!")
    logger.info(f"{'='*60}")
    logger.info(f"Total chunks processed: {stats['total_chunks']}")
    logger.info(f"  [+] Successful: {stats['successful']}")
    logger.info(f"  [-] Failed: {stats['failed']}")
    logger.info(f"  [>] Skipped: {stats['skipped']}")
    logger.info(f"Batches processed: {stats['batches_processed']}")
    logger.info(f"Batches failed: {stats['batches_failed']}")
    logger.info(f"Total chunks in KB: {final_count} (was {initial_count})")
    logger.info(f"\nPerformance Metrics:")
    logger.info(f"  Total time: {stats['performance']['total_time_seconds']:.2f} seconds")
    logger.info(f"  Throughput: {stats['performance']['throughput_chunks_per_second']:.2f} chunks/second")
    if PSUTIL_AVAILABLE:
        logger.info(f"  Peak memory: {stats['performance']['peak_memory_mb']:.2f} MB")
        logger.info(f"  Memory increase: {stats['performance']['peak_memory_mb'] - stats['performance']['initial_memory_mb']:.2f} MB")
    logger.info(f"{'='*60}")
    
    if version_tracker:
        recorded_sources = 0
        for source_path, chunk_ids in source_chunk_id_map.items():
            if not chunk_ids:
                continue
            try:
                version_tracker.mark_indexed(source_path, chunk_ids=chunk_ids)
                recorded_sources += 1
            except Exception as tracker_error:  # noqa: BLE001
                logger.warning(
                    "Incremental updates: failed to mark indexed for %s: %s",
                    source_path,
                    tracker_error,
                )
        stats["incremental"]["recorded"] = recorded_sources
        if recorded_sources:
            logger.info(
                "Incremental updates: marked %d source file(s) as indexed.",
                recorded_sources,
            )
    
    return {
        "status": "success",
        "stats": stats,
        "final_kb_count": final_count,
        "initial_kb_count": initial_count
    }


def main() -> None:
    """Main function"""
    logger.info("="*60)
    logger.info("Knowledge Base Backfill Script - Optimized v2.1.6")
    logger.info("="*60)
    
    # Load configuration
    config = load_config()
    
    # Check if RAG is enabled
    if not config.get("rag_enabled", False):
        logger.warning("[!] RAG is not enabled in config.json")
        response = input("Do you want to enable RAG now? (y/n): ").strip().lower()
        if response == 'y':
            config["rag_enabled"] = True
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            logger.info("[+] RAG enabled in config.json")
        else:
            logger.error("Cannot proceed without RAG enabled. Exiting.")
            return
    
    # Get output directory
    output_dir = Path(config.get("output_dir", "04_output"))
    if not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}", exc_info=True)
        return
    
    # Get configuration with command-line args (if using argparse)
    import sys
    use_multiprocessing = config.get("backfill_multiprocessing", True)
    num_workers = config.get("backfill_num_workers")
    enable_profile = config.get("backfill_profile", False)
    force_reindex = "--force" in sys.argv
    
    # Simple command-line parsing (can be enhanced with argparse later)
    if "--no-multiprocessing" in sys.argv:
        use_multiprocessing = False
    if "--profile" in sys.argv:
        enable_profile = True
    
    # Get batch size from config or use default
    batch_size = config.get("backfill_batch_size", 750)
    if batch_size < 100 or batch_size > 10000:
        logger.warning(f"Batch size {batch_size} out of range (100-10000), using 750")
        batch_size = 750
    
    # Find all chunk files with validation
    logger.info("Scanning for chunk files...")
    expected_count = config.get("expected_chunk_count")  # Optional: set in config.json
    chunk_files, folder_stats = find_chunk_files(output_dir, expected_count=expected_count)
    
    # Log folder statistics
    logger.info(f"Folder statistics: {folder_stats['folders_with_chunks']} folders with chunks, "
                f"{folder_stats['empty_folders']} empty folders")
    
    if not chunk_files:
        logger.warning("No chunk files found!")
        return
    
    # Confirm before proceeding
    logger.info(f"\nFound {len(chunk_files)} chunk files to add to knowledge base")
    logger.info(f"Batch size: {batch_size} chunks per batch")
    logger.info(f"Multiprocessing: {'enabled' if use_multiprocessing else 'disabled'}")
    if use_multiprocessing:
        if num_workers:
            logger.info(f"Workers: {num_workers}")
        else:
            logger.info(f"Workers: auto (4-8 based on CPU cores)")
    logger.info(f"Estimated batches: {(len(chunk_files) + batch_size - 1) // batch_size}")
    if force_reindex:
        logger.info("Incremental updates: force flag detected; backfill will reindex all eligible chunks.")
    response = input("Proceed with backfill? (y/n): ").strip().lower()
    if response != 'y':
        logger.info("Backfill cancelled by user")
        return
    
    # Perform backfill with optional profiling
    if enable_profile:
        import cProfile
        import pstats
        
        logger.info("Profiling enabled - output: backfill_profile.prof")
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = backfill_to_knowledge_base(
                chunk_files, 
                config, 
                batch_size=batch_size,
                use_multiprocessing=use_multiprocessing,
                num_workers=num_workers,
                force=force_reindex,
            )
        finally:
            profiler.disable()
            profiler.dump_stats("backfill_profile.prof")
            logger.info("Profile saved to backfill_profile.prof")
            
            # Print top 20 functions by cumulative time
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            logger.info("\nTop 20 functions by cumulative time:")
            stats.print_stats(20)
    else:
        result = backfill_to_knowledge_base(
            chunk_files,
            config,
            batch_size=batch_size,
            use_multiprocessing=use_multiprocessing,
            num_workers=num_workers,
            force=force_reindex,
        )
    
    if result.get("status") == "success":
        logger.info("[+] Backfill completed successfully!")
        logger.info(f"Knowledge base now contains {result['final_kb_count']} chunks")
        logger.info(f"Added {result['final_kb_count'] - result['initial_kb_count']} new chunks")
    else:
        logger.error(f"[-] Backfill failed: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    main()
