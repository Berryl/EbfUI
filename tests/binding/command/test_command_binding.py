from types import SimpleNamespace

import pytest

from ebf_ui.binding.command.command_binding import CommandBinding, CommandBindingEvent
from ebf_ui.state.state_tracker import StateTracker


class TestCommandBinding:

    @pytest.fixture
    def tracker(self) -> StateTracker:
        return StateTracker(SimpleNamespace(name="original"))

    class TestIsEnabled:
        class TestWhenDisabled:

            def test_when_not_editing(self, tracker):
                validation = SimpleNamespace(is_valid=True)

                sut = CommandBinding(tracker, validation, lambda: None)
                assert not tracker.is_editing

                assert not sut.is_enabled

            def test_when_editing_but_not_dirty(self, tracker):
                validation = SimpleNamespace(is_valid=True)
                sut = CommandBinding(tracker, validation, lambda: None)

                tracker.begin_edit()

                assert tracker.is_editing
                assert not tracker.is_dirty

                assert not sut.is_enabled

            def test_dirty_but_not_valid(self, tracker):
                validation = SimpleNamespace(is_valid=False)
                sut = CommandBinding(tracker, validation, lambda: None)

                tracker.begin_edit()
                tracker.instance.name = "updated"
                tracker.update_edit()

                assert tracker.is_dirty
                assert not validation.is_valid

                assert not sut.is_enabled

        class TestWhenEnabled:
            def test_dirty_and_valid(self, tracker):
                validation = SimpleNamespace(is_valid=True)
                sut = CommandBinding(tracker, validation, lambda: None)

                tracker.begin_edit()
                tracker.instance.name = "updated"
                tracker.update_edit()

                assert tracker.is_dirty
                assert validation.is_valid

                assert sut.is_enabled

    class TestStateTrackerEvents:
        def test_notifies_when_enabled_changes(self, tracker):
            validation = SimpleNamespace(is_valid=True)
            sut = CommandBinding(tracker, validation, lambda: None)
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
        def test_not_called_when_disabled(self, tracker):
            calls = []

            def execute():
                calls.append("executed")

            validation = SimpleNamespace(is_valid=False)

            sut = CommandBinding(
                tracker=tracker,
                validation=validation,
                execute=execute,
            )

            assert not sut.is_enabled
            sut.execute()

            assert calls == []

        def test_called_when_enabled(self, tracker):
            calls = []

            def execute():
                calls.append("executed")

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

        def test_notifies_after_executed(self, tracker):
            validation = SimpleNamespace(is_valid=True)
            received = []

            sut = CommandBinding(
                tracker=tracker,
                validation=validation,
                execute=lambda: None,
            )
            sut.listeners.append(received.append)

            tracker.begin_edit()
            tracker.instance.name = "updated"
            tracker.update_edit()

            sut.execute()

            assert received == [
                CommandBindingEvent.ENABLED_CHANGED,
                CommandBindingEvent.EXECUTED,
            ]

        def test_does_not_notify_when_disabled(self, tracker):
            validation = SimpleNamespace(is_valid=True)
            received = []

            sut = CommandBinding(tracker, validation, lambda: None)
            sut.listeners.append(received.append)

            sut.execute()

            assert received == []

