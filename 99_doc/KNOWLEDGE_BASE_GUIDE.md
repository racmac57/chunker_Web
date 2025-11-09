# Claude Knowledge Base Guide

## Overview

The Claude Knowledge Base system converts your Claude conversation exports into a searchable, semantic database with vector embeddings for intelligent information retrieval.

## Features

### 1. Semantic Chunking
- Intelligent text chunking (150 words max, sentence-aware)
- Preserves semantic boundaries using NLTK
- Handles code blocks and technical content

### 2. Search Capabilities
- **Keyword Search (FTS5)**: Traditional full-text search
- **Semantic Search (Vector)**: AI-powered meaning-based search
- **Hybrid Search**: Combines both for best results

### 3. Organization
- Automatic tag extraction (tech keywords, dates, content types)
- File/attachment indexing with extracted content
- Conversation metadata tracking

### 4. Performance
- Batch embedding generation
- Optimized SQLite indexes
- ~18,354 chunks processed in ~17 seconds (401 conversations)
- Database size: ~194 MB with embeddings

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# This installs:
# - nltk (sentence tokenization)
# - sentence-transformers (vector embeddings)
# - numpy (similarity calculations)
```

## Quick Start

### Build a Knowledge Base

```bash
# From conversations.json
python claude_knowledge_base.py conversations.json

# From ZIP export
python claude_knowledge_base.py export.zip my_kb.db

# Without embeddings (keyword search only)
python -c "from claude_knowledge_base import *; kb = ClaudeKnowledgeBase('my_kb.db', use_embeddings=False); ..."
```

### Query the Knowledge Base

**Interactive Mode:**
```bash
python claude_kb_query.py my_kb.db --interactive

# Commands:
> search power bi dax measures
> semantic python arcgis automation
> hybrid data analysis techniques
> filter tag=python
> filter after=2025-01-01
> export results.md
> quit
```

**CLI Mode:**
```bash
# Keyword search
python claude_kb_query.py my_kb.db "power bi dax measures"

# Semantic search
python claude_kb_query.py my_kb.db --semantic "python automation"

# Hybrid search with filters
python claude_kb_query.py my_kb.db --hybrid "data analysis" --tag python --after 2025-01-01 --limit 10

# Export results
python claude_kb_query.py my_kb.db "sql query" --export results.json

# Show conversation context
python claude_kb_query.py my_kb.db "error handling" --context
```

## Search Modes Explained

### Keyword Search (FTS5)
**Best for**: Exact terms, technical names, specific phrases

```bash
python claude_kb_query.py my_kb.db "Power BI DAX"
```

- Uses SQLite FTS5 full-text search
- Fast and precise
- Finds exact word matches
- Good for: function names, error messages, specific technologies

### Semantic Search (Vector)
**Best for**: Concepts, meanings, related ideas

```bash
python claude_kb_query.py my_kb.db --semantic "automating GIS workflows"
```

- Uses AI embeddings (all-MiniLM-L6-v2)
- Finds semantically similar content
- Understands synonyms and context
- Good for: "How do I...", conceptual questions, topic exploration

**Examples:**
- Query: "automate data pipelines" → Finds: "scheduled ETL processes", "workflow automation"
- Query: "visualize geographic data" → Finds: "mapping with ArcGIS", "spatial data display"

### Hybrid Search (Combined)
**Best for**: General use, complex queries

```bash
python claude_kb_query.py my_kb.db --hybrid "python data transformation"
```

- Combines keyword + semantic search
- Default weight: 50% keyword, 50% semantic
- Balances precision and recall
- Best overall results for most queries

## Filtering

### By Tags
```bash
# Single tag
python claude_kb_query.py my_kb.db "query" --tag python

# Multiple tags (OR logic)
python claude_kb_query.py my_kb.db "query" --tag python --tag sql
```

**Auto-extracted tags:**
- Technology: `python`, `javascript`, `sql`, `power-bi`, `arcgis`
- Activity: `code-review`, `refactoring`, `troubleshooting`, `automation`
- Content: `has-code`, `has-attachments`
- Date: `year-2025`, `month-2025-01`

### By Date
```bash
# After date (inclusive)
python claude_kb_query.py my_kb.db "query" --after 2025-01-01

# Before date (inclusive)
python claude_kb_query.py my_kb.db "query" --before 2025-10-26

# Date range
python claude_kb_query.py my_kb.db "query" --after 2025-01-01 --before 2025-10-26
```

## Export Formats

### Markdown (Default)
```bash
python claude_kb_query.py my_kb.db "query" --export results.md
```
- Formatted for readability
- Includes scores, tags, snippets
- Good for documentation

### JSON
```bash
python claude_kb_query.py my_kb.db "query" --export results.json
```
- Structured data
- All fields preserved
- Good for processing/analysis

### CSV
```bash
python claude_kb_query.py my_kb.db "query" --export results.csv
```
- Spreadsheet-compatible
- Easy to import into Excel/Sheets
- Good for reporting

## Conversation Context

View surrounding messages for search results:

```bash
python claude_kb_query.py my_kb.db "error handling" --context
```

Shows:
- Conversation name and tags
- 2 messages before match
- Matched message (marked with >>>)
- 2 messages after match

Interactive mode:
```
> context f5e38daa-5247-4b73-988e-c5342c263de8_chunk_0
```

## Performance Tips

### 1. Build Time
- **With embeddings**: ~17s for 401 conversations (18,354 chunks)
- **Without embeddings**: ~5s (keyword search only)
- First run downloads ~90MB embedding model

### 2. Search Speed
- **Keyword**: < 100ms (SQLite FTS5)
- **Semantic**: 1-3s (loading all embeddings, calculating similarity)
- **Hybrid**: 1-3s (runs both in parallel)

### 3. Database Size
- **Base**: ~80 MB (conversations, messages, chunks, FTS5 index)
- **With embeddings**: ~194 MB (+114 MB for vector data)
- **Ratio**: ~10 KB per chunk with embedding

### 4. Memory Usage
- Embedding model: ~300 MB RAM
- Database: Minimal (SQLite streams data)
- Peak: ~500 MB during build with embeddings

## Advanced Usage

### Python API

```python
from claude_knowledge_base import ClaudeKnowledgeBase

# Build knowledge base
kb = ClaudeKnowledgeBase('my_kb.db', use_embeddings=True)

# Load conversations
import json
with open('conversations.json') as f:
    data = json.load(f)

for conv in data:
    kb.process_conversation(conv)

# Search
results = kb.search("power bi")
results = kb.semantic_search("automation workflows", limit=10)
results = kb.hybrid_search("python data", keyword_weight=0.7)

# Stats
stats = kb.get_stats()
print(f"Chunks: {stats['chunks']}, Tokens: {stats['total_tokens']}")

kb.close()
```

### Query API

```python
from claude_kb_query import KnowledgeBaseQuery

kbq = KnowledgeBaseQuery('my_kb.db')

# Search with filters
results = kbq.search_with_filters(
    query="data analysis",
    search_mode='hybrid',
    tags=['python', 'sql'],
    after_date='2025-01-01',
    limit=20
)

# Get context
context = kbq.get_context('chunk_id', context_messages=3)

# Export
kbq.export_results(results, 'output.md', format='markdown')

kbq.close()
```

## Troubleshooting

### "sentence-transformers not available"
```bash
pip install sentence-transformers
```

### "NLTK not available"
```bash
pip install nltk
```

### Embedding model download fails
```python
# Manual download
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Database locked
- Close all connections
- Only one writer at a time
- Readers can run concurrently

### Semantic search returns no results
- Check embeddings were generated (look for `embedding_vector` in database)
- Adjust `min_similarity` threshold (default: 0.3)
- Try lower threshold: `kb.semantic_search(query, min_similarity=0.2)`

### Slow semantic search
- Reduce chunk count (larger chunk size)
- Use keyword or hybrid search instead
- Consider indexing options (future: vector databases)

## Database Schema

```sql
-- Conversations table
CREATE TABLE conversations (
    uuid TEXT PRIMARY KEY,
    name TEXT,
    created_at TEXT,
    updated_at TEXT,
    model TEXT,
    message_count INTEGER,
    total_tokens INTEGER,
    tags TEXT,  -- JSON array
    metadata TEXT  -- Full conversation JSON
);

-- Messages table
CREATE TABLE messages (
    uuid TEXT PRIMARY KEY,
    conversation_uuid TEXT,
    index_num INTEGER,
    sender TEXT,
    text TEXT,
    created_at TEXT,
    model_slug TEXT,
    has_files BOOLEAN,
    has_artifacts BOOLEAN,
    has_code BOOLEAN,
    FOREIGN KEY (conversation_uuid) REFERENCES conversations(uuid)
);

-- Chunks table (semantic units)
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    conversation_uuid TEXT,
    message_uuid TEXT,
    chunk_text TEXT,
    chunk_index INTEGER,
    sentence_count INTEGER,
    word_count INTEGER,
    chunk_hash TEXT,
    embedding_vector TEXT,  -- JSON array of floats
    tags TEXT,  -- JSON array
    created_at TEXT,
    FOREIGN KEY (conversation_uuid) REFERENCES conversations(uuid),
    FOREIGN KEY (message_uuid) REFERENCES messages(uuid)
);

-- FTS5 search index
CREATE VIRTUAL TABLE search_index USING fts5(
    conversation_uuid,
    message_uuid,
    chunk_id,
    content,
    tags
);
```

## Examples

### Municipal Government Workflow
```bash
# Find all conversations about GIS automation
python claude_kb_query.py my_kb.db --semantic "GIS automation" --tag arcgis

# Search for Power BI troubleshooting
python claude_kb_query.py my_kb.db "Power BI error" --tag power-bi --after 2025-09-01

# Export all Python code examples
python claude_kb_query.py my_kb.db "python script" --tag has-code --export python_examples.md
```

### Data Analysis Research
```bash
# Find related concepts
python claude_kb_query.py my_kb.db --semantic "time series forecasting"

# Technical documentation
python claude_kb_query.py my_kb.db "DAX measure formula" --export dax_measures.md

# Cross-reference topics
python claude_kb_query.py my_kb.db --hybrid "API integration webhook" --tag automation
```

### Code Review
```bash
# Find code review conversations
python claude_kb_query.py my_kb.db "code review" --tag code-review

# Error troubleshooting
python claude_kb_query.py my_kb.db --semantic "debugging authentication errors" --context

# Refactoring examples
python claude_kb_query.py my_kb.db "refactor" --tag python --export refactoring_patterns.md
```

## Next Steps

1. **Build Your First Knowledge Base**:
   ```bash
   python claude_knowledge_base.py your_export.zip
   ```

2. **Try Different Search Modes**:
   - Start with hybrid search (best overall)
   - Use semantic for conceptual questions
   - Use keyword for exact terms

3. **Explore Interactive Mode**:
   ```bash
   python claude_kb_query.py my_kb.db --interactive
   ```

4. **Export Key Findings**:
   ```bash
   python claude_kb_query.py my_kb.db "important topic" --export findings.md
   ```

## Support

- **Issues**: See `VALIDATION_FIX_SUMMARY.md` for troubleshooting
- **Examples**: Check `CHANGELOG.md` for version-specific features
- **Advanced**: Review source code for API details

---

**Version**: 1.3.0
**Last Updated**: 2025-10-26
