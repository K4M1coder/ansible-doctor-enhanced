"""Integration tests: use demo artifacts to generate project documentation via CLI.

Ensures that the CLI project generate command uses demo project layout and
creates docs in the project's `doc` subfolder.
"""
from pathlib import Path
from click.testing import CliRunner

from ansibledoctor.cli import cli


def test_project_generate_creates_doc_in_demo(tmp_path):
    # Use the demo project created under the repository
    repo_root = Path(__file__).parent.parent.parent
    demo_project = repo_root / "demo" / "project_demo_namespace.demo_project"
    assert demo_project.exists()

    runner = CliRunner()
    result = runner.invoke(cli, ["project", "generate", str(demo_project)])

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    # The generator writes README.md in `docs/ansibleproject_{projectname}/` subdirectory
    doc_file = demo_project / "docs" / "ansibleproject_project-demo-namespace-demo-project" / "README.md"
    assert doc_file.exists(), f"Doc not created at {doc_file}"
    content = doc_file.read_text(encoding="utf-8")
    assert "Roles" in content or "Collections" in content
    # Check for Mermaid diagram
    assert "## Architecture" in content
    assert "```mermaid" in content
