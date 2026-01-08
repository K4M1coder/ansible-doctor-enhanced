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
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear cache before validation (force fresh check)",
)
def linkcheck(
    path: Path,
    format: str,
    external: bool,
    timeout: float,
    exit_code: bool,
    clear_cache: bool,
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

    # Clear cache if requested (T043)
    if clear_cache:
        validator.clear_cache()
        if show_progress:
            click.echo("🗑️  Cache cleared")

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

    # Step 5: Save cache for next run (T043)
    validator.save_cache()

    # Step 6: Exit with appropriate code
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
            "warning": sum(
                1 for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)
            ),
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
def linkreport(
    path: Path,
    output: Path | None,
    format: str,
    group_by: str,
    external: bool,
    timeout: float,
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

    # T042: Full implementation
    # Step 1: Run link validation (same as linkcheck)
    parser = LinkParser()
    click.echo("📂 Scanning documentation files...")

    try:
        all_links = parser.parse_directory(path)
    except Exception as e:
        click.echo(f"❌ Error scanning directory: {e}", err=True)
        sys.exit(1)

    if not all_links:
        click.echo("⚠️  No links found in documentation")
        return

    click.echo(f"🔗 Found {len(all_links)} links to validate")

    # Step 2: Validate all links
    validator = LinkValidator(base_path=path, timeout=timeout, enable_cache=True)
    results: list[ValidationResult] = []

    for i, link in enumerate(all_links, start=1):
        # Skip external links if disabled
        if not external and link.link_type.name.startswith("EXTERNAL"):
            continue

        result = validator.validate(link)
        results.append(result)

        # Show progress for large doc sets
        if i % 100 == 0:
            click.echo(f"⏳ Progress: {i}/{len(all_links)} links validated...")

    # Step 3: Generate report in requested format
    if format == "markdown":
        report_content = _generate_markdown_report(results, group_by, path)
    elif format == "html":
        report_content = _generate_html_report(results, group_by, path)
    elif format == "json":
        report_content = _generate_json_report(results, group_by)
    else:  # text
        report_content = _generate_text_report(results, group_by, path)

    # Step 4: Save cache for next run (T043)
    validator.save_cache()

    # Step 5: Write to file or stdout
    if output:
        output.write_text(report_content, encoding="utf-8")
        click.echo(f"✅ Report written to: {output}")
    else:
        click.echo("\n" + report_content)


def _generate_markdown_report(
    results: list[ValidationResult], group_by: str, base_path: Path
) -> str:
    """Generate Markdown format report."""
    from datetime import datetime

    # Calculate statistics
    total = len(results)
    valid = sum(1 for r in results if r.status == LinkStatus.VALID)
    warning = sum(1 for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT))
    broken = sum(1 for r in results if r.status == LinkStatus.BROKEN)

    # Build report
    report = f"""# Link Validation Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Base Path**: `{base_path}`  

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Valid | {valid} | {(valid/total*100):.1f}% |
| ⚠️  Warning | {warning} | {(warning/total*100):.1f}% |
| ❌ Broken | {broken} | {(broken/total*100):.1f}% |
| **Total** | **{total}** | **100%** |

"""

    # Group and add details
    if group_by == "file":
        report += _group_by_file_markdown(results)
    elif group_by == "severity":
        report += _group_by_severity_markdown(results)
    else:  # type
        report += _group_by_type_markdown(results)

    # Add recommendations
    if broken > 0 or warning > 0:
        report += "\n## Recommendations\n\n"
        if broken > 0:
            report += (
                f"- 🔧 **Fix {broken} broken link(s)**: Update file paths or remove invalid links\n"
            )
        if warning > 0:
            report += f"- ⚠️  **Review {warning} warning(s)**: Check external URLs for timeouts or redirects\n"
        report += "- 📝 **Run validation regularly**: Catch broken links early in development\n"
        report += (
            "- 🔄 **Use CI/CD integration**: Add `ansible-doctor link check` to your pipeline\n"
        )

    return report


def _group_by_file_markdown(results: list[ValidationResult]) -> str:
    """Group results by source file for Markdown report."""
    from collections import defaultdict

    by_file: dict[Path, list[ValidationResult]] = defaultdict(list)
    for result in results:
        by_file[result.source_file].append(result)

    report = "## Results by File\n\n"

    for file_path in sorted(by_file.keys()):
        file_results = by_file[file_path]
        broken = [r for r in file_results if r.status == LinkStatus.BROKEN]
        warnings = [
            r for r in file_results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)
        ]

        status_icon = "❌" if broken else ("⚠️" if warnings else "✅")
        report += f"### {status_icon} `{file_path.name}`\n\n"
        report += f"**Path**: `{file_path}`  \n"
        report += f"**Links**: {len(file_results)} total ({len(broken)} broken, {len(warnings)} warnings)\n\n"

        if broken:
            report += "**Broken Links**:\n\n"
            for result in broken:
                report += f"- Line {result.line_number}: `{result.link.target}`\n"
                report += f"  - Error: {result.error_message}\n"

        if warnings:
            report += "\n**Warnings**:\n\n"
            for result in warnings:
                report += f"- Line {result.line_number}: `{result.link.target}`\n"
                report += f"  - Warning: {result.error_message}\n"

        report += "\n"

    return report


def _group_by_severity_markdown(results: list[ValidationResult]) -> str:
    """Group results by severity for Markdown report."""
    broken = [r for r in results if r.status == LinkStatus.BROKEN]
    warnings = [r for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)]
    valid = [r for r in results if r.status == LinkStatus.VALID]

    report = "## Results by Severity\n\n"

    if broken:
        report += f"### ❌ Broken Links ({len(broken)})\n\n"
        for result in broken:
            report += (
                f"- `{result.source_file.name}`:{result.line_number} → `{result.link.target}`\n"
            )
            report += f"  - Error: {result.error_message}\n"
        report += "\n"

    if warnings:
        report += f"### ⚠️  Warnings ({len(warnings)})\n\n"
        for result in warnings:
            report += (
                f"- `{result.source_file.name}`:{result.line_number} → `{result.link.target}`\n"
            )
            report += f"  - Warning: {result.error_message}\n"
        report += "\n"

    if valid:
        report += f"### ✅ Valid Links ({len(valid)})\n\n"
        report += f"All {len(valid)} links validated successfully.\n\n"

    return report


def _group_by_type_markdown(results: list[ValidationResult]) -> str:
    """Group results by link type for Markdown report."""
    from collections import defaultdict

    by_type: dict[str, list[ValidationResult]] = defaultdict(list)
    for result in results:
        by_type[result.link.link_type.name].append(result)

    report = "## Results by Link Type\n\n"

    for link_type in sorted(by_type.keys()):
        type_results = by_type[link_type]
        broken = sum(1 for r in type_results if r.status == LinkStatus.BROKEN)
        warnings = sum(
            1 for r in type_results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)
        )
        valid = sum(1 for r in type_results if r.status == LinkStatus.VALID)

        status_icon = "❌" if broken > 0 else ("⚠️" if warnings > 0 else "✅")
        report += f"### {status_icon} {link_type}\n\n"
        report += f"**Total**: {len(type_results)} | **Valid**: {valid} | **Warnings**: {warnings} | **Broken**: {broken}\n\n"

        # Show broken links for this type
        broken_links = [r for r in type_results if r.status == LinkStatus.BROKEN]
        if broken_links:
            report += "**Broken**:\n\n"
            for result in broken_links[:10]:  # Limit to 10 per type
                report += (
                    f"- `{result.source_file.name}`:{result.line_number} → `{result.link.target}`\n"
                )
            if len(broken_links) > 10:
                report += f"- ... and {len(broken_links) - 10} more\n"
            report += "\n"

    return report


def _generate_html_report(results: list[ValidationResult], group_by: str, base_path: Path) -> str:
    """Generate HTML format report."""
    from datetime import datetime

    # Calculate statistics
    total = len(results)
    valid = sum(1 for r in results if r.status == LinkStatus.VALID)
    warning = sum(1 for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT))
    broken = sum(1 for r in results if r.status == LinkStatus.BROKEN)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007bff; color: white; }}
        .valid {{ color: #28a745; font-weight: bold; }}
        .warning {{ color: #ffc107; font-weight: bold; }}
        .broken {{ color: #dc3545; font-weight: bold; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .recommendation {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Link Validation Report</h1>
        <div class="meta">
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Base Path:</strong> <code>{base_path}</code></p>
        </div>
        
        <h2>📊 Summary</h2>
        <table>
            <tr>
                <th>Status</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td class="valid">✅ Valid</td>
                <td>{valid}</td>
                <td>{(valid/total*100):.1f}%</td>
            </tr>
            <tr>
                <td class="warning">⚠️  Warning</td>
                <td>{warning}</td>
                <td>{(warning/total*100):.1f}%</td>
            </tr>
            <tr>
                <td class="broken">❌ Broken</td>
                <td>{broken}</td>
                <td>{(broken/total*100):.1f}%</td>
            </tr>
            <tr>
                <th>Total</th>
                <th>{total}</th>
                <th>100%</th>
            </tr>
        </table>
"""

    # Add recommendations
    if broken > 0 or warning > 0:
        html += """
        <div class="recommendation">
            <h3>💡 Recommendations</h3>
            <ul>
"""
        if broken > 0:
            html += f"                <li>🔧 <strong>Fix {broken} broken link(s):</strong> Update file paths or remove invalid links</li>\n"
        if warning > 0:
            html += f"                <li>⚠️  <strong>Review {warning} warning(s):</strong> Check external URLs for timeouts or redirects</li>\n"
        html += """                <li>📝 Run validation regularly to catch broken links early</li>
                <li>🔄 Use CI/CD integration: Add <code>ansible-doctor link check</code> to your pipeline</li>
            </ul>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""
    return html


def _generate_text_report(results: list[ValidationResult], group_by: str, base_path: Path) -> str:
    """Generate plain text format report."""
    from datetime import datetime

    # Calculate statistics
    total = len(results)
    valid = sum(1 for r in results if r.status == LinkStatus.VALID)
    warning = sum(1 for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT))
    broken = sum(1 for r in results if r.status == LinkStatus.BROKEN)

    report = f"""
{'=' * 60}
LINK VALIDATION REPORT
{'=' * 60}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Base Path: {base_path}

SUMMARY
-------
Valid:    {valid:4d} ({(valid/total*100):5.1f}%)
Warning:  {warning:4d} ({(warning/total*100):5.1f}%)
Broken:   {broken:4d} ({(broken/total*100):5.1f}%)
Total:    {total:4d} (100.0%)

"""

    # Show broken links
    broken_links = [r for r in results if r.status == LinkStatus.BROKEN]
    if broken_links:
        report += f"\nBROKEN LINKS ({len(broken_links)})\n"
        report += "-" * 60 + "\n"
        for result in broken_links:
            report += f"\nFile: {result.source_file}\n"
            report += f"Line: {result.line_number}\n"
            report += f"Target: {result.link.target}\n"
            report += f"Error: {result.error_message}\n"

    # Show warnings
    warning_links = [r for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)]
    if warning_links:
        report += f"\nWARNINGS ({len(warning_links)})\n"
        report += "-" * 60 + "\n"
        for result in warning_links:
            report += f"\nFile: {result.source_file}\n"
            report += f"Line: {result.line_number}\n"
            report += f"Target: {result.link.target}\n"
            report += f"Warning: {result.error_message}\n"

    report += "\n" + "=" * 60 + "\n"
    return report


def _generate_json_report(results: list[ValidationResult], group_by: str) -> str:
    """Generate JSON format report."""
    from datetime import datetime

    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "valid": sum(1 for r in results if r.status == LinkStatus.VALID),
            "warning": sum(
                1 for r in results if r.status in (LinkStatus.TIMEOUT, LinkStatus.REDIRECT)
            ),
            "broken": sum(1 for r in results if r.status == LinkStatus.BROKEN),
        },
        "results": [
            {
                "source_file": str(r.source_file),
                "line_number": r.line_number,
                "target": r.link.target,
                "link_type": r.link.link_type.name,
                "status": r.status.name,
                "is_valid": r.is_valid,
                "error_message": r.error_message,
            }
            for r in results
        ],
    }

    return json.dumps(report, indent=2)


# Export for integration with main CLI
__all__ = ["link_commands", "linkcheck", "linkfix", "linkreport"]
