"""
Unit tests for Tag value object.

Tests the Tag model which represents an Ansible task tag with its metadata.
Following TDD Red-Green-Refactor cycle for Phase 8 US3.
"""

import pytest
from pydantic import ValidationError

from ansibledoctor.models.tag import Tag


class TestTagCreation:
    """Test Tag value object creation and validation."""

    def test_create_simple_tag(self):
        """Should create tag with just name."""
        tag = Tag(name="install")

        assert tag.name == "install"
        assert tag.description is None
        assert tag.usage_count == 1
        assert tag.file_locations == []

    def test_create_tag_with_description(self):
        """Should create tag with name and description."""
        tag = Tag(
            name="configure",
            description="Configures application settings",
        )

        assert tag.name == "configure"
        assert tag.description == "Configures application settings"
        assert tag.usage_count == 1

    def test_create_tag_with_usage_count(self):
        """Should create tag with specified usage count."""
        tag = Tag(
            name="deploy",
            description="Deploy application",
            usage_count=5,
        )

        assert tag.name == "deploy"
        assert tag.usage_count == 5

    def test_create_tag_with_file_locations(self):
        """Should create tag with file location references."""
        tag = Tag(
            name="security",
            file_locations=["tasks/main.yml:15", "tasks/hardening.yml:23"],
        )

        assert tag.name == "security"
        assert len(tag.file_locations) == 2
        assert "tasks/main.yml:15" in tag.file_locations

    def test_tag_name_required(self):
        """Should fail validation when name is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Tag()  # type: ignore

        assert "name" in str(exc_info.value)

    def test_tag_name_cannot_be_empty(self):
        """Should fail validation when name is empty string."""
        with pytest.raises(ValidationError) as exc_info:
            Tag(name="")

        assert "name" in str(exc_info.value)

    def test_tag_is_immutable(self):
        """Should prevent modification of tag after creation (frozen)."""
        tag = Tag(name="test")

        with pytest.raises(ValidationError):
            tag.name = "modified"  # type: ignore


class TestTagEquality:
    """Test Tag equality and hashing behavior."""

    def test_tags_with_same_name_are_equal(self):
        """Should consider tags equal if they have the same name."""
        tag1 = Tag(name="install")
        tag2 = Tag(name="install")

        assert tag1 == tag2

    def test_tags_with_different_names_are_not_equal(self):
        """Should consider tags unequal if names differ."""
        tag1 = Tag(name="install")
        tag2 = Tag(name="configure")

        assert tag1 != tag2

    def test_tags_are_hashable(self):
        """Should allow tags to be used in sets and as dict keys."""
        tag1 = Tag(name="install")
        tag2 = Tag(name="configure")
        tag3 = Tag(name="install")  # duplicate name

        tag_set = {tag1, tag2, tag3}

        # Should have only 2 unique tags (install counted once)
        assert len(tag_set) == 2


class TestTagSerialization:
    """Test Tag serialization to dict/JSON."""

    def test_tag_to_dict(self):
        """Should serialize tag to dictionary."""
        tag = Tag(
            name="backup",
            description="Backup data before changes",
            usage_count=3,
            file_locations=["tasks/backup.yml:10"],
        )

        result = tag.model_dump()

        assert result["name"] == "backup"
        assert result["description"] == "Backup data before changes"
        assert result["usage_count"] == 3
        assert result["file_locations"] == ["tasks/backup.yml:10"]

    def test_tag_to_json(self):
        """Should serialize tag to JSON string."""
        tag = Tag(name="test", description="Test tag")

        json_str = tag.model_dump_json()

        assert '"name":"test"' in json_str or '"name": "test"' in json_str
        assert "test tag" in json_str.lower()


class TestTagUsageTracking:
    """Test tag usage count and location tracking."""

    def test_increment_usage_count(self):
        """Should track multiple occurrences of same tag."""
        # This would be done by parser, but test the model accepts it
        tag = Tag(name="install", usage_count=5)

        assert tag.usage_count == 5

    def test_multiple_file_locations(self):
        """Should track tag appearances across multiple files."""
        locations = [
            "tasks/main.yml:10",
            "tasks/install.yml:5",
            "tasks/configure.yml:20",
        ]
        tag = Tag(name="install", file_locations=locations)

        assert len(tag.file_locations) == 3
        assert all(loc in tag.file_locations for loc in locations)

    def test_default_usage_count_is_one(self):
        """Should default to usage count of 1 when not specified."""
        tag = Tag(name="test")

        assert tag.usage_count == 1


class TestTagRepresentation:
    """Test Tag string representation."""

    def test_tag_repr(self):
        """Should provide useful string representation."""
        tag = Tag(name="install", description="Install packages")

        repr_str = repr(tag)

        assert "install" in repr_str
        assert "Tag" in repr_str

    def test_tag_str(self):
        """Should provide readable string format."""
        tag = Tag(name="configure")

        str_result = str(tag)

        assert "configure" in str_result
