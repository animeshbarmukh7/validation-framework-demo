from __future__ import annotations

import logging
from uuid import uuid4

from validation_framework.execution.options import RunOptions
from validation_framework.execution.plan import ExecutionPlan, PlannedValidation
from validation_framework.models.enums import ResultStatus, RunState
from validation_framework.models.record import ValidationRecord
from validation_framework.models.result import CheckResult, ExecutionError
from validation_framework.models.subject import Subject
from validation_framework.reporting.report import ValidationReport
from validation_framework.suite import ValidationSuite

logger = logging.getLogger(__name__)


class ValidationRunner:
    """
    This class can be considered as an entry-point. This class is responsible for
    executing the validation suite for given inputs and creating detailed execution record.

    subjects = (
        Subject(subject_id="car-1", value=Car(name="CAR_Taxi")),
        Subject(subject_id="car-2", value=Car(name="Taxi")),
    )

    report = ValidationRunner().run(
        subjects=subjects,
        suite=suite,
        config=Config()
    )

    print(report.state)
    print(report.counts_by_status())
    """

    def run(
        self,
        subjects: list[Subject],
        suite: type[ValidationSuite],
        config: object,
        options: RunOptions | None = None,
    ) -> ValidationReport:

        if options is None:
            options = RunOptions()
        elif not isinstance(options, RunOptions):
            raise TypeError("options must be a RunOptions or None.")

        plan = ExecutionPlan.from_suite(suite_class=suite, config=config)

        run_id = uuid4().hex
        records: list[ValidationRecord] = []
        seen_subject_ids: set[str] = set()

        def finish(state: RunState, reason: str | None = None) -> ValidationReport:
            return ValidationReport(run_id=run_id, state=state, records=tuple(records), termination_reason=reason)

        for subject in subjects:
            if not isinstance(subject, Subject):
                return finish(RunState.ABORTED, "Every input must be a Subject instance.")

            if subject.subject_id in seen_subject_ids:
                return finish(RunState.ABORTED, f"Duplicate subject_id: {subject.subject_id}")

            seen_subject_ids.add(subject.subject_id)

            for invocation in plan.invocations:
                record = self._execute(run_id=run_id, subject=subject, invocation=invocation)
                records.append(record)

                if options.fail_fast and record.result.status in (ResultStatus.FAILED, ResultStatus.ERROR):
                    return finish(RunState.ABORTED, f"Fail-fast triggered by {record.record_id}.")

        return finish(RunState.COMPLETED)

    def _execute(self, run_id: str, subject: Subject, invocation: PlannedValidation) -> ValidationRecord:

        try:
            result = invocation.validator.check(subject.value)

            if not isinstance(result, CheckResult):
                raise TypeError("Validator.check() must return a CheckResult.")

        except Exception as exc:
            logger.exception(
                "Validator %s failed while processing subject %s.", invocation.validator_id, subject.subject_id
            )

            result = CheckResult.execution_error(ExecutionError(exception_type=type(exc).__name__, message=str(exc)))

        return ValidationRecord(
            record_id=uuid4().hex,
            run_id=run_id,
            invocation_id=invocation.invocation_id,
            validator_id=invocation.validator_id,
            validator_version=invocation.validator_version,
            suite_path=invocation.suite_path,
            subject_id=subject.subject_id,
            result=result,
        )
