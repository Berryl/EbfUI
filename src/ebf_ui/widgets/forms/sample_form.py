from dataclasses import dataclass
from types import SimpleNamespace

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
)

from ebf_ui.binding.command.command_binding import CommandBinding
from ebf_ui.binding.validation.validation_binding import (
    ValidationBinding,
    bind_validation,
)
from ebf_ui.binding.validation.violation_mapper import ViolationMapper
from ebf_ui.state.state_tracker import StateTracker
from ebf_ui.widgets.fields.button_binding import ButtonBinding
from ebf_ui.widgets.fields.line_edit_binding import LineEditBinding
from ebf_ui.widgets.forms.form_binding import FormBinding


@dataclass
class Person:
    name: str


class SampleForm(QWidget):

    def __init__(self):
        super().__init__()

        self._build_model()
        self._build_validation()

        self._setup_ui()
        self._setup_bindings()

    # region setup
    def _build_model(self) -> None:
        self.person = Person(name="")

        self.tracker = StateTracker(self.person)

    def _build_validation(self) -> None:
        def validate():
            if self.person.name.strip():
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

        self.validation = ValidationBinding(validate)

    def _setup_ui(self) -> None:
        self.setWindowTitle("Sample Form")

        layout = QVBoxLayout(self)

        self.name_line_edit = QLineEdit()
        self.save_button = QPushButton("Save")

        layout.addWidget(self.name_line_edit)
        layout.addWidget(self.save_button)

    def _setup_bindings(self) -> None:
        bind_validation(self.tracker, self.validation)

        self.save_command = CommandBinding(
            tracker=self.tracker,
            validation=self.validation,
            execute=self._save,
        )

        self.name_binding = LineEditBinding(
            line_edit=self.name_line_edit,
            tracker=self.tracker,
            get_value=lambda: self.person.name,
            set_value=lambda v: setattr(self.person, "name", v),
        )

        self.violation_mapper = ViolationMapper({
            "name": self.name_binding,
        })

        def sync_ui():
            if self.validation.result is not None:
                self.violation_mapper.apply(self.validation.result)

        self.name_binding.sync_ui = sync_ui

        self.save_button_binding = ButtonBinding(
            button=self.save_button,
            command=self.save_command,
        )

        self.form = FormBinding([
            self.name_binding,
            self.save_button_binding,
        ])

        self.tracker.begin_edit()

    # endregion

    def _save(self) -> None:
        print(f"Saved: {self.person.name}")

        self.tracker.begin_edit()
        self.form.refresh()