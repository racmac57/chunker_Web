import argparse
import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

try:
    import chromadb
    from chromadb.config import Settings
except ImportError as exc:  # pragma: no cover - handled in consumer modules
    chromadb = None  # type: ignore
    Settings = None  # type: ignore
    _import_error = exc
else:
    _import_error = None


logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "chunker_knowledge_base"


@dataclass
class HashNormalizationRules:
    lowercase: bool = True
    strip: bool = True
    collapse_whitespace: bool = True


@dataclass
class DeduplicationConfig:
    enabled: bool = False
    auto_remove: bool = False
    log_only: bool = True
    batch_size: int = 200
    normalization: HashNormalizationRules = field(default_factory=HashNormalizationRules)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "DeduplicationConfig":
        if not data:
            return cls()
        norm = data.get("hash_normalization") or data.get("normalization") or {}
        normalization = HashNormalizationRules(
            lowercase=norm.get("lowercase", True),
            strip=norm.get("strip", True),
            collapse_whitespace=norm.get("collapse_whitespace", True),
        )
        return cls(
            enabled=data.get("enabled", False),
            auto_remove=data.get("auto_remove", False),
            log_only=data.get("log_only", True),
            batch_size=int(data.get("batch_size", 200)),
            normalization=normalization,
        )


class DeduplicationManager:
    """
    Utility class for detecting and removing duplicate chunks stored in ChromaDB.
    """

    def __init__(
        self,
        persist_directory: str,
        config: Optional[dict] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        client: Optional["chromadb.PersistentClient"] = None,
        preload: bool = True,
    ) -> None:
        if chromadb is None or Settings is None:
            raise ImportError(
                "chromadb is required for deduplication but is not installed"
            ) from _import_error

        self.config = DeduplicationConfig.from_dict(config)
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.hash_index: Dict[str, Set[str]] = {}
        self.chunk_hash_map: Dict[str, str] = {}
        # Create settings with explicit API implementation
        chroma_settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True,
            chroma_api_impl="chromadb.api.segment.SegmentAPI",
            chroma_sysdb_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_producer_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_consumer_impl="chromadb.db.impl.sqlite.SqliteDB",
            chroma_segment_manager_impl="chromadb.segment.impl.manager.local.LocalSegmentManager"
        )
        self._client = client or chromadb.PersistentClient(
            path=persist_directory,
            settings=chroma_settings,
        )
        self.collection = self._ensure_collection()

        if preload and self.config.enabled:
            self.load_existing_hashes()

    def _ensure_collection(self):
        try:
            return self._client.get_collection(name=self.collection_name)
        except Exception:
            logger.warning(
                "Collection '%s' not found, attempting to create it before deduplication",
                self.collection_name,
            )
            return self._client.create_collection(name=self.collection_name)

    # ------------------------------------------------------------------ #
    # Hashing helpers
    # ------------------------------------------------------------------ #
    def normalize_text(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text or "")

        rules = self.config.normalization
        normalized = text
        if rules.strip:
            normalized = normalized.strip()
        if rules.lowercase:
            normalized = normalized.lower()
        if rules.collapse_whitespace:
            normalized = " ".join(normalized.split())
        return normalized

    def hash_content(self, text: str) -> str:
        normalized = self.normalize_text(text)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------ #
    # Hash store management
    # ------------------------------------------------------------------ #
    def load_existing_hashes(self) -> None:
        """
        Load existing document hashes from ChromaDB metadata/documents into memory.
        """
        logger.info("Loading existing chunk hashes from ChromaDB for deduplication")
        self.hash_index.clear()
        self.chunk_hash_map.clear()

        batch_size = max(1, self.config.batch_size)
        offset = 0

        while True:
            batch = self.collection.get(
                include=["documents", "metadatas"],
                limit=batch_size,
                offset=offset,
            )

            ids = batch.get("ids") or []
            documents = batch.get("documents") or []
            metadatas = batch.get("metadatas") or []

            # Handle potential nested list structure defensively
            if documents and isinstance(documents[0], list):
                documents = documents[0]
            if metadatas and isinstance(metadatas[0], list):
                metadatas = metadatas[0]

            if not ids:
                break

            for idx, chunk_id in enumerate(ids):
                metadata = metadatas[idx] if idx < len(metadatas) else {}
                document_text = documents[idx] if idx < len(documents) else ""

                stored_hash = None
                if isinstance(metadata, dict):
                    stored_hash = metadata.get("content_hash")

                if stored_hash:
                    hash_value = stored_hash
                else:
                    hash_value = self.hash_content(document_text)

                self._register_hash(hash_value, chunk_id)

            offset += len(ids)

            if len(ids) < batch_size:
                break

        logger.info(
            "Deduplication loaded %d unique hashes for %d chunks",
            len(self.hash_index),
            len(self.chunk_hash_map),
        )

    def _register_hash(self, hash_value: str, chunk_id: Optional[str]) -> None:
        if not hash_value:
            return
        if chunk_id is None:
            chunk_id = f"unknown-{len(self.chunk_hash_map)}"

        ids = self.hash_index.setdefault(hash_value, set())
        ids.add(chunk_id)
        self.chunk_hash_map[chunk_id] = hash_value

    def add_hash(self, hash_value: str, chunk_id: Optional[str]) -> None:
        self._register_hash(hash_value, chunk_id)

    # ------------------------------------------------------------------ #
    # Duplicate detection
    # ------------------------------------------------------------------ #
    def is_duplicate(
        self,
        text: str,
        chunk_id: Optional[str] = None,
    ) -> Tuple[bool, str, List[str]]:
        """
        Determine if text already exists in the knowledge base.

        Returns tuple of (duplicate?, hash_value, existing_ids).
        """
        hash_value = self.hash_content(text)
        existing = self.hash_index.get(hash_value, set()).copy()
        if chunk_id:
            existing.discard(chunk_id)
        return (len(existing) > 0, hash_value, sorted(existing))

    # ------------------------------------------------------------------ #
    # Batch scanning utilities
    # ------------------------------------------------------------------ #
    def find_duplicates_in_kb(self) -> List[Dict[str, Iterable[str]]]:
        """
        Scan the knowledge base for duplicate hashes.
        """
        duplicates: List[Dict[str, Iterable[str]]] = []
        for hash_value, ids in self.hash_index.items():
            if len(ids) > 1:
                duplicates.append({"hash": hash_value, "ids": sorted(ids)})
        return duplicates

    def remove_duplicates(self, dry_run: bool = True) -> Dict[str, List[str]]:
        """
        Remove duplicate chunks from ChromaDB, keeping the first occurrence.
        """
        duplicates = self.find_duplicates_in_kb()
        to_remove: Dict[str, List[str]] = {}

        for entry in duplicates:
            ids = list(entry["ids"])
            if len(ids) <= 1:
                continue
            keep = ids[0]
            remove_ids = ids[1:]
            to_remove[keep] = remove_ids

        if dry_run or not to_remove:
            logger.info(
                "Deduplication dry-run complete: %d duplicate groups identified",
                len(to_remove),
            )
            return to_remove

        removed_total = 0
        for keeper, ids_to_remove in to_remove.items():
            if not ids_to_remove:
                continue
            logger.warning(
                "Removing %d duplicates for keeper chunk '%s'",
                len(ids_to_remove),
                keeper,
            )
            self.collection.delete(ids=ids_to_remove)
            removed_total += len(ids_to_remove)
            for chunk_id in ids_to_remove:
                hash_value = self.chunk_hash_map.pop(chunk_id, None)
                if not hash_value:
                    continue
                self.hash_index.get(hash_value, set()).discard(chunk_id)
        logger.info("Deduplication removed %d duplicate chunks from ChromaDB", removed_total)
        return to_remove


def _parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deduplication utility for ChromaDB")
    parser.add_argument(
        "--persist-directory",
        "-p",
        default="./chroma_db",
        help="Path to ChromaDB persistence directory",
    )
    parser.add_argument(
        "--auto-remove",
        action="store_true",
        help="Remove duplicates instead of performing a dry-run",
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to JSON config file containing deduplication settings",
    )
    return parser.parse_args()


def _load_config_from_path(path: Optional[str]) -> dict:
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # pragma: no cover - CLI helper
        logger.error("Failed to load config from %s: %s", path, exc)
        return {}


def main() -> None:  # pragma: no cover - CLI helper
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    args = _parse_cli_args()
    config = _load_config_from_path(args.config)
    dedup_config = config.get("deduplication", {}) if isinstance(config, dict) else {}
    if args.auto_remove:
        dedup_config["auto_remove"] = True
        dedup_config["log_only"] = False
        dedup_config["enabled"] = True

    manager = DeduplicationManager(
        persist_directory=args.persist_directory,
        config=dedup_config,
        preload=True,
    )

    dry_run = not args.auto_remove and dedup_config.get("log_only", True)
    duplicates = manager.remove_duplicates(dry_run=dry_run)

    if duplicates:
        logger.info(
            "Duplicate groups identified: %d. Use --auto-remove to delete duplicates.",
            len(duplicates),
        )
    else:
        logger.info("No duplicates found in the knowledge base.")


if __name__ == "__main__":  # pragma: no cover - CLI helper
    main()

