from dataclasses import dataclass
from typing import Any

from validation_framework.execution.runner import ValidationRunner
from validation_framework.models.result import CheckResult, ValidationIssue
from validation_framework.models.subject import Subject
from validation_framework.suite import ValidationSuite
from validation_framework.validator import Validator


class PrefixValidator(Validator):
    validator_id = "prefix-validator"

    def check(self, value: Any) -> CheckResult:
        if not isinstance(value.name, str):
            return CheckResult.skipped(reason="Provided input should be of type string")

        if not value.name.startswith(self.config.prefix):
            return CheckResult.failed(
                ValidationIssue(code="MISSING_PREFIX", message=f"{value} does not start with valid prefix.")
            )

        return CheckResult.passed()


class AgeValidator(Validator):
    validator_id = "age-validator"

    def check(self, value: Any) -> CheckResult:

        if not isinstance(value.age, int):
            return CheckResult.skipped(reason="Age Input should be int")

        if value.age < self.config.age:
            return CheckResult.failed(
                ValidationIssue(code="INVALID_AGE", message=f"The age limit is {self.config.age}.")
            )

        return CheckResult.passed()


class CustomValidationSuite(ValidationSuite):
    suite_id = "custom-suite-1"
    validators = (PrefixValidator, AgeValidator)


@dataclass
class Config:
    prefix: str = "m_"
    age: int = 18


@dataclass
class Data:
    name: str
    age: int


def main():

    inputs = [
        Subject(subject_id="id-1", value=Data(name="my_invalid_asset", age=19)),
        Subject(subject_id="id-2", value=Data(name="m_valid_asset", age=19)),
        Subject(subject_id="id-3", value=Data(name="my_invalid_asset", age=17)),
    ]

    report = ValidationRunner().run(suite=CustomValidationSuite, subjects=inputs, config=Config())

    for record in report.records:
        print(record)
        print("\n")

    print(report.counts_by_status())
    print(report.state)


if __name__ == "__main__":
    main()
