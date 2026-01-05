"""Correlation ID utilities for tracing operations.

This module provides utilities for generating and managing correlation IDs
that trace execution across nested operations (role → collection → project).
Uses contextvars for thread-safe correlation ID propagation.

Integration with structlog: When set_correlation_id() is called, the correlation_id
is also bound to structlog's context, ensuring it appears in all log entries.
"""

import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable for storing correlation ID in thread-local storage
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID using UUID4.

    Returns:
        UUID4 string in format: "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

    Example:
        >>> cid = generate_correlation_id()
        >>> len(cid)
        36
        >>> cid.count('-')
        4
    """
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context.

    Uses contextvars to store the ID in thread-local storage,
    ensuring proper propagation across async operations and
    nested function calls.

    Also binds the correlation_id to structlog's context so it
    appears in all log entries automatically.

    Args:
        correlation_id: Correlation ID to set (any string format)

    Example:
        >>> set_correlation_id("test-123")
        >>> get_correlation_id()
        'test-123'
    """
    _correlation_id.set(correlation_id)

    # Bind to structlog context for automatic inclusion in all log entries
    try:
        import structlog

        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    except ImportError:
        # structlog not available, skip binding (e.g., in minimal environments)
        pass


def get_correlation_id() -> Optional[str]:
    """Get the correlation ID for the current context.

    Returns:
        Current correlation ID or None if not set

    Example:
        >>> set_correlation_id("abc-123")
        >>> get_correlation_id()
        'abc-123'
    """
    return _correlation_id.get()


def clear_correlation_id() -> None:
    """Clear the correlation ID from the current context.

    Useful for cleanup between operations or in test teardown.

    Example:
        >>> set_correlation_id("test")
        >>> clear_correlation_id()
        >>> get_correlation_id() is None
        True
    """
    _correlation_id.set(None)
