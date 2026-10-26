from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from validation_framework.exceptions import InvalidSuiteError, InvalidValidatorError, SuiteCycleError
from validation_framework.suite import ValidationSuite
from validation_framework.validator import Validator


@dataclass(frozen=True)
class PlannedValidation:
    """
    This class represents an entity to hold a ready to be executed validation occurrence.
    """

    invocation_id: str
    validator_id: str
    validator_version: str
    suite_path: tuple[str, ...]

    validator: Validator[Any, Any]


@dataclass(frozen=True)
class ExecutionPlan:
    """
    This class supports prepping and planning execution of validators.
    This class is responsible for resolving suites and nested suites to collect all executable
    validators.
    """

    invocations: tuple[PlannedValidation, ...]

    @classmethod
    def from_suite(cls, suite_class: type[ValidationSuite], config: object) -> ExecutionPlan:
        # First collect and validate the suite declarations.
        declarations = []
        active_suites: set[type[ValidationSuite]] = set()

        def visit(current: type[ValidationSuite], parent_path: tuple[str, ...], occurrence_path: str) -> None:
            if not isinstance(current, type) or not issubclass(current, ValidationSuite):
                raise InvalidSuiteError("Suites must be ValidationSuite subclasses.")

            if current in active_suites:
                raise SuiteCycleError(f"Suite cycle detected at {current.__name__}.")

            suite_id = getattr(current, "suite_id", None)

            if not isinstance(suite_id, str) or not suite_id.strip():
                raise InvalidSuiteError(f"{current.__name__}.suite_id must be a nonempty string.")

            validators = current.validators
            suites = current.suites

            if not isinstance(validators, tuple):
                raise InvalidSuiteError("validators must be a tuple of validator classes.")

            if not isinstance(suites, tuple):
                raise InvalidSuiteError("suites must be a tuple of suite classes.")

            suite_path = parent_path + (suite_id,)
            active_suites.add(current)

            try:
                for index, validator_class in enumerate(validators):
                    if not isinstance(validator_class, type) or not issubclass(validator_class, Validator):
                        raise InvalidValidatorError("Each validator must be a Validator subclass.")

                    validator_id = getattr(validator_class, "validator_id", None)
                    version = getattr(validator_class, "version", None)

                    for name, value in (("validator_id", validator_id), ("version", version)):
                        if not isinstance(value, str) or not value.strip():
                            raise InvalidValidatorError(
                                f"{validator_class.__name__}.{name} must be a non-empty string."
                            )

                    declarations.append(
                        (f"{occurrence_path}/validators/{index}", validator_id, version, suite_path, validator_class)
                    )

                for index, child in enumerate(suites):
                    visit(child, suite_path, f"{occurrence_path}/suites/{index}")
            finally:
                active_suites.remove(current)

        visit(suite_class, (), "root")

        # Then construct fresh validator instances for this run.
        invocations = []

        for invocation_id, validator_id, version, suite_path, validator_class in declarations:
            try:
                validator = validator_class(config)
            except Exception as exc:
                raise InvalidValidatorError(f"Could not initialize {validator_id} at {invocation_id}: {exc}") from exc

            invocations.append(
                PlannedValidation(
                    invocation_id=invocation_id,
                    validator_id=validator_id,
                    validator_version=version,
                    suite_path=suite_path,
                    validator=validator,
                )
            )

        return cls(invocations=tuple(invocations))
