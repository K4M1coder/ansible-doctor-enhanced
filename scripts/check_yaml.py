#!/usr/bin/env python3
"""Validate YAML files passed on the command line.

This checks each specified file with PyYAML's safe_load to ensure it's valid YAML.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("No files to validate")
        return 0
    ok = True
    for p in argv:
        try:
            content = Path(p).read_text(encoding="utf-8")
            yaml.safe_load(content)
        except Exception as e:
            print(f"YAML validation failed for {p}: {e}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
