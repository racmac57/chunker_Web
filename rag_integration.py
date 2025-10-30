"""
RAG Integration Module for Chunker_v2
Handles retrieval-augmented generation with ChromaDB and Ollama embeddings
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class ChromaRAG:
    """
    ChromaDB-based RAG implementation for knowledge base management
    Provides CRUD operations for vector database with hybrid search
    """
    
    def __init__(self, persist_directory="./chroma_db"):
        """
        Initialize ChromaDB client and collection
        
        Args:
            persist_directory: Directory to persist ChromaDB database
        """
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection for chunker knowledge base
        self.collection = self.client.get_or_create_collection(
            name="chunker_knowledge_base",
            metadata={"description": "Enterprise chunker knowledge base with RAG capabilities"}
        )
        
        logger.info(f"Initialized ChromaDB collection with {self.collection.count()} existing chunks")
    
    def add_chunk(self, chunk_text: str, metadata: Dict[str, Any]) -> str:
        """
        Add a chunk to the vector database
        
        Args:
            chunk_text: The text content of the chunk
            metadata: Dictionary containing chunk metadata
        
        Returns:
            chunk_id: Unique identifier for the added chunk
        """
        # Generate unique chunk ID
        chunk_id = f"{metadata['timestamp']}_{metadata['file_name']}_chunk{metadata['chunk_index']}"
        
        # Prepare metadata for ChromaDB (ensure values are serializable)
        chroma_metadata = {
            "file_name": metadata["file_name"],
            "file_type": metadata["file_type"],
            "chunk_index": str(metadata["chunk_index"]),
            "timestamp": metadata["timestamp"],
            "department": metadata.get("department", "admin"),
            "keywords": json.dumps(metadata.get("keywords", [])),
            "file_size": str(metadata.get("file_size", 0)),
            "processing_time": str(metadata.get("processing_time", 0))
        }
        
        try:
            # Add to collection
            self.collection.add(
                documents=[chunk_text],
                metadatas=[chroma_metadata],
                ids=[chunk_id]
            )
            
            logger.info(f"Added chunk to ChromaDB: {chunk_id}")
            return chunk_id
            
        except Exception as e:
            logger.error(f"Failed to add chunk to ChromaDB: {e}")
            raise
    
    def search_similar(self, query: str, n_results: int = 5, 
                       file_type: Optional[str] = None, 
                       department: Optional[str] = None) -> List[Dict]:
        """
        Search for similar chunks using semantic similarity
        
        Args:
            query: Search query text
            n_results: Number of results to return
            file_type: Filter by file type (optional)
            department: Filter by department (optional)
        
        Returns:
            List of formatted search results
        """
        where_clause = {}
        
        if file_type:
            where_clause["file_type"] = file_type
        if department:
            where_clause["department"] = department
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            return self._format_results(results)
            
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {e}")
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

