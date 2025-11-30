import os
import subprocess
import sys
from pathlib import Path


def test_demo_collection_outputs_to_docs_collections(tmp_path, capsys):
    # Run run_demo_in_precommit.py and verify collection docs generated under tempdir/docs/collections/<name>
    project_root = Path(__file__).resolve().parents[2]
    script = project_root / "scripts" / "run_demo_in_precommit.py"

    # Run script with default behavior (no staging)
    env = os.environ.copy()
    env["ANSIBLE_DOCTOR_DEMO_KEEP_TEMP"] = "1"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        print("STDOUT:", proc.stdout)
        print("STDERR:", proc.stderr)
    assert proc.returncode == 0
    out = proc.stdout + "\n" + proc.stderr
    print("DEMO SCRIPT OUTPUT:\n", out)
    assert (
        "Generated docs written to temp directory" in out
        or "All demo commands executed successfully." in out
    )

    # The script prints a JSON summary line 'DEMO_OUTPUT_JSON={...}'; prefer parsing it for robust detection
    import json
    import re

    tmp_parent = None
    doc_paths: list[Path] = []
    json_summary = None
    for line in out.splitlines():
        if line.startswith("DEMO_OUTPUT_JSON="):
            try:
                json_str = line.split("DEMO_OUTPUT_JSON=", 1)[1].strip()
                json_summary = json.loads(json_str)
                tmp_parent = Path(json_summary.get("base")) if json_summary.get("base") else None
                doc_paths = [Path(p) for p in json_summary.get("files", [])]
                break
            except Exception:
                # fallback to legacy parsing if JSON parse fails
                json_summary = None
                continue

    # If no JSON summary was found, fallback to legacy parsing
    if json_summary is None:
        tmp_parent = None
        doc_paths = []
        # Parse 'Demo temp base path: <path>' or 'Documentation generated: <path>' for temp paths
        for line in out.splitlines():
            if "Demo temp base path:" in line:
                # extract path after colon
                p = Path(line.split("Demo temp base path:", 1)[1].strip())
                # Assign base path (may be created later); prefer doc-generated paths
                tmp_parent = p
                # Do not break: allow scanning other lines for explicit generated docs
            # New: check for machine-friendly env-like var printed by script
            if line.startswith("DEMO_TEMP_BASE="):
                p = Path(line.split("DEMO_TEMP_BASE=", 1)[1].strip())
                tmp_parent = p
            if "Documentation generated:" in line and "collections" in line:
                # format: Documentation generated: C:\path\to\temp\...\README.md
                path_str = line.split("Documentation generated:", 1)[1].strip()
                p = Path(path_str)
                doc_paths.append(p)

        # Attempt a regex over the entire output (with newlines collapsed) so we can find wrapped paths
        single_line_out = re.sub(r"\s+", " ", out)
        # Look for paths like C:\\...ansibledoctor-demo-...\\docs\\collections\\...\\README.md
        coll_matches = re.findall(
            r"([A-Za-z]:\\\\[^\s]*ansibledoctor-demo-[^\\\s]*\\\\docs\\\\collections\\\\[^\s]*)",
            single_line_out,
        )
        if coll_matches:
            for m in coll_matches:
                doc_paths.append(Path(m))

        # If not found in doc paths, fallback: scan tempdir pattern in system temp
        # If not found in output, try to find path using regex
        if tmp_parent is None:
            # look for Windows or Unix-like path in output
            matches = re.findall(r"([A-Za-z]:\\\\[^\s]*ansibledoctor-demo-[^\s]*)", out)
            if matches:
                # take latest match
                tmp_parent = Path(matches[-1])

        if tmp_parent is None:
            from tempfile import gettempdir

            temp_root = Path(gettempdir())
            matches = list(temp_root.glob("ansibledoctor-demo-*"))
            # Try to find a matching directory that has a docs/collections/*/README.md
            candidate = None
            for d in sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True):
                # look for collections dir under d
                coll_root = d / "docs" / "collections"
                if coll_root.exists():
                    candidate = coll_root
                    break
            if candidate:
                tmp_parent = candidate

    assert tmp_parent is not None or doc_paths, "Could not locate demo temp dir in script output"

    print("TMP_PARENT:", tmp_parent)
    print("TMP_PARENT_EXISTS:", tmp_parent.exists())
    print("TMP_PARENT_PARENT:", tmp_parent.parent)
    print("TMP_PARENT_PARENT_EXISTS:", tmp_parent.parent.exists())

    # Prefer explicit doc_paths for collections; otherwise, normalize tmp_parent to docs/collections.
    collection_dir = None
    for p in doc_paths:
        if "collections" in p.parts:
            # parents[1] of README.md -> docs/collections
            collection_dir = p.parents[1]
            break
    if collection_dir is None:
        # If tmp_parent points to the repo base (temp dir), normalize to docs/collections under it.
        if tmp_parent and tmp_parent.name == "collections":
            collection_dir = tmp_parent
        elif tmp_parent and (tmp_parent / "docs" / "collections").exists():
            collection_dir = tmp_parent / "docs" / "collections"
        else:
            collection_dir = (
                tmp_parent
                if tmp_parent and tmp_parent.name == "collections"
                else (tmp_parent.parent / "collections")
            )
    # One of the demo collections should exist - prefer checking the explicit doc paths
    if doc_paths:
        # At minimum, the CLI printed the generated docs path(s) for the collection; assert FQCN present
        assert any(
            "collection_demo_namespace.demo_collection" in str(p) for p in doc_paths
        ), f"Expected collection FQCN to be present in doc paths: {doc_paths}"
    else:
        assert (
            collection_dir is not None and collection_dir.exists()
        ), f"Expected collections directory under temp demo output: {collection_dir}"

    # Check that README exists for our demo collection
    found = False
    for child in collection_dir.iterdir():
        if child.is_dir():
            readme_md = child / "README.md"
            if readme_md.exists():
                found = True
                content = readme_md.read_text(encoding="utf-8")
                assert "demo_namespace.demo_collection" in content
                break

    assert found, "Demo collection README.md not found in generated output"
