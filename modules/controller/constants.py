from enum import Enum, auto

class MaskMode(Enum):
    SELECT = auto()
    THRESHOLD = auto()
    DRAW = auto()
    ADJUST = auto()


class CursorType(Enum):
    CIRCLE = 0
    SQUARE = 1



