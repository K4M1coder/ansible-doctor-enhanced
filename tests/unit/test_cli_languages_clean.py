from pathlib import Path

from click.testing import CliRunner

from ansibledoctor.cli.project import project as project_cli


def make_project(tmp_path: Path) -> Path:
    proj_dir = tmp_path / "myproj"
    (proj_dir / "roles" / "webserver").mkdir(parents=True)
    (proj_dir / "collections" / "my_namespace" / "my_collection").mkdir(parents=True)
    return proj_dir


def test_cli_generate_with_language_flag(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    trans_dir = proj_dir / ".ansibledoctor" / "translations"
    trans_dir.mkdir(parents=True, exist_ok=True)
    fr_file = trans_dir / "fr.yml"
    fr_file.write_text(
        """
project:
    title: 'Mon Projet'
roles:
    header: 'Rôles'
""",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--language", "fr"])
    assert result.exit_code == 0
    out = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "# Mon Projet" in content
