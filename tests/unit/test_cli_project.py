from pathlib import Path
from click.testing import CliRunner
from ansibledoctor.cli.project import project as project_cli


def make_project(tmp_path: Path) -> Path:
    proj_dir = tmp_path / "myproj"
    (proj_dir / "roles" / "webserver").mkdir(parents=True)
    (proj_dir / "collections" / "my_namespace" / "my_collection").mkdir(parents=True)
    return proj_dir


def test_cli_generate_markdown_default(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()

    result = runner.invoke(project_cli, ["generate", str(proj_dir)])
    assert result.exit_code == 0
    output_file = proj_dir / "doc" / "README.md"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "# myproj" in content or "# My Project" in content


def test_cli_generate_html_with_relative_output_dir(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()

    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--format", "html", "--output-dir", "out"])
    assert result.exit_code == 0
    output_file = proj_dir / "out" / "README.html"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_cli_generate_html_with_explicit_absolute_output_dir(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    out_dir = tmp_path / "external_out"
    out_dir.mkdir()
    runner = CliRunner()

    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--format", "html", "--output-dir", str(out_dir)])
    assert result.exit_code == 0
    output_file = out_dir / "README.html"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "<h1>" in content


def test_cli_generate_handles_exception(tmp_path: Path, monkeypatch):
    proj_dir = make_project(tmp_path)
    # Force the parser to raise an exception
    def fake_parse(self, path):
        raise RuntimeError("boom")

    monkeypatch.setattr("ansibledoctor.parser.project_parser.ProjectParser.parse", fake_parse)
    runner = CliRunner()
    result = runner.invoke(project_cli, ["generate", str(proj_dir)])
    assert result.exit_code == 1
    assert "Unexpected error: boom" in result.output
