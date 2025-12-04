import pytest
from pathlib import Path
from ansibledoctor.parser.collection_parser import CollectionParser
from ansibledoctor.models.plugin import PluginType, Plugin

class TestDeepPluginParsing:
    def test_deep_parse_extracts_plugin_docs(self, tmp_path):
        """Test that deep_parse=True extracts plugin documentation."""
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text("namespace: my_namespace\nname: my_collection\nversion: 1.0.0")
        
        modules_dir = collection_dir / "plugins" / "modules"
        modules_dir.mkdir(parents=True)
        
        module_content = """
#!/usr/bin/python
DOCUMENTATION = r'''
---
module: my_module
short_description: Test module
description:
    - This is a test module.
options:
    name:
        description: Name option
        required: true
'''
EXAMPLES = r'''
- name: Example
  my_module:
    name: test
'''
RETURN = r'''
result:
    description: The result
    returned: always
'''
"""
        (modules_dir / "my_module.py").write_text(module_content)
        
        parser = CollectionParser()
        collection = parser.parse(collection_dir, deep_parse=True)
        
        # Verify plugin details
        plugins = collection.plugins[PluginType.MODULE]
        assert len(plugins) == 1
        plugin = plugins[0]
        
        # Expecting full Plugin object
        assert isinstance(plugin, Plugin)
        assert plugin.name == "my_module"
        assert plugin.short_description == "Test module"
        # assert plugin.documentation['description'] == ["This is a test module."]
        # assert "Example" in plugin.examples
        # assert "result" in plugin.return_values
