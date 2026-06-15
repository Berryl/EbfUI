from datetime import date, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)
from ebf_core.date_time.parsers import parse_flex_datetime

from ebf_ui.widgets.styles import DATE_FORMAT_PY


class DateLineEdit(QLineEdit):
    """A QLineEdit with date-aware keyboard shortcuts, flex parsing, and a
    calendar popup.

    Keyboard shortcuts:
        "t" — fill with today's date
        "+" — increment the current date by one day (falls back to today if no current date)
        "-" — decrement the current date by one day (falls back to today if no current date)
        "Alt+↓" — open the calendar popup

    Flex parsing:
        see parse_flex_datetime.

    Calendar popup:
        A frameless QCalendarWidget drops below the widget. It initializes
        to the currently parsed date when the field holds a valid value, otherwise
        to today.  Clicking a date fills the field and closes the popup.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setPlaceholderText("YYYY-MM-DD  or  t  /  +  /  -  /  Alt+↓")
        self._popup: QFrame | None = None

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

        popup = QFrame(self.window(), Qt.WindowType.Popup)
        popup.setFrameShape(QFrame.Shape.StyledPanel)

        calendar = QCalendarWidget(popup)
        calendar.setGridVisible(True)

        initial = self._parse_current_text() or date.today()
        calendar.setSelectedDate(QDate(initial.year, initial.month, initial.day))

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(calendar)

        calendar.activated.connect(self._on_date_selected)
        popup.destroyed.connect(self._on_popup_destroyed)

        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        popup.move(global_pos)
        popup.show()
        self._popup = popup

    def _on_date_selected(self, q_date: QDate) -> None:
        self._set_date(date(q_date.year(), q_date.month(), q_date.day()))
        self.editingFinished.emit()
        if self._popup is not None:
            self._popup.close()

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
            return None

    def _set_date(self, d: date) -> None:
        self.setText(d.strftime(DATE_FORMAT_PY))

    def _try_reformat(self) -> None:
        parsed = self._parse_current_text()
        if parsed is not None:
            self._set_date(parsed)

    @staticmethod
    def _offset_date(d: date, delta: int) -> date:
        return d + timedelta(days=delta)

    # endregion
