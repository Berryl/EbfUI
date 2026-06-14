# Option 1 — universal selector, one constant
from PySide6.QtWidgets import QWidget

ERROR_BORDER_STYLESHEET = "* { border: 2px solid #e74c3c; }"

# Option 2 — widget-specific constants
LINE_EDIT_ERROR_BORDER_STYLESHEET = "QLineEdit { border: 2px solid #e74c3c; }"
COMBO_BOX_ERROR_BORDER_STYLESHEET = "QComboBox { border: 2px solid #e74c3c; }"

BASELINE_STYLESHEET_PROPERTY = "_baseline_stylesheet"


def apply_errors(widget: QWidget, messages: list[str]) -> None:
    if widget.property(BASELINE_STYLESHEET_PROPERTY) is None:
        widget.setProperty(BASELINE_STYLESHEET_PROPERTY, widget.styleSheet())

    original = widget.property(BASELINE_STYLESHEET_PROPERTY)

    if messages:
        widget.setStyleSheet(f"{original}\n{ERROR_BORDER_STYLESHEET}")
        widget.setToolTip("<br>".join(messages))
    else:
        widget.setStyleSheet(original)
        widget.setToolTip("")