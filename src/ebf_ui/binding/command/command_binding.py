class CommandBinding:
    def __init__(self, tracker, validation):
        self.tracker = tracker
        self.validation = validation

    @property
    def is_enabled(self) -> bool:
        return (
                self.tracker.is_editing
                and self.tracker.is_dirty
                and self.validation.is_valid
        )