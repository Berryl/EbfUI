from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton

from ebf_ui.binding.command.command_binding import CommandBinding
from ebf_ui.binding.validation.validation_binding import ValidationBinding, bind_validation
from ebf_ui.state.state_tracker import StateTracker
from ebf_ui.widgets.fields.line_edit_binding import LineEditBinding


@dataclass
class Person:
    name: str


def build_form(qtbot) -> SimpleNamespace:
    """Build the form harness. Do not call sync_ui() here — LineEditBinding does it."""
    calls: list[str] = []
    person = Person(name="original")

    tracker = StateTracker(person)
    tracker.begin_edit()

    def validate():
        return SimpleNamespace(
            is_valid=bool(person.name.strip()),
            violations=[],
        )

    validation = ValidationBinding(validate)
    bind_validation(tracker, validation)

    save_binding = CommandBinding(
        tracker=tracker,
        validation=validation,
        execute=lambda: calls.append("saved"),
    )

    widget = QWidget()
    layout = QVBoxLayout(widget)

    line_edit = QLineEdit()
    save_button = QPushButton("Save")

    name_binding = LineEditBinding(
        line_edit=line_edit,
        tracker=tracker,
        get_value=lambda: person.name,
        set_value=lambda v: setattr(person, "name", v),
        sync_ui=lambda: save_button.setEnabled(save_binding.is_enabled),
    )

    layout.addWidget(line_edit)
    layout.addWidget(save_button)

    save_button.clicked.connect(save_binding.execute)

    qtbot.addWidget(widget)

    return SimpleNamespace(
        person=person,
        tracker=tracker,
        validation=validation,
        save_binding=save_binding,
        name_binding=name_binding,
        line_edit=line_edit,
        save_button=save_button,
        calls=calls,
        _root_widget=widget,          # for cleanup
    )


@pytest.fixture
def form_harness(qtbot) -> SimpleNamespace:
    harness = build_form(qtbot)
    yield harness

    # Clean up Qt objects to prevent "already deleted" errors
    if hasattr(harness, "_root_widget") and harness._root_widget is not None:
        harness._root_widget.deleteLater()


def test_save_is_enabled_when_text_is_not_blank(form_harness):
    h = form_harness

    assert not h.save_button.isEnabled()

    h.line_edit.setText("ted")

    assert h.person.name == "ted"
    assert h.tracker.is_dirty
    assert h.validation.is_valid
    assert h.save_button.isEnabled()


@pytest.mark.parametrize("blank_text", ["", "   ", "\t"])
def test_save_is_disabled_when_text_is_blank(form_harness, blank_text):
    h = form_harness

    h.line_edit.setText("blah")
    assert h.save_button.isEnabled()

    h.line_edit.setText(blank_text)

    assert not h.validation.is_valid
    assert not h.save_button.isEnabled()


def test_clicking_save_executes_command(form_harness):
    h = form_harness

    h.line_edit.setText("blah")
    h.save_button.click()

    assert h.calls == ["saved"]

def test_refresh_does_not_mark_tracker_dirty(form_harness):
    """External model change via refresh() should not mark the tracker dirty."""
    person = Person(name="original")
    tracker = StateTracker(person)
    tracker.begin_edit()

    line_edit = QLineEdit()

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
