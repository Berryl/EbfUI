from ebf_ui.widgets.forms.sample_form import SampleForm


class TestSampleForm:
    def test_save_resets_dirty_state_and_disables_save(self, qtbot):
        sut = SampleForm()
        qtbot.addWidget(sut)

        sut.ui.nameLineEdit.setText("Ted")

        assert sut.tracker.is_dirty
        assert sut.ui.saveButton.isEnabled()

        sut.ui.saveButton.click()

        assert not sut.tracker.is_dirty
        assert not sut.ui.saveButton.isEnabled()
