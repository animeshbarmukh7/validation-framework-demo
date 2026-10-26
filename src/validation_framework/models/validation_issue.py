from dataclasses import dataclass

from validation_framework.models.enums import Severity


@dataclass(frozen=True)
class ValidationIssue:
    """
    A class to represent one single Validation Issue discovered while running
    a validation rule.
    """

    code: str
    message: str
    severity: Severity = Severity.ERROR
    location: str | None = None

    def __post_init__(self) -> None:

        for field in ("code", "message"):
            value = getattr(self, field)

            if not isinstance(value, str):
                raise TypeError(f"{field} must be a string.")

            if not value.strip():
                raise ValueError(f"{field} must not be empty.")

        if not isinstance(self.severity, Severity):
            raise TypeError("severity must be of type Severity.")

        if self.location is not None:
            if not isinstance(self.location, str):
                raise TypeError("location must be a string or None.")

            if not self.location.strip():
                raise ValueError("location must not be empty.")
