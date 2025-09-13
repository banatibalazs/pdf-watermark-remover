from enum import Enum
from dataclasses import dataclass

class MaskMode(Enum):
    SELECT = 0
    DRAW = 1
    ADJUST = 2

class CursorType(Enum):
    CIRCLE = 0
    SQUARE = 1



