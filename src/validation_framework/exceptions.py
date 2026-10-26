from __future__ import annotations


class ValidationFrameworkError(Exception):
    """Base exception for framework errors."""


class InvalidSuiteError(ValidationFrameworkError):
    """A suite cannot be prepared for execution."""


class SuiteCycleError(InvalidSuiteError):
    """Nested suites contain a cycle."""


class InvalidValidatorError(ValidationFrameworkError):
    """A validator has invalid execution metadata."""
