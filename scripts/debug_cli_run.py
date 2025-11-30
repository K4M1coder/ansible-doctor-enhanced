from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from ansibledoctor.cli.project import project as project_cli

with TemporaryDirectory() as tmp:
    proj_dir = Path(tmp) / "myproj"
    (proj_dir / "roles" / "webserver").mkdir(parents=True)
    (proj_dir / "collections" / "my_namespace" / "my_collection").mkdir(parents=True)
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
    print("exit_code=", result.exit_code)
    print("output:")
    print(result.output)
    if result.exception:
        import traceback

        traceback.print_exception(
            result.exception, result.exception, result.exception.__traceback__
        )
