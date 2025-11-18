"""Template validation for Jinja2 templates."""
from pathlib import Path
from typing import Any

from jinja2 import Environment, TemplateSyntaxError, meta

from ansibledoctor.generator.errors import TemplateValidationError


class TemplateValidator:
    """Validator for Jinja2 templates.
    
    Validates template syntax, required blocks, and variable usage.
    """

    def __init__(self, environment: Environment):
        """Initialize validator with Jinja2 environment.
        
        Args:
            environment: Configured Jinja2 Environment
        """
        self.environment = environment

    def validate_syntax(self, template_source: str, template_name: str = "template") -> None:
        """Validate Jinja2 template syntax.
        
        Args:
            template_source: Template source code
            template_name: Template identifier for error messages
            
        Raises:
            TemplateValidationError: If syntax is invalid
        """
        try:
            self.environment.parse(template_source)
        except TemplateSyntaxError as e:
            error_details = f"Syntax error at line {e.lineno}: {e.message}"
            raise TemplateValidationError(template_name, error_details) from e

    def validate_file(self, template_path: str | Path) -> None:
        """Validate template file.
        
        Args:
            template_path: Path to template file
            
        Raises:
            TemplateValidationError: If validation fails
        """
        path = Path(template_path)
        
        if not path.exists():
            raise TemplateValidationError(
                str(template_path),
                f"Template file not found: {template_path}"
            )
        
        if not path.is_file():
            raise TemplateValidationError(
                str(template_path),
                f"Not a file: {template_path}"
            )
        
        # Read and validate syntax
        template_source = path.read_text(encoding="utf-8")
        self.validate_syntax(template_source, template_name=str(template_path))

    def get_undeclared_variables(self, template_source: str) -> set[str]:
        """Get variables used in template but not declared.
        
        Args:
            template_source: Template source code
            
        Returns:
            Set of undeclared variable names
        """
        try:
            ast = self.environment.parse(template_source)
            return meta.find_undeclared_variables(ast)
        except TemplateSyntaxError:
            return set()

    def validate_required_variables(
        self,
        template_source: str,
        required_vars: set[str],
        template_name: str = "template",
    ) -> None:
        """Validate that template uses all required variables.
        
        Args:
            template_source: Template source code
            required_vars: Set of required variable names
            template_name: Template identifier for error messages
            
        Raises:
            TemplateValidationError: If required variables are missing
        """
        undeclared = self.get_undeclared_variables(template_source)
        missing = required_vars - undeclared
        
        if missing:
            error_details = f"Missing required variables: {', '.join(sorted(missing))}"
            raise TemplateValidationError(template_name, error_details)

    def check_variable_usage(
        self,
        template_source: str,
        context: dict[str, Any],
    ) -> list[str]:
        """Check which context variables are not used in template.
        
        Args:
            template_source: Template source code
            context: Template context dictionary
            
        Returns:
            List of unused variable names
        """
        undeclared = self.get_undeclared_variables(template_source)
        unused = set(context.keys()) - undeclared
        return sorted(unused)

    def validate_template(
        self,
        template_source: str,
        template_name: str = "template",
        required_vars: set[str] | None = None,
    ) -> dict[str, Any]:
        """Comprehensive template validation.
        
        Args:
            template_source: Template source code
            template_name: Template identifier
            required_vars: Optional set of required variables
            
        Returns:
            Validation result dictionary with:
            - valid: bool
            - errors: list of error messages
            - warnings: list of warning messages
            - undeclared_variables: set of used variables
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "undeclared_variables": set(),
        }
        
        # Validate syntax
        try:
            self.validate_syntax(template_source, template_name)
        except TemplateValidationError as e:
            result["valid"] = False
            result["errors"].append(str(e))
            return result
        
        # Get undeclared variables
        undeclared = self.get_undeclared_variables(template_source)
        result["undeclared_variables"] = undeclared
        
        # Check required variables
        if required_vars:
            missing = required_vars - undeclared
            if missing:
                result["valid"] = False
                result["errors"].append(
                    f"Missing required variables: {', '.join(sorted(missing))}"
                )
        
        return result
