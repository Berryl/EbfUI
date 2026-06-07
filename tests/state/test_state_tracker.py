import pytest

from ebf_ui.state.state_events import StateTrackerEvent
from ebf_ui.state.state_tracker import StateTracker


class MyClass:
    def __init__(self):
        self.name = "original"


@pytest.fixture
def obj() -> MyClass:
    return MyClass()


@pytest.fixture
def sut(obj) -> StateTracker:
    return StateTracker(obj)


class TestStateTracker:
    def test_begin_edit_captures_original_state(self, sut: StateTracker):
        sut.begin_edit()

        assert sut.original == {"name": "original"}

    def test_is_dirty_is_false_immediately_after_begin_edit(self, sut: StateTracker):
        sut.begin_edit()

        assert not sut.is_dirty

    def test_is_dirty_is_true_after_update_edit(self, sut: StateTracker, obj: MyClass):
        sut.begin_edit()

        obj.name = "updated"
        sut.update_edit()

        assert sut.is_dirty

    def test_changes_returns_empty_dict_when_not_dirty(self, sut: StateTracker):
        sut.begin_edit()

        assert sut.changes == {}

    def test_changes_returns_changed_values(self, sut: StateTracker, obj: MyClass):
        sut.begin_edit()

        obj.name = "updated"
        sut.update_edit()

        assert sut.changes == {"name": ("original", "updated")}

    def test_end_edit_clears_state(self, sut: StateTracker):
        sut.begin_edit()

        sut.end_edit()

        assert sut.original is None
        assert sut.current is None
        assert not sut.is_dirty
        assert sut.changes == {}

    def test_cancel_edit_clears_state(self, sut: StateTracker, obj: MyClass):
        sut.begin_edit()

        obj.name = "updated"
        sut.update_edit()

        sut.cancel_edit()

        assert sut.original is None
        assert sut.current is None
        assert not sut.is_dirty
        assert sut.changes == {}

    class TestRequestedAttrsAndExclusions:
        def test_requested_attrs_limits_tracking_scope(self, obj: MyClass):
            sut = StateTracker(obj, requested_attrs=["name"])
            sut.begin_edit()

            obj.name = "updated"
            obj.extra = "ignored"
            sut.update_edit()

            assert sut.changes == {"name": ("original", "updated")}

        def test_exclusions_remove_attrs_from_tracking_scope(self, obj: MyClass):
            obj.value = 42
            sut = StateTracker(obj, exclusions=["value"])
            sut.begin_edit()

            obj.value = 99
            sut.update_edit()

            assert not sut.is_dirty

    class TestNestedPaths:
        @pytest.fixture
        def obj(self):
            class Parent:
                def __init__(self):
                    self.name = "original"

            class Child:
                def __init__(self):
                    self.parent = Parent()

            return Child()

        @pytest.fixture
        def sut(self, obj):
            return StateTracker(obj, requested_attrs=["parent.name"])

        def test_is_dirty_is_false_immediately_after_begin_edit(self, sut):
            sut.begin_edit()

            assert not sut.is_dirty

        def test_is_dirty_is_true_after_nested_attr_changes(self, sut, obj):
            sut.begin_edit()

            obj.parent.name = "updated"
            sut.update_edit()

            assert sut.is_dirty

        def test_changes_reflects_nested_attr(self, sut, obj):
            sut.begin_edit()

            obj.parent.name = "updated"
            sut.update_edit()

            assert sut.changes == {"parent.name": ("original", "updated")}

    class TestRestoreOnCancel:
        def test_cancel_edit_restores_original_values(self, sut: StateTracker, obj: MyClass):
            sut.begin_edit()

            obj.name = "updated"
            sut.update_edit()

            sut.cancel_edit()

            assert obj.name == "original"

        def test_end_edit_does_not_restore(self, sut: StateTracker, obj: MyClass):
            sut.begin_edit()

            obj.name = "updated"
            sut.update_edit()

            sut.end_edit()

            assert obj.name == "updated"

        def test_cancel_without_changes_leaves_instance_unchanged(
            self, sut: StateTracker, obj: MyClass
        ):
            sut.begin_edit()
            sut.cancel_edit()

            assert obj.name == "original"

        def test_cancel_restores_nested_attr(self, obj: MyClass):
            class Parent:
                def __init__(self):
                    self.name = "original"

            class Child:
                def __init__(self):
                    self.parent = Parent()

            child = Child()
            sut = StateTracker(child, requested_attrs=["parent.name"])
            sut.begin_edit()

            child.parent.name = "updated"
            sut.update_edit()

            sut.cancel_edit()

            assert child.parent.name == "original"

    class TestListeners:
        def test_begin_edit(self, sut: StateTracker):
            received = []
            sut.listeners.append(received.append)

            sut.begin_edit()

            assert received == [StateTrackerEvent.BEGIN_EDIT]

        def test_update_edit_notifies_dirty_changed_when_dirty_state_changes(
            self, sut: StateTracker, obj: MyClass
        ):
            received = []
            sut.listeners.append(received.append)

            sut.begin_edit()
            obj.name = "updated"
            sut.update_edit()

            assert received == [
                StateTrackerEvent.BEGIN_EDIT,
                StateTrackerEvent.DIRTY_CHANGED,
                StateTrackerEvent.UPDATE_EDIT,
            ]

        def test_update_edit_does_not_notify_dirty_changed_when_dirty_state_does_not_change(
            self, sut: StateTracker, obj: MyClass
        ):
            received = []
            sut.listeners.append(received.append)

            sut.begin_edit()
            obj.name = "updated"
            sut.update_edit()
            sut.update_edit()

            assert received == [
                StateTrackerEvent.BEGIN_EDIT,
                StateTrackerEvent.DIRTY_CHANGED,
                StateTrackerEvent.UPDATE_EDIT,
                StateTrackerEvent.UPDATE_EDIT,
            ]

        def test_update_edit_notifies_dirty_changed_when_dirty_state_returns_to_clean(
            self, sut: StateTracker, obj: MyClass
        ):
            received = []
            sut.listeners.append(received.append)

            sut.begin_edit()
            obj.name = "updated"
            sut.update_edit()
            obj.name = "original"
            sut.update_edit()

            assert received == [
                StateTrackerEvent.BEGIN_EDIT,
                StateTrackerEvent.DIRTY_CHANGED,
                StateTrackerEvent.UPDATE_EDIT,
                StateTrackerEvent.DIRTY_CHANGED,
                StateTrackerEvent.UPDATE_EDIT,
            ]

        def test_end_edit(self, sut: StateTracker):
            received = []
            sut.listeners.append(received.append)

            sut.begin_edit()
            sut.end_edit()

            assert received == [
                StateTrackerEvent.BEGIN_EDIT,
                StateTrackerEvent.END_EDIT,
            ]

        def test_cancel_edit(self, sut: StateTracker):
            received = []
            sut.listeners.append(received.append)

            sut.begin_edit()
            sut.cancel_edit()

            assert received == [
                StateTrackerEvent.BEGIN_EDIT,
                StateTrackerEvent.CANCEL_EDIT,
            ]

    class TestIsEditing:
        def test_is_false_before_begin_edit(self, sut):
            assert not sut.is_editing

        def test_is_true_after_begin_edit(self, sut):
            sut.begin_edit()

            assert sut.is_editing

        def test_is_false_after_end_edit(self, sut):
            sut.begin_edit()
            sut.end_edit()

            assert not sut.is_editing

        def test_is_false_after_cancel_edit(self, sut):
            sut.begin_edit()
            sut.cancel_edit()

            assert not sut.is_editing

    class TestOutOfSequenceGuards:
        def test_begin_edit_raises_if_already_editing(self, sut):
            sut.begin_edit()

            with pytest.raises(RuntimeError):
                sut.begin_edit()

        def test_update_edit_raises_if_not_editing(self, sut):
            with pytest.raises(RuntimeError):
                sut.update_edit()

        def test_end_edit_raises_if_not_editing(self, sut):
            with pytest.raises(RuntimeError):
                sut.end_edit()

        def test_cancel_edit_raises_if_not_editing(self, sut):
            with pytest.raises(RuntimeError):
                sut.cancel_edit()
