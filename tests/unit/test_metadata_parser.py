"""
Unit tests for metadata parser.

Following Constitution Article III (TDD): Tests written BEFORE implementation.
This test suite drives the design of MetadataParser through Red-Green-Refactor cycle.
"""

from pathlib import Path

import pytest

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


@pytest.fixture
def yaml_loader():
    """Fixture providing YAML loader instance."""
    return RuamelYAMLLoader()


@pytest.fixture
def metadata_parser(yaml_loader):
    """Fixture providing metadata parser instance."""
    return MetadataParser(yaml_loader)


@pytest.fixture
def minimal_role_path():
    """Fixture providing path to minimal test role."""
    return Path(__file__).parent.parent / "integration" / "fixtures" / "minimal_role"


@pytest.fixture
def complex_role_path():
    """Fixture providing path to complex test role."""
    return Path(__file__).parent.parent / "integration" / "fixtures" / "complex_role"


class TestMetadataParser:
    """Test suite for MetadataParser following TDD principles."""

    def test_parse_galaxy_info_basic(self, metadata_parser, minimal_role_path):
        """
        RED: Test parsing basic galaxy_info from minimal role.

        Validates extraction of: author, description, license, min_ansible_version,
        platforms, galaxy_tags.
        """
        meta_file = minimal_role_path / "meta" / "main.yml"

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert metadata.author == "Test Author"
        assert metadata.description == "A minimal test role for ansible-doctor-enhanced"
        assert metadata.license == "MIT"
        assert metadata.min_ansible_version == "2.9"
        assert len(metadata.platforms) == 1
        assert metadata.platforms[0].name == "Ubuntu"
        assert "20.04" in metadata.platforms[0].versions
        assert "22.04" in metadata.platforms[0].versions
        assert "testing" in metadata.galaxy_tags
        assert "minimal" in metadata.galaxy_tags

    def test_parse_galaxy_info_complex(self, metadata_parser, complex_role_path):
        """
        RED: Test parsing galaxy_info with company and multiple platforms.
        """
        meta_file = complex_role_path / "meta" / "main.yml"

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert metadata.author == "Complex Author"
        assert metadata.company == "Test Corp"
        assert metadata.license == "BSD-3-Clause"
        assert len(metadata.platforms) == 2

        # Verify Ubuntu platform
        ubuntu = next(p for p in metadata.platforms if p.name == "Ubuntu")
        assert "20.04" in ubuntu.versions
        assert "22.04" in ubuntu.versions

        # Verify EL platform
        el = next(p for p in metadata.platforms if p.name == "EL")
        assert "8" in el.versions
        assert "9" in el.versions

    def test_parse_dependencies_empty(self, metadata_parser, minimal_role_path):
        """
        RED: Test parsing role with no dependencies.
        """
        meta_file = minimal_role_path / "meta" / "main.yml"

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.dependencies) == 0
        assert not metadata.has_dependencies()

    def test_parse_dependencies_with_version(self, metadata_parser, complex_role_path):
        """
        RED: Test parsing dependencies with version constraints.
        """
        meta_file = complex_role_path / "meta" / "main.yml"

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.dependencies) == 1
        assert metadata.has_dependencies()

        dep = metadata.dependencies[0]
        assert dep.name == "geerlingguy.docker"
        assert dep.version == ">=4.0.0"

    def test_parse_missing_meta_file(self, metadata_parser, tmp_path):
        """
        RED: Test error handling when meta/main.yml doesn't exist.
        """
        non_existent = tmp_path / "meta" / "main.yml"

        with pytest.raises(ParsingError) as exc_info:
            metadata_parser.parse_galaxy_info(non_existent)

        assert "not found" in str(exc_info.value).lower()
        assert str(non_existent) in str(exc_info.value)

    def test_parse_malformed_yaml(self, metadata_parser, tmp_path):
        """
        RED: Test error handling for malformed YAML syntax.
        """
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text("galaxy_info:\n  author: Test\n    invalid: indentation")

        with pytest.raises(ParsingError) as exc_info:
            metadata_parser.parse_galaxy_info(meta_file)

        assert "parse" in str(exc_info.value).lower() or "yaml" in str(exc_info.value).lower()

    def test_parse_empty_galaxy_info(self, metadata_parser, tmp_path):
        """
        RED: Test parsing when galaxy_info is empty or missing.
        """
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text("dependencies: []")

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        # Should return metadata with None/empty values, not crash
        assert metadata.author is None
        assert metadata.description is None

    def test_parse_platforms_edge_cases(self, metadata_parser, tmp_path):
        """
        RED: Test parsing platforms with edge cases (no versions, string instead of list).
        """
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text(
            """
galaxy_info:
  platforms:
    - name: Fedora
      versions: all
    - name: Debian
"""
        )

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.platforms) >= 1
        # Parser should handle both list and string versions gracefully

    def test_parse_argument_specs_basic(self, metadata_parser, tmp_path):
        """
        RED: Test parsing argument_specs.yml (Ansible 2.11+).
        """
        specs_file = tmp_path / "meta" / "argument_specs.yml"
        specs_file.parent.mkdir(parents=True)
        specs_file.write_text(
            """
argument_specs:
  main:
    short_description: Main entry point
    options:
      app_name:
        type: str
        required: true
        description: Application name
      app_port:
        type: int
        default: 8080
        description: Application port
"""
        )

        arg_specs = metadata_parser.parse_argument_specs(specs_file)

        assert "main" in arg_specs
        assert arg_specs["main"].entry_point == "main"
        assert arg_specs["main"].short_description == "Main entry point"
        assert "app_name" in arg_specs["main"].options
        assert "app_port" in arg_specs["main"].options

    def test_parse_argument_specs_missing_file(self, metadata_parser, tmp_path):
        """
        RED: Test that missing argument_specs.yml returns empty dict (not error).

        argument_specs.yml is optional (Ansible 2.11+), so missing file should not fail.
        """
        non_existent = tmp_path / "meta" / "argument_specs.yml"

        arg_specs = metadata_parser.parse_argument_specs(non_existent)

        assert arg_specs == {}

    def test_parse_metadata_complete(self, metadata_parser, complex_role_path):
        """
        RED: Test complete metadata parsing (galaxy_info + argument_specs).

        Integration-style test ensuring both parsers work together.
        """
        meta_dir = complex_role_path / "meta"

        metadata = metadata_parser.parse_metadata(meta_dir)

        # Galaxy info
        assert metadata.author == "Complex Author"
        assert metadata.has_dependencies()

        # Should work even without argument_specs.yml (optional)
        assert isinstance(metadata.argument_specs, dict)

    def test_metadata_file_path_tracking(self, metadata_parser, minimal_role_path):
        """
        RED: Test that metadata includes source file path for debugging.
        """
        meta_file = minimal_role_path / "meta" / "main.yml"

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert metadata.meta_file_path is not None
        assert str(meta_file) in metadata.meta_file_path


class TestPlatformParsing:
    """Test suite for Platform value object parsing."""

    def test_platform_with_versions_list(self, metadata_parser, tmp_path):
        """RED: Test platform with versions as list."""
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text(
            """
galaxy_info:
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
"""
        )

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.platforms) == 1
        assert metadata.platforms[0].name == "Ubuntu"
        assert "focal" in metadata.platforms[0].versions
        assert "jammy" in metadata.platforms[0].versions

    def test_platform_no_versions(self, metadata_parser, tmp_path):
        """RED: Test platform without versions specified."""
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text(
            """
galaxy_info:
  platforms:
    - name: Alpine
"""
        )

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.platforms) == 1
        assert metadata.platforms[0].name == "Alpine"
        assert metadata.platforms[0].versions == []


class TestDependencyParsing:
    """Test suite for Dependency value object parsing."""

    def test_dependency_string_format(self, metadata_parser, tmp_path):
        """RED: Test dependency as simple string (role name only)."""
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text(
            """
dependencies:
  - geerlingguy.nginx
  - geerlingguy.mysql
"""
        )

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.dependencies) == 2
        assert metadata.dependencies[0].name == "geerlingguy.nginx"
        assert metadata.dependencies[1].name == "geerlingguy.mysql"

    def test_dependency_dict_format(self, metadata_parser, tmp_path):
        """RED: Test dependency as dictionary with name/version/source."""
        meta_file = tmp_path / "meta" / "main.yml"
        meta_file.parent.mkdir(parents=True)
        meta_file.write_text(
            """
dependencies:
  - name: geerlingguy.docker
    version: ">=4.0.0"
  - role: geerlingguy.php
    version: "3.x"
"""
        )

        metadata = metadata_parser.parse_galaxy_info(meta_file)

        assert len(metadata.dependencies) >= 1
        # Parser should handle both 'name' and 'role' keys
