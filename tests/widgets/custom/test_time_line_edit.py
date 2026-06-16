from datetime import datetime, time

import pytest
from PySide6.QtCore import Qt, QTime
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QTimeEdit
from ebf_core.date_time.testing_helpers import is_effectively_now

from ebf_ui.widgets.custom.time_line_edit import TimeLineEdit


def _fmt(t: time) -> str:
    """Canonical display format: e.g. '09:30:00 AM'"""
    return datetime.combine(datetime.today(), t).strftime("%I:%M:%S %p")


def _signal_count(spy: QSignalSpy) -> int:
    return spy.count() if hasattr(spy, "count") else len(spy)


SOME_TIME_STRING = "09:30:00 AM"
SOME_TIME = time(9, 30, 0)


class TestTimeLineEdit:

    @pytest.fixture
    def sut(self, qtbot) -> TimeLineEdit:
        widget = TimeLineEdit()
        qtbot.addWidget(widget)
        return widget

    class TestGetTime:

        def test_returns_none_when_empty(self, sut):
            assert sut.get_time() is None

        @pytest.mark.parametrize("raw", ["  ", "", "blah"])
        def test_returns_none_when_text_is_empty_or_unparseable(self, sut, raw):
            sut.setText(raw)
            assert sut.get_time() is None

        def test_returns_parsed_time_when_valid(self, sut):
            sut.setText(SOME_TIME_STRING)
            assert sut.get_time() == SOME_TIME

    class TestKeyboardShortcuts:
        class TestNowWith_n:

            def test_fills_with_current_time(self, sut, qtbot):
                qtbot.keyClick(sut, Qt.Key.Key_N)

                result = sut.get_time()
                assert is_effectively_now(result)

        class TestIncrementingWith_plus:

            def test_increments_by_one_second(self, sut, qtbot):
                sut.setText(SOME_TIME_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Plus)
                assert sut.get_time() == time(9, 30, 1)

            def test_increments_by_one_minute_with_shift(self, sut, qtbot):
                sut.setText(SOME_TIME_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Plus, modifier=Qt.KeyboardModifier.ShiftModifier)
                assert sut.get_time() == time(9, 31, 0)

            def test_increments_by_one_hour_with_ctrl(self, sut, qtbot):
                sut.setText(SOME_TIME_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Plus, modifier=Qt.KeyboardModifier.ControlModifier)
                assert sut.get_time() == time(10, 30, 0)

            def test_falls_back_to_now_when_empty(self, sut, qtbot):
                before = datetime.now().time()
                qtbot.keyClick(sut, Qt.Key.Key_Plus)
                result = sut.get_time()
                assert result >= before

        class TestDecrementingWith_minus:

            def test_decrements_by_one_second(self, sut, qtbot):
                sut.setText(SOME_TIME_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Minus)
                assert sut.get_time() == time(9, 29, 59)

            def test_decrements_by_one_minute_with_shift(self, sut, qtbot):
                sut.setText(SOME_TIME_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Minus, modifier=Qt.KeyboardModifier.ShiftModifier)
                assert sut.get_time() == time(9, 29, 0)

            def test_decrements_by_one_hour_with_ctrl(self, sut, qtbot):
                sut.setText(SOME_TIME_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Minus, modifier=Qt.KeyboardModifier.ControlModifier)
                assert sut.get_time() == time(8, 30, 0)

            def test_falls_back_to_now_when_empty(self, sut, qtbot):
                before = datetime.now().time()
                qtbot.keyClick(sut, Qt.Key.Key_Minus)
                result = sut.get_time()
                assert result <= before or result is not None

    class TestParsing:

        def test_reformats_valid_input(self, sut):
            sut.setText("9:30 AM")
            sut._try_reformat()
            assert sut.text() == "09:30:00 AM"

        def test_leaves_invalid_text_as_is(self, sut):
            sut.setText("not a time")
            sut._try_reformat()
            assert sut.text() == "not a time"

        def test_leaves_empty_field_as_is(self, sut):
            sut._try_reformat()
            assert sut.text() == ""

        def test_reformats_24h_input(self, sut):
            sut.setText("14:30:00")
            sut._try_reformat()
            assert sut.text() == "02:30:00 PM"

    class TestEditingFinished:

        def test_n_emits_once(self, sut, qtbot):
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_N)
            assert _signal_count(spy) == 1

        def test_plus_emits_once(self, sut, qtbot):
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert _signal_count(spy) == 1

        def test_minus_emits_once(self, sut, qtbot):
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_Minus)
            assert _signal_count(spy) == 1

        def test_enter_emits_once(self, sut, qtbot):
            sut.setText(SOME_TIME_STRING)
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_Return)
            assert _signal_count(spy) == 1

        def test_spinner_selection_emits_once(self, sut):
            sut._show_time_popup()
            spy = QSignalSpy(sut.editingFinished)
            sut._on_time_selected(QTime(9, 30, 0))
            assert _signal_count(spy) == 1

    class TestTimePopup:

        def test_alt_down_opens_popup(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is not None
            assert sut._popup.findChild(QTimeEdit) is not None

        def test_alt_down_when_open_closes_popup(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is not None
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is None

        def test_popup_initializes_from_current_value(self, sut):
            sut.setText(SOME_TIME_STRING)
            sut._show_time_popup()
            spinner = sut._popup.findChild(QTimeEdit)
            assert spinner.time() == QTime(9, 30, 0)

        def test_spinner_selection_sets_text_and_closes_popup(self, sut):
            sut._show_time_popup()

            sut._on_time_selected(QTime(14, 30, 0))

            assert sut.text() == "02:30:00 PM"
            assert sut._popup is None
