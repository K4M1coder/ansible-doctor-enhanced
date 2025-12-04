import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from ansibledoctor.parser.collection_parser import CollectionParser
from ansibledoctor.models.role import AnsibleRole

class TestDeepParsing:
    @patch("ansibledoctor.parser.collection_parser.RoleParser")
    def test_deep_parse_triggers_role_parsing(self, mock_role_parser_cls, tmp_path):
        """Test that deep_parse=True triggers RoleParser."""
        # Arrange
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text("namespace: my_namespace\nname: my_collection\nversion: 1.0.0")
        
        roles_dir = collection_dir / "roles"
        roles_dir.mkdir()
        role_path = roles_dir / "my_role"
        role_path.mkdir()
        
        # Create a real AnsibleRole object for the mock return value
        real_role = AnsibleRole(
            name="my_role",
            path=role_path
        )
        
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = real_role
        mock_role_parser_cls.return_value = mock_parser_instance
        
        # Act
        parser = CollectionParser()
        collection = parser.parse(collection_dir, deep_parse=True)
        
        # Assert
        mock_role_parser_cls.assert_called()
        mock_parser_instance.parse.assert_called_with(role_path)
        
        # Verify collection has the role object
        assert len(collection.roles) == 1
        assert isinstance(collection.roles[0], AnsibleRole)
        assert collection.roles[0].name == "my_role"
