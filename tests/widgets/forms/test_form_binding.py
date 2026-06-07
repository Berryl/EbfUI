from types import SimpleNamespace

from ebf_ui.widgets.forms.form_binding import FormBinding


class TestFormBinding:
    class TestRefresh:
        def test_child_bindings_with_refresh_method_are_called(self):
            calls = []

            binding = SimpleNamespace(refresh=lambda: calls.append("refresh"))

            sut = FormBinding([binding, binding])

            sut.refresh()

            assert calls == ["refresh", "refresh"]

        def test_child_bindings_without_refresh_method_are_ignored(self):
            sut = FormBinding([object()])
            sut.refresh()  # should not raise

        def test_when_no_child_bindings_there_is_no_error(self):
            sut = FormBinding()
            sut.refresh()  # should not raise
