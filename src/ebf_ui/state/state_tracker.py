from ebf_core.reflection.attr_reflector import AttributeReflector
from ebf_core.reflection.attr_selection import select_attrs
from ebf_core.reflection.snapshot import capture, has_changes, get_changes


class StateTracker:
    def __init__(self, instance: object):
        self.instance = instance
        self.original: dict | None = None
        self.current: dict | None = None

    @property
    def is_dirty(self) -> bool:
        if self.original is None or self.current is None:
            return False
        return has_changes(self.original, self.current)

    @property
    def changes(self) -> dict:
        if self.original is None or self.current is None:
            return {}
        return get_changes(self.original, self.current)

    def begin_edit(self) -> None:
        self.original = self._capture()
        self.current = self.original.copy()

    def update_edit(self) -> None:
        self.current = self._capture()

    def end_edit(self) -> None:
        self.original = None
        self.current = None

    def _capture(self) -> dict:
        reflector = AttributeReflector(self.instance)
        attrs = select_attrs(self.instance)
        return capture(reflector, attrs)
