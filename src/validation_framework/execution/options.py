from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunOptions:
    """
    Run options. Use this to stop validation execution for critical validator.
    """

    fail_fast: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.fail_fast, bool):
            raise TypeError("fail_fast must be a bool.")
