"""
Plugin parser module.

This module provides functionality to parse Ansible plugin files and extract
metadata such as DOCUMENTATION, EXAMPLES, and RETURN blocks.
"""
import ast
import logging
import yaml
from typing import Dict, Any, Optional, Union

from ansibledoctor.models.plugin import Plugin

logger = logging.getLogger(__name__)


class PluginParser:
    """Parses Ansible plugin files to extract documentation."""

    def parse(self, plugin: Plugin) -> Plugin:
        """
        Parse plugin file and populate metadata fields.

        Extracts DOCUMENTATION, EXAMPLES, and RETURN blocks from the plugin
        source code using AST parsing.

        Args:
            plugin: The Plugin object to parse (must have path set)

        Returns:
            The updated Plugin object with documentation fields populated
        """
        if not plugin.path or not plugin.path.exists():
            logger.warning(f"Plugin path does not exist: {plugin.path}")
            return plugin

        updates: Dict[str, Any] = {}

        try:
            content = plugin.path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "DOCUMENTATION":
                                doc_yaml = self._extract_string_value(node.value)
                                if doc_yaml:
                                    doc_dict = self._parse_yaml(doc_yaml, plugin.name, "DOCUMENTATION")
                                    if doc_dict:
                                        updates["documentation"] = doc_dict
                                        if "short_description" in doc_dict:
                                            updates["short_description"] = doc_dict["short_description"]
                            elif target.id == "EXAMPLES":
                                examples_str = self._extract_string_value(node.value)
                                if examples_str:
                                    updates["examples"] = examples_str
                            elif target.id == "RETURN":
                                return_yaml = self._extract_string_value(node.value)
                                if return_yaml:
                                    return_dict = self._parse_yaml(return_yaml, plugin.name, "RETURN")
                                    if return_dict:
                                        updates["return_values"] = return_dict

        except Exception as e:
            logger.error(f"Error parsing plugin {plugin.name}: {e}")
            return plugin

        if updates:
            return plugin.model_copy(update=updates)

        return plugin

    def _extract_string_value(self, node: ast.AST) -> Optional[str]:
        """Extract string value from an AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.Str):  # Legacy Python < 3.8
            return node.s
        return None

    def _parse_yaml(self, yaml_str: str, plugin_name: str, block_type: str) -> Optional[Dict[str, Any]]:
        """Parse YAML string with error handling."""
        try:
            return yaml.safe_load(yaml_str)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse {block_type} YAML in plugin {plugin_name}: {e}")
            return None
