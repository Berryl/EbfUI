from typing import Callable
from typing import Protocol

from ebf_ui.state.state_events import StateTrackerEvent
from ebf_ui.state.state_tracker import StateTracker


# region protocols
class ValidationViolation(Protocol):
    @property
    def field_name(self) -> str: ...

    @property
    def ui_error_message(self) -> str: ...


class ValidationState(Protocol):
    @property
    def is_valid(self) -> bool: ...

    @property
    def violations(self) -> list[ValidationViolation]: ...


class ErrorTarget(Protocol):
    def set_error(self, message: str | None) -> None: ...


# endregion


class ValidationBinding:
    def __init__(self, validate: Callable[[], ValidationState]):
        self.validate = validate
        self.result: ValidationState | None = None

    @property
    def is_valid(self) -> bool:
        return self.result is not None and self.result.is_valid

    @property
    def violations(self) -> list[ValidationViolation]:
        if self.result is None:
            return []
        return self.result.violations

    @property
    def ui_error_messages(self) -> list[str]:
        return [v.ui_error_message for v in self.violations]

    def update(self) -> None:
        self.result = self.validate()


def bind_validation(tracker: StateTracker, validation: ValidationBinding) -> None:
    def listener(event: StateTrackerEvent) -> None:
        if event in {StateTrackerEvent.BEGIN_EDIT, StateTrackerEvent.UPDATE_EDIT}:
            validation.update()

    tracker.listeners.append(listener)
