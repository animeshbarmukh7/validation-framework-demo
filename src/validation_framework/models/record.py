from __future__ import annotations

from dataclasses import dataclass

from validation_framework.models.result import CheckResult


@dataclass(frozen=True)
class ValidationRecord:
    """
    This class defines a single ValidationRecord entity.
    A validation record tracks single run and holds a resul and other data.
    """

    record_id: str
    run_id: str
    invocation_id: str

    validator_id: str
    validator_version: str
    suite_path: tuple[str, ...]

    subject_id: str
    result: CheckResult

    def __post_init__(self) -> None:
        for name in ("record_id", "run_id", "invocation_id", "validator_id", "validator_version", "subject_id"):
            value = getattr(self, name)

            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string.")

            if not value.strip():
                raise ValueError(f"{name} must not be empty.")

        if not isinstance(self.suite_path, tuple):
            raise TypeError("suite_path must be a tuple.")

        for part in self.suite_path:
            if not isinstance(part, str):
                raise TypeError("Each suite path element must be a string.")

            if not part.strip():
                raise ValueError("Suite path elements must not be empty.")

        if not isinstance(self.result, CheckResult):
            raise TypeError("result must be a CheckResult.")
