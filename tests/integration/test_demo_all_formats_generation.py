"""Integration: generate docs in all formats for demo artifacts (role, collection, project).

Ensures the CLI supports producing markdown, html and rst outputs for demo artifacts
and writes outputs to the artifact demo folders (role->doc, collection->docs, project->doc).
"""

import re
import shutil
from pathlib import Path

from click.testing import CliRunner

try:
    import html5lib  # type: ignore

    HAS_HTML5LIB = True
except Exception:
    HAS_HTML5LIB = False

try:
    from docutils.core import publish_parts  # type: ignore

    HAS_DOCUTILS = True
except Exception:
    HAS_DOCUTILS = False

from ansibledoctor.cli import cli

FORMATS = ["markdown", "html", "rst"]


def test_generate_all_formats_for_demo_role(tmp_path):
    repo_root = Path(__file__).parent.parent.parent
    original_demo_role = repo_root / "demo" / "role_demo_namespace.demo_demo_role"
    demo_role = tmp_path / "role_demo_namespace.demo_demo_role"
    shutil.copytree(original_demo_role, demo_role)
    assert demo_role.exists()

    runner = CliRunner()
    for fmt in FORMATS:
        ext = "md" if fmt == "markdown" else ("html" if fmt == "html" else "rst")
        out_file = demo_role / "doc" / f"README.{ext}"
        # Call CLI generate for role specifying output path
        result = runner.invoke(
            cli, ["generate", str(demo_role), "--format", fmt, "--output", str(out_file)]
        )
        assert result.exit_code == 0, f"Failed to generate for role {fmt}: {result.output}"
        assert out_file.exists(), f"Role output missing: {out_file}"
        content = out_file.read_text(encoding="utf-8")
        if fmt == "html":
            if HAS_HTML5LIB:
                # parse to catch HTML errors
                doc = html5lib.parse(content)
                assert doc is not None
            else:
                assert re.search(r"<html|<!DOCTYPE html", content, flags=re.I)
        elif fmt == "rst":
            if HAS_DOCUTILS:
                # Try parse with docutils to validate RST syntax; will raise on serious errors
                publish_parts(content, writer_name="html")
            else:
                assert "=" * 3 in content or "-" * 3 in content
        else:
            assert "#" in content or "Roles" in content


def test_generate_all_formats_for_demo_collection(tmp_path):
    repo_root = Path(__file__).parent.parent.parent
    original_demo_collection = repo_root / "demo" / "collection_demo_namespace.demo_collection"
    demo_collection = tmp_path / "collection_demo_namespace.demo_collection"
    shutil.copytree(original_demo_collection, demo_collection)
    assert demo_collection.exists()

    runner = CliRunner()
    for fmt in FORMATS:
        ext = "md" if fmt == "markdown" else ("html" if fmt == "html" else "rst")
        # Use default collection-cli output-dir (docs)
        result = runner.invoke(
            cli, ["collection", "generate", str(demo_collection), "--format", fmt]
        )
        assert result.exit_code == 0, f"Failed to generate collection {fmt}: {result.output}"
        out_file = demo_collection / "docs" / f"README.{ext}"
        assert out_file.exists(), f"Collection output missing: {out_file}"
        content = out_file.read_text(encoding="utf-8")
        if fmt == "html":
            if HAS_HTML5LIB:
                doc = html5lib.parse(content)
                assert doc is not None
            else:
                assert re.search(r"<html|<!DOCTYPE html", content, flags=re.I)
        elif fmt == "rst":
            if HAS_DOCUTILS:
                publish_parts(content, writer_name="html")
            else:
                assert "=" * 3 in content or "-" * 3 in content
        else:
            assert "#" in content or "Collection:" in content


def test_generate_all_formats_for_demo_project(tmp_path):
    repo_root = Path(__file__).parent.parent.parent
    original_demo_project = repo_root / "demo" / "project_demo_namespace.demo_project"
    demo_project = tmp_path / "project_demo_namespace.demo_project"
    shutil.copytree(original_demo_project, demo_project)
    assert demo_project.exists()

    runner = CliRunner()
    for fmt in FORMATS:
        ext = "md" if fmt == "markdown" else ("html" if fmt == "html" else "rst")
        out_file = demo_project / "doc" / f"README.{ext}"
        result = runner.invoke(
            cli,
            [
                "project",
                "generate",
                str(demo_project),
                "--format",
                fmt,
                "--legacy-output",
                "--output-dir",
                str(demo_project / "doc"),
            ],
        )
        assert result.exit_code == 0, f"Failed to generate project {fmt}: {result.output}"
        assert out_file.exists(), f"Project output missing: {out_file}"
        content = out_file.read_text(encoding="utf-8")
        if fmt == "html":
            if HAS_HTML5LIB:
                doc = html5lib.parse(content)
                assert doc is not None
            else:
                assert re.search(r"<html|<!DOCTYPE html", content, flags=re.I)
        elif fmt == "rst":
            if HAS_DOCUTILS:
                publish_parts(content, writer_name="html")
            else:
                assert "=" * 3 in content or "-" * 3 in content
        else:
            assert "#" in content or "Roles" in content
