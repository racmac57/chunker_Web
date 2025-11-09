# Final Project Tasks

## Critical
- Review the untracked reference documents in the repository root. Archive them under `99_doc/` or remove them to keep the repo clean for future releases.
- Replace the placeholder smoke tests in `tests/` with full regression suites covering cache, incremental updates, backup manager, and monitoring flows end to end.
- Validate the release helper (`scripts/release_commit_and_tag.bat`) on a clean workstation, ensuring the backup, interactive cleanup, commit, tag, and push steps complete without manual fixes.

## Recommended
- Schedule a production backfill run with the rebuilt ChromaDB collection and verify the metrics documented in `docs/CHROMADB_VALIDATION_SUMMARY.md` remain accurate.
- Peer review the README, SUMMARY, and changelog updates before the next tagged release.
- Re-run `python deduplication.py --auto-remove` after each major ingest to confirm duplicate cleanup stays healthy.

## Optional
- Draft a pull-request template that captures the new release flow and testing expectations.
- Enable CI checks (markdownlint, pytest smoke suite) on pushes to `main` to guard against regressions.
- Capture screenshots or short recordings of the release helper workflow for onboarding material.
