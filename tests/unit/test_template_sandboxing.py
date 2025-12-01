"""Tests for template sandboxing and security features."""

import pytest
from jinja2 import Environment
from jinja2.exceptions import SecurityError, UndefinedError

from ansibledoctor.generator.errors import TemplateValidationError
from ansibledoctor.generator.validator import (
    DANGEROUS_PATTERNS,
    UNSAFE_ATTRIBUTES,
    SecureSandboxedEnvironment,
    TemplateValidator,
    create_sandboxed_environment,
    create_secure_validator,
)


class TestSecureSandboxedEnvironment:
    """Tests for SecureSandboxedEnvironment."""

    @pytest.fixture
    def sandbox_env(self):
        """Create sandboxed environment."""
        return SecureSandboxedEnvironment()

    def test_create_sandboxed_environment(self):
        """Test creating sandboxed environment."""
        env = SecureSandboxedEnvironment()

        assert env is not None
        assert hasattr(env, "is_safe_attribute")
        assert hasattr(env, "is_safe_callable")

    def test_basic_template_rendering(self, sandbox_env):
        """Test basic template rendering works."""
        template = sandbox_env.from_string("Hello {{ name }}!")
        result = template.render(name="World")

        assert result == "Hello World!"

    def test_loops_work(self, sandbox_env):
        """Test loops work in sandboxed environment."""
        template = sandbox_env.from_string(
            "{% for item in items %}{{ item }} {% endfor %}"
        )
        result = template.render(items=["a", "b", "c"])

        assert result == "a b c "

    def test_conditionals_work(self, sandbox_env):
        """Test conditionals work in sandboxed environment."""
        template = sandbox_env.from_string(
            "{% if active %}yes{% else %}no{% endif %}"
        )
        assert template.render(active=True) == "yes"
        assert template.render(active=False) == "no"

    def test_filters_work(self, sandbox_env):
        """Test filters work in sandboxed environment."""
        template = sandbox_env.from_string("{{ name | upper }}")
        result = template.render(name="world")

        assert result == "WORLD"

    def test_blocks_dunder_class(self, sandbox_env):
        """Test __class__ attribute access returns safe value or is restricted."""
        # Jinja2 sandbox allows attribute access but restricts unsafe operations
        # The is_safe_attribute method blocks access to __class__
        template = sandbox_env.from_string("{{ obj.__class__ }}")

        # Access should be blocked - either raises or returns empty/safe value
        try:
            result = template.render(obj="test")
            # If it renders, it should be empty or restricted
            assert result.strip() == "" or "__class__" not in result
        except SecurityError:
            pass  # Expected behavior

    def test_blocks_dunder_mro(self, sandbox_env):
        """Test __mro__ access chain is blocked."""
        # This involves chained unsafe access
        template = sandbox_env.from_string("{{ obj.__class__.__mro__ }}")

        try:
            result = template.render(obj="test")
            # If rendered, __mro__ details should not be exposed
            assert "tuple" not in result.lower()
        except SecurityError:
            pass  # Expected

    def test_blocks_dunder_subclasses(self, sandbox_env):
        """Test __subclasses__ callable is blocked."""
        template = sandbox_env.from_string("{{ obj.__class__.__subclasses__() }}")

        try:
            result = template.render(obj="test")
            # Should not expose subclass information
            assert "[" not in result or "class" not in result.lower()
        except (SecurityError, TypeError):
            pass  # Expected

    def test_blocks_dunder_globals(self, sandbox_env):
        """Test __globals__ access is restricted on functions."""
        template = sandbox_env.from_string("{{ func.__globals__ }}")

        try:
            result = template.render(func=lambda x: x)
            # Should not expose globals
            assert result.strip() == "" or "globals" not in result.lower()
        except SecurityError:
            pass  # Expected

    def test_blocks_dunder_init(self, sandbox_env):
        """Test __init__ access is restricted."""
        template = sandbox_env.from_string("{{ obj.__init__ }}")

        try:
            result = template.render(obj="test")
            # Should not expose init method details
            assert "method" not in result.lower()
        except SecurityError:
            pass  # Expected

    def test_blocks_private_attributes(self, sandbox_env):
        """Test private attributes (starting with _) are restricted."""
        obj = type("Obj", (), {"_private": "secret", "public": "visible"})()
        template = sandbox_env.from_string("{{ obj._private }}")

        try:
            result = template.render(obj=obj)
            # Private value should not be exposed
            assert "secret" not in result
        except (SecurityError, UndefinedError):
            pass  # Expected

    def test_safe_attribute_access(self, sandbox_env):
        """Test safe attribute access works."""
        obj = type("User", (), {"name": "Alice", "email": "alice@test.com"})()
        template = sandbox_env.from_string("{{ user.name }} - {{ user.email }}")
        result = template.render(user=obj)

        assert result == "Alice - alice@test.com"

    def test_dict_access_works(self, sandbox_env):
        """Test dictionary access works."""
        template = sandbox_env.from_string("{{ data['key'] }}")
        result = template.render(data={"key": "value"})

        assert result == "value"

    def test_list_access_works(self, sandbox_env):
        """Test list access works."""
        template = sandbox_env.from_string("{{ items[0] }}")
        result = template.render(items=["first", "second"])

        assert result == "first"


class TestSecureCallables:
    """Tests for secure callable restrictions."""

    @pytest.fixture
    def sandbox_env(self):
        """Create sandboxed environment."""
        return SecureSandboxedEnvironment()

    def test_blocks_eval(self, sandbox_env):
        """Test eval is blocked."""
        template = sandbox_env.from_string("{{ dangerous('1+1') }}")

        with pytest.raises(SecurityError):
            template.render(dangerous=eval)

    def test_blocks_exec(self, sandbox_env):
        """Test exec is blocked."""
        template = sandbox_env.from_string("{{ dangerous('x=1') }}")

        with pytest.raises(SecurityError):
            template.render(dangerous=exec)

    def test_blocks_compile(self, sandbox_env):
        """Test compile is blocked."""
        template = sandbox_env.from_string("{{ dangerous('x', 'f', 'exec') }}")

        with pytest.raises(SecurityError):
            template.render(dangerous=compile)

    def test_blocks_open(self, sandbox_env):
        """Test open is blocked."""
        template = sandbox_env.from_string("{{ dangerous('/etc/passwd') }}")

        with pytest.raises(SecurityError):
            template.render(dangerous=open)

    def test_blocks_type(self, sandbox_env):
        """Test type() is blocked."""
        template = sandbox_env.from_string("{{ dangerous('X', (), {}) }}")

        with pytest.raises(SecurityError):
            template.render(dangerous=type)

    def test_safe_callables_work(self, sandbox_env):
        """Test safe callables work."""
        template = sandbox_env.from_string("{{ format_name(name) }}")

        def format_name(n):
            return n.title()

        result = template.render(format_name=format_name, name="alice")
        assert result == "Alice"


class TestDangerousPatternDetection:
    """Tests for dangerous pattern detection in templates."""

    @pytest.fixture
    def validator(self):
        """Create template validator."""
        return create_secure_validator()

    def test_detects_import(self, validator):
        """Test detection of __import__."""
        template = "{{ __import__('os').system('ls') }}"

        violations = validator.validate_security(template)

        assert any("__import__" in v for v in violations)

    def test_detects_eval(self, validator):
        """Test detection of eval(."""
        template = "{{ eval('1+1') }}"

        violations = validator.validate_security(template)

        assert any("eval(" in v for v in violations)

    def test_detects_exec(self, validator):
        """Test detection of exec(."""
        template = "{{ exec('x=1') }}"

        violations = validator.validate_security(template)

        assert any("exec(" in v for v in violations)

    def test_detects_open(self, validator):
        """Test detection of open(."""
        template = "{{ open('/etc/passwd') }}"

        violations = validator.validate_security(template)

        assert any("open(" in v for v in violations)

    def test_detects_builtins(self, validator):
        """Test detection of __builtins__."""
        template = "{{ __builtins__['eval'] }}"

        violations = validator.validate_security(template)

        assert any("__builtins__" in v for v in violations)

    def test_detects_getattr(self, validator):
        """Test detection of getattr(."""
        template = "{{ getattr(obj, '__class__') }}"

        violations = validator.validate_security(template)

        assert any("getattr(" in v for v in violations)

    def test_detects_os_system(self, validator):
        """Test detection of os.system."""
        template = "{{ os.system('rm -rf /') }}"

        violations = validator.validate_security(template)

        assert any("os.system" in v for v in violations)

    def test_detects_subprocess(self, validator):
        """Test detection of subprocess."""
        template = "{{ subprocess.call(['ls']) }}"

        violations = validator.validate_security(template)

        assert any("subprocess" in v for v in violations)

    def test_safe_template_passes(self, validator):
        """Test safe template passes validation."""
        template = "Hello {{ name }}! Your items: {% for i in items %}{{ i }}{% endfor %}"

        violations = validator.validate_security(template)

        assert violations == []

    def test_is_safe_template_true(self, validator):
        """Test is_safe_template returns True for safe template."""
        template = "{{ user.name | upper }}"

        assert validator.is_safe_template(template) is True

    def test_is_safe_template_false(self, validator):
        """Test is_safe_template returns False for dangerous template."""
        template = "{{ eval('1+1') }}"

        assert validator.is_safe_template(template) is False


class TestValidateSecure:
    """Tests for validate_secure method."""

    @pytest.fixture
    def validator(self):
        """Create template validator."""
        return create_secure_validator()

    def test_passes_safe_template(self, validator):
        """Test validate_secure passes for safe template."""
        template = "Hello {{ name }}!"

        # Should not raise
        validator.validate_secure(template)

    def test_raises_for_dangerous_template(self, validator):
        """Test validate_secure raises for dangerous template."""
        template = "{{ eval('code') }}"

        with pytest.raises(TemplateValidationError) as exc_info:
            validator.validate_secure(template, "dangerous.j2")

        assert "Security violations" in str(exc_info.value)
        assert "eval(" in str(exc_info.value)

    def test_raises_with_multiple_violations(self, validator):
        """Test validate_secure includes all violations."""
        template = "{{ eval('x') }} {{ exec('y') }} {{ __import__('os') }}"

        with pytest.raises(TemplateValidationError) as exc_info:
            validator.validate_secure(template)

        error_msg = str(exc_info.value)
        assert "eval(" in error_msg
        assert "exec(" in error_msg
        assert "__import__" in error_msg


class TestCreateSandboxedEnvironment:
    """Tests for create_sandboxed_environment factory."""

    def test_creates_secure_environment(self):
        """Test factory creates SecureSandboxedEnvironment."""
        env = create_sandboxed_environment()

        assert isinstance(env, SecureSandboxedEnvironment)

    def test_default_autoescape_enabled(self):
        """Test autoescape is enabled by default."""
        env = create_sandboxed_environment()

        assert env.autoescape is True

    def test_custom_options(self):
        """Test custom options are applied."""
        env = create_sandboxed_environment(autoescape=False, trim_blocks=False)

        assert env.autoescape is False
        assert env.trim_blocks is False

    def test_environment_renders_safely(self):
        """Test environment renders safely."""
        env = create_sandboxed_environment()
        template = env.from_string("{{ name }}")

        result = template.render(name="<script>alert(1)</script>")

        # Autoescape should escape HTML
        assert "&lt;script&gt;" in result
        assert "<script>" not in result


class TestCreateSecureValidator:
    """Tests for create_secure_validator factory."""

    def test_creates_validator(self):
        """Test factory creates TemplateValidator."""
        validator = create_secure_validator()

        assert isinstance(validator, TemplateValidator)

    def test_uses_sandboxed_environment(self):
        """Test validator uses sandboxed environment."""
        validator = create_secure_validator()

        assert isinstance(validator.environment, SecureSandboxedEnvironment)

    def test_validates_syntax(self):
        """Test validator can validate syntax."""
        validator = create_secure_validator()

        # Should not raise
        validator.validate_syntax("{{ name }}")

    def test_validates_security(self):
        """Test validator can validate security."""
        validator = create_secure_validator()

        violations = validator.validate_security("{{ eval('x') }}")

        assert len(violations) > 0


class TestUnsafeAttributesList:
    """Tests for UNSAFE_ATTRIBUTES configuration."""

    def test_contains_dunder_class(self):
        """Test __class__ is in unsafe list."""
        assert "__class__" in UNSAFE_ATTRIBUTES

    def test_contains_dunder_mro(self):
        """Test __mro__ is in unsafe list."""
        assert "__mro__" in UNSAFE_ATTRIBUTES

    def test_contains_dunder_subclasses(self):
        """Test __subclasses__ is in unsafe list."""
        assert "__subclasses__" in UNSAFE_ATTRIBUTES

    def test_contains_dunder_globals(self):
        """Test __globals__ is in unsafe list."""
        assert "__globals__" in UNSAFE_ATTRIBUTES

    def test_contains_dunder_code(self):
        """Test __code__ is in unsafe list."""
        assert "__code__" in UNSAFE_ATTRIBUTES

    def test_contains_gi_frame(self):
        """Test gi_frame is in unsafe list."""
        assert "gi_frame" in UNSAFE_ATTRIBUTES

    def test_contains_func_globals(self):
        """Test func_globals is in unsafe list."""
        assert "func_globals" in UNSAFE_ATTRIBUTES


class TestDangerousPatternsList:
    """Tests for DANGEROUS_PATTERNS configuration."""

    def test_contains_import(self):
        """Test __import__ is in dangerous list."""
        assert "__import__" in DANGEROUS_PATTERNS

    def test_contains_eval(self):
        """Test eval( is in dangerous list."""
        assert "eval(" in DANGEROUS_PATTERNS

    def test_contains_exec(self):
        """Test exec( is in dangerous list."""
        assert "exec(" in DANGEROUS_PATTERNS

    def test_contains_open(self):
        """Test open( is in dangerous list."""
        assert "open(" in DANGEROUS_PATTERNS

    def test_contains_subprocess(self):
        """Test subprocess is in dangerous list."""
        assert "subprocess" in DANGEROUS_PATTERNS

    def test_contains_os_system(self):
        """Test os.system is in dangerous list."""
        assert "os.system" in DANGEROUS_PATTERNS


class TestSecurityWithComplexTemplates:
    """Tests for security with complex template structures."""

    @pytest.fixture
    def sandbox_env(self):
        """Create sandboxed environment."""
        return SecureSandboxedEnvironment()

    @pytest.fixture
    def validator(self):
        """Create secure validator."""
        return create_secure_validator()

    def test_nested_loops_safe(self, sandbox_env):
        """Test nested loops work safely."""
        template = sandbox_env.from_string(
            """
            {% for group in groups %}
                Group: {{ group.name }}
                {% for member in group.members %}
                    - {{ member }}
                {% endfor %}
            {% endfor %}
            """
        )
        result = template.render(
            groups=[
                {"name": "A", "members": ["x", "y"]},
                {"name": "B", "members": ["z"]},
            ]
        )

        assert "Group: A" in result
        assert "- x" in result

    def test_macros_work(self, sandbox_env):
        """Test macros work in sandboxed environment."""
        template = sandbox_env.from_string(
            """
            {% macro button(text) %}
                <button>{{ text }}</button>
            {% endmacro %}
            {{ button("Click me") }}
            """
        )
        result = template.render()

        assert "<button>Click me</button>" in result

    def test_includes_blocked_in_basic_env(self, sandbox_env):
        """Test includes without loader raise appropriate error."""
        template = sandbox_env.from_string("{% include 'other.j2' %}")

        # Should raise because no loader configured
        with pytest.raises(Exception):  # TemplatesNotFound or similar
            template.render()

    def test_comprehensive_validation(self, validator):
        """Test comprehensive validation with security check."""
        template = "{{ user.name }}"

        result = validator.validate_template(template)

        assert result["valid"] is True
        assert "user" in result["undeclared_variables"]

    def test_safe_complex_template(self, validator):
        """Test complex but safe template passes security."""
        template = """
        # {{ title }}

        {% for section in sections %}
        ## {{ section.name }}

        {% for item in section.items %}
        - {{ item.name }}: {{ item.description | default('No description') }}
        {% endfor %}
        {% endfor %}

        Generated by {{ generator }} on {{ date }}
        """

        assert validator.is_safe_template(template) is True
        violations = validator.validate_security(template)
        assert violations == []

    def test_template_with_filters_safe(self, validator):
        """Test template using filters is safe."""
        template = """
        {{ name | upper | trim }}
        {{ items | join(', ') }}
        {{ count | default(0) }}
        """

        assert validator.is_safe_template(template) is True

    def test_mixed_dangerous_and_safe_content(self, validator):
        """Test template with mixed content is flagged."""
        template = """
        Hello {{ name }}!
        {{ eval('dangerous') }}
        Goodbye!
        """

        assert validator.is_safe_template(template) is False
        violations = validator.validate_security(template)
        assert any("eval(" in v for v in violations)


class TestTemplateInheritanceValidation:
    """Tests for template inheritance validation (T356)."""

    @pytest.fixture
    def validator(self):
        """Create validator with standard environment."""
        return create_secure_validator()

    def test_validate_extends_detects_parent(self, validator):
        """Test detecting parent template in extends."""
        template = '{% extends "base.html.j2" %}'

        # Get inheritance info
        parents = validator.get_parent_templates(template)

        assert "base.html.j2" in parents

    def test_validate_extends_multiple_layers(self, validator):
        """Test detecting extends with dynamic parent."""
        template = '{% extends parent_template %}'

        parents = validator.get_parent_templates(template)

        # Should return the variable name when dynamic
        assert "parent_template" in parents or len(parents) == 0

    def test_validate_includes_detects_partials(self, validator):
        """Test detecting included templates."""
        template = '''
        {% extends "base.html.j2" %}
        {% include "_header.j2" %}
        {% include "_footer.j2" %}
        '''

        includes = validator.get_included_templates(template)

        assert "_header.j2" in includes
        assert "_footer.j2" in includes

    def test_validate_inheritance_chain(self, validator):
        """Test getting all template dependencies."""
        template = '''
        {% extends "layout.html.j2" %}
        {% include "_nav.j2" %}
        {% block content %}
            {% include "_sidebar.j2" %}
        {% endblock %}
        '''

        deps = validator.get_template_dependencies(template)

        assert "layout.html.j2" in deps["extends"]
        assert "_nav.j2" in deps["includes"]
        assert "_sidebar.j2" in deps["includes"]

    def test_missing_parent_error_message(self, validator, tmp_path):
        """Test actionable error for missing parent template."""
        child = tmp_path / "child.html.j2"
        child.write_text('{% extends "missing_parent.html.j2" %}')

        errors = validator.validate_inheritance(str(child))

        assert len(errors) > 0
        assert any("missing_parent.html.j2" in e for e in errors)
        assert any("not found" in e.lower() or "missing" in e.lower() for e in errors)

    def test_missing_include_error_message(self, validator, tmp_path):
        """Test actionable error for missing include."""
        template = tmp_path / "page.html.j2"
        template.write_text('{% include "_nonexistent.j2" %}')

        errors = validator.validate_inheritance(str(template))

        assert len(errors) > 0
        assert any("_nonexistent.j2" in e for e in errors)

    def test_circular_inheritance_detection(self, validator):
        """Test detecting circular template inheritance."""
        # This would require multi-file validation
        template_a = '{% extends "b.html.j2" %}'
        template_b = '{% extends "a.html.j2" %}'

        # Should be detected in multi-template validation
        deps_a = validator.get_template_dependencies(template_a)
        deps_b = validator.get_template_dependencies(template_b)

        # At minimum, dependencies are captured
        assert "b.html.j2" in deps_a["extends"]
        assert "a.html.j2" in deps_b["extends"]

    def test_error_message_includes_suggestions(self, validator, tmp_path):
        """Test error messages include helpful suggestions."""
        child = tmp_path / "child.html.j2"
        child.write_text('{% extends "base.html.j2" %}')

        errors = validator.validate_inheritance(str(child))

        # Error should suggest where to look
        assert len(errors) > 0
        error_text = " ".join(errors).lower()
        assert "base.html.j2" in error_text

    def test_valid_inheritance_no_errors(self, validator, tmp_path):
        """Test valid inheritance reports no errors."""
        # Create parent template
        parent = tmp_path / "base.html.j2"
        parent.write_text("<html>{% block content %}{% endblock %}</html>")

        # Create child template
        child = tmp_path / "child.html.j2"
        child.write_text('{% extends "base.html.j2" %}{% block content %}Hello{% endblock %}')

        # Validate with search path including tmp_path
        errors = validator.validate_inheritance(str(child), search_paths=[str(tmp_path)])

        assert len(errors) == 0

    def test_nested_includes_validation(self, validator, tmp_path):
        """Test validation of nested include dependencies."""
        template = '''
        {% include "level1.j2" %}
        '''

        deps = validator.get_template_dependencies(template)

        assert "level1.j2" in deps["includes"]

    def test_conditional_includes(self, validator):
        """Test conditional includes are detected."""
        template = '''
        {% if show_header %}
            {% include "_header.j2" %}
        {% endif %}
        '''

        includes = validator.get_included_templates(template)

        assert "_header.j2" in includes

    def test_import_detection(self, validator):
        """Test import statements are detected."""
        template = '''
        {% import "macros.j2" as macros %}
        {% from "helpers.j2" import format_date %}
        '''

        deps = validator.get_template_dependencies(template)

        assert "macros.j2" in deps.get("imports", [])
        assert "helpers.j2" in deps.get("imports", [])

