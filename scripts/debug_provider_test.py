import tempfile
from pathlib import Path

from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader

p_dir = Path(tempfile.mkdtemp()) / "myproj"
p_dir.mkdir()
roles_dir = p_dir / "roles" / "webserver"
roles_dir.mkdir(parents=True)
(roles_dir / "tasks").mkdir()
(roles_dir / "tasks" / "main.yml").write_text('- name: noop\n  debug: msg="noop"\n')
trans_dir = p_dir / ".ansibledoctor" / "translations"
trans_dir.mkdir(parents=True)
(trans_dir / "en.yml").write_text(
    '\nproject:\n    title: "My Project"\nroles:\n    header: "Roles"\n', encoding="utf-8"
)
(trans_dir / "fr.yml").write_text('\nroles:\n    header: "R\u00f4les"\n', encoding="utf-8")
proj = Project(
    name="My Project",
    path=str(p_dir),
    roles=[RoleInfo(name="webserver", path=str(roles_dir))],
    collections=[
        CollectionInfo(name="my_collection", path=str(p_dir / "collections" / "my_collection"))
    ],
)
loader = TranslationLoader()
prov = loader.load("es", p_dir)
print("resolved lang", prov.lang)
print("requested lang", prov._requested_lang)
print("fallback", prov._fallback_lang)
print("provider translations", prov._translations)
print("provider orig_translations", prov._orig_translations)
print("t(project.title) =", prov.t("project.title"))
print("t(roles.header) =", prov.t("roles.header"))
print("lookup project", prov._lookup("project"))
print("lookup project.title", prov._lookup("project.title"))
