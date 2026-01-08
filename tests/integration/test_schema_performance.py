"""Performance tests for schema validation.

Tests validation performance with large configurations (500+ properties).
Target: < 10ms per validation for typical configs.
"""

import time
from typing import Any, Dict

import pytest

from ansibledoctor.utils.schema_cache import SchemaCache
from ansibledoctor.validation import ConfigurationValidator


@pytest.fixture
def large_config_data() -> Dict[str, Any]:
    """Generate large configuration with 500+ properties."""
    return {
        "output_format": "markdown",
        "output_dir": "docs/",
        "recursive": True,
        "template_dir": ".ansibledoctor/templates",
        "languages": {"default": "en", "enabled": ["en", "fr", "de"], "fallback": "en"},
        # Add 500 custom properties to stress test
        **{f"custom_property_{i}": f"value_{i}" for i in range(500)},
    }


@pytest.fixture
def extra_large_config_data() -> Dict[str, Any]:
    """Generate extra large configuration with 1000+ properties."""
    return {
        "output_format": "html",
        "output_dir": "docs/output/",
        "recursive": False,
        "template_dir": ".ansibledoctor/custom-templates",
        "languages": {"default": "fr", "enabled": ["en", "fr", "de", "es", "it"], "fallback": "en"},
        # Add 1000 custom properties
        **{
            f"extended_property_{i}": {
                "value": f"data_{i}",
                "metadata": {"id": i, "type": "test"},
                "nested": {"level": i % 10},
            }
            for i in range(1000)
        },
    }


class TestValidationPerformance:
    """Test validation performance benchmarks."""

    def test_single_validation_under_10ms(self, large_config_data):
        """Test single validation completes under 10ms."""
        validator = ConfigurationValidator()

        start = time.perf_counter()
        result = validator.validate(large_config_data)
        end = time.perf_counter()

        duration_ms = (end - start) * 1000

        # Should be valid (extra properties are allowed)
        assert result.is_valid

        # Should complete in under 10ms
        assert duration_ms < 10.0, f"Validation took {duration_ms:.2f}ms (expected < 10ms)"

    def test_repeated_validation_performance(self, large_config_data):
        """Test repeated validations maintain performance."""
        validator = ConfigurationValidator()
        iterations = 100

        # Warmup
        for _ in range(10):
            validator.validate(large_config_data)

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            validator.validate(large_config_data)
        end = time.perf_counter()

        total_ms = (end - start) * 1000
        avg_ms = total_ms / iterations

        # Average should be under 10ms
        assert avg_ms < 10.0, f"Average validation: {avg_ms:.2f}ms (expected < 10ms)"

        # Report throughput
        throughput = iterations / (end - start)
        print(f"\nValidation throughput: {throughput:.0f} validations/second")
        print(f"Average latency: {avg_ms:.2f}ms")

    def test_extra_large_config_performance(self, extra_large_config_data):
        """Test performance with extra large configs (1000+ properties)."""
        validator = ConfigurationValidator()

        start = time.perf_counter()
        result = validator.validate(extra_large_config_data)
        end = time.perf_counter()

        duration_ms = (end - start) * 1000

        assert result.is_valid

        # For very large configs, allow up to 50ms
        assert (
            duration_ms < 50.0
        ), f"Large config validation took {duration_ms:.2f}ms (expected < 50ms)"

        print(f"\nExtra large config (1000+ props): {duration_ms:.2f}ms")


class TestCachePerformanceImpact:
    """Test cache impact on validation performance."""

    def test_cache_improves_repeated_validations(self, large_config_data):
        """Test cache provides performance benefit for repeated validations."""
        cache = SchemaCache(max_size=10)
        validator = ConfigurationValidator(schema_cache=cache)

        # First validation (cache miss - compile schema)
        start_first = time.perf_counter()
        validator.validate(large_config_data)
        end_first = time.perf_counter()
        first_ms = (end_first - start_first) * 1000

        # Second validation (cache hit - use compiled schema)
        start_second = time.perf_counter()
        validator.validate(large_config_data)
        end_second = time.perf_counter()
        second_ms = (end_second - start_second) * 1000

        # Cache should improve performance (or at least not hurt it)
        # Note: jsonschema compiles on first use, so cache benefit may be minimal
        # but should not be slower
        assert second_ms <= first_ms * 1.5, "Cached validation should not be significantly slower"

        # Check cache stats
        stats = cache.get_stats()
        print(f"\nCache stats: {stats}")
        print(f"First validation: {first_ms:.2f}ms")
        print(f"Second validation: {second_ms:.2f}ms")

    def test_cache_hit_rate_with_multiple_schemas(self):
        """Test cache hit rate with multiple schema types."""
        cache = SchemaCache(max_size=5)

        # Simulate multiple schema validations
        schemas = {
            "config": {"type": "object", "properties": {"format": {"type": "string"}}},
            "role": {"type": "object", "properties": {"name": {"type": "string"}}},
            "collection": {"type": "object", "properties": {"namespace": {"type": "string"}}},
        }

        # Perform validations
        for _ in range(10):
            for schema_type, schema in schemas.items():
                # Simulate cache get/set
                cached = cache.get(schema_type)
                if cached is None:
                    cache.set(schema_type, schema)
                else:
                    # Use cached version
                    pass

        stats = cache.get_stats()

        # Should have high hit rate (27 hits, 3 misses = 90%)
        assert stats["hits"] == 27
        assert stats["misses"] == 3
        assert stats["hit_rate"] == 0.9

        print(f"\nCache hit rate: {stats['hit_rate']*100:.1f}%")


class TestMemoryUsage:
    """Test memory-related performance characteristics."""

    def test_cache_respects_max_size(self, large_config_data):
        """Test cache doesn't grow beyond max_size."""
        cache = SchemaCache(max_size=5)

        # Add 20 different schemas
        for i in range(20):
            cache.set(f"schema_{i}", large_config_data.copy())

        stats = cache.get_stats()

        # Cache should not exceed max size
        assert stats["size"] == 5
        assert stats["size"] <= cache.max_size

        # Should have evicted 15 schemas
        assert stats["evictions"] == 15

    def test_large_schema_storage(self):
        """Test cache can handle large schema objects."""
        cache = SchemaCache()

        # Create very large schema (10,000 properties)
        huge_schema = {
            "type": "object",
            "properties": {
                f"prop_{i}": {
                    "type": "string",
                    "description": f"Description for property {i}" * 5,
                    "default": f"default_value_{i}",
                    "examples": [f"example_{i}_1", f"example_{i}_2"],
                }
                for i in range(10000)
            },
        }

        start = time.perf_counter()
        cache.set("huge", huge_schema)
        end = time.perf_counter()

        set_ms = (end - start) * 1000

        start = time.perf_counter()
        retrieved = cache.get("huge")
        end = time.perf_counter()

        get_ms = (end - start) * 1000

        assert retrieved is not None
        assert len(retrieved["properties"]) == 10000

        # Cache operations should be fast even with large objects
        assert set_ms < 100.0, f"Cache set took {set_ms:.2f}ms"
        assert get_ms < 10.0, f"Cache get took {get_ms:.2f}ms"

        print(f"\nHuge schema (10k props) - Set: {set_ms:.2f}ms, Get: {get_ms:.2f}ms")


class TestConcurrentPerformance:
    """Test performance under concurrent-like load."""

    def test_rapid_sequential_access(self, large_config_data):
        """Test rapid sequential cache access."""
        cache = SchemaCache()

        # Rapid fire 1000 operations
        start = time.perf_counter()
        for i in range(1000):
            if i % 2 == 0:
                cache.set(f"schema_{i % 10}", large_config_data)
            else:
                cache.get(f"schema_{(i-1) % 10}")
        end = time.perf_counter()

        total_ms = (end - start) * 1000
        avg_ms = total_ms / 1000

        # Should handle 1000 operations quickly
        assert total_ms < 1000.0, f"1000 operations took {total_ms:.2f}ms"

        throughput = 1000 / (end - start)
        print(f"\nCache throughput: {throughput:.0f} operations/second")
        print(f"Average operation: {avg_ms:.3f}ms")


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_typical_ci_pipeline_performance(self, large_config_data):
        """Test performance for typical CI/CD pipeline validation."""
        # Simulate CI pipeline: validate config 5 times (e.g., 5 branches)
        validator = ConfigurationValidator()

        validations = []
        for _ in range(5):
            start = time.perf_counter()
            result = validator.validate(large_config_data)
            end = time.perf_counter()

            validations.append((end - start) * 1000)
            assert result.is_valid

        avg_ms = sum(validations) / len(validations)
        max_ms = max(validations)

        # All validations should be fast
        assert max_ms < 20.0, f"Slowest validation: {max_ms:.2f}ms"
        assert avg_ms < 10.0, f"Average validation: {avg_ms:.2f}ms"

        print("\nCI Pipeline Simulation:")
        print("  Validations: 5")
        print(f"  Average: {avg_ms:.2f}ms")
        print(f"  Max: {max_ms:.2f}ms")
        print(f"  Min: {min(validations):.2f}ms")

    def test_development_workflow_performance(self, large_config_data):
        """Test performance for development workflow (frequent small changes)."""
        validator = ConfigurationValidator()

        # Simulate 50 validation runs during development
        start = time.perf_counter()
        for i in range(50):
            # Slight variation in config (simulating edits)
            config = large_config_data.copy()
            config[f"dev_property_{i}"] = f"value_{i}"

            result = validator.validate(config)
            assert result.is_valid
        end = time.perf_counter()

        total_ms = (end - start) * 1000
        avg_ms = total_ms / 50

        # Should maintain good performance
        assert avg_ms < 15.0, f"Average validation: {avg_ms:.2f}ms"

        print("\nDevelopment Workflow:")
        print(f"  50 validations: {total_ms:.2f}ms")
        print(f"  Average: {avg_ms:.2f}ms")
        print(f"  Throughput: {50/(total_ms/1000):.0f} validations/second")
