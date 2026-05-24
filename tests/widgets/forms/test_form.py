from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton

from ebf_ui.binding.command.command_binding import CommandBinding
from ebf_ui.binding.validation.validation_binding import ValidationBinding, bind_validation
from ebf_ui.state.state_tracker import StateTracker


@dataclass
class Person:
    name: str


class ValidationResult:
    def __init__(self, is_valid: bool):
        self.is_valid = is_valid
        self.violations = []


@dataclass
class FormHarness:
    person: Person
    tracker: StateTracker
    validation: ValidationBinding
    save_binding: CommandBinding
    widget: QWidget
    line_edit: QLineEdit
    save_button: QPushButton
    calls: list[str]


def build_form(qtbot) -> FormHarness:
    calls = []
    person = Person(name="original")

    tracker = StateTracker(person)
    tracker.begin_edit()

    validation = ValidationBinding(
        lambda: ValidationResult(bool(person.name.strip()))
    )
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

    layout.addWidget(line_edit)
    layout.addWidget(save_button)

    def sync_ui():
        save_button.setEnabled(save_binding.is_enabled)

    def on_text_changed(text: str):
        person.name = text
        tracker.update_edit()
        sync_ui()

    line_edit.textChanged.connect(on_text_changed)
    save_button.clicked.connect(save_binding.execute)

    sync_ui()
    qtbot.addWidget(widget)

    return FormHarness(
        person=person,
        tracker=tracker,
        validation=validation,
        save_binding=save_binding,
        widget=widget,
        line_edit=line_edit,
        save_button=save_button,
        calls=calls,
    )


def test_save_is_enabled_when_text_is_not_blank(qtbot):
    h = build_form(qtbot)

    assert not h.save_button.isEnabled()

    h.line_edit.setText("ted")

    assert h.person.name == "ted"
    assert h.tracker.is_dirty
    assert h.validation.is_valid
    assert h.save_button.isEnabled()


def test_save_is_disabled_when_text_is_cleared(qtbot):
    h = build_form(qtbot)

    h.line_edit.setText("blah")
    assert h.save_button.isEnabled()

    h.line_edit.setText("")

    assert not h.validation.is_valid
    assert not h.save_button.isEnabled()


def test_clicking_save_executes_command(qtbot):
    h = build_form(qtbot)

    h.line_edit.setText("blah")

    assert h.save_button.isEnabled()

    h.save_button.click()

    assert h.calls == ["saved"]
