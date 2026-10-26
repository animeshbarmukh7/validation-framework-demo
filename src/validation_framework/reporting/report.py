from __future__ import annotations

from dataclasses import dataclass

from validation_framework.models.enums import ResultStatus, RunState
from validation_framework.models.record import ValidationRecord


@dataclass(frozen=True)
class ValidationReport:
    """
    This class represents a complete validaiton report for single validation run.
    """

    run_id: str
    state: RunState
    records: tuple[ValidationRecord, ...]
    termination_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str):
            raise TypeError("run_id must be a string.")

        if not self.run_id.strip():
            raise ValueError("run_id must not be empty.")

        if not isinstance(self.state, RunState):
            raise TypeError("state must be a RunState.")

        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple.")

        record_ids: set[str] = set()

        for record in self.records:
            if not isinstance(record, ValidationRecord):
                raise TypeError("Every record must be a ValidationRecord.")

            if record.run_id != self.run_id:
                raise ValueError("Record belongs to a different run.")

            if record.record_id in record_ids:
                raise ValueError("Duplicate record_id.")

            record_ids.add(record.record_id)

        if self.state is RunState.COMPLETED:
            if self.termination_reason is not None:
                raise ValueError("A completed run cannot have a termination reason.")
        else:
            if not isinstance(self.termination_reason, str):
                raise TypeError("An incomplete run requires a termination reason.")

            if not self.termination_reason.strip():
                raise ValueError("termination_reason must not be empty.")

    def for_subject(self, subject_id: str) -> tuple[ValidationRecord, ...]:
        return tuple(record for record in self.records if record.subject_id == subject_id)

    def for_validator(self, validator_id: str) -> tuple[ValidationRecord, ...]:
        return tuple(record for record in self.records if record.validator_id == validator_id)

    def with_status(self, status: ResultStatus) -> tuple[ValidationRecord, ...]:
        return tuple(record for record in self.records if record.result.status is status)

    def counts_by_status(self) -> dict[ResultStatus, int]:
        counts = {status: 0 for status in ResultStatus}

        for record in self.records:
            counts[record.result.status] += 1

        return counts

    @property
    def has_failures(self) -> bool:
        """Whether any check failed or encountered an execution error."""
        for record in self.records:
            if record.result.status in (
                ResultStatus.FAILED,
                ResultStatus.ERROR,
            ):
                return True

        return False

    @property
    def is_successful(self) -> bool:
        """Whether the run completed without failed or errored checks."""
        return self.state is RunState.COMPLETED and not self.has_failures
