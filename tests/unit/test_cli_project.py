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


def test_cli_generate_uses_template_path(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    tpl = tmp_path / "cli_template.j2"
    tpl.write_text("CLI TEMPLATE: {{ project.name }} - {{ roles|length }} roles")

    runner = CliRunner()
    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--template", str(tpl)])
    assert result.exit_code == 0
    out = proj_dir / "doc" / "README.md"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "CLI TEMPLATE" in content
    assert "roles" in content


def test_cli_parse_project_outputs_json(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()
    result = runner.invoke(project_cli, ["parse", str(proj_dir)])
    assert result.exit_code == 0
    # Should output JSON representation of the project
    import json
    data = json.loads(result.output)
    assert "name" in data
    assert "roles" in data
    assert "collections" in data
    assert "playbooks" in data


def test_cli_parse_project_with_redact_flag(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    # Add inventory with a host
    (proj_dir / "inventory").mkdir()
    (proj_dir / "inventory" / "hosts.ini").write_text("[webservers]\nhost1")
    # Add some vars to test redaction
    (proj_dir / "group_vars").mkdir(parents=True)
    (proj_dir / "group_vars" / "all.yml").write_text("password: secret123\ntoken: abcdef")
    runner = CliRunner()
    result = runner.invoke(project_cli, ["parse", str(proj_dir), "--redact-values"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    # Check that sensitive vars are redacted in effective_vars
    assert "***REDACTED***" in str(data)


def test_cli_parse_project_no_redact_flag(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    # Add inventory with a host
    (proj_dir / "inventory").mkdir()
    (proj_dir / "inventory" / "hosts.ini").write_text("[webservers]\nhost1")
    (proj_dir / "group_vars").mkdir(parents=True)
    (proj_dir / "group_vars" / "all.yml").write_text("password: secret123\ntoken: abcdef")
    runner = CliRunner()
    result = runner.invoke(project_cli, ["parse", str(proj_dir), "--no-redact-values"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    # Check that sensitive vars are NOT redacted in effective_vars
    assert "secret123" in str(data)
    assert "abcdef" in str(data)
