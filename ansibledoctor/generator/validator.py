"""Template validation for Jinja2 templates with sandboxing security."""

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, TemplateSyntaxError, meta
from jinja2.sandbox import SandboxedEnvironment

from ansibledoctor.generator.errors import TemplateValidationError

# Dangerous constructs that should be blocked in user templates
DANGEROUS_PATTERNS = [
    "__import__",
    "eval(",
    "exec(",
    "compile(",
    "open(",
    "__builtins__",
    "__globals__",
    "__class__",
    "__mro__",
    "__subclasses__",
    "os.system",
    "subprocess",
    "getattr(",
    "setattr(",
    "delattr(",
]

# Attributes that should not be accessible in sandboxed templates
UNSAFE_ATTRIBUTES = frozenset(
    [
        "__class__",
        "__mro__",
        "__subclasses__",
        "__bases__",
        "__init__",
        "__globals__",
        "__code__",
        "__builtins__",
        "__reduce__",
        "__reduce_ex__",
        "func_globals",
        "func_code",
        "gi_frame",
        "gi_code",
        "cr_frame",
        "cr_code",
    ]
)


class SecureSandboxedEnvironment(SandboxedEnvironment):
    """Sandboxed Jinja2 environment with additional security restrictions.

    Extends Jinja2's SandboxedEnvironment with:
    - Blocked access to dangerous attributes
    - Restricted callable objects
    - Prevention of class introspection
    """

    def is_safe_attribute(self, obj: Any, attr: str, value: Any) -> bool:
        """Check if attribute access is safe.

        Args:
            obj: Object being accessed
            attr: Attribute name
            value: Attribute value

        Returns:
            True if attribute access is safe
        """
        if attr in UNSAFE_ATTRIBUTES:
            return False
        if attr.startswith("_"):
            return False
        return super().is_safe_attribute(obj, attr, value)

    def is_safe_callable(self, obj: Any) -> bool:
        """Check if callable is safe to call.

        Args:
            obj: Callable object

        Returns:
            True if callable is safe
        """
        # Prevent calling dangerous builtins
        dangerous_callables = (type, eval, exec, compile, open, __import__)
        try:
            if obj in dangerous_callables:
                return False
        except TypeError:
            # Some objects can't be compared
            pass
        return super().is_safe_callable(obj)


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
                str(template_path), f"Template file not found: {template_path}"
            )

        if not path.is_file():
            raise TemplateValidationError(str(template_path), f"Not a file: {template_path}")

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
                result["errors"].append(f"Missing required variables: {', '.join(sorted(missing))}")

        return result

    def validate_security(
        self,
        template_source: str,
        template_name: str = "template",
    ) -> list[str]:
        """Check template for dangerous patterns.

        Args:
            template_source: Template source code
            template_name: Template identifier

        Returns:
            List of security violations found
        """
        violations = []

        for pattern in DANGEROUS_PATTERNS:
            if pattern in template_source:
                violations.append(f"Dangerous pattern '{pattern}' found in {template_name}")

        return violations

    def is_safe_template(self, template_source: str) -> bool:
        """Check if template is safe to render.

        Args:
            template_source: Template source code

        Returns:
            True if template passes security checks
        """
        violations = self.validate_security(template_source)
        return len(violations) == 0

    def validate_secure(
        self,
        template_source: str,
        template_name: str = "template",
    ) -> None:
        """Validate template security, raising on violations.

        Args:
            template_source: Template source code
            template_name: Template identifier

        Raises:
            TemplateValidationError: If security violations found
        """
        violations = self.validate_security(template_source)
        if violations:
            error_details = "; ".join(violations)
            raise TemplateValidationError(template_name, f"Security violations: {error_details}")

    def get_parent_templates(self, template_source: str) -> list[str]:
        """Extract parent template names from extends statements.

        Args:
            template_source: Template source code

        Returns:
            List of parent template names
        """
        parents = []
        # Match {% extends "template.j2" %} or {% extends 'template.j2' %}
        extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
        matches = re.findall(extends_pattern, template_source)
        parents.extend(matches)

        # Also match {% extends variable %}
        variable_pattern = r"{%\s*extends\s+(\w+)\s*%}"
        var_matches = re.findall(variable_pattern, template_source)
        parents.extend(var_matches)

        return parents

    def get_included_templates(self, template_source: str) -> list[str]:
        """Extract included template names from include statements.

        Args:
            template_source: Template source code

        Returns:
            List of included template names
        """
        includes = []
        # Match {% include "template.j2" %} or {% include 'template.j2' %}
        include_pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
        matches = re.findall(include_pattern, template_source)
        includes.extend(matches)

        return includes

    def get_template_dependencies(self, template_source: str) -> dict[str, list[str]]:
        """Get all template dependencies including extends, includes, and imports.

        Args:
            template_source: Template source code

        Returns:
            Dictionary with keys: extends, includes, imports
        """
        deps: dict[str, list[str]] = {
            "extends": [],
            "includes": [],
            "imports": [],
        }

        # Get extends
        deps["extends"] = self.get_parent_templates(template_source)

        # Get includes
        deps["includes"] = self.get_included_templates(template_source)

        # Get imports: {% import "macros.j2" as x %} and {% from "helpers.j2" import y %}
        import_pattern = r'{%\s*import\s+["\']([^"\']+)["\']\s+as\s+\w+\s*%}'
        from_pattern = r'{%\s*from\s+["\']([^"\']+)["\']\s+import\s+'

        import_matches = re.findall(import_pattern, template_source)
        from_matches = re.findall(from_pattern, template_source)

        deps["imports"] = list(set(import_matches + from_matches))

        return deps

    def validate_inheritance(
        self,
        template_path: str | Path,
        search_paths: list[str] | None = None,
    ) -> list[str]:
        """Validate template inheritance chain for missing parents or includes.

        Args:
            template_path: Path to template file
            search_paths: Optional list of directories to search for templates

        Returns:
            List of error messages for missing dependencies
        """
        errors = []
        path = Path(template_path)

        if not path.exists():
            errors.append(f"Template file not found: {template_path}")
            return errors

        template_source = path.read_text(encoding="utf-8")
        deps = self.get_template_dependencies(template_source)

        # Default search paths include template's directory
        paths_to_search = [path.parent]
        if search_paths:
            paths_to_search.extend(Path(p) for p in search_paths)

        # Check extends
        for parent in deps["extends"]:
            found = False
            for search_path in paths_to_search:
                if (search_path / parent).exists():
                    found = True
                    break
            if not found:
                errors.append(
                    f"Parent template '{parent}' not found. "
                    f"Searched in: {', '.join(str(p) for p in paths_to_search)}. "
                    f"Create '{parent}' or check the template search path."
                )

        # Check includes
        for include in deps["includes"]:
            found = False
            for search_path in paths_to_search:
                if (search_path / include).exists():
                    found = True
                    break
            if not found:
                errors.append(
                    f"Included template '{include}' not found. "
                    f"Searched in: {', '.join(str(p) for p in paths_to_search)}. "
                    f"Create '{include}' or update the include path."
                )

        # Check imports
        for imp in deps["imports"]:
            found = False
            for search_path in paths_to_search:
                if (search_path / imp).exists():
                    found = True
                    break
            if not found:
                errors.append(
                    f"Imported template '{imp}' not found. "
                    f"Searched in: {', '.join(str(p) for p in paths_to_search)}. "
                    f"Create '{imp}' or update the import path."
                )

        return errors


def create_sandboxed_environment(**options: Any) -> SecureSandboxedEnvironment:
    """Create a secure sandboxed Jinja2 environment.

    Creates a SandboxedEnvironment with restricted attribute access
    and blocked dangerous operations.

    Args:
        **options: Additional Jinja2 environment options

    Returns:
        Configured SecureSandboxedEnvironment

    Example:
        >>> env = create_sandboxed_environment()
        >>> validator = TemplateValidator(env)
    """
    default_options = {
        "autoescape": True,
        "trim_blocks": True,
        "lstrip_blocks": True,
    }
    default_options.update(options)
    return SecureSandboxedEnvironment(**default_options)


def create_secure_validator(**env_options: Any) -> TemplateValidator:
    """Create a TemplateValidator with secure sandboxed environment.

    Convenience function to create a fully configured secure validator.

    Args:
        **env_options: Options for the sandboxed environment

    Returns:
        TemplateValidator with secure environment

    Example:
        >>> validator = create_secure_validator()
        >>> validator.validate_secure("{{ user.name }}")
    """
    env = create_sandboxed_environment(**env_options)
    return TemplateValidator(env)
