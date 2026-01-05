from ansibledoctor.models.existing_docs import ExistingDocs
from ansibledoctor.parser.docs_extractor import DocsExtractor


class TestCollectionExistingDocs:
    def test_extract_collection_docs(self, tmp_path):
        """Test extracting docs from a collection root."""
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)

        (collection_dir / "README.md").write_text("# My Collection")
        (collection_dir / "CHANGELOG.md").write_text("# Changelog")
        (collection_dir / "LICENSE").write_text("MIT License")

        extractor = DocsExtractor(str(collection_dir))
        docs = extractor.extract()

        assert isinstance(docs, ExistingDocs)
        assert docs.readme_content == "# My Collection"
        assert docs.changelog_content == "# Changelog"
        assert docs.license_content == "MIT License"
        assert docs.license_type == "MIT"

    def test_license_detection(self, tmp_path):
        """Test license type detection."""
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)

        # Apache 2.0
        (collection_dir / "LICENSE").write_text("Apache License Version 2.0")
        extractor = DocsExtractor(str(collection_dir))
        docs = extractor.extract()
        assert docs.license_type == "Apache-2.0"

        # GPL 3.0
        (collection_dir / "LICENSE").write_text("GNU General Public License Version 3")
        extractor = DocsExtractor(str(collection_dir))
        docs = extractor.extract()
        assert docs.license_type == "GPL-3.0"

    def test_extract_partial_docs(self, tmp_path):
        """Test extracting partial docs (only README)."""
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)

        (collection_dir / "README.md").write_text("# My Collection")

        extractor = DocsExtractor(str(collection_dir))
        docs = extractor.extract()

        assert docs.readme_content == "# My Collection"
        assert docs.changelog_content is None
        assert docs.license_content is None
