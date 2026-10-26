from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

InputT = TypeVar("InputT")


@dataclass(frozen=True)
class Subject(Generic[InputT]):
    """
    This class simply represents an input entity.
    subject_id must be provided while implementing.

    Example usage:

    subject = Subject(
        subject_id="car-123",
        value=Car(name="Taxi"),
    )

    """

    subject_id: str
    value: InputT

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str):
            raise TypeError("subject_id must be a string.")

        if not self.subject_id.strip():
            raise ValueError("subject_id must not be empty.")
