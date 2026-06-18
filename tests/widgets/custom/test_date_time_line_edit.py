from datetime import date, datetime, time, timedelta

import pytest
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QCalendarWidget, QTimeEdit
from ebf_core.date_time.testing_helpers import is_effectively_now

from ebf_ui.widgets.custom.date_time_line_edit import DateTimeLineEdit


def _fmt(dt: datetime) -> str:
    """Canonical display format: e.g. 'Jun-15 2026 09:30:00 AM'"""
    date_part = f"{dt.strftime('%b')}-{dt.day} {dt.year}"
    time_part = dt.strftime("%I:%M:%S %p")
    return f"{date_part} {time_part}"


def _signal_count(spy: QSignalSpy) -> int:
    return spy.count() if hasattr(spy, "count") else len(spy)


SOME_DATETIME_STRING = "Jun-15 2026 09:30:00 AM"
SOME_DATETIME = datetime(2026, 6, 15, 9, 30, 0)


class TestDateTimeLineEdit:

    @pytest.fixture
    def sut(self, qtbot) -> DateTimeLineEdit:
        widget = DateTimeLineEdit()
        qtbot.addWidget(widget)
        return widget

    class TestGetDatetime:

        def test_returns_none_when_empty(self, sut):
            assert sut.get_datetime() is None

        @pytest.mark.parametrize("raw", ["  ", "", "blah"])
        def test_returns_none_when_empty_or_unparseable(self, sut, raw):
            sut.setText(raw)
            assert sut.get_datetime() is None

        def test_returns_parsed_datetime_when_valid(self, sut):
            sut.setText(SOME_DATETIME_STRING)
            assert sut.get_datetime() == SOME_DATETIME

    class TestTodayWith_t:

        def test_when_empty_sets_today_and_now(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_T)
            result = sut.get_datetime()
            assert result.date() == date.today()
            assert is_effectively_now(result.time())

        def test_when_populated_preserves_existing_time(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_T)
            result = sut.get_datetime()
            assert result.date() == date.today()
            assert result.time() == time(9, 30, 0)

    class TestNowWith_n:

        def test_when_empty_sets_today_and_now(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_N)
            result = sut.get_datetime()
            assert result.date() == date.today()
            assert is_effectively_now(result.time())

        def test_when_populated_preserves_existing_date(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            before = datetime.now().replace(microsecond=0)
            qtbot.keyClick(sut, Qt.Key.Key_N)
            after = datetime.now().replace(microsecond=0)
            result = sut.get_datetime()
            assert result.date() == date(2026, 6, 15)
            assert before.time() <= result.time() <= after.time()

    class TestIncrementingDateWith_plus:

        def test_increments_date_by_one_day(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert sut.get_datetime() == SOME_DATETIME + timedelta(days=1)

        def test_falls_back_to_today_and_now_when_empty(self, sut, qtbot):
            before = datetime.now().replace(microsecond=0)
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            result = sut.get_datetime()
            assert result.date() == date.today() + timedelta(days=1)
            assert result.time() >= before.time() or result.time() <= before.time()

        def test_handles_month_boundary(self, sut, qtbot):
            sut.setText("Jun-30 2026 09:30:00 AM")
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert sut.get_datetime().date() == date(2026, 7, 1)

    class TestDecrementingDateWith_minus:

        def test_decrements_date_by_one_day(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Minus)
            assert sut.get_datetime() == SOME_DATETIME - timedelta(days=1)

        def test_handles_month_boundary(self, sut, qtbot):
            sut.setText("Jul-1 2026 09:30:00 AM")
            qtbot.keyClick(sut, Qt.Key.Key_Minus)
            assert sut.get_datetime().date() == date(2026, 6, 30)

    class TestIncrementingTimeWith_up:

        def test_increments_by_one_second(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Up)
            assert sut.get_datetime() == SOME_DATETIME + timedelta(seconds=1)

        def test_increments_by_one_minute_with_shift(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.ShiftModifier)
            assert sut.get_datetime() == SOME_DATETIME + timedelta(minutes=1)

        def test_increments_by_one_hour_with_ctrl(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.ControlModifier)
            assert sut.get_datetime() == SOME_DATETIME + timedelta(hours=1)

    class TestDecrementingTimeWith_down:

        def test_decrements_by_one_second(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Down)
            assert sut.get_datetime() == SOME_DATETIME - timedelta(seconds=1)

        def test_decrements_by_one_minute_with_shift(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.ShiftModifier)
            assert sut.get_datetime() == SOME_DATETIME - timedelta(minutes=1)

        def test_decrements_by_one_hour_with_ctrl(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.ControlModifier)
            assert sut.get_datetime() == SOME_DATETIME - timedelta(hours=1)

    class TestParsing:

        def test_reformats_valid_input(self, sut):
            sut.setText("6/15/2026 9:30 AM")
            sut._try_reformat()
            assert sut.text() == SOME_DATETIME_STRING

        def test_leaves_invalid_text_as_is(self, sut):
            sut.setText("not a datetime")
            sut._try_reformat()
            assert sut.text() == "not a datetime"

        def test_leaves_empty_field_as_is(self, sut):
            sut._try_reformat()
            assert sut.text() == ""

    class TestEditingFinished:

        def test_t_emits_once(self, sut, qtbot):
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_T)
            assert _signal_count(spy) == 1

        def test_n_emits_once(self, sut, qtbot):
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_N)
            assert _signal_count(spy) == 1

        def test_plus_emits_once(self, sut, qtbot):
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert _signal_count(spy) == 1

        def test_up_emits_once(self, sut, qtbot):
            sut.setText(SOME_DATETIME_STRING)
            spy = QSignalSpy(sut.editingFinished)
            qtbot.keyClick(sut, Qt.Key.Key_Up)
            assert _signal_count(spy) == 1

        def test_calendar_selection_emits_once(self, sut):
            sut._show_calendar_popup()
            spy = QSignalSpy(sut.editingFinished)
            sut._on_date_selected(QDate(2026, 6, 20))
            assert _signal_count(spy) == 1

        def test_spinner_selection_emits_once(self, sut):
            sut._show_time_popup()
            spy = QSignalSpy(sut.editingFinished)
            sut._on_time_selected(QTime(9, 30, 0))
            assert _signal_count(spy) == 1

    class TestCalendarPopup:

        def test_alt_down_opens_popup(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is not None
            assert sut._popup.findChild(QCalendarWidget) is not None

        def test_alt_down_when_open_closes_popup(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is not None
            qtbot.keyClick(sut, Qt.Key.Key_Down, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is None

        def test_popup_initializes_from_current_date(self, sut):
            sut.setText(SOME_DATETIME_STRING)
            sut._show_calendar_popup()
            calendar = sut._popup.findChild(QCalendarWidget)
            assert calendar.selectedDate() == QDate(2026, 6, 15)

        def test_selecting_date_preserves_existing_time(self, sut):
            sut.setText(SOME_DATETIME_STRING)
            sut._show_calendar_popup()
            sut._on_date_selected(QDate(2026, 6, 20))
            assert sut.get_datetime() == datetime(2026, 6, 20, 9, 30, 0)
            assert sut._popup is None

        def test_selecting_date_when_empty_defaults_time_to_now(self, sut):
            sut._show_calendar_popup()
            sut._on_date_selected(QDate(2026, 6, 20))
            result = sut.get_datetime()
            assert result.date() == date(2026, 6, 20)
            assert is_effectively_now(result.time())
            assert sut._popup is None

    class TestTimePopup:

        def test_alt_up_opens_popup(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is not None
            assert sut._popup.findChild(QTimeEdit) is not None

        def test_alt_up_when_open_closes_popup(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is not None
            qtbot.keyClick(sut, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.AltModifier)
            assert sut._popup is None

        def test_popup_initializes_from_current_time(self, sut):
            sut.setText(SOME_DATETIME_STRING)
            sut._show_time_popup()
            spinner = sut._popup.findChild(QTimeEdit)
            assert spinner.time() == QTime(9, 30, 0)

        def test_selecting_time_preserves_existing_date(self, sut):
            sut.setText(SOME_DATETIME_STRING)
            sut._show_time_popup()
            sut._on_time_selected(QTime(14, 45, 0))
            assert sut.get_datetime() == datetime(2026, 6, 15, 14, 45, 0)
            assert sut._popup is None

        def test_selecting_time_when_empty_defaults_date_to_today(self, sut):
            sut._show_time_popup()
            sut._on_time_selected(QTime(14, 45, 0))
            result = sut.get_datetime()
            assert result.date() == date.today()
            assert result.time() == time(14, 45, 0)
            assert sut._popup is None