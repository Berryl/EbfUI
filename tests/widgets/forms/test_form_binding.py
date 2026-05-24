from ebf_ui.widgets.forms.form_binding import FormBinding


class TestFormBinding:
    def test_refresh_calls_refresh_on_child_bindings(self):
        calls = []

        class Binding:
            @staticmethod
            def refresh():
                calls.append("refresh")

        sut = FormBinding([Binding(), Binding()])

        sut.refresh()

        assert calls == ["refresh", "refresh"]