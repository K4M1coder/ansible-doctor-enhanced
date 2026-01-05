"""Unit tests for project existing docs extraction (Spec 006, T325-T330).

Tests that DocsExtractor correctly extracts README, CHANGELOG, CONTRIBUTING, LICENSE
files from the project root directory.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.existing_docs import ExistingDocs
from ansibledoctor.models.project import Project
from ansibledoctor.parser.docs_extractor import DocsExtractor


class TestProjectExistingDocs:
    """Test DocsExtractor functionality for project-level docs."""

    def test_extract_all_project_docs(self, tmp_path: Path) -> None:
        """T325: DocsExtractor extracts README, CHANGELOG, CONTRIBUTING, LICENSE at project root."""
        # Arrange - Create all standard project docs
        (tmp_path / "README.md").write_text("# My Project\n\nProject description.")
        (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [1.0.0]\n- Initial release")
        (tmp_path / "CONTRIBUTING.md").write_text("# Contributing\n\nHow to contribute.")
        (tmp_path / "LICENSE").write_text("MIT License\n\nCopyright (c) 2025")

        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        # Assert
        assert docs.readme_content is not None
        assert "My Project" in docs.readme_content
        assert docs.readme_format == "markdown"

        assert docs.changelog_content is not None
        assert "[1.0.0]" in docs.changelog_content

        assert docs.contributing_content is not None
        assert "Contributing" in docs.contributing_content

        assert docs.license_content is not None
        assert docs.license_type == "MIT"

    def test_license_type_detection_mit(self, tmp_path: Path) -> None:
        """T327: License type detection for MIT."""
        (tmp_path / "LICENSE").write_text(
            "MIT License\n\n"
            "Copyright (c) 2025 Author\n\n"
            "Permission is hereby granted, free of charge..."
        )

        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        assert docs.license_type == "MIT"

    def test_license_type_detection_apache(self, tmp_path: Path) -> None:
        """T327: License type detection for Apache-2.0."""
        (tmp_path / "LICENSE").write_text(
            "Apache License\n" "Version 2.0, January 2004\n" "http://www.apache.org/licenses/"
        )

        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        assert docs.license_type == "Apache-2.0"

    def test_license_type_detection_gpl3(self, tmp_path: Path) -> None:
        """T327: License type detection for GPL-3.0."""
        (tmp_path / "LICENSE").write_text(
            "GNU GENERAL PUBLIC LICENSE\n"
            "Version 3, 29 June 2007\n"
            "Copyright (C) 2007 Free Software Foundation, Inc."
        )

        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        assert docs.license_type == "GPL-3.0"

    def test_partial_docs_only_readme(self, tmp_path: Path) -> None:
        """T329: DocsExtractor handles partial docs (only README exists)."""
        # Arrange - Only README exists
        (tmp_path / "README.md").write_text("# Project\n\nMinimal project.")

        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        # Assert
        assert docs.readme_content is not None
        assert docs.changelog_content is None
        assert docs.contributing_content is None
        assert docs.license_content is None
        assert docs.license_type is None

    def test_partial_docs_readme_and_license(self, tmp_path: Path) -> None:
        """T329: DocsExtractor handles partial docs (README + LICENSE only)."""
        # Arrange
        (tmp_path / "README.md").write_text("# Project\n\nWith license.")
        (tmp_path / "LICENSE").write_text("BSD 3-Clause License\n\nRedistribution allowed...")

        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        # Assert
        assert docs.readme_content is not None
        assert docs.license_content is not None
        assert docs.changelog_content is None
        assert docs.contributing_content is None

    def test_no_docs_present(self, tmp_path: Path) -> None:
        """T329: DocsExtractor handles directories with no docs."""
        # Arrange - Empty directory

        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        # Assert
        assert docs.readme_content is None
        assert docs.changelog_content is None
        assert docs.contributing_content is None
        assert docs.license_content is None
        assert docs.license_type is None

    def test_readme_rst_format(self, tmp_path: Path) -> None:
        """T325: DocsExtractor detects RST format for README.rst."""
        (tmp_path / "README.rst").write_text(
            "My Project\n" "==========\n\n" "Project using reStructuredText."
        )

        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()

        assert docs.readme_content is not None
        assert docs.readme_format == "rst"


class TestProjectModelExistingDocs:
    """T328: Test Project model accepts existing_docs field."""

    def test_project_model_with_existing_docs(self, tmp_path: Path) -> None:
        """T328: Project model can hold existing_docs field."""
        # Arrange
        docs = ExistingDocs(
            readme_content="# My Project",
            readme_format="markdown",
            changelog_content="## [1.0.0]",
            license_content="MIT License",
            license_type="MIT",
        )

        # Act
        project = Project(name="test-project", path=str(tmp_path), existing_docs=docs)

        # Assert
        assert project.existing_docs is not None
        assert project.existing_docs.readme_content == "# My Project"
        assert project.existing_docs.license_type == "MIT"

    def test_project_model_without_existing_docs(self, tmp_path: Path) -> None:
        """T328: Project model defaults existing_docs to None."""
        # Act
        project = Project(name="minimal-project", path=str(tmp_path))

        # Assert
        assert project.existing_docs is None


class TestProjectParserExistingDocsIntegration:
    """T326: Test ProjectParser integrates DocsExtractor."""

    def test_project_parser_populates_existing_docs(self, tmp_path: Path) -> None:
        """T326: ProjectParser.parse() populates project.existing_docs."""
        from ansibledoctor.parser.project_parser import ProjectParser

        # Arrange - Create minimal project structure with docs
        (tmp_path / "README.md").write_text("# Test Project\n\nProject docs.")
        (tmp_path / "LICENSE").write_text("MIT License\n\nCopyright 2025")
        (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [1.0.0]")

        # Act
        parser = ProjectParser()
        project = parser.parse(str(tmp_path))

        # Assert
        assert project.existing_docs is not None
        assert project.existing_docs.readme_content is not None
        assert "Test Project" in project.existing_docs.readme_content
        assert project.existing_docs.license_type == "MIT"
        assert project.existing_docs.changelog_content is not None

    def test_project_parser_no_docs(self, tmp_path: Path) -> None:
        """T326: ProjectParser.parse() sets existing_docs even when no docs exist."""
        from ansibledoctor.parser.project_parser import ProjectParser

        # Arrange - Empty project (no README/LICENSE)
        # Act
        parser = ProjectParser()
        project = parser.parse(str(tmp_path))

        # Assert
        assert project.existing_docs is not None  # ExistingDocs is created but empty
        assert project.existing_docs.readme_content is None
        assert project.existing_docs.license_content is None


class TestDemoProjectExistingDocsIntegration:
    """T330: Integration test with demo project."""

    def test_demo_project_existing_docs(self) -> None:
        """T330: Demo project has README, LICENSE, CHANGELOG extracted."""
        from ansibledoctor.parser.project_parser import ProjectParser

        # Arrange - Use actual demo project
        demo_path = (
            Path(__file__).parent.parent.parent.parent
            / "demo"
            / "project_demo_namespace.demo_project"
        )

        if not demo_path.exists():
            pytest.skip("Demo project not found")

        # Act
        parser = ProjectParser()
        project = parser.parse(str(demo_path))

        # Assert
        assert project.existing_docs is not None

        # README
        assert project.existing_docs.readme_content is not None
        assert "Demo Project" in project.existing_docs.readme_content
        assert project.existing_docs.readme_format == "markdown"

        # LICENSE
        assert project.existing_docs.license_content is not None
        assert project.existing_docs.license_type == "MIT"

        # CHANGELOG
        assert project.existing_docs.changelog_content is not None
        assert "Keep a Changelog" in project.existing_docs.changelog_content
