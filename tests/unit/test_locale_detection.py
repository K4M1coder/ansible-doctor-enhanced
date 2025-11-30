import locale
from pathlib import Path

import yaml
from click.testing import CliRunner

from ansibledoctor.cli.project import project as project_group
from ansibledoctor.config.language import detect_system_language


def test_detect_system_language_positive(monkeypatch):
    monkeypatch.setattr(locale, "getdefaultlocale", lambda: ("fr_FR", "UTF-8"))
    assert detect_system_language() == "fr"


def test_cli_detect_system_appends_language(tmp_path: Path, monkeypatch):
    # Create project with .ansibledoctor.yml enabling detect_system
    proj_dir = tmp_path / "multilang_proj"
    proj_dir.mkdir()
    config = {
        "languages": {
            "detect_system": True,
        }
    }
    cfg_path = proj_dir / ".ansibledoctor.yml"
    cfg_path.write_text(yaml.dump(config), encoding="utf-8")

    # Create translations for fr
    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    (translations_dir / "fr.yml").write_text(
        "\nproject:\n  title: 'Mon Projet'\n", encoding="utf-8"
    )

    # Make minimal role and collection directories to run the generator
    (proj_dir / "roles" / "webserver").mkdir(parents=True)
    (proj_dir / "roles" / "webserver" / "tasks").mkdir()
    (proj_dir / "roles" / "webserver" / "tasks" / "main.yml").write_text(
        '- name: noop\n  debug: msg="noop"\n'
    )

    monkeypatch.setattr(locale, "getdefaultlocale", lambda: ("fr_FR", "UTF-8"))

    runner = CliRunner()
    res = runner.invoke(project_group, ["generate", str(proj_dir)])
    assert res.exit_code == 0
    # Should include 'fr' in the message when detect_system adds it to languages
    assert "fr" in res.output
