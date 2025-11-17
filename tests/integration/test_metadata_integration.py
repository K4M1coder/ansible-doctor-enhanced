"""
Integration tests for metadata parser using fixture roles.

Following Constitution Article III (TDD): Tests written BEFORE implementation.
These tests validate end-to-end metadata parsing with realistic role structures.
"""

from pathlib import Path

import pytest

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


@pytest.fixture
def metadata_parser():
    """Fixture providing metadata parser with YAML loader."""
    yaml_loader = RuamelYAMLLoader()
    return MetadataParser(yaml_loader)


@pytest.fixture
def fixtures_path():
    """Fixture providing path to integration test fixtures."""
    return Path(__file__).parent / "fixtures"


class TestMinimalRoleMetadata:
    """Integration tests using minimal_role fixture."""

    def test_parse_minimal_role_complete(self, metadata_parser, fixtures_path):
        """
        RED: Test complete metadata parsing for minimal role.
        
        Validates US1 acceptance criteria:
        - Extract galaxy_info (author, description, license, platforms, tags)
        - Handle roles without dependencies
        - Parse platform versions correctly
        """
        role_path = fixtures_path / "minimal_role"
        meta_dir = role_path / "meta"
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        # Galaxy info validation
        assert metadata.author == "Test Author"
        assert metadata.description == "A minimal test role for ansible-doctor-enhanced"
        assert metadata.license == "MIT"
        assert metadata.min_ansible_version == "2.9"
        
        # Platform validation
        assert len(metadata.platforms) == 1
        ubuntu = metadata.platforms[0]
        assert ubuntu.name == "Ubuntu"
        assert len(ubuntu.versions) == 2
        assert "20.04" in ubuntu.versions
        assert "22.04" in ubuntu.versions
        
        # Galaxy tags
        assert len(metadata.galaxy_tags) == 2
        assert "testing" in metadata.galaxy_tags
        assert "minimal" in metadata.galaxy_tags
        
        # No dependencies
        assert len(metadata.dependencies) == 0
        assert not metadata.has_dependencies()

    def test_minimal_role_platforms_summary(self, metadata_parser, fixtures_path):
        """
        RED: Test RoleMetadata.get_supported_platforms_summary() method.
        """
        role_path = fixtures_path / "minimal_role"
        meta_dir = role_path / "meta"
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        summary = metadata.get_supported_platforms_summary()
        
        # Summary is list of strings like "Ubuntu (20.04, 22.04)"
        assert len(summary) > 0
        assert any("Ubuntu" in platform for platform in summary)
        summary_str = " ".join(summary)
        assert "20.04" in summary_str or "22.04" in summary_str


class TestComplexRoleMetadata:
    """Integration tests using complex_role fixture."""

    def test_parse_complex_role_complete(self, metadata_parser, fixtures_path):
        """
        RED: Test complete metadata parsing for complex role with dependencies.
        
        Validates US1 acceptance criteria:
        - Extract complex galaxy_info with company field
        - Parse role dependencies with version constraints
        - Handle multiple platforms
        """
        role_path = fixtures_path / "complex_role"
        meta_dir = role_path / "meta"
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        # Galaxy info validation
        assert metadata.author == "Complex Author"
        assert metadata.company == "Test Corp"
        assert metadata.description is not None
        assert "complex" in metadata.description.lower()
        assert metadata.license == "BSD-3-Clause"
        
        # Multiple platforms
        assert len(metadata.platforms) == 2
        platform_names = [p.name for p in metadata.platforms]
        assert "Ubuntu" in platform_names
        assert "EL" in platform_names
        
        # Dependencies validation
        assert len(metadata.dependencies) == 1
        assert metadata.has_dependencies()
        
        dep = metadata.dependencies[0]
        assert dep.name == "geerlingguy.docker"
        assert dep.version == ">=4.0.0"

    def test_complex_role_ubuntu_versions(self, metadata_parser, fixtures_path):
        """
        RED: Test parsing Ubuntu platform versions from complex role.
        """
        role_path = fixtures_path / "complex_role"
        meta_dir = role_path / "meta"
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        ubuntu = next(p for p in metadata.platforms if p.name == "Ubuntu")
        assert "20.04" in ubuntu.versions
        assert "22.04" in ubuntu.versions

    def test_complex_role_el_versions(self, metadata_parser, fixtures_path):
        """
        RED: Test parsing EL (Enterprise Linux) platform versions.
        """
        role_path = fixtures_path / "complex_role"
        meta_dir = role_path / "meta"
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        el = next(p for p in metadata.platforms if p.name == "EL")
        assert "8" in el.versions
        assert "9" in el.versions


class TestEdgeCases:
    """Integration tests for edge cases and error scenarios."""

    def test_missing_meta_directory(self, metadata_parser, tmp_path):
        """
        RED: Test graceful handling when meta/ directory doesn't exist.
        """
        non_existent_meta = tmp_path / "fake_role" / "meta"
        
        with pytest.raises(ParsingError) as exc_info:
            metadata_parser.parse_metadata(non_existent_meta)
        
        assert "meta" in str(exc_info.value).lower()

    def test_empty_meta_main(self, metadata_parser, tmp_path):
        """
        RED: Test parsing when meta/main.yml is empty.
        """
        meta_dir = tmp_path / "meta"
        meta_dir.mkdir(parents=True)
        meta_file = meta_dir / "main.yml"
        meta_file.write_text("")
        
        # Should not crash, but return metadata with None/empty fields
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        assert metadata is not None
        assert metadata.author is None or metadata.author == ""

    def test_galaxy_info_required_fields_only(self, metadata_parser, tmp_path):
        """
        RED: Test parsing with only absolutely required galaxy_info fields.
        """
        meta_dir = tmp_path / "meta"
        meta_dir.mkdir(parents=True)
        meta_file = meta_dir / "main.yml"
        meta_file.write_text("""
galaxy_info:
  author: Minimal Author
  description: Minimal description
  license: MIT
""")
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        assert metadata.author == "Minimal Author"
        assert metadata.description == "Minimal description"
        assert metadata.license == "MIT"
        assert len(metadata.platforms) == 0  # Optional field
        assert len(metadata.dependencies) == 0  # Optional field


class TestArgumentSpecs:
    """Integration tests for argument_specs.yml parsing (Ansible 2.11+)."""

    def test_argument_specs_optional(self, metadata_parser, fixtures_path):
        """
        RED: Test that argument_specs.yml is optional.
        
        Both fixtures don't have argument_specs.yml, parser should handle gracefully.
        """
        minimal_meta = fixtures_path / "minimal_role" / "meta"
        
        metadata = metadata_parser.parse_metadata(minimal_meta)
        
        assert isinstance(metadata.argument_specs, dict)
        # Empty dict when file doesn't exist (not an error)

    def test_argument_specs_parsing(self, metadata_parser, tmp_path):
        """
        RED: Test parsing valid argument_specs.yml.
        """
        meta_dir = tmp_path / "meta"
        meta_dir.mkdir(parents=True)
        
        # Create main.yml
        main_file = meta_dir / "main.yml"
        main_file.write_text("""
galaxy_info:
  author: Test
  description: Test role
  license: MIT
""")
        
        # Create argument_specs.yml
        specs_file = meta_dir / "argument_specs.yml"
        specs_file.write_text("""
argument_specs:
  main:
    short_description: Main entry point for role
    options:
      server_name:
        type: str
        required: true
        description: Server hostname
      server_port:
        type: int
        default: 443
        description: Server port number
""")
        
        metadata = metadata_parser.parse_metadata(meta_dir)
        
        assert "main" in metadata.argument_specs
        main_spec = metadata.argument_specs["main"]
        assert main_spec.entry_point == "main"
        assert "server_name" in main_spec.options
        assert "server_port" in main_spec.options
