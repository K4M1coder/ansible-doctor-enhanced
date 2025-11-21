#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Formatting filters for text manipulation."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def format_bytes(size_bytes):
    """
    Format bytes to human-readable size.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.5 MB")
        
    Examples:
        {{ 1048576 | format_bytes }}  # Returns "1.0 MB"
        {{ 1500 | format_bytes }}     # Returns "1.5 KB"
    """
    if not isinstance(size_bytes, (int, float)):
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_uptime(seconds):
    """
    Format seconds to uptime string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted uptime string (e.g., "2 days, 3 hours")
        
    Examples:
        {{ 86400 | format_uptime }}      # Returns "1 day"
        {{ 90061 | format_uptime }}      # Returns "1 day, 1 hour, 1 minute"
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "0 seconds"
    
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 and not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts) if parts else "0 seconds"


def format_version(version_string):
    """
    Format version string with semantic version padding.
    
    Args:
        version_string: Version string (e.g., "1.2", "1.2.3")
        
    Returns:
        Padded version string (e.g., "1.2.0", "1.2.3")
        
    Examples:
        {{ "1.2" | format_version }}     # Returns "1.2.0"
        {{ "2" | format_version }}       # Returns "2.0.0"
    """
    if not isinstance(version_string, str):
        version_string = str(version_string)
    
    parts = version_string.split('.')
    while len(parts) < 3:
        parts.append('0')
    
    return '.'.join(parts[:3])


class FilterModule(object):
    """Ansible filter plugin for formatting."""
    
    def filters(self):
        return {
            'format_bytes': format_bytes,
            'format_uptime': format_uptime,
            'format_version': format_version,
        }
