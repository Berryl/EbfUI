from decimal import Decimal, InvalidOperation
import ast
import operator

from PySide6.QtGui import QFocusEvent, QKeyEvent
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QWidget

from ebf_domain.money.money import Money


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class MoneyLineEdit(QLineEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._show_explicit_positive_sign = False
        self.setToolTip("Enter amount or expression, e.g. 1.25, 100*.05, 15000/100")

    def get_money(self) -> Money | None:
        value = self._parse_current_text()
        return Money.mint(value) if value is not None else None

    def set_money(self, value: Money | None) -> None:
        if value is None:
            self.clear()
            return
        self.setText(self._format_money(value))

    def set_show_explicit_positive_sign(self, show_sign: bool) -> None:
        self._show_explicit_positive_sign = show_sign
        self._try_reformat()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._try_reformat()
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._try_reformat()
        super().focusOutEvent(event)

    def _parse_current_text(self) -> Decimal | None:
        text = self.text().strip()
        if not text:
            return None

        text = text.replace("$", "").replace(",", "")

        try:
            return Decimal(text)
        except InvalidOperation:
            pass

        try:
            return _evaluate_decimal_expression(text)
        except (ValueError, ZeroDivisionError, InvalidOperation):
            return None

    def _try_reformat(self) -> None:
        value = self._parse_current_text()
        if value is not None:
            self.setText(self._format_money(Money.mint(value)))

    def _format_money(self, value: Money) -> str:
        text = value.format(show_currency=False, symbol="", use_separators=True)

        if self._show_explicit_positive_sign and value.is_positive:
            return f"+{text}"

        return text

def _evaluate_decimal_expression(text: str) -> Decimal:
    tree = ast.parse(text, mode="eval")
    return _eval_ast(tree.body)


def _eval_ast(node) -> Decimal:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return Decimal(node.value)
        if isinstance(node.value, float):
            return Decimal(str(node.value))
        raise ValueError("Unsupported constant")

    if isinstance(node, ast.BinOp):
        operator_func = _ALLOWED_OPERATORS.get(type(node.op))
        if operator_func is None:
            raise ValueError("Unsupported operator")
        return operator_func(_eval_ast(node.left), _eval_ast(node.right))

    if isinstance(node, ast.UnaryOp):
        operator_func = _ALLOWED_OPERATORS.get(type(node.op))
        if operator_func is None:
            raise ValueError("Unsupported unary operator")
        return operator_func(_eval_ast(node.operand))

    raise ValueError("Unsupported expression")