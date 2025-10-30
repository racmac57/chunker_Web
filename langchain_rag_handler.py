"""
Enhanced RAG Handler with LangChain Integration
Provides better retrieval orchestration and error handling
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import Ollama

logger = logging.getLogger(__name__)


class LangChainRAGHandler:
    """
    Enhanced RAG handler using LangChain patterns
    Provides better orchestration and error handling
    """
    
    def __init__(self, config_path="config.json", embeddings=None, llm=None):
        """
        Initialize LangChain RAG handler with error handling
        
        Args:
            config_path: Path to config file
            embeddings: Optional pre-initialized embeddings
            llm: Optional pre-initialized LLM
        """
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}
        
        # Initialize components with error handling
        self.embeddings = embeddings or self._init_embeddings()
        self.llm = llm or self._init_llm()
        self.vectorstore = self._init_vectorstore()
        self.retriever = None
        self.qa_chain = None
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("chunk_size", 800),
            chunk_overlap=config.get("overlap", 50)
        )
    
    def _init_embeddings(self):
        """Initialize embeddings with error handling"""
        try:
            # Try to use Ollama for local embeddings
            if self.config.get("use_local_embeddings", True):
                logger.info("Initializing Ollama embeddings...")
                return OllamaEmbeddings(model="nomic-embed-text")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama embeddings: {e}")
            logger.info("Falling back to alternative embeddings...")
        
        # Fallback to default (would need actual implementation)
        return None
    
    def _init_llm(self):
        """Initialize LLM with error handling"""
        try:
            if self.config.get("use_local_llm", True):
                logger.info("Initializing Ollama LLM...")
                return Ollama(model="llama3.2")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}")
        
        return None
    
    def _init_vectorstore(self):
        """Initialize vector store with error handling"""
        try:
            persist_directory = self.config.get("chroma_persist_dir", "./chroma_db")
            
            if self.embeddings:
                vectorstore = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=self.embeddings
                )
                logger.info("Initialized ChromaDB vector store")
                return vectorstore
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
        
        return None
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """
        Add documents to vector store with error handling
        
        Args:
            texts: List of text documents
            metadatas: List of metadata dictionaries
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized")
            return False
        
        try:
            # Split texts into chunks
            all_chunks = []
            all_metadata = []
            
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                all_chunks.extend(chunks)
                
                if metadatas:
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    for _ in range(len(chunks)):
                        all_metadata.append(metadata)
            
            # Add to vector store
            self.vectorstore.add_texts(
                texts=all_chunks,
                metadatas=all_metadata if all_metadata else None
            )
            
            logger.info(f"Added {len(all_chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def search(self, query: str, k: int = 5, **kwargs):
        """
        Search with error handling and recovery
        
        Args:
            query: Search query
            k: Number of results
            **kwargs: Additional search parameters
        
        Returns:
            Search results or empty list on error
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized")
            return []
        
        try:
            results = self.vectorstore.similarity_search(query, k=k, **kwargs)
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def create_retrieval_chain(self):
        """
        Create LangChain retrieval QA chain
        
        Returns:
            QA chain or None if LLM not available
        """
        if not self.vectorstore or not self.llm:
            logger.warning("Cannot create retrieval chain - missing components")
            return None
        
        try:
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True
            )
            
            logger.info("Created retrieval QA chain")
            return self.qa_chain
            
        except Exception as e:
            logger.error(f"Failed to create retrieval chain: {e}")
            return None
    
    def query(self, question: str):
        """
        Query the RAG system with error handling
        
        Args:
            question: Query question
        
        Returns:
            Answer with sources or error message
        """
        if not self.qa_chain:
            self.create_retrieval_chain()
        
        if not self.qa_chain:
            return {
                "answer": "Unable to process query - components not initialized",
                "sources": []
            }
        
        try:
            result = self.qa_chain({"query": question})
            return {
                "answer": result.get("result", ""),
                "sources": result.get("source_documents", [])
            }
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": []
            }


def graceful_rag_handler(func):
    """
    Decorator for graceful RAG error handling
    
    Usage:
        @graceful_rag_handler
        def process_with_rag(...):
            ...
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            logger.warning(f"RAG dependencies not installed: {e}")
            logger.info("Continuing without RAG functionality")
            return None
        except Exception as e:
            logger.error(f"RAG operation failed: {e}")
            return None
    return wrapper


def check_rag_dependencies():
    """
    Check if RAG dependencies are installed
    
    Returns:
        Dictionary with dependency status
    """
    dependencies = {
        "chromadb": False,
        "langchain": False,
        "langchain_community": False,
        "ollama": False
    }
    
    try:
        import chromadb
        dependencies["chromadb"] = True
    except ImportError:
        pass
    
    try:
        import langchain
        dependencies["langchain"] = True
    except ImportError:
        pass
    
    try:
        import langchain_community
        dependencies["langchain_community"] = True
    except ImportError:
        pass
    
    try:
        import ollama
        dependencies["ollama"] = True
    except ImportError:
        pass
    
    return dependencies


if __name__ == "__main__":
    # Test dependency checking
    deps = check_rag_dependencies()
    print("RAG Dependency Status:")
    for dep, status in deps.items():
        print(f"  {dep}: {'✓' if status else '✗'}")
    
    # Test handler initialization
    if all(deps.values()):
        print("\nInitializing LangChain RAG handler...")
        handler = LangChainRAGHandler()
        print("Handler initialized successfully")
    else:
        print("\nCannot initialize handler - missing dependencies")
