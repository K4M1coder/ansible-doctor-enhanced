import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import ast
import yaml

from ansibledoctor.parser.plugin_parser import PluginParser
from ansibledoctor.models.plugin import Plugin, PluginType
from ansibledoctor.parser.collection_parser import CollectionParser
from ansibledoctor.exceptions import ParsingError

class TestPluginParserCoverage:
    def test_parse_non_existent_file(self):
        """Test parsing a plugin file that does not exist."""
        parser = PluginParser()
        plugin = Plugin(
            name="test_plugin",
            type=PluginType.MODULE,
            path=Path("/non/existent/path.py")
        )
        
        result = parser.parse(plugin)
        assert result == plugin
        assert result.documentation == {}

    def test_parse_syntax_error(self, tmp_path):
        """Test parsing a plugin file with Python syntax errors."""
        plugin_path = tmp_path / "syntax_error.py"
        plugin_path.write_text("This is not valid python code", encoding="utf-8")
        
        parser = PluginParser()
        plugin = Plugin(
            name="syntax_error",
            type=PluginType.MODULE,
            path=plugin_path
        )
        
        # Should log error and return original plugin
        result = parser.parse(plugin)
        assert result == plugin

    def test_parse_invalid_yaml_documentation(self, tmp_path):
        """Test parsing a plugin with invalid YAML in DOCUMENTATION block."""
        plugin_path = tmp_path / "invalid_yaml.py"
        content = '''
DOCUMENTATION = r"""
module: invalid_yaml
short_description: Test module
options:
  - invalid: [ unclosed list
"""
'''
        plugin_path.write_text(content, encoding="utf-8")
        
        parser = PluginParser()
        plugin = Plugin(
            name="invalid_yaml",
            type=PluginType.MODULE,
            path=plugin_path
        )
        
        result = parser.parse(plugin)
        # Should not crash, but documentation should be empty
        assert result.documentation == {}

    def test_parse_legacy_string_node(self, tmp_path):
        """Test parsing with ast.Str node (simulated for coverage)."""
        parser = PluginParser()
        
        # Create a dummy class for Legacy Str
        class LegacyStr:
            s = "test string"
            
        node = LegacyStr()
        
        # Patch ast.Constant to be something unrelated
        # Patch ast.Str to be LegacyStr
        with patch("ansibledoctor.parser.plugin_parser.ast.Constant", type("DummyConstant", (), {})), \
             patch("ansibledoctor.parser.plugin_parser.ast.Str", LegacyStr):
            result = parser._extract_string_value(node)
        
        assert result == "test string"

class TestCollectionParserCoverage:
    @pytest.fixture
    def parser(self):
        return CollectionParser()

    @pytest.fixture
    def mock_collection_path(self, tmp_path):
        collection_dir = tmp_path / "test_ns" / "test_coll"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text("namespace: test_ns\nname: test_coll\nversion: 1.0.0\nauthors: [me]", encoding="utf-8")
        (collection_dir / "roles").mkdir()
        (collection_dir / "plugins").mkdir()
        return collection_dir

    def test_deep_parse_role_failure(self, parser, mock_collection_path):
        """Test that role parsing failure is handled gracefully in deep mode."""
        role_dir = mock_collection_path / "roles" / "broken_role"
        role_dir.mkdir()
        
        with patch("ansibledoctor.parser.collection_parser.RoleParser") as MockRoleParser:
            mock_instance = MockRoleParser.return_value
            mock_instance.parse.side_effect = Exception("Role parsing failed")
            
            collection = parser.parse(mock_collection_path, deep_parse=True)
            
            # Should fall back to string name
            assert "broken_role" in collection.roles
            assert len(collection.roles) == 1

    def test_unexpected_error_during_parse(self, parser, mock_collection_path):
        """Test handling of unexpected exceptions during parsing."""
        # Mock the instance method directly since parser is already initialized
        parser._galaxy_parser.parse = Mock(side_effect=Exception("Unexpected crash"))
        
        with pytest.raises(ParsingError) as excinfo:
            parser.parse(mock_collection_path)
        
        assert "Failed to parse collection" in str(excinfo.value)
        assert "Unexpected crash" in str(excinfo.value)

    def test_discover_playbooks_exception(self, parser, mock_collection_path):
        """Test exception handling during playbook discovery."""
        playbooks_dir = mock_collection_path / "playbooks"
        playbooks_dir.mkdir()
        bad_playbook = playbooks_dir / "bad.yml"
        bad_playbook.write_text("invalid: yaml: [", encoding="utf-8")
        
        # Should not crash, just log warning and skip or return partial info
        playbooks = parser.discover_playbooks(mock_collection_path)
        
        assert len(playbooks) == 1
        assert playbooks[0].name == "bad"
        # Tags should be empty due to parse failure
        assert playbooks[0].tags == []
