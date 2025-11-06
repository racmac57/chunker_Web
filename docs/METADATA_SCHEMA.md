# Metadata Schema & Tagging Rules

This document defines the metadata fields emitted by the watcher, sidecars, and manifests after the enrichment pipeline runs. The goal is to keep chunk- and file-level metadata consistent across the watcher, sidecar JSON, `.origin.json` manifests, and ChromaDB records.

## Overview
- `metadata_enrichment.py` produces lightweight tags, summaries, and derived attributes for each processed file and chunk.
- `watcher_splitter.py` writes the enrichment payload into three places:
  - Chunk filenames (`tags-<slug>` suffix)
  - Updated `.origin.json` manifest (under `metadata_enrichment`)
  - Sidecar JSON (`*_sidecar.json`) that accompanies chunk output
- `backfill_knowledge_base.py` reads the same metadata and forwards it to ChromaDB, ensuring tags are searchable downstream.

## Manifest (`*.origin.json`) Fields
| Field | Type | Description |
| --- | --- | --- |
| `tags` | `List[str]` | High-level tags merged from existing manifest values and enrichment output. |
| `department` | `str` | Department inferred from path, manifest, or enrichment. |
| `metadata_enrichment.metadata.project_name` | `str` | Inferred project label (parent directory fallback). |
| `metadata_enrichment.metadata.source_type` | `str` | One of `code`, `data`, `documentation`, `log`, `notes`, or `other`. |
| `metadata_enrichment.metadata.language` | `str` | Basic language code (`en`, `multi`, or `unknown`). |
| `metadata_enrichment.metadata.department` | `str` | Department reflected in the enrichment pass. |
| `metadata_enrichment.metadata.key_terms` | `List[str]` | Most frequent non-stop words in the file. |
| `metadata_enrichment.metadata.enrichment_version` | `str` | Enrichment algorithm version. |
| `metadata_enrichment.summaries.file_summary` | `str` | Two-sentence summary derived from the document. |
| `metadata_enrichment.summaries.first_line` | `str` | First line snippet for quick preview. |
| `metadata_enrichment.enrichment_version` | `str` | Mirrors `metadata_enrichment.metadata.enrichment_version`. |
| `last_processed_at` | `str` | ISO timestamp the watcher last processed the file. |

## Sidecar (`*_sidecar.json`) Fields
| Field | Type | Description |
| --- | --- | --- |
| `source_file` | `str` | Source filename. |
| `source_path` | `str` | Original watcher path when processed. |
| `manifest_path` | `str` or `null` | Path to the manifest copy stored with output. |
| `created_at` | `str` | Timestamp the sidecar was generated. |
| `tags` | `List[str]` | File-level tags (same values written to manifest). |
| `metadata` | `Dict[str, Any]` | Same structure as `metadata_enrichment.metadata`. |
| `summaries` | `Dict[str, str]` | File summaries as described above. |
| `chunks[].file` | `str` | Chunk filename (with tag suffix if present). |
| `chunks[].tags` | `List[str]` | Chunk-level tags (base + chunk-specific terms). |
| `chunks[].key_terms` | `List[str]` | Frequent terms extracted from the chunk body. |
| `chunks[].summary` | `str` | One-sentence summary of the chunk. |
| `chunks[].char_length` | `int` | Character count for the chunk. |
| `chunks[].byte_length` | `int` | Byte size written to disk. |
| `enrichment_version` | `str` | Enrichment algorithm version (for auditing upgrades). |

## ChromaDB Metadata Fields
The backfill script persists the following metadata per document:

- `tags` & `file_tags` — JSON-encoded lists from the sidecar/manifest.
- `keywords` & `key_terms` — JSON-encoded list of dominant terms (chunk-level).
- `project_name`, `source_type`, `language`, `department`, `enrichment_version` — propagated from the enrichment metadata block.
- `chunk_summary` & `file_summary` — short text summaries supporting preview experiences.
- `char_length` & `byte_length` — stored as strings for consistency with existing fields.
- `manifest_path` & `sidecar_path` — references that allow downstream tooling to retrieve the full metadata bundle.

## Tagging Guidelines
1. **General tags**: The enrichment module adds semantic tags such as `code`, `dataset`, `docs`, `ai-chat`, `legal`, `police`, `it-ops`. Tags are lower-case and slugged in filenames.
2. **Technical tags**: Language/framework keywords (e.g., `python`, `powershell`, `sql`) are added when detected in file text or extension.
3. **Contextual tags**: Common departmental or topic words (e.g., `summons`, `incident`, `budget`) trigger matching tags to aid retrieval.
4. **Chunk-specific tags**: Each chunk inherits file-level tags and may add high-frequency terms unique to the chunk body.
5. **Filename suffixes**: Up to three slugified tags are appended to chunk filenames using `tags-<joined-slugs>` to aid quick identification while keeping compatibility with existing parsers.

## Example Sidecar Snippet
```json
{
  "source_file": "SummonsMaster.py",
  "tags": ["code", "python", "legal"],
  "metadata": {
    "project_name": "summons_tools",
    "source_type": "code",
    "language": "en",
    "department": "legal",
    "key_terms": ["summons", "pdf", "generate"],
    "enrichment_version": "1.0.0"
  },
  "chunks": [
    {
      "chunk_index": 1,
      "file": "2025_11_06_14_20_17_SummonsMaster_chunk1_tags-code-python.txt",
      "tags": ["code", "python", "pdf"],
      "key_terms": ["summons", "canvas", "document"],
      "summary": "Builds the PDF header and initializes the document canvas.",
      "char_length": 1820,
      "byte_length": 4096
    }
  ],
  "enrichment_version": "1.0.0"
}
```

## Integration Notes
- All new config toggles default to `false` to preserve existing behavior until explicitly enabled.
- The watcher maintains tag usage counts in `session_stats["tag_counts"]` for observability.
- The sidecar path is optionally copied back to the source directory when `copy_sidecar_to_source` is enabled.
- Backfill pipelines should prefer the `file_tags` and `metadata` objects to remain source-of-truth; they mirror what manifests contain.

