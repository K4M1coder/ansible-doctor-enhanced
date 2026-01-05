"""Unit tests for playbook discovery in collections.

Tests the discovery of playbook files in the playbooks/ directory of a collection.
"""

from pathlib import Path

import pytest

from ansibledoctor.parser.collection_parser import CollectionParser


@pytest.fixture
def collection_path(tmp_path):
    """Create a temporary collection structure with playbooks."""
    collection_dir = tmp_path / "my_namespace" / "my_collection"
    collection_dir.mkdir(parents=True)

    # Create galaxy.yml
    (collection_dir / "galaxy.yml").write_text(
        "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\nauthors: [Me]"
    )

    # Create playbooks directory
    playbooks_dir = collection_dir / "playbooks"
    playbooks_dir.mkdir()

    # Create some playbooks
    (playbooks_dir / "site.yml").write_text("---\n- name: Site playbook\n  hosts: all")
    (playbooks_dir / "webservers.yaml").write_text("---\n- name: Webservers\n  hosts: web")
    (playbooks_dir / "dbservers.yml").write_text(
        "---\n# Description: Database setup\n- name: DB\n  hosts: db"
    )
    (playbooks_dir / "not_a_playbook.txt").write_text("text file")

    return collection_dir


class TestPlaybookDiscovery:
    """Test discovery of playbooks in a collection."""

    def test_discover_playbooks_finds_files(self, collection_path):
        """Test that discover_playbooks finds .yml and .yaml files in playbooks/."""
        parser = CollectionParser()

        # This method doesn't exist yet, so this test will fail (RED)
        playbooks = parser.discover_playbooks(collection_path)

        assert len(playbooks) == 3
        filenames = [Path(p.path).name for p in playbooks]
        assert "site.yml" in filenames
        assert "webservers.yaml" in filenames
        assert "dbservers.yml" in filenames
        assert "not_a_playbook.txt" not in filenames

        # Verify PlaybookInfo model fields
        site = next(p for p in playbooks if Path(p.path).name == "site.yml")
        assert site.path == str(collection_path / "playbooks" / "site.yml")
        assert site.name == "site"  # Derived from filename stem

    def test_discover_playbooks_extracts_metadata(self, collection_path):
        """Test that discover_playbooks extracts description and tags."""
        parser = CollectionParser()
        playbooks = parser.discover_playbooks(collection_path)

        # dbservers.yml has description
        # Content: "---\n# Description: Database setup\n- name: DB\n  hosts: db"
        db = next(p for p in playbooks if Path(p.path).name == "dbservers.yml")
        assert db.description == "Database setup"
