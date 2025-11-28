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
    output_file = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
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
    out = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
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


def test_cli_generate_uses_project_slug_for_default_path(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()

    result = runner.invoke(project_cli, ["generate", str(proj_dir)])
    assert result.exit_code == 0
    # Should use docs/ansibleproject_{projectname}/README.md
    expected_path = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
    assert expected_path.exists()
    # Also check that the old path doesn't exist
    old_path = proj_dir / "doc" / "README.md"
    assert not old_path.exists()


def test_cli_generate_legacy_output_uses_simple_path(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()

    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--legacy-output"])
    assert result.exit_code == 0
    # Should use docs/README.md (legacy path)
    expected_path = proj_dir / "docs" / "README.md"
    assert expected_path.exists()
    # Check that the new slug path doesn't exist
    slug_path = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
    assert not slug_path.exists()


def test_cli_generate_language_option_respects_translations(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    # Create translation file in project
    trans_dir = proj_dir / ".ansibledoctor" / "translations"
    trans_dir.mkdir(parents=True, exist_ok=True)
    fr_file = trans_dir / "fr.yml"
    fr_file.write_text("project.title: 'Mon Projet'\nroles.header: 'Rôles'\ncollections.header: 'Collections'\narchitecture.header: 'Architecture'", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--language", "fr"]) 
    assert result.exit_code == 0
    out = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "# Mon Projet" in content
    assert "## Rôles" in content


def test_cli_analyze_project_outputs_analysis(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()
    result = runner.invoke(project_cli, ["analyze", str(proj_dir)])
    assert result.exit_code == 0
    # Should output analysis JSON
    import json
    data = json.loads(result.output)
    assert "project" in data
    assert "analysis" in data


def test_cli_visualize_project_outputs_diagram(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    runner = CliRunner()
    result = runner.invoke(project_cli, ["visualize", str(proj_dir)])
    assert result.exit_code == 0
    # Should output Mermaid diagram
    assert "graph TD" in result.output or "mermaid" in result.output.lower()


def test_cli_analyze_playbook_generates_task_flow_mermaid(tmp_path: Path):
        proj_dir = make_project(tmp_path)
        # Create playbook
        playbooks_dir = proj_dir / "playbooks"
        playbooks_dir.mkdir()
        pb = playbooks_dir / "site.yml"
        pb.write_text("- name: Site\n  hosts: web\n  tasks:\n    - name: task a\n      debug: msg=hello\n", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(project_cli, ["analyze", str(proj_dir), "--playbook", "site.yml"])
        assert result.exit_code == 0
        assert "graph TD" in result.output


def test_cli_analyze_playbook_generates_task_flow_json(tmp_path: Path):
        proj_dir = make_project(tmp_path)
        playbooks_dir = proj_dir / "playbooks"
        playbooks_dir.mkdir()
        pb = playbooks_dir / "site.yml"
        pb.write_text("- name: Site\n  hosts: web\n  tasks:\n    - name: task a\n      debug: msg=hello\n", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(project_cli, ["analyze", str(proj_dir), "--playbook", "site.yml", "--format", "json"])
        assert result.exit_code == 0
        assert "playbook" in result.output and "nodes" in result.output
