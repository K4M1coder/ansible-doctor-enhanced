"""Unit tests for index filtering functionality."""

from pathlib import Path

from ansibledoctor.models.index import IndexFilter, IndexItem


class TestIndexFilters:
    """Test index filtering operations (Phase 8 US6)."""

    def test_tag_filtering(self):
        """T074: Test tag:database filter."""
        # Create items with different tags
        items = [
            IndexItem(
                name="db_role",
                type="role",
                path=Path("r1"),
                description="",
                tags=["database", "postgres"],
            ),
            IndexItem(
                name="web_role",
                type="role",
                path=Path("r2"),
                description="",
                tags=["web", "nginx"],
            ),
        ]

        # Apply tag filter
        filter_obj = IndexFilter.parse("tag:database")
        filtered = [item for item in items if filter_obj.matches(item)]

        # Verify only database role matches
        assert len(filtered) == 1
        assert filtered[0].name == "db_role"

    def test_namespace_filtering(self):
        """T075: Test namespace:my_namespace filter."""
        items = [
            IndexItem(
                name="role1",
                type="role",
                path=Path("r1"),
                description="",
                namespace="my_namespace",
            ),
            IndexItem(
                name="role2",
                type="role",
                path=Path("r2"),
                description="",
                namespace="other_namespace",
            ),
        ]

        # Apply namespace filter
        filter_obj = IndexFilter.parse("namespace:my_namespace")
        filtered = [item for item in items if filter_obj.matches(item)]

        # Verify only my_namespace matches
        assert len(filtered) == 1
        assert filtered[0].namespace == "my_namespace"

    def test_multiple_filters(self):
        """T076: Test multiple filters with AND logic."""
        items = [
            IndexItem(
                name="role1",
                type="role",
                path=Path("r1"),
                description="",
                tags=["web"],
                namespace="my_namespace",
            ),
            IndexItem(
                name="role2",
                type="role",
                path=Path("r2"),
                description="",
                tags=["web"],
                namespace="other_namespace",
            ),
            IndexItem(
                name="role3",
                type="role",
                path=Path("r3"),
                description="",
                tags=["database"],
                namespace="my_namespace",
            ),
        ]

        # Apply multiple filters (AND logic)
        filters = [
            IndexFilter.parse("tag:web"),
            IndexFilter.parse("namespace:my_namespace"),
        ]

        filtered = items
        for filter_obj in filters:
            filtered = [item for item in filtered if filter_obj.matches(item)]

        # Only role1 matches both filters
        assert len(filtered) == 1
        assert filtered[0].name == "role1"

    def test_type_filtering(self):
        """Test type filtering."""
        items = [
            IndexItem(name="r1", type="role", path=Path("r1"), description=""),
            IndexItem(name="c1", type="collection", path=Path("c1"), description=""),
        ]

        filter_obj = IndexFilter.parse("type:role")
        filtered = [item for item in items if filter_obj.matches(item)]

        assert len(filtered) == 1
        assert filtered[0].type == "role"

    def test_empty_filter_results(self):
        """T077: Test empty filter results."""
        items = [
            IndexItem(
                name="role1",
                type="role",
                path=Path("r1"),
                description="",
                tags=["web"],
            )
        ]

        # Filter that matches nothing
        filter_obj = IndexFilter.parse("tag:nonexistent")
        filtered = [item for item in items if filter_obj.matches(item)]

        # Should be empty
        assert len(filtered) == 0
