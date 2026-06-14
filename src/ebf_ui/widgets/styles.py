# Option 1 — universal selector, one constant
ERROR_BORDER_STYLESHEET = "* { border: 2px solid #e74c3c; }"

# Option 2 — widget-specific constants
LINE_EDIT_ERROR_BORDER_STYLESHEET = "QLineEdit { border: 2px solid #e74c3c; }"
COMBO_BOX_ERROR_BORDER_STYLESHEET = "QComboBox { border: 2px solid #e74c3c; }"

def apply_errors(widget, original_stylesheet: str, messages: list[str]) -> None:
    if messages:
        widget.setStyleSheet(f"{original_stylesheet}\n{ERROR_BORDER_STYLESHEET}")
        widget.setToolTip("<br>".join(messages))
    else:
        widget.setStyleSheet(original_stylesheet)
        widget.setToolTip("")