import pytest
from pathlib import Path
from ansibledoctor.parser.collection_parser import CollectionParser

def test_collection_existing_docs_integration(tmp_path):
    """Test full integration of existing docs extraction in collection parsing."""
    # Create collection structure
    collection_dir = tmp_path / "my_namespace" / "my_collection"
    collection_dir.mkdir(parents=True)
    (collection_dir / "galaxy.yml").write_text("namespace: my_namespace\nname: my_collection\nversion: 1.0.0")
    
    # Create docs
    (collection_dir / "README.md").write_text("# My Collection")
    (collection_dir / "CHANGELOG.md").write_text("# Changelog")
    (collection_dir / "LICENSE").write_text("MIT License")
    
    # Parse
    parser = CollectionParser()
    collection = parser.parse(collection_dir)
    
    # Verify
    assert collection.existing_docs is not None
    assert collection.existing_docs.readme_content == "# My Collection"
    assert collection.existing_docs.changelog_content == "# Changelog"
    assert collection.existing_docs.license_content == "MIT License"
    assert collection.existing_docs.license_type == "MIT"
