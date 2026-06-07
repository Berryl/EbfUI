from collections.abc import Iterable


class FormBinding:
    def __init__(self, bindings: Iterable[object] = ()):
        # this holds strong references to prevent Qt signal-bound bindings from being GC'd
        self.bindings = list(bindings)

    def add(self, binding: object) -> None:
        self.bindings.append(binding)

    def refresh(self) -> None:
        for binding in self.bindings:
            refresh = getattr(binding, "refresh", None)
            if callable(refresh):
                refresh()
