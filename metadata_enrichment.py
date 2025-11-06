"""
Utility functions to enrich chunk metadata with lightweight tagging and summaries.

The heuristics in this module are intentionally rule-based so they can run inside
the watcher without adding heavyweight dependencies.  The same helpers are used
by the watcher and backfill pipeline to keep metadata semantics aligned.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

METADATA_ENRICHMENT_VERSION = "1.0.0"
SIDECAR_SUFFIX = "_sidecar.json"
MANIFEST_ENRICHMENT_KEY = "metadata_enrichment"
CHUNK_SUMMARY_MAX_CHARS = 240
DEFAULT_MAX_KEY_TERMS = 6
MAX_TAGS_FOR_FILENAME = 3

# Basic keyword catalogues for heuristics.  These are intentionally compact; they
# can be extended over time without impacting existing outputs.
TOPIC_KEYWORDS: Dict[str, Sequence[str]] = {
    "ai": ("llm", "prompt", "embedding", "openai", "anthropic", "chatgpt", "rag"),
    "police": ("incident", "arrest", "cad", "dispatch", "officer"),
    "legal": ("summons", "court", "affidavit", "warrant", "compliance"),
    "finance": ("budget", "invoice", "purchase order", "forecast"),
    "it-ops": ("deployment", "infrastructure", "server", "uptime", "monitoring"),
    "data": ("dataset", "csv", "analysis", "pandas", "query"),
    "docs": ("readme", "documentation", "guide", "tutorial"),
    "code": ("function", "class", "import", "def ", "return "),
    "conversation": ("user:", "assistant:", "system:", "transcript"),
    "training": ("curriculum", "lesson", "learning", "training", "quiz"),
}

TECH_KEYWORDS: Dict[str, Sequence[str]] = {
    "python": (".py", "def ", "import ", "pandas", "numpy", "flask"),
    "powershell": (".ps1", "param(", "Write-Host", "Get-ChildItem", "Set-Item"),
    "sql": (".sql", "select ", "from ", "join ", "where "),
    "excel": (".xlsx", ".xls", "spreadsheet"),
    "markdown": (".md", "# ", "```"),
    "json": (".json", "{", "}"),
}

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "is",
    "are",
    "be",
    "this",
    "that",
    "from",
    "as",
    "was",
    "were",
    "it",
    "if",
    "not",
}

SOURCE_TYPE_BY_EXTENSION: Dict[str, str] = {
    ".py": "code",
    ".ps1": "code",
    ".js": "code",
    ".ts": "code",
    ".json": "data",
    ".csv": "data",
    ".log": "log",
    ".md": "documentation",
    ".txt": "notes",
    ".sql": "query",
}

DEPARTMENT_HINTS: Dict[str, Sequence[str]] = {
    "police": ("police", "cad", "rms", "incident"),
    "legal": ("legal", "court", "summons"),
    "admin": ("admin", "administration", "general"),
}


@dataclass
class EnrichmentResult:
    tags: List[str]
    metadata: Dict[str, Any]
    summaries: Dict[str, Any]


def enrich_metadata(
    text: str,
    original_path: Path,
    manifest_data: Optional[Dict[str, Any]] = None,
    *,
    max_key_terms: int = DEFAULT_MAX_KEY_TERMS,
) -> EnrichmentResult:
    """
    Perform lightweight enrichment based on the file content and source context.
    """
    manifest_data = manifest_data or {}
    lower_text = text.lower()

    extension = original_path.suffix.lower()
    source_type = SOURCE_TYPE_BY_EXTENSION.get(extension, "other")

    tags: List[str] = []
    if source_type == "code":
        tags.append("code")
    elif source_type == "data":
        tags.append("dataset")
    elif source_type == "documentation":
        tags.append("docs")
    elif source_type == "log":
        tags.append("log")

    if looks_like_chat_transcript(lower_text):
        tags.append("ai-chat")

    tags.extend(find_matching_tags(lower_text, original_path, TOPIC_KEYWORDS))
    tags.extend(find_matching_tags(lower_text, original_path, TECH_KEYWORDS))

    manifest_tags = manifest_data.get("tags")
    if isinstance(manifest_tags, list):
        tags.extend(str(tag).lower() for tag in manifest_tags if tag)

    tags = sorted(unique_preserve_order(tag for tag in tags if tag))

    department = infer_department(original_path, manifest_data)
    language = detect_language(text)
    project_name = infer_project_name(original_path)
    key_terms = extract_key_terms(lower_text, max_terms=max_key_terms)
    summary = summarize_text(text)

    metadata: Dict[str, Any] = {
        "project_name": project_name,
        "source_type": source_type,
        "language": language,
        "department": department,
        "key_terms": key_terms,
        "enrichment_version": METADATA_ENRICHMENT_VERSION,
    }

    summaries = {
        "file_summary": summary,
        "first_line": text.strip().splitlines()[0][:CHUNK_SUMMARY_MAX_CHARS]
        if text.strip()
        else "",
    }

    return EnrichmentResult(tags=tags, metadata=metadata, summaries=summaries)


def enrich_chunk(
    chunk_text: str,
    base_tags: Iterable[str],
    *,
    max_key_terms: int = DEFAULT_MAX_KEY_TERMS,
) -> Dict[str, Any]:
    """
    Produce per-chunk metadata derived from the chunk body combined with the
    file-level tags.
    """
    lower_chunk = chunk_text.lower()
    chunk_terms = extract_key_terms(lower_chunk, max_terms=max_key_terms)
    candidate_tags = set(t.lower() for t in base_tags)
    candidate_tags.update(
        find_matching_tags(lower_chunk, None, {"ai-chat": ("assistant:", "user:")})
    )

    # Promote chunk-specific key terms as ad-hoc tags if they look meaningful.
    for term in chunk_terms:
        if len(term) > 3 and term not in candidate_tags:
            candidate_tags.add(term)

    summary = summarize_text(chunk_text, max_sentences=1)

    payload = {
        "tags": sorted(candidate_tags),
        "key_terms": chunk_terms,
        "summary": summary,
        "char_length": len(chunk_text),
    }
    return payload


def build_sidecar_payload(
    *,
    source_path: Path,
    manifest_path: Optional[Path],
    enrichment: EnrichmentResult,
    chunk_records: List[Dict[str, Any]],
    timestamp: str,
) -> Dict[str, Any]:
    """
    Assemble the JSON payload written alongside chunk files.
    """
    return {
        "source_file": source_path.name,
        "source_path": str(source_path),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "created_at": timestamp,
        "tags": enrichment.tags,
        "metadata": enrichment.metadata,
        "summaries": enrichment.summaries,
        "chunks": chunk_records,
        "enrichment_version": METADATA_ENRICHMENT_VERSION,
    }


def slugify_tag(tag: str) -> str:
    """
    Convert a tag into a filesystem-safe slug for filenames.
    """
    tag = tag.lower()
    tag = re.sub(r"[^a-z0-9]+", "-", tag)
    tag = tag.strip("-")
    return tag[:32]


def tag_suffix_for_filename(tags: Sequence[str]) -> str:
    if not tags:
        return ""
    slugs = [slugify_tag(tag) for tag in tags if slugify_tag(tag)]
    if not slugs:
        return ""
    return f"tags-{'-'.join(slugs[:MAX_TAGS_FOR_FILENAME])}"


def looks_like_chat_transcript(text: str) -> bool:
    indicators = ("user:", "assistant:", "system:", "[assistant]")
    return sum(1 for token in indicators if token in text) >= 2


def find_matching_tags(
    text: str,
    original_path: Optional[Path],
    catalogue: Dict[str, Sequence[str]],
) -> List[str]:
    matches: List[str] = []
    path_text = " ".join(original_path.parts).lower() if original_path else ""
    for tag, keywords in catalogue.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text or keyword_lower in path_text:
                matches.append(tag)
                break
    return matches


def unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def infer_department(path: Path, manifest: Dict[str, Any]) -> str:
    manifest_department = manifest.get("department")
    if isinstance(manifest_department, str) and manifest_department:
        return manifest_department.lower()

    lower_parts = [part.lower() for part in path.parts]
    for department, indicators in DEPARTMENT_HINTS.items():
        if any(indicator in lower_parts for indicator in indicators):
            return department
    return manifest.get("metadata", {}).get("department", "admin")


def detect_language(text: str) -> str:
    # Extremely lightweight detector that distinguishes English vs. other based
    # on ASCII ratio.  This can be replaced later with a richer library.
    if not text:
        return "unknown"

    ascii_chars = sum(1 for ch in text if ord(ch) < 128)
    ratio = ascii_chars / max(len(text), 1)
    if ratio > 0.95:
        return "en"
    return "multi"


def infer_project_name(path: Path) -> str:
    # Use the immediate parent directory as an approximate project name.
    if len(path.parts) >= 2:
        return path.parent.name
    return path.stem


def extract_key_terms(text: str, *, max_terms: int = DEFAULT_MAX_KEY_TERMS) -> List[str]:
    words = re.findall(r"\b[a-z0-9_\-]{3,}\b", text.lower())
    words = [word for word in words if word not in STOPWORDS]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(max_terms)]


def summarize_text(
    text: str,
    *,
    max_sentences: int = 2,
    max_chars: int = CHUNK_SUMMARY_MAX_CHARS,
) -> str:
    stripped = text.strip()
    if not stripped:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", stripped)
    summary = " ".join(sentences[:max_sentences])
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3].rstrip() + "..."
    return summary


def merge_manifest_metadata(
    manifest_data: Dict[str, Any],
    enrichment: EnrichmentResult,
) -> Dict[str, Any]:
    """
    Merge enrichment details into a manifest dictionary without discarding
    existing fields.  Returns the updated manifest.
    """
    manifest_data = manifest_data.copy()
    existing_tags = manifest_data.get("tags", [])
    if not isinstance(existing_tags, list):
        existing_tags = [existing_tags] if existing_tags else []

    merged_tags = unique_preserve_order([*existing_tags, *enrichment.tags])
    manifest_data["tags"] = merged_tags

    enrichment_payload = {
        "metadata": enrichment.metadata,
        "summaries": enrichment.summaries,
        "enrichment_version": METADATA_ENRICHMENT_VERSION,
    }

    previous = manifest_data.get(MANIFEST_ENRICHMENT_KEY, {})
    if isinstance(previous, dict):
        previous.update(enrichment_payload)
        manifest_data[MANIFEST_ENRICHMENT_KEY] = previous
    else:
        manifest_data[MANIFEST_ENRICHMENT_KEY] = enrichment_payload

    return manifest_data


def dump_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


