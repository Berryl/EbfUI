from typing import Any

from ebf_core.reflection.attr_reflector import AttributeReflector
from ebf_core.reflection.attr_selection import select_attrs
from ebf_core.reflection.snapshot import capture, get_changes, has_changes
from ebf_ui.state.state_events import StateTrackerEvent, StateTrackerListener


class StateTracker:
    def __init__(
        self,
        instance: object,
        requested_attrs: list[str] | None = None,
        exclusions: list[str] | None = None,
    ):
        self.instance = instance
        self.attrs = select_attrs(instance, requested_attrs, exclusions)
        self.original: dict | None = None
        self.current: dict | None = None
        self.listeners: list[StateTrackerListener] = []

    @property
    def is_dirty(self) -> bool:
        if self.original is None or self.current is None:
            return False
        return has_changes(self.original, self.current)

    @property
    def is_editing(self) -> bool:
        return self.original is not None

    @property
    def changes(self) -> dict:
        if self.original is None or self.current is None:
            return {}
        return get_changes(self.original, self.current)

    def begin_edit(self) -> None:
        if self.is_editing:
            raise RuntimeError("begin_edit called while already editing")

        self.original = self._capture()
        self.current = self.original.copy()  # type: ignore[union-attr]
        self._notify(StateTrackerEvent.BEGIN_EDIT)

    def update_edit(self) -> None:
        if not self.is_editing:
            raise RuntimeError("update_edit called before begin_edit")

        was_dirty = self.is_dirty
        self.current = self._capture()
        if self.is_dirty != was_dirty:
            self._notify(StateTrackerEvent.DIRTY_CHANGED)
        self._notify(StateTrackerEvent.UPDATE_EDIT)

    def end_edit(self) -> None:
        self._ensure_editing("end")
        self._reset()
        self._notify(StateTrackerEvent.END_EDIT)

    def cancel_edit(self) -> None:
        self._ensure_editing("cancel")
        self._restore()
        self._reset()
        self._notify(StateTrackerEvent.CANCEL_EDIT)

    def _capture(self) -> dict[str, Any]:
        reflector = AttributeReflector(self.instance)
        return capture(reflector, self.attrs)

    def _ensure_editing(self, action: str) -> None:
        if not self.is_editing:
            raise RuntimeError(f"{action}_edit called before begin_edit")

    def _notify(self, event: StateTrackerEvent) -> None:
        for listener in self.listeners:
            listener(event)

    def _reset(self) -> None:
        self.original = None
        self.current = None

    def _restore(self) -> None:
        reflector = AttributeReflector(self.instance)
        assert self.original is not None, "Original state cannot be None during restore"
        for attr, value in self.original.items():
            reflector.set_value(attr, value)
