from datetime import date, timedelta

import pytest
from PySide6.QtCore import Qt

from ebf_ui.widgets.custom.date_line_edit import DateLineEdit


def _fmt(d: date) -> str:
    """Canonical display format: e.g. 'Jun-5 2026'"""
    return f"{d.strftime('%b')}-{d.day} {d.year}"


SOME_DATE_STRING = "Jun-15 2026"
SOME_DATE = date(2026, 6, 15)


class TestDateLineEdit:

    @pytest.fixture
    def sut(self, qtbot) -> DateLineEdit:
        widget = DateLineEdit()
        qtbot.addWidget(widget)
        return widget

    class TestGetDate:

        @pytest.mark.parametrize("raw", [None, "", "blah"])
        def test_returns_none_when_text_is_empty_or_unparseable(self, sut, raw):
            sut.setText(raw)
            assert sut.get_date() is None

        def test_returns_parsed_date_when_valid(self, sut):
            sut.setText(SOME_DATE_STRING)
            assert sut.get_date() == SOME_DATE

    class TestKeyboardShortcuts:
        class TestTodayWith_t:

            def test_when_no_text_then_returns_today(self, sut, qtbot):
                qtbot.keyClick(sut, Qt.Key.Key_T)
                assert sut.text() == _fmt(date.today())

        class TestIncrementingWith_plus:

            def test_increments_current_date(self, sut, qtbot):
                sut.setText(SOME_DATE_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Plus)
                assert sut.text() == _fmt(SOME_DATE + timedelta(days=1))

            def test_when_empty_text_falls_back_to_today_(self, sut, qtbot):
                qtbot.keyClick(sut, Qt.Key.Key_Plus)
                assert sut.text() == _fmt(date.today() + timedelta(days=1))

            def test_can_handle_month_boundary(self, sut, qtbot):
                sut.setText("Jun-30 2026")
                qtbot.keyClick(sut, Qt.Key.Key_Plus)
                assert sut.text() == _fmt(date(2026, 7, 1))

        class TestDecrementingWith_minus:
            def test_decrements_current_date(self, sut, qtbot):
                sut.setText(SOME_DATE_STRING)
                qtbot.keyClick(sut, Qt.Key.Key_Minus)
                assert sut.text() == _fmt(date.today() - timedelta(days=1))

            def test_minus_falls_back_to_today_when_empty(self, sut, qtbot):
                qtbot.keyClick(sut, Qt.Key.Key_Minus)
                assert sut.text() == _fmt(date.today() - timedelta(days=1))

            def test_minus_handles_month_boundary(self, sut, qtbot):
                sut.setText("Jul-1 2026")
                qtbot.keyClick(sut, Qt.Key.Key_Minus)
                assert sut.text() == _fmt(date(2026, 6, 30))

    class TestFlexParsing:

        def test_reformats_on_focus_out(self, sut):
            sut.setText("Jun-15")
            sut._try_reformat()
            assert sut.text() == _fmt(date(date.today().year, 6, 15))

        def test_leaves_invalid_text_as_is(self, sut):
            sut.setText("not a date")
            sut._try_reformat()
            assert sut.text() == "not a date"

        def test_leaves_empty_field_as_is(self, sut):
            sut._try_reformat()
            assert sut.text() == ""

        def test_explicit_year_is_preserved(self, sut):
            sut.setText("Jun-5 2027")
            sut._try_reformat()
            assert sut.text() == "Jun-5 2027"
