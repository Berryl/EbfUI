from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton

from ebf_ui.binding.command.command_binding import CommandBinding
from ebf_ui.binding.validation.validation_binding import ValidationBinding, bind_validation
from ebf_ui.binding.validation.violation_mapper import ViolationMapper
from ebf_ui.state.state_tracker import StateTracker
from ebf_ui.widgets.fields.button_binding import ButtonBinding
from ebf_ui.widgets.fields.line_edit_binding import LineEditBinding
from ebf_ui.widgets.forms.form_binding import FormBinding
from ebf_ui.widgets.styles import ERROR_STYLESHEET


@dataclass
class Person:
    name: str


def build_form(qtbot) -> SimpleNamespace:
    """Build the form harness. Do not call sync_ui() here — LineEditBinding does it."""
    calls: list[str] = []
    person = Person(name="original")

    tracker = StateTracker(person)

    def validate():
        if person.name.strip():
            return SimpleNamespace(
                is_valid=True,
                violations=[],
            )

        return SimpleNamespace(
            is_valid=False,
            violations=[
                SimpleNamespace(
                    field_name="name",
                    ui_error_message="Name is required",
                )
            ],
        )

    validation = ValidationBinding(validate)
    bind_validation(tracker, validation)

    save_binding = CommandBinding(
        tracker=tracker,
        validation=validation,
        execute=lambda: calls.append("saved"),
    )
    tracker.begin_edit()

    widget = QWidget()
    layout = QVBoxLayout(widget)

    line_edit = QLineEdit()
    save_button = QPushButton("Save")

    name_binding = LineEditBinding(
        line_edit=line_edit,
        tracker=tracker,
        get_value=lambda: person.name,
        set_value=lambda v: setattr(person, "name", v),
    )

    violation_mapper = ViolationMapper({"name": name_binding})

    def sync_ui():
        save_button.setEnabled(save_binding.is_enabled)
        if validation.result is not None:
            violation_mapper.apply(validation.result)

    name_binding.sync_ui = sync_ui

    button_binding = ButtonBinding(
        button=save_button,
        command=save_binding,
    )

    form = FormBinding([name_binding, button_binding])

    layout.addWidget(line_edit)
    layout.addWidget(save_button)

    qtbot.addWidget(widget)

    return SimpleNamespace(
        person=person,
        tracker=tracker,lj
        validation=validation,
        save_binding=save_binding,
        name_binding=name_binding,
        button_binding=button_binding,
        form=form,
        line_edit=line_edit,
        save_button=save_button,
        calls=calls,
        _root_widget=widget,  # keep Qt widget tree alive for the test
    )


@pytest.fixture
def form_harness(qtbot) -> SimpleNamespace:
    harness = build_form(qtbot)
    yield harness


class TestWhenModelIsNotValid:

    @pytest.mark.parametrize("blank_text", ["", "   ", "\t"])
    def test_save_is_disabled(self, form_harness, blank_text):
        h = form_harness

        h.line_edit.setText("blah")
        assert h.save_button.isEnabled()

        h.line_edit.setText(blank_text)

        assert not h.validation.is_valid
        assert h.line_edit.toolTip() == "Name is required"
        assert not h.save_button.isEnabled()


class TestWhenModelIsValidAndDirty:
    """ in this example the name is valid simply if it isn't blank"""

    def test_save_is_enabled(self, form_harness):
        h = form_harness

        assert not h.save_button.isEnabled()

        h.line_edit.setText("ted")

        assert h.person.name == "ted"
        assert h.tracker.is_dirty
        assert h.validation.is_valid
        assert h.save_button.isEnabled()

    def test_clicking_save_executes_command(self, form_harness):
        h = form_harness

        h.line_edit.setText("blah")
        h.save_button.click()

        assert h.calls == ["saved"]


class TestEdgeCases:

    def test_refresh_does_not_mark_tracker_dirty(self, qtbot):
        """External model change via refresh() should not mark the tracker dirty."""
        person = Person(name="original")
        tracker = StateTracker(person)
        tracker.begin_edit()

        line_edit = QLineEdit()
        qtbot.addWidget(line_edit)

        binding = LineEditBinding(
            line_edit=line_edit,
            tracker=tracker,
            get_value=lambda: person.name,
            set_value=lambda v: setattr(person, "name", v),
        )

        tracker.cancel_edit()

        person.name = "updated externally"
        binding.refresh()

        assert line_edit.text() == "updated externally"
        assert not tracker.is_dirty

    def test_model_value_of_none_displays_as_empty_text(self, qtbot):
        person = Person(name=None)
        tracker = StateTracker(person)
        tracker.begin_edit()

        line_edit = QLineEdit()
        qtbot.addWidget(line_edit)

        LineEditBinding(
            line_edit=line_edit,
            tracker=tracker,
            get_value=lambda: person.name,
            set_value=lambda v: setattr(person, "name", v),
        )

        assert line_edit.text() == ""
        assert not tracker.is_dirty


class TestSetError:
    class TestWhenError:
        def test_tooltip_displays_error(self, form_harness):
            form_harness.name_binding.set_errors(["Name is required"])

            assert form_harness.line_edit.toolTip() == "Name is required"

        def test_stylesheet_includes_error_style(self, form_harness):
            form_harness.name_binding.set_errors(["Name is required"])

            assert ERROR_STYLESHEET in form_harness.line_edit.styleSheet()

        def test_tooltip_stacks_multiple_errors(self, form_harness):
            form_harness.name_binding.set_errors(["Name is required", "Name is too long"])

            assert form_harness.line_edit.toolTip() == "Name is required<br>Name is too long"

    class TestWhenNoError:
        def test_tooltip_is_cleared(self, form_harness):
            form_harness.name_binding.set_errors(["Name is required"])
            form_harness.name_binding.set_errors([])

            assert form_harness.line_edit.toolTip() == ""

        def test_stylesheet_is_restored(self, form_harness):
            form_harness.name_binding.set_errors(["Name is required"])
            form_harness.name_binding.set_errors([])

            assert ERROR_STYLESHEET not in form_harness.line_edit.styleSheet()