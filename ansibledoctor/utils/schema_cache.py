"""Schema cache implementation with LRU eviction and TTL support.

Provides caching for compiled JSON schemas to improve validation performance.
"""

import time
from collections import OrderedDict
from typing import Any, Dict, Optional


class SchemaCache:
    """LRU cache for compiled schemas with optional TTL expiration.

    Provides:
    - LRU (Least Recently Used) eviction policy
    - Optional time-to-live (TTL) for cache entries
    - Hit/miss/eviction statistics tracking
    - Thread-safe operations (basic)

    Usage:
        cache = SchemaCache(max_size=100, ttl=3600)
        cache.set("config", compiled_schema)
        schema = cache.get("config")
        stats = cache.get_stats()
    """

    def __init__(self, max_size: int = 100, ttl: Optional[float] = None):
        """Initialize schema cache.

        Args:
            max_size: Maximum number of schemas to cache (0 disables caching)
            ttl: Time-to-live in seconds (None means no expiration)
        """
        self.max_size = max_size
        self.ttl = ttl

        # OrderedDict maintains insertion order and provides O(1) move_to_end()
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve schema from cache.

        Args:
            key: Cache key (e.g., "config", "role", "collection")

        Returns:
            Cached schema or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]

        # Check TTL expiration
        if self.ttl is not None:
            if time.time() - entry["timestamp"] > self.ttl:
                # Expired - treat as miss and remove
                del self._cache[key]
                self._misses += 1
                return None

        # Cache hit - move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1

        return entry["schema"]

    def set(self, key: str, schema: Dict[str, Any]) -> None:
        """Store schema in cache.

        Args:
            key: Cache key
            schema: Schema to cache
        """
        # Disable caching if max_size is 0
        if self.max_size == 0:
            return

        # If key exists, remove it first (will be re-added at end)
        if key in self._cache:
            del self._cache[key]

        # Add new entry with timestamp
        self._cache[key] = {"schema": schema, "timestamp": time.time()}

        # Enforce max size - evict oldest (first item)
        if len(self._cache) > self.max_size:
            # popitem(last=False) removes first (oldest) item
            self._cache.popitem(last=False)
            self._evictions += 1

    def delete(self, key: str) -> None:
        """Remove specific entry from cache.

        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with hit/miss/eviction counts, hit rate, and size
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
        }
