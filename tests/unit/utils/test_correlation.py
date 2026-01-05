"""Unit tests for correlation ID utilities.

Tests correlation ID generation, propagation via contextvars, and custom ID acceptance.
Following TDD RED phase - write tests first, then implement.
"""

import re
import uuid

import pytest

from ansibledoctor.utils.correlation import (
    clear_correlation_id,
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
)


class TestCorrelationIDGeneration:
    """T044: Unit tests for correlation ID generation."""

    def test_generate_correlation_id_returns_uuid4_format(self):
        """Verify generated correlation ID matches UUID4 format."""
        # Act
        correlation_id = generate_correlation_id()
        
        # Assert
        # UUID4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        uuid4_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        assert uuid4_pattern.match(correlation_id), f"Invalid UUID4 format: {correlation_id}"
    
    def test_generate_correlation_id_is_unique(self):
        """Verify each generated correlation ID is unique."""
        # Act
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()
        id3 = generate_correlation_id()
        
        # Assert
        assert id1 != id2
        assert id2 != id3
        assert id1 != id3
    
    def test_generated_id_can_be_parsed_as_uuid(self):
        """Verify generated ID is a valid UUID object."""
        # Act
        correlation_id = generate_correlation_id()
        
        # Assert - Should not raise ValueError
        parsed_uuid = uuid.UUID(correlation_id)
        assert parsed_uuid.version == 4  # UUID4


class TestCorrelationIDPropagation:
    """T045: Unit tests for correlation ID propagation via contextvars."""

    def test_set_and_get_correlation_id(self):
        """Verify set_correlation_id stores value retrievable by get_correlation_id."""
        # Arrange
        test_id = "test-correlation-123"
        
        # Act
        set_correlation_id(test_id)
        retrieved_id = get_correlation_id()
        
        # Assert
        assert retrieved_id == test_id
    
    def test_get_correlation_id_returns_none_when_not_set(self):
        """Verify get_correlation_id returns None when no ID is set."""
        # Arrange
        clear_correlation_id()
        
        # Act
        result = get_correlation_id()
        
        # Assert
        assert result is None
    
    def test_clear_correlation_id_removes_stored_value(self):
        """Verify clear_correlation_id removes the stored correlation ID."""
        # Arrange
        set_correlation_id("test-123")
        assert get_correlation_id() == "test-123"
        
        # Act
        clear_correlation_id()
        
        # Assert
        assert get_correlation_id() is None
    
    def test_correlation_id_isolated_between_contexts(self):
        """Verify correlation IDs are isolated in different execution contexts."""
        # Note: contextvars provides automatic isolation
        # This test verifies sequential operations don't interfere
        
        # Arrange & Act
        set_correlation_id("context-1")
        id1 = get_correlation_id()
        
        clear_correlation_id()
        id2 = get_correlation_id()
        
        set_correlation_id("context-2")
        id3 = get_correlation_id()
        
        # Assert
        assert id1 == "context-1"
        assert id2 is None
        assert id3 == "context-2"


class TestCustomCorrelationID:
    """T046: Unit tests for custom correlation ID acceptance."""

    def test_set_correlation_id_accepts_custom_format(self):
        """Verify custom correlation ID formats are accepted."""
        # Arrange
        custom_ids = [
            "custom-trace-id-123",
            "x-request-id:abc-def-ghi",
            "trace_parent:00-abc123-def456-01",
            "simple-123",
        ]
        
        # Act & Assert
        for custom_id in custom_ids:
            set_correlation_id(custom_id)
            assert get_correlation_id() == custom_id
    
    def test_set_correlation_id_accepts_uuid_string(self):
        """Verify UUID strings from external systems are accepted."""
        # Arrange
        external_uuid = "550e8400-e29b-41d4-a716-446655440000"
        
        # Act
        set_correlation_id(external_uuid)
        retrieved = get_correlation_id()
        
        # Assert
        assert retrieved == external_uuid
    
    def test_set_correlation_id_overwrites_previous_value(self):
        """Verify setting a new correlation ID overwrites the previous one."""
        # Arrange
        set_correlation_id("first-id")
        assert get_correlation_id() == "first-id"
        
        # Act
        set_correlation_id("second-id")
        
        # Assert
        assert get_correlation_id() == "second-id"
        assert get_correlation_id() != "first-id"
