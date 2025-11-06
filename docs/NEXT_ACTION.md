# Next Actions

As of 2025-11-06 the Enterprise Chunker enhancements are validated with all feature toggles enabled. The remaining work before release is to install the Visual C++ build tools, add hnswlib, rerun the ChromaDB backfill, and execute the RAG API tests.

## Immediate Tasks
1. Install Visual C++ Build Tools (Desktop C++ workload).
2. python -m pip install --upgrade pip
3. python -m pip install hnswlib
4. python backfill_knowledge_base.py --force
5. Restart pi_server.py and verify:
   - POST /api/search
   - GET /api/cache/stats
6. python deduplication.py --scan --auto-remove
7. python -m pytest tests/test_query_cache.py tests/test_incremental_updates.py tests/test_backup_manager.py tests/test_monitoring_system.py

## Documentation
- Update docs/CHROMADB_VALIDATION_SUMMARY.md and docs/VALIDATION_NOTES.md with the above test run results.

## Release
- Commit the repo after validation is complete and tag the release once ChromaDB tests pass.
