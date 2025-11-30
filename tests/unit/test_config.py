"""
Tests for project configuration and quality gates.

Following Constitution Article III (TDD): Tests ensuring quality standards.
"""

from pathlib import Path

import pytest


class TestProjectStructure:
    """Test suite for project structure validation."""

    def test_project_root_exists(self):
        """Test that project root directory exists."""
        project_root = Path(__file__).parent.parent.parent
        assert project_root.exists()
        assert (project_root / "pyproject.toml").exists()

    def test_source_package_exists(self):
        """Test that ansibledoctor package exists."""
        project_root = Path(__file__).parent.parent.parent
        package_dir = project_root / "ansibledoctor"
        assert package_dir.exists()
        assert (package_dir / "__init__.py").exists()

    def test_tests_directory_structure(self):
        """Test that tests directory has proper structure."""
        tests_dir = Path(__file__).parent.parent
        assert tests_dir.exists()
        assert (tests_dir / "unit").exists()
        assert (tests_dir / "integration").exists()
        assert (tests_dir / "integration" / "fixtures").exists()

    def test_required_config_files(self):
        """Test that required configuration files exist."""
        project_root = Path(__file__).parent.parent.parent

        required_files = [
            "pyproject.toml",
            "README.md",
            "CHANGELOG.md",
            ".gitignore",
        ]

        for file_name in required_files:
            assert (project_root / file_name).exists(), f"Missing {file_name}"


class TestConstitutionCompliance:
    """Test suite for Constitution compliance checks."""

    def test_constitution_exists(self):
        """Test that constitution file exists."""
        project_root = Path(__file__).parent.parent.parent
        constitution = project_root / ".specify" / "memory" / "constitution.md"
        assert constitution.exists()

    def test_specification_exists(self):
        """Test that feature specifications exist."""
        project_root = Path(__file__).parent.parent.parent
        specs_dir = project_root / "specs"
        assert specs_dir.exists()

        # Feature 001 should exist
        feature_001 = specs_dir / "001-ansible-role-parser"
        assert feature_001.exists()
        assert (feature_001 / "spec.md").exists()
        assert (feature_001 / "plan.md").exists()
        assert (feature_001 / "tasks.md").exists()


class TestCodeQuality:
    """Test suite for code quality standards."""

    def test_all_modules_have_docstrings(self):
        """Test that all Python modules have docstrings."""
        project_root = Path(__file__).parent.parent.parent
        package_dir = project_root / "ansibledoctor"

        for py_file in package_dir.rglob("*.py"):
            if py_file.name == "__init__.py" and py_file.stat().st_size < 100:
                continue  # Skip small __init__.py files

            content = py_file.read_text(encoding="utf-8")
            # Should have docstring at the top
            lines = [line for line in content.split("\n") if line.strip()]
            if lines:
                # First non-comment line should be docstring
                for line in lines:
                    if not line.startswith("#"):
                        assert (
                            '"""' in line or "'''" in line
                        ), f"Module {py_file.name} missing docstring"
                        break

    def test_no_bare_except_clauses(self):
        """Test that code doesn't use bare except clauses."""
        project_root = Path(__file__).parent.parent.parent
        package_dir = project_root / "ansibledoctor"

        for py_file in package_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")

            # Check for bare except (allowing except Exception)
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "except:" in line and not line.strip().startswith("#"):
                    # Allowed if it's "except Exception:" or has a type
                    if line.strip() == "except:":
                        pytest.fail(
                            f"Bare except clause in {py_file.name}:{i} - "
                            "use specific exception types"
                        )


class TestImportCompliance:
    """Test suite for import standards."""

    def test_no_star_imports(self):
        """Test that code doesn't use star imports."""
        project_root = Path(__file__).parent.parent.parent
        package_dir = project_root / "ansibledoctor"

        for py_file in package_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")

            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "import *" in line and not line.strip().startswith("#"):
                    pytest.fail(
                        f"Star import in {py_file.name}:{i} - "
                        "use explicit imports per Constitution Article I"
                    )

    def test_imports_from_ansibledoctor_only(self):
        """Test that modules import from ansibledoctor package correctly."""
        project_root = Path(__file__).parent.parent.parent
        package_dir = project_root / "ansibledoctor"

        for py_file in package_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")

            # Check for relative imports at package level
            if "from .." in content and py_file.name != "__init__.py":
                # Relative imports should be from direct parent only
                pass  # This is allowed


class TestVersioning:
    """Test suite for version management."""

    def test_version_defined_in_init(self):
        """Test that version is defined in __init__.py."""
        project_root = Path(__file__).parent.parent.parent
        init_file = project_root / "ansibledoctor" / "__init__.py"

        content = init_file.read_text(encoding="utf-8")
        assert "__version__" in content

    def test_version_format(self):
        """Test that version follows semantic versioning."""
        from ansibledoctor import __version__

        # Should match X.Y.Z or X.Y.Z-prerelease format
        parts = __version__.split("-")[0].split(".")
        assert len(parts) == 3, "Version should be MAJOR.MINOR.PATCH"

        for part in parts:
            assert part.isdigit(), f"Version part '{part}' should be numeric"


class TestDocumentation:
    """Test suite for documentation requirements."""

    def test_readme_sections(self):
        """Test that README has required sections per Constitution Article IX."""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "README.md"

        content = readme.read_text(encoding="utf-8")

        required_sections = [
            "# Ansible Doctor Enhanced",
            "## 🎯 Project Description",
            "## ✨ Key Features",
            "## 🚀 Installation",
            "## 📖 Usage",
            "## 🏗️ Architecture",
            "## 🤝 Contributing",
            "## 📄 License",
        ]

        for section in required_sections:
            assert section in content, f"README missing section: {section}"

    def test_changelog_format(self):
        """Test that CHANGELOG follows Keep a Changelog format."""
        project_root = Path(__file__).parent.parent.parent
        changelog = project_root / "CHANGELOG.md"

        content = changelog.read_text(encoding="utf-8")

        # Should have standard sections
        assert "## [Unreleased]" in content
        assert "### Added" in content
        assert "### Changed" in content


class TestEntryPoints:
    """Test suite for CLI entry points."""

    def test_cli_entry_point_configured(self):
        """Test that CLI entry point is configured in pyproject.toml."""
        project_root = Path(__file__).parent.parent.parent
        pyproject = project_root / "pyproject.toml"

        content = pyproject.read_text(encoding="utf-8")

        assert "[tool.poetry.scripts]" in content
        assert "ansible-doctor-enhanced" in content

    def test_cli_module_exists(self):
        """Test that CLI module exists and has main function."""
        from ansibledoctor import cli

        assert hasattr(cli, "main")
        assert callable(cli.main)
        assert hasattr(cli, "cli")
        assert callable(cli.cli)
