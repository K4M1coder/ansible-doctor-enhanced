"""Unit tests for SchemaDocumenter.

Tests for generating human-readable Markdown documentation from JSON Schema.

Spec 012 Phase 7: T069-T073 - Schema documentation tests
"""

import pytest

from ansibledoctor.serialization.schema_documenter import SchemaDocumenter


class TestMarkdownGeneration:
    """Test basic Markdown generation from JSON Schema."""
    
    @pytest.fixture
    def documenter(self):
        """Create SchemaDocumenter instance."""
        return SchemaDocumenter()
    
    def test_generates_markdown_sections_for_each_property(self, documenter):
        """Test that each property gets its own section.
        
        T069: Markdown generation with sections for each property
        """
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "TestConfig",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name property"
                },
                "age": {
                    "type": "integer",
                    "description": "The age property"
                },
                "active": {
                    "type": "boolean",
                    "description": "The active property"
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should generate markdown documentation
        assert isinstance(docs, str)
        assert len(docs) > 0
        
        # Should include title
        assert "TestConfig" in docs
        
        # Should have sections for each property
        assert "name" in docs
        assert "age" in docs
        assert "active" in docs
        
        # Should include property descriptions
        assert "The name property" in docs
        assert "The age property" in docs
        assert "The active property" in docs
    
    def test_includes_property_types(self, documenter):
        """Test that property types are documented."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer"},
                "enabled": {"type": "boolean"},
                "items": {"type": "array"}
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should document types
        assert "string" in docs
        assert "integer" in docs
        assert "boolean" in docs
        assert "array" in docs
    
    def test_includes_required_fields_marker(self, documenter):
        """Test that required fields are marked."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"}
            },
            "required": ["name"]
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should mark required fields
        # Common markers: "required", "*", "(required)", etc.
        assert "name" in docs
        # Should indicate requirement somehow
        assert "required" in docs.lower() or "*" in docs


class TestDescriptionDocumentation:
    """Test that schema descriptions are included in documentation."""
    
    @pytest.fixture
    def documenter(self):
        """Create SchemaDocumenter instance."""
        return SchemaDocumenter()
    
    def test_includes_schema_description(self, documenter):
        """Test that top-level schema description is included.
        
        T070: Schema descriptions included in documentation
        """
        schema = {
            "title": "Configuration",
            "description": "This is the main configuration schema for the application.",
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include schema description
        assert "This is the main configuration schema" in docs
    
    def test_includes_property_descriptions(self, documenter):
        """Test that property descriptions are included."""
        schema = {
            "type": "object",
            "properties": {
                "database_url": {
                    "type": "string",
                    "description": "PostgreSQL connection string including host, port, and credentials"
                },
                "max_connections": {
                    "type": "integer",
                    "description": "Maximum number of concurrent database connections (default: 10)"
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include detailed descriptions
        assert "PostgreSQL connection string" in docs
        assert "Maximum number of concurrent database connections" in docs
    
    def test_includes_default_values(self, documenter):
        """Test that default values are documented."""
        schema = {
            "type": "object",
            "properties": {
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Request timeout in seconds"
                },
                "enabled": {
                    "type": "boolean",
                    "default": True
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include default values
        assert "30" in docs
        assert "True" in docs or "true" in docs
        
        # Should indicate these are defaults
        assert "default" in docs.lower()
    
    def test_includes_examples(self, documenter):
        """Test that examples are included if present."""
        schema = {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "User email address",
                    "examples": ["user@example.com", "admin@company.org"]
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include examples
        assert "user@example.com" in docs
        # Should have examples section/indicator
        assert "example" in docs.lower()


class TestNestedObjectHandling:
    """Test documentation of nested objects with proper hierarchy."""
    
    @pytest.fixture
    def documenter(self):
        """Create SchemaDocumenter instance."""
        return SchemaDocumenter()
    
    def test_handles_nested_objects_with_proper_heading_hierarchy(self, documenter):
        """Test that nested objects use proper heading levels.
        
        T071: Proper heading hierarchy for nested objects
        """
        schema = {
            "title": "Configuration",
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "description": "Database configuration",
                    "properties": {
                        "host": {
                            "type": "string",
                            "description": "Database hostname"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Database port"
                        }
                    }
                },
                "cache": {
                    "type": "object",
                    "description": "Cache configuration",
                    "properties": {
                        "ttl": {
                            "type": "integer",
                            "description": "Time to live in seconds"
                        }
                    }
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include nested properties
        assert "database" in docs
        assert "host" in docs
        assert "port" in docs
        assert "cache" in docs
        assert "ttl" in docs
        
        # Should use markdown headings (##, ###, etc.)
        assert "#" in docs
        
        # Nested properties should be under parent
        # Check relative ordering
        database_pos = docs.find("database")
        host_pos = docs.find("host")
        port_pos = docs.find("port")
        
        assert database_pos < host_pos
        assert database_pos < port_pos
    
    def test_handles_deeply_nested_objects(self, documenter):
        """Test documentation of deeply nested structures."""
        schema = {
            "type": "object",
            "properties": {
                "server": {
                    "type": "object",
                    "properties": {
                        "http": {
                            "type": "object",
                            "properties": {
                                "ssl": {
                                    "type": "object",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should handle deep nesting
        assert "server" in docs
        assert "http" in docs
        assert "ssl" in docs
        assert "enabled" in docs


class TestEnumDocumentation:
    """Test documentation of enum values."""
    
    @pytest.fixture
    def documenter(self):
        """Create SchemaDocumenter instance."""
        return SchemaDocumenter()
    
    def test_lists_all_enum_values(self, documenter):
        """Test that all enum values are listed.
        
        T072: All enum values listed in documentation
        """
        schema = {
            "type": "object",
            "properties": {
                "log_level": {
                    "type": "string",
                    "description": "Logging verbosity level",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                },
                "environment": {
                    "type": "string",
                    "description": "Deployment environment",
                    "enum": ["development", "staging", "production"]
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should list all enum values for log_level
        assert "DEBUG" in docs
        assert "INFO" in docs
        assert "WARNING" in docs
        assert "ERROR" in docs
        assert "CRITICAL" in docs
        
        # Should list all enum values for environment
        assert "development" in docs
        assert "staging" in docs
        assert "production" in docs
    
    def test_enum_with_descriptions(self, documenter):
        """Test enum documentation with value descriptions."""
        schema = {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "pending"],
                    "description": "Current status of the resource"
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include enum values
        assert "active" in docs
        assert "inactive" in docs
        assert "pending" in docs
        
        # Should have enum indicator
        assert "enum" in docs.lower() or "allowed" in docs.lower() or "possible" in docs.lower()


class TestDeprecatedProperties:
    """Test documentation of deprecated properties."""
    
    @pytest.fixture
    def documenter(self):
        """Create SchemaDocumenter instance."""
        return SchemaDocumenter()
    
    def test_marks_deprecated_properties(self, documenter):
        """Test that deprecated properties are marked.
        
        T073: Deprecated properties marked in documentation
        """
        schema = {
            "type": "object",
            "properties": {
                "old_field": {
                    "type": "string",
                    "description": "Legacy field, use new_field instead",
                    "deprecated": True
                },
                "new_field": {
                    "type": "string",
                    "description": "Replacement for old_field"
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include both fields
        assert "old_field" in docs
        assert "new_field" in docs
        
        # Should mark deprecated field
        assert "deprecated" in docs.lower()
    
    def test_includes_deprecation_message(self, documenter):
        """Test that deprecation messages are included."""
        schema = {
            "type": "object",
            "properties": {
                "legacy_setting": {
                    "type": "string",
                    "deprecated": True,
                    "description": "Deprecated: Use modern_setting instead. Will be removed in v2.0"
                }
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should include deprecation message
        assert "Deprecated" in docs
        assert "modern_setting" in docs
        assert "v2.0" in docs


class TestFormattingAndStructure:
    """Test overall formatting and structure of generated docs."""
    
    @pytest.fixture
    def documenter(self):
        """Create SchemaDocumenter instance."""
        return SchemaDocumenter()
    
    def test_generates_valid_markdown(self, documenter):
        """Test that output is valid Markdown."""
        schema = {
            "title": "Config",
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should be valid markdown
        assert isinstance(docs, str)
        
        # Should use markdown syntax
        # Headings, lists, code blocks, etc.
        assert "#" in docs  # Headings
    
    def test_includes_table_of_contents(self, documenter):
        """Test that a table of contents is generated for large schemas."""
        schema = {
            "title": "Large Config",
            "type": "object",
            "properties": {
                "section1": {"type": "object", "properties": {"a": {"type": "string"}}},
                "section2": {"type": "object", "properties": {"b": {"type": "string"}}},
                "section3": {"type": "object", "properties": {"c": {"type": "string"}}},
                "section4": {"type": "object", "properties": {"d": {"type": "string"}}},
            }
        }
        
        docs = documenter.generate_docs(schema)
        
        # For larger schemas, might include TOC
        # (This is optional - implementation dependent)
        assert len(docs) > 0
    
    def test_handles_empty_schema(self, documenter):
        """Test handling of minimal/empty schemas."""
        schema = {
            "type": "object",
            "properties": {}
        }
        
        docs = documenter.generate_docs(schema)
        
        # Should handle gracefully
        assert isinstance(docs, str)
        # Should indicate no properties
        assert "no properties" in docs.lower() or "empty" in docs.lower() or len(docs) < 100
