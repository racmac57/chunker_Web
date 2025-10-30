# Claude Code Task: Implement Incremental Update System for ClaudeExportFixer

## Project Context

**Repository**: ClaudeExportFixer v1.4.0
**GitHub**: https://github.com/racmac57/ClaudeExportFixer
**Language**: Python 3.13
**Platform**: Windows (cross-platform preferred)

### Current Status (v1.4.0)
- ✅ Export fixer with full osteele viewer compatibility
- ✅ Knowledge base builder with vector embeddings
- ✅ Analytics suite with HTML dashboards
- ✅ Query tool with semantic/keyword/hybrid search
- ✅ 24/24 tests passing

### The Problem
**Current Behavior**: Both tools process entire export from scratch every time
- **Export Fixer** (`patch_conversations.py`): ~5-10 seconds (fast, but still wastes time)
- **Knowledge Base Builder** (`claude_knowledge_base.py`): **60+ minutes** (CRITICAL ISSUE)
  - Bottleneck: Embedding generation with sentence-transformers
  - 401 conversations → ~18,000 chunks → ~55 minutes for embeddings
  - CPU-bound, no GPU acceleration currently

**User Workflow**:
- Monthly Claude.ai exports
- Typically adds 5-20 new conversations (1-5% of total)
- 2-5 existing conversations updated (0.5-1% of total)
- **95%+ unchanged** but still reprocessed (wasting 60+ minutes)

**Goal**: Reduce 60+ minutes to ~5-10 minutes for typical incremental updates

---

## Task Objectives

Implement incremental update capability for both `patch_conversations.py` and `claude_knowledge_base.py` that:

1. **Detects changes** efficiently using timestamps and/or content hashing
2. **Reuses existing data** (especially embeddings) for unchanged conversations
3. **Processes only new/modified** conversations
4. **Maintains 100% compatibility** with full rebuild results
5. **Provides clear UX** with progress reporting and time savings estimates

---

## Deliverables

### 1. Enhanced `patch_conversations.py` (v1.5.0)
**New Features**:
- `--incremental` flag: Enable incremental mode
- `--previous FILE` argument: Path to previous output for comparison
- `--force-reprocess` flag: Force reprocessing even if unchanged
- `--dry-run` flag: Show what would be updated without processing

**Implementation Requirements**:
```python
# New function signatures
def detect_changes(new_export: Dict, previous_export: Dict) -> ChangeReport:
    """
    Compare exports and return what changed.
    
    Returns:
        ChangeReport with:
        - new_conversations: List[str] (UUIDs)
        - modified_conversations: List[str] (UUIDs)
        - unchanged_conversations: List[str] (UUIDs)
        - deleted_conversations: List[str] (UUIDs)
    """
    pass

def merge_exports(new_data: Dict, previous_data: Dict, changes: ChangeReport) -> Dict:
    """
    Merge new/modified conversations with previous export.
    
    Strategy:
    - Keep unchanged conversations from previous
    - Process new/modified conversations
    - Remove deleted conversations (optional, warn user)
    """
    pass
```

**Change Detection Strategy**:
- Use `updated_at` timestamp comparison (simple, fast)
- Fallback to content hash if timestamp unreliable
- Track both conversation-level and message-level changes

**Progress Reporting**:
```
Analyzing changes...
  ✓ Found 5 new conversations
  ✓ Found 2 modified conversations (new messages)
  ✓ Skipping 394 unchanged conversations
  
Processing changes...
  [=====>    ] 3/7 conversations (42%) - Est. 2m remaining
  
Complete! Saved ~8 minutes by reusing 394 conversations.
Output: fixed_incremental.zip
```

---

### 2. Enhanced `claude_knowledge_base.py` (v1.5.0)
**New Features**:
- `--incremental` flag: Enable incremental mode (auto-detects existing DB)
- `--force-rebuild` flag: Force full rebuild
- `--show-changes` flag: Preview changes without updating
- `--validate` flag: Compare incremental result against full rebuild

**Implementation Requirements**:

#### A. Database Schema Changes
```sql
-- New table: Track processed conversations for change detection
CREATE TABLE IF NOT EXISTS processing_manifest (
    conversation_uuid TEXT PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,              -- From Claude export
    content_hash TEXT,            -- SHA256 of conversation JSON
    message_count INTEGER,
    chunk_count INTEGER,
    embedding_model TEXT,         -- Track model version
    embedding_dimensions INTEGER
);

-- New index for faster lookups
CREATE INDEX IF NOT EXISTS idx_manifest_updated 
ON processing_manifest(updated_at);
```

#### B. Change Detection Function
```python
def detect_kb_changes(
    export_path: str, 
    db_path: str
) -> KBChangeReport:
    """
    Compare export against existing knowledge base.
    
    Returns:
        KBChangeReport with:
        - new_conversations: List[Conversation]
        - modified_conversations: List[Conversation]
        - unchanged_count: int
        - embedding_model_changed: bool (force rebuild if True)
    """
    # 1. Load existing manifest from DB
    manifest = load_manifest(db_path)
    
    # 2. For each conversation in export:
    #    - Check if UUID exists in manifest
    #    - Compare updated_at timestamp
    #    - If timestamps equal, optionally verify content_hash
    #    - Mark as new/modified/unchanged
    
    # 3. Check if embedding model changed (force rebuild)
    
    # 4. Return change report
    pass
```

#### C. Incremental Update Function
```python
def update_knowledge_base_incremental(
    export_path: str,
    db_path: str,
    changes: KBChangeReport
) -> UpdateStats:
    """
    Update knowledge base with only new/modified conversations.
    
    Strategy:
    1. For each modified conversation:
       - DELETE existing chunks/embeddings/tags for that conversation
       - Re-process and INSERT new data
    2. For each new conversation:
       - Process and INSERT
    3. Update processing_manifest with new timestamps/hashes
    4. Rebuild FTS5 index (fast, <5 seconds)
    
    Returns:
        UpdateStats with timing, counts, embeddings reused
    """
    conn = sqlite3.connect(db_path)
    
    # Transaction for safety
    with conn:
        # Process modified conversations
        for conv in changes.modified_conversations:
            # DELETE old data for this conversation
            delete_conversation_data(conn, conv['uuid'])
            
            # Re-process
            chunks = chunk_conversation(conv)
            embeddings = generate_embeddings(chunks)  # Still slow, but only for changed
            insert_conversation_data(conn, conv, chunks, embeddings)
            
            # Update manifest
            update_manifest(conn, conv)
        
        # Process new conversations
        for conv in changes.new_conversations:
            # Same as above but no DELETE needed
            chunks = chunk_conversation(conv)
            embeddings = generate_embeddings(chunks)
            insert_conversation_data(conn, conv, chunks, embeddings)
            insert_manifest(conn, conv)
        
        # Rebuild FTS5 (fast)
        rebuild_fts_index(conn)
    
    return UpdateStats(...)
```

#### D. Content Hashing for Validation
```python
def compute_conversation_hash(conversation: Dict) -> str:
    """
    Compute deterministic hash of conversation content.
    
    Include:
    - All message texts (in order)
    - Message timestamps
    - File attachments
    
    Exclude:
    - Conversation name (can change without content change)
    - UI metadata
    """
    import hashlib
    import json
    
    # Normalize conversation for hashing
    normalized = {
        'uuid': conversation['uuid'],
        'messages': [
            {
                'sender': msg['sender'],
                'text': msg['text'],
                'created_at': msg['created_at']
            }
            for msg in conversation.get('chat_messages', [])
        ]
    }
    
    # Deterministic JSON + SHA256
    content = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()
```

**Progress Reporting**:
```
Loading existing knowledge base...
  ✓ Found 401 conversations in database
  ✓ Embedding model: all-MiniLM-L6-v2 (384D) - COMPATIBLE

Analyzing changes...
  ✓ Found 5 new conversations
  ✓ Found 2 modified conversations (8 new messages)
  ✓ Reusing 394 conversations (95% of total)
  
Estimated time:
  - New conversations: ~5 minutes (embeddings)
  - Modified conversations: ~2 minutes (embeddings)
  - Database updates: ~30 seconds
  - Total: ~8 minutes (vs 60+ minutes full rebuild)
  - Time saved: ~52 minutes (87% reduction)

Processing changes...
  [=====>    ] 3/7 conversations - 5m12s remaining
  
  New: "Power BI Dashboard Optimization" (45 chunks, 45 embeddings)
  Modified: "ArcGIS Python Integration" (+8 messages, +12 chunks)
  ...

Complete! Knowledge base updated.
  - Conversations: 406 total (5 new, 2 updated, 394 reused)
  - Chunks: 18,234 total (+156 new)
  - Embeddings: Generated 156, Reused 18,078 (99.1% reuse)
  - Time: 7m43s (saved 52m17s vs full rebuild)
  - Database: production_kb.db (315 MB, +3 MB)
```

---

### 3. CLI Interface Design

#### Export Fixer
```bash
# Full rebuild (current behavior, default)
python patch_conversations.py export.zip -o fixed.zip

# Incremental update (NEW)
python patch_conversations.py new_export.zip -o fixed.zip --incremental --previous fixed.zip

# Dry run (preview changes)
python patch_conversations.py new_export.zip --incremental --previous fixed.zip --dry-run

# Force reprocess everything
python patch_conversations.py new_export.zip -o fixed.zip --force-reprocess
```

#### Knowledge Base
```bash
# Full rebuild (current behavior, default if DB doesn't exist)
python claude_knowledge_base.py export.zip my_kb.db

# Incremental update (NEW - auto-detects existing DB)
python claude_knowledge_base.py new_export.zip my_kb.db --incremental

# Preview changes without updating
python claude_knowledge_base.py new_export.zip my_kb.db --show-changes

# Force full rebuild even if DB exists
python claude_knowledge_base.py export.zip my_kb.db --force-rebuild

# Validate incremental matches full rebuild
python claude_knowledge_base.py export.zip my_kb.db --validate
```

---

### 4. Error Handling & Edge Cases

#### Scenario 1: Embedding Model Changed
```python
# If user upgrades sentence-transformers or changes model
if manifest['embedding_model'] != current_model:
    print("⚠️  WARNING: Embedding model changed!")
    print(f"   Database: {manifest['embedding_model']}")
    print(f"   Current:  {current_model}")
    print("")
    print("Incremental updates not supported with different models.")
    print("Options:")
    print("  1. Use --force-rebuild to rebuild entire database")
    print("  2. Continue with old model (not recommended)")
    
    if not args.force_rebuild:
        sys.exit(1)
```

#### Scenario 2: Database Schema Version Changed
```python
# Track schema version in DB
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Check compatibility
db_version = get_schema_version(db_path)
if db_version != CURRENT_SCHEMA_VERSION:
    print("⚠️  Database schema outdated!")
    print(f"   Database: v{db_version}")
    print(f"   Current:  v{CURRENT_SCHEMA_VERSION}")
    print("")
    print("Run with --force-rebuild to migrate to new schema.")
    sys.exit(1)
```

#### Scenario 3: Corrupted Previous Export
```python
try:
    previous_data = load_export(args.previous)
except Exception as e:
    print(f"❌ Error loading previous export: {e}")
    print("")
    print("Cannot perform incremental update with corrupted previous file.")
    print("Options:")
    print("  1. Use a different --previous file")
    print("  2. Run without --incremental for full rebuild")
    sys.exit(1)
```

#### Scenario 4: Clock Skew (Timestamp Issues)
```python
# If updated_at goes backward in time
if new_updated_at < manifest_updated_at:
    # Don't trust timestamp, use content hash
    new_hash = compute_conversation_hash(conversation)
    old_hash = manifest['content_hash']
    
    if new_hash != old_hash:
        # Content changed despite timestamp
        mark_as_modified(conversation)
    else:
        # False alarm, skip
        mark_as_unchanged(conversation)
```

---

### 5. Testing Requirements

#### A. Unit Tests (`tests/test_incremental_updates.py`)
```python
def test_detect_changes_new_conversation():
    """Test detection of new conversation."""
    old_export = {"conversations": [{"uuid": "1", "updated_at": "2025-01-01"}]}
    new_export = {
        "conversations": [
            {"uuid": "1", "updated_at": "2025-01-01"},
            {"uuid": "2", "updated_at": "2025-01-15"}  # NEW
        ]
    }
    
    changes = detect_changes(new_export, old_export)
    
    assert len(changes.new_conversations) == 1
    assert "2" in changes.new_conversations
    assert len(changes.unchanged_conversations) == 1

def test_detect_changes_modified_conversation():
    """Test detection of modified conversation."""
    old_export = {"conversations": [{"uuid": "1", "updated_at": "2025-01-01"}]}
    new_export = {"conversations": [{"uuid": "1", "updated_at": "2025-01-15"}]}
    
    changes = detect_changes(new_export, old_export)
    
    assert len(changes.modified_conversations) == 1
    assert "1" in changes.modified_conversations

def test_incremental_kb_update_reuses_embeddings():
    """Test that embeddings are reused for unchanged conversations."""
    # Create KB with 10 conversations
    kb = build_test_kb(num_conversations=10)
    
    # Add 2 new conversations
    new_export = create_test_export(num_conversations=12)
    
    # Track embedding generation calls
    with patch('claude_knowledge_base._generate_embeddings') as mock_embed:
        update_knowledge_base_incremental(new_export, kb.db_path)
        
        # Should only generate embeddings for 2 new conversations
        assert mock_embed.call_count == 2  # Not 12!

def test_incremental_produces_same_result_as_full_rebuild():
    """Validate incremental update produces identical results."""
    # Build full KB
    full_kb = build_knowledge_base(export_path, "full.db")
    
    # Build incrementally (split export into 3 batches)
    incremental_kb = build_knowledge_base(batch1, "incremental.db")
    update_knowledge_base_incremental(batch2, "incremental.db")
    update_knowledge_base_incremental(batch3, "incremental.db")
    
    # Compare results
    assert compare_databases(full_kb, incremental_kb) == True

def test_content_hash_detects_message_edits():
    """Test content hashing detects changes even with same timestamp."""
    conv_v1 = {
        "uuid": "1",
        "updated_at": "2025-01-01",
        "chat_messages": [{"text": "Original message"}]
    }
    
    conv_v2 = {
        "uuid": "1", 
        "updated_at": "2025-01-01",  # SAME timestamp
        "chat_messages": [{"text": "Edited message"}]  # DIFFERENT content
    }
    
    hash_v1 = compute_conversation_hash(conv_v1)
    hash_v2 = compute_conversation_hash(conv_v2)
    
    assert hash_v1 != hash_v2
```

#### B. Integration Tests
```python
def test_real_world_incremental_update():
    """Test incremental update with realistic data."""
    # Use actual 401-conversation export
    full_export = load_real_export("data-FINAL-v1.4.0.zip")
    
    # Build initial KB
    kb_path = "test_incremental.db"
    build_knowledge_base(full_export, kb_path)
    
    # Simulate monthly update: Add 5 new conversations
    updated_export = add_new_conversations(full_export, count=5)
    
    # Time incremental update
    start = time.time()
    stats = update_knowledge_base_incremental(updated_export, kb_path)
    elapsed = time.time() - start
    
    # Verify performance
    assert elapsed < 600  # Should be < 10 minutes (not 60+)
    assert stats.new_conversations == 5
    assert stats.reused_conversations == 401
    assert stats.embeddings_generated < 200  # Only for new convs

def test_incremental_update_benchmark():
    """Benchmark incremental vs full rebuild."""
    export = load_real_export("data-FINAL-v1.4.0.zip")
    
    # Full rebuild baseline
    start = time.time()
    build_knowledge_base(export, "full.db")
    full_time = time.time() - start
    
    # Incremental update (add 10 conversations)
    updated_export = add_new_conversations(export, count=10)
    start = time.time()
    update_knowledge_base_incremental(updated_export, "full.db")
    incremental_time = time.time() - start
    
    # Report
    speedup = full_time / incremental_time
    print(f"Full rebuild: {full_time:.1f}s")
    print(f"Incremental:  {incremental_time:.1f}s")
    print(f"Speedup:      {speedup:.1f}x")
    
    # Verify significant speedup
    assert speedup > 5  # Should be at least 5x faster
```

---

### 6. Documentation Updates

#### A. README.md Updates
Add new section after "Building Executables":

```markdown
## Incremental Updates (v1.5.0)

Both the export fixer and knowledge base builder support incremental updates to save time when processing regular exports.

### Export Fixer Incremental Mode

Process only new or modified conversations:

\`\`\`bash
# First export
python patch_conversations.py export_jan.zip -o fixed.zip

# Later exports (incremental)
python patch_conversations.py export_feb.zip -o fixed.zip --incremental --previous fixed.zip
\`\`\`

**Benefits:**
- 90%+ faster for typical monthly updates
- Only processes new/modified conversations
- Preserves all existing data

### Knowledge Base Incremental Mode

Update knowledge base with new conversations only:

\`\`\`bash
# Initial build
python claude_knowledge_base.py export_jan.zip my_kb.db

# Later updates (incremental)
python claude_knowledge_base.py export_feb.zip my_kb.db --incremental
\`\`\`

**Benefits:**
- **Reuses embeddings** for unchanged conversations (90%+ time savings)
- Typical update: 5-10 minutes instead of 60+ minutes
- Shows detailed progress: "5 new, 2 updated, 394 reused"

### Preview Changes (Dry Run)

See what would be updated without processing:

\`\`\`bash
# Export fixer
python patch_conversations.py new_export.zip --incremental --previous fixed.zip --dry-run

# Knowledge base
python claude_knowledge_base.py new_export.zip my_kb.db --show-changes
\`\`\`

### Force Full Rebuild

Override incremental mode:

\`\`\`bash
# Export fixer
python patch_conversations.py export.zip -o fixed.zip --force-reprocess

# Knowledge base
python claude_knowledge_base.py export.zip my_kb.db --force-rebuild
\`\`\`

**When to use:**
- Embedding model changed
- Database schema updated
- Suspected corruption
- After major version upgrade
```

#### B. CHANGELOG.md Entry
```markdown
## [1.5.0] - 2025-10-27

### Added - Incremental Updates
- **Incremental mode for Export Fixer** (`patch_conversations.py`)
  - `--incremental` flag: Process only new/modified conversations
  - `--previous FILE` argument: Specify previous output for comparison
  - `--dry-run` flag: Preview changes without processing
  - Change detection: Timestamp-based with content hash fallback
  - Progress reporting: Shows new/modified/unchanged counts
  - Time savings: 90%+ faster for typical monthly updates
  
- **Incremental mode for Knowledge Base** (`claude_knowledge_base.py`)
  - `--incremental` flag: Auto-detects existing database
  - `--show-changes` flag: Preview updates without modifying database
  - `--force-rebuild` flag: Override incremental mode
  - `--validate` flag: Compare incremental result against full rebuild
  - **Embedding reuse**: Preserves embeddings for unchanged conversations
  - **Processing manifest**: Tracks conversation hashes, timestamps, chunk counts
  - Performance: 5-10 minutes instead of 60+ minutes for typical updates
  
- **New database table**: `processing_manifest`
  - Tracks processed conversations with timestamps and content hashes
  - Enables efficient change detection
  - Stores embedding model version for compatibility checks

### Changed
- Default behavior unchanged (full rebuild if `--incremental` not specified)
- Knowledge base auto-enables incremental mode if database exists (override with `--force-rebuild`)

### Performance
- **Incremental export fixer**: ~5 seconds for 5 new conversations (vs ~10 seconds full)
- **Incremental KB update**: ~5-10 minutes for 5-10 new conversations (vs 60+ minutes full)
- **Embedding reuse**: 95%+ for typical monthly updates
- **Time savings**: 85-90% reduction for incremental updates

### Technical Details
- Change detection: `updated_at` timestamp comparison with SHA256 hash fallback
- Database strategy: DELETE old chunks + INSERT new for modified conversations
- Content hashing: Deterministic SHA256 of normalized conversation JSON
- Compatibility checks: Embedding model version, database schema version
- Error handling: Corrupted files, clock skew, schema migrations
```

---

### 7. Performance Targets

| Scenario | Current (v1.4.0) | Target (v1.5.0) | Improvement |
|----------|------------------|-----------------|-------------|
| **Export Fixer** |
| Full rebuild (401 convs) | ~10s | ~10s | No change |
| Incremental (5 new) | ~10s | ~2s | 80% faster |
| **Knowledge Base** |
| Full rebuild (401 convs) | ~60 min | ~60 min | No change |
| Incremental (5 new) | ~60 min | ~5-8 min | **87% faster** |
| Incremental (20 new) | ~60 min | ~15-20 min | **75% faster** |
| **Embedding Reuse** |
| Unchanged conversations | 0% | 95%+ | Critical |

---

### 8. Implementation Checklist

#### Phase 1: Core Infrastructure
- [ ] Add `processing_manifest` table to database schema
- [ ] Implement `compute_conversation_hash()` function
- [ ] Implement `detect_changes()` for export fixer
- [ ] Implement `detect_kb_changes()` for knowledge base
- [ ] Add CLI arguments (`--incremental`, `--previous`, etc.)

#### Phase 2: Incremental Update Logic
- [ ] Implement `merge_exports()` for export fixer
- [ ] Implement `update_knowledge_base_incremental()` for KB
- [ ] Implement `delete_conversation_data()` helper
- [ ] Implement `update_manifest()` helper
- [ ] Add progress reporting with time estimates

#### Phase 3: Error Handling
- [ ] Detect embedding model changes
- [ ] Detect schema version changes
- [ ] Handle corrupted previous files
- [ ] Handle clock skew (timestamp issues)
- [ ] Add validation mode (`--validate`)

#### Phase 4: Testing
- [ ] Unit tests for change detection
- [ ] Unit tests for content hashing
- [ ] Integration tests with real data
- [ ] Benchmark tests (timing validation)
- [ ] Validation tests (incremental == full rebuild)

#### Phase 5: Documentation
- [ ] Update README.md with incremental usage
- [ ] Update CHANGELOG.md with v1.5.0 entry
- [ ] Add inline code documentation
- [ ] Create usage examples

#### Phase 6: Polish
- [ ] Verify Windows compatibility (CRLF)
- [ ] Run all tests (`pytest -q`)
- [ ] Performance profiling
- [ ] User feedback integration

---

## Acceptance Criteria

- [ ] **Export Fixer**:
  - [ ] `--incremental` flag processes only new/modified conversations
  - [ ] `--dry-run` shows preview without processing
  - [ ] Progress reporting shows new/modified/unchanged counts
  - [ ] Incremental result identical to full rebuild

- [ ] **Knowledge Base**:
  - [ ] `--incremental` reuses embeddings for unchanged conversations
  - [ ] Processing manifest tracks hashes and timestamps
  - [ ] `--show-changes` previews updates
  - [ ] `--validate` compares against full rebuild
  - [ ] **Performance**: 5-10 minutes for 5-10 new conversations (vs 60+ minutes)

- [ ] **Testing**:
  - [ ] All existing tests pass (24/24)
  - [ ] New tests added for incremental features (10+ new tests)
  - [ ] Benchmark confirms performance targets
  - [ ] Validation confirms incremental == full rebuild

- [ ] **Documentation**:
  - [ ] README.md updated with incremental usage section
  - [ ] CHANGELOG.md has v1.5.0 entry
  - [ ] Inline documentation for new functions
  - [ ] Code examples for common scenarios

- [ ] **UX**:
  - [ ] Clear progress reporting with time estimates
  - [ ] Helpful error messages for edge cases
  - [ ] Time savings shown ("Saved ~52 minutes")
  - [ ] Dry-run mode for previewing changes

---

## Files to Modify

### Primary Files
1. **`patch_conversations.py`**
   - Add `--incremental`, `--previous`, `--dry-run` arguments
   - Implement `detect_changes()`, `merge_exports()`
   - Add progress reporting

2. **`claude_knowledge_base.py`**
   - Add `processing_manifest` table to schema
   - Add `--incremental`, `--show-changes`, `--validate` arguments
   - Implement `detect_kb_changes()`, `update_knowledge_base_incremental()`
   - Add content hashing, embedding reuse logic

### Documentation Files
3. **`README.md`**
   - Add "Incremental Updates" section
   - Update CLI usage examples

4. **`CHANGELOG.md`**
   - Add `[1.5.0]` section with incremental features

### Test Files
5. **`tests/test_incremental_updates.py`** (NEW)
   - Unit tests for change detection
   - Integration tests with real data
   - Benchmark tests
   - Validation tests

---

## Technical Constraints

- **Python 3.13** (stdlib preferred)
- **SQLite** (no external databases)
- **Windows** primary platform (but cross-platform)
- **No new dependencies** (use existing: sentence-transformers, nltk, etc.)
- **Backward compatible** (default behavior unchanged, incremental is opt-in)
- **CRLF line endings** for Windows compatibility

---

## Success Metrics

1. **Performance**: 85-90% time reduction for typical incremental updates
2. **Correctness**: Incremental produces identical results to full rebuild
3. **Usability**: Clear progress reporting, helpful error messages
4. **Reliability**: Handles edge cases gracefully (model changes, corruption, etc.)
5. **Maintainability**: Well-tested, well-documented, clean code

---

## Priority

**HIGH PRIORITY** - This feature directly addresses the biggest user pain point (60+ minute processing time for monthly updates).

---

## Questions or Clarifications?

- Embedding model versioning: Should we support automatic migration between models?
- Content hash algorithm: Is SHA256 sufficient or should we use a faster hash (e.g., xxhash)?
- Database backup: Should we auto-backup before incremental updates?
- Parallel processing: Should modified conversations be processed in parallel (ThreadPoolExecutor)?

---

**Ready to implement! Please review and let me know if you need any clarifications or modifications to the requirements.**

Generated: 2025-10-26
Target Version: v1.5.0
Estimated Implementation Time: 4-6 hours

