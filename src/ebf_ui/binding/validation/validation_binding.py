from typing import Any, Callable
from typing import Protocol


class ValidationViolation(Protocol):
    @property
    def ui_error_message(self) -> str: ...


class ValidationResultLike(Protocol):
    @property
    def is_valid(self) -> bool: ...

    @property
    def violations(self) -> list[ValidationViolation]: ...


class ValidationBinding:
    def __init__(self, validate: Callable[[], ValidationResultLike]):
        self.validate = validate
        self.result: ValidationResultLike | None = None

    @property
    def is_valid(self) -> bool:
        return self.result is not None and self.result.is_valid

    @property
    def violations(self) -> list[Any]:
        if self.result is None:
            return []
        return list(self.result.violations)

    @property
    def ui_error_messages(self) -> list[str]:
        return [v.ui_error_message for v in self.violations]

    def update(self) -> None:
        self.result = self.validate()
