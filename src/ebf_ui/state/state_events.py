from enum import StrEnum, auto
from typing import Callable


class StateTrackerEvent(StrEnum):
    BEGIN_EDIT = auto()
    UPDATE_EDIT = auto()
    CANCEL_EDIT = auto()
    END_EDIT = auto()
    DIRTY_CHANGED = auto()

type StateTrackerListener = Callable[[StateTrackerEvent], None]
