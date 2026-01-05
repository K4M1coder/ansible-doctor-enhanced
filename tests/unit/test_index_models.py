"""Unit tests for index models (IndexItem, IndexPage, SectionIndex)."""

from pathlib import Path

import pytest

from ansibledoctor.models.index import IndexFilter, IndexItem, IndexPage, SectionIndex


class TestIndexItem:
    """Tests for IndexItem model."""

    def test_create_basic_item(self):
        """Test creating a basic index item."""
        item = IndexItem(
            name="webserver",
            type="role",
            description="Configure web servers",
            path=Path("roles/webserver"),
            doc_link="./roles/webserver.md",
            tags=["web", "nginx"],
            namespace="my_namespace",
        )

        assert item.name == "webserver"
        assert item.type == "role"
        assert item.description == "Configure web servers"
        assert item.tags == ["web", "nginx"]
        assert item.namespace == "my_namespace"

    def test_depth_calculation_no_children(self):
        """Test depth calculation for item with no children."""
        item = IndexItem(
            name="role1",
            type="role",
            path=Path("roles/role1"),
        )

        assert item.depth == 0

    def test_depth_calculation_with_children(self):
        """Test depth calculation for item with children."""
        child1 = IndexItem(name="child1", type="role", path=Path("child1"))
        child2 = IndexItem(name="child2", type="role", path=Path("child2"))
        grandchild = IndexItem(name="grandchild", type="plugin", path=Path("gc"))

        child1.children = [grandchild]

        parent = IndexItem(
            name="parent",
            type="collection",
            path=Path("collections/parent"),
            children=[child1, child2],
        )

        assert parent.depth == 2  # parent -> child1 -> grandchild
        assert child1.depth == 1
        assert child2.depth == 0

    def test_total_descendants_empty(self):
        """Test total_descendants for item with no children."""
        item = IndexItem(name="item", type="role", path=Path("item"))
        assert item.total_descendants == 0

    def test_total_descendants_with_children(self):
        """Test total_descendants calculation."""
        child1 = IndexItem(name="child1", type="role", path=Path("c1"))
        child2 = IndexItem(name="child2", type="role", path=Path("c2"))
        grandchild1 = IndexItem(name="gc1", type="plugin", path=Path("gc1"))
        grandchild2 = IndexItem(name="gc2", type="plugin", path=Path("gc2"))

        child1.children = [grandchild1, grandchild2]

        parent = IndexItem(
            name="parent",
            type="collection",
            path=Path("parent"),
            children=[child1, child2],
        )

        # parent has 2 children + 2 grandchildren = 4 descendants
        assert parent.total_descendants == 4
        assert child1.total_descendants == 2
        assert child2.total_descendants == 0

    def test_find_child_found(self):
        """Test finding a direct child by name."""
        child1 = IndexItem(name="child1", type="role", path=Path("c1"))
        child2 = IndexItem(name="child2", type="role", path=Path("c2"))

        parent = IndexItem(
            name="parent",
            type="collection",
            path=Path("parent"),
            children=[child1, child2],
        )

        found = parent.find_child("child2")
        assert found is not None
        assert found.name == "child2"

    def test_find_child_not_found(self):
        """Test finding non-existent child returns None."""
        child1 = IndexItem(name="child1", type="role", path=Path("c1"))

        parent = IndexItem(
            name="parent",
            type="collection",
            path=Path("parent"),
            children=[child1],
        )

        found = parent.find_child("nonexistent")
        assert found is None

    def test_find_descendant_self(self):
        """Test find_descendant returns self if name matches."""
        item = IndexItem(name="target", type="role", path=Path("target"))
        found = item.find_descendant("target")
        assert found is item

    def test_find_descendant_in_children(self):
        """Test finding descendant at any level."""
        grandchild = IndexItem(name="grandchild", type="plugin", path=Path("gc"))
        child = IndexItem(
            name="child",
            type="role",
            path=Path("child"),
            children=[grandchild],
        )
        parent = IndexItem(
            name="parent",
            type="collection",
            path=Path("parent"),
            children=[child],
        )

        found = parent.find_descendant("grandchild")
        assert found is not None
        assert found.name == "grandchild"

    def test_find_descendant_not_found(self):
        """Test find_descendant returns None if not found."""
        child = IndexItem(name="child", type="role", path=Path("child"))
        parent = IndexItem(
            name="parent",
            type="collection",
            path=Path("parent"),
            children=[child],
        )

        found = parent.find_descendant("nonexistent")
        assert found is None


class TestIndexPage:
    """Tests for IndexPage model."""

    def test_create_basic_page(self):
        """Test creating a basic index page."""
        items = [
            IndexItem(name="role1", type="role", path=Path("r1")),
            IndexItem(name="role2", type="role", path=Path("r2")),
        ]

        page = IndexPage(
            title="Role Index",
            component_type="roles",
            items=items,
            format="list",
            total_count=2,
        )

        assert page.title == "Role Index"
        assert len(page.items) == 2
        assert page.total_pages == 1

    def test_has_pagination_single_page(self):
        """Test has_pagination returns False for single page."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=0,
            page_number=1,
            total_pages=1,
        )

        assert page.has_pagination is False

    def test_has_pagination_multiple_pages(self):
        """Test has_pagination returns True for multiple pages."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=1,
            total_pages=3,
        )

        assert page.has_pagination is True

    def test_has_previous_first_page(self):
        """Test has_previous returns False for first page."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=1,
            total_pages=3,
        )

        assert page.has_previous is False

    def test_has_previous_middle_page(self):
        """Test has_previous returns True for middle page."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=2,
            total_pages=3,
        )

        assert page.has_previous is True

    def test_has_next_last_page(self):
        """Test has_next returns False for last page."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=3,
            total_pages=3,
        )

        assert page.has_next is False

    def test_has_next_first_page(self):
        """Test has_next returns True for first page with more pages."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=1,
            total_pages=3,
        )

        assert page.has_next is True

    def test_previous_page_link_none_for_first(self):
        """Test previous_page_link returns None for first page."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=1,
            total_pages=3,
        )

        assert page.previous_page_link is None

    def test_previous_page_link_to_index(self):
        """Test previous_page_link returns ./index.md for page 2."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=2,
            total_pages=3,
        )

        assert page.previous_page_link == "./index.md"

    def test_previous_page_link_numbered(self):
        """Test previous_page_link returns numbered link for page 3+."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=3,
            total_pages=3,
        )

        assert page.previous_page_link == "./index-2.md"

    def test_next_page_link_none_for_last(self):
        """Test next_page_link returns None for last page."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=3,
            total_pages=3,
        )

        assert page.next_page_link is None

    def test_next_page_link_numbered(self):
        """Test next_page_link returns numbered link."""
        page = IndexPage(
            title="Test",
            component_type="roles",
            items=[],
            total_count=100,
            page_number=1,
            total_pages=3,
        )

        assert page.next_page_link == "./index-2.md"


class TestSectionIndex:
    """Tests for SectionIndex model."""

    def test_create_basic_section(self):
        """Test creating a basic section index."""
        items = [
            IndexItem(name="role1", type="role", path=Path("r1")),
            IndexItem(name="role2", type="role", path=Path("r2")),
        ]

        section = SectionIndex(
            component_type="roles",
            items=items,
            format="list",
        )

        assert section.component_type == "roles"
        assert len(section.items) == 2
        assert section.limit is None

    def test_is_limited_false_no_limit(self):
        """Test is_limited returns False when no limit set."""
        items = [
            IndexItem(name="role1", type="role", path=Path("r1")),
            IndexItem(name="role2", type="role", path=Path("r2")),
        ]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=None,
        )

        assert section.is_limited is False

    def test_is_limited_false_items_under_limit(self):
        """Test is_limited returns False when items under limit."""
        items = [
            IndexItem(name="role1", type="role", path=Path("r1")),
            IndexItem(name="role2", type="role", path=Path("r2")),
        ]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=5,
        )

        assert section.is_limited is False

    def test_is_limited_true_items_over_limit(self):
        """Test is_limited returns True when items exceed limit."""
        items = [IndexItem(name=f"role{i}", type="role", path=Path(f"r{i}")) for i in range(10)]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=5,
        )

        assert section.is_limited is True

    def test_visible_items_no_limit(self):
        """Test visible_items returns all items when no limit."""
        items = [
            IndexItem(name="role1", type="role", path=Path("r1")),
            IndexItem(name="role2", type="role", path=Path("r2")),
            IndexItem(name="role3", type="role", path=Path("r3")),
        ]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=None,
        )

        assert len(section.visible_items) == 3

    def test_visible_items_with_limit(self):
        """Test visible_items respects limit."""
        items = [IndexItem(name=f"role{i}", type="role", path=Path(f"r{i}")) for i in range(10)]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=5,
        )

        assert len(section.visible_items) == 5
        assert section.visible_items[0].name == "role0"
        assert section.visible_items[4].name == "role4"

    def test_hidden_count_no_limit(self):
        """Test hidden_count returns 0 when no limit."""
        items = [
            IndexItem(name="role1", type="role", path=Path("r1")),
            IndexItem(name="role2", type="role", path=Path("r2")),
        ]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=None,
        )

        assert section.hidden_count == 0

    def test_hidden_count_with_limit(self):
        """Test hidden_count calculates correctly."""
        items = [IndexItem(name=f"role{i}", type="role", path=Path(f"r{i}")) for i in range(10)]

        section = SectionIndex(
            component_type="roles",
            items=items,
            limit=5,
        )

        assert section.hidden_count == 5


class TestIndexFilter:
    """Tests for IndexFilter model."""

    def test_parse_tag_filter(self):
        """Test parsing tag filter."""
        filter_obj = IndexFilter.parse("tag:database")

        assert filter_obj.field == "tag"
        assert filter_obj.value == "database"
        assert filter_obj.operator == "equals"

    def test_parse_namespace_filter(self):
        """Test parsing namespace filter."""
        filter_obj = IndexFilter.parse("namespace:my_namespace")

        assert filter_obj.field == "namespace"
        assert filter_obj.value == "my_namespace"

    def test_parse_invalid_format(self):
        """Test parsing invalid filter format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid filter format"):
            IndexFilter.parse("invalid")

    def test_matches_tag_equals(self):
        """Test matching item by tag with equals operator."""
        item = IndexItem(
            name="role1",
            type="role",
            path=Path("r1"),
            tags=["database", "postgres"],
        )

        filter_obj = IndexFilter(field="tag", operator="equals", value="database")
        assert filter_obj.matches(item) is True

        filter_obj2 = IndexFilter(field="tag", operator="equals", value="web")
        assert filter_obj2.matches(item) is False

    def test_matches_namespace_equals(self):
        """Test matching item by namespace."""
        item = IndexItem(
            name="role1",
            type="role",
            path=Path("r1"),
            namespace="my_namespace",
        )

        filter_obj = IndexFilter(field="namespace", operator="equals", value="my_namespace")
        assert filter_obj.matches(item) is True

        filter_obj2 = IndexFilter(field="namespace", operator="equals", value="other_ns")
        assert filter_obj2.matches(item) is False

    def test_matches_type_equals(self):
        """Test matching item by type."""
        item = IndexItem(name="role1", type="role", path=Path("r1"))

        filter_obj = IndexFilter(field="type", operator="equals", value="role")
        assert filter_obj.matches(item) is True

        filter_obj2 = IndexFilter(field="type", operator="equals", value="collection")
        assert filter_obj2.matches(item) is False

    def test_matches_contains_operator(self):
        """Test matching with contains operator."""
        item = IndexItem(
            name="role1",
            type="role",
            path=Path("r1"),
            tags=["webserver", "nginx"],
        )

        filter_obj = IndexFilter(field="tag", operator="contains", value="web")
        assert filter_obj.matches(item) is True

        filter_obj2 = IndexFilter(field="tag", operator="contains", value="database")
        assert filter_obj2.matches(item) is False

    def test_matches_startswith_operator(self):
        """Test matching with startswith operator."""
        item = IndexItem(
            name="role1",
            type="role",
            path=Path("r1"),
            namespace="my_namespace",
        )

        filter_obj = IndexFilter(field="namespace", operator="startswith", value="my_")
        assert filter_obj.matches(item) is True

        filter_obj2 = IndexFilter(field="namespace", operator="startswith", value="other_")
        assert filter_obj2.matches(item) is False

    def test_matches_metadata_field(self):
        """Test matching custom metadata field."""
        item = IndexItem(
            name="role1",
            type="role",
            path=Path("r1"),
            metadata={"status": "stable", "maintainer": "team"},
        )

        filter_obj = IndexFilter(field="status", operator="equals", value="stable")
        assert filter_obj.matches(item) is True

        filter_obj2 = IndexFilter(field="status", operator="equals", value="beta")
        assert filter_obj2.matches(item) is False

    def test_matches_nonexistent_field(self):
        """Test matching nonexistent field returns False."""
        item = IndexItem(name="role1", type="role", path=Path("r1"))

        filter_obj = IndexFilter(field="nonexistent", operator="equals", value="value")
        assert filter_obj.matches(item) is False
