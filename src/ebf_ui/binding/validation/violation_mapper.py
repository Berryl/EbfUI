from typing import Protocol

from ebf_ui.binding.validation.validation_binding import ValidationState


class ErrorTarget(Protocol):
    def set_error(self, message: str | None) -> None: ...


class ViolationMapper:
    def __init__(self, bindings: dict[str, ErrorTarget]):
        self._bindings = bindings

    def apply(self, validation: ValidationState) -> None:
        for binding in self._bindings.values():
            binding.set_error(None)

        for violation in validation.violations:
            binding = self._bindings.get(violation.field_name)
            if binding is not None:
                binding.set_error(violation.ui_error_message)
