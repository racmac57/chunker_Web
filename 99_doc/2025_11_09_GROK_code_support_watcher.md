File 'incremental_updates.py' missing, causing import failure. Fallback in watcher_splitter.py fixes build_chunk_id. Keep "incremental_updates.enabled": false in config.json.

Implement incremental_updates.py
import json
import logging
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class VersionTracker:
    def __init__(self, config: Dict, logger: Optional[logging.Logger] = None):
        self.version_file = Path(config["version_file"])
        self.hash_algorithm = config.get("hash_algorithm", "sha256")
        self.move_unchanged_to_archive = config.get("move_unchanged_to_archive", True)
        self.logger = logger or logging.getLogger(__name__)
        self.versions: Dict[str, str] = self._load_versions()

    def _load_versions(self) -> Dict[str, str]:
        if self.version_file.exists():
            try:
                with open(self.version_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load versions: {e}")
                return {}
        return {}

    def _save_versions(self) -> None:
        try:
            self.version_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.version_file, "w", encoding="utf-8") as f:
                json.dump(self.versions, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save versions: {e}")

    def compute_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.new(self.hash_algorithm)
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to hash {file_path}: {e}")
            raise

    def is_unchanged(self, file_path: str, file_hash: str) -> bool:
        stored_hash = self.versions.get(file_path)
        return stored_hash == file_hash

    def update_version(self, file_path: str, file_hash: str) -> None:
        self.versions[file_path] = file_hash
        self._save_versions()

    def remove_old_artifacts(self, file_path: str, output_dir: str) -> int:
        file_stem = Path(file_path).stem
        old_folder = Path(output_dir) / file_stem
        if old_folder.exists():
            try:
                count = len(list(old_folder.iterdir()))
                shutil.rmtree(old_folder)
                self.logger.info(f"Removed {count} old artifacts for {file_path}")
                return count
            except Exception as e:
                self.logger.warning(f"Failed to remove old artifacts for {file_path}: {e}")
                return 0
        return 0

def build_chunk_id(timestamp: str, base_name: str, chunk_index: int) -> str:
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    safe_ts = timestamp.replace(" ", "_").replace(":", "-")
    safe_base = base_name.replace(" ", "_")
    return f"{safe_ts}:{safe_base}:{chunk_index:05d}"

C:\Users\carucci_r\Downloads\VisualStudioSetup.exe
import chromadb
import hashlib
import logging
from typing import Dict, List
from chromadb.types import Collection

logger = logging.getLogger(__name__)

class DeduplicationManager:
    def __init__(self, persist_directory: str, config: Dict, preload: bool = True):
        self.persist_directory = persist_directory
        self.config = config
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection: Collection = self.client.get_or_create_collection(name="chunks")
        self.hash_index: set[str] = set()
        if preload:
            self._load_hashes()

    def _load_hashes(self) -> None:
        data = self.collection.get(include=['documents'])
        for doc in data['documents']:
            h = self.compute_hash(doc)
            self.hash_index.add(h)

    def normalize_text(self, text: str) -> str:
        norm = self.config.get('hash_normalization', {})
        if norm.get('lowercase', True):
            text = text.lower()
        if norm.get('strip', True):
            text = text.strip()
        if norm.get('collapse_whitespace', True):
            text = ' '.join(text.split())
        return text

    def compute_hash(self, text: str) -> str:
        norm_text = self.normalize_text(text)
        return hashlib.sha256(norm_text.encode('utf-8')).hexdigest()

    def is_duplicate(self, text: str) -> bool:
        h = self.compute_hash(text)
        return h in self.hash_index

    def register(self, text: str) -> bool:
        h = self.compute_hash(text)
        if h not in self.hash_index:
            self.hash_index.add(h)
            return True
        return False

    def prune_duplicates(self, auto_remove: bool = False, log_only: bool = True, batch_size: int = 200) -> int:
        seen: Dict[str, List[str]] = {}
        data = self.collection.get(include=['documents'])
        for id, doc in zip(data['ids'], data['documents']):
            h = self.compute_hash(doc)
            if h not in seen:
                seen[h] = []
            seen[h].append(id)
        to_remove = []
        for h, ids in seen.items():
            if len(ids) > 1:
                keep = ids[0]
                dups = ids[1:]
                if log_only:
                    logger.info(f"Found {len(dups)} duplicates for hash {h} (keeping {keep})")
                to_remove.extend(dups)
        if auto_remove and to_remove:
            for i in range(0, len(to_remove), batch_size):
                batch = to_remove[i:i + batch_size]
                self.collection.delete(ids=batch)
                logger.info(f"Removed {len(batch)} duplicates")
        return len(to_remove)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deduplication tool")
    parser.add_argument("--auto-remove", action="store_true", help="Automatically remove duplicates")
    args = parser.parse_args()
    config = {
        "hash_normalization": {
            "lowercase": True,
            "strip": True,
            "collapse_whitespace": True
        }
    }
    manager = DeduplicationManager("./chroma_db", config, preload=True)
    removed = manager.prune_duplicates(auto_remove=args.auto_remove, log_only=not args.auto_remove)
    logger.info(f"Detected {removed} duplicates")

Optimize for large-scale deduplication
import chromadb
import hashlib
import logging
import numpy as np
from typing import Dict, List, Union
from chromadb.types import Collection
from scipy.spatial.distance import cdist
import networkx as nx  # For hash-based if needed; otherwise use UnionFind for efficiency

logger = logging.getLogger(__name__)

class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, p: int) -> int:
        if self.parent[p] != p:
            self.parent[p] = self.find(self.parent[p])
        return self.parent[p]

    def union(self, p: int, q: int) -> None:
        rootP = self.find(p)
        rootQ = self.find(q)
        if rootP == rootQ:
            return
        if self.rank[rootP] < self.rank[rootQ]:
            self.parent[rootP] = rootQ
        elif self.rank[rootP] > self.rank[rootQ]:
            self.parent[rootQ] = rootP
        else:
            self.parent[rootQ] = rootP
            self.rank[rootP] += 1

class DeduplicationManager:
    def __init__(self, persist_directory: str, config: Dict, preload: bool = False):
        self.persist_directory = persist_directory
        self.config = config
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection: Collection = self.client.get_or_create_collection(name="chunks")
        # No preload for large scale

    def normalize_text(self, text: str) -> str:
        norm = self.config.get('hash_normalization', {})
        if norm.get('lowercase', True):
            text = text.lower()
        if norm.get('strip', True):
            text = text.strip()
        if norm.get('collapse_whitespace', True):
            text = ' '.join(text.split())
        return text

    def compute_hash(self, text: str) -> str:
        norm_text = self.normalize_text(text)
        return hashlib.sha256(norm_text.encode('utf-8')).hexdigest()

    def is_duplicate(self, text: str) -> bool:
        h = self.compute_hash(text)
        result = self.collection.get(where={"hash": h}, limit=1, include=[])
        return len(result['ids']) > 0

    def register(self, text: str) -> bool:
        h = self.compute_hash(text)
        if self.is_duplicate(text):
            return False
        self.collection.add(documents=[text], metadatas=[{"hash": h}])
        return True

    def prune_duplicates(self, auto_remove: bool = False, log_only: bool = True, batch_size: int = 200) -> int:
        total = self.collection.count()
        seen: Dict[str, List[str]] = {}
        offset = 0
        while offset < total:
            data = self.collection.get(limit=batch_size, offset=offset, include=['metadatas'])
            for id, meta in zip(data['ids'], data['metadatas']):
                h = meta.get('hash')
                if h not in seen:
                    seen[h] = []
                seen[h].append(id)
            offset += batch_size
        to_remove = []
        for h, ids in seen.items():
            if len(ids) > 1:
                keep = ids[0]
                dups = ids[1:]
                if log_only:
                    logger.info(f"Found {len(dups)} duplicates for hash {h} (keeping {keep})")
                to_remove.extend(dups)
        if auto_remove and to_remove:
            for i in range(0, len(to_remove), batch_size):
                batch = to_remove[i:i + batch_size]
                self.collection.delete(ids=batch)
                logger.info(f"Removed {len(batch)} duplicates")
        return len(to_remove)

class SemanticDeduplicationManager:
    def __init__(self, persist_directory: str, config: Dict):
        self.persist_directory = persist_directory
        self.config = config
        self.threshold = config.get('semantic_threshold', 0.05)
        self.client = chromadb.PersistentClient(path=persist_directory)
        metadata = {"hnsw:space": "cosine"}
        self.collection: Collection = self.client.get_or_create_collection(name="chunks", metadata=metadata)

    def is_duplicate(self, text: str) -> bool:
        results = self.collection.query(query_texts=[text], n_results=2, include=["distances"])
        if results['distances'] and results['distances'][0]:
            distances = results['distances'][0]
            min_dist = min(d for d in distances if d > 0)  # Exclude self
            return min_dist < self.threshold
        return False

    def register(self, text: str, embedding: Optional[np.ndarray] = None, metadata: Optional[Dict] = None, id: Optional[str] = None) -> bool:
        if self.is_duplicate(text):
            return False
        self.collection.add(documents=[text], embeddings=[embedding] if embedding is not None else None, 
                            metadatas=[metadata] if metadata else None, ids=[id] if id else None)
        return True

    def prune_duplicates(self, auto_remove: bool = False, log_only: bool = True, batch_size: int = 200, graph_batch_size: int = 1000) -> int:
        total = self.collection.count()
        all_ids: List[str] = []
        all_emb: List[np.ndarray] = []
        offset = 0
        while offset < total:
            data = self.collection.get(limit=batch_size, offset=offset, include=['embeddings'])
            all_ids.extend(data['ids'])
            all_emb.extend(data['embeddings'])
            offset += batch_size
        all_emb_np = np.array(all_emb)
        n = len(all_ids)
        uf = UnionFind(n)
        for i in range(0, n, graph_batch_size):
            batch_emb = all_emb_np[i:i+graph_batch_size]
            dists = cdist(batch_emb, all_emb_np, metric='cosine')
            rows, cols = np.where((dists < self.threshold) & (dists > 0))
            for r, c in zip(rows, cols):
                if i + r < c:  # Avoid self and duplicates
                    uf.union(i + r, c)
        # Group by root
        components: Dict[int, List[int]] = {}
        for idx in range(n):
            root = uf.find(idx)
            if root not in components:
                components[root] = []
            components[root].append(idx)
        to_remove = []
        for comp in components.values():
            if len(comp) > 1:
                keep_idx = min(comp)  # Keep smallest index
                dups = [all_ids[idx] for idx in comp if idx != keep_idx]
                if log_only:
                    logger.info(f"Duplicate group: {[all_ids[idx] for idx in comp]}, keeping {all_ids[keep_idx]}")
                to_remove.extend(dups)
        if auto_remove and to_remove:
            for i in range(0, len(to_remove), batch_size):
                batch = to_remove[i:i + batch_size]
                self.collection.delete(ids=batch)
                logger.info(f"Removed {len(batch)} semantic duplicates")
        return len(to_remove)
