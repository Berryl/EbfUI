import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from ebf_domain.money.money import Money

from ebf_ui.widgets.custom.money_line_edit import MoneyLineEdit


def _signal_count(spy: QSignalSpy) -> int:
    return spy.count() if hasattr(spy, "count") else len(spy)


class TestMoneyLineEdit:

    @pytest.fixture
    def sut(self, qtbot) -> MoneyLineEdit:
        widget = MoneyLineEdit()
        qtbot.addWidget(widget)
        return widget

    class TestGetMoney:

        @pytest.mark.parametrize("raw", ["", "  ", "blah"])
        def test_returns_none_when_empty_or_unparseable(self, sut, raw):
            sut.setText(raw)

            assert sut.get_money() is None

        @pytest.mark.parametrize(
            "raw, expected",
            [
                ("123", Money.mint("123")),
                ("123.45", Money.mint("123.45")),
                ("$123.45", Money.mint("123.45")),
                ("1,234.56", Money.mint("1234.56")),
                ("-12.34", Money.mint("-12.34")),
            ],
        )
        def test_returns_money_when_valid(self, sut, raw, expected):
            sut.setText(raw)

            assert sut.get_money() == expected

    class TestSetMoney:

        @pytest.fixture
        def new_amount(self) -> Money:
            return Money.mint("1234.56")

        def test_none_clears_text(self, sut):
            sut.setText("1234.56")

            sut.set_money(None)

            assert sut.text() == ""

        def test_display_is_with_separator_and_without_currency_symbol(self, sut, new_amount):
            sut.set_money(new_amount)

            assert sut.text() == "1,234.56"

        def test_can_display_negative_money(self, sut, new_amount):
            sut.set_money(new_amount * -1)

            assert sut.text() == "-1,234.56"

    class TestFormatting:

        @pytest.mark.parametrize(
            "raw, expected",
            [
                ("123", "123.00"),
                ("123.4", "123.40"),
                ("123.456", "123.46"),
                ("$1,234.5", "1,234.50"),
                ("-123.4", "-123.40"),
            ],
        )
        def test_reformats_on_enter(self, sut, qtbot, raw, expected):
            sut.setText(raw)

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert sut.text() == expected

        def test_leaves_invalid_text_as_is(self, sut, qtbot):
            sut.setText("not money")

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert sut.text() == "not money"

    class TestExpressions:

        @pytest.mark.parametrize(
            "raw, expected",
            [
                ("100*.05", "5.00"),
                ("15000/100", "150.00"),
                ("141.85 - 133.50", "8.35"),
                ("(10 + 5) * 2", "30.00"),
                ("-10 + 2", "-8.00"),
            ],
        )
        def test_evaluates_decimal_expression_on_enter(self, sut, qtbot, raw, expected):
            sut.setText(raw)

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert sut.text() == expected

        @pytest.mark.parametrize(
            "raw",
            [
                "10 ** 2",
                "abs(-10)",
                "__import__('os').system('dir')",
                "10 // 3",
            ],
        )
        def test_rejects_unsupported_expression(self, sut, qtbot, raw):
            sut.setText(raw)

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert sut.text() == raw

    class TestExplicitPositiveSignDisplay:

        @pytest.fixture
        def new_amount(self) -> Money:
            return Money.mint("123.45")

        def test_positive_money_shows_plus_when_enabled(self, sut, new_amount):
            sut.set_money(new_amount)
            assert sut.text() == "123.45"  # off by default

            sut.set_show_explicit_positive_sign(True)
            assert sut.text() == "+123.45"

            sut.set_show_explicit_positive_sign(False)
            assert sut.text() == "123.45"

        def test_negative_money_always_shows_minus_sign_no_matter(self, sut, new_amount):
            sut.set_money(new_amount * -1)

            sut.set_show_explicit_positive_sign(True)
            assert sut.text() == "-123.45"

            sut.set_show_explicit_positive_sign(False)
            assert sut.text() == "-123.45"

        def test_zero_money_never_shows_sign_no_matter(self, sut):
            sut.set_money(Money.zero())

            sut.set_show_explicit_positive_sign(True)
            assert sut.text() == "0.00"

            sut.set_show_explicit_positive_sign(False)
            assert sut.text() == "0.00"

    class TestKeyboardAdjustments:

        @pytest.fixture(autouse=True)
        def sut_start(self, sut) -> MoneyLineEdit:
            sut.setText("123.45")
            return sut

        def test_up_increments_by_one_cent(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Up)
            assert sut_start.text() == "123.46"

        def test_down_decrements_by_one_cent(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Down)
            assert sut_start.text() == "123.44"

        def test_shift_up_increments_by_one_dollar(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.ShiftModifier)
            assert sut_start.text() == "124.45"

        def test_shift_down_decrements_by_one_dollar(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.ShiftModifier)
            assert sut_start.text() == "122.45"

        def test_invalid_text_is_left_unchanged(self, sut, qtbot):
            sut.setText("not money")
            qtbot.keyClick(sut, Qt.Key.Key_Up)

            assert sut.text() == "not money"

        def test_up_emits_once(self, sut_start, qtbot):
            spy = QSignalSpy(sut_start.editingFinished)
            qtbot.keyClick(sut_start, Qt.Key.Key_Up)

            assert _signal_count(spy) == 1

    class TestEditingFinished:

        def test_enter_emits_once(self, sut, qtbot):
            sut.setText("123.45")
            spy = QSignalSpy(sut.editingFinished)

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert _signal_count(spy) == 1
