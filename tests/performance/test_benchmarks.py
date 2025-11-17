"""
Performance benchmarks for ansible-doctor-enhanced.

Tests that parsing meets performance requirements from SC-002:
- Typical role: <500ms
- Large role: <2s

Following Constitution Article III (TDD).
"""

import time
from pathlib import Path

import pytest

from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.variable_parser import VariableParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


class TestParsingPerformance:
    """Performance benchmark tests."""

    def test_minimal_role_parsing_speed(self):
        """Verify minimal role parses in <500ms (typical role requirement)."""
        role_path = Path("tests/integration/fixtures/minimal_role")
        
        start = time.perf_counter()
        
        # Parse metadata
        yaml_loader = RuamelYAMLLoader()
        metadata_parser = MetadataParser(yaml_loader)
        metadata = metadata_parser.parse_metadata(role_path / "meta")
        
        # Parse variables
        from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
        annotation_extractor = AnnotationExtractor()
        variable_parser = VariableParser(yaml_loader, annotation_extractor)
        variables = variable_parser.parse_role_variables(role_path)
        
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000
        
        # SC-002: Typical role should parse in <500ms
        assert elapsed_ms < 500, f"Minimal role took {elapsed_ms:.2f}ms (target: <500ms)"
        
        # Verify parsed correctly
        assert metadata.author == "Test Author"
        assert len(variables) == 3

    def test_complex_role_parsing_speed(self):
        """Verify complex role parses in <2000ms (large role requirement)."""
        role_path = Path("tests/integration/fixtures/complex_role")
        
        start = time.perf_counter()
        
        # Parse metadata
        yaml_loader = RuamelYAMLLoader()
        metadata_parser = MetadataParser(yaml_loader)
        metadata = metadata_parser.parse_metadata(role_path / "meta")
        
        # Parse variables
        from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
        annotation_extractor = AnnotationExtractor()
        variable_parser = VariableParser(yaml_loader, annotation_extractor)
        variables = variable_parser.parse_role_variables(role_path)
        
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000
        
        # SC-002: Large role should parse in <2s
        assert elapsed_ms < 2000, f"Complex role took {elapsed_ms:.2f}ms (target: <2000ms)"
        
        # Verify parsed correctly
        assert metadata.author == "Complex Author"
        assert len(variables) > 0

    def test_cli_end_to_end_performance(self, tmp_path):
        """Verify CLI end-to-end parsing meets performance requirements."""
        from click.testing import CliRunner
        from ansibledoctor.cli import cli
        
        role_path = Path("tests/integration/fixtures/minimal_role")
        output_file = tmp_path / "output.json"
        
        runner = CliRunner()
        
        start = time.perf_counter()
        result = runner.invoke(
            cli,
            ["parse", str(role_path), "--output", str(output_file), "--log-level", "error"]
        )
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000
        
        # CLI should complete quickly for typical role
        assert elapsed_ms < 1000, f"CLI took {elapsed_ms:.2f}ms (target: <1000ms)"
        assert result.exit_code == 0
        assert output_file.exists()

    def test_annotation_extraction_performance(self):
        """Verify annotation extraction is fast enough."""
        from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
        
        # Create content with many annotations
        lines = []
        for i in range(100):
            lines.append(f"# @var var_{i}: Description for variable {i}")
            lines.append(f"var_{i}: value_{i}")
        content = "\n".join(lines)
        
        extractor = AnnotationExtractor()
        
        start = time.perf_counter()
        annotations = extractor.extract_annotations(content, "test.yml")
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000
        
        # Should extract 100 annotations quickly
        assert len(annotations) == 100
        assert elapsed_ms < 200, f"Annotation extraction took {elapsed_ms:.2f}ms (target: <200ms)"

    def test_yaml_loading_performance(self, tmp_path):
        """Verify YAML loading is performant."""
        from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
        
        # Create file with many variables
        yaml_content = "\n".join([f"var_{i}: value_{i}" for i in range(1000)])
        yaml_file = tmp_path / "large.yml"
        yaml_file.write_text(yaml_content)
        
        loader = RuamelYAMLLoader()
        
        start = time.perf_counter()
        data = loader.load_file(yaml_file)
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000
        
        # Should load 1000 variables quickly
        assert len(data) == 1000
        assert elapsed_ms < 500, f"YAML loading took {elapsed_ms:.2f}ms (target: <500ms)"


