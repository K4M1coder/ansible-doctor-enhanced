#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Data validation filters."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
        
    Examples:
        {{ "user@example.com" | validate_email }}     # Returns True
        {{ "invalid-email" | validate_email }}        # Returns False
    """
    if not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url):
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL format, False otherwise
        
    Examples:
        {{ "https://example.com" | validate_url }}    # Returns True
        {{ "not-a-url" | validate_url }}              # Returns False
    """
    if not isinstance(url, str):
        return False
    
    # URL regex pattern
    pattern = r'^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})?(?:/.*)?$'
    return bool(re.match(pattern, url))


def validate_port(port):
    """
    Validate TCP/UDP port number.
    
    Args:
        port: Port number to validate (int or string)
        
    Returns:
        True if valid port (1-65535), False otherwise
        
    Examples:
        {{ 8080 | validate_port }}        # Returns True
        {{ "443" | validate_port }}       # Returns True
        {{ 0 | validate_port }}           # Returns False
        {{ 70000 | validate_port }}       # Returns False
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def validate_ipv4(ip):
    """
    Validate IPv4 address format.
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if valid IPv4 address, False otherwise
        
    Examples:
        {{ "192.168.1.1" | validate_ipv4 }}       # Returns True
        {{ "256.1.1.1" | validate_ipv4 }}         # Returns False
        {{ "192.168.1" | validate_ipv4 }}         # Returns False
    """
    if not isinstance(ip, str):
        return False
    
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


class FilterModule(object):
    """Ansible filter plugin for data validation."""
    
    def filters(self):
        return {
            'validate_email': validate_email,
            'validate_url': validate_url,
            'validate_port': validate_port,
            'validate_ipv4': validate_ipv4,
        }
