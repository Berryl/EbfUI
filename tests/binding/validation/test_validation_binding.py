from dataclasses import dataclass
from types import SimpleNamespace

from ebf_ui.binding.validation.validation_binding import ValidationBinding, bind_validation
from ebf_ui.state.state_tracker import StateTracker


@dataclass
class FakeViolation:
    ui_error_message: str


@dataclass
class FakeResult:
    is_valid: bool
    violations: list[FakeViolation]


class TestValidationBinding:
    def test_update_exposes_ui_error_messages(self):
        message = "Name: is required"
        binding = ValidationBinding(
            lambda: FakeResult(is_valid=False, violations=[FakeViolation(message)])
        )

        binding.update()

        assert not binding.is_valid
        assert binding.ui_error_messages == [message]

    def test_before_update_is_neutral(self):
        binding = ValidationBinding(lambda: FakeResult(True, []))

        assert not binding.is_valid
        assert binding.violations == []
        assert binding.ui_error_messages == []

    class TestStateTrackerEvents:
        def test_begin_edit_triggers_update(self):
            calls = []

            class FakeValidation:
                @staticmethod
                def update():
                    calls.append("updated")

            tracker = StateTracker(SimpleNamespace(name="original"))
            bind_validation(tracker, FakeValidation())

            tracker.begin_edit()

            assert calls == ["updated"]

        def test_update_edit_triggers_update(self):
            calls = []

            class FakeValidation:
                @staticmethod
                def update():
                    calls.append("updated")

            tracker = StateTracker(SimpleNamespace(name="original"))
            bind_validation(tracker, FakeValidation())

            tracker.begin_edit()
            calls.clear()

            tracker.instance.name = "updated"
            tracker.update_edit()

            assert calls == ["updated"]
