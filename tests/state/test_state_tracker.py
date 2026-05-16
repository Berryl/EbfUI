from ebf_ui.state.state_tracker import StateTracker


class TestStateTracker:
    class MyClass:
        def __init__(self):
            self.name = "original"

    def test_begin_edit_captures_original_state(self):
        obj = self.MyClass()

        sut = StateTracker(obj)

        sut.begin_edit()

        assert sut.original == {
            "name": "original"
        }

    def test_is_dirty_is_false_immediately_after_begin_edit(self):
        obj = self.MyClass()
        sut = StateTracker(obj)

        sut.begin_edit()

        assert not sut.is_dirty

    def test_is_dirty_is_true_after_update_edit(self):
        obj = self.MyClass()
        sut = StateTracker(obj)
        sut.begin_edit()

        obj.name = "updated"
        sut.update_edit()

        assert sut.is_dirty

    def test_changes_returns_empty_dict_when_not_dirty(self):
        obj = self.MyClass()
        sut = StateTracker(obj)

        sut.begin_edit()

        assert sut.changes == {}

    def test_changes_returns_changed_values(self):
        obj = self.MyClass()
        sut = StateTracker(obj)
        sut.begin_edit()

        obj.name = "updated"
        sut.update_edit()

        assert sut.changes == {
            "name": ("original", "updated")
        }

    def test_end_edit_clears_state(self):
        obj = self.MyClass()
        sut = StateTracker(obj)
        sut.begin_edit()

        sut.end_edit()

        assert sut.original is None
        assert sut.current is None
        assert not sut.is_dirty
        assert sut.changes == {}