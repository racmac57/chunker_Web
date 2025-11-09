"""
RAG Integration Module for Chunker_v2
Handles retrieval-augmented generation with ChromaDB and Ollama embeddings
"""

import chromadb
from chromadb.config import Settings
from copy import deepcopy
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure compatibility with chromadb expectations on hnswlib builds
try:  # pragma: no cover - defensive guard for varying hnswlib builds
    import hnswlib  # type: ignore

    if not hasattr(hnswlib.Index, "file_handle_count"):
        # Older hnswlib wheels (e.g., Windows builds) do not expose this attribute.
        # Provide a benign fallback value so chromadb's guard logic succeeds.
        hnswlib.Index.file_handle_count = 0
except ImportError:
    # hnswlib is optional when using alternative vector stores; leave unmodified.
    hnswlib = None  # type: ignore

from query_cache import QueryCache, CacheKey

logger = logging.getLogger(__name__)


class ChromaRAG:
    """
    ChromaDB-based RAG implementation for knowledge base management
    Provides CRUD operations for vector database with hybrid search
    """
    
    @staticmethod
    def _build_chunk_id(metadata: Dict[str, Any]) -> str:
        timestamp = metadata.get("timestamp") or datetime.now().isoformat()
        file_name = metadata.get("file_name") or metadata.get("source_file") or "chunk"
        chunk_index = metadata.get("chunk_index", 0)
        chunk_index_str = str(chunk_index)
        return f"{timestamp}_{file_name}_chunk{chunk_index_str}"

    def __init__(self, persist_directory="./chroma_db",
                 persist_dir: Optional[str] = None,
                 hnsw_m: int = 32, 
                 hnsw_ef_construction: int = 512,
                 hnsw_ef_search: int = 200,
                 collection_name: str = "chunker_knowledge_base",
                 recreate_collection: bool = False,
                 query_cache_config: Optional[Dict[str, Any]] = None,
                 config_path: str = "config.json"):
        """
        Initialize ChromaDB client and collection with HNSW optimization
        
        Args:
            persist_directory: Directory to persist ChromaDB database
            hnsw_m: Number of bi-directional links for each node (default: 32)
            hnsw_ef_construction: Size of the dynamic candidate list during construction (default: 512)
            hnsw_ef_search: Size of the dynamic candidate list during search (default: 200)
            recreate_collection: If True, delete existing collection and recreate with new HNSW params (default: False)
        """
        # Allow alias parameter persist_dir
        if persist_dir is not None:
            persist_directory = persist_dir

        # Create settings with explicit API implementation
        chroma_settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True,
            chroma_api_impl="chromadb.api.segment.SegmentAPI",
            chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_producer_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_consumer_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_segment_manager_impl="chromadb.segment.impl.manager.local.LocalSegmentManager"
        )
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=chroma_settings
        )
        self._query_cache: Optional[QueryCache] = None
        self._configure_query_cache(query_cache_config, config_path)

        self._config_path = config_path
        self._global_config = self._load_global_config(config_path)
        batch_config = (self._global_config or {}).get("batch", {})
        self._batch_size = max(int(batch_config.get("size", 500) or 1), 1)
        self._search_config = (self._global_config or {}).get("search", {})
        default_ef_value = (self._global_config or {}).get("default_ef_search", 64)
        try:
            self.default_ef_search = int(default_ef_value)
        except (TypeError, ValueError):
            self.default_ef_search = 64
        
        # Create or get collection for chunker knowledge base with HNSW optimization
        # HNSW parameters are immutable after creation, so we try to get existing first
        # If recreate_collection is True, delete existing collection first
        if recreate_collection:
            try:
                self.client.delete_collection(name=collection_name)
                logger.warning(f"Deleted existing collection '{collection_name}' to recreate with new HNSW params")
            except Exception as e:
                logger.info(f"Collection '{collection_name}' doesn't exist or already deleted: {e}")
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection (using its original HNSW params)")
        except Exception:
            # Collection doesn't exist, create new with HNSW parameters
            # Note: Key names must be exact: "hnsw:construction_ef" not "hnsw:ef_construction"
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "description": "Enterprise chunker knowledge base with RAG capabilities",
                    "hnsw:M": hnsw_m,
                    "hnsw:construction_ef": hnsw_ef_construction,
                    "hnsw:search_ef": hnsw_ef_search  # Default for queries; override per query if needed
                }
            )
            logger.info(f"Created new collection with custom HNSW params: M={hnsw_m}, construction_ef={hnsw_ef_construction}, search_ef={hnsw_ef_search}")
        
        logger.info(f"Initialized ChromaDB collection with {self.collection.count()} existing chunks")
    
    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        raw = dict(metadata or {})
        file_name = raw.get("file_name") or raw.get("source_file") or "chunk"
        file_type = raw.get("file_type") or Path(file_name).suffix or ""
        timestamp = raw.get("timestamp") or datetime.now().isoformat()
        chunk_index = raw.get("chunk_index", raw.get("chunk_id", 0))

        keywords_raw = raw.get("keywords", [])
        if isinstance(keywords_raw, str):
            try:
                parsed = json.loads(keywords_raw)
                keywords_list = (
                    [str(item).strip() for item in parsed if str(item).strip()]
                    if isinstance(parsed, list)
                    else ([keywords_raw.strip()] if keywords_raw.strip() else [])
                )
            except Exception:
                keywords_list = [keywords_raw.strip()] if keywords_raw.strip() else []
        elif isinstance(keywords_raw, (list, tuple, set)):
            keywords_list = [str(item).strip() for item in keywords_raw if str(item).strip()]
        elif keywords_raw:
            keywords_list = [str(keywords_raw).strip()]
        else:
            keywords_list = []

        tags_raw = raw.get("tags", [])
        if isinstance(tags_raw, str):
            try:
                parsed = json.loads(tags_raw)
                tags_list = (
                    [str(item).strip() for item in parsed if str(item).strip()]
                    if isinstance(parsed, list)
                    else ([tags_raw.strip()] if tags_raw.strip() else [])
                )
            except Exception:
                tags_list = [tags_raw.strip()] if tags_raw.strip() else []
        elif isinstance(tags_raw, (list, tuple, set)):
            tags_list = [str(item).strip() for item in tags_raw if str(item).strip()]
        else:
            tags_list = []

        department = raw.get("department", "admin")
        file_size = raw.get("file_size", 0)
        processing_time = raw.get("processing_time", 0)
        content_hash = raw.get("content_hash", "")

        return {
            "file_name": file_name,
            "file_type": file_type,
            "chunk_index": str(chunk_index),
            "timestamp": timestamp,
            "department": department,
            "keywords": json.dumps(keywords_list),
            "keywords_list": keywords_list,
            "tags": tags_list,
            "file_size": str(file_size),
            "processing_time": str(processing_time),
            "content_hash": content_hash,
        }

    def add_chunk(self, chunk_text: str, metadata: Dict[str, Any]) -> str:
        prepared_metadata = self._prepare_metadata(metadata)
        doc_id = self._build_chunk_id(prepared_metadata)

        self.collection.add(
            documents=[chunk_text],
            metadatas=[prepared_metadata],
            ids=[doc_id],
        )
        self._update_collection_search_ef()
        return doc_id

    def add_chunks(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[Any]] = None,
    ) -> List[str]:
        batch_size = getattr(self, "_batch_size", 500)
        batch_documents: List[str] = []
        batch_metadatas: List[Dict[str, Any]] = []
        batch_ids: List[str] = []
        batch_embeddings: List[Any] = []
        added_ids: List[str] = []

        for index, chunk_text in enumerate(chunks):
            if not chunk_text or not chunk_text.strip():
                logger.debug("Skipping empty chunk at index %s", index)
                continue

            raw_metadata = metadatas[index] if index < len(metadatas) else {}
            prepared_metadata = self._prepare_metadata(raw_metadata)
            doc_id = (
                ids[index]
                if ids and index < len(ids) and ids[index]
                else self._build_chunk_id(prepared_metadata)
            )

            embedding_value = None
            if embeddings is not None:
                if index >= len(embeddings):
                    logger.debug("Missing embedding for chunk index %s; skipping", index)
                    continue
                embedding_value = embeddings[index]
                if embedding_value is None:
                    logger.debug("Skipping chunk %s due to null embedding", doc_id)
                    continue
                if hasattr(embedding_value, "__len__") and len(embedding_value) == 0:
                    logger.debug("Skipping chunk %s due to empty embedding", doc_id)
                    continue

            batch_documents.append(chunk_text)
            batch_metadatas.append(prepared_metadata)
            batch_ids.append(doc_id)
            if embeddings is not None:
                batch_embeddings.append(embedding_value)

            if len(batch_documents) >= batch_size:
                self._flush_batch(
                    batch_documents,
                    batch_metadatas,
                    batch_ids,
                    batch_embeddings if embeddings is not None else None,
                )
                added_ids.extend(batch_ids)
                batch_documents, batch_metadatas, batch_ids = [], [], []
                if embeddings is not None:
                    batch_embeddings = []

        # Flush remainder
        if batch_documents:
            self._flush_batch(
                batch_documents,
                batch_metadatas,
                batch_ids,
                batch_embeddings if embeddings is not None else None,
            )
            added_ids.extend(batch_ids)

        if not added_ids:
            logger.info("No valid chunks to add to ChromaDB")
            return []

        self._update_collection_search_ef()
        return added_ids

    def _flush_batch(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: Optional[List[Any]],
    ) -> None:
        kwargs: Dict[str, Any] = {
            "documents": list(documents),
            "metadatas": list(metadatas),
            "ids": list(ids),
        }
        if embeddings is not None:
            kwargs["embeddings"] = list(embeddings)
        self.collection.add(**kwargs)
        logger.info("Added %s chunks to ChromaDB", len(documents))

    def add_chunks_bulk(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[Any]] = None,
    ) -> List[str]:
        return self.add_chunks(chunks, metadatas, ids=ids, embeddings=embeddings)
    
    def search_similar(self, query: str, n_results: int = 5,
                       file_type: Optional[str] = None,
                       department: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       ef_search: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using semantic similarity with query optimizations
        
        Features:
        - Metadata filtering for faster queries
        - Configurable ef_search for accuracy/speed tradeoff
        - Batch query support
        
        Args:
            query: Search query text
            n_results: Number of results to return
            file_type: Filter by file type (optional) - improves performance
            department: Filter by department (optional) - improves performance
            ef_search: HNSW ef_search parameter (100-500, higher = more accurate but slower)
        
        Returns:
            List of formatted search results
        """
        normalized_tags: List[str] = []
        if tags:
            normalized_tags = [str(tag).strip() for tag in tags if str(tag).strip()]

        filters: List[Dict[str, Any]] = []
        if file_type:
            filters.append({"file_type": file_type})
        if department:
            filters.append({"department": department})
        if normalized_tags:
            filters.extend({"tags": {"$contains": tag}} for tag in normalized_tags)

        if ef_search is None:
            ef_search = self.default_ef_search

        if not filters:
            where_clause: Optional[Dict[str, Any]] = None
        elif len(filters) == 1:
            where_clause = filters[0]
        else:
            where_clause = {"$and": filters}

        # Use optimized ef_search if provided
        query_kwargs = {
            "query_texts": [query],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where_clause:
            query_kwargs["where"] = where_clause
        
        # Add ef_search if specified (override default search_ef from collection metadata)
        if ef_search:
            query_kwargs["ef"] = ef_search

        cache_key: Optional[CacheKey] = None
        if self._query_cache:
            cache_key = self._build_cache_key(
                query,
                n_results,
                file_type,
                department,
                tuple(sorted(normalized_tags)) if normalized_tags else (),
                ef_search,
            )
            cached = self._query_cache.get(cache_key)
            if cached is not None:
                logger.debug("Query cache hit for '%s'", query)
                return deepcopy(cached)
        
        try:
            # Query the collection with optimizations
            results = self.collection.query(**query_kwargs)
            formatted = self._format_results(results)

            if self._query_cache and cache_key is not None:
                self._query_cache.put(cache_key, deepcopy(formatted))
            
            return formatted
            
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {e}", exc_info=True)
            return []
    
    def search_by_keywords(self, keywords: List[str], n_results: int = 5) -> List[Dict]:
        """
        Search by specific keywords
        
        Args:
            keywords: List of keywords to search for
            n_results: Number of results to return
        
        Returns:
            List of formatted search results
        """
        # Convert keywords to query string
        query = " ".join(keywords)
        return self.search_similar(query, n_results)
    
    def get_chunk_by_id(self, chunk_id: str) -> Dict:
        """
        Retrieve specific chunk by ID
        
        Args:
            chunk_id: Unique chunk identifier
        
        Returns:
            Chunk data as dictionary
        """
        try:
            results = self.collection.get(ids=[chunk_id])
            formatted = self._format_results(results)
            return formatted[0] if formatted else None
            
        except Exception as e:
            logger.error(f"Failed to get chunk by ID: {e}")
            return {}
    
    def update_chunk(self, chunk_id: str, new_text: str, new_metadata: Dict):
        """Update existing chunk in database"""
        try:
            self.collection.update(
                ids=[chunk_id],
                documents=[new_text],
                metadatas=[new_metadata]
            )
            logger.info(f"Updated chunk: {chunk_id}")
            
        except Exception as e:
            logger.error(f"Failed to update chunk: {e}")
            raise
    
    def delete_chunk(self, chunk_id: str):
        """Delete chunk from database"""
        try:
            self.collection.delete(ids=[chunk_id])
            logger.info(f"Deleted chunk: {chunk_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete chunk: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name,
            "last_updated": datetime.now().isoformat()
        }
    
    def _format_results(self, results: Dict) -> List[Dict]:
        """
        Format ChromaDB results for easier use
        
        Args:
            results: Raw ChromaDB query results
        
        Returns:
            List of formatted result dictionaries
        """
        formatted_results = []
        
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })
        
        return formatted_results

    @staticmethod
    def _load_global_config(config_path: str) -> Dict[str, Any]:
        try:
            path = Path(config_path)
            if not path.exists():
                return {}
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception as exc:
            logger.debug("Unable to load global config: %s", exc)
            return {}

    # ------------------------------------------------------------------ #
    # Query cache helpers
    # ------------------------------------------------------------------ #
    def _configure_query_cache(
        self,
        provided_config: Optional[Dict[str, Any]],
        config_path: str,
    ) -> None:
        config = provided_config or self._load_query_cache_config(config_path)
        if not config or not isinstance(config, dict):
            return

        if not config.get("enabled", False):
            return

        max_entries = config.get("max_entries", config.get("max_size", 128))
        ttl_seconds = config.get("ttl_seconds")

        try:
            max_entries_int = int(max_entries)
        except (TypeError, ValueError):
            max_entries_int = 128

        if ttl_seconds is None:
            ttl_hours = float(config.get("ttl_hours", 1))
            ttl_seconds_value = max(ttl_hours, 0.001) * 3600
        else:
            try:
                ttl_seconds_value = max(float(ttl_seconds), 0.001)
            except (TypeError, ValueError):
                ttl_seconds_value = 600.0

        memory_limit_mb = config.get("memory_limit_mb")
        memory_limit_bytes = None
        if memory_limit_mb:
            try:
                memory_limit_bytes = int(memory_limit_mb) * 1024 * 1024
            except (TypeError, ValueError):
                memory_limit_bytes = None

        try:
            self._query_cache = QueryCache(
                max_size=max_entries_int,
                ttl_seconds=ttl_seconds_value,
                memory_limit_bytes=memory_limit_bytes,
            )
            logger.info(
                "Query cache enabled (entries=%s, ttl_seconds=%.2f, memory_limit=%s)",
                max_entries_int,
                ttl_seconds_value,
                f"{memory_limit_mb}MB" if memory_limit_mb else "None",
            )
        except Exception as exc:
            logger.error("Failed to initialize query cache: %s", exc)
            self._query_cache = None

    @staticmethod
    def _load_query_cache_config(config_path: str) -> Optional[Dict[str, Any]]:
        try:
            path = Path(config_path)
            if not path.exists():
                return None
            import json

            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("query_cache")
        except Exception as exc:
            logger.debug("Unable to load query cache config: %s", exc)
            return None

    @staticmethod
    def _build_cache_key(
        query: str,
        n_results: int,
        file_type: Optional[str],
        department: Optional[str],
        tags: Tuple[str, ...],
        ef_search: Optional[int],
    ) -> CacheKey:
        return (
            query,
            n_results,
            file_type or "",
            department or "",
            tags,
            ef_search or 0,
        )

    def get_query_cache_stats(self) -> Optional[Dict[str, Any]]:
        if not self._query_cache:
            return None
        return self._query_cache.get_stats()

    def invalidate_query_cache(self) -> None:
        if self._query_cache:
            self._query_cache.invalidate()

    def _update_collection_search_ef(self) -> None:
        if not isinstance(getattr(self, "_search_config", None), dict):
            return

        target = self._search_config.get("ef_search")
        if target is None:
            return

        try:
            target_value = int(target)
        except (TypeError, ValueError):
            logger.debug("Invalid ef_search value configured: %s", target)
            return

        modify = getattr(self.collection, "modify", None)
        if not callable(modify):
            logger.debug("Chroma collection does not support modify(); skipping ef update")
            return

        try:
            modify(metadata={"hnsw:search_ef": target_value})
            logger.debug("Updated hnsw:search_ef to %s", target_value)
        except Exception as exc:
            logger.debug("Unable to update hnsw:search_ef: %s", exc)


class FaithfulnessScorer:
    """
    Advanced faithfulness scoring for RAG evaluation
    Evaluates how well generated answers are grounded in source context
    """
    
    def __init__(self):
        """Initialize faithfulness scorer with sentence transformer model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def extract_claims(self, answer: str) -> List[str]:
        """
        Extract factual claims from the answer
        
        Args:
            answer: Generated answer text
        
        Returns:
            List of extracted claim sentences
        """
        import nltk
        import re
        
        sentences = nltk.sent_tokenize(answer)
        claims = []
        
        for sentence in sentences:
            # Remove questions and opinion indicators
            if not re.search(r'\?|I think|I believe|in my opinion', sentence, re.IGNORECASE):
                # Extract factual statements
                if re.search(r'\b(is|are|was|were|has|have|will|can|should)\b', sentence, re.IGNORECASE):
                    claims.append(sentence.strip())
        
        return claims
    
    def calculate_faithfulness(self, answer: str, context: str, threshold: float = 0.7) -> float:
        """
        Calculate faithfulness score (0-1) based on how well answer claims
        are supported by the context
        
        Args:
            answer: Generated answer
            context: Source context
            threshold: Similarity threshold for support (default: 0.7)
        
        Returns:
            Faithfulness score between 0 and 1
        """
        claims = self.extract_claims(answer)
        if not claims:
            return 1.0  # No claims to verify
        
        # Get embeddings for claims and context
        claim_embeddings = self.model.encode(claims)
        context_embeddings = self.model.encode([context])
        
        faithfulness_scores = []
        
        for claim_emb in claim_embeddings:
            # Find best matching context sentence
            similarities = cosine_similarity([claim_emb], context_embeddings)[0]
            max_similarity = np.max(similarities)
            
            # Check if claim is supported by context
            if max_similarity >= threshold:
                faithfulness_scores.append(1.0)
            else:
                # Check for partial support
                faithfulness_scores.append(max_similarity)
        
        return float(np.mean(faithfulness_scores))
    
    def detailed_faithfulness_analysis(self, answer: str, context: str) -> Dict:
        """
        Provide detailed analysis of faithfulness
        
        Args:
            answer: Generated answer
            context: Source context
        
        Returns:
            Detailed analysis dictionary
        """
        claims = self.extract_claims(answer)
        analysis = {
            "total_claims": len(claims),
            "supported_claims": 0,
            "unsupported_claims": 0,
            "claim_details": []
        }
        
        for claim in claims:
            claim_emb = self.model.encode([claim])
            context_emb = self.model.encode([context])
            similarity = cosine_similarity(claim_emb, context_emb)[0][0]
            
            is_supported = similarity >= 0.7
            if is_supported:
                analysis["supported_claims"] += 1
            else:
                analysis["unsupported_claims"] += 1
            
            analysis["claim_details"].append({
                "claim": claim,
                "similarity": float(similarity),
                "supported": is_supported
            })
        
        analysis["faithfulness_score"] = analysis["supported_claims"] / analysis["total_claims"] if analysis["total_claims"] > 0 else 1.0
        
        return analysis


def integrate_chroma_with_watcher():
    """
    Integration example for ChromaDB with existing watcher system
    
    This function demonstrates how to integrate ChromaDB with the
    existing file processing pipeline
    """
    
    # Initialize ChromaDB
    chroma_rag = ChromaRAG()
    
    def process_file_with_chroma(file_path, config, chunks, department="admin"):
        """
        Enhanced file processing with ChromaDB integration
        
        Args:
            file_path: Path to the file being processed
            config: Configuration dictionary
            chunks: List of text chunks from file
            department: Department classification
        
        Returns:
            True if successful
        """
        timestamp = datetime.now().isoformat()
        
        # Add each chunk to ChromaDB
        for i, chunk in enumerate(chunks):
            metadata = {
                "file_name": file_path.name,
                "file_type": file_path.suffix,
                "chunk_index": i + 1,
                "timestamp": timestamp,
                "department": department,
                "keywords": extract_keywords(chunk),
                "file_size": file_path.stat().st_size,
                "processing_time": 0
            }
            
            try:
                chunk_id = chroma_rag.add_chunk(chunk, metadata)
                logger.info(f"Added chunk to ChromaDB: {chunk_id}")
            except Exception as e:
                logger.error(f"Failed to add chunk to ChromaDB: {e}")
        
        return True
    
    return process_file_with_chroma


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


def example_usage():
    """Example usage of ChromaRAG system"""
    
    # Initialize RAG system
    rag = ChromaRAG()
    
    # Add a chunk to the knowledge base
    metadata = {
        "file_name": "excel_guide.md",
        "file_type": ".md",
        "chunk_index": 1,
        "timestamp": "2025-10-27T12:00:00Z",
        "department": "admin",
        "keywords": ["excel", "vlookup", "formulas"]
    }
    
    chunk_id = rag.add_chunk(
        "VLOOKUP is used to find values in a table. Syntax: VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup])",
        metadata
    )
    print(f"Added chunk: {chunk_id}")
    
    # Search for similar content
    results = rag.search_similar("How do I use vlookup in Excel?", n_results=3)
    print(f"Found {len(results)} similar chunks")
    
    # Get collection statistics
    stats = rag.get_collection_stats()
    print(f"Total chunks in database: {stats['total_chunks']}")


if __name__ == "__main__":
    # Run example usage
    example_usage()

