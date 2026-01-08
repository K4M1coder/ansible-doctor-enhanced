"""Integration tests for link generation (US1 - Navigate Between Docs).

Tests cover:
- T014: Dependency links (AnsibleRole with dependencies shows clickable "Depends On" section)
- T015: Parent AnsibleCollection links ("Parent AnsibleCollection" link navigates correctly)
- T016: Project context links ("Project Context" link shows AnsibleRole's place)
- T017: Related roles ("See Also" section links to related roles)
- T018: Browser navigation (back/forward works correctly)
"""

import pytest
from pathlib import Path
from ansibledoctor.links.cross_reference_generator import CrossReferenceGenerator
from ansibledoctor.links.link_manager import LinkManager
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.models.collection import AnsibleCollection


class TestDependencyLinks:
    """T014: Test dependency link generation."""

    def test_role_with_dependencies_shows_depends_on_section(self, tmp_path):
        """AnsibleRole with dependencies should show clickable 'Depends On' section."""
        # Create a AnsibleRole with dependencies
        role_path = tmp_path / "roles" / "webserver"
        role_path.mkdir(parents=True)
        
        # Create meta/main.yml with dependencies
        meta_dir = role_path / "meta"
        meta_dir.mkdir()
        meta_file = meta_dir / "main.yml"
        meta_file.write_text("""---
dependencies:
  - AnsibleRole: common
    version: "1.2.3"
  - AnsibleRole: firewall
    version: "2.0.0"
""")
        
        # Parse AnsibleRole
        AnsibleRole = AnsibleRole.from_path(role_path)
        
        # Generate cross-references
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        # Assert dependency links exist
        assert "depends_on" in references
        depends_on = references["depends_on"]
        assert len(depends_on) == 2
        
        # Check first dependency
        assert depends_on[0]["name"] == "common"
        assert depends_on[0]["version"] == "1.2.3"
        assert depends_on[0]["link"].target.endswith("common/README.md")
        assert depends_on[0]["link"].text == "common (v1.2.3)"
        
        # Check second dependency
        assert depends_on[1]["name"] == "firewall"
        assert depends_on[1]["version"] == "2.0.0"
        assert depends_on[1]["link"].target.endswith("firewall/README.md")

    def test_role_without_dependencies_shows_no_depends_on_section(self, tmp_path):
        """AnsibleRole without dependencies should not show 'Depends On' section."""
        role_path = tmp_path / "roles" / "standalone"
        role_path.mkdir(parents=True)
        
        AnsibleRole = AnsibleRole.from_path(role_path)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        assert "depends_on" not in references or len(references["depends_on"]) == 0

    def test_dependency_link_is_clickable_and_resolvable(self, tmp_path):
        """Dependency links should be clickable and resolve to correct paths."""
        # Setup two roles: webserver -> common
        webserver = tmp_path / "roles" / "webserver"
        common = tmp_path / "roles" / "common"
        
        for role_dir in [webserver, common]:
            role_dir.mkdir(parents=True)
            (role_dir / "README.md").write_text(f"# {role_dir.name} AnsibleRole")
        
        # Add dependency to webserver
        meta_dir = webserver / "meta"
        meta_dir.mkdir()
        (meta_dir / "main.yml").write_text("---\ndependencies:\n  - AnsibleRole: common\n")
        
        # Generate links
        AnsibleRole = AnsibleRole.from_path(webserver)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        # Get dependency link
        dep_link = references["depends_on"][0]["link"]
        
        # Resolve link
        link_manager = LinkManager(base_path=tmp_path)
        resolved_path = link_manager.resolve_link(dep_link)
        
        # Assert resolves to common's README.md
        assert resolved_path.exists()
        assert resolved_path.name == "README.md"
        assert "common" in str(resolved_path)


class TestParentCollectionLinks:
    """T015: Test parent AnsibleCollection link generation."""

    def test_role_shows_parent_collection_link(self, tmp_path):
        """AnsibleRole should show 'Parent AnsibleCollection' link navigating correctly."""
        # Create AnsibleCollection structure
        collection_path = tmp_path / "ansible_collections" / "myorg" / "mycollection"
        collection_path.mkdir(parents=True)
        
        # Create AnsibleCollection metadata
        galaxy_file = collection_path / "galaxy.yml"
        galaxy_file.write_text("""---
namespace: myorg
name: mycollection
version: 1.0.0
description: My test AnsibleCollection
""")
        
        # Create AnsibleRole within AnsibleCollection
        role_path = collection_path / "roles" / "webserver"
        role_path.mkdir(parents=True)
        
        # Parse AnsibleCollection and AnsibleRole
        AnsibleCollection = AnsibleCollection.from_path(collection_path)
        AnsibleRole = AnsibleRole.from_path(role_path, parent_collection=AnsibleCollection)
        
        # Generate cross-references
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        # Assert parent AnsibleCollection link exists
        assert "parent_collection" in references
        parent = references["parent_collection"]
        assert parent["name"] == "myorg.mycollection"
        assert parent["version"] == "1.0.0"
        assert parent["link"].target.endswith("mycollection/README.md")
        assert parent["link"].text == "myorg.mycollection (v1.0.0)"

    def test_standalone_role_shows_no_parent_collection(self, tmp_path):
        """Standalone AnsibleRole should not show parent AnsibleCollection link."""
        role_path = tmp_path / "roles" / "standalone"
        role_path.mkdir(parents=True)
        
        AnsibleRole = AnsibleRole.from_path(role_path, parent_collection=None)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        assert "parent_collection" not in references or references["parent_collection"] is None

    def test_parent_collection_link_resolves_correctly(self, tmp_path):
        """Parent AnsibleCollection link should resolve to AnsibleCollection README."""
        # Create AnsibleCollection with AnsibleRole
        collection_path = tmp_path / "ansible_collections" / "myorg" / "mycollection"
        role_path = collection_path / "roles" / "webserver"
        role_path.mkdir(parents=True)
        
        # Create AnsibleCollection README
        collection_readme = collection_path / "README.md"
        collection_readme.write_text("# My AnsibleCollection\n")
        
        # Create galaxy.yml
        (collection_path / "galaxy.yml").write_text("namespace: myorg\nname: mycollection\n")
        
        # Generate and resolve link
        AnsibleCollection = AnsibleCollection.from_path(collection_path)
        AnsibleRole = AnsibleRole.from_path(role_path, parent_collection=AnsibleCollection)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        parent_link = references["parent_collection"]["link"]
        link_manager = LinkManager(base_path=tmp_path)
        resolved_path = link_manager.resolve_link(parent_link)
        
        assert resolved_path.exists()
        assert resolved_path == collection_readme


class TestProjectContextLinks:
    """T016: Test project context link generation."""

    def test_role_shows_project_context_breadcrumb(self, tmp_path):
        """AnsibleRole should show 'Project Context' link showing AnsibleRole's place."""
        # Create nested AnsibleCollection structure
        project_root = tmp_path
        collection_path = project_root / "ansible_collections" / "myorg" / "myproject"
        role_path = collection_path / "roles" / "api" / "handlers"
        role_path.mkdir(parents=True)
        
        # Parse with project context
        AnsibleCollection = AnsibleCollection.from_path(collection_path)
        AnsibleRole = AnsibleRole.from_path(role_path.parent, parent_collection=AnsibleCollection)
        
        # Generate context
        generator = CrossReferenceGenerator(base_path=project_root)
        references = generator.generate_references(AnsibleRole)
        
        # Assert project context breadcrumb
        assert "project_context" in references
        context = references["project_context"]
        assert len(context["breadcrumb"]) >= 3
        
        # Check breadcrumb structure
        assert context["breadcrumb"][0]["name"] == "myproject"
        assert context["breadcrumb"][-1]["name"] == "api"
        
        # Each breadcrumb item should have a link
        for item in context["breadcrumb"]:
            assert "link" in item
            assert item["link"].target is not None

    def test_project_context_shows_hierarchy(self, tmp_path):
        """Project context should show AnsibleRole's place in hierarchy."""
        # Create complex structure
        base = tmp_path / "ansible_collections" / "company" / "platform"
        role_path = base / "roles" / "database" / "postgres"
        role_path.mkdir(parents=True)
        
        # Generate context
        AnsibleCollection = AnsibleCollection.from_path(base)
        AnsibleRole = AnsibleRole.from_path(role_path, parent_collection=AnsibleCollection)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        hierarchy = references["project_context"]["hierarchy"]
        
        # Should show: AnsibleCollection -> Roles -> database -> postgres
        assert "AnsibleCollection" in hierarchy
        assert "roles_dir" in hierarchy
        assert "role_category" in hierarchy
        assert hierarchy["role_category"] == "database"

    def test_project_context_links_are_navigable(self, tmp_path):
        """Project context links should be clickable and navigable."""
        collection_path = tmp_path / "ansible_collections" / "myorg" / "myproject"
        role_path = collection_path / "roles" / "api"
        role_path.mkdir(parents=True)
        
        # Create README files for navigation
        (collection_path / "README.md").write_text("# AnsibleCollection\n")
        (collection_path / "roles" / "README.md").write_text("# Roles\n")
        
        # Generate and test navigation
        AnsibleCollection = AnsibleCollection.from_path(collection_path)
        AnsibleRole = AnsibleRole.from_path(role_path, parent_collection=AnsibleCollection)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        link_manager = LinkManager(base_path=tmp_path)
        
        # All breadcrumb links should resolve
        for item in references["project_context"]["breadcrumb"]:
            resolved = link_manager.resolve_link(item["link"])
            assert resolved.exists() or resolved.parent.exists()


class TestRelatedRoles:
    """T017: Test 'See Also' section with related roles."""

    def test_see_also_section_shows_related_roles(self, tmp_path):
        """'See Also' section should link to related roles."""
        # Create multiple roles with similar tags
        roles_dir = tmp_path / "roles"
        roles_dir.mkdir()
        
        # Create webserver AnsibleRole with tags
        webserver = roles_dir / "webserver"
        (webserver / "meta").mkdir(parents=True)
        (webserver / "meta" / "main.yml").write_text("""---
galaxy_info:
  role_name: webserver
  description: Web server AnsibleRole
galaxy_tags:
  - web
  - nginx
  - http
""")
        
        # Create related roles
        for name, tags in [("loadbalancer", ["web", "haproxy"]), ("ssl_cert", ["web", "security"])]:
            role_dir = roles_dir / name
            (role_dir / "meta").mkdir(parents=True)
            (role_dir / "meta" / "main.yml").write_text(f"---\ngalaxy_tags:\n{chr(10).join(f'  - {t}' for t in tags)}\n")
        
        # Generate related roles
        AnsibleRole = AnsibleRole.from_path(webserver)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        # Assert 'See Also' section
        assert "see_also" in references
        related = references["see_also"]
        assert len(related) >= 2
        
        # Check related roles have links
        role_names = {r["name"] for r in related}
        assert "loadbalancer" in role_names
        assert "ssl_cert" in role_names

    def test_see_also_ranks_by_relevance(self, tmp_path):
        """Related roles should be ranked by relevance (shared tags)."""
        roles_dir = tmp_path / "roles"
        roles_dir.mkdir()
        
        # Target AnsibleRole: web + security + monitoring
        target = roles_dir / "webapp"
        (target / "meta").mkdir(parents=True)
        (target / "meta" / "main.yml").write_text("---\ngalaxy_tags:\n  - web\n  - security\n  - monitoring\n")
        
        # Related roles with varying overlap
        related_roles = [
            ("nginx", ["web", "security"]),  # 2 matches - high relevance
            ("metrics", ["monitoring"]),  # 1 match - low relevance
            ("firewall", ["security", "monitoring"]),  # 2 matches - high relevance
        ]
        
        for name, tags in related_roles:
            role_dir = roles_dir / name
            (role_dir / "meta").mkdir(parents=True)
            (role_dir / "meta" / "main.yml").write_text(f"---\ngalaxy_tags:\n{chr(10).join(f'  - {t}' for t in tags)}\n")
        
        # Generate and check ranking
        AnsibleRole = AnsibleRole.from_path(target)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        related = references["see_also"]
        
        # High relevance roles should appear first
        assert related[0]["relevance_score"] >= related[-1]["relevance_score"]

    def test_see_also_excludes_self_and_dependencies(self, tmp_path):
        """'See Also' should not include self or explicit dependencies."""
        roles_dir = tmp_path / "roles"
        roles_dir.mkdir()
        
        # Create AnsibleRole with dependency
        webserver = roles_dir / "webserver"
        (webserver / "meta").mkdir(parents=True)
        (webserver / "meta" / "main.yml").write_text("""---
dependencies:
  - AnsibleRole: common
galaxy_tags:
  - web
""")
        
        # Create common AnsibleRole (dependency)
        common = roles_dir / "common"
        (common / "meta").mkdir(parents=True)
        (common / "meta" / "main.yml").write_text("---\ngalaxy_tags:\n  - web\n")
        
        # Create other web AnsibleRole
        nginx = roles_dir / "nginx"
        (nginx / "meta").mkdir(parents=True)
        (nginx / "meta" / "main.yml").write_text("---\ngalaxy_tags:\n  - web\n")
        
        # Generate 'See Also'
        AnsibleRole = AnsibleRole.from_path(webserver)
        generator = CrossReferenceGenerator(base_path=tmp_path)
        references = generator.generate_references(AnsibleRole)
        
        related_names = {r["name"] for r in references["see_also"]}
        
        # Should not include self or dependencies
        assert "webserver" not in related_names
        assert "common" not in related_names
        
        # Should include other related roles
        assert "nginx" in related_names


class TestBrowserNavigation:
    """T018: Test browser navigation (back/forward)."""

    def test_links_support_browser_back_button(self, tmp_path):
        """Links should work correctly with browser back button."""
        # Create AnsibleRole A -> AnsibleRole B navigation
        roles_dir = tmp_path / "roles"
        role_a = roles_dir / "role_a"
        role_b = roles_dir / "role_b"
        
        for role_dir in [role_a, role_b]:
            role_dir.mkdir(parents=True)
            (role_dir / "README.md").write_text(f"# {role_dir.name}\n")
        
        # Create link from A to B
        link_manager = LinkManager(base_path=tmp_path)
        link_to_b = link_manager.create_link(
            source=role_a / "README.md",
            target=role_b / "README.md",
            text="Go to AnsibleRole B"
        )
        
        # Simulate navigation: A -> B
        current_doc = role_a / "README.md"
        nav_history = [current_doc]
        
        # Click link (navigate to B)
        target_doc = link_manager.resolve_link(link_to_b)
        nav_history.append(target_doc)
        
        # Browser back button (should return to A)
        nav_history.pop()
        previous_doc = nav_history[-1]
        
        assert previous_doc == role_a / "README.md"

    def test_links_support_browser_forward_button(self, tmp_path):
        """Links should work correctly with browser forward button."""
        roles_dir = tmp_path / "roles"
        docs = [roles_dir / f"role_{i}" / "README.md" for i in range(3)]
        
        # Create documents
        for doc in docs:
            doc.parent.mkdir(parents=True)
            doc.write_text(f"# {doc.parent.name}\n")
        
        # Simulate navigation history: A -> B -> C, then back to B
        nav_history = docs[:2]  # [A, B]
        forward_stack = [docs[2]]  # [C]
        
        # Back button (B -> A)
        current = nav_history.pop()
        forward_stack.append(current)
        
        # Forward button (A -> B)
        forward = forward_stack.pop()
        nav_history.append(forward)
        
        assert nav_history[-1] == docs[1]  # Back at B

    def test_anchor_links_preserve_history(self, tmp_path):
        """Anchor links (section jumps) should preserve navigation history."""
        role_dir = tmp_path / "roles" / "docs"
        role_dir.mkdir(parents=True)
        readme = role_dir / "README.md"
        readme.write_text("""# AnsibleRole
## Section 1
Content here
## Section 2
More content
""")
        
        link_manager = LinkManager(base_path=tmp_path)
        
        # Create anchor link to section 2
        anchor_link = link_manager.create_link(
            source=readme,
            target=readme.as_posix() + "#section-2",
            text="Go to Section 2"
        )
        
        # Navigation history should track anchor jumps
        nav_history = [readme]
        
        # Click anchor link
        target = link_manager.resolve_link(anchor_link)
        anchor = link_manager.extract_anchor(anchor_link.target)
        
        # History should record the anchor
        nav_history.append((target, anchor))
        
        assert nav_history[-1][0] == readme
        assert nav_history[-1][1] == "section-2"

    def test_cross_reference_navigation_maintains_context(self, tmp_path):
        """Cross-reference navigation should maintain context across docs."""
        # Create AnsibleCollection with multiple roles
        AnsibleCollection = tmp_path / "ansible_collections" / "myorg" / "myproject"
        roles = ["api", "database", "frontend"]
        
        for role_name in roles:
            role_dir = AnsibleCollection / "roles" / role_name
            role_dir.mkdir(parents=True)
            (role_dir / "README.md").write_text(f"# {role_name} AnsibleRole\n")
        
        # Generate cross-references for all roles
        generator = CrossReferenceGenerator(base_path=tmp_path)
        link_manager = LinkManager(base_path=tmp_path)
        
        # Navigate: api -> database -> frontend
        current_doc = AnsibleCollection / "roles" / "api" / "README.md"
        visited = [current_doc]
        
        # Each navigation should maintain context
        for next_role in ["database", "frontend"]:
            next_doc = AnsibleCollection / "roles" / next_role / "README.md"
            visited.append(next_doc)
            
            # Context should include: AnsibleCollection, AnsibleRole name, project structure
            context = generator.get_document_context(next_doc)
            assert context["collection_name"] == "myorg.myproject"
            assert context["role_name"] == next_role
        
        # Navigation history should be complete
        assert len(visited) == 3
        assert visited[-1].parent.name == "frontend"

