import pytest
from pathlib import Path
from ansibledoctor.parser.collection_parser import CollectionParser

def test_collection_playbooks_integration(tmp_path):
    """Test full integration of playbook discovery in collection parsing."""
    # Create collection structure
    collection_dir = tmp_path / "my_namespace" / "my_collection"
    collection_dir.mkdir(parents=True)
    (collection_dir / "galaxy.yml").write_text("namespace: my_namespace\nname: my_collection\nversion: 1.0.0")
    
    playbooks_dir = collection_dir / "playbooks"
    playbooks_dir.mkdir()
    
    # Create playbooks
    (playbooks_dir / "site.yml").write_text("---\n- hosts: all\n  roles: []")
    (playbooks_dir / "db.yml").write_text("---\n# Description: DB Setup\n- hosts: db\n  tags: [database, sql]")
    
    # Parse
    parser = CollectionParser()
    collection = parser.parse(collection_dir)
    
    # Verify
    assert len(collection.playbooks) == 2
    
    site = next(p for p in collection.playbooks if p.name == "site")
    assert site.description is None
    
    db = next(p for p in collection.playbooks if p.name == "db")
    assert db.description == "DB Setup"
    assert "database" in db.tags
    assert "sql" in db.tags
