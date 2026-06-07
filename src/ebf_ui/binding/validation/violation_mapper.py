from typing import Protocol

from ebf_ui.binding.validation.validation_binding import ValidationState


class ErrorTarget(Protocol):
    def set_errors(self, messages: list[str]) -> None: ...


class ViolationMapper:
    def __init__(self, bindings: dict[str, ErrorTarget]):
        self._bindings = bindings

    def apply(self, validation: ValidationState) -> None:
        messages: dict[str, list[str]] = {field: [] for field in self._bindings}

        for violation in validation.violations:
            if violation.field_name in messages:
                messages[violation.field_name].append(violation.ui_error_message)

        for field, binding in self._bindings.items():
            binding.set_errors(messages[field])
