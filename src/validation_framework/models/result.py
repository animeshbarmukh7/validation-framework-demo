from __future__ import annotations

from dataclasses import dataclass

from validation_framework.models.enums import ResultStatus
from validation_framework.models.validation_issue import ValidationIssue


@dataclass(frozen=True)
class ExecutionError:
    exception_type: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.exception_type, str):
            raise TypeError("exception_type must be a string.")

        if not self.exception_type.strip():
            raise ValueError("exception_type must not be empty.")


@dataclass(frozen=True)
class CheckResult:
    """
    This class represents validaiton check outupt state.
    A ValidationRecord holds instance of CheckResult.
    """

    status: ResultStatus
    issues: tuple[ValidationIssue, ...] = ()
    reason: str | None = None
    error: ExecutionError | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, ResultStatus):
            raise TypeError("status must be a ResultStatus.")

        if not isinstance(self.issues, tuple):
            raise TypeError("issues must be a tuple.")

        if not all(isinstance(issue, ValidationIssue) for issue in self.issues):
            raise TypeError("Every issue must be a ValidationIssue.")

        if self.reason is not None:
            if not isinstance(self.reason, str):
                raise TypeError("reason must be a string or None.")

            if not self.reason.strip():
                raise ValueError("reason must not be empty.")

        if self.error is not None and not isinstance(self.error, ExecutionError):
            raise TypeError("error must be an ExecutionError or None.")

        self._validate_result_state()

    def _validate_result_state(self) -> None:

        if self.status is ResultStatus.PASSED:
            if self.issues or self.reason is not None or self.error is not None:
                raise ValueError("Validation status PASSED can't contain issues, reason, or an error.")

        elif self.status is ResultStatus.FAILED:
            if not self.issues:
                raise ValueError("Validation status FAILED requires at least one issue.")

            if self.reason is not None or self.error is not None:
                raise ValueError("Validation status FAILED can't contain a reason or execution error.")

        elif self.status is ResultStatus.SKIPPED:
            if self.reason is None:
                raise ValueError("Validation status SKIPPED requires a reason.")

            if self.issues or self.error is not None:
                raise ValueError("Validation status SKIPPED can't contain issues or an execution error.")

        elif self.status is ResultStatus.ERROR:
            if self.error is None:
                raise ValueError("Validation status ERROR requires an execution error.")

            if self.issues or self.reason is not None:
                raise ValueError("Validation status ERROR can't contain issues or a skip reason.")

        else:
            raise ValueError(f"Unsupported result status: {self.status}")

    @classmethod
    def passed(cls) -> CheckResult:
        return cls(status=ResultStatus.PASSED)

    @classmethod
    def failed(cls, *issues: ValidationIssue) -> CheckResult:
        return cls(status=ResultStatus.FAILED, issues=issues)

    @classmethod
    def skipped(cls, reason: str) -> CheckResult:
        return cls(status=ResultStatus.SKIPPED, reason=reason)

    @classmethod
    def execution_error(cls, error: ExecutionError) -> CheckResult:
        return cls(status=ResultStatus.ERROR, error=error)
