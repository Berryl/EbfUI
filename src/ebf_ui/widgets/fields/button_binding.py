from PySide6.QtWidgets import QPushButton

from ebf_ui.binding.command.command_binding import CommandBinding, CommandBindingEvent


class ButtonBinding:
    def __init__(self, button: QPushButton, command: CommandBinding):
        self.button = button
        self.command = command

        button.clicked.connect(command.execute)
        command.listeners.append(self._on_command_event)

        self.refresh()

    def refresh(self) -> None:
        self.button.setEnabled(self.command.is_enabled)

    def _on_command_event(self, event: CommandBindingEvent) -> None:
        if event == CommandBindingEvent.ENABLED_CHANGED:
            self.refresh()
