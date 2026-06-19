from datetime import date, datetime, time, timedelta

import pandas as pd
from PySide6.QtCore import QDate, Qt, QTime
from PySide6.QtGui import QFocusEvent, QKeyEvent
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QLineEdit,
    QTimeEdit,
    QWidget,
)

from ebf_ui.widgets.custom.utils import show_popup


def _format_date(d: date) -> str:
    """Canonical date display format: e.g. 'Jun-15 2026'"""
    return f"{d.strftime('%b')}-{d.day} {d.year}"


def _format_datetime(dt: datetime) -> str:
    """Canonical datetime display format: e.g. 'Jun-15 2026 09:30:00 AM'"""
    return f"{_format_date(dt.date())} {dt.strftime('%I:%M:%S %p')}"


class DateTimeLineEdit(QLineEdit):
    """A QLineEdit carrying a full datetime, with date- and time-aware keyboard
    shortcuts, a single pandas parse, and separate calendar/spinner popups.

    Keyboard shortcuts:
        "t"        — set date to today, preserving existing time (or now() if empty)
        "n"        — set time to now, preserving existing date (or today if empty)
        "+" / "-"  — increment/decrement the date by 1 day (fallback to today+now when empty)
        "↑" / "↓"  — increment/decrement the time by 1 second
        "Shift+↑/↓"— increment/decrement the time by 1 minute
        "Ctrl+↑/↓" — increment/decrement the time by 1 hour
        "Alt+↓"    — open the calendar popup (date portion only, preserves time)
        "Alt+↑"    — open the time spinner popup (time portion only, preserves date)
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setToolTip(
            "t = today, n = now, +/- = adjust date, ↑/↓ = adjust time, Alt+↓ = calendar, Alt+↑ = timepicker")
        self._popup: QDialog | None = None

    # region Public interface

    def get_datetime(self) -> datetime | None:
        """Return the currently parsed datetime, or None if empty/unparseable."""
        return self._parse_current_text()

    # endregion

    # region Event overrides

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        text = event.text().lower()
        modifiers = event.modifiers()
        current = self._parse_current_text()

        if text == "t":
            existing_time = current.time() if current is not None else datetime.now().time()
            self._set_datetime(datetime.combine(date.today(), existing_time))
            self.editingFinished.emit()
            return

        if text == "n":
            existing_date = current.date() if current is not None else date.today()
            self._set_datetime(datetime.combine(existing_date, datetime.now().time()))
            self.editingFinished.emit()
            return

        if text in ("+", "-"):
            base = current or datetime.combine(date.today(), datetime.now().time())
            delta_sign = 1 if text == "+" else -1
            self._set_datetime(base + timedelta(days=delta_sign))
            self.editingFinished.emit()
            return

        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            base = current or datetime.combine(date.today(), datetime.now().time())
            delta_sign = 1 if key == Qt.Key.Key_Up else -1

            if modifiers & Qt.KeyboardModifier.AltModifier:
                if key == Qt.Key.Key_Down:
                    self._show_calendar_popup()
                else:
                    self._show_time_popup()
                return

            if modifiers & Qt.KeyboardModifier.ControlModifier:
                delta = timedelta(hours=delta_sign)
            elif modifiers & Qt.KeyboardModifier.ShiftModifier:
                delta = timedelta(minutes=delta_sign)
            else:
                delta = timedelta(seconds=delta_sign)

            self._set_datetime(base + delta)
            self.editingFinished.emit()
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

    # region Calendar popup (date portion only)

    def _show_calendar_popup(self) -> None:
        if self._popup is not None:
            self._popup.close()
            self._popup = None
            return

        calendar = QCalendarWidget()
        calendar.setGridVisible(True)

        current = self._parse_current_text()
        initial_date = current.date() if current is not None else date.today()
        calendar.setSelectedDate(QDate(initial_date.year, initial_date.month, initial_date.day))

        calendar.activated.connect(self._on_date_selected)

        popup = show_popup(anchor=self, widget=calendar)
        popup.destroyed.connect(self._on_popup_destroyed)
        self._popup = popup

    def _on_date_selected(self, q_date: QDate) -> None:
        current = self._parse_current_text()
        existing_time = current.time() if current is not None else datetime.now().time()
        new_date = date(q_date.year(), q_date.month(), q_date.day())
        self._set_datetime(datetime.combine(new_date, existing_time))
        self.editingFinished.emit()
        if self._popup is not None:
            popup = self._popup
            self._popup = None
            popup.close()

    # endregion

    # region Time popup (time portion only)

    def _show_time_popup(self) -> None:
        if self._popup is not None:
            self._popup.close()
            self._popup = None
            return

        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("hh:mm:ss AP")

        current = self._parse_current_text()
        initial_time = current.time() if current is not None else datetime.now().time()
        time_edit.setTime(QTime(initial_time.hour, initial_time.minute, initial_time.second))

        time_edit.timeChanged.connect(self._on_time_selected)

        popup = show_popup(anchor=self, widget=time_edit)
        popup.destroyed.connect(self._on_popup_destroyed)
        self._popup = popup

    def _on_time_selected(self, q_time: QTime) -> None:
        current = self._parse_current_text()
        existing_date = current.date() if current is not None else date.today()
        new_time = time(q_time.hour(), q_time.minute(), q_time.second())
        self._set_datetime(datetime.combine(existing_date, new_time))
        self.editingFinished.emit()

        if self._popup is not None:
            popup = self._popup
            self._popup = None
            popup.close()

    # endregion

    def _on_popup_destroyed(self) -> None:
        self._popup = None

    # region Helpers

    def _parse_current_text(self) -> datetime | None:
        text = self.text().strip()
        if not text:
            return None
        try:
            return pd.to_datetime(text).to_pydatetime()
        except (ValueError, TypeError, pd.errors.ParserError):
            return None

    def _set_datetime(self, dt: datetime) -> None:
        self.setText(_format_datetime(dt))

    def _try_reformat(self) -> None:
        parsed = self._parse_current_text()
        if parsed is not None:
            self._set_datetime(parsed)

    # endregion
