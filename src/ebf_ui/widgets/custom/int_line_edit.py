from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent, QKeyEvent
from PySide6.QtWidgets import QLineEdit, QWidget


class IntLineEdit(QLineEdit):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        step: int = 1,
        shift_step: int = 100,
    ) -> None:
        super().__init__(parent)
        self._step = step
        self._shift_step = shift_step
        self.setToolTip("Enter whole number. ↑/↓ adjusts by 1, Shift+↑/↓ adjusts by 100.")

    # region Public interface

    def get_int(self) -> int | None:
        return self._parse_current_text()

    def set_int(self, value: int | None) -> None:
        if value is None:
            self.clear()
            return

        self.setText(self._format_int(value))

    # endregion

    # region Event overrides

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            current = self._parse_current_text()

            if current is None:
                if self.text().strip():
                    super().keyPressEvent(event)
                    return
                current = 0

            step = self._shift_step if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else self._step
            if event.key() == Qt.Key.Key_Down:
                step = -step

            self.set_int(current + step)
            self.editingFinished.emit()
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._try_reformat()
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._try_reformat()
        super().focusOutEvent(event)

    # endregion

    # region Helpers

    def _parse_current_text(self) -> int | None:
        text = self.text().strip()
        if not text:
            return None

        text = text.replace(",", "")

        try:
            return int(text)
        except ValueError:
            return None

    @staticmethod
    def _format_int(value: int) -> str:
        return f"{value:,}"

    def _try_reformat(self) -> None:
        value = self._parse_current_text()
        if value is not None:
            self.setText(self._format_int(value))

    # endregion