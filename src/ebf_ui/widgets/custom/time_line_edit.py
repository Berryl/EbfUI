from datetime import datetime, time, timedelta

import pandas as pd
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QTimeEdit,
    QWidget,
)

from ebf_ui.widgets.custom.utils import show_popup

TIME_FORMAT_PY = "%I:%M:%S %p"  # e.g., 09:30:00 AM


class TimeLineEdit(QLineEdit):
    """A QLineEdit with time-aware keyboard shortcuts, pandas parsing, and a
    time spinner popup.

    Keyboard shortcuts:
        "n" — fill with the current time (to the second)
        "+" / "-" — increment/decrement by 1 second (fallback to now() when empty)
        "Shift+/-" — increment/decrement by 1 minute
        "Ctrl+/-" — increment/decrement by 1 hour
        "Alt+↓" — open the time spinner popup
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setToolTip(
            "n = now, +/- = adjust seconds, Shift+/- = adjust minutes, Ctrl+/- = adjust hours, Alt+↓ = timepicker")
        self._popup: QDialog | None = None

    # region Public interface

    def get_time(self) -> time | None:
        """Return the currently parsed time, or None if the field is empty or unparseable."""
        return self._parse_current_text()

    # endregion

    # region Event overrides

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        text = event.text().lower()
        modifiers = event.modifiers()

        if text == "n":
            self._set_time(datetime.now().time())
            self.editingFinished.emit()
            return

        if key in (Qt.Key.Key_Plus, Qt.Key.Key_Minus):
            delta_sign = 1 if key == Qt.Key.Key_Plus else -1
            current = self._parse_current_text() or datetime.now().time()

            if modifiers & Qt.KeyboardModifier.ControlModifier:
                delta = timedelta(hours=delta_sign)
            elif modifiers & Qt.KeyboardModifier.ShiftModifier:
                delta = timedelta(minutes=delta_sign)
            else:
                delta = timedelta(seconds=delta_sign)

            self._set_time(self._offset_time(current, delta))
            self.editingFinished.emit()
            return

        if key == Qt.Key.Key_Down and modifiers & Qt.KeyboardModifier.AltModifier:
            self._show_time_popup()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._try_reformat()
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._try_reformat()
        super().focusOutEvent(event)

    # endregion

    # region Time popup

    def _show_time_popup(self) -> None:
        if self._popup is not None:
            self._popup.close()
            self._popup = None
            return

        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("hh:mm:ss AP")

        initial = self._parse_current_text() or datetime.now().time()
        time_edit.setTime(QTime(initial.hour, initial.minute, initial.second))

        time_edit.timeChanged.connect(self._on_time_selected)

        popup = show_popup(anchor=self, widget=time_edit)
        popup.destroyed.connect(self._on_popup_destroyed)
        self._popup = popup

    def _on_time_selected(self, q_time: QTime) -> None:
        self._set_time(time(q_time.hour(), q_time.minute(), q_time.second()))
        self.editingFinished.emit()
        if self._popup is not None:
            popup = self._popup
            self._popup = None
            popup.close()

    def _on_popup_destroyed(self) -> None:
        self._popup = None

    # endregion

    # region Helpers

    def _parse_current_text(self) -> time | None:
        text = self.text().strip()
        if not text:
            return None
        try:
            return pd.to_datetime(text).time()
        except (ValueError, TypeError, pd.errors.ParserError):
            return None

    def _set_time(self, t: time) -> None:
        self.setText(datetime.combine(datetime.today(), t).strftime(TIME_FORMAT_PY))

    def _try_reformat(self) -> None:
        parsed = self._parse_current_text()
        if parsed is not None:
            self._set_time(parsed)

    @staticmethod
    def _offset_time(t: time, delta: timedelta) -> time:
        return (datetime.combine(datetime.today(), t) + delta).time()

    # endregion
