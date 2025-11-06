"""
Query cache utilities for RAG search results.

Provides an in-memory LRU cache with TTL support and optional memory limits.
"""

from __future__ import annotations

import sys
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Dict, Hashable, Optional, Tuple


CacheKey = Tuple[Hashable, ...]


@dataclass
class _CacheEntry:
    value: Any
    created_at: float
    size_bytes: int


class QueryCache:
    """
    Thread-safe LRU cache with TTL for Query -> Result mappings.
    """

    def __init__(
        self,
        max_size: int,
        ttl_seconds: float,
        memory_limit_bytes: Optional[int] = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._max_size = max_size
        self._ttl = ttl_seconds
        self._memory_limit = memory_limit_bytes
        self._clock = clock

        self._lock = threading.RLock()
        self._entries: "OrderedDict[CacheKey, _CacheEntry]" = OrderedDict()

        # Metrics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._invalidations = 0
        self._memory_usage = 0

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def get(self, key: CacheKey) -> Optional[Any]:
        """
        Retrieve cached value if present and not expired.
        """
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._misses += 1
                return None

            if self._is_expired(entry):
                self._remove_entry(key, entry)
                self._misses += 1
                return None

            # Move to end to preserve LRU ordering
            self._entries.move_to_end(key)
            self._hits += 1
            return entry.value

    def put(self, key: CacheKey, value: Any, size_bytes: Optional[int] = None) -> None:
        """
        Insert or update cache entry.
        """
        with self._lock:
            entry_size = self._estimate_size(value) if size_bytes is None else size_bytes

            existing = self._entries.pop(key, None)
            if existing:
                self._memory_usage -= existing.size_bytes

            new_entry = _CacheEntry(value=value, created_at=self._clock(), size_bytes=entry_size)
            self._entries[key] = new_entry
            self._memory_usage += entry_size

            self._evict_if_needed()

    def invalidate(self, key: Optional[CacheKey] = None) -> None:
        """
        Invalidate single key or entire cache when key is None.
        """
        with self._lock:
            if key is None:
                removed = len(self._entries)
                self._entries.clear()
                self._memory_usage = 0
                self._invalidations += removed
                return

            entry = self._entries.pop(key, None)
            if entry:
                self._memory_usage -= entry.size_bytes
                self._invalidations += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Return cache metrics snapshot.
        """
        with self._lock:
            return {
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
                "memory_limit_bytes": self._memory_limit,
                "current_size": len(self._entries),
                "memory_usage_bytes": self._memory_usage,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._compute_hit_rate(),
                "evictions": self._evictions,
                "invalidations": self._invalidations,
            }

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _is_expired(self, entry: _CacheEntry) -> bool:
        return (self._clock() - entry.created_at) >= self._ttl

    def _evict_if_needed(self) -> None:
        # Evict based on size limit
        while len(self._entries) > self._max_size:
            self._evict_oldest()

        if self._memory_limit is not None:
            while self._memory_usage > self._memory_limit and self._entries:
                self._evict_oldest()

    def _evict_oldest(self) -> None:
        key, entry = self._entries.popitem(last=False)
        self._memory_usage -= entry.size_bytes
        self._evictions += 1

    def _remove_entry(self, key: CacheKey, entry: _CacheEntry) -> None:
        del self._entries[key]
        self._memory_usage -= entry.size_bytes
        self._invalidations += 1

    @staticmethod
    def _estimate_size(value: Any) -> int:
        """
        Helper to approximate the size of cached value.
        """
        try:
            return sys.getsizeof(value)
        except TypeError:
            return 0

    def _compute_hit_rate(self) -> float:
        total = self._hits + self._misses
        return (self._hits / total) if total else 0.0


__all__ = ["QueryCache", "CacheKey"]

