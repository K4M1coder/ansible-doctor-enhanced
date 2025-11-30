#!/usr/bin/env python3
"""Create a GitHub PR using ghapi and an environment token.

Usage: set GITHUB_TOKEN in environment (Temp, or via 'setx' on Windows), then run:
    poetry run python scripts/create_pr.py --title "PR title" --head 005-i18n-support --base dev --body-file pr_body.md

This script uses `ghapi` to create a pull request and returns the PR URL.
"""
from __future__ import annotations

import argparse
import os

from ghapi.all import GhApi


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a GitHub PR")
    parser.add_argument("--title", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--body-file", help="Path to a file containing the PR body text")
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: set GITHUB_TOKEN in the environment before running this script.")
        return 2

    body_text = ""
    if args.body_file:
        try:
            with open(args.body_file, "r", encoding="utf-8") as fh:
                body_text = fh.read()
        except FileNotFoundError:
            print("Body file not found: %s" % args.body_file)
            return 3

    api = GhApi(owner="K4M1coder", repo="ansible-doctor-enhanced", token=token)
    pr = api.pulls.create(title=args.title, head=args.head, base=args.base, body=body_text)
    print("PR created:", pr.html_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
