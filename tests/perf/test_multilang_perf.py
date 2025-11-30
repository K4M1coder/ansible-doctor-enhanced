import time
from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_medium_project(tmp_path: Path, name: str = "perf_project") -> Project:
    proj_dir = tmp_path / name
    proj_dir.mkdir()

    for role_name in [f"role_{i}" for i in range(10)]:
        roles_dir = proj_dir / "roles" / role_name
        roles_dir.mkdir(parents=True)
        (roles_dir / "tasks").mkdir()
        (roles_dir / "tasks" / "main.yml").write_text('- name: noop\n  debug: msg="noop"\n')

    collections_dir = proj_dir / "collections" / "my_collection"
    collections_dir.mkdir(parents=True)
    (collections_dir / "roles").mkdir(parents=True)

    # Write english translation
    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    (translations_dir / "en.yml").write_text(
        """
project:
    title: "My Project"
roles:
    header: "Roles"
""",
        encoding="utf-8",
    )

    roles = [
        RoleInfo(name=f"role_{i}", path=str(proj_dir / "roles" / f"role_{i}")) for i in range(10)
    ]
    collections = [CollectionInfo(name="my_collection", path=str(collections_dir))]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def test_multilang_perf(tmp_path: Path):
    p = make_medium_project(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)

    start = time.perf_counter()
    gen.generate(p, ["en", "fr", "de"])  # Generate for three languages
    elapsed = time.perf_counter() - start

    assert elapsed < 5.0, f"Multi-language generation took too long: {elapsed:.2f}s"
