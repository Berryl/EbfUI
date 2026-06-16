from PySide6.QtCore import Qt  # ← SignalInstance is the key
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget


def show_popup(
        anchor: QWidget,
        widget: QWidget,
        *,
        margins: tuple[int, int, int, int] = (2, 2, 2, 2),
) -> QDialog:
    popup = QDialog(anchor.window())
    popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)

    layout = QVBoxLayout(popup)
    layout.setContentsMargins(*margins)
    layout.addWidget(widget)

    popup.adjustSize()
    popup.move(anchor.mapToGlobal(anchor.rect().bottomLeft()))
    popup.show()
    return popup
