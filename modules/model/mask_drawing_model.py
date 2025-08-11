import cv2
from modules.interfaces.redo_undo_interface import RedoUndoInterface


class MaskDrawingModel:
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

    def draw_circle(self, x, y, erase=False, fill=True):
        color = 0 if erase else 255
        if fill:
            cv2.circle(self.final_mask, (x, y), self.cursor_size, [color], -1)
        else:
            cv2.circle(self.final_mask, (x, y), self.cursor_size, [color], 1)

    def adjust_cursor_size(self, increase=True):
        if increase:
            self.cursor_size = min(self.cursor_size + 1, 50)
        else:
            self.cursor_size = max(self.cursor_size - 1, 1)

    def get_gray_mask(self):
        if len(self.final_mask.shape) == 2:
            return self.final_mask
        return cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)

    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask.png'
        cv2.imwrite(path, self.final_mask)
        print("Mask saved as " + path)
        print("Mask size:", self.final_mask.shape)

    def reset_mask(self):
        self.final_mask = self.input_mask.copy()
        self.undo_stack.clear()
        self.redo_stack.clear()
        print("Mask reset to initial state.")

    def load_mask(self, path=None):
        if path is None:
            return
        try:
            self.final_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if self.final_mask is None:
                print("No saved mask found. Using default mask.")
                self.reset_mask()
            else:
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)
        except Exception as e:
            print(f"Error loading mask from {path}: {e}")
            self.reset_mask()
