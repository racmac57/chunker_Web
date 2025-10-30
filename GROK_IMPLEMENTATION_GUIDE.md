# Grok Implementation Guide for RAG Enhancement

## Overview
This document provides Grok with the complete implementation plan for adding RAG, vector database (ChromaDB), and evaluation capabilities to Chunker_v2.

## Files Created
1. `rag_integration.py` - ChromaDB RAG implementation with faithfulness scoring
2. `rag_evaluation.py` - Comprehensive RAG evaluation metrics
3. `config.json` - Updated with LangSmith and RAG configuration
4. `requirements.txt` - Updated with all necessary dependencies

## Key Components to Implement

### 1. ChromaDB Integration (`rag_integration.py`)
- **ChromaRAG Class**: Full CRUD operations for vector database
  - `add_chunk()` - Add documents with metadata
  - `search_similar()` - Semantic similarity search
  - `search_by_keywords()` - Keyword-based search
  - `get_chunk_by_id()` - Retrieve specific chunks
  - `update_chunk()` - Update existing chunks
  - `delete_chunk()` - Remove chunks
  - `get_collection_stats()` - Get database statistics

- **FaithfulnessScorer Class**: Evaluate answer grounding
  - `extract_claims()` - Extract factual claims from answers
  - `calculate_faithfulness()` - Calculate faithfulness score (0-1)
  - `detailed_faithfulness_analysis()` - Detailed breakdown

### 2. RAG Evaluation (`rag_evaluation.py`)
- **RAGEvaluator Class**: Comprehensive evaluation metrics
  - `precision_at_k()` - Precision@K metric
  - `recall_at_k()` - Recall@K metric
  - `mean_reciprocal_rank()` - MRR metric
  - `ndcg_at_k()` - nDCG@K metric
  - `calculate_rouge_scores()` - ROUGE-1/2/L scores
  - `calculate_bleu_score()` - BLEU score
  - `evaluate_retrieval()` - Full retrieval evaluation
  - `evaluate_answer_quality()` - Answer quality metrics

### 3. New File Type Support
Files added to `config.json`:
- `.xlsx` - Excel files (use openpyxl)
- `.pdf` - PDF files (use PyPDF2)
- `.py` - Python files (use ast module)
- `.docx` - Word documents (use python-docx)
- `.sql` - SQL files
- `.yaml` - YAML files
- `.xml` - XML files
- `.log` - Log files

## Integration Steps for Grok

### Step 1: Process New File Types
Add file processing functions to `watcher_splitter.py`:

```python
def process_excel_file(file_path):
    """Extract data from Excel files"""
    import openpyxl
    wb = openpyxl.load_workbook(file_path)
    content = []
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        content.append(f"Sheet: {sheet_name}")
        # Extract formulas, data types, etc.
        for row in sheet.iter_rows(values_only=True):
            content.append(str(row))
    return "\n".join(content)

def process_pdf_file(file_path):
    """Extract text from PDF files"""
    import PyPDF2
    content = []
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            content.append(page.extract_text())
    return "\n".join(content)

def process_python_file(file_path):
    """Extract code structure from Python files"""
    import ast
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    # Extract functions, classes, imports
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    return f"Functions: {functions}\nClasses: {classes}\nImports: {imports}"
```

### Step 2: Integrate ChromaDB with Watcher
Add to `process_file_enhanced()` in `watcher_splitter.py`:

```python
def process_file_enhanced(file_path, config):
    # ... existing code ...
    
    # If RAG enabled, add to ChromaDB
    if config.get("rag_enabled"):
        try:
            from rag_integration import ChromaRAG
            chroma_rag = ChromaRAG()
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "file_name": file_path.name,
                    "file_type": file_path.suffix,
                    "chunk_index": i + 1,
                    "timestamp": datetime.now().isoformat(),
                    "department": department,
                    "keywords": extract_keywords(chunk),
                    "file_size": file_path.stat().st_size,
                    "processing_time": time.time() - start_time
                }
                chroma_rag.add_chunk(chunk, metadata)
                logger.info(f"Added chunk to ChromaDB: {metadata['file_name']} - chunk{i+1}")
        except Exception as e:
            logger.error(f"Failed to add to ChromaDB: {e}")
    
    # ... rest of existing code ...
```

### Step 3: Add Evaluation Capabilities
Create test queries file `test_queries.json`:

```json
[
  {
    "query": "How do I fix vlookup errors in Excel?",
    "expected_answer": "Check data types and table references",
    "expected_sources": ["excel_troubleshooting.md", "vlookup_guide.xlsx"],
    "category": "excel"
  },
  {
    "query": "What is Power BI query syntax?",
    "expected_answer": "Use M language for Power Query",
    "expected_sources": ["power_bi_guide.md"],
    "category": "power-bi"
  }
]
```

### Step 4: Set Up LangSmith Integration (Optional)
Create `langsmith_integration.py`:

```python
import os
from langsmith import Client, traceable
from langsmith.evaluation import evaluate

# Configure LangSmith
os.environ["LANGCHAIN_API_KEY"] = "your_api_key"
os.environ["LANGCHAIN_PROJECT"] = "chunker-rag-eval"

client = Client()

@traceable
def traced_rag_query(query, rag_system):
    """RAG query with LangSmith tracing"""
    results = rag_system.search_similar(query, n_results=5)
    # Add generation step
    return results

def create_feedback(run_id, score, comment=""):
    """Collect user feedback"""
    client.create_feedback(run_id=run_id, key="user_feedback", score=score, comment=comment)

def run_evaluation(examples, rag_func):
    """Run automated evaluation"""
    return evaluate(
        rag_func,
        data=examples,
        evaluators=["answer_relevance", "context_relevance"],
        experiment_prefix="rag-eval-v1"
    )
```

## Usage Examples

### Basic RAG Usage
```python
from rag_integration import ChromaRAG, FaithfulnessScorer

# Initialize
rag = ChromaRAG()
scorer = FaithfulnessScorer()

# Query knowledge base
results = rag.search_similar("How do I use vlookup?", n_results=5)

# Evaluate faithfulness
answer = generate_answer(results)
faithfulness = scorer.calculate_faithfulness(answer, context)

print(f"Faithfulness Score: {faithfulness:.2f}")
```

### Comprehensive Evaluation
```python
from rag_evaluation import run_evaluation_pipeline
from rag_integration import ChromaRAG, FaithfulnessScorer
import json

# Load test queries
with open('test_queries.json') as f:
    test_queries = json.load(f)

# Run evaluation
results = run_evaluation_pipeline(test_queries, rag, scorer)

# Analyze results
for result in results:
    print(f"Query: {result['query']}")
    print(f"Precision@K: {result['retrieval_metrics']['precision_at_k']:.2f}")
    print(f"Faithfulness: {result['faithfulness']:.2f}")
```

## Testing Strategy

1. **Unit Tests**: Test each metric calculation independently
2. **Integration Tests**: Test ChromaDB operations with mock data
3. **End-to-End Tests**: Test full RAG pipeline with sample queries
4. **Performance Tests**: Measure latency and resource usage

## Performance Considerations

1. **Embedding Generation**: Use Ollama for local embeddings (no API costs)
2. **Batch Processing**: Process multiple files in batches
3. **Caching**: Cache embeddings for unchanged files
4. **Incremental Updates**: Only re-embed changed chunks

## Next Steps for Grok

1. Complete file type processors (Excel, PDF, Python)
2. Integrate ChromaDB into existing watcher
3. Add evaluation capability with test queries
4. Implement LangSmith tracing (optional)
5. Add comprehensive error handling
6. Create monitoring and alerting
7. Document API usage

## Dependencies Summary

Key packages to install:
```bash
pip install chromadb faiss-cpu sentence-transformers ollama
pip install openpyxl pypdf2 python-docx pyyaml
pip install langchain langchain-community langsmith
pip install rouge-score bert-score numpy scikit-learn
```

## Success Metrics

- **Retrieval Quality**: Precision@K > 0.7, Recall@K > 0.6
- **Answer Quality**: Faithfulness > 0.8, ROUGE-1 F1 > 0.7
- **Latency**: Query time < 2 seconds
- **Coverage**: Process all supported file types successfully

---

*This guide provides the foundation for Grok to implement comprehensive RAG capabilities in Chunker_v2.*

