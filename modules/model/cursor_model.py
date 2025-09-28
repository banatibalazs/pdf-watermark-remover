from typing import Tuple
from dataclasses import dataclass
from typing import Tuple

from modules.controller.constants import CursorType


@dataclass
class CursorData:
    type: CursorType = CursorType.CIRCLE
    size: int = 10
    pos: Tuple[int, int] = (0, 0)
    thickness: int = 2
    ix: int = -1
    iy: int = -1


class CursorModel:
    def __init__(self):
        self.cursor_data = CursorData()

    def toggle_cursor_type(self) -> None:
        if self.cursor_data.type == CursorType.CIRCLE:
            self.cursor_data.type = CursorType.SQUARE
        else:
            self.cursor_data.type = CursorType.CIRCLE
        print("Cursor type changed to:", self.cursor_data.type)

    def set_cursor_size(self, size: int) -> None:
        self.cursor_data.size = size

    def set_cursor_pos(self, pos: tuple) -> None:
        self.cursor_data.pos = pos

    def get_cursor_type(self) -> CursorType:
        return self.cursor_data.type

    def get_cursor_size(self) -> int:
        return self.cursor_data.size

    def get_cursor_pos(self) -> Tuple[int, int]:
        return self.cursor_data.pos
