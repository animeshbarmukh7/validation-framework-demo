"""Generic contract for a single validation rule."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from .models.result import CheckResult


InputT = TypeVar("InputT")
ConfigT = TypeVar("ConfigT")


class Validator(ABC, Generic[InputT, ConfigT]):
    """
    An abstract base class to represent a single validation check/rule that can be applied to an input.

    Every validator Subclass should inherit this abstract base class in order to validate an input data.
    Subclass should also define a non-empty validator_id. SubClass should define clear Input types and configuration requirements.
    This class expects implementation of def check() method which returns an instance of CheckResult.

    """

    validator_id: str
    version: str = "1"

    def __init__(self, config: ConfigT) -> None:
        """
        Retain the caller's configuration without copying or interpreting it.

        Subclass validators should reject invalid configuration during construction.
        """
        self._config = config

    @property
    def config(self) -> ConfigT:
        """Returns the supplied configuration setting."""
        return self._config

    @abstractmethod
    def check(self, value: InputT) -> CheckResult:
        """
        This method should implement actual logic for validation check and return a complete result.
        Return PASSED or FAILED for an evaluated rule, or SKIPPED with a
        reason when the input is unsupported or the rule is inapplicable.

        Example:
            for skipping:
            return CheckResult.skipped(reason="Reason")

            for Fail case:
            return CheckResult.failed(ValidationIssue(code="MISSING_PREFIX", message=f"Reason"))

            for success case:
            return CheckResult.passed()

        """
        raise NotImplementedError
