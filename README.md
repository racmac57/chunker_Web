# Chunker_v2 - Enterprise RAG-Powered File Processing System

**Version 2.1.2** - Enhanced with comprehensive RAG (Retrieval-Augmented Generation) capabilities, real-time monitoring, advanced evaluation metrics, and **critical performance optimizations**.

## 🚀 What's New in v2.1.2

### 🚨 Critical Performance Fixes
- **⚡ Processing Loop Resolution**: Fixed infinite loops that caused system hangs
- **📁 Smart File Archiving**: Failed files automatically moved to organized archive folders
- **🔒 Database Stability**: Eliminated "database is locked" errors with batch operations
- **⚡ 8-12x Speed Improvement**: Dynamic parallel workers and optimized processing

### 🚀 Performance Enhancements
- **🔍 Advanced RAG System**: Ollama + FAISS for local embeddings and semantic search
- **📊 Comprehensive Evaluation**: Precision@K, Recall@K, MRR, ROUGE, BLEU, Faithfulness scoring
- **🔗 LangSmith Integration**: Tracing, evaluation, and feedback collection
- **⚡ Real-time Monitoring**: Watchdog-based file system monitoring with debouncing
- **🤖 Hybrid Search**: Combines semantic similarity with keyword matching
- **📈 Automated Evaluation**: Scheduled testing with regression detection
- **🛡️ Production Ready**: Graceful degradation, error handling, and monitoring
- **📂 Source Folder Copying**: Configurable copying of processed files back to source locations

## Directory Structure

- **C:/_chunker** - Main project directory with scripts
- **02_data/** - Input files to be processed (watch folder)
- **03_archive/** - Archived original files and processed source files
- **04_output/** - Generated chunks and transcripts (organized by source file)
- **05_logs/** - Application logs and tracking
- **06_config/** - Configuration files
- **99_doc/legacy/** - Consolidated legacy docs (latest snapshot per project)
- **06_config/legacy/** - Consolidated legacy config (latest snapshot per project)
- **05_logs/legacy/** - Consolidated legacy logs (latest snapshot per project)
- **03_archive/legacy/** - Consolidated legacy db/backups (latest snapshot per project)
- **faiss_index/** - FAISS vector database storage
- **evaluations/** - RAG evaluation results
- **reports/** - Automated evaluation reports

## 🚀 Quick Start

### Basic Usage (Core Chunking)
1. Place files to process in `02_data/` folder
2. Run the watcher: `python watcher_splitter.py`
3. Check `04_output/` for processed chunks and transcripts
4. Original files are moved to `03_archive/` after processing

### Advanced Usage (RAG-Enabled)
1. Install RAG dependencies: `python install_rag_dependencies.py`
2. Install Ollama and pull model: `ollama pull nomic-embed-text`
3. Enable RAG in `config.json`: Set `"rag_enabled": true`
4. Run the watcher: `python watcher_splitter.py`
5. Search knowledge base: `python rag_search.py`

### Advanced Usage (Celery-Enabled)
For high-volume processing and advanced task management:

1. **Install Celery Dependencies**:
   ```bash
   pip install celery redis flower
   ```

2. **Start Redis Server**:
   ```bash
   # Windows: Download from https://github.com/microsoftarchive/redis/releases
   redis-server
   
   # Linux: sudo apt-get install redis-server
   # macOS: brew install redis
   ```

3. **Start Celery Services**:
   ```bash
   # Option A: Use orchestrator (recommended)
   python orchestrator.py
   
   # Option B: Start manually
   celery -A celery_tasks worker --loglevel=info --concurrency=4
   celery -A celery_tasks beat --loglevel=info
   celery -A celery_tasks flower --port=5555
   python enhanced_watchdog.py
   ```

4. **Monitor Tasks**:
   - Flower Dashboard: http://localhost:5555 (with authentication)
   - Celery CLI: `celery -A celery_tasks inspect active`
   - Logs: Check `logs/watcher.log`

5. **Security & Priority Features**:
   - **Flower Authentication**: Default credentials logged on startup
   - **Priority Queues**: High-priority processing for legal/police files
   - **Redis Fallback**: Automatic fallback to direct processing if Redis fails
   - **Task Timeouts**: 300s hard limit with graceful handling

6. **Configuration**:
   ```json
   {
     "celery_enabled": true,
     "celery_broker": "redis://localhost:6379/0",
     "celery_task_time_limit": 300,
     "celery_worker_concurrency": 4,
     "priority_departments": ["legal", "police"]
   }
   ```

7. **Environment Variables** (Optional):
   ```bash
   export FLOWER_USERNAME="your_username"
   export FLOWER_PASSWORD="your_secure_password"
   ```

## ✨ Features

### Core Chunking
- [x] **Organized output** by source file name with timestamp prefixes
- [x] **Multi-file type support** - .txt, .md, .json, .csv, .xlsx, .pdf, .py, .docx, .sql, .yaml, .xml, .log
- [x] **Unicode filename support** - Handles files with emojis, special characters, and symbols
- [x] **Enhanced filename sanitization** - Automatically cleans problematic characters
- [x] **Database tracking and logging** - Comprehensive activity monitoring
- [x] **Automatic file organization** - Moves processed files to archive

### RAG System (v2.0)
- [x] **Ollama Integration** - Local embeddings with nomic-embed-text model
- [x] **FAISS Vector Database** - High-performance similarity search
- [x] **Hybrid Search** - Combines semantic similarity with keyword matching
- [x] **ChromaDB Support** - Alternative vector database (optional)
- [x] **Real-time Monitoring** - Watchdog-based file system monitoring
- [x] **Debounced Processing** - Prevents race conditions and duplicate processing

### Performance & Scalability (v2.1.2)
- [x] **Dynamic Parallel Processing** - Up to 12 workers for large batches (50+ files)
- [x] **Batch Processing** - Configurable batch sizes with system overload protection
- [x] **Database Optimization** - Batch logging eliminates locking issues
- [x] **Smart File Archiving** - Failed files automatically moved to organized folders
- [x] **Real-time Performance Metrics** - Files/minute, avg processing time, peak CPU/memory
- [x] **500+ File Capability** - Handles large volumes efficiently without loops or crashes
- [x] **Source Folder Copying** - Configurable copying of processed files back to source locations

### Evaluation & Quality Assurance
- [x] **Comprehensive Metrics** - Precision@K, Recall@K, MRR, NDCG@K
- [x] **Generation Quality** - ROUGE-1/2/L, BLEU, BERTScore
- [x] **Faithfulness Scoring** - Evaluates answer grounding in source context
- [x] **Context Utilization** - Measures how much context is used in answers
- [x] **Automated Evaluation** - Scheduled testing with regression detection
- [x] **LangSmith Integration** - Tracing, evaluation, and feedback collection

### Production Features
- [x] **Graceful Degradation** - Continues working even if RAG components fail
- [x] **Error Handling** - Robust error recovery and logging
- [x] **Performance Monitoring** - System metrics and performance tracking
- [x] **Security Redaction** - PII masking in metadata
- [x] **Modular Architecture** - Clean separation of concerns
- [x] **JSON Sidecar (optional)** - Per-file sidecar with chunk list, metadata, and Python code blocks

### Windows “Send to” (Optional Helper)
To quickly drop files into `02_data` via right‑click:
1. Press Win+R → type `shell:sendto` → Enter
2. New → Shortcut → Target: `C:\_chunker\02_data` → Name: `Send to Chunker (02_data)`
3. Right‑click any file → Send to → `Send to Chunker (02_data)`

Optional PowerShell variant (recommended): `SendTo\Chunker.ps1` + `Chunker.bat`
- Recursively copies files/folders into `02_data`, preserving relative paths
- Writes `<filename>.origin.json` manifest (original_full_path, times, size, sha256, optional hmac)
- Watcher reads the manifest and populates sidecar `origin` (falls back if missing)

Notes
- Discovery is recursive under `02_data` and case-insensitive for extensions
- Optional sidecar copy-back to `source/` is enabled via `copy_sidecar_to_source`

## 🔄 Consolidation (2025-10-29)
- New sidecar flags (config.json):
  - `enable_json_sidecar` (default: true)
  - `enable_block_summary` (default: true)
  - `enable_grok` (default: false)

Sidecar schema (high-level):
- `file`, `processed_at`, `department`, `type`, `output_folder`, `transcript`
- `chunks[]`: filename, path, size, index
- `code_blocks[]` (for .py): type, name, signature, start_line, end_line, docstring

- Older project iterations (e.g., ClaudeExportFixer, chat_log_chunker_v1, chat_watcher) were unified under `C:\_chunker`.
- Historical outputs migrated to `C:\_chunker\04_output\<ProjectName>_<timestamp>`.
- Legacy artifacts captured once per project (latest snapshot only):
  - Docs → `99_doc\legacy\<ProjectName>_<timestamp>`
  - Config → `06_config\legacy\<ProjectName>_<timestamp>`
  - Logs → `05_logs\legacy\<ProjectName>_<timestamp>`
  - DB/Backups → `03_archive\legacy\<ProjectName>_<timestamp>`
- Script backups stored with timestamp prefixes at
  `C:\Users\carucci_r\OneDrive - City of Hackensack\00_dev\backup_scripts\<ProjectName>\`.
- Policy: keep only the latest legacy snapshot per project (older snapshots pruned).

## ⚙️ Configuration

Edit `config.json` to customize:

### Core Settings
- **File filter modes**: all, patterns, suffix
- **Supported file extensions**: .txt, .md, .json, .csv, .xlsx, .pdf, .py, .docx, .sql, .yaml, .xml, .log
- **Chunk sizes and processing options**: sentence limits, overlap settings
- **Notification settings**: email alerts and summaries

### RAG Settings
- **`rag_enabled`**: Enable/disable RAG functionality
- **`ollama_model`**: Ollama embedding model (default: nomic-embed-text)
- **`faiss_persist_dir`**: FAISS index storage directory
- **`chroma_persist_dir`**: ChromaDB storage directory (optional)

### LangSmith Settings (Optional)
- **`langsmith_api_key`**: Your LangSmith API key
- **`langsmith_project`**: Project name for tracing
- **`tracing_enabled`**: Enable/disable tracing
- **`evaluation_enabled`**: Enable/disable evaluation

### Monitoring Settings
- **`debounce_window`**: File event debouncing time (seconds)
- **`max_workers`**: Maximum parallel processing workers
- **`failed_dir`**: Directory for failed file processing

## 🔍 RAG Usage

### Setup
1. **Install Dependencies**: `python install_rag_dependencies.py`
2. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/)
3. **Pull Model**: `ollama pull nomic-embed-text`
4. **Enable RAG**: Set `"rag_enabled": true` in `config.json`
5. **Start Processing**: `python watcher_splitter.py`

### Search Knowledge Base

#### Interactive Search
```bash
python rag_search.py
```

#### Command Line Search
```bash
# Single query
python rag_search.py --query "How do I fix vlookup errors?"

# Batch search
python rag_search.py --batch queries.txt --output results.json

# Different search types
python rag_search.py --query "Excel formulas" --search-type semantic
python rag_search.py --query "vlookup excel" --search-type keyword
```

#### Programmatic Search
```python
from ollama_integration import initialize_ollama_rag

# Initialize RAG system
rag = initialize_ollama_rag()

# Search
results = rag.hybrid_search("How do I fix vlookup errors?", top_k=5)

# Display results
for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Source: {result['metadata']['source_file']}")
```

### Example Output

**Interactive Search Session:**
```
RAG Search Interface
==================================================
Commands:
  search <query> - Search the knowledge base
  semantic <query> - Semantic similarity search
  keyword <query> - Keyword-based search
  stats - Show knowledge base statistics
  quit - Exit the interface

RAG> search How do I fix vlookup errors?

Search Results for: 'How do I fix vlookup errors?'
==================================================

1. Score: 0.847 (semantic)
   Source: excel_guide.md
   Type: .md
   Content: VLOOKUP is used to find values in a table. Syntax: VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup]). Use FALSE for exact matches...
   Keywords: vlookup, excel, formula, table

2. Score: 0.723 (semantic)
   Source: troubleshooting.xlsx
   Type: .xlsx
   Content: Common VLOOKUP errors include #N/A when lookup value not found, #REF when table array is invalid...
   Keywords: vlookup, error, troubleshooting, excel

Search completed in 0.234 seconds
Found 2 results
```

## 📊 Evaluation & Testing

### Automated Evaluation
```bash
# Run comprehensive evaluation
python automated_eval.py

# Run specific tests
python rag_test.py

# Generate evaluation report
python -c "from automated_eval import AutomatedEvaluator; evaluator = AutomatedEvaluator({}); evaluator.generate_csv_report()"
```

### Manual Evaluation
```python
from rag_evaluation import RAGEvaluator
from rag_integration import FaithfulnessScorer

# Initialize evaluator
evaluator = RAGEvaluator()

# Evaluate retrieval quality
retrieval_metrics = evaluator.evaluate_retrieval(
    retrieved_docs=["doc1.md", "doc2.xlsx"],
    relevant_docs=["doc1.md", "doc2.xlsx", "doc3.pdf"],
    k_values=[1, 3, 5]
)

# Evaluate generation quality
generation_metrics = evaluator.evaluate_generation(
    reference="Check data types and table references",
    generated="Verify data types and table references for vlookup errors"
)

# Evaluate faithfulness
scorer = FaithfulnessScorer()
faithfulness_score = scorer.calculate_faithfulness(
    answer="VLOOKUP requires exact data types",
    context="VLOOKUP syntax requires exact data type matching"
)

print(f"Precision@5: {retrieval_metrics['precision_at_5']:.3f}")
print(f"ROUGE-1: {generation_metrics['rouge1']:.3f}")
print(f"Faithfulness: {faithfulness_score:.3f}")
```

### LangSmith Integration
```python
from langsmith_integration import initialize_langsmith

# Initialize LangSmith
langsmith = initialize_langsmith(
    api_key="your_api_key",
    project="chunker-rag-eval"
)

# Create evaluation dataset
test_queries = [
    {
        "query": "How do I fix vlookup errors?",
        "expected_answer": "Check data types and table references",
        "expected_sources": ["excel_guide.md", "troubleshooting.xlsx"]
    }
]

# Run evaluation
results = langsmith.run_evaluation(test_queries, rag_function)
```

## 📁 Supported File Types

| Type | Extensions | Processing Method | Metadata Extracted |
|------|------------|------------------|-------------------|
| **Text** | .txt, .md, .log | Direct text processing | Word count, sentences, keywords |
| **Structured** | .json, .csv, .yaml, .xml | Parsed structure | Schema, data types, samples |
| **Office** | .xlsx, .xlsm, .docx | Library extraction | Sheets, formulas, formatting |
| **Code** | .py | AST parsing | Functions, classes, imports, docstrings |
| **Documents** | .pdf | Text extraction | Pages, metadata, text content |

## 🛠️ Advanced Features

### Real-time Monitoring
```python
from watchdog_system import create_watchdog_monitor

# Initialize watchdog monitor
monitor = create_watchdog_monitor(config, process_callback)

# Start monitoring
monitor.start()

# Monitor stats
stats = monitor.get_stats()
print(f"Queue size: {stats['queue_size']}")
print(f"Processing files: {stats['processing_files']}")
```

### Modular File Processing
```python
from file_processors import process_excel_file, process_pdf_file

# Process specific file types
excel_content = process_excel_file("", "data.xlsx")
pdf_content = process_pdf_file("", "document.pdf")
```

### Embedding Management
```python
from embedding_helpers import EmbeddingManager

# Initialize embedding manager
manager = EmbeddingManager(chunk_size=1000, chunk_overlap=200)

# Process files for embedding
results = batch_process_files(file_paths, manager, extract_keywords_func)
```

## 🚀 Performance & Scalability

- **Parallel Processing**: Multi-threaded file processing with configurable workers
- **Streaming**: Large file support with memory-efficient streaming
- **Caching**: FAISS index persistence for fast startup
- **Debouncing**: Prevents duplicate processing of rapidly changing files
- **Graceful Degradation**: Continues working even if optional components fail

## 🔧 Troubleshooting

### Common Issues

1. **ChromaDB Installation Fails (Windows)**
   ```bash
   # Use FAISS instead
   pip install faiss-cpu
   # Or install build tools
   # Or use Docker deployment
   ```

2. **Ollama Not Available**
   ```bash
   # Install Ollama from https://ollama.ai/
   # Pull the model
   ollama pull nomic-embed-text
   ```

3. **Memory Issues with Large Files**
   ```python
   # Enable streaming in config
   "enable_streaming": true,
   "stream_chunk_size": 1048576  # 1MB chunks
   ```

### Performance Optimization

- **Chunk Size**: Adjust based on content type (75 for police, 150 for admin)
- **Parallel Workers**: Set based on CPU cores (default: 4)
- **Debounce Window**: Increase for slow file systems (default: 1s)
- **Index Persistence**: Enable for faster startup after restart

## 📈 Monitoring & Analytics

- **Database Tracking**: SQLite database with processing statistics
- **Session Metrics**: Files processed, chunks created, performance metrics
- **Error Logging**: Comprehensive error tracking and notification
- **System Metrics**: CPU, memory, disk usage monitoring
- **RAG Metrics**: Search performance, evaluation scores, user feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for local embedding models
- **FAISS** for vector similarity search
- **LangChain** for RAG framework
- **LangSmith** for evaluation and tracing
- **Watchdog** for file system monitoring

## 🔄 Version Control & GitHub

### Git Repository
This project is version-controlled using Git and backed up to GitHub.

**Remote Repository:** `https://github.com/racmac57/chunker_Web.git`

### Quick Git Commands
```bash
# Check status
git status

# Stage and commit changes
git add -A
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# View commit history
git log --oneline -10
```

### Files Excluded from Git
The following are automatically excluded via `.gitignore`:
- Processed documents (`99_doc/`, `04_output/`)
- Archived files (`03_archive/`)
- Database files (`*.db`, `*.sqlite`)
- Log files (`logs/`, `*.log`)
- Virtual environments (`.venv/`, `venv/`)
- NLTK data (`nltk_data/`)
- Temporary and backup files

### Contributing via Git
1. Clone the repository: `git clone https://github.com/racmac57/chunker_Web.git`
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and commit: `git commit -m "Feature: description"`
4. Push to your fork and create a pull request

For detailed Git setup information, see `GIT_SETUP_STATUS.md`.

## Directory Health

**Last Cleanup:** 2025-10-31 19:22:39  
**Items Scanned:** 16595  
**Items Moved:** 7  
**Items Deleted:** 627  
**Snapshots Pruned:** 0

**Snapshot Policy:** Keep only the latest legacy snapshot per project. Older snapshots are pruned during maintenance. Config backups follow the same policy.

**Log Location:** `05_logs/maintenance/2025_10_31_19_16_35/`

**Git Status:** ✅ Repository initialized, connected to GitHub, and regularly backed up
