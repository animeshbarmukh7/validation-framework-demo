from enum import Enum


class ResultStatus(Enum):
    "Result state for a validation check"

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class Severity(Enum):
    """Severity of an individual finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RunState(Enum):
    """Completion state of an entire validation run."""

    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABORTED = "aborted"
