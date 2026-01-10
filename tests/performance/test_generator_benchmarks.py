"""
Performance benchmarks for documentation generator.

Uses progressive tolerance thresholds to avoid false positives from CI variance:
- Target: Optimal performance goal
- Warning: Acceptable degradation (test passes with warning)
- Failure: Significant regression (test fails)

Thresholds:
- Small role (10 vars): Target <60ms, Warn 60-80ms, Fail >80ms
- Medium role (50 vars): Target <100ms, Warn 100-130ms, Fail >130ms
- Large role (100 vars): Target <200ms, Warn 200-250ms, Fail >250ms

This approach provides performance feedback without blocking CI on minor variations
due to shared resources, Windows/Linux differences, or runner load.
"""

import time
import warnings
from datetime import datetime

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable
from ansibledoctor.models.variable import VariableType


@pytest.fixture
def small_role(tmp_path):
    """Create a small role with 10 variables for benchmarking."""
    variables = [
        Variable(
            name=f"var_{i}",
            value=f"value_{i}",
            type=VariableType.STRING,
            source="defaults",
            description=f"Variable {i} description",
            example=None,
            required=None,
            deprecated=None,
            default=None,
            file_path=None,
            line_number=None,
        )
        for i in range(10)
    ]

    metadata = RoleMetadata(
        author="Benchmark Test",
        description="Small role for performance testing",
        license="MIT",
        min_ansible_version="2.9",
    )

    role_path = tmp_path / "benchmark_small"
    role_path.mkdir()

    return AnsibleRole(
        name="benchmark_small",
        path=role_path,
        metadata=metadata,
        variables=variables,
        tags=[],
        todos=[],
        examples=[],
    )


@pytest.fixture
def medium_role(tmp_path):
    """Create a medium role with 50 variables for benchmarking."""
    variables = [
        Variable(
            name=f"var_{i}",
            value=f"value_{i}",
            type=VariableType.STRING,
            source="defaults",
            description=f"Variable {i} description with more detailed information",
            example=None,
            required=None,
            deprecated=None,
            default=None,
            file_path=None,
            line_number=None,
        )
        for i in range(50)
    ]

    metadata = RoleMetadata(
        author="Benchmark Test",
        description="Medium role for performance testing",
        license="MIT",
        min_ansible_version="2.9",
    )

    role_path = tmp_path / "benchmark_medium"
    role_path.mkdir()

    return AnsibleRole(
        name="benchmark_medium",
        path=role_path,
        metadata=metadata,
        variables=variables,
        tags=[],
        todos=[],
        examples=[],
    )


@pytest.fixture
def large_role(tmp_path):
    """Create a large role with 100 variables for benchmarking."""
    variables = [
        Variable(
            name=f"var_{i}",
            value={"key": f"value_{i}", "nested": {"data": i}},
            type=VariableType.DICT,
            source="defaults",
            description=f"Variable {i} description with extensive documentation explaining usage patterns and examples",
            example=None,
            required=None,
            deprecated=None,
            default=None,
            file_path=None,
            line_number=None,
        )
        for i in range(100)
    ]

    metadata = RoleMetadata(
        author="Benchmark Test",
        description="Large role for performance testing with comprehensive metadata",
        license="MIT",
        min_ansible_version="2.9",
    )

    role_path = tmp_path / "benchmark_large"
    role_path.mkdir()

    return AnsibleRole(
        name="benchmark_large",
        path=role_path,
        metadata=metadata,
        variables=variables,
        tags=[],
        todos=[],
        examples=[],
    )


@pytest.fixture
def markdown_renderer():
    """Create a MarkdownRenderer for benchmarking."""
    return MarkdownRenderer()


def test_small_role_rendering_performance(small_role, markdown_renderer):
    """Benchmark Markdown rendering for small role (10 variables).

    Performance thresholds:
    - Target: <60ms (optimal)
    - Warning: 60-80ms (acceptable degradation)
    - Failure: >80ms (significant regression)
    """
    context = TemplateContext(
        role=small_role,
        generator_version="0.3.0",
        generation_date=datetime.now(),
        output_format=OutputFormat.MARKDOWN,
    )

    # Warm up
    markdown_renderer.render(context)

    # Benchmark
    start = time.perf_counter()
    for _ in range(10):
        markdown_renderer.render(context)
    end = time.perf_counter()

    avg_time_ms = ((end - start) / 10) * 1000

    # Progressive tolerance: warn at 60ms, fail at 80ms
    TARGET_MS = 60
    MAX_ACCEPTABLE_MS = 80

    if avg_time_ms > MAX_ACCEPTABLE_MS:
        pytest.fail(
            f"❌ PERFORMANCE REGRESSION: Small role rendering took {avg_time_ms:.2f}ms "
            f"(target: <{TARGET_MS}ms, max acceptable: <{MAX_ACCEPTABLE_MS}ms)"
        )
    elif avg_time_ms > TARGET_MS:
        warnings.warn(
            f"⚠️ PERFORMANCE WARNING: Small role rendering took {avg_time_ms:.2f}ms "
            f"(target: <{TARGET_MS}ms). Consider optimization if this persists.",
            UserWarning,
            stacklevel=2,
        )
        print(f"⚠️ Small role (10 vars): {avg_time_ms:.2f}ms (slower than target)")
    else:
        print(f"✅ Small role (10 vars): {avg_time_ms:.2f}ms")


def test_medium_role_rendering_performance(medium_role, markdown_renderer):
    """Benchmark Markdown rendering for medium role (50 variables).

    Performance thresholds:
    - Target: <100ms (optimal)
    - Warning: 100-130ms (acceptable degradation)
    - Failure: >130ms (significant regression)
    """
    context = TemplateContext(
        role=medium_role,
        generator_version="0.3.0",
        generation_date=datetime.now(),
        output_format=OutputFormat.MARKDOWN,
    )

    # Warm up
    markdown_renderer.render(context)

    # Benchmark
    start = time.perf_counter()
    for _ in range(10):
        markdown_renderer.render(context)
    end = time.perf_counter()

    avg_time_ms = ((end - start) / 10) * 1000

    # Progressive tolerance: warn at 100ms, fail at 130ms
    TARGET_MS = 100
    MAX_ACCEPTABLE_MS = 130

    if avg_time_ms > MAX_ACCEPTABLE_MS:
        pytest.fail(
            f"❌ PERFORMANCE REGRESSION: Medium role rendering took {avg_time_ms:.2f}ms "
            f"(target: <{TARGET_MS}ms, max acceptable: <{MAX_ACCEPTABLE_MS}ms)"
        )
    elif avg_time_ms > TARGET_MS:
        warnings.warn(
            f"⚠️ PERFORMANCE WARNING: Medium role rendering took {avg_time_ms:.2f}ms "
            f"(target: <{TARGET_MS}ms). Consider optimization if this persists.",
            UserWarning,
            stacklevel=2,
        )
        print(f"⚠️ Medium role (50 vars): {avg_time_ms:.2f}ms (slower than target)")
    else:
        print(f"✅ Medium role (50 vars): {avg_time_ms:.2f}ms")


def test_large_role_rendering_performance(large_role, markdown_renderer):
    """Benchmark Markdown rendering for large role (100 variables).

    Performance thresholds:
    - Target: <200ms (optimal)
    - Warning: 200-250ms (acceptable degradation)
    - Failure: >250ms (significant regression)
    """
    context = TemplateContext(
        role=large_role,
        generator_version="0.3.0",
        generation_date=datetime.now(),
        output_format=OutputFormat.MARKDOWN,
    )

    # Warm up
    markdown_renderer.render(context)

    # Benchmark
    start = time.perf_counter()
    for _ in range(10):
        markdown_renderer.render(context)
    end = time.perf_counter()

    avg_time_ms = ((end - start) / 10) * 1000

    # Progressive tolerance: warn at 200ms, fail at 250ms
    TARGET_MS = 200
    MAX_ACCEPTABLE_MS = 250

    if avg_time_ms > MAX_ACCEPTABLE_MS:
        pytest.fail(
            f"❌ PERFORMANCE REGRESSION: Large role rendering took {avg_time_ms:.2f}ms "
            f"(target: <{TARGET_MS}ms, max acceptable: <{MAX_ACCEPTABLE_MS}ms)"
        )
    elif avg_time_ms > TARGET_MS:
        warnings.warn(
            f"⚠️ PERFORMANCE WARNING: Large role rendering took {avg_time_ms:.2f}ms "
            f"(target: <{TARGET_MS}ms). Consider optimization if this persists.",
            UserWarning,
            stacklevel=2,
        )
        print(f"⚠️ Large role (100 vars): {avg_time_ms:.2f}ms (slower than target)")
    else:
        print(f"✅ Large role (100 vars): {avg_time_ms:.2f}ms")
