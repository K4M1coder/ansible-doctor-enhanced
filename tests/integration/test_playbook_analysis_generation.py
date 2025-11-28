from click.testing import CliRunner
from ansibledoctor.cli.project import project as project_cli
from pathlib import Path


def test_demo_project_analyze_playbook_mermaid(tmp_path: Path):
    # Use a small demo project structure
    proj_dir = tmp_path / "demo_project"
    proj_dir.mkdir()
    (proj_dir / "roles" / "webserver").mkdir(parents=True)
    (proj_dir / "playbooks").mkdir()
    pb = proj_dir / "playbooks" / "site.yml"
    pb.write_text("- name: Site\n  hosts: web\n  tasks:\n    - name: ensure package\n      debug: msg=ok\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(project_cli, ["analyze", str(proj_dir), "--playbook", "site.yml"])
    assert result.exit_code == 0
    assert "graph TD" in result.output
