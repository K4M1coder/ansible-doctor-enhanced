"""
Utility functions for YAML parsing tasks.

Common utilities shared between parsers.
"""

from typing import Any


def extract_tags_from_yaml(tags_value: Any) -> list[str]:
    """
    Extract and normalize tags from YAML data.
    
    Handles multiple formats:
    - String: "tag1" → ["tag1"]
    - List: ["tag1", "tag2"] → ["tag1", "tag2"]
    - Mixed list: ["tag1", null, "", "tag2"] → ["tag1", "tag2"]
    - Invalid types → []
    
    Args:
        tags_value: Raw tags value from YAML (can be str, list, or other)
        
    Returns:
        List of normalized tag strings (stripped, non-empty)
    """
    if not tags_value:
        return []
    
    # Handle string format
    if isinstance(tags_value, str):
        tag = tags_value.strip()
        return [tag] if tag else []
    
    # Handle list format
    if isinstance(tags_value, list):
        normalized_tags = []
        for tag in tags_value:
            if isinstance(tag, str):
                tag = tag.strip()
                if tag:
                    normalized_tags.append(tag)
        return normalized_tags
    
    # Invalid type
    return []
