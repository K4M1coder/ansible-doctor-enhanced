"""
Performance benchmarks for documentation generator.

Validates rendering performance meets target thresholds:
- Small role (10 vars): <50ms
- Medium role (50 vars): <100ms
- Large role (100 vars): <200ms

Uses pytest-benchmark for accurate timing measurements.
"""

import time
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
        )
        for i in range(10)
    ]

    metadata = RoleMetadata(
        role_name="benchmark_small",
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
        )
        for i in range(50)
    ]

    metadata = RoleMetadata(
        role_name="benchmark_medium",
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
        )
        for i in range(100)
    ]

    metadata = RoleMetadata(
        role_name="benchmark_large",
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
    """Benchmark Markdown rendering for small role (10 variables)."""
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

    # Target: <50ms
    assert avg_time_ms < 50, f"Small role rendering took {avg_time_ms:.2f}ms (target: <50ms)"

    print(f"✅ Small role (10 vars): {avg_time_ms:.2f}ms")


def test_medium_role_rendering_performance(medium_role, markdown_renderer):
    """Benchmark Markdown rendering for medium role (50 variables)."""
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

    # Target: <100ms
    assert avg_time_ms < 100, f"Medium role rendering took {avg_time_ms:.2f}ms (target: <100ms)"

    print(f"✅ Medium role (50 vars): {avg_time_ms:.2f}ms")


def test_large_role_rendering_performance(large_role, markdown_renderer):
    """Benchmark Markdown rendering for large role (100 variables)."""
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

    # Target: <200ms (relaxed for large roles)
    assert avg_time_ms < 200, f"Large role rendering took {avg_time_ms:.2f}ms (target: <200ms)"

    print(f"✅ Large role (100 vars): {avg_time_ms:.2f}ms")
