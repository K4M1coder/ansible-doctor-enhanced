"""Integration tests for i18n fallback behavior.

Verifies that when a translation key is missing in a requested language,
the content falls back to a configured fallback language (e.g., English).
"""

from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_project_with_en_only(tmp_path: Path, name: str = "myproj") -> Project:
    proj_dir = tmp_path / name
    proj_dir.mkdir()

    roles_dir = proj_dir / "roles" / "webserver"
    roles_dir.mkdir(parents=True)
    (roles_dir / "tasks").mkdir()
    (roles_dir / "tasks" / "main.yml").write_text('- name: noop\n  debug: msg="noop"\n')

    # Write English translation and a French translation that is intentionally
    # missing `project.title` to test fallback behavior for missing keys.
    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    (translations_dir / "en.yml").write_text(
        'project.title: "My Project"\nroles.header: "Roles"\n', encoding="utf-8"
    )
    # FR translation intentionally missing project.title
    (translations_dir / "fr.yml").write_text('roles.header: "Rôles"\n', encoding="utf-8")

    roles = [RoleInfo(name="webserver", path=str(roles_dir))]
    collections = [
        CollectionInfo(name="my_collection", path=str(proj_dir / "collections" / "my_collection"))
    ]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def test_i18n_fallback_to_en(tmp_path: Path):
    p = make_project_with_en_only(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)
    # Generate content for an unsupported language 'es' even though only English is present
    gen.generate(p, ["es"])

    out_fr = Path(p.path) / "docs" / "lang" / "es" / "ansibleproject_my-project" / "README.md"
    assert out_fr.exists()
    # Should fall back to the English content (project.title == "My Project")
    assert out_fr.read_text(encoding="utf-8").startswith("# My Project")
