from types import SimpleNamespace

from ebf_ui.binding.command.command_binding import CommandBinding
from ebf_ui.state.state_tracker import StateTracker


class TestCommandBinding:
    class TestIsEnabled:
        class TestWhenDisabled:

            def test_when_not_editing(self):
                tracker = StateTracker(SimpleNamespace(name="original"))
                validation = SimpleNamespace(is_valid=True)

                sut = CommandBinding(tracker, validation)
                assert not tracker.is_editing

                assert not sut.is_enabled

            def test_when_editing_but_not_dirty(self):
                tracker = StateTracker(SimpleNamespace(name="original"))
                validation = SimpleNamespace(is_valid=True)
                sut = CommandBinding(tracker, validation)

                tracker.begin_edit()

                assert tracker.is_editing
                assert not tracker.is_dirty

                assert not sut.is_enabled

            def test_dirty_but_not_valid(self):
                tracker = StateTracker(SimpleNamespace(name="original"))
                validation = SimpleNamespace(is_valid=False)
                sut = CommandBinding(tracker, validation)

                tracker.begin_edit()
                tracker.instance.name = "updated"
                tracker.update_edit()

                assert tracker.is_dirty
                assert not validation.is_valid

                assert not sut.is_enabled

        class TestWhenEnabled:
            def test_dirty_and_valid(self):
                tracker = StateTracker(SimpleNamespace(name="original"))
                validation = SimpleNamespace(is_valid=True)
                sut = CommandBinding(tracker, validation)

                tracker.begin_edit()
                tracker.instance.name = "updated"
                tracker.update_edit()

                assert tracker.is_dirty
                assert validation.is_valid

                assert sut.is_enabled
