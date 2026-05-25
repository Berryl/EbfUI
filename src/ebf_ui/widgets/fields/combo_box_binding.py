from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QComboBox

from ebf_ui.state.state_tracker import StateTracker
from ebf_ui.widgets.styles import ERROR_STYLESHEET


class ComboBoxBinding[T]:
    def __init__(
        self,
        combo_box: QComboBox,
        tracker: StateTracker,
        items: Sequence[T],
        get_value: Callable[[], T | None],
        set_value: Callable[[T | None], None],
        get_text: Callable[[T], str] = str,
        sync_ui: Callable[[], None] | None = None,
    ):
        self.combo_box = combo_box
        self.tracker = tracker
        self.items = list(items)
        self.get_value = get_value
        self.set_value = set_value
        self.get_text = get_text
        self.sync_ui = sync_ui
        self._is_refreshing = False
        self._original_stylesheet = combo_box.styleSheet()

        self._load_items()

        # Connection is cleaned up automatically when the widget is destroyed
        combo_box.currentIndexChanged.connect(self._on_current_index_changed)

        self.refresh()

    def refresh(self) -> None:
        self._push_model_to_view()
        self._sync_ui_state()

    def set_errors(self, messages: list[str]) -> None:
        if messages:
            self.combo_box.setStyleSheet(self._original_stylesheet + ERROR_STYLESHEET)
            self.combo_box.setToolTip("<br>".join(messages))
        else:
            self.combo_box.setStyleSheet(self._original_stylesheet)
            self.combo_box.setToolTip("")

    def _load_items(self) -> None:
        self.combo_box.clear()
        for item in self.items:
            self.combo_box.addItem(self.get_text(item), item)

    def _on_current_index_changed(self, index: int) -> None:
        if self._is_refreshing:
            return

        value = self.combo_box.itemData(index) if index >= 0 else None
        self.set_value(value)
        self.tracker.update_edit()
        self._sync_ui_state()

    def _push_model_to_view(self) -> None:
        value = self.get_value()
        index = self.combo_box.findData(value)

        self._is_refreshing = True
        try:
            self.combo_box.setCurrentIndex(index)
        finally:
            self._is_refreshing = False

    def _sync_ui_state(self) -> None:
        if self.sync_ui is not None:
            self.sync_ui()