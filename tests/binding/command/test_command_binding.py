from types import SimpleNamespace

import pytest

from ebf_ui.binding.command.command_binding import CommandBinding, CommandBindingEvent
from ebf_ui.state.state_tracker import StateTracker


class TestCommandBinding:

    @pytest.fixture
    def tracker(self) -> StateTracker:
        return StateTracker(SimpleNamespace(name="original"))

    @pytest.fixture
    def to_execute(self):
        def _execute():
            pass

        return _execute

    class TestIsEnabled:
        class TestWhenDisabled:

            def test_when_not_editing(self, tracker, to_execute):
                validation = SimpleNamespace(is_valid=True)

                sut = CommandBinding(tracker, validation, to_execute)
                assert not tracker.is_editing

                assert not sut.is_enabled

            def test_when_editing_but_not_dirty(self, tracker, to_execute):
                validation = SimpleNamespace(is_valid=True)
                sut = CommandBinding(tracker, validation, to_execute)

                tracker.begin_edit()

                assert tracker.is_editing
                assert not tracker.is_dirty

                assert not sut.is_enabled

            def test_dirty_but_not_valid(self, tracker, to_execute):
                validation = SimpleNamespace(is_valid=False)
                sut = CommandBinding(tracker, validation, to_execute)

                tracker.begin_edit()
                tracker.instance.name = "updated"
                tracker.update_edit()

                assert tracker.is_dirty
                assert not validation.is_valid

                assert not sut.is_enabled

        class TestWhenEnabled:
            def test_dirty_and_valid(self, tracker, to_execute):
                validation = SimpleNamespace(is_valid=True)
                sut = CommandBinding(tracker, validation, to_execute)

                tracker.begin_edit()
                tracker.instance.name = "updated"
                tracker.update_edit()

                assert tracker.is_dirty
                assert validation.is_valid

                assert sut.is_enabled

    class TestStateTrackerEvents:
        def test_notifies_when_enabled_changes(self, tracker, to_execute):
            validation = SimpleNamespace(is_valid=True)
            sut = CommandBinding(tracker, validation, to_execute)
            received = []

            sut.listeners.append(received.append)

            tracker.begin_edit()

            tracker.instance.name = "updated"
            tracker.update_edit()

            tracker.instance.name = "original"
            tracker.update_edit()

            assert received == [
                CommandBindingEvent.ENABLED_CHANGED,
                CommandBindingEvent.ENABLED_CHANGED,
            ]

    class TestExecutionCalls:
        def test_not_called_when_disabled(self):
            calls = []

            def execute():
                calls.append("executed")

            tracker = StateTracker(SimpleNamespace(name="original"))
            validation = SimpleNamespace(is_valid=False)

            sut = CommandBinding(
                tracker=tracker,
                validation=validation,
                execute=execute,
            )

            assert not sut.is_enabled
            sut.execute()

            assert calls == []

        def test_execute_calls_command_when_enabled(self):
            calls = []

            def execute():
                calls.append("executed")

            tracker = StateTracker(SimpleNamespace(name="original"))
            validation = SimpleNamespace(is_valid=True)

            sut = CommandBinding(
                tracker=tracker,
                validation=validation,
                execute=execute,
            )

            tracker.begin_edit()
            tracker.instance.name = "updated"
            tracker.update_edit()

            assert sut.is_enabled
            sut.execute()

            assert calls == ["executed"]
