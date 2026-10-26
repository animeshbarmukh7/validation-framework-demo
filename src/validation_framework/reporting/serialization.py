import json
from typing import Any

from validation_framework.reporting.report import ValidationReport


def report_to_dict(report: ValidationReport) -> dict[str, Any]:
    records = []

    for record in report.records:
        result = record.result

        issues = []

        for issue in result.issues:
            issue_data = {
                "code": issue.code,
                "message": issue.message,
                "severity": issue.severity.value,
                "location": issue.location,
            }
            issues.append(issue_data)

        error_data = None

        if result.error is not None:
            error_data = {
                "exception_type": result.error.exception_type,
                "message": result.error.message,
            }

        result_data = {
            "status": result.status.value,
            "issues": issues,
            "reason": result.reason,
            "error": error_data,
        }

        record_data = {
            "record_id": record.record_id,
            "run_id": record.run_id,
            "invocation_id": record.invocation_id,
            "validator_id": record.validator_id,
            "validator_version": record.validator_version,
            "suite_path": list(record.suite_path),
            "subject_id": record.subject_id,
            "result": result_data,
        }
        records.append(record_data)

    report_data = {
        "schema_version": "1",
        "run_id": report.run_id,
        "state": report.state.value,
        "has_failures": report.has_failures,
        "is_successful": report.is_successful,
        "termination_reason": report.termination_reason,
        "records": records,
    }

    return report_data


def report_to_json(report: ValidationReport, *, indent: int | None = 2) -> str:
    report_data = report_to_dict(report)

    json_text = json.dumps(
        report_data,
        indent=indent,
        ensure_ascii=False,
        allow_nan=False,
    )

    return json_text
