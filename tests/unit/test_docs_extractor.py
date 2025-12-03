"""Unit tests for docs extractor (Spec 001, User Story 5)."""

import pytest
from pathlib import Path
from ansibledoctor.parser.docs_extractor import DocsExtractor
from ansibledoctor.models.existing_docs import ExistingDocs


class TestDocsExtractor:
    """Test DocsExtractor functionality."""

    def test_extract_readme_md(self, tmp_path):
        """T108: DocsExtractor extracts README.md content."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text("# My Role\n\nThis is a test role.\n")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.readme_content == "# My Role\n\nThis is a test role.\n"
        assert docs.readme_format == "markdown"

    def test_detect_markdown_vs_rst_format(self, tmp_path):
        """T109: DocsExtractor detects markdown vs rst format."""
        # Arrange - RST file
        readme = tmp_path / "README.rst"
        readme.write_text("""My Role
=======

This is a test role.
""")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.readme_format == "rst"
        assert "My Role" in docs.readme_content

    def test_extract_changelog_md(self, tmp_path):
        """T110: DocsExtractor extracts CHANGELOG.md content."""
        # Arrange
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## v1.0.0\n- Initial release\n")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.changelog_content == "# Changelog\n\n## v1.0.0\n- Initial release\n"

    def test_extract_license_and_detect_type(self, tmp_path):
        """T111: DocsExtractor extracts LICENSE and detects license type."""
        # Arrange - MIT License
        license_file = tmp_path / "LICENSE"
        license_file.write_text("""MIT License

Copyright (c) 2025 Test Author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert "MIT License" in docs.license_content
        assert docs.license_type == "MIT"

    def test_detect_apache_license(self, tmp_path):
        """Test Apache-2.0 license detection."""
        # Arrange
        license_file = tmp_path / "LICENSE"
        license_file.write_text("""Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
""")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.license_type == "Apache-2.0"

    def test_detect_gpl_license(self, tmp_path):
        """Test GPL-3.0 license detection."""
        # Arrange
        license_file = tmp_path / "LICENSE"
        license_file.write_text("""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc.
""")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.license_type == "GPL-3.0"

    def test_list_templates_directory(self, tmp_path):
        """T112: DocsExtractor lists templates/ directory files."""
        # Arrange
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "config.j2").touch()
        (templates_dir / "service.j2").touch()
        (templates_dir / "subdir").mkdir()  # Should not be listed
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert len(docs.templates_list) == 2
        assert "config.j2" in docs.templates_list
        assert "service.j2" in docs.templates_list

    def test_list_files_directory(self, tmp_path):
        """T113: DocsExtractor lists files/ directory files."""
        # Arrange
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        (files_dir / "script.sh").touch()
        (files_dir / "config.txt").touch()
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert len(docs.files_list) == 2
        assert "script.sh" in docs.files_list
        assert "config.txt" in docs.files_list

    def test_missing_docs_returns_none(self, tmp_path):
        """T114: DocsExtractor returns None for missing docs."""
        # Act - no docs in tmp_path
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.readme_content is None
        assert docs.readme_format is None
        assert docs.changelog_content is None
        assert docs.license_content is None
        assert docs.license_type is None
        assert docs.templates_list == []
        assert docs.files_list == []

    def test_contributing_file_extraction(self, tmp_path):
        """Test CONTRIBUTING.md extraction."""
        # Arrange
        contributing = tmp_path / "CONTRIBUTING.md"
        contributing.write_text("# Contributing\n\nPlease follow these guidelines.\n")
        
        # Act
        extractor = DocsExtractor(str(tmp_path))
        docs = extractor.extract()
        
        # Assert
        assert docs.contributing_content == "# Contributing\n\nPlease follow these guidelines.\n"
