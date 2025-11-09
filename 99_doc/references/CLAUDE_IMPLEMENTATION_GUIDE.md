# Claude Implementation Guide: API & GUI

## Overview

Based on Claude's recommendations, we've implemented:
1. **FastAPI REST API** - For AI system access
2. **Streamlit GUI** - For user-friendly knowledge base management

## Files Created

### 1. `api_server.py` - FastAPI REST API
- REST endpoints for knowledge base access
- CORS enabled for web clients
- OpenAPI/Swagger documentation
- Ready for Claude/GPT integration

### 2. `gui_app.py` - Streamlit GUI
- Modern web-based interface
- Search, statistics, browse, and status pages
- Export functionality (JSON, CSV)
- Real-time search results

### 3. `requirements_api_gui.txt` - Additional Dependencies
- FastAPI, uvicorn, pydantic
- Streamlit, pandas

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_api_gui.txt
```

### 2. Start API Server

```bash
python api_server.py
```

**Access:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 3. Start GUI Application

```bash
streamlit run gui_app.py
```

**Access:** http://localhost:8501

## API Endpoints

### Search Knowledge Base
```bash
POST /api/search
Content-Type: application/json

{
  "query": "Excel vlookup errors",
  "n_results": 5,
  "file_type": ".xlsx",
  "department": "admin",
  "ef_search": 200
}
```

### Get Context for LLM
```bash
POST /api/context
Content-Type: application/json

{
  "query": "How to fix Excel formulas?",
  "max_chunks": 3,
  "min_score": 0.7
}
```

### Get Statistics
```bash
GET /api/stats
```

### Get Specific Chunk
```bash
GET /api/chunk/{chunk_id}
```

### Health Check
```bash
GET /api/health
```

## Using with Claude/GPT

### Claude API Integration Example

```python
import requests

# Search knowledge base
response = requests.post(
    "http://localhost:8000/api/search",
    json={
        "query": "Excel vlookup errors",
        "n_results": 5
    }
)

results = response.json()
for result in results["results"]:
    print(f"Score: {result['score']:.2f}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Source: {result['metadata']['file_name']}")
```

### Get Context for RAG Prompt

```python
response = requests.post(
    "http://localhost:8000/api/context",
    json={
        "query": "How to fix Excel formulas?",
        "max_chunks": 3,
        "min_score": 0.7
    }
)

context = response.json()
formatted_context = context["formatted_context"]

# Use in Claude prompt
prompt = f"""
Context from knowledge base:
{formatted_context}

Question: {context["query"]}
"""
```

## GUI Features

### Search Page
- Semantic and keyword search
- Advanced filters (file type, department)
- Real-time results with relevance scores
- Export to JSON/CSV

### Statistics Page
- Total chunks count
- Distribution by department
- Distribution by file type
- Metadata summary

### Browse Page
- Paginated chunk browsing
- Filter by department/file type
- View full chunk content
- Copy chunk IDs

### System Status Page
- ChromaDB connection status
- HNSW index information
- Configuration viewer
- Test query functionality

## Next Steps

1. **Test API**: Try the endpoints with Postman or curl
2. **Test GUI**: Run Streamlit and explore the interface
3. **Integrate with Claude**: Use the API endpoints in your Claude workflows
4. **Customize**: Adjust UI/UX based on your preferences
5. **Add Authentication**: Implement API keys if needed for production

## Production Considerations

1. **Authentication**: Add API key authentication for `/api/*` endpoints
2. **Rate Limiting**: Implement rate limiting for API requests
3. **CORS**: Restrict CORS origins in production
4. **Error Handling**: Enhanced error messages and logging
5. **Monitoring**: Add metrics and monitoring endpoints

## Support

- **API Docs**: http://localhost:8000/docs
- **GUI Help**: See sidebar tips in the Streamlit app
- **Configuration**: Edit `config.json` for settings

