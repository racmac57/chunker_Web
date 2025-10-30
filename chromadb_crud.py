"""
ChromaDB CRUD Operations for Chunker_v2
Comprehensive vector database operations with metadata management
"""

import os
import json
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ChromaDBManager:
    """
    Comprehensive ChromaDB manager with CRUD operations and advanced features.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "chunker_knowledge_base"):
        """
        Initialize ChromaDB manager.
        
        Args:
            persist_directory: Directory to persist ChromaDB database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        self._initialize_chromadb()
        
        logger.info(f"Initialized ChromaDB manager with collection: {collection_name}")
    
    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Enterprise chunker knowledge base with RAG capabilities"}
            )
            
            logger.info(f"ChromaDB collection '{self.collection_name}' ready with {self.collection.count()} existing chunks")
            
        except ImportError:
            logger.error("ChromaDB not available. Install with: pip install chromadb")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def create_chunk(self, chunk_text: str, metadata: Dict[str, Any], 
                    chunk_id: Optional[str] = None) -> str:
        """
        Create a new chunk in the vector database.
        
        Args:
            chunk_text: The text content of the chunk
            metadata: Dictionary containing chunk metadata
            chunk_id: Optional custom chunk ID
            
        Returns:
            chunk_id: Unique identifier for the created chunk
        """
        try:
            if not chunk_id:
                chunk_id = self._generate_chunk_id(metadata)
            
            # Prepare metadata for ChromaDB
            chroma_metadata = self._prepare_metadata(metadata)
            
            # Add to collection
            self.collection.add(
                documents=[chunk_text],
                metadatas=[chroma_metadata],
                ids=[chunk_id]
            )
            
            logger.info(f"Created chunk: {chunk_id}")
            return chunk_id
            
        except Exception as e:
            logger.error(f"Failed to create chunk: {e}")
            raise
    
    def read_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a specific chunk by ID.
        
        Args:
            chunk_id: Unique chunk identifier
            
        Returns:
            Chunk data dictionary or None if not found
        """
        try:
            results = self.collection.get(ids=[chunk_id])
            
            if not results['documents']:
                return None
            
            return {
                "id": chunk_id,
                "document": results['documents'][0],
                "metadata": results['metadatas'][0]
            }
            
        except Exception as e:
            logger.error(f"Failed to read chunk {chunk_id}: {e}")
            return None
    
    def update_chunk(self, chunk_id: str, new_text: Optional[str] = None, 
                    new_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing chunk.
        
        Args:
            chunk_id: Unique chunk identifier
            new_text: New text content (optional)
            new_metadata: New metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing chunk
            existing = self.read_chunk(chunk_id)
            if not existing:
                logger.warning(f"Chunk not found for update: {chunk_id}")
                return False
            
            # Prepare update data
            update_text = new_text if new_text is not None else existing['document']
            update_metadata = existing['metadata'].copy()
            
            if new_metadata:
                update_metadata.update(self._prepare_metadata(new_metadata))
            
            # Update timestamp
            update_metadata['updated_at'] = datetime.now().isoformat()
            
            # Perform update
            self.collection.update(
                ids=[chunk_id],
                documents=[update_text],
                metadatas=[update_metadata]
            )
            
            logger.info(f"Updated chunk: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update chunk {chunk_id}: {e}")
            return False
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk from the database.
        
        Args:
            chunk_id: Unique chunk identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if chunk exists
            existing = self.read_chunk(chunk_id)
            if not existing:
                logger.warning(f"Chunk not found for deletion: {chunk_id}")
                return False
            
            # Delete chunk
            self.collection.delete(ids=[chunk_id])
            
            logger.info(f"Deleted chunk: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete chunk {chunk_id}: {e}")
            return False
    
    def search_similar(self, query: str, n_results: int = 5, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using semantic similarity.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of similar chunks with scores
        """
        try:
            # Prepare where clause for filtering
            where_clause = self._build_where_clause(filters)
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                        "similarity_score": 1 - results["distances"][0][i] if results.get("distances") else None
                    })
            
            logger.info(f"Found {len(formatted_results)} similar chunks for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {e}")
            return []
    
    def search_by_metadata(self, filters: Dict[str, Any], 
                          n_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search chunks by metadata filters.
        
        Args:
            filters: Metadata filters
            n_results: Maximum number of results
            
        Returns:
            List of matching chunks
        """
        try:
            where_clause = self._build_where_clause(filters)
            
            results = self.collection.get(
                where=where_clause,
                limit=n_results
            )
            
            formatted_results = []
            if results.get("documents"):
                for i, doc in enumerate(results["documents"]):
                    formatted_results.append({
                        "id": results["ids"][i],
                        "document": doc,
                        "metadata": results["metadatas"][i]
                    })
            
            logger.info(f"Found {len(formatted_results)} chunks matching metadata filters")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search by metadata: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive collection statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            count = self.collection.count()
            
            # Get sample of metadata to analyze
            sample_results = self.collection.get(limit=100)
            
            # Analyze metadata
            file_types = {}
            departments = {}
            keywords_count = 0
            
            if sample_results.get("metadatas"):
                for metadata in sample_results["metadatas"]:
                    file_type = metadata.get("file_type", "unknown")
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    
                    department = metadata.get("department", "unknown")
                    departments[department] = departments.get(department, 0) + 1
                    
                    keywords = metadata.get("keywords", [])
                    if isinstance(keywords, str):
                        try:
                            keywords = json.loads(keywords)
                        except:
                            keywords = []
                    keywords_count += len(keywords)
            
            return {
                "total_chunks": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory,
                "last_updated": datetime.now().isoformat(),
                "file_types": file_types,
                "departments": departments,
                "avg_keywords_per_chunk": keywords_count / max(count, 1),
                "sample_size": min(count, 100)
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def batch_create_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple chunks in a batch operation.
        
        Args:
            chunks_data: List of chunk data dictionaries
            
        Returns:
            List of created chunk IDs
        """
        try:
            if not chunks_data:
                return []
            
            documents = []
            metadatas = []
            ids = []
            
            for chunk_data in chunks_data:
                chunk_text = chunk_data.get("text", "")
                metadata = chunk_data.get("metadata", {})
                chunk_id = chunk_data.get("id") or self._generate_chunk_id(metadata)
                
                documents.append(chunk_text)
                metadatas.append(self._prepare_metadata(metadata))
                ids.append(chunk_id)
            
            # Batch add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Batch created {len(chunks_data)} chunks")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to batch create chunks: {e}")
            return []
    
    def batch_delete_chunks(self, chunk_ids: List[str]) -> int:
        """
        Delete multiple chunks in a batch operation.
        
        Args:
            chunk_ids: List of chunk IDs to delete
            
        Returns:
            Number of chunks successfully deleted
        """
        try:
            if not chunk_ids:
                return 0
            
            # Check which chunks exist
            existing_results = self.collection.get(ids=chunk_ids)
            existing_ids = existing_results.get("ids", [])
            
            if not existing_ids:
                logger.warning("No existing chunks found for batch deletion")
                return 0
            
            # Delete existing chunks
            self.collection.delete(ids=existing_ids)
            
            logger.info(f"Batch deleted {len(existing_ids)} chunks")
            return len(existing_ids)
            
        except Exception as e:
            logger.error(f"Failed to batch delete chunks: {e}")
            return 0
    
    def export_collection(self, output_file: str) -> bool:
        """
        Export collection data to JSON file.
        
        Args:
            output_file: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all chunks
            results = self.collection.get()
            
            export_data = {
                "collection_name": self.collection_name,
                "export_timestamp": datetime.now().isoformat(),
                "total_chunks": len(results.get("ids", [])),
                "chunks": []
            }
            
            if results.get("documents"):
                for i, doc in enumerate(results["documents"]):
                    chunk_data = {
                        "id": results["ids"][i],
                        "document": doc,
                        "metadata": results["metadatas"][i]
                    }
                    export_data["chunks"].append(chunk_data)
            
            # Write to file
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported collection to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export collection: {e}")
            return False
    
    def import_collection(self, input_file: str) -> int:
        """
        Import collection data from JSON file.
        
        Args:
            input_file: Input file path
            
        Returns:
            Number of chunks imported
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            chunks_data = import_data.get("chunks", [])
            if not chunks_data:
                logger.warning("No chunks found in import file")
                return 0
            
            # Import chunks
            imported_ids = self.batch_create_chunks(chunks_data)
            
            logger.info(f"Imported {len(imported_ids)} chunks from: {input_file}")
            return len(imported_ids)
            
        except Exception as e:
            logger.error(f"Failed to import collection: {e}")
            return 0
    
    def cleanup_old_chunks(self, days_old: int = 30) -> int:
        """
        Clean up old chunks based on creation date.
        
        Args:
            days_old: Number of days old to consider for cleanup
            
        Returns:
            Number of chunks cleaned up
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cutoff_iso = datetime.fromtimestamp(cutoff_date).isoformat()
            
            # Find old chunks
            old_chunks = self.search_by_metadata({
                "created_at": {"$lt": cutoff_iso}
            })
            
            if not old_chunks:
                logger.info("No old chunks found for cleanup")
                return 0
            
            # Delete old chunks
            old_ids = [chunk["id"] for chunk in old_chunks]
            deleted_count = self.batch_delete_chunks(old_ids)
            
            logger.info(f"Cleaned up {deleted_count} old chunks")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old chunks: {e}")
            return 0
    
    def _generate_chunk_id(self, metadata: Dict[str, Any]) -> str:
        """
        Generate a unique chunk ID.
        
        Args:
            metadata: Chunk metadata
            
        Returns:
            Unique chunk ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = metadata.get("file_name", "unknown")
        chunk_index = metadata.get("chunk_index", 0)
        
        return f"{timestamp}_{file_name}_chunk{chunk_index}_{str(uuid.uuid4())[:8]}"
    
    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata for ChromaDB storage.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Prepared metadata dictionary
        """
        prepared = {}
        
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                prepared[key] = json.dumps(value)
            elif isinstance(value, (int, float, str, bool)):
                prepared[key] = str(value)
            else:
                prepared[key] = str(value)
        
        # Add timestamps
        prepared["created_at"] = datetime.now().isoformat()
        prepared["updated_at"] = datetime.now().isoformat()
        
        return prepared
    
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Build ChromaDB where clause from filters.
        
        Args:
            filters: Filter dictionary
            
        Returns:
            ChromaDB where clause or None
        """
        if not filters:
            return None
        
        where_clause = {}
        
        for key, value in filters.items():
            if isinstance(value, dict):
                # Handle operators like $gt, $lt, etc.
                where_clause[key] = value
            else:
                # Simple equality
                where_clause[key] = value
        
        return where_clause if where_clause else None

# Convenience functions
def create_chromadb_manager(persist_directory: str = "./chroma_db") -> ChromaDBManager:
    """
    Create ChromaDB manager instance.
    
    Args:
        persist_directory: Directory to persist ChromaDB database
        
    Returns:
        ChromaDBManager instance
    """
    return ChromaDBManager(persist_directory=persist_directory)

# Example usage
if __name__ == "__main__":
    # Initialize ChromaDB manager
    manager = create_chromadb_manager()
    
    # Create a test chunk
    test_metadata = {
        "file_name": "test_document.md",
        "file_type": ".md",
        "chunk_index": 1,
        "department": "admin",
        "keywords": ["test", "example", "document"]
    }
    
    chunk_id = manager.create_chunk(
        "This is a test document chunk for ChromaDB operations.",
        test_metadata
    )
    
    print(f"Created chunk: {chunk_id}")
    
    # Search for similar chunks
    results = manager.search_similar("test document", n_results=3)
    print(f"Found {len(results)} similar chunks")
    
    # Get collection stats
    stats = manager.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    print("ChromaDB CRUD operations test completed successfully!")
