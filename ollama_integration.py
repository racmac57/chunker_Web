"""
Ollama Integration for Chunker_v2
Provides local embeddings using Ollama with nomic-embed-text model
"""

import logging
import os
from typing import List, Dict, Any, Optional

import numpy as np

from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

try:
    from langchain_community.docstore import InMemoryDocstore
except ImportError:
    from langchain.docstore.in_memory import InMemoryDocstore

try:
    from langchain_community.retrievers import BM25Retriever
except ImportError:  # Backwards compatibility for older LangChain installs
    from langchain.retrievers import BM25Retriever

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

try:
    import faiss
except ImportError as exc:
    raise ImportError(
        "faiss (faiss-cpu) is required for OllamaRAGSystem. Please install it via "
        "`pip install faiss-cpu`."
    ) from exc

logger = logging.getLogger(__name__)

class OllamaRAGSystem:
    """
    RAG system using Ollama for local embeddings and FAISS for vector storage.
    Provides hybrid search combining semantic and keyword retrieval.
    """
    
    def __init__(self, model_name: str = "nomic-embed-text", persist_dir: str = "./faiss_index"):
        """
        Initialize Ollama RAG system.
        
        Args:
            model_name: Ollama embedding model to use
            persist_dir: Directory to persist FAISS index
        """
        self.model_name = model_name
        self.persist_dir = persist_dir
        self.embeddings = None
        self.vectorstore = None
        self.keyword_retriever = None
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self._embedding_dimension: Optional[int] = None
        
        self._initialize_ollama()
        self._initialize_vectorstore()
    
    def _initialize_ollama(self) -> None:
        """Initialize Ollama embeddings."""
        try:
            self.embeddings = OllamaEmbeddings(model=self.model_name)
            logger.info(f"Initialized Ollama embeddings with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama embeddings: {e}")
            raise
    
    def _initialize_vectorstore(self) -> None:
        """Initialize FAISS vector store."""
        try:
            embedding_dimension = self._get_embedding_dimension()
            index = faiss.IndexFlatL2(embedding_dimension)
            self.vectorstore = FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=InMemoryDocstore({}),
                index_to_docstore_id={},
            )
            logger.info("Initialized FAISS vector store")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS vector store: {e}")
            raise

    def _get_embedding_dimension(self) -> int:
        """Determine embedding dimension for FAISS index."""
        if self._embedding_dimension is None:
            test_vector = self.embeddings.embed_query("dimension probe")
            self._embedding_dimension = len(test_vector)
            logger.debug("Determined embedding dimension: %d", self._embedding_dimension)
        return self._embedding_dimension
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
        """
        try:
            # Add to FAISS
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            
            # Update BM25 retriever
            self.keyword_retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
            
            # Store for persistence
            self.documents.extend(texts)
            self.metadatas.extend(metadatas)
            
            logger.info(f"Added {len(texts)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword retrieval.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            # Semantic search
            vector_results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            # Keyword search
            keyword_results = []
            if self.keyword_retriever:
                keyword_results = self.keyword_retriever.get_relevant_documents(query)[:top_k]
            
            # Combine and deduplicate results
            combined_results = []
            seen_content = set()
            
            # Add vector results
            for doc, score in vector_results:
                if doc.page_content not in seen_content:
                    combined_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score),
                        "type": "semantic"
                    })
                    seen_content.add(doc.page_content)
            
            # Add keyword results
            for doc in keyword_results:
                if doc.page_content not in seen_content:
                    combined_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": 0.0,  # BM25 doesn't provide scores in this implementation
                        "type": "keyword"
                    })
                    seen_content.add(doc.page_content)
            
            # Sort by score (higher is better for semantic, lower is better for FAISS distance)
            combined_results.sort(key=lambda x: x["score"], reverse=True)
            
            return combined_results[:top_k]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                    "type": "semantic"
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def search_by_keywords(self, keywords: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search by specific keywords using BM25.
        
        Args:
            keywords: List of keywords to search for
            top_k: Number of results to return
            
        Returns:
            List of documents matching keywords
        """
        try:
            if not self.keyword_retriever:
                return []
            
            query = " ".join(keywords)
            results = self.keyword_retriever.get_relevant_documents(query)[:top_k]
            
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 0.0,
                    "type": "keyword"
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def save_index(self) -> None:
        """Save FAISS index to disk."""
        try:
            os.makedirs(self.persist_dir, exist_ok=True)
            self.vectorstore.save_local(self.persist_dir)
            logger.info(f"Saved FAISS index to {self.persist_dir}")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def load_index(self) -> bool:
        """
        Load FAISS index from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.persist_dir):
                self.vectorstore = FAISS.load_local(
                    self.persist_dir,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )

                # Rehydrate documents and BM25 retriever from stored docstore
                if hasattr(self.vectorstore, "docstore") and getattr(self.vectorstore.docstore, "_dict", None):
                    documents = list(self.vectorstore.docstore._dict.values())
                    self.documents = [doc.page_content for doc in documents]
                    self.metadatas = [doc.metadata for doc in documents]

                    if documents:
                        try:
                            self.keyword_retriever = BM25Retriever.from_documents(documents)
                        except AttributeError:
                            self.keyword_retriever = BM25Retriever.from_texts(
                                self.documents,
                                metadatas=self.metadatas
                            )

                logger.info(f"Loaded FAISS index from {self.persist_dir}")
                return True
            else:
                logger.info("No existing index found, starting fresh")
                return False
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            count = self.vectorstore.index.ntotal if self.vectorstore.index else 0
            return {
                "total_documents": count,
                "model_name": self.model_name,
                "persist_dir": self.persist_dir,
                "has_keyword_retriever": self.keyword_retriever is not None
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

def initialize_ollama_rag(model_name: str = "nomic-embed-text", persist_dir: str = "./faiss_index") -> OllamaRAGSystem:
    """
    Initialize Ollama RAG system.
    
    Args:
        model_name: Ollama embedding model to use
        persist_dir: Directory to persist FAISS index
        
    Returns:
        Initialized OllamaRAGSystem instance
    """
    return OllamaRAGSystem(model_name=model_name, persist_dir=persist_dir)

def check_ollama_availability() -> bool:
    """
    Check if Ollama is available and the model is installed.
    
    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        # Try a simple embedding to test
        test_embedding = embeddings.embed_query("test")
        return len(test_embedding) > 0
    except Exception as e:
        logger.warning(f"Ollama not available: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = initialize_ollama_rag()
    
    # Add some test documents
    test_docs = [
        "VLOOKUP is used to find values in Excel tables.",
        "Power BI uses M language for data transformation.",
        "Python pandas is great for data analysis."
    ]
    
    test_metadata = [
        {"source": "excel_guide.md", "topic": "excel"},
        {"source": "powerbi_guide.md", "topic": "powerbi"},
        {"source": "python_guide.md", "topic": "python"}
    ]
    
    rag.add_documents(test_docs, test_metadata)
    
    # Search
    results = rag.hybrid_search("How do I use vlookup?", top_k=3)
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"- {result['content'][:50]}... (score: {result['score']:.3f})")
    
    # Save index
    rag.save_index()
    
    # Get stats
    stats = rag.get_stats()
    print(f"Vector store stats: {stats}")
