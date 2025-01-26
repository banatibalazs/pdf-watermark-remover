import cv2
from modules.interfaces.redo_undo_interface import RedoUndoInterface


class MaskDrawingModel(RedoUndoInterface):
    def __init__(self, input_mask):
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.cursor_size = 15
        self.cursor_color = (0, 0, 0)
        self.cursor_thickness = 1
        self.cursor_pos = (0, 0)
        self.is_text_shown = True
        self.undo_stack = []
        self.redo_stack = []


    def save_state(self):
        self.undo_stack.append(self.final_mask.copy())
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.final_mask.copy())
            self.final_mask = self.undo_stack.pop()
        else:
            self.final_mask = self.input_mask.copy()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.final_mask.copy())
            self.final_mask = self.redo_stack.pop()

    def draw_circle(self, x, y, erase=False):
        color = 0 if erase else 255
        cv2.circle(self.final_mask, (x, y), self.cursor_size, (color), -1)

    def adjust_cursor_size(self, increase=True):
        if increase:
            self.cursor_size = min(self.cursor_size + 1, 50)
        else:
            self.cursor_size = max(self.cursor_size - 1, 1)

    def get_gray_mask(self):
        if len(self.final_mask.shape) == 2:
            return self.final_mask
        return cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)