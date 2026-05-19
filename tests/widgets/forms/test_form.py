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

def test_typing_updates_model_and_enables_save(qtbot):
    person = Person(name="original")

    tracker = StateTracker(person, requested_attrs=["name"])
    tracker.begin_edit()

    validation = ValidationBinding(
        lambda: ValidationResult(bool(person.name.strip()))
    )
    bind_validation(tracker, validation)

    save_binding = CommandBinding(
        tracker=tracker,
        validation=validation,
        execute=lambda: None,
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

    sync_ui()

    qtbot.addWidget(widget)

    assert not save_button.isEnabled()

    line_edit.setText("updated")

    assert person.name == "updated"
    assert tracker.is_dirty
    assert validation.is_valid
    assert save_button.isEnabled()