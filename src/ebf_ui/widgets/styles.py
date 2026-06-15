from PySide6.QtWidgets import QWidget

# region Errors
ERROR_BORDER_STYLESHEET = "* { border: 2px solid #e74c3c; }"  # universal selector

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
# endregion

# region Dates
DATE_FORMAT_PY =  "%m-%d-%Y"     # e.g. 06-15-2026
DATE_FORMAT_QT = "MM-dd-yyyy"    # Qt format string
# endregion
