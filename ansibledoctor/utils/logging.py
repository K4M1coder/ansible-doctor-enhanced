"""
Structured logging infrastructure for Ansible Doctor Enhanced.

Implements Constitution Article V (Observability & Structured Logging) with:
- JSON formatting for machine readability
- Contextual information in all log entries
- Correlation IDs for operation tracing
- Performance metrics collection
"""

import logging
import sys
import uuid
from typing import Any, Optional

import structlog


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    correlation_id: Optional[str] = None,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output logs in JSON format; otherwise human-readable
        correlation_id: Optional correlation ID for request tracing; auto-generated if not provided

    Examples:
        >>> setup_logging(level="DEBUG", json_output=True)
        >>> logger = structlog.get_logger()
        >>> logger.info("parsing_started", role_name="my-role", file_path="/path/to/role")
    """
    # Generate correlation ID if not provided
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,  # Logs to stderr per Constitution Article II
        level=getattr(logging, level.upper()),
    )

    # Select processors based on output format
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_output:
        # Machine-readable JSON output
        processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ]
        )
    else:
        # Human-readable console output with colors
        processors.extend(
            [
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Bind correlation ID to context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance with the given name.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Configured structlog logger instance

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("task_completed", task_id="T001", duration_ms=150.5)
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind additional context variables to all subsequent log entries.

    Useful for adding request-scoped or operation-scoped context like
    role_name, file_path, or operation_type.

    Args:
        **kwargs: Key-value pairs to bind to logging context

    Examples:
        >>> bind_context(role_name="my-role", operation="parse_metadata")
        >>> logger = get_logger(__name__)
        >>> logger.info("metadata_extracted")  # Will include role_name and operation in log
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """
    Clear all bound context variables.

    Typically called at the end of an operation to prevent context leaking
    into subsequent operations.

    Examples:
        >>> bind_context(role_name="my-role")
        >>> # ... do work ...
        >>> clear_context()
    """
    structlog.contextvars.clear_contextvars()
