from typing import Callable, Any

from PySide6.QtWidgets import QLineEdit

from ebf_ui.state.state_tracker import StateTracker


class LineEditBinding:
    """Two-way binding between a QLineEdit and a property in the model."""

    def __init__(
            self,
            line_edit: QLineEdit,
            tracker: StateTracker,
            get_value: Callable[[], Any],
            set_value: Callable[[str], None],
            sync_ui: Callable[[], None] | None = None,
    ):
        self.line_edit = line_edit
        self.tracker = tracker
        self.get_value = get_value
        self.set_value = set_value
        self.sync_ui = sync_ui
        self._is_refreshing = False

        line_edit.textChanged.connect(self._on_text_changed)

        self._push_model_to_view()
        self._sync()

    def refresh(self) -> None:
        """Call this when the model changes from outside the line edit."""
        self._push_model_to_view()
        self._sync()

    def _on_text_changed(self, text: str) -> None:
        """Called when the user types in the line edit."""
        if self._is_refreshing:
            return
        self.set_value(text)
        self.tracker.update_edit()
        self._sync()

    def _push_model_to_view(self) -> None:
        """Push the current model value to the QLineEdit."""
        current_value = self.get_value()
        text_to_set = current_value if current_value is not None else ""

        if self.line_edit.text() != text_to_set:
            self._is_refreshing = True
            try:
                self.line_edit.setText(text_to_set)
            finally:
                self._is_refreshing = False

    def _sync(self):
        """Sync UI state (button enablement, validation styling, etc.)."""
        if self.sync_ui is not None:
            self.sync_ui()
