"""Integration test for generate project docs including existing docs (T342).

Parses and generates documentation for the demo project and validates the
generated README includes existing project README content and license badge.
"""
from pathlib import Path
from click.testing import CliRunner
from ansibledoctor.cli.project import project as project_cli
from ansibledoctor.utils.slug import project_slug


def test_demo_generate_existing_docs():
    demo_path = Path(__file__).parent.parent.parent / "demo" / "project_demo_namespace.demo_project"
    runner = CliRunner()
    # Invoke for markdown (default)
    result = runner.invoke(project_cli, ["generate", str(demo_path)])
    assert result.exit_code == 0
    expected_slug = project_slug(Path(demo_path).name)
    out = demo_path / "docs" / expected_slug / "README.md"
    # Some demo projects may use different slug rules; fallback: check docs/README if legacy
    if not out.exists():
        out = demo_path / "docs" / "README.md"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    # Check demo README and license information included
    assert "Demo Project" in content
    assert "img.shields.io" in content

    # Also generate and verify HTML and RST explicitly to ensure templates include README and license badges
    for fmt in ["html", "rst"]:
        result = runner.invoke(project_cli, ["generate", str(demo_path), "--format", fmt])
        assert result.exit_code == 0
        out_file = demo_path / "docs" / expected_slug / f"README.{fmt}"
        # Some template loaders may write to legacy output; fallback to docs/README
        if not out_file.exists():
            out_file = demo_path / "docs" / f"README.{fmt}"
        assert out_file.exists()
        text = out_file.read_text(encoding="utf-8")
        assert "Demo Project" in text or "project_demo_namespace.demo_project" in text
        # Check license badge presence
        if fmt == "html":
            assert "img.shields.io" in text
        else:
            assert ".. image::" in text or "img.shields.io" in text