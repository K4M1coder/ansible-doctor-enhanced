import pytest
import os
from unittest.mock import Mock
from jinja2 import Environment, FileSystemLoader
from ansibledoctor.models.collection import AnsibleCollection, PlaybookInfo
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.existing_docs import ExistingDocs
from ansibledoctor.generator.collection_generator import CollectionTemplateContext

@pytest.fixture
def mock_collection_with_docs():
    metadata = GalaxyMetadata(
        namespace="test_ns",
        name="test_coll",
        version="1.0.0",
        authors=["me"],
        license=["MIT"]
    )
    existing_docs = ExistingDocs(
        readme_content="# My README\n\nThis is the readme.",
        changelog_content="# Changelog\n\n- Initial release",
        license_content="MIT License",
        contributing_content="# Contributing\n\nPlease contribute."
    )
    return AnsibleCollection(
        metadata=metadata,
        existing_docs=existing_docs
    )

def test_context_includes_existing_docs(mock_collection_with_docs):
    """Test that CollectionTemplateContext includes existing_docs."""
    context_builder = CollectionTemplateContext(
        collection=mock_collection_with_docs,
        plugins=[]
    )
    context = context_builder.build()
    
    assert "collection" in context
    assert context["collection"].existing_docs is not None
    assert context["collection"].existing_docs.readme_content == "# My README\n\nThis is the readme."

def test_render_includes_existing_docs(mock_collection_with_docs):
    """Test that the rendered template includes existing docs content."""
    # Setup Jinja2 environment to load the actual template
    # We need to point to the correct directory relative to where pytest is run
    # Assuming pytest is run from the root of the repo
    template_dir = os.path.abspath("ansibledoctor/generator/templates/markdown")
    
    # We need to mock the _breadcrumb.j2 include or ensure it exists
    # Since we are using the real template dir, it should exist.
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("collection.j2")
    
    # Build context
    context_builder = CollectionTemplateContext(
        collection=mock_collection_with_docs,
        plugins=[]
    )
    context = context_builder.build()
    
    # Render
    output = template.render(**context)
    
    # Assertions
    assert "## README" in output
    assert "# My README" in output
    assert "This is the readme." in output
    
    assert "## Changelog" in output
    assert "- Initial release" in output
    
    assert "## Contributing" in output
    assert "Please contribute." in output
    
    assert "## License" in output
    assert "MIT License" in output
    # Should NOT have the fallback text
    assert "See LICENSE file in the collection." not in output

