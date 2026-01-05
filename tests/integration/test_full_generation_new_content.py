from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator
from ansibledoctor.parser.collection_parser import CollectionParser


def test_full_generation_with_playbooks_and_docs(tmp_path):
    # 1. Setup mock collection
    collection_dir = tmp_path / "my_namespace" / "my_collection"
    collection_dir.mkdir(parents=True)

    # galaxy.yml
    (collection_dir / "galaxy.yml").write_text(
        """
namespace: my_namespace
name: my_collection
version: 1.0.0
authors:
  - Me
readme: README.md
"""
    )

    # README.md
    (collection_dir / "README.md").write_text("# My Collection README\n\nIntro text.")

    # CHANGELOG.md
    (collection_dir / "CHANGELOG.md").write_text("# Changelog\n\n- v1.0.0")

    # Playbooks
    playbooks_dir = collection_dir / "playbooks"
    playbooks_dir.mkdir()
    (playbooks_dir / "site.yml").write_text(
        """
# description: Main site playbook
---
- name: Site Playbook
  hosts: all
  tags: [deploy, site]
  tasks: []
"""
    )  # 2. Parse
    parser = CollectionParser()
    collection = parser.parse(collection_dir)

    # 3. Generate
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_file = output_dir / "README.md"

    generator = CollectionDocumentationGenerator(collection=collection)
    generator.generate(format="markdown", output_path=output_file)

    # 4. Verify
    assert output_file.exists()
    content = output_file.read_text()

    # Check Playbooks
    assert "## Playbooks" in content
    assert "site" in content
    assert "Main site playbook" in content
    assert "deploy, site" in content  # Check Existing Docs
    assert "## README" in content
    assert "# My Collection README" in content
    assert "## Changelog" in content
    assert "- v1.0.0" in content
