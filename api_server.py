"""
FastAPI REST Interface for ChromaDB Knowledge Base Access
Provides API endpoints for AI systems (Claude, GPT, etc.) to query the knowledge base

Version: 2.1.6
Author: R. A. Carucci
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import time
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Import RAG integration
try:
    from rag_integration import ChromaRAG
except ImportError:
    logger.error("Failed to import ChromaRAG. Make sure rag_integration.py exists.")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Chunker RAG API",
    description="REST API for ChromaDB knowledge base search and retrieval",
    version="2.1.6",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize RAG system
try:
    rag = ChromaRAG(persist_directory="./chroma_db")
    logger.info("ChromaRAG initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ChromaRAG: {e}", exc_info=True)
    rag = None

# Request/Response Models
class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., description="Search query text", min_length=1)
    n_results: int = Field(5, ge=1, le=50, description="Number of results to return")
    file_type: Optional[str] = Field(None, description="Filter by file type (e.g., '.txt', '.md')")
    department: Optional[str] = Field(None, description="Filter by department (e.g., 'admin', 'police', 'legal')")
    ef_search: Optional[int] = Field(None, ge=100, le=500, description="HNSW ef_search parameter (higher = more accurate, slower)")

class SearchResult(BaseModel):
    """Individual search result model"""
    id: str
    content: str
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float

class StatsResponse(BaseModel):
    """Statistics response model"""
    total_chunks: int
    collection_name: str
    last_updated: str

class ContextRequest(BaseModel):
    """Context request for LLM prompts"""
    query: str = Field(..., description="Query for context retrieval")
    max_chunks: int = Field(3, ge=1, le=10, description="Maximum chunks to retrieve")
    min_score: float = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity score")
    file_type: Optional[str] = None
    department: Optional[str] = None

class ContextResponse(BaseModel):
    """Formatted context for LLM prompts"""
    query: str
    sources: List[Dict[str, Any]]
    formatted_context: str
    chunk_count: int

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Chunker RAG API",
        "version": "2.1.6",
        "status": "operational" if rag else "error",
        "endpoints": {
            "search": "POST /api/search",
            "chunk": "GET /api/chunk/{chunk_id}",
            "stats": "GET /api/stats",
            "context": "POST /api/context",
            "health": "GET /api/health"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search the knowledge base with semantic similarity
    
    - **query**: Search query text
    - **n_results**: Number of results (1-50)
    - **file_type**: Optional filter by file type
    - **department**: Optional filter by department
    - **ef_search**: Optional HNSW ef_search parameter (100-500)
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = time.time()
    
    try:
        # Perform search
        results = rag.search_similar(
            query=request.query,
            n_results=request.n_results,
            file_type=request.file_type,
            department=request.department,
            ef_search=request.ef_search
        )
        
        # Format results
        formatted_results = []
        for r in results:
            # Convert distance to similarity score (ChromaDB returns distance, we want similarity)
            distance = r.get("distance", 1.0)
            score = max(0.0, min(1.0, 1.0 - distance))  # Clamp to 0-1
            
            formatted_results.append(
                SearchResult(
                    id=r["id"],
                    content=r["document"],
                    score=score,
                    metadata=r["metadata"]
                )
            )
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/chunk/{chunk_id}")
async def get_chunk(chunk_id: str):
    """
    Retrieve a specific chunk by ID
    
    - **chunk_id**: Unique chunk identifier
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        chunk = rag.get_chunk_by_id(chunk_id)
        if not chunk:
            raise HTTPException(status_code=404, detail=f"Chunk not found: {chunk_id}")
        return chunk
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chunk retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get knowledge base statistics
    
    Returns total chunks, collection name, and last updated timestamp
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        stats = rag.get_collection_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.post("/api/context", response_model=ContextResponse)
async def get_context(request: ContextRequest):
    """
    Get formatted context for LLM prompts (RAG workflow)
    
    Returns context formatted for use in AI prompts with source attribution
    
    - **query**: Query for context retrieval
    - **max_chunks**: Maximum chunks to retrieve (1-10)
    - **min_score**: Minimum similarity score (0.0-1.0)
    - **file_type**: Optional file type filter
    - **department**: Optional department filter
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Search for relevant chunks
        results = rag.search_similar(
            query=request.query,
            n_results=request.max_chunks,
            file_type=request.file_type,
            department=request.department
        )
        
        # Filter by minimum score and format
        sources = []
        filtered_results = []
        
        for r in results:
            distance = r.get("distance", 1.0)
            score = max(0.0, min(1.0, 1.0 - distance))
            
            if score >= request.min_score:
                metadata = r.get("metadata", {})
                source_info = {
                    "content": r["document"],
                    "source": metadata.get("file_name", "unknown"),
                    "file_type": metadata.get("file_type", "unknown"),
                    "department": metadata.get("department", "unknown"),
                    "relevance": score,
                    "chunk_id": r["id"]
                }
                sources.append(source_info)
                filtered_results.append(r)
        
        # Format context for LLM prompts
        formatted_parts = []
        for r in filtered_results:
            metadata = r.get("metadata", {})
            file_name = metadata.get("file_name", "unknown")
            content = r["document"]
            formatted_parts.append(f"[Source: {file_name}]\n{content}")
        
        formatted_context = "\n\n---\n\n".join(formatted_parts)
        
        return ContextResponse(
            query=request.query,
            sources=sources,
            formatted_context=formatted_context,
            chunk_count=len(sources)
        )
        
    except Exception as e:
        logger.error(f"Context generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Context error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    
    Returns API and ChromaDB connection status
    """
    try:
        if not rag:
            return {
                "status": "unhealthy",
                "api": "operational",
                "chromadb": "not_initialized",
                "error": "RAG system not initialized"
            }
        
        stats = rag.get_collection_stats()
        return {
            "status": "healthy",
            "api": "operational",
            "chromadb": "connected",
            "chunks": stats["total_chunks"],
            "collection": stats["collection_name"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api": "operational",
            "chromadb": "error",
            "error": str(e)
        }

# Additional utility endpoints

@app.get("/api/search/keywords")
async def search_by_keywords(
    keywords: str = Query(..., description="Comma-separated keywords"),
    n_results: int = Query(5, ge=1, le=50)
):
    """
    Search by keywords (keyword-based search)
    
    - **keywords**: Comma-separated list of keywords
    - **n_results**: Number of results to return
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        keyword_list = [k.strip() for k in keywords.split(",")]
        results = rag.search_by_keywords(keyword_list, n_results=n_results)
        
        formatted_results = [
            SearchResult(
                id=r["id"],
                content=r["document"],
                score=1.0 - r.get("distance", 0.0),
                metadata=r["metadata"]
            )
            for r in results
        ]
        
        return SearchResponse(
            query=f"Keywords: {keywords}",
            results=formatted_results,
            total_results=len(formatted_results),
            search_time_ms=0.0  # Could add timing if needed
        )
    except Exception as e:
        logger.error(f"Keyword search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Keyword search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Chunker RAG API Server...")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Alternative docs: http://localhost:8000/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

