from enum import StrEnum, auto
from typing import Callable

from ebf_ui.binding.validation.validation_binding import ValidationState
from ebf_ui.state.state_events import StateTrackerEvent
from ebf_ui.state.state_tracker import StateTracker


class CommandBindingEvent(StrEnum):
    ENABLED_CHANGED = auto()
    EXECUTED = auto()


type CommandBindingListener = Callable[[CommandBindingEvent], None]


class CommandBinding:
    def __init__(
        self, tracker: StateTracker, validation: ValidationState, execute: Callable[[], None]
    ):
        self.tracker = tracker
        self.validation = validation
        self._execute = execute
        self.listeners: list[CommandBindingListener] = []
        self._was_enabled = self.is_enabled

        tracker.listeners.append(self._on_state_changed)

    def execute(self) -> None:
        if not self.is_enabled:
            return

        self._execute()
        self._notify(CommandBindingEvent.EXECUTED)

    @property
    def is_enabled(self) -> bool:
        return self.tracker.is_editing and self.tracker.is_dirty and self.validation.is_valid

    def _on_state_changed(self, _: StateTrackerEvent) -> None:
        was_enabled = self._was_enabled
        self._was_enabled = self.is_enabled

        if self._was_enabled != was_enabled:
            self._notify(CommandBindingEvent.ENABLED_CHANGED)

    def _notify(self, event: CommandBindingEvent) -> None:
        for listener in self.listeners:
            listener(event)
