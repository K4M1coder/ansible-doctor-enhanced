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
    assert out.exists(), f"Missing README at {out}"
    content = out.read_text(encoding="utf-8")
    assert "# Mon Projet" in content
    assert "## Rôles" in content


def test_cli_generate_with_languages_flag(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    # rely on embedded translations for 'en' and 'fr' provided by the package
    runner = CliRunner()
    result = runner.invoke(project_cli, ["generate", str(proj_dir), "--languages", "en,fr"])
    assert result.exit_code == 0
    out_en = proj_dir / "docs" / "lang" / "en" / "ansibleproject_myproj" / "README.md"
    out_fr = proj_dir / "docs" / "lang" / "fr" / "ansibleproject_myproj" / "README.md"
    assert out_en.exists(), f"Missing en README at {out_en}"
    assert out_fr.exists(), f"Missing fr README at {out_fr}"


def test_cli_respects_config_file_languages(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    # Create a config file specifying languages
    config_file = proj_dir / ".ansibledoctor.yml"
    config_file.write_text(
        """
languages:
    default: fr
    enabled:
        - fr
        - en
    fallback: en
    detect_system: false
"""
    )

    # Create project-level translations for FR
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
    result = runner.invoke(project_cli, ["generate", str(proj_dir)])
    assert result.exit_code == 0, f"CLI failed: {result.output}"

    out_en = proj_dir / "docs" / "lang" / "en" / "ansibleproject_myproj" / "README.md"
    out_fr = proj_dir / "docs" / "lang" / "fr" / "ansibleproject_myproj" / "README.md"
    assert out_en.exists(), "English language output missing"
    assert out_fr.exists(), "French language output missing"


def test_cli_language_flag_overrides_config_file(tmp_path: Path):
    proj_dir = make_project(tmp_path)
    # Create config specifying only 'en' but request '--language fr'
    config_file = proj_dir / ".ansibledoctor.yml"
    config_file.write_text(
        """
languages:
    default: en
    enabled:
        - en
    fallback: en
    detect_system: false
"""
    )

    # Create project-level FR translation
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
    # Since we asked for fr, ensure FR README exists
    out_fr = proj_dir / "docs" / "ansibleproject_myproj" / "README.md"
    assert out_fr.exists(), f"Missing fr README at {out_fr}"
    content = out_fr.read_text(encoding="utf-8")
    assert "# Mon Projet" in content
