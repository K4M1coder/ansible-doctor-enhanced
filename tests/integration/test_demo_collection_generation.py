"""Integration tests: use demo artifacts to generate collection documentation via CLI.

Ensures that the CLI collection generate command uses demo collection layout and
creates docs in the collection's `docs` subfolder by default.
"""
from pathlib import Path
from click.testing import CliRunner

from ansibledoctor.cli import cli


def test_collection_generate_creates_doc_in_demo(tmp_path):
    repo_root = Path(__file__).parent.parent.parent
    demo_collection = repo_root / "demo" / "collection_demo_namespace.demo_collection"
    assert demo_collection.exists()

    runner = CliRunner()
    result = runner.invoke(cli, ["collection", "generate", str(demo_collection)])
    assert result.exit_code == 0, f"CLI failed: {result.output}"

    # The generator writes README.md in `docs` subdirectory by default
    doc_file = demo_collection / "docs" / "README.md"
    assert doc_file.exists(), f"Doc not created at {doc_file}"
    content = doc_file.read_text(encoding="utf-8")
    assert "demo_collection" in content or "demo_namespace" in content
