class CommandBinding:
    def __init__(self, tracker, validation):
        self.tracker = tracker
        self.validation = validation

    @property
    def is_enabled(self) -> bool:
        return False