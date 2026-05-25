from types import SimpleNamespace

from ebf_ui.binding.validation.violation_mapper import ViolationMapper, ErrorTarget


class TestViolationMapper:
    class TestApply:

        def test_violation_is_bound_to_matching_binding(self):
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

        def test_non_matching_violation_is_ignored(self):
            received = []

            class Binding(ErrorTarget):
                def set_error(self, message: str | None) -> None:
                    received.append(message)

            violation = SimpleNamespace(
                field_name="email",
                ui_error_message="Email is required",
            )

            validation = SimpleNamespace(
                is_valid=False,
                violations=[violation],
            )

            sut = ViolationMapper({
                "name": Binding(),
            })

            sut.apply(validation)

            assert received == [None]

        def test_clears_previous_error_when_validation_has_no_violations(self):
            received = []

            class Binding(ErrorTarget):
                def set_error(self, message: str | None) -> None:
                    received.append(message)

            validation = SimpleNamespace(
                is_valid=True,
                violations=[],
            )

            sut = ViolationMapper({
                "name": Binding(),
            })

            sut.apply(validation)

            assert received == [None]