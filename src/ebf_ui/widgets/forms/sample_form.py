from dataclasses import dataclass
from types import SimpleNamespace

from PySide6.QtWidgets import QWidget

from .form_binding import FormBinding
from .ui_sample_form import Ui_personForm
from ..fields.button_binding import ButtonBinding
from ..fields.line_edit_binding import LineEditBinding
from ...binding.command.command_binding import CommandBinding
from ...binding.validation.validation_binding import ValidationBinding, bind_validation
from ...binding.validation.violation_mapper import ViolationMapper
from ...state.state_tracker import StateTracker


@dataclass
class Person:
    name: str


class SampleForm(QWidget):

    def __init__(self):
        super().__init__()

        self._build_model()
        self._build_validation()

        self.ui = Ui_personForm()
        self.ui.setupUi(self)

        self._setup_bindings()

    # region build Model
    def _build_model(self) -> None:
        self.person = Person(name="")
        self.tracker = StateTracker(self.person)
    # endregion

    # region build Validation
    def _build_validation(self) -> None:
        def validate():
            if self.person.name.strip():
                return SimpleNamespace(is_valid=True, violations=[])

            return SimpleNamespace(
                is_valid=False,
                violations=[SimpleNamespace(field_name="name", ui_error_message="Name is required", )],
            )

        self.validation = ValidationBinding(validate)
    # endregion

    # region setup Bindings
    def _setup_bindings(self) -> None:
        bind_validation(self.tracker, self.validation)

        self.save_command_binding = CommandBinding(
            tracker=self.tracker,
            validation=self.validation,
            execute=self._save,
        )

        self.name_binding = LineEditBinding(
            line_edit=self.ui.nameLineEdit,
            tracker=self.tracker,
            get_value=lambda: self.person.name,
            set_value=lambda v: setattr(self.person, "name", v),
        )

        violation_mapper = ViolationMapper({"name": self.name_binding, })

        def sync_ui():
            if self.validation.result is not None:
                violation_mapper.apply(self.validation.result)

        self.name_binding.sync_ui = sync_ui

        self.save_button_binding = ButtonBinding(
            button=self.ui.saveButton,
            command=self.save_command_binding,
        )

        self.form = FormBinding([
            self.name_binding,
            self.save_button_binding,
        ])

        self.tracker.begin_edit()
    # endregion

    def _save(self) -> None:
        print(f"Saved: {self.person.name}")

        self.tracker.end_edit() # end edit to clear state
        self.tracker.begin_edit()
        self.form.refresh()
