"""Integration test verifying per-key fallback for custom (unknown) languages.

If a requested language has only some keys defined, missing keys should be
filled from the configured fallback language (EN) while existing keys are used
from the requested language.
"""

from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_project_with_custom_lang(tmp_path: Path, name: str = "myproj") -> Project:
    proj_dir = tmp_path / name
    proj_dir.mkdir()

    roles_dir = proj_dir / "roles" / "webserver"
    roles_dir.mkdir(parents=True)
    (roles_dir / "tasks").mkdir()
    (roles_dir / "tasks" / "main.yml").write_text('- name: noop\n  debug: msg="noop"\n')

    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    # Only put 'roles.header' for custom language 'xx'
    (translations_dir / "xx.yml").write_text(
        """
roles:
    header: "Rôles-XX"
""",
        encoding="utf-8",
    )
    # Include an english title in project translation
    (translations_dir / "en.yml").write_text(
        """
project:
    title: "My Project"
roles:
    header: "Roles"
""",
        encoding="utf-8",
    )

    roles = [RoleInfo(name="webserver", path=str(roles_dir))]
    collections = [
        CollectionInfo(name="my_collection", path=str(proj_dir / "collections" / "my_collection"))
    ]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def test_i18n_per_key_fallback_custom_lang(tmp_path: Path):
    p = make_project_with_custom_lang(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)
    # Generate content for the custom language 'xx'
    gen.generate(p, ["xx"])  # Unknown language code; project provides partial translations

    out_xx = Path(p.path) / "docs" / "lang" / "xx" / "ansibleproject_my-project" / "README.md"
    assert out_xx.exists()
    content = out_xx.read_text(encoding="utf-8")

    # Expect title to be pulled from English fallback (project.title)
    assert content.startswith("# My Project")
    # Expect roles header to be from custom language 'xx'
    assert "## Rôles-XX" in content
