import tempfile
from pathlib import Path

from click.testing import CliRunner

from ansibledoctor.cli.project import project as project_cli

# replicate make_project
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    proj_dir = tmp / "myproj"
    (proj_dir / "roles" / "webserver").mkdir(parents=True)
    (proj_dir / "collections" / "my_namespace" / "my_collection").mkdir(parents=True)
    print("proj_dir:", proj_dir)
    runner = CliRunner()
    res = runner.invoke(project_cli, ["generate", str(proj_dir), "--languages", "en,fr"])
    print("res.exit_code", res.exit_code)
    for p in proj_dir.rglob("README.*"):
        print("found:", p)
    # walk docs
    for p in proj_dir.glob("docs/**"):
        print("docs glob:", p)
    print("Done")
