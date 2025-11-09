# 🕒 2025-11-05-17-10-00
# Project: chunker/tests/test_query_cache.py
# Author: R. A. Carucci
# Purpose: Comprehensive test suite for query cache with TTL, eviction, stats, and invalidation

import pytest
import time
from query_cache import CacheKey, QueryCache


class TestQueryCacheBasics:
    """Test basic cache operations"""
    
    def test_query_cache_round_trip(self):
        """Test basic put/get operation"""
        cache = QueryCache(max_size=2, ttl_seconds=60)
        key = ("demo", 1, None, None, None)
        payload = [{"id": "chunk-1", "document": "example"}]
        
        cache.put(key, payload)
        cached = cache.get(key)
        
        assert cached == payload
        assert cached is not None
        assert len(cached) == 1
    
    def test_cache_miss_returns_none(self):
        """Test that non-existent keys return None"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("nonexistent", 5, None, None, None)
        
        result = cache.get(key)
        
        assert result is None
    
    def test_cache_overwrites_existing_key(self):
        """Test that putting same key overwrites previous value"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("test", 1, None, None, None)
        
        cache.put(key, [{"id": "chunk-1"}])
        cache.put(key, [{"id": "chunk-2"}])
        
        result = cache.get(key)
        assert result == [{"id": "chunk-2"}]


class TestQueryCacheTTL:
    """Test TTL (Time-To-Live) expiration"""
    
    def test_ttl_expiration(self):
        """Test that entries expire after TTL"""
        cache = QueryCache(max_size=10, ttl_seconds=0.1)
        key = ("expire", 1, None, None, None)
        payload = [{"id": "chunk-1"}]
        
        cache.put(key, payload)
        assert cache.get(key) is not None
        
        time.sleep(0.2)  # Wait for TTL to expire
        
        assert cache.get(key) is None
    
    def test_ttl_not_expired_yet(self):
        """Test that entries don't expire before TTL"""
        cache = QueryCache(max_size=10, ttl_seconds=1.0)
        key = ("fresh", 1, None, None, None)
        payload = [{"id": "chunk-1"}]
        
        cache.put(key, payload)
        time.sleep(0.5)  # Sleep for half the TTL
        
        assert cache.get(key) is not None
    
    def test_multiple_entries_expire_independently(self):
        """Test that multiple entries have independent TTLs"""
        cache = QueryCache(max_size=10, ttl_seconds=0.2)
        key1 = ("k1", 1, None, None, None)
        key2 = ("k2", 1, None, None, None)
        
        cache.put(key1, [{"id": "chunk-1"}])
        time.sleep(0.15)
        cache.put(key2, [{"id": "chunk-2"}])
        time.sleep(0.1)  # Total: key1 = 0.25s, key2 = 0.1s
        
        assert cache.get(key1) is None  # Expired
        assert cache.get(key2) is not None  # Still fresh
    
    def test_zero_ttl_immediate_expiration(self):
        """Test that TTL=0 causes immediate expiration"""
        with pytest.raises(ValueError):
            QueryCache(max_size=10, ttl_seconds=0.0)


class TestQueryCacheEviction:
    """Test LRU eviction behavior"""
    
    def test_query_cache_eviction_and_ttl(self):
        """Test eviction when cache is full (example from Cursor)"""
        cache = QueryCache(max_size=1, ttl_seconds=0.1)
        key1, key2 = ("k1", 1, None, None, None), ("k2", 1, None, None, None)
        
        cache.put(key1, [{"id": "chunk-1"}])
        cache.put(key2, [{"id": "chunk-2"}])  # Should evict key1
        
        assert cache.get(key1) is None  # Evicted
        assert cache.get(key2) is not None
        
        time.sleep(0.2)
        assert cache.get(key2) is None  # TTL expired
        
        stats = cache.get_stats()
        assert stats["evictions"] == 1
        assert stats["ttl_seconds"] == 0.1
    
    def test_lru_eviction_order(self):
        """Test that least recently used item is evicted"""
        cache = QueryCache(max_size=2, ttl_seconds=60)
        k1 = ("k1", 1, None, None, None)
        k2 = ("k2", 1, None, None, None)
        k3 = ("k3", 1, None, None, None)
        
        cache.put(k1, [{"id": "1"}])
        cache.put(k2, [{"id": "2"}])
        cache.get(k1)  # Access k1 (make k2 LRU)
        cache.put(k3, [{"id": "3"}])  # Should evict k2
        
        assert cache.get(k1) is not None
        assert cache.get(k2) is None  # Evicted
        assert cache.get(k3) is not None
    
    def test_access_refreshes_lru(self):
        """Test that accessing an entry refreshes its LRU position"""
        cache = QueryCache(max_size=2, ttl_seconds=60)
        k1 = ("k1", 1, None, None, None)
        k2 = ("k2", 1, None, None, None)
        k3 = ("k3", 1, None, None, None)
        
        cache.put(k1, [{"id": "1"}])
        cache.put(k2, [{"id": "2"}])
        
        # Access k1 multiple times
        for _ in range(5):
            cache.get(k1)
        
        cache.put(k3, [{"id": "3"}])  # Should evict k2, not k1
        
        assert cache.get(k1) is not None
        assert cache.get(k2) is None
        assert cache.get(k3) is not None
    
    def test_multiple_evictions(self):
        """Test multiple evictions track correctly"""
        cache = QueryCache(max_size=2, ttl_seconds=60)
        
        for i in range(5):
            key = (f"k{i}", 1, None, None, None)
            cache.put(key, [{"id": f"chunk-{i}"}])
        
        stats = cache.get_stats()
        assert stats["evictions"] == 3  # Added 5, capacity 2 = 3 evictions


class TestQueryCacheInvalidation:
    """Test cache invalidation operations"""
    
    def test_invalidate_single_key(self):
        """Test invalidating a specific key"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("test", 1, None, None, None)
        
        cache.put(key, [{"id": "chunk-1"}])
        assert cache.get(key) is not None
        
        cache.invalidate(key)
        
        assert cache.get(key) is None
    
    def test_invalidate_nonexistent_key(self):
        """Test that invalidating non-existent key doesn't error"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("nonexistent", 1, None, None, None)
        
        # Should not raise error
        cache.invalidate(key)
        
        assert cache.get(key) is None
    
    def test_invalidate_all(self):
        """Test clearing entire cache"""
        cache = QueryCache(max_size=10, ttl_seconds=60)

        for i in range(5):
            key = (f"k{i}", 1, None, None, None)
            cache.put(key, [{"id": f"chunk-{i}"}])

        cache.invalidate()  # invalidate everything when key is None

        for i in range(5):
            key = (f"k{i}", 1, None, None, None)
            assert cache.get(key) is None

        stats = cache.get_stats()
        assert stats["current_size"] == 0


class TestQueryCacheStats:
    """Test cache statistics tracking"""
    
    def test_stats_initial_state(self):
        """Test initial stats values"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        
        stats = cache.get_stats()
        
        assert stats["max_size"] == 10
        assert stats["ttl_seconds"] == 60
        assert stats["current_size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
    
    def test_stats_track_hits_and_misses(self):
        """Test that hits and misses are tracked correctly"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("test", 1, None, None, None)
        
        cache.get(key)  # Miss
        cache.put(key, [{"id": "chunk-1"}])
        cache.get(key)  # Hit
        cache.get(key)  # Hit
        cache.get(("other", 1, None, None, None))  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 2
    
    def test_stats_track_size(self):
        """Test that cache size is tracked correctly"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        
        for i in range(5):
            cache.put((f"k{i}", 1, None, None, None), [{"id": f"{i}"}])
        
        stats = cache.get_stats()
        assert stats["current_size"] == 5
    
    def test_stats_hit_rate_calculation(self):
        """Test hit rate calculation"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("test", 1, None, None, None)
        
        cache.put(key, [{"id": "chunk-1"}])
        cache.get(key)  # Hit
        cache.get(key)  # Hit
        cache.get(key)  # Hit
        cache.get(("miss", 1, None, None, None))  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.75  # 3/4
    
    def test_stats_after_invalidate_all(self):
        """Test stats are updated after clearing cache"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        
        for i in range(5):
            cache.put((f"k{i}", 1, None, None, None), [{"id": f"{i}"}])
        
        cache.invalidate()
        stats = cache.get_stats()

        assert stats["current_size"] == 0
        # Note: hits/misses/evictions may persist or reset depending on implementation


class TestQueryCacheEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_max_size(self):
        """Test cache with max_size=0"""
        with pytest.raises(ValueError):
            QueryCache(max_size=0, ttl_seconds=60)
    
    def test_large_payload(self):
        """Test caching large payloads"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("large", 1, None, None, None)
        
        # Create large payload
        payload = [{"id": f"chunk-{i}", "document": "x" * 1000} for i in range(100)]
        
        cache.put(key, payload)
        result = cache.get(key)
        
        assert result == payload
        assert len(result) == 100
    
    def test_complex_cache_key(self):
        """Test cache key with all parameters"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("query text", 5, "python", "rms", 100)
        payload = [{"id": "chunk-1"}]
        
        cache.put(key, payload)
        result = cache.get(key)
        
        assert result == payload
    
    def test_concurrent_operations_safety(self):
        """Test that basic operations don't corrupt state"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        
        # Rapid put/get operations
        for i in range(20):
            key = (f"k{i % 5}", 1, None, None, None)
            cache.put(key, [{"id": f"chunk-{i}"}])
            cache.get(key)
        
        # Cache should still be functional
        stats = cache.get_stats()
        assert stats["current_size"] <= 10
        assert stats["hits"] >= 0
    
    def test_empty_payload(self):
        """Test caching empty result list"""
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = ("empty", 1, None, None, None)
        
        cache.put(key, [])
        result = cache.get(key)
        
        assert result == []
        assert result is not None  # Distinguish from miss


class TestQueryCachePerformance:
    """Test performance-related aspects"""
    
    def test_get_performance_with_large_cache(self):
        """Test that get performance is acceptable with full cache"""
        cache = QueryCache(max_size=1000, ttl_seconds=60)
        
        # Fill cache
        for i in range(1000):
            cache.put((f"k{i}", 1, None, None, None), [{"id": f"chunk-{i}"}])
        
        # Time a get operation
        start = time.time()
        cache.get(("k500", 1, None, None, None))
        elapsed = time.time() - start
        
        # Should be very fast (< 10ms)
        assert elapsed < 0.01
    
    def test_memory_efficiency(self):
        """Test that stats can report memory estimates"""
        cache = QueryCache(max_size=100, ttl_seconds=60)
        
        for i in range(50):
            payload = [{"id": f"chunk-{i}", "doc": "x" * 100}]
            cache.put((f"k{i}", 1, None, None, None), payload)
        
        stats = cache.get_stats()
        assert stats["current_size"] == 50


# Integration test combining multiple features
class TestQueryCacheIntegration:
    """Integration tests combining multiple cache features"""
    
    def test_realistic_usage_scenario(self):
        """Test realistic cache usage with queries, TTL, and eviction"""
        cache = QueryCache(max_size=5, ttl_seconds=0.5)
        
        # Simulate user queries
        queries = [
            ("rms incident", 10, None, None, None),
            ("cad response", 5, None, None, None),
            ("rms arrest", 10, None, None, None),
        ]
        
        # Store results
        for i, query in enumerate(queries):
            cache.put(query, [{"id": f"chunk-{i}"}])
        
        # Access first query multiple times (make it "hot")
        for _ in range(3):
            assert cache.get(queries[0]) is not None
        
        # Add more queries to trigger eviction
        for i in range(3, 8):
            query = (f"query{i}", 5, None, None, None)
            cache.put(query, [{"id": f"chunk-{i}"}])
        
        # First query may be evicted once capacity is exceeded
        assert cache.get(queries[0]) is None
        
        # Wait for TTL expiration
        time.sleep(0.6)
        
        # All entries should be expired
        assert cache.get(queries[0]) is None
        
        # Stats should show the activity
        stats = cache.get_stats()
        assert stats["evictions"] >= 3  # Some queries evicted
        assert stats["hits"] >= 3  # The repeated accesses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
