from enum import StrEnum, auto
from typing import Callable


class CommandBindingEvent(StrEnum):
    ENABLED_CHANGED = auto()


type CommandBindingListener = Callable[[CommandBindingEvent], None]


class CommandBinding:
    def __init__(self, tracker, validation):
        self.tracker = tracker
        self.validation = validation
        self.listeners: list[CommandBindingListener] = []
        self._was_enabled = self.is_enabled

        tracker.listeners.append(self._on_state_changed)

    @property
    def is_enabled(self) -> bool:
        return (
                self.tracker.is_editing
                and self.tracker.is_dirty
                and self.validation.is_valid
        )

    def _on_state_changed(self, event):
        was_enabled = self._was_enabled
        self._was_enabled = self.is_enabled

        if self._was_enabled != was_enabled:
            self._notify(CommandBindingEvent.ENABLED_CHANGED)

    def _notify(self, event: CommandBindingEvent) -> None:
        for listener in self.listeners:
            listener(event)
