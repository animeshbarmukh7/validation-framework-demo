from __future__ import annotations

from typing import Any

from validation_framework.validator import Validator


class ValidationSuite:
    """
    This class represents a collection of validators and nested suites.

    class CustomValidationSuite(ValidationSuite):
        suite_id = "custom-suite-1"
        validators = (PrefixValidator, AgeValidator)
    """

    suite_id: str
    validators: tuple[type[Validator[Any, Any]], ...] = ()
    suites: tuple[type[ValidationSuite], ...] = ()
