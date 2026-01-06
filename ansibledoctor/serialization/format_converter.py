"""Format conversion utilities for ansible-doctor.

Converts between YAML, JSON, XML, and Mermaid diagram formats.
Supports pretty formatting and round-trip conversions.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


class FormatConverter:
    """Converts data between different serialization formats.
    
    Supports conversions between:
    - YAML ↔ JSON
    - JSON ↔ XML
    - Data → Mermaid diagrams
    
    Examples:
        >>> converter = FormatConverter()
        >>> result = converter.convert_file("config.yml", to_format="json")
        >>> result = converter.convert("{'key': 'value'}", from_format="yaml", to_format="json")
    """

    def __init__(self):
        """Initialize FormatConverter."""
        self.yaml = YAML()
        self.yaml.default_flow_style = False
        self.yaml.preserve_quotes = True

    def convert_file(
        self, 
        file_path: Path | str, 
        to_format: str,
        from_format: str | None = None,
        pretty: bool = True
    ) -> str:
        """Convert a file from one format to another.
        
        Args:
            file_path: Path to input file
            to_format: Target format (json, yaml, xml, mermaid)
            from_format: Source format (auto-detected if None)
            pretty: Whether to format output for readability
            
        Returns:
            Converted data as string
            
        Raises:
            ValueError: If format is unsupported
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect source format from extension
        if from_format is None:
            from_format = self._detect_format(file_path)
        
        # Read and parse file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse source data
        data = self._parse(content, from_format)
        
        # Convert to target format
        return self._serialize(data, to_format, pretty=pretty)

    def convert(
        self,
        data: str | dict | list,
        from_format: str,
        to_format: str,
        pretty: bool = True
    ) -> str:
        """Convert data from one format to another.
        
        Args:
            data: Input data (string or parsed data)
            from_format: Source format (json, yaml, xml)
            to_format: Target format (json, yaml, xml, mermaid)
            pretty: Whether to format output for readability
            
        Returns:
            Converted data as string
            
        Raises:
            ValueError: If format is unsupported
        """
        # If data is already parsed, use it directly
        if isinstance(data, (dict, list)):
            parsed_data = data
        else:
            # Parse from source format
            parsed_data = self._parse(data, from_format)
        
        # Convert to target format
        return self._serialize(parsed_data, to_format, pretty=pretty)

    def _detect_format(self, file_path: Path) -> str:
        """Detect format from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected format (yaml, json, xml)
        """
        suffix = file_path.suffix.lower()
        
        if suffix in [".yml", ".yaml"]:
            return "yaml"
        elif suffix == ".json":
            return "json"
        elif suffix == ".xml":
            return "xml"
        else:
            # Default to YAML for config files
            return "yaml"

    def _parse(self, content: str, format_type: str) -> dict | list:
        """Parse content from a specific format.
        
        Args:
            content: Raw content string
            format_type: Format to parse (json, yaml, xml)
            
        Returns:
            Parsed data as dict or list
            
        Raises:
            ValueError: If format is unsupported
        """
        if format_type == "json":
            return json.loads(content)
        elif format_type == "yaml":
            return self.yaml.load(content)
        elif format_type == "xml":
            return self._xml_to_dict(content)
        else:
            raise ValueError(f"Unsupported source format: {format_type}")

    def _serialize(
        self, 
        data: dict | list, 
        format_type: str, 
        pretty: bool = True
    ) -> str:
        """Serialize data to a specific format.
        
        Args:
            data: Data to serialize
            format_type: Target format (json, yaml, xml, mermaid)
            pretty: Whether to format for readability
            
        Returns:
            Serialized data as string
            
        Raises:
            ValueError: If format is unsupported
        """
        if format_type == "json":
            if pretty:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, ensure_ascii=False)
                
        elif format_type == "yaml":
            from io import StringIO
            stream = StringIO()
            self.yaml.dump(data, stream)
            return stream.getvalue()
            
        elif format_type == "xml":
            return self._dict_to_xml(data, pretty=pretty)
            
        elif format_type == "mermaid":
            return self._generate_mermaid(data)
            
        else:
            raise ValueError(f"Unsupported target format: {format_type}")

    def _xml_to_dict(self, xml_content: str) -> dict:
        """Convert XML to dictionary.
        
        Args:
            xml_content: XML content as string
            
        Returns:
            Dictionary representation of XML
        """
        root = ET.fromstring(xml_content)
        return self._element_to_dict(root)

    def _element_to_dict(self, element: ET.Element) -> dict | str:
        """Convert XML element to dictionary recursively.
        
        Args:
            element: XML element
            
        Returns:
            Dictionary or string representation
        """
        result = {}
        
        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib
        
        # Process children
        if len(element):
            children = {}
            for child in element:
                child_data = self._element_to_dict(child)
                
                if child.tag in children:
                    # Multiple children with same tag - convert to list
                    if not isinstance(children[child.tag], list):
                        children[child.tag] = [children[child.tag]]
                    children[child.tag].append(child_data)
                else:
                    children[child.tag] = child_data
            
            result.update(children)
        
        # Add text content
        if element.text and element.text.strip():
            text = element.text.strip()
            if result:
                result["#text"] = text
            else:
                return text
        
        return result if result else ""

    def _dict_to_xml(self, data: dict | list, pretty: bool = True) -> str:
        """Convert dictionary to XML.
        
        Args:
            data: Dictionary or list to convert
            pretty: Whether to format with indentation
            
        Returns:
            XML string
        """
        root = ET.Element("root")
        self._build_xml_element(root, data)
        
        if pretty:
            self._indent_xml(root)
        
        tree = ET.ElementTree(root)
        from io import StringIO
        stream = StringIO()
        tree.write(stream, encoding="unicode", xml_declaration=False)
        xml_content = stream.getvalue()
        
        # Add XML declaration manually
        return '<?xml version="1.0" encoding="utf-8"?>\n' + xml_content

    def _build_xml_element(self, parent: ET.Element, data: Any) -> None:
        """Build XML element from data recursively.
        
        Args:
            parent: Parent XML element
            data: Data to add
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "@attributes":
                    parent.attrib.update(value)
                elif key == "#text":
                    parent.text = str(value)
                else:
                    if isinstance(value, list):
                        for item in value:
                            child = ET.SubElement(parent, key)
                            if isinstance(item, (dict, list)):
                                self._build_xml_element(child, item)
                            else:
                                child.text = str(item)
                    else:
                        child = ET.SubElement(parent, key)
                        if isinstance(value, (dict, list)):
                            self._build_xml_element(child, value)
                        else:
                            child.text = str(value)
                            
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, "item")
                if isinstance(item, (dict, list)):
                    self._build_xml_element(child, item)
                else:
                    child.text = str(item)
        else:
            parent.text = str(data)

    def _indent_xml(self, element: ET.Element, level: int = 0) -> None:
        """Add indentation to XML element for pretty printing.
        
        Args:
            element: XML element to indent
            level: Current indentation level
        """
        indent = "\n" + "  " * level
        
        if len(element):
            if not element.text or not element.text.strip():
                element.text = indent + "  "
            if not element.tail or not element.tail.strip():
                element.tail = indent
                
            for child in element:
                self._indent_xml(child, level + 1)
                
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = indent

    def _generate_mermaid(self, data: dict | list) -> str:
        """Generate Mermaid diagram from data structure.
        
        Args:
            data: Data to visualize
            
        Returns:
            Mermaid diagram syntax
        """
        lines = ["graph TB"]
        
        if isinstance(data, dict):
            lines.append('    root["Root"]')
            self._add_dict_to_mermaid_lines(lines, "root", data)
        elif isinstance(data, list):
            lines.append('    root["Root List"]')
            for i, item in enumerate(data):
                node_id = f"item{i}"
                lines.append(f'    {node_id}["Item {i}"]')
                lines.append(f"    root --> {node_id}")
                
                if isinstance(item, dict):
                    self._add_dict_to_mermaid_lines(lines, node_id, item)
        
        return "\n".join(lines)

    def _add_dict_to_mermaid_lines(
        self, 
        lines: list[str],
        parent_id: str, 
        data: dict,
        depth: int = 0,
        max_depth: int = 3
    ) -> None:
        """Add dictionary structure to Mermaid diagram lines.
        
        Args:
            lines: List of Mermaid lines to append to
            parent_id: Parent node ID
            data: Dictionary data
            depth: Current recursion depth
            max_depth: Maximum recursion depth
        """
        if depth >= max_depth:
            return
        
        for key, value in data.items():
            # Sanitize key for node ID
            node_id = f"{parent_id}_{key}".replace("-", "_").replace(".", "_").replace(" ", "_")
            
            if isinstance(value, dict):
                lines.append(f'    {node_id}["{key}"]')
                lines.append(f"    {parent_id} --> {node_id}")
                self._add_dict_to_mermaid_lines(lines, node_id, value, depth + 1, max_depth)
            elif isinstance(value, list):
                list_label = f"{key} (list)"
                lines.append(f'    {node_id}["{list_label}"]')
                lines.append(f"    {parent_id} --> {node_id}")
            else:
                # Leaf node with value
                value_str = str(value)[:30]  # Truncate long values
                # Escape quotes in label
                label = f"{key}: {value_str}".replace('"', "'")
                lines.append(f'    {node_id}["{label}"]')
                lines.append(f"    {parent_id} --> {node_id}")
