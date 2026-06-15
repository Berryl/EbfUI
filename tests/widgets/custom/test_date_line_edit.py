from datetime import date, timedelta

import pytest
from PySide6.QtCore import Qt

from ebf_ui.widgets.custom.date_line_edit import DateLineEdit


class TestDateLineEdit:

    @pytest.fixture
    def sut(self, qtbot) -> DateLineEdit:
        widget = DateLineEdit()
        qtbot.addWidget(widget)
        return widget

    class TestGetDate:

        def test_returns_none_when_empty(self, sut):
            assert sut.get_date() is None

        def test_returns_none_when_unparseable(self, sut):
            sut.setText("not a date")
            assert sut.get_date() is None

        def test_returns_parsed_date_when_valid(self, sut):
            sut.setText("06-15-2026")
            assert sut.get_date() == date(2026, 6, 15)

    class TestKeyboardShortcuts:

        def test_t_fills_today(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_T)
            assert sut.get_date() == date.today()

        def test_plus_increments_current_date(self, sut, qtbot):
            sut.setText("06-15-2026")
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert sut.get_date() == date(2026, 6, 16)

        def test_minus_decrements_current_date(self, sut, qtbot):
            sut.setText("06-15-2026")
            qtbot.keyClick(sut, Qt.Key.Key_Minus)
            assert sut.get_date() == date(2026, 6, 14)

        def test_plus_falls_back_to_today_when_empty(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert sut.get_date() == date.today() + timedelta(days=1)

        def test_minus_falls_back_to_today_when_empty(self, sut, qtbot):
            qtbot.keyClick(sut, Qt.Key.Key_Minus)
            assert sut.get_date() == date.today() - timedelta(days=1)

        def test_plus_handles_month_boundary(self, sut, qtbot):
            sut.setText("06-30-2026")
            qtbot.keyClick(sut, Qt.Key.Key_Plus)
            assert sut.get_date() == date(2026, 7, 1)

        def test_minus_handles_month_boundary(self, sut, qtbot):
            sut.setText("07-01-2026")
            qtbot.keyClick(sut, Qt.Key.Key_Minus)
            assert sut.get_date() == date(2026, 6, 30)

    class TestFlexParsing:

        def test_reformats_on_focus_out(self, sut, qtbot):
            sut.setText("Jun-15")
            sut.clearFocus()
            assert sut.text() == f"06-15-{date.today().year}"

        def test_leaves_invalid_text_as_is_on_focus_out(self, sut, qtbot):
            sut.setText("not a date")
            sut.clearFocus()
            assert sut.text() == "not a date"

        def test_leaves_empty_field_as_is_on_focus_out(self, sut, qtbot):
            sut.clearFocus()
            assert sut.text() == ""

        def test_reformats_on_enter(self, sut, qtbot):
            sut.setText("Jun-15")
            qtbot.keyClick(sut, Qt.Key.Key_Return)
            assert sut.text() == f"06-15-{date.today().year}"

        def test_canonical_format_is_mm_dd_yyyy(self, sut, qtbot):
            sut.setText("6-15-2026")
            sut.clearFocus()
            assert sut.text() == "06-15-2026"

        def test_explicit_year_is_preserved(self, sut, qtbot):
            sut.setText("Jun-5 2027")
            sut.clearFocus()
            assert sut.text() == "06-05-2027"