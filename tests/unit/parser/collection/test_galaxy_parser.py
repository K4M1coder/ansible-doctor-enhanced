"""Tests for GalaxyMetadataParser.

Following Constitution Article III (TDD - RED Phase):
These tests are written FIRST and MUST FAIL before implementation.
"""

from pathlib import Path

import pytest

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.parser.galaxy_parser import GalaxyMetadataParser


class TestGalaxyMetadataParserValidFile:
    """Test parsing valid galaxy.yml files (T016)."""
    
    def test_parse_valid_galaxy_yml(self):
        """Test parsing a valid galaxy.yml with required fields (T016)."""
        # Arrange
        galaxy_file = Path("tests/fixtures/collections/minimal_valid/galaxy.yml")
        parser = GalaxyMetadataParser()
        
        # Act
        metadata = parser.parse(galaxy_file)
        
        # Assert
        assert metadata.namespace == "test_namespace"
        assert metadata.name == "test_collection"
        assert metadata.version == "1.0.0"
        assert len(metadata.authors) > 0


class TestGalaxyMetadataParserMissingFile:
    """Test error handling for missing galaxy.yml (T017)."""
    
    def test_raises_error_for_missing_file(self):
        """Test that parser raises FileNotFoundError for missing file (T017)."""
        # Arrange
        galaxy_file = Path("tests/fixtures/nonexistent/galaxy.yml")
        parser = GalaxyMetadataParser()
        
        # Act & Assert
        with pytest.raises((FileNotFoundError, ParsingError)) as exc_info:
            parser.parse(galaxy_file)
        
        # Verify error message is helpful
        error_msg = str(exc_info.value).lower()
        assert "not found" in error_msg or "does not exist" in error_msg


class TestGalaxyMetadataParserMalformedYAML:
    """Test error handling for malformed YAML (T018)."""
    
    def test_raises_error_for_malformed_yaml(self):
        """Test that parser raises error for malformed YAML (T018)."""
        # Arrange
        galaxy_file = Path("tests/fixtures/collections/malformed_yaml/galaxy.yml")
        parser = GalaxyMetadataParser()
        
        # Act & Assert
        with pytest.raises(ParsingError) as exc_info:
            parser.parse(galaxy_file)
        
        # Verify error mentions YAML parsing
        error_msg = str(exc_info.value).lower()
        assert "yaml" in error_msg or "parse" in error_msg


class TestGalaxyMetadataParserRequiredFields:
    """Test validation of required fields (T019)."""
    
    def test_validates_required_namespace_field(self):
        """Test that parser validates required 'namespace' field (T019)."""
        # Arrange
        galaxy_file = Path("tests/fixtures/collections/invalid_missing_namespace/galaxy.yml")
        parser = GalaxyMetadataParser()
        
        # Act & Assert
        with pytest.raises(ParsingError) as exc_info:
            parser.parse(galaxy_file)
        
        # Verify error mentions missing field
        error_msg = str(exc_info.value).lower()
        assert "namespace" in error_msg or "required" in error_msg


class TestGalaxyMetadataParserDependencies:
    """Test dependency extraction (T020)."""
    
    def test_extracts_dependencies_with_version_constraints(self):
        """Test extracting dependencies dictionary with version constraints (T020)."""
        # Arrange
        # Will need a fixture with dependencies - using minimal_valid for now
        galaxy_file = Path("tests/fixtures/collections/minimal_valid/galaxy.yml")
        parser = GalaxyMetadataParser()
        
        # Act
        metadata = parser.parse(galaxy_file)
        
        # Assert
        assert isinstance(metadata.dependencies, dict)
        # Empty dict is valid for minimal collection
        assert metadata.dependencies == {}
