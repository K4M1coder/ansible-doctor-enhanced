#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ansible filter plugins for string manipulation.
"""


def to_snake_case(value):
    """Convert string to snake_case."""
    import re

    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_camel_case(value):
    """Convert string to camelCase."""
    components = value.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class FilterModule:
    """Ansible filter module."""

    def filters(self):
        return {
            "to_snake_case": to_snake_case,
            "to_camel_case": to_camel_case,
        }
