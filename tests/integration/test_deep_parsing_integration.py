"""Integration tests for deep parsing of collections."""

from ansibledoctor.models.plugin import Plugin, PluginType
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.parser.collection_parser import CollectionParser


class TestDeepParsingIntegration:
    """Integration tests for deep parsing functionality."""

    def test_deep_parsing_full_collection(self, tmp_path):
        """
        Test that deep_parse=True correctly parses a full collection structure
        including roles (with tasks) and plugins (with documentation).
        """
        # Setup collection structure
        collection_dir = tmp_path / "test_ns" / "test_coll"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: test_ns\nname: test_coll\nversion: 1.0.0"
        )

        # Setup Role
        role_dir = collection_dir / "roles" / "my_role"
        (role_dir / "tasks").mkdir(parents=True)
        (role_dir / "tasks" / "main.yml").write_text(
            "- name: Task 1\n  debug: msg='hello'\n  tags: [my_tag]"
        )
        (role_dir / "meta").mkdir(parents=True)
        (role_dir / "meta" / "main.yml").write_text("galaxy_info:\n  author: me")

        # Setup Plugin
        plugin_dir = collection_dir / "plugins" / "modules"
        plugin_dir.mkdir(parents=True)
        plugin_content = """
DOCUMENTATION = r'''
module: my_module
short_description: My Module
'''
"""
        (plugin_dir / "my_module.py").write_text(plugin_content)

        # Parse
        parser = CollectionParser()
        collection = parser.parse(collection_dir, deep_parse=True)

        # Verify Role
        assert len(collection.roles) == 1
        role = collection.roles[0]
        assert isinstance(role, AnsibleRole)
        assert role.name == "my_role"

        # Verify metadata
        assert role.metadata.author == "me"

        # Verify tags
        assert len(role.tags) == 1
        assert role.tags[0].name == "my_tag"

        # Verify Plugin
        assert PluginType.MODULE in collection.plugins
        plugin = collection.plugins[PluginType.MODULE][0]
        assert isinstance(plugin, Plugin)
        assert plugin.name == "my_module"
        assert plugin.short_description == "My Module"
