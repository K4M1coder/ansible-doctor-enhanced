#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Text manipulation filters."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re


def slugify(text):
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to convert
        
    Returns:
        Slugified text
        
    Examples:
        {{ "Hello World!" | slugify }}      # Returns "hello-world"
        {{ "Test_123 (Demo)" | slugify }}   # Returns "test-123-demo"
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    
    # Remove leading/trailing hyphens
    return text.strip('-')


def truncate_words(text, count=50, suffix='...'):
    """
    Truncate text to specified word count.
    
    Args:
        text: Text to truncate
        count: Maximum word count
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
        
    Examples:
        {{ long_text | truncate_words(10) }}
        {{ description | truncate_words(20, '...') }}
    """
    if not isinstance(text, str):
        text = str(text)
    
    words = text.split()
    if len(words) <= count:
        return text
    
    return ' '.join(words[:count]) + suffix


def sanitize_filename(filename):
    """
    Sanitize filename by removing unsafe characters.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Safe filename
        
    Examples:
        {{ "my/file:name.txt" | sanitize_filename }}  # Returns "my_file_name.txt"
    """
    if not isinstance(filename, str):
        filename = str(filename)
    
    # Remove or replace unsafe characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    safe = re.sub(r'[\x00-\x1f\x7f]', '', safe)
    
    # Limit length to 255 characters (common filesystem limit)
    if len(safe) > 255:
        name, ext = safe.rsplit('.', 1) if '.' in safe else (safe, '')
        safe = name[:255 - len(ext) - 1] + '.' + ext if ext else name[:255]
    
    return safe


class FilterModule(object):
    """Ansible filter plugin for text manipulation."""
    
    def filters(self):
        return {
            'slugify': slugify,
            'truncate_words': truncate_words,
            'sanitize_filename': sanitize_filename,
        }
