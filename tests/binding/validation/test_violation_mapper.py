from types import SimpleNamespace

from ebf_ui.binding.validation.validation_binding import ErrorTarget
from ebf_ui.binding.validation.violation_mapper import ViolationMapper


class TestViolationMapper:

    def test_applies_error_to_matching_binding(self):
        received = []

        class Binding(ErrorTarget):
            def set_error(self, message: str | None) -> None:
                received.append(message)

        violation = SimpleNamespace(
            field_name="name",
            ui_error_message="Name is required",
        )

        validation = SimpleNamespace(
            is_valid=False,
            violations=[violation],
        )

        sut = ViolationMapper({
            "name": Binding(),
        })

        sut.apply(validation)

        assert received == [
            None,
            "Name is required",
        ]