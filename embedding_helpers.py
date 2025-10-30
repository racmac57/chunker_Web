"""
Embedding Helpers for Chunker_v2
Utilities for generating, storing, and managing embeddings
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """
    Manages embedding generation, storage, and retrieval for chunks.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize embedding manager.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def generate_chunk_metadata(self, chunk: str, filename: str, file_type: str, 
                               timestamp: str, index: int, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive metadata for a chunk.
        
        Args:
            chunk: Text content of the chunk
            filename: Source filename
            file_type: File extension
            timestamp: Processing timestamp
            index: Chunk index within file
            keywords: Extracted keywords
            
        Returns:
            Metadata dictionary
        """
        return {
            "source_file": filename,
            "file_type": file_type,
            "chunk_index": index,
            "timestamp": timestamp,
            "keywords": keywords or [],
            "chunk_size": len(chunk),
            "word_count": len(chunk.split()),
            "sentence_count": len([s for s in chunk.split('.') if s.strip()]),
            "processing_date": datetime.now().isoformat()
        }
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks using the configured splitter.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        try:
            chunks = self.splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to split text: {e}")
            return [text]  # Fallback to single chunk
    
    def create_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[Document]:
        """
        Create LangChain Document objects from texts and metadata.
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
            
        Returns:
            List of Document objects
        """
        try:
            documents = []
            for text, metadata in zip(texts, metadatas):
                doc = Document(page_content=text, metadata=metadata)
                documents.append(doc)
            
            logger.info(f"Created {len(documents)} Document objects")
            return documents
        except Exception as e:
            logger.error(f"Failed to create documents: {e}")
            return []
    
    def extract_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File metadata dictionary
        """
        try:
            stat = file_path.stat()
            return {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_extension": file_path.suffix.lower(),
                "is_binary": self._is_binary_file(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to extract file metadata: {e}")
            return {}
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is binary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if binary, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except Exception:
            return False
    
    def save_metadata(self, metadata: Dict[str, Any], output_path: str) -> None:
        """
        Save metadata to JSON file.
        
        Args:
            metadata: Metadata dictionary
            output_path: Output file path
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved metadata to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def load_metadata(self, input_path: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata from JSON file.
        
        Args:
            input_path: Input file path
            
        Returns:
            Metadata dictionary or None if failed
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            logger.info(f"Loaded metadata from {input_path}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return None

def generate_chunk_metadata(chunk: str, filename: str, file_type: str, 
                           timestamp: str, index: int, keywords: List[str] = None) -> Dict[str, Any]:
    """
    Generate metadata for a chunk (convenience function).
    
    Args:
        chunk: Text content of the chunk
        filename: Source filename
        file_type: File extension
        timestamp: Processing timestamp
        index: Chunk index within file
        keywords: Extracted keywords
        
    Returns:
        Metadata dictionary
    """
    manager = EmbeddingManager()
    return manager.generate_chunk_metadata(chunk, filename, file_type, timestamp, index, keywords)

def save_embeddings(vectorstore, path: str = "faiss_index") -> None:
    """
    Save FAISS index to disk.
    
    Args:
        vectorstore: FAISS vector store
        path: Directory path to save to
    """
    try:
        os.makedirs(path, exist_ok=True)
        vectorstore.save_local(path)
        logger.info(f"Saved FAISS index to {path}")
    except Exception as e:
        logger.error(f"Failed to save FAISS index: {e}")
        raise

def load_embeddings(embeddings, path: str = "faiss_index"):
    """
    Load FAISS index from disk.
    
    Args:
        embeddings: Embeddings object
        path: Directory path to load from
        
    Returns:
        Loaded FAISS vector store
    """
    try:
        if os.path.exists(path):
            from langchain_community.vectorstores import FAISS
            vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
            logger.info(f"Loaded FAISS index from {path}")
            return vectorstore
        else:
            logger.warning(f"No FAISS index found at {path}")
            return None
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        return None

def create_embedding_index(texts: List[str], metadatas: List[Dict[str, Any]], 
                          embeddings, output_path: str = "faiss_index") -> None:
    """
    Create and save FAISS index from texts and metadata.
    
    Args:
        texts: List of text chunks
        metadatas: List of metadata dictionaries
        embeddings: Embeddings object
        output_path: Directory path to save to
    """
    try:
        from langchain_community.vectorstores import FAISS
        
        # Create FAISS index
        vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
        
        # Save to disk
        save_embeddings(vectorstore, output_path)
        
        logger.info(f"Created FAISS index with {len(texts)} documents")
        
    except Exception as e:
        logger.error(f"Failed to create embedding index: {e}")
        raise

def batch_process_files(file_paths: List[Path], embedding_manager: EmbeddingManager, 
                       extract_keywords_func) -> List[Dict[str, Any]]:
    """
    Batch process multiple files for embedding.
    
    Args:
        file_paths: List of file paths to process
        embedding_manager: EmbeddingManager instance
        extract_keywords_func: Function to extract keywords from text
        
    Returns:
        List of processed file results
    """
    results = []
    
    for file_path in file_paths:
        try:
            # Extract file metadata
            file_metadata = embedding_manager.extract_file_metadata(file_path)
            
            # Read file content
            if file_metadata.get("is_binary", False):
                logger.warning(f"Skipping binary file: {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Split into chunks
            chunks = embedding_manager.split_text(content)
            
            # Generate metadata for each chunk
            timestamp = datetime.now().isoformat()
            chunk_metadatas = []
            
            for i, chunk in enumerate(chunks):
                keywords = extract_keywords_func(chunk) if extract_keywords_func else []
                metadata = embedding_manager.generate_chunk_metadata(
                    chunk, file_path.name, file_path.suffix, timestamp, i, keywords
                )
                metadata.update(file_metadata)  # Add file-level metadata
                chunk_metadatas.append(metadata)
            
            results.append({
                "file_path": str(file_path),
                "chunks": chunks,
                "metadatas": chunk_metadatas,
                "file_metadata": file_metadata,
                "success": True
            })
            
            logger.info(f"Processed {file_path.name}: {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            results.append({
                "file_path": str(file_path),
                "chunks": [],
                "metadatas": [],
                "file_metadata": {},
                "success": False,
                "error": str(e)
            })
    
    return results

# Example usage
if __name__ == "__main__":
    # Initialize embedding manager
    manager = EmbeddingManager(chunk_size=500, chunk_overlap=50)
    
    # Example text
    sample_text = """
    This is a sample document for testing the embedding manager.
    It contains multiple sentences and paragraphs to demonstrate
    how text splitting and metadata generation works.
    
    The system should handle various file types and extract
    meaningful metadata for each chunk.
    """
    
    # Split text
    chunks = manager.split_text(sample_text)
    print(f"Split into {len(chunks)} chunks")
    
    # Generate metadata
    timestamp = datetime.now().isoformat()
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        metadata = manager.generate_chunk_metadata(
            chunk, "sample.txt", ".txt", timestamp, i, ["sample", "test"]
        )
        metadatas.append(metadata)
    
    # Create documents
    documents = manager.create_documents(chunks, metadatas)
    print(f"Created {len(documents)} documents")
    
    # Save metadata
    manager.save_metadata({"chunks": metadatas}, "sample_metadata.json")
    
    print("Embedding manager test completed successfully!")
