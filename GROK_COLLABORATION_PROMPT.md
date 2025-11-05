# Grok Collaboration Prompt Template

Use this prompt when sharing your project with Grok for review and collaboration.

---

## 🎯 **Quick Start Prompt**

```
I'm working on an Enterprise Chunker v2.1.5 project - a file processing system with RAG knowledge base capabilities. I'd like you to review the Python scripts and help with improvements.

**Key Context:**
- We have 908 processed files (5,462 chunks) that need to be backfilled into the knowledge base
- Need to implement multi-cloud support (OneDrive + Google Drive) for processed file syncing
- RAG is currently disabled but needs to be enabled
- System uses move-based workflow (50-60% storage reduction) per your previous recommendations

**Priority Review Areas:**
1. `backfill_knowledge_base.py` - New script for KB backfill (5,462 files)
2. `watcher_splitter.py` - Main processing engine, especially `copy_to_cloud_enhanced()`
3. Multi-cloud support implementation
4. Code quality and performance improvements

**Files shared:**
[Attach files from grok_review_package folder]

Please review and provide:
- Code quality feedback
- Performance optimizations
- Multi-cloud implementation approach
- Architecture recommendations
- Any security concerns
```

---

## 📋 **Detailed Review Request**

```
I'm sharing my Enterprise Chunker v2.1.5 project for comprehensive review and collaboration.

## Project Overview
This is a file processing system that:
- Processes files from a watch folder (02_data/)
- Chunks content into manageable pieces
- Stores chunks in organized output folders (04_output/)
- Archives original files (03_archive/)
- Can integrate with RAG knowledge base (ChromaDB)
- Uses move-based workflow to reduce storage overhead

## Current State
- **Version**: 2.1.5
- **Processed Files**: 908 files
- **Chunk Files**: 5,462 chunks ready for KB
- **RAG Status**: Disabled (needs enabling)
- **Cloud Sync**: Disabled (needs Google Drive path)

## Key Files for Review

### 1. Critical Scripts
- `watcher_splitter.py` - Main processing engine (lines 287-627)
- `backfill_knowledge_base.py` - NEW script for KB backfill
- `manual_process_files.py` - Manual file processing
- `celery_tasks.py` - Async task processing

### 2. RAG Integration
- `rag_integration.py` - ChromaDB integration
- `rag_search.py` - Knowledge base search interface

### 3. Configuration
- `config.json` - Current system configuration

## Specific Review Requests

### A. Backfill Script Review
Please review `backfill_knowledge_base.py`:
- Is chunk parsing logic correct?
- Performance with 5,462 files?
- Metadata extraction complete?
- Error handling adequate?
- Any improvements needed?

### B. Multi-Cloud Support
Currently `copy_to_cloud_enhanced()` only supports single path.
Need to support multiple locations:
- OneDrive: `C:/Users/.../OneDrive - City of Hackensack/...`
- Google Drive: `G:/Google Drive/...` or `C:/Users/.../Google Drive/...`

**Questions:**
- Best approach for multiple cloud locations?
- Should `cloud_repo_root` become an array?
- How to handle different sync behaviors?

### C. Code Quality
- Python coding standards compliance
- Error handling patterns
- Performance bottlenecks
- Security concerns
- Missing documentation

### D. Architecture
- Scalability considerations
- Design improvements
- Better integration patterns
- Component interactions

## Expected Outcomes
1. Code quality improvements
2. Multi-cloud implementation plan
3. Backfill script optimizations
4. Architecture recommendations
5. Performance improvements
6. Security audit results

Please review the files and provide detailed feedback.
```

---

## 🔍 **Focused Review Prompts**

### For Backfill Script Only
```
Please review `backfill_knowledge_base.py`:

**Purpose**: Backfills 5,462 existing chunk files into ChromaDB knowledge base

**Context**:
- Scans 04_output/ directory for *_chunk*.txt files
- Extracts metadata from filenames
- Adds chunks to ChromaDB with proper metadata
- Handles 908 processed files (5,462 chunks total)

**Review Focus**:
1. Chunk file parsing logic (parse_chunk_filename function)
2. Metadata extraction completeness
3. Performance with large file counts
4. Error handling and recovery
5. ChromaDB integration correctness
6. Department detection logic
7. Keyword extraction

**Questions**:
- Is the parsing logic robust?
- Will it handle all filename variations?
- Any performance issues with 5,462 files?
- Missing error handling?
- Improvements needed?
```

### For Multi-Cloud Support
```
I need to implement multi-cloud support for `copy_to_cloud_enhanced()` in `watcher_splitter.py`.

**Current State**:
- Function accepts single `cloud_dir` path
- Config has `cloud_repo_root: null` (single string)
- Only copies to one location

**Requirements**:
- Support multiple cloud locations (OneDrive + Google Drive)
- Copy same files to both locations
- Maintain existing functionality for single location

**Current Function** (lines 590-627):
[Include relevant code section]

**Questions**:
1. Best approach: Array in config or separate config keys?
2. Should we modify function signature or keep backward compatible?
3. Error handling: If one fails, continue with others?
4. Performance: Parallel copies or sequential?
5. Logging: How to track which location succeeded?

Please provide implementation approach and code suggestions.
```

### For Code Quality Review
```
Please perform a comprehensive code quality review of:

**Files**: 
- watcher_splitter.py
- backfill_knowledge_base.py
- rag_integration.py
- celery_tasks.py

**Review Areas**:
1. **PEP 8 Compliance**: Python style guide adherence
2. **Error Handling**: Try/except blocks, error messages
3. **Performance**: Algorithm efficiency, bottlenecks
4. **Security**: Input validation, path sanitization
5. **Maintainability**: Code organization, comments
6. **Testing**: Test coverage, edge cases
7. **Documentation**: Docstrings, inline comments

**Focus Areas**:
- File I/O operations
- Database queries
- Error recovery mechanisms
- Resource cleanup
- Logging practices

Please provide specific feedback with code examples where possible.
```

---

## 📝 **Response Template for Grok**

After Grok reviews, you can use this to organize feedback:

```
## Grok Review Results

### Code Quality
- ✅ Strengths: [What's good]
- ⚠️ Issues Found: [Problems identified]
- 🔧 Improvements Suggested: [Recommendations]

### Backfill Script Review
- ✅ Correctness: [Is it correct?]
- ⚡ Performance: [Optimizations needed?]
- 🛡️ Error Handling: [Improvements?]

### Multi-Cloud Implementation
- 📋 Approach: [Recommended solution]
- 💻 Code Changes: [Specific changes needed]
- ⚠️ Considerations: [Things to watch for]

### Architecture Recommendations
- 🏗️ Design: [Improvements]
- 📈 Scalability: [Suggestions]
- 🔗 Integration: [Patterns]

### Performance Optimizations
- ⚡ Identified Bottlenecks: [List]
- 🚀 Suggested Improvements: [List]
- 📊 Expected Impact: [Metrics]

### Security Audit
- 🔒 Issues Found: [List]
- 🛡️ Recommendations: [List]
- ✅ Secure Practices: [What's good]
```

---

## 🎯 **Quick Reference**

**Minimum Files for Grok:**
1. watcher_splitter.py
2. backfill_knowledge_base.py
3. config.json
4. README.md
5. GROK_REVIEW_PACKAGE.md

**Best Results:**
- Share complete grok_review_package folder
- Start with README.md context
- Use focused prompts for specific areas
- Follow up with implementation questions

---

**Last Updated**: 2025-11-01  
**For Use With**: Grok AI Collaboration

