from enum import Enum, auto

MAX_MEDIAN_IMAGE_NUMBER = 50

class MaskMode(Enum):
    SELECT = auto()
    THRESHOLD = auto()
    DRAW = auto()
    ADJUST = auto()


class CursorType(Enum):
    CIRCLE = 0
    SQUARE = 1





