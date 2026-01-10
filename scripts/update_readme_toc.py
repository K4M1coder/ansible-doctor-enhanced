#!/usr/bin/env python3
"""Update README.md Table of Contents using a custom parser."""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def extract_headings(content: str, verbose: bool = False) -> List[Tuple[int, str, str]]:
    """Extract headings from markdown content.

    Returns:
        List of tuples: (level, text, anchor)
    """
    headings = []
    anchor_counts: dict[str, int] = {}  # Track duplicate anchors
    lines = content.split("\n")
    in_code_block = False

    for line in lines:
        # Track code blocks - toggle on fence lines
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        # Skip headings inside code blocks
        if in_code_block:
            continue

        # Match markdown headings H2-H6 (skip H1 as it's usually document title or comments in code)
        match = re.match(r"^(#{2,6})\s+(.+)$", line)
        if match:
            hashes = match.group(1)
            level = len(hashes)
            text = match.group(2).strip()

            # Skip the TOC heading itself
            if "📑 Table of Contents" in text or "Table of Contents" in text:
                continue

            # Skip headings with markdown links (example headings)
            if "[" in text and "](" in text:
                continue

            # Skip headings with template syntax
            if "{{" in text or "{%" in text:
                continue

            # Generate GitHub-style anchor
            anchor = generate_github_anchor(text)

            # Handle duplicate anchors (GitHub adds -1, -2, etc.)
            if anchor in anchor_counts:
                anchor_counts[anchor] += 1
                anchor = f"{anchor}-{anchor_counts[anchor]}"
            else:
                anchor_counts[anchor] = 0

            if verbose:
                print(f"Heading: {text!r} -> Anchor: {anchor!r}")
            headings.append((level, text, anchor))

    return headings


def generate_github_anchor(text: str) -> str:
    """Generate GitHub-compatible anchor from heading text.

    GitHub converts emojis to hyphens in anchors and preserves leading hyphens.
    For example: "📦 Ansible" becomes "-ansible".

    Args:
        text: The heading text

    Returns:
        GitHub-style anchor (lowercase, hyphens, emoji → hyphen)
    """
    anchor = text

    # Remove markdown formatting first
    anchor = re.sub(r"\*\*(.+?)\*\*", r"\1", anchor)  # Bold
    anchor = re.sub(r"\*(.+?)\*", r"\1", anchor)  # Italic
    anchor = re.sub(r"`(.+?)`", r"\1", anchor)  # Code
    anchor = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", anchor)  # Links

    # Convert to lowercase
    anchor = anchor.lower()

    # Replace emojis with hyphen (GitHub converts each emoji to single hyphen)
    anchor = re.sub(r"[\U0001F000-\U0001F9FF]", "-", anchor)  # Emoticons and symbols
    anchor = re.sub(r"[\u2600-\u26FF]", "-", anchor)  # Misc symbols
    anchor = re.sub(r"[\u2700-\u27BF]", "-", anchor)  # Dingbats
    anchor = re.sub(r"[\U0001FA00-\U0001FAFF]", "-", anchor)  # Extended symbols
    anchor = re.sub(r"[\uFE00-\uFE0F]", "", anchor)  # Variation selectors (remove)
    anchor = re.sub(r"[\u200D]", "", anchor)  # Zero-width joiner (remove)

    # Remove special characters and punctuation (keep only alphanumeric, spaces, hyphens)
    anchor = re.sub(r"[^\w\s-]", "", anchor)

    # Replace whitespace with hyphens
    anchor = re.sub(r"\s+", "-", anchor)
    
    # Collapse multiple hyphens into single hyphen
    anchor = re.sub(r"-+", "-", anchor)

    # Remove only trailing hyphens (keep leading hyphen from emoji)
    anchor = anchor.rstrip("-")

    return anchor


def extract_current_toc(content: str) -> List[str]:
    """Extract current TOC lines from content.

    Returns:
        List of TOC link lines (e.g., ['- [Text](#anchor)', ...])
    """
    pattern = r"<!-- toc -->(.*?)<!-- tocstop -->"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []

    toc_content = match.group(1).strip()
    if not toc_content:
        return []

    # Split into lines and filter out empty lines
    lines = [line.strip() for line in toc_content.split("\n") if line.strip()]
    return lines


def compare_tocs(current_toc: List[str], new_toc: List[str]) -> Tuple[List[str], List[str]]:
    """Compare current and new TOC to find added and removed links.

    Returns:
        Tuple of (added, removed) lists
    """
    current_set = set(current_toc)
    new_set = set(new_toc)

    added = sorted(new_set - current_set)
    removed = sorted(current_set - new_set)

    return added, removed


def generate_toc(headings: List[Tuple[int, str, str]]) -> str:
    """Generate table of contents from headings.

    Args:
        headings: List of (level, text, anchor) tuples

    Returns:
        Formatted TOC markdown
    """
    if not headings:
        return ""

    toc_lines = []

    for level, text, anchor in headings:
        # Calculate indentation: H2=0, H3=2, H4=4, H5=6, H6=8 spaces
        indent = "  " * (level - 2)
        # Keep original text with emojis in the link text
        toc_lines.append(f"{indent}- [{text}](#{anchor})")

    return "\n".join(toc_lines)


def update_readme_toc(readme_path: Path, verbose: bool = False) -> bool:
    """Update TOC in README.md between <!-- toc --> and <!-- tocstop --> markers.

    Args:
        readme_path: Path to README.md file
        verbose: Whether to print detailed heading processing info

    Returns:
        True if TOC was updated, False otherwise
    """
    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        return False

    # Read the README content
    content = readme_path.read_text(encoding="utf-8")

    # Check if TOC markers exist
    if "<!-- toc -->" not in content or "<!-- tocstop -->" not in content:
        print("Warning: TOC markers (<!-- toc --> / <!-- tocstop -->) not found in README.md")
        print("Skipping TOC update.")
        return False

    # Extract current TOC
    current_toc_lines = extract_current_toc(content)

    # Extract headings from the content
    headings = extract_headings(content, verbose)

    if not headings:
        print("Warning: No headings found in README.md")
        return False

    print(f"Found {len(headings)} headings")

    # Generate TOC
    toc = generate_toc(headings)

    if not toc:
        print("Warning: Generated TOC is empty")
        return False

    # Get new TOC lines
    new_toc_lines = [line.strip() for line in toc.split("\n") if line.strip()]

    # Compare TOCs
    added, removed = compare_tocs(current_toc_lines, new_toc_lines)

    # Show statistics
    total_changes = len(added) + len(removed)
    if total_changes > 0:
        print(f"TOC changes: +{len(added)} added, -{len(removed)} removed")
    else:
        print("TOC is up to date (no changes needed)")

    # In verbose mode, show details
    if verbose and total_changes > 0:
        if added:
            print("\nAdded links:")
            for link in added:
                print(f"  + {link}")
        if removed:
            print("\nRemoved links:")
            for link in removed:
                print(f"  - {link}")

    # Replace content between markers
    pattern = r"(<!-- toc -->).*?(<!-- tocstop -->)"
    replacement = f"\\1\n\n{toc}\n\n\\2"

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Check if content changed
    if new_content == content:
        if total_changes > 0:
            print("Warning: TOC changes detected but content unchanged")
        # No message for up-to-date case since we already showed statistics
        return False

    # Write updated content
    readme_path.write_text(new_content, encoding="utf-8")
    print("✓ README.md TOC updated successfully")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update README.md Table of Contents")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print detailed heading processing information"
    )

    args = parser.parse_args()

    readme_path = Path("README.md")

    try:
        updated = update_readme_toc(readme_path, verbose=args.verbose)
        return 0 if not updated else 0  # Always return 0 to not block commits
    except Exception as e:
        print(f"Error updating TOC: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
