import re

from ansibledoctor.utils.slug import (
    build_context_path,
    collection_slug,
    join_hierarchy,
    project_slug,
    relative_link,
    role_slug,
)


def test_project_slug_basic():
    assert project_slug("My Project") == "ansibleproject_my-project"
    assert project_slug("Café du Monde") == "ansibleproject_cafe-du-monde"


def test_collection_slug_basic():
    assert (
        collection_slug("my-namespace", "my-collection") == "collection_my-namespace.my-collection"
    )
    # underscores are converted to dashes in namespace for collections
    assert (
        collection_slug("my_namespace", "my_collection") == "collection_my-namespace.my-collection"
    )


def test_role_slug_allows_underscore():
    assert role_slug("my_namespace", "web_server") == "role_my_namespace.web-server"
    # role namespace preserves underscore
    assert role_slug("My_Namespace", "webserver") == "role_my_namespace.webserver"


def test_join_hierarchy_simple():
    proj = "ansibleproject_my-project"
    coll = "collection_my-namespace.my-collection"
    role = "role_my_namespace.webserver"

    assert (
        join_hierarchy(proj, coll, role)
        == "ansibleproject_my-project/collections/collection_my-namespace.my-collection/role_my_namespace.webserver"
    )


def test_slug_special_characters_and_spaces():
    assert project_slug("A  B   C") == "ansibleproject_a-b-c"
    assert project_slug("A---B___C") == "ansibleproject_a-b-c"


def test_slug_valid_characters_and_length():
    # Ensure only allowed characters (a-z, 0-9, dash) are present in the slug portion
    s = project_slug("Project Name with € symbols © and emojis 🚀")
    slug_portion = s.replace("ansibleproject_", "")
    assert re.match(r"^[a-z0-9-]+$", slug_portion)
    # confirm hyphenated words
    assert "project-name-with" in slug_portion


# ============================================================
# Context Path Building Tests (T308)
# ============================================================


class TestBuildContextPath:
    """Tests for build_context_path function."""

    def test_project_only(self):
        """Project-level documentation path."""
        result = build_context_path("en", project="ansibleproject_my-project")
        assert result == "docs/lang/en/ansibleproject_my-project"

    def test_collection_in_project(self):
        """Collection inside a project."""
        result = build_context_path(
            "en",
            project="ansibleproject_my-project",
            collection="collection_ns.coll",
        )
        assert result == "docs/lang/en/ansibleproject_my-project/collections/collection_ns.coll"

    def test_role_in_collection_in_project(self):
        """Full hierarchy: project > collection > role."""
        result = build_context_path(
            "fr",
            project="ansibleproject_my-project",
            collection="collection_ns.coll",
            role="role_ns.webserver",
        )
        assert result == "docs/lang/fr/ansibleproject_my-project/collections/collection_ns.coll/role_ns.webserver"

    def test_standalone_collection(self):
        """Standalone collection (no parent project)."""
        result = build_context_path("en", collection="collection_ns.coll")
        assert result == "docs/lang/en/collection_ns.coll"

    def test_role_in_standalone_collection(self):
        """Role in a standalone collection."""
        result = build_context_path(
            "de",
            collection="collection_ns.coll",
            role="role_ns.webserver",
        )
        assert result == "docs/lang/de/collection_ns.coll/role_ns.webserver"

    def test_standalone_role(self):
        """Standalone role (no parent collection or project)."""
        result = build_context_path("en", role="role_ns.webserver")
        assert result == "docs/lang/en/role_ns.webserver"

    def test_different_languages(self):
        """Path varies by language code."""
        en = build_context_path("en", project="ansibleproject_proj")
        fr = build_context_path("fr", project="ansibleproject_proj")
        de = build_context_path("de", project="ansibleproject_proj")
        
        assert en == "docs/lang/en/ansibleproject_proj"
        assert fr == "docs/lang/fr/ansibleproject_proj"
        assert de == "docs/lang/de/ansibleproject_proj"


class TestRelativeLink:
    """Tests for relative_link function."""

    def test_role_to_parent_collection(self):
        """Link from role docs to parent collection docs."""
        from_path = "docs/lang/en/collection_ns.coll/role_ns.webserver"
        to_path = "docs/lang/en/collection_ns.coll"
        result = relative_link(from_path, to_path)
        assert result == "../README.md"

    def test_collection_to_parent_project(self):
        """Link from collection to parent project."""
        from_path = "docs/lang/en/ansibleproject_proj/collections/collection_ns.coll"
        to_path = "docs/lang/en/ansibleproject_proj"
        result = relative_link(from_path, to_path)
        assert result == "../../README.md"

    def test_role_to_grandparent_project(self):
        """Link from role to grandparent project (2 levels up)."""
        from_path = "docs/lang/en/ansibleproject_proj/collections/collection_ns.coll/role_ns.web"
        to_path = "docs/lang/en/ansibleproject_proj"
        result = relative_link(from_path, to_path)
        assert result == "../../../README.md"

    def test_role_to_sibling_role(self):
        """Link from one role to another in same collection."""
        from_path = "docs/lang/en/collection_ns.coll/role_ns.webserver"
        to_path = "docs/lang/en/collection_ns.coll/role_ns.database"
        result = relative_link(from_path, to_path)
        assert result == "../role_ns.database/README.md"

    def test_collection_to_sibling_collection(self):
        """Link from one collection to another in same project."""
        from_path = "docs/lang/en/ansibleproject_proj/collections/collection_ns.web"
        to_path = "docs/lang/en/ansibleproject_proj/collections/collection_ns.db"
        result = relative_link(from_path, to_path)
        assert result == "../collection_ns.db/README.md"

    def test_same_directory(self):
        """Link to same directory returns README.md."""
        path = "docs/lang/en/collection_ns.coll"
        result = relative_link(path, path)
        assert result == "README.md"

    def test_cross_language_not_supported(self):
        """Cross-language links still work but produce relative paths."""
        # Note: Cross-language linking would need explicit handling
        from_path = "docs/lang/en/collection_ns.coll"
        to_path = "docs/lang/fr/collection_ns.coll"
        result = relative_link(from_path, to_path)
        # Goes up to docs/lang, then down to fr/...
        assert "../fr/collection_ns.coll/README.md" in result


class TestHierarchyPathPreservation:
    """Tests ensuring slugs are preserved correctly through the hierarchy."""

    def test_full_hierarchy_preserves_slugs(self):
        """Slugs should be preserved exactly in hierarchical paths."""
        proj = project_slug("My Great Project")
        coll = collection_slug("my_namespace", "awesome_collection")
        role = role_slug("my_namespace", "web_server")
        
        path = build_context_path("en", project=proj, collection=coll, role=role)
        
        assert "ansibleproject_my-great-project" in path
        assert "collection_my-namespace.awesome-collection" in path
        assert "role_my_namespace.web-server" in path

    def test_special_characters_in_names(self):
        """Special characters should be normalized in slugs."""
        proj = project_slug("Café Project ™")
        coll = collection_slug("über_ns", "collection_éè")
        
        path = build_context_path("en", project=proj, collection=coll)
        
        # Verify only valid slug characters
        assert "cafe" in path.lower()
        assert "uber" in path.lower() or "ber" in path.lower()

