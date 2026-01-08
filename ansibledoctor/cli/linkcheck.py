"""
CLI commands for link validation in Ansible Doctor.

Provides commands for validating, fixing, and reporting on documentation links.
Part of Spec 013 User Story 2 (Detect Broken Links).

Commands:
- ansible-doctor linkcheck: Validate all links in documentation
- ansible-doctor linkfix: Attempt to fix broken links (future)
- ansible-doctor linkreport: Generate detailed link health report

Architecture:
- Library-First: Uses LinkValidator from ansibledoctor.links
- CLI-thin: Command parsing and output formatting only
- Follows Constitution Article VII (CLI Design)

Spec: 013-links-cross-references
Phase: 4 (User Story 2 - Detect Broken Links)
Tasks: T040-T044
"""

import json
import sys
from pathlib import Path
from typing import Any

import click

from ansibledoctor.links.link_validator import LinkValidator, ValidationResult
from ansibledoctor.models.link import LinkStatus
from ansibledoctor.utils.link_parser import LinkParser
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


@click.group(name="link")
def link_commands():
    """Link validation and management commands."""
    pass


@link_commands.command(name="check")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    type=click.Choice(["text", "json", "summary"]),
    default="text",
    help="Output format for validation results",
)
@click.option(
    "--external/--no-external",
    default=True,
    help="Validate external HTTP links (may be slow)",
)
@click.option(
    "--timeout",
    type=float,
    default=5.0,
    help="Timeout for external link validation (seconds)",
)
@click.option(
    "--exit-code/--no-exit-code",
    default=True,
    help="Exit with non-zero code if broken links found",
)
def linkcheck(
    path: Path,
    format: str,
    external: bool,
    timeout: float,
    exit_code: bool,
) -> None:
    """Validate all links in documentation.
    
    Scans all documentation files and validates internal file links,
    section anchors, and optionally external HTTP links.
    
    Examples:
        ansible-doctor link check ./docs
        ansible-doctor link check ./docs --no-external
        ansible-doctor link check ./docs --format json
    """
    # Only show progress messages for non-JSON formats
    show_progress = format != "json"
    
    if show_progress:
        click.echo(f"🔍 Validating links in: {path}")
    
    # T041: Full implementation
    # Step 1: Scan directory for documentation files
    parser = LinkParser()
    if show_progress:
        click.echo("📂 Scanning documentation files...")
    
    try:
        all_links = parser.parse_directory(path)
    except Exception as e:
        if show_progress:
            click.echo(f"❌ Error scanning directory: {e}", err=True)
        if exit_code:
            sys.exit(1)
        return
    
    if not all_links:
        if show_progress:
            click.echo("⚠️  No links found in documentation")
        return
    
    if show_progress:
        click.echo(f"🔗 Found {len(all_links)} links to validate")
    
    # Step 2: Initialize validator
    validator = LinkValidator(base_path=path, timeout=timeout, enable_cache=True)
    
    # Step 3: Validate each link
    results: list[ValidationResult] = []
    broken_count = 0
    warning_count = 0
    valid_count = 0
    
    for i, link in enumerate(all_links, start=1):
        # Skip external links if disabled
        if not external and link.link_type.name.startswith("EXTERNAL"):
            continue
        
        # Validate link
        result = validator.validate(link)
        results.append(result)
        
        # Count by status
        if result.status == LinkStatus.BROKEN:
            broken_count += 1
        elif result.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT):
            warning_count += 1
        elif result.status == LinkStatus.VALID:
            valid_count += 1
        
        # Show progress for large doc sets
        if show_progress and i % 100 == 0:
            click.echo(f"⏳ Progress: {i}/{len(all_links)} links validated...")
    
    # Step 4: Format and output results
    if format == "json":
        _output_json_format(results)
    elif format == "summary":
        _output_summary_format(results, broken_count, warning_count, valid_count)
    else:  # text
        _output_text_format(results, broken_count, warning_count, valid_count)
    
    # Step 5: Exit with appropriate code
    if exit_code and broken_count > 0:
        sys.exit(1)


def _output_text_format(
    results: list[ValidationResult],
    broken_count: int,
    warning_count: int,
    valid_count: int,
) -> None:
    """Output validation results in text format."""
    click.echo("\n" + "=" * 60)
    click.echo("📊 Link Validation Results")
    click.echo("=" * 60)
    
    # Show broken links
    if broken_count > 0:
        click.echo(f"\n❌ Broken Links ({broken_count}):")
        for result in results:
            if result.status == LinkStatus.BROKEN:
                click.echo(
                    f"  • {result.source_file}:{result.line_number or '?'}\n"
                    f"    Target: {result.link.target}\n"
                    f"    Error: {result.error_message}"
                )
    
    # Show warnings
    if warning_count > 0:
        click.echo(f"\n⚠️  Warnings ({warning_count}):")
        for result in results:
            if result.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT):
                click.echo(
                    f"  • {result.source_file}:{result.line_number or '?'}\n"
                    f"    Target: {result.link.target}\n"
                    f"    Warning: {result.error_message}"
                )
    
    # Summary
    click.echo("\n" + "=" * 60)
    click.echo(f"✅ Valid:   {valid_count}")
    click.echo(f"⚠️  Warning: {warning_count}")
    click.echo(f"❌ Broken:  {broken_count}")
    click.echo(f"📊 Total:   {len(results)}")
    click.echo("=" * 60)
    
    if broken_count == 0 and warning_count == 0:
        click.echo("\n🎉 All links are valid!")


def _output_summary_format(
    results: list[ValidationResult],
    broken_count: int,
    warning_count: int,
    valid_count: int,
) -> None:
    """Output validation results in summary format."""
    click.echo("\n📊 Summary:")
    click.echo(f"  Valid:   {valid_count}")
    click.echo(f"  Warning: {warning_count}")
    click.echo(f"  Broken:  {broken_count}")
    click.echo(f"  Total:   {len(results)}")
    
    if broken_count > 0:
        click.echo(f"\n❌ {broken_count} broken link(s) found")
    elif warning_count > 0:
        click.echo(f"\n⚠️  {warning_count} warning(s) found")
    else:
        click.echo("\n✅ All links valid!")


def _output_json_format(results: list[ValidationResult]) -> None:
    """Output validation results in JSON format."""
    output = {
        "links": [
            {
                "source_file": str(r.source_file),
                "line_number": r.line_number,
                "target": r.link.target,
                "link_type": r.link.link_type.name,
                "status": r.status.name,
                "is_valid": r.is_valid,
                "error_message": r.error_message,
                "resolved_path": str(r.resolved_path) if r.resolved_path else None,
            }
            for r in results
        ],
        "summary": {
            "total": len(results),
            "valid": sum(1 for r in results if r.status == LinkStatus.VALID),
            "warning": sum(1 for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)),
            "broken": sum(1 for r in results if r.status == LinkStatus.BROKEN),
        },
    }
    click.echo(json.dumps(output, indent=2))


@link_commands.command(name="fix")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--dry-run/--no-dry-run",
    default=True,
    help="Show what would be fixed without making changes",
)
@click.option(
    "--backup/--no-backup",
    default=True,
    help="Create backup files before fixing",
)
def linkfix(path: Path, dry_run: bool, backup: bool) -> None:
    """Attempt to automatically fix broken links.
    
    Analyzes broken links and attempts to fix common issues:
    - Update moved file paths
    - Fix incorrect section anchors
    - Update renamed files
    
    Examples:
        ansible-doctor link fix ./docs --dry-run
        ansible-doctor link fix ./docs --no-backup
    """
    click.echo(f"🔧 Fixing links in: {path}")
    
    # Future enhancement (not in current spec)
    click.echo("⚠️  Link fixing not yet implemented")
    click.echo("📋 This will attempt to auto-fix broken links")
    
    if dry_run:
        click.echo("🔍 Running in dry-run mode (no changes will be made)")


@link_commands.command(name="report")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file for report (default: stdout)",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "html", "markdown"]),
    default="markdown",
    help="Report format",
)
@click.option(
    "--group-by",
    type=click.Choice(["file", "severity", "type"]),
    default="file",
    help="How to group validation results",
)
def linkreport(
    path: Path,
    output: Path | None,
    format: str,
    group_by: str,
) -> None:
    """Generate detailed link health report.
    
    Creates comprehensive report of link validation results with statistics
    and recommendations.
    
    Examples:
        ansible-doctor link report ./docs
        ansible-doctor link report ./docs --format html --output report.html
        ansible-doctor link report ./docs --group-by severity
    """
    click.echo(f"📊 Generating link report for: {path}")
    
    # TODO T042: Implementation
    # 1. Run link validation
    # 2. Collect statistics (total links, broken, warnings, etc.)
    # 3. Group results as requested
    # 4. Generate report in requested format
    # 5. Write to file or stdout
    
    click.echo("⚠️  Link reporting not yet implemented")
    click.echo(f"📋 Report format: {format}, grouping: {group_by}")
    
    if output:
        click.echo(f"📄 Output will be written to: {output}")


# Export for integration with main CLI
__all__ = ["link_commands", "linkcheck", "linkfix", "linkreport"]
