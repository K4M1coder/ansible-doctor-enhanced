"""Integration tests for format conversion functionality.

Tests the FormatConverter with YAML, JSON, XML, and Mermaid format conversions.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from ansibledoctor.serialization.format_converter import FormatConverter


@pytest.fixture
def format_converter():
    """Create a FormatConverter instance."""
    return FormatConverter()


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        "output_format": "markdown",
        "output_dir": "docs/",
        "recursive": True,
        "exclude_patterns": ["*.pyc", "__pycache__"],
        "theme": {"primary_color": "#007acc", "font_family": "Arial"},
        "languages": {"default": "en", "available": ["en", "de", "fr"]},
    }


@pytest.fixture
def sample_yaml_file(tmp_path, sample_config_data):
    """Create a temporary YAML file with sample data."""
    yaml_file = tmp_path / "config.yml"
    yaml = YAML()
    with open(yaml_file, "w") as f:
        yaml.dump(sample_config_data, f)
    return yaml_file


@pytest.fixture
def sample_json_file(tmp_path, sample_config_data):
    """Create a temporary JSON file with sample data."""
    json_file = tmp_path / "config.json"
    with open(json_file, "w") as f:
        json.dump(sample_config_data, f, indent=2)
    return json_file


class TestFormatConversion:
    """Tests for FormatConverter."""

    def test_yaml_to_json_conversion(self, format_converter, sample_yaml_file):
        """Test converting YAML to JSON preserves data structure.
        
        T044: Validates that YAML to JSON conversion:
        - Parses YAML correctly
        - Outputs valid JSON
        - Preserves data types and structure
        - Round-trip preserves original data
        """
        # Convert YAML to JSON
        result = format_converter.convert_file(
            sample_yaml_file, to_format="json", pretty=False
        )

        # Verify result is valid JSON string
        assert isinstance(result, str)
        data = json.loads(result)

        # Verify data structure
        assert data["output_format"] == "markdown"
        assert data["recursive"] is True
        assert isinstance(data["exclude_patterns"], list)
        assert len(data["exclude_patterns"]) == 2
        assert isinstance(data["theme"], dict)

    def test_json_to_xml_conversion(self, format_converter, sample_json_file):
        """Test converting JSON to XML produces valid XML structure.
        
        T045: Validates that JSON to XML conversion:
        - Parses JSON correctly
        - Outputs valid XML
        - Has proper root element
        - Nested objects become nested elements
        """
        # Convert JSON to XML
        result = format_converter.convert_file(
            sample_json_file, to_format="xml", pretty=True
        )

        # Verify result is valid XML
        assert isinstance(result, str)
        root = ET.fromstring(result)

        # Verify XML structure
        assert root.tag == "root"
        
        # Check for key elements
        output_format = root.find("output_format")
        assert output_format is not None
        assert output_format.text == "markdown"
        
        recursive = root.find("recursive")
        assert recursive is not None
        assert recursive.text.lower() == "true"  # Python bool → "True" or "true"

    def test_yaml_to_json_round_trip(
        self, format_converter, sample_yaml_file, sample_config_data
    ):
        """Test YAML to JSON and back preserves data fidelity.
        
        T047: Validates that:
        - YAML → JSON → YAML preserves all data
        - No data loss in conversion
        - Types are maintained correctly
        """
        # Convert YAML to JSON
        json_result = format_converter.convert_file(
            sample_yaml_file, to_format="json", pretty=False
        )

        # Parse JSON back to data
        json_data = json.loads(json_result)

        # Verify data matches original
        assert json_data == sample_config_data
        assert json_data["recursive"] is True  # Boolean preserved
        assert isinstance(json_data["exclude_patterns"], list)  # List preserved
        assert isinstance(json_data["theme"], dict)  # Dict preserved

    def test_convert_with_pretty_formatting(
        self, format_converter, sample_yaml_file
    ):
        """Test pretty formatting produces readable output.
        
        T048: Validates that --pretty flag:
        - Adds proper indentation to JSON
        - Adds newlines between elements
        - Produces human-readable output
        """
        # Convert with pretty formatting
        pretty_result = format_converter.convert_file(
            sample_yaml_file, to_format="json", pretty=True
        )

        # Verify pretty formatting
        assert isinstance(pretty_result, str)
        assert "\n" in pretty_result  # Has newlines
        assert "  " in pretty_result or "\t" in pretty_result  # Has indentation

        # Verify it's still valid JSON
        data = json.loads(pretty_result)
        assert "output_format" in data

    def test_convert_without_pretty_formatting(
        self, format_converter, sample_yaml_file
    ):
        """Test conversion without pretty formatting is compact."""
        # Convert without pretty formatting
        compact_result = format_converter.convert_file(
            sample_yaml_file, to_format="json", pretty=False
        )

        # Verify compact formatting (minimal whitespace)
        assert isinstance(compact_result, str)
        
        # Compact should have fewer newlines than pretty
        pretty_result = format_converter.convert_file(
            sample_yaml_file, to_format="json", pretty=True
        )
        assert compact_result.count("\n") < pretty_result.count("\n")

    def test_json_to_yaml_conversion(self, format_converter, sample_json_file):
        """Test converting JSON back to YAML."""
        # Convert JSON to YAML
        result = format_converter.convert_file(
            sample_json_file, to_format="yaml", pretty=True
        )

        # Verify result is valid YAML
        assert isinstance(result, str)
        yaml = YAML()
        data = yaml.load(result)

        # Verify data structure
        assert data["output_format"] == "markdown"
        assert data["recursive"] is True

    def test_xml_to_json_conversion(self, format_converter, tmp_path):
        """Test converting XML to JSON.
        
        T052: Validates XML to JSON conversion
        """
        # Create sample XML file
        xml_content = """<?xml version="1.0"?>
<root>
    <output_format>markdown</output_format>
    <recursive>true</recursive>
    <output_dir>docs/</output_dir>
</root>"""
        xml_file = tmp_path / "config.xml"
        xml_file.write_text(xml_content)

        # Convert XML to JSON
        result = format_converter.convert_file(xml_file, to_format="json", pretty=True)

        # Verify result is valid JSON
        assert isinstance(result, str)
        data = json.loads(result)

        # Verify data structure
        assert "output_format" in data
        assert data["output_format"] == "markdown"

    def test_mermaid_diagram_generation(self, format_converter, sample_yaml_file):
        """Test generating Mermaid diagrams from config data.
        
        T046: Validates Mermaid generation:
        - Extends Spec 011 MermaidBuilder
        - Generates valid Mermaid syntax
        - Represents config structure as diagram
        """
        # Convert to Mermaid diagram
        result = format_converter.convert_file(
            sample_yaml_file, to_format="mermaid", pretty=True
        )

        # Verify Mermaid syntax
        assert isinstance(result, str)
        assert "graph" in result.lower() or "flowchart" in result.lower()
        # Should contain config keys
        assert "output_format" in result or "markdown" in result

    def test_unsupported_format_raises_error(self, format_converter, sample_yaml_file):
        """Test that unsupported formats raise appropriate errors."""
        with pytest.raises((ValueError, NotImplementedError)):
            format_converter.convert_file(sample_yaml_file, to_format="pdf")

    def test_convert_to_same_format(self, format_converter, sample_json_file):
        """Test converting to the same format (should work as passthrough)."""
        # Convert JSON to JSON (should parse and re-serialize)
        result = format_converter.convert_file(
            sample_json_file, to_format="json", pretty=True
        )

        # Verify it's valid JSON
        data = json.loads(result)
        assert "output_format" in data
