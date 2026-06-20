import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy

from ebf_ui.widgets.custom.int_line_edit import IntLineEdit


def _signal_count(spy: QSignalSpy) -> int:
    return spy.count() if hasattr(spy, "count") else len(spy)


class TestIntLineEdit:

    @pytest.fixture
    def sut(self, qtbot) -> IntLineEdit:
        widget = IntLineEdit()
        qtbot.addWidget(widget)
        return widget

    class TestGetInt:

        @pytest.mark.parametrize("raw", ["", "  ", "blah", "123.45"])
        def test_returns_none_when_empty_or_unparseable(self, sut, raw):
            sut.setText(raw)

            assert sut.get_int() is None

        @pytest.mark.parametrize(
            "raw, expected",
            [
                ("123", 123),
                ("1,234", 1234),
                ("+123", 123),
                ("-123", -123),
            ],
        )
        def test_returns_int_when_valid(self, sut, raw, expected):
            sut.setText(raw)

            assert sut.get_int() == expected

    class TestSetInt:

        def test_none_clears_text(self, sut):
            sut.setText("1234")

            sut.set_int(None)

            assert sut.text() == ""

        def test_displays_with_separator(self, sut):
            sut.set_int(1234)

            assert sut.text() == "1,234"

        def test_can_display_negative_int(self, sut):
            sut.set_int(-1234)

            assert sut.text() == "-1,234"

    class TestFormatting:

        @pytest.mark.parametrize(
            "raw, expected",
            [
                ("123", "123"),
                ("1234", "1,234"),
                ("1,234", "1,234"),
                ("+1234", "1,234"),
                ("-1234", "-1,234"),
            ],
        )
        def test_reformats_on_enter(self, sut, qtbot, raw, expected):
            sut.setText(raw)

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert sut.text() == expected

        def test_leaves_invalid_text_as_is(self, sut, qtbot):
            sut.setText("not int")

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert sut.text() == "not int"

    class TestKeyboardAdjustments:

        @pytest.fixture(autouse=True)
        def sut_start(self, sut) -> IntLineEdit:
            sut.setText("100")
            return sut

        def test_up_increments_by_step(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Up)
            assert sut_start.text() == "101"

        def test_down_decrements_by_step(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Down)
            assert sut_start.text() == "99"

        def test_shift_up_increments_by_shift_step(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.ShiftModifier)
            assert sut_start.text() == "200"

        def test_shift_down_decrements_by_shift_step(self, sut_start, qtbot):
            qtbot.keyClick(sut_start, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.ShiftModifier)
            assert sut_start.text() == "0"

        def test_invalid_text_is_left_unchanged(self, sut, qtbot):
            sut.setText("not int")

            qtbot.keyClick(sut, Qt.Key.Key_Up)

            assert sut.text() == "not int"

        def test_up_emits_once(self, sut_start, qtbot):
            spy = QSignalSpy(sut_start.editingFinished)
            qtbot.keyClick(sut_start, Qt.Key.Key_Up)

            assert _signal_count(spy) == 1

    class TestCustomSteps:

        @pytest.fixture
        def sut(self, qtbot) -> IntLineEdit:
            widget = IntLineEdit(step=10, shift_step=1000)
            qtbot.addWidget(widget)
            return widget

        def test_up_uses_custom_step(self, sut, qtbot):
            sut.setText("100")

            qtbot.keyClick(sut, Qt.Key.Key_Up)

            assert sut.text() == "110"

        def test_shift_up_uses_custom_shift_step(self, sut, qtbot):
            sut.setText("100")

            qtbot.keyClick(sut, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.ShiftModifier)

            assert sut.text() == "1,100"

    class TestEditingFinished:

        def test_enter_emits_once(self, sut, qtbot):
            sut.setText("1234")
            spy = QSignalSpy(sut.editingFinished)

            qtbot.keyClick(sut, Qt.Key.Key_Return)

            assert _signal_count(spy) == 1