"""Test project generator includes existing docs content (T337-T341).

Verifies that README, CHANGELOG, and license badge are included in generated README.
"""

from pathlib import Path

from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.parser.project_parser import ProjectParser


def test_generate_includes_existing_docs(tmp_path: Path):
    # Arrange: create project with existing docs
    proj_dir = tmp_path / "myproj"
    proj_dir.mkdir(parents=True)
    (proj_dir / "README.md").write_text("# My Test Project\n\nThis is README content.")
    (proj_dir / "CHANGELOG.md").write_text("# Changelog\n\n## [1.0.0] - Initial")
    (proj_dir / "CONTRIBUTING.md").write_text("# Contributing\n\nPlease contribute")
    (proj_dir / "LICENSE").write_text("MIT License\n\nCopyright 2025")

    parser = ProjectParser()
    project = parser.parse(str(proj_dir))
    gen = ProjectDocumentationGenerator(project)

    # Act
    out_file = gen.generate(
        format="markdown", output_dir=None, template_path=None, legacy_output=False
    )

    # Assert
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "My Test Project" in content
    assert "This is README content." in content
    # Changelog summary - should include the line "# Changelog" or version
    assert "Changelog" in content or "1.0.0" in content
    # License badge should be present
    assert "img.shields.io" in content and "MIT" in content


def test_generate_license_badge_for_apache(tmp_path: Path):
    # Arrange: project with Apache license
    proj_dir = tmp_path / "proj2"
    proj_dir.mkdir(parents=True)
    (proj_dir / "LICENSE").write_text(
        "Apache License\nVersion 2.0, January 2004\nhttp://www.apache.org/licenses/"
    )

    parser = ProjectParser()
    project = parser.parse(str(proj_dir))
    gen = ProjectDocumentationGenerator(project)

    # Act
    out_file = gen.generate(
        format="markdown", output_dir=None, template_path=None, legacy_output=False
    )

    # Assert
    content = out_file.read_text(encoding="utf-8")
    assert "img.shields.io" in content
    assert "Apache-2.0" in content


def test_generate_includes_existing_docs_html(tmp_path: Path):
    # Arrange
    proj_dir = tmp_path / "myproj_html"
    proj_dir.mkdir(parents=True)
    (proj_dir / "README.md").write_text("# My Test Project\n\nThis is README content.")
    (proj_dir / "LICENSE").write_text("MIT License\n\nCopyright 2025")

    parser = ProjectParser()
    project = parser.parse(str(proj_dir))
    gen = ProjectDocumentationGenerator(project)

    # Act
    out_file = gen.generate(format="html", output_dir=None, template_path=None, legacy_output=False)

    # Assert
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "My Test Project" in content
    assert "This is README content." in content
    assert "img.shields.io" in content and "MIT" in content


def test_generate_includes_existing_docs_rst(tmp_path: Path):
    # Arrange
    proj_dir = tmp_path / "myproj_rst"
    proj_dir.mkdir(parents=True)
    (proj_dir / "README.md").write_text("# My Test Project\n\nThis is README content.")
    (proj_dir / "LICENSE").write_text("MIT License\n\nCopyright 2025")

    parser = ProjectParser()
    project = parser.parse(str(proj_dir))
    gen = ProjectDocumentationGenerator(project)

    # Act
    out_file = gen.generate(format="rst", output_dir=None, template_path=None, legacy_output=False)

    # Assert
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "My Test Project" in content
    assert "This is README content." in content
    assert ".. image::" in content or "img.shields.io" in content
