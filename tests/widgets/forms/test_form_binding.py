from types import SimpleNamespace

from ebf_ui.widgets.forms.form_binding import FormBinding


class TestFormBinding:
    def test_refresh_calls_refresh_on_child_bindings(self):
        calls = []

        binding = SimpleNamespace(refresh=lambda: calls.append("refresh"))

        sut = FormBinding([binding, binding])

        sut.refresh()

        assert calls == ["refresh", "refresh"]

    def test_refresh_skips_bindings_without_refresh(self):
        sut = FormBinding([object()])
        sut.refresh()  # should not raise