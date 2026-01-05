"""SARIF 2.1.0 format generator for IDE integration.

SARIF (Static Analysis Results Interchange Format) is a standard format
for static analysis tool output that integrates with IDEs like VS Code,
IntelliJ IDEA, and PyCharm.
"""

from pathlib import Path
from typing import Dict, List
from ansibledoctor.models.error_report import ErrorReport, ErrorEntry


class SARIFFormatter:
    """Formats error reports as SARIF 2.1.0 for IDE integration."""
    
    SARIF_VERSION = "2.1.0"
    SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
    
    def __init__(self, tool_name: str = "ansible-doctor-enhanced", tool_version: str = "0.1.0"):
        """Initialize SARIF formatter.
        
        Args:
            tool_name: Name of the analysis tool
            tool_version: Version of the analysis tool
        """
        self.tool_name = tool_name
        self.tool_version = tool_version
    
    def format(self, error_report: ErrorReport, working_dir: Path = None) -> dict:
        """Convert ErrorReport to SARIF 2.1.0 format.
        
        Args:
            error_report: Error report to convert
            working_dir: Working directory for relative path resolution
        
        Returns:
            SARIF document as dictionary
        """
        working_dir = working_dir or Path.cwd()
        
        # Combine errors and warnings
        all_issues = error_report.errors + error_report.warnings
        
        # Build SARIF document
        sarif_doc = {
            "$schema": self.SARIF_SCHEMA,
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "version": self.tool_version,
                            "informationUri": "https://github.com/thegeeklab/ansible-doctor",
                            "rules": self._build_rules(all_issues),
                        }
                    },
                    "results": self._build_results(all_issues, working_dir),
                    "columnKind": "utf16CodeUnits",
                }
            ]
        }
        
        # Add invocation metadata
        sarif_doc["runs"][0]["invocations"] = [
            {
                "executionSuccessful": error_report.error_count == 0,
                "endTimeUtc": error_report.timestamp.isoformat() + "Z",
                "properties": {
                    "correlationId": error_report.correlation_id,
                    "errorCount": error_report.error_count,
                    "warningCount": error_report.warning_count,
                    "partialSuccess": error_report.partial_success,
                }
            }
        ]
        
        return sarif_doc
    
    def _build_rules(self, issues: List[ErrorEntry]) -> List[dict]:
        """Build SARIF rules from unique error codes.
        
        Args:
            issues: List of all error entries
        
        Returns:
            List of SARIF rule objects
        """
        # Get unique error codes
        unique_codes = set(issue.code for issue in issues)
        
        rules = []
        for code in sorted(unique_codes):
            # Find first issue with this code to get details
            example = next(issue for issue in issues if issue.code == code)
            
            rule = {
                "id": code,
                "name": f"AnsibleDoctor{code}",
                "shortDescription": {
                    "text": self._get_rule_short_description(code, example.category)
                },
                "fullDescription": {
                    "text": self._get_rule_full_description(example)
                },
                "defaultConfiguration": {
                    "level": self._get_sarif_level(example.severity)
                },
                "properties": {
                    "category": example.category,
                }
            }
            
            if example.doc_url:
                rule["helpUri"] = example.doc_url
            
            rules.append(rule)
        
        return rules
    
    def _build_results(self, issues: List[ErrorEntry], working_dir: Path) -> List[dict]:
        """Build SARIF results from error entries.
        
        Args:
            issues: List of all error entries
            working_dir: Working directory for path resolution
        
        Returns:
            List of SARIF result objects
        """
        results = []
        
        for issue in issues:
            result = {
                "ruleId": issue.code,
                "level": self._get_sarif_level(issue.severity),
                "message": {
                    "text": issue.message
                },
            }
            
            # Add location if file path is available
            if issue.file_path:
                # Convert to URI
                file_path = Path(issue.file_path)
                if not file_path.is_absolute():
                    file_path = working_dir / file_path
                
                # Resolve to absolute path for URI conversion
                try:
                    file_path = file_path.resolve()
                except (OSError, ValueError):
                    # If resolution fails, use as-is
                    pass
                
                location = {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path.as_uri(),
                            "uriBaseId": "%SRCROOT%"
                        },
                        "region": {}
                    }
                }
                
                # Add line and column if available
                if issue.line:
                    location["physicalLocation"]["region"]["startLine"] = issue.line
                    if issue.column:
                        location["physicalLocation"]["region"]["startColumn"] = issue.column
                
                result["locations"] = [location]
            
            # Add recovery suggestion as fix
            if issue.recovery_suggestion:
                result["fixes"] = [
                    {
                        "description": {
                            "text": issue.recovery_suggestion
                        }
                    }
                ]
            
            results.append(result)
        
        return results
    
    @staticmethod
    def _get_sarif_level(severity: str) -> str:
        """Convert severity to SARIF level.
        
        Args:
            severity: Severity string ("error" or "warning")
        
        Returns:
            SARIF level ("error", "warning", or "note")
        """
        return {
            "error": "error",
            "warning": "warning",
        }.get(severity, "note")
    
    @staticmethod
    def _get_rule_short_description(code: str, category: str) -> str:
        """Generate short description for a rule.
        
        Args:
            code: Error code
            category: Error category
        
        Returns:
            Short description text
        """
        category_names = {
            "parsing": "Parsing Error",
            "validation": "Validation Error",
            "generation": "Generation Error",
            "io": "I/O Error",
        }
        return f"{category_names.get(category, 'Error')}: {code}"
    
    @staticmethod
    def _get_rule_full_description(issue: ErrorEntry) -> str:
        """Generate full description for a rule.
        
        Args:
            issue: Example error entry
        
        Returns:
            Full description text
        """
        desc = issue.message
        if issue.recovery_suggestion:
            desc += f" Suggestion: {issue.recovery_suggestion}"
        return desc
