import pytest
from unittest.mock import Mock, MagicMock
from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator
from ansibledoctor.models.collection import AnsibleCollection, PlaybookInfo
from ansibledoctor.models.galaxy import GalaxyMetadata

class TestGeneratePlaybooksSection:
    @pytest.fixture
    def mock_collection(self):
        metadata = GalaxyMetadata(
            namespace="test_ns",
            name="test_coll",
            version="1.0.0",
            authors=["me"],
            dependencies={}
        )
        playbooks = [
            PlaybookInfo(
                name="site",
                path="/path/to/site.yml",
                description="Main playbook",
                tags=["deploy", "web"]
            ),
            PlaybookInfo(
                name="db",
                path="/path/to/db.yml",
                description="Database playbook",
                tags=["db"]
            )
        ]
        return AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
            playbooks=playbooks
        )

    def test_generate_playbooks_section(self, mock_collection):
        """Test that playbooks section is generated correctly."""
        generator = CollectionDocumentationGenerator(mock_collection)
        
        # We need to ensure the template context includes playbooks
        # This test will fail until we update the generator to pass playbooks to the template
        # and update the template to render them.
        
        output = generator.generate(format="markdown")
        
        assert "## Playbooks" in output
        assert "site" in output
        assert "Main playbook" in output
        assert "deploy, web" in output
        assert "db" in output
        assert "Database playbook" in output
