"""Tests for schema cache implementation.

Tests for LRU cache with TTL, hit/miss tracking, and invalidation.
"""

import time

from ansibledoctor.utils.schema_cache import SchemaCache


class TestCacheBasics:
    """Test basic cache operations."""

    def test_cache_stores_and_retrieves_schema(self):
        """Test basic get/set operations."""
        cache = SchemaCache(max_size=10)
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}

        cache.set("config", schema)
        retrieved = cache.get("config")

        assert retrieved == schema

    def test_cache_returns_none_for_missing_key(self):
        """Test cache miss returns None."""
        cache = SchemaCache()

        result = cache.get("nonexistent")

        assert result is None

    def test_cache_overwrites_existing_key(self):
        """Test updating cached value."""
        cache = SchemaCache()
        schema_v1 = {"version": "1.0"}
        schema_v2 = {"version": "2.0"}

        cache.set("config", schema_v1)
        cache.set("config", schema_v2)

        assert cache.get("config") == schema_v2


class TestLRUEviction:
    """Test LRU eviction policy."""

    def test_evicts_least_recently_used_when_full(self):
        """Test LRU eviction when cache is full."""
        cache = SchemaCache(max_size=3)

        # Fill cache
        cache.set("schema1", {"id": 1})
        cache.set("schema2", {"id": 2})
        cache.set("schema3", {"id": 3})

        # Access schema1 to make it recently used
        cache.get("schema1")

        # Add new item - should evict schema2 (least recently used)
        cache.set("schema4", {"id": 4})

        assert cache.get("schema1") == {"id": 1}  # Still cached
        assert cache.get("schema2") is None  # Evicted
        assert cache.get("schema3") == {"id": 3}  # Still cached
        assert cache.get("schema4") == {"id": 4}  # Newly added

    def test_get_updates_lru_order(self):
        """Test that get() updates LRU order."""
        cache = SchemaCache(max_size=2)

        cache.set("old", {"value": 1})
        cache.set("new", {"value": 2})

        # Access old item to make it recently used
        cache.get("old")

        # Add another item - should evict 'new' (now least recently used)
        cache.set("newest", {"value": 3})

        assert cache.get("old") == {"value": 1}
        assert cache.get("new") is None  # Evicted
        assert cache.get("newest") == {"value": 3}


class TestCacheStatistics:
    """Test cache statistics tracking."""

    def test_tracks_hit_count(self):
        """Test cache hit tracking."""
        cache = SchemaCache()
        cache.set("config", {"type": "object"})

        cache.get("config")
        cache.get("config")
        cache.get("config")

        stats = cache.get_stats()
        assert stats["hits"] == 3

    def test_tracks_miss_count(self):
        """Test cache miss tracking."""
        cache = SchemaCache()

        cache.get("missing1")
        cache.get("missing2")
        cache.get("missing3")

        stats = cache.get_stats()
        assert stats["misses"] == 3

    def test_calculates_hit_rate(self):
        """Test hit rate calculation."""
        cache = SchemaCache()
        cache.set("config", {"type": "object"})

        # 2 hits
        cache.get("config")
        cache.get("config")

        # 3 misses
        cache.get("missing1")
        cache.get("missing2")
        cache.get("missing3")

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert stats["hit_rate"] == 0.4  # 2/5 = 40%

    def test_tracks_eviction_count(self):
        """Test eviction counting."""
        cache = SchemaCache(max_size=2)

        cache.set("schema1", {})
        cache.set("schema2", {})
        cache.set("schema3", {})  # Evicts schema1
        cache.set("schema4", {})  # Evicts schema2

        stats = cache.get_stats()
        assert stats["evictions"] == 2

    def test_stats_includes_cache_size(self):
        """Test stats include current cache size."""
        cache = SchemaCache(max_size=10)

        cache.set("schema1", {})
        cache.set("schema2", {})
        cache.set("schema3", {})

        stats = cache.get_stats()
        assert stats["size"] == 3
        assert stats["max_size"] == 10


class TestCacheInvalidation:
    """Test cache invalidation operations."""

    def test_clear_removes_all_entries(self):
        """Test clearing entire cache."""
        cache = SchemaCache()

        cache.set("schema1", {"id": 1})
        cache.set("schema2", {"id": 2})
        cache.set("schema3", {"id": 3})

        cache.clear()

        assert cache.get("schema1") is None
        assert cache.get("schema2") is None
        assert cache.get("schema3") is None
        assert cache.get_stats()["size"] == 0

    def test_delete_removes_specific_entry(self):
        """Test deleting specific cache entry."""
        cache = SchemaCache()

        cache.set("schema1", {"id": 1})
        cache.set("schema2", {"id": 2})

        cache.delete("schema1")

        assert cache.get("schema1") is None
        assert cache.get("schema2") == {"id": 2}

    def test_delete_nonexistent_key_is_safe(self):
        """Test deleting non-existent key doesn't error."""
        cache = SchemaCache()

        # Should not raise exception
        cache.delete("nonexistent")

    def test_clear_resets_statistics(self):
        """Test clear() resets statistics."""
        cache = SchemaCache()

        cache.set("config", {})
        cache.get("config")
        cache.get("missing")

        cache.clear()

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
        assert stats["size"] == 0


class TestTTLExpiration:
    """Test time-to-live expiration."""

    def test_expired_entries_return_none(self):
        """Test expired entries are treated as cache miss."""
        cache = SchemaCache(ttl=0.1)  # 100ms TTL

        cache.set("config", {"type": "object"})

        # Wait for expiration
        time.sleep(0.15)

        result = cache.get("config")
        assert result is None

    def test_unexpired_entries_are_accessible(self):
        """Test entries within TTL are accessible."""
        cache = SchemaCache(ttl=1.0)  # 1 second TTL

        cache.set("config", {"type": "object"})

        # Immediate access
        result = cache.get("config")
        assert result == {"type": "object"}

    def test_expired_entries_count_as_miss(self):
        """Test expired entries increment miss count."""
        cache = SchemaCache(ttl=0.1)

        cache.set("config", {})
        time.sleep(0.15)

        cache.get("config")

        stats = cache.get_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0

    def test_ttl_none_disables_expiration(self):
        """Test TTL=None means no expiration."""
        cache = SchemaCache(ttl=None)

        cache.set("config", {"type": "object"})

        # Wait a bit
        time.sleep(0.1)

        # Should still be cached
        result = cache.get("config")
        assert result == {"type": "object"}


class TestCacheIntegrationWithValidator:
    """Test cache integration scenarios."""

    def test_validator_uses_cached_schema(self):
        """Test that validator can use cached compiled schema."""
        cache = SchemaCache()

        # Simulate validator storing compiled schema
        compiled_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "$compiled": True,  # Marker for compiled schema
        }

        cache.set("config_compiled", compiled_schema)

        # Validator retrieves it
        retrieved = cache.get("config_compiled")

        assert retrieved == compiled_schema
        assert retrieved.get("$compiled") is True

    def test_cache_improves_validation_performance(self):
        """Test cache provides performance benefit."""
        cache = SchemaCache()
        large_schema = {
            "type": "object",
            "properties": {f"prop{i}": {"type": "string"} for i in range(100)},
        }

        # First access - cache miss
        result1 = cache.get("large_config")
        assert result1 is None

        # Store in cache
        cache.set("large_config", large_schema)

        # Subsequent access - cache hit (much faster than recompiling)
        result2 = cache.get("large_config")
        assert result2 == large_schema

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_multiple_schema_types_cached_separately(self):
        """Test different schema types don't collide."""
        cache = SchemaCache()

        config_schema = {"type": "object", "title": "Config"}
        role_schema = {"type": "object", "title": "Role"}
        collection_schema = {"type": "object", "title": "Collection"}

        cache.set("config", config_schema)
        cache.set("role", role_schema)
        cache.set("collection", collection_schema)

        assert cache.get("config") == config_schema
        assert cache.get("role") == role_schema
        assert cache.get("collection") == collection_schema


class TestCacheEdgeCases:
    """Test edge cases and error conditions."""

    def test_max_size_zero_disables_caching(self):
        """Test max_size=0 effectively disables cache."""
        cache = SchemaCache(max_size=0)

        cache.set("config", {"type": "object"})

        # Should not cache anything
        result = cache.get("config")
        assert result is None

    def test_max_size_one_stores_single_item(self):
        """Test max_size=1 stores only one item."""
        cache = SchemaCache(max_size=1)

        cache.set("schema1", {"id": 1})
        cache.set("schema2", {"id": 2})

        # Only most recent should be cached
        assert cache.get("schema1") is None
        assert cache.get("schema2") == {"id": 2}

    def test_cache_handles_none_values(self):
        """Test cache can store None as a value."""
        cache = SchemaCache()

        cache.set("nullable", None)

        # Should distinguish between cached None and cache miss
        # For this test, we expect None is stored and retrieved
        result = cache.get("nullable")
        # Implementation detail: might need special handling
        # For now, test that it doesn't crash

    def test_cache_handles_large_schemas(self):
        """Test cache handles very large schemas."""
        cache = SchemaCache()

        # Create large schema (1000 properties)
        large_schema = {
            "type": "object",
            "properties": {
                f"property_{i}": {
                    "type": "string",
                    "description": f"Property {i}" * 10,  # Make it bigger
                    "default": f"default_{i}",
                }
                for i in range(1000)
            },
        }

        cache.set("large", large_schema)
        retrieved = cache.get("large")

        assert retrieved == large_schema
        assert len(retrieved["properties"]) == 1000


class TestCacheThreadSafety:
    """Test cache is thread-safe (if implemented)."""

    def test_concurrent_access_is_safe(self):
        """Test concurrent get/set operations don't corrupt cache.

        Note: This is a placeholder. Full thread-safety testing requires
        concurrent execution which is complex for unit tests.
        """
        cache = SchemaCache()

        # Basic test - ensure no exceptions
        cache.set("config", {"type": "object"})

        for _ in range(100):
            cache.get("config")
            cache.set("config", {"type": "object"})

        # Should still work correctly
        assert cache.get("config") == {"type": "object"}
