"""Error code definitions and mappings.

This module defines hierarchical error codes for ansible-doctor-enhanced:
- E1xx: Parsing errors (YAML, file reading, etc.)
- E2xx: Validation errors (schema, requirements, etc.)
- E3xx: Generation errors (template rendering, output writing, etc.)
- E4xx: I/O errors (file system, network, etc.)
- W1xx-W4xx: Warnings (same categories)
"""

from enum import Enum
from typing import Dict


class ErrorCode(str, Enum):
    """Hierarchical error codes for ansible-doctor-enhanced."""

    # Parsing Errors (E1xx)
    E100_PARSING_GENERIC = "E100"
    E101_YAML_SYNTAX = "E101"
    E102_YAML_STRUCTURE = "E102"
    E103_INVALID_ENCODING = "E103"
    E104_GALAXY_META_INVALID = "E104"
    E105_TASK_SYNTAX = "E105"
    E106_HANDLER_SYNTAX = "E106"
    E107_VARIABLE_PARSE = "E107"
    E108_ANNOTATION_PARSE = "E108"
    E109_PLAYBOOK_SYNTAX = "E109"

    # Validation Errors (E2xx)
    E200_VALIDATION_GENERIC = "E200"
    E201_REQUIRED_FILE_MISSING = "E201"
    E202_REQUIRED_FIELD_MISSING = "E202"
    E203_INVALID_FIELD_VALUE = "E203"
    E204_VERSION_CONSTRAINT = "E204"
    E205_DEPENDENCY_MISSING = "E205"
    E206_CIRCULAR_DEPENDENCY = "E206"
    E207_INVALID_TAG = "E207"
    E208_INVALID_VARIABLE_NAME = "E208"
    E209_INVALID_PLATFORM = "E209"

    # Generation Errors (E3xx)
    E300_GENERATION_GENERIC = "E300"
    E301_TEMPLATE_NOT_FOUND = "E301"
    E302_TEMPLATE_SYNTAX = "E302"
    E303_TEMPLATE_RENDER = "E303"
    E304_OUTPUT_FORMAT_INVALID = "E304"
    E305_CSS_INJECTION_FAILED = "E305"
    E306_MARKDOWN_CONVERSION = "E306"
    E307_RST_CONVERSION = "E307"
    E308_HTML_GENERATION = "E308"
    E309_VARIANT_RESOLUTION = "E309"

    # I/O Errors (E4xx)
    E400_IO_GENERIC = "E400"
    E401_FILE_NOT_FOUND = "E401"
    E402_PERMISSION_DENIED = "E402"
    E403_DISK_FULL = "E403"
    E404_PATH_TOO_LONG = "E404"
    E405_FILE_LOCKED = "E405"
    E406_DIRECTORY_NOT_FOUND = "E406"
    E407_WRITE_FAILED = "E407"
    E408_READ_FAILED = "E408"
    E409_SYMLINK_LOOP = "E409"

    # Warnings (W1xx-W4xx)
    W100_WARNING_GENERIC = "W100"
    W101_DEPRECATED_SYNTAX = "W101"
    W102_MISSING_DOCUMENTATION = "W102"
    W103_UNDOCUMENTED_VARIABLE = "W103"
    W104_UNUSED_VARIABLE = "W104"
    W105_POTENTIAL_TYPO = "W105"
    W201_MISSING_OPTIONAL_FIELD = "W201"
    W202_DEPRECATED_FIELD = "W202"
    W301_TEMPLATE_WARNING = "W301"
    W401_SLOW_IO_OPERATION = "W401"


class ErrorCategory(str, Enum):
    """Error categories for grouping."""

    PARSING = "parsing"
    VALIDATION = "validation"
    GENERATION = "generation"
    IO = "io"
    UNKNOWN = "unknown"


# Error code to category mapping
ERROR_CATEGORY_MAP: Dict[str, ErrorCategory] = {
    **{
        code.value: ErrorCategory.PARSING
        for code in ErrorCode
        if code.value.startswith(("E1", "W1"))
    },
    **{
        code.value: ErrorCategory.VALIDATION
        for code in ErrorCode
        if code.value.startswith(("E2", "W2"))
    },
    **{
        code.value: ErrorCategory.GENERATION
        for code in ErrorCode
        if code.value.startswith(("E3", "W3"))
    },
    **{code.value: ErrorCategory.IO for code in ErrorCode if code.value.startswith(("E4", "W4"))},
}


def get_category(error_code: str) -> ErrorCategory:
    """Get category for an error code.

    Args:
        error_code: Error code string (e.g., "E101")

    Returns:
        ErrorCategory enum value
    """
    return ERROR_CATEGORY_MAP.get(error_code, ErrorCategory.UNKNOWN)


def is_warning(error_code: str) -> bool:
    """Check if error code is a warning.

    Args:
        error_code: Error code string

    Returns:
        True if code starts with 'W', False otherwise
    """
    return error_code.startswith("W")


def get_severity(error_code: str) -> str:
    """Get severity level for an error code.

    Args:
        error_code: Error code string

    Returns:
        "warning" or "error"
    """
    return "warning" if is_warning(error_code) else "error"
