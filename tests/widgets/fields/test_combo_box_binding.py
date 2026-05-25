from dataclasses import dataclass

import pytest
from PySide6.QtWidgets import QComboBox

from ebf_ui.state.state_tracker import StateTracker
from ebf_ui.widgets.fields.combo_box_binding import ComboBoxBinding
from ebf_ui.widgets.styles import ERROR_STYLESHEET


@dataclass
class Person:
    status: str | None


ITEMS = ["active", "inactive"]


class TestComboBoxBinding:

    @pytest.fixture
    def person(self):
        return Person(status="active")

    @pytest.fixture
    def tracker(self, person):
        t = StateTracker(person)
        t.begin_edit()
        return t

    @pytest.fixture
    def combo(self, qtbot):
        c = QComboBox()
        qtbot.addWidget(c)
        return c

    @pytest.fixture
    def sut(self, combo, tracker, person):
        return ComboBoxBinding(
            combo_box=combo,
            tracker=tracker,
            items=ITEMS,
            get_value=lambda: person.status,
            set_value=lambda v: setattr(person, "status", v),
        )

    class TestItemLoading:

        def test_all_items_are_loaded(self, sut):
            cbo = sut.combo_box
            assert cbo.count() == 2
            assert cbo.itemText(0) == "active"
            assert cbo.itemText(1) == "inactive"

        def test_get_text_can_format_display(self, combo, tracker, person):
            binding = ComboBoxBinding(
                combo_box=combo,
                tracker=tracker,
                items=ITEMS,
                get_value=lambda: person.status,
                set_value=lambda v: setattr(person, "status", v),
                get_text=lambda v: v.upper(),
            )

            cbo = binding.combo_box
            assert cbo.itemText(0) == "ACTIVE"
            assert cbo.itemText(1) == "INACTIVE"

    class TestInitialSelection:

        # region helper
        @staticmethod
        def _bind_person_with_status_of(status: str | None, qtbot) -> ComboBoxBinding:
            person = Person(status=status)
            tracker = StateTracker(person)
            tracker.begin_edit()
            combo = QComboBox()
            qtbot.addWidget(combo)

            binding = ComboBoxBinding(
                combo_box=combo,
                tracker=tracker,
                items=ITEMS,
                get_value=lambda: person.status,
                set_value=lambda v: setattr(person, "status", v),
            )
            return binding

        # endregion

        def test_model_value_is_reflected(self, qtbot):
            binding = self._bind_person_with_status_of("inactive", qtbot)

            assert binding.combo_box.currentText() == "inactive"

        def test_tracker_is_not_made_dirty(self, sut):
            assert not sut.tracker.is_dirty

        def test_when_none_value_then_shows_no_selection(self, qtbot):
            binding = self._bind_person_with_status_of(None, qtbot)
            assert binding.combo_box.currentIndex() == -1

        def test_when_unknown_value_then_shows_no_selection(self, qtbot):
            binding = self._bind_person_with_status_of("unknown", qtbot)
            assert binding.combo_box.currentIndex() == -1

    class TestUserSelection:

        def test_updates_model(self, person, sut):
            sut.combo_box.setCurrentIndex(1)

            assert person.status == "inactive"

        def test_marks_tracker_dirty(self, tracker, sut):
            sut.combo_box.setCurrentIndex(1)

            assert tracker.is_dirty

        def test_deselecting_sets_none_on_model(self, person, sut):
            sut.combo_box.setCurrentIndex(-1)

            assert person.status is None

    class TestRefresh:

        def test_updates_display(self, person, sut):
            sut.tracker.cancel_edit()
            person.status = "inactive"
            sut.refresh()

            assert sut.combo_box.currentText() == "inactive"

        def test_does_not_mark_tracker_dirty(self, person, sut):
            sut.tracker.cancel_edit()
            person.status = "inactive"
            sut.refresh()

            assert not sut.tracker.is_dirty

    class TestSetError:

        def test_tooltip_displays_error(self, sut):
            sut.set_errors(["Name is required"])
            assert sut.combo_box.toolTip() == "Name is required"

        def test_stylesheet_includes_error_style(self, sut):
            sut.set_errors(["Name is required"])
            assert ERROR_STYLESHEET in sut.combo_box.styleSheet()

        def test_tooltip_stacks_multiple_errors(self, sut):
            sut.set_errors(["Name is required", "Name is too long"])
            assert sut.combo_box.toolTip() == "Name is required<br>Name is too long"

        class TestWhenNoError:

            def test_tooltip_is_cleared(self, sut):
                sut.set_errors(["Name is required"])
                sut.set_errors([])
                assert sut.combo_box.toolTip() == ""

            def test_stylesheet_is_restored(self, sut):
                sut.set_errors(["Name is required"])
                sut.set_errors([])
                assert ERROR_STYLESHEET not in sut.combo_box.styleSheet()
