from types import SimpleNamespace

import pytest

from ebf_ui.binding.validation.validation_binding import ValidationViolation
from ebf_ui.binding.validation.violation_mapper import ViolationMapper


class TestViolationMapper:

    # region fixtures
    @pytest.fixture
    def name_missing_violation(self) -> ValidationViolation:
        return SimpleNamespace(field_name="name", ui_error_message="Name is required")

    @pytest.fixture
    def name_too_long_violation(self) -> ValidationViolation:
        return SimpleNamespace(field_name="name", ui_error_message="Name is too long")

    @pytest.fixture
    def email_missing_violation(self) -> ValidationViolation:
        return SimpleNamespace(field_name="email", ui_error_message="Email is required")

    @pytest.fixture
    def received(self):
        return []
    # endregion

    @pytest.fixture
    def sut(self, received) -> ViolationMapper:
        return ViolationMapper({"name": SimpleNamespace(set_errors=received.append)})

    class TestWhenSingleViolation:
        class TestWhenBindingMatches:

            def test_violation_is_applied(self, sut, name_missing_violation, received):
                validation = SimpleNamespace(is_valid=False, violations=[name_missing_violation])

                sut.apply(validation)

                assert received == [["Name is required"]]

        class TestWhenNoBindingMatches:

            def test_violation_is_safely_ignored(self, sut, email_missing_violation, received):
                validation = SimpleNamespace(is_valid=False, violations=[email_missing_violation])

                sut.apply(validation)

                assert received == [[]]

        class TestUnviolatedBindings:

            def test_remain_cleared(self, name_missing_violation):
                name_received = []
                email_received = []
                validation = SimpleNamespace(is_valid=False, violations=[name_missing_violation])
                sut = ViolationMapper({
                    "name": SimpleNamespace(set_errors=name_received.append),
                    "email": SimpleNamespace(set_errors=email_received.append),
                })

                sut.apply(validation)

                assert name_received == [["Name is required"]]
                assert email_received == [[]]

    class TestWhenMultipleViolations:

        def test_same_field_are_stacked(self, sut, name_missing_violation, name_too_long_violation, received):
            validation = SimpleNamespace(is_valid=False, violations=[name_missing_violation, name_too_long_violation])

            sut.apply(validation)

            assert received == [["Name is required", "Name is too long"]]

    class TestWhenNoViolations:

        def test_all_bindings_are_cleared(self, sut, received):
            validation = SimpleNamespace(is_valid=True, violations=[])

            sut.apply(validation)

            assert received == [[]]
