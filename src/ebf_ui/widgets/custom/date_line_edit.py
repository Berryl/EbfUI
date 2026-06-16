from datetime import date, timedelta

import pandas as pd
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QCalendarWidget,
    QLineEdit,
    QWidget, QDialog,
)
from ebf_core.date_time.parsers import parse_flex_datetime

from ebf_ui.widgets.custom.utils import show_popup


class DateLineEdit(QLineEdit):
    """A QLineEdit with date-aware keyboard shortcuts, flex parsing, and a
    calendar popup.

    Keyboard shortcuts:
        "t" — fill with today's date
        "+" — increment the current date by one day (falls back to today if no current date)
        "-" — decrement the current date by one day (falls back to today if no current date)
        "Alt+↓" — open the calendar popup
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setPlaceholderText("Jun-15 2026  or  t  /  +  /  -  /  Alt+↓")
        self._popup: QDialog | None = None

    # region Public interface

    def get_date(self) -> date | None:
        """Return the currently parsed date, or None if the field is empty or unparseable."""
        return self._parse_current_text()

    # endregion

    # region Event overrides

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        text = event.text().lower()

        if text == "t":
            self._set_date(date.today())
            self.editingFinished.emit()
            return

        if text in ("+", "-"):
            current = self._parse_current_text() or date.today()
            delta = 1 if text == "+" else -1
            self._set_date(self._offset_date(current, delta))
            self.editingFinished.emit()
            return

        if key == Qt.Key.Key_Down and event.modifiers() & Qt.KeyboardModifier.AltModifier:
            self._show_calendar_popup()
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

    # region Calendar popup

    def _show_calendar_popup(self) -> None:
        if self._popup is not None:
            self._popup.close()
            self._popup = None
            return

        calendar = QCalendarWidget()
        calendar.setGridVisible(True)

        initial = self._parse_current_text() or date.today()
        calendar.setSelectedDate(QDate(initial.year, initial.month, initial.day))

        calendar.activated.connect(self._on_date_selected)

        popup = show_popup(
            anchor=self,
            widget=calendar,
        )

        popup.destroyed.connect(self._on_popup_destroyed)
        self._popup = popup

    def _on_date_selected(self, q_date: QDate) -> None:
        self._set_date(date(q_date.year(), q_date.month(), q_date.day()))
        self.editingFinished.emit()
        if self._popup is not None:
            popup = self._popup
            self._popup = None
            popup.close()

    def _on_popup_destroyed(self) -> None:
        self._popup = None

    # endregion

    # region Helpers

    def _parse_current_text(self) -> date | None:
        text = self.text().strip()
        if not text:
            return None
        try:
            return parse_flex_datetime(text).date()
        except ValueError:
            pass
        try:
            return pd.to_datetime(text).date()
        except (ValueError, TypeError, pd.errors.ParserError):
            return None

    def _set_date(self, d: date) -> None:
        self.setText(f"{d.strftime('%b')}-{d.day} {d.year}")

    def _try_reformat(self) -> None:
        parsed = self._parse_current_text()
        if parsed is not None:
            self._set_date(parsed)

    @staticmethod
    def _offset_date(d: date, delta: int) -> date:
        return d + timedelta(days=delta)

    # endregion
