import cv2

from modules.interfaces.gui_interfaces import MouseHandlerInterface, KeyHandlerInterface, DisplayInterface
from modules.interfaces.redo_undo_interface import RedoUndoInterface
from modules.utils import add_texts_to_image


class MaskDrawingView(DisplayInterface):
    TEXTS = ["Draw on the mask.",
             "L mouse: erase",
             "R mouse: draw",
             "Mouse wheel: cursor size",
             "Press 'R' to reset the mask.",
             "Press 'U' to undo.",
             "Press 'Y' to redo.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self):
        self.texts = MaskDrawingView.TEXTS
        self.text_color = MaskDrawingView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def display_image(self, mask=None, cursor_pos=None, cursor_size=15, cursor_color=(255), cursor_thickness=1):
        if mask is None:
            return
        displayed_image = mask.copy()
        cv2.circle(displayed_image, cursor_pos, cursor_size, cursor_color, cursor_thickness)
        if self.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow('Mask processing', displayed_image)


class MaskDrawing(RedoUndoInterface, MouseHandlerInterface, KeyHandlerInterface):

    def __init__(self, input_mask):
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.view: DisplayInterface = MaskDrawingView()
        self.cursor_size = 15
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self):
        self.undo_stack.append(self.final_mask.copy())
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.final_mask.copy())
            self.final_mask = self.undo_stack.pop()
            self.view.display_image()
        else:
            self.final_mask = self.input_mask.copy()
            self.view.display_image()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.final_mask.copy())
            self.final_mask = self.redo_stack.pop()
            self.view.display_image()

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            self.save_state()

        if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
            cv2.circle(self.final_mask, (x, y), self.cursor_size, (0), -1)
        elif event == cv2.EVENT_RBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON):
            cv2.circle(self.final_mask, (x, y), self.cursor_size, (255), -1)
        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.cursor_size = min(self.cursor_size + 1, 50)
            else:
                self.cursor_size = max(self.cursor_size - 1, 1)

        self.view.display_image(self.final_mask, (x, y), self.cursor_size, (255), 1)


    def handle_key(self, key):
        if key == ord('r'):
            self.final_mask = self.input_mask.copy()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.view.display_image()
        elif key == ord('c'):
            self.view.is_text_shown = not self.view.is_text_shown
            self.view.display_image()
        elif key == ord('u'):
            self.undo()
        elif key == ord('y'):
            self.redo()
        elif key == 32:
            return False
        return True

    def process_mask(self):
        cv2.namedWindow('Mask processing')
        cv2.setMouseCallback('Mask processing', self.handle_mouse)
        cv2.imshow('Mask processing', self.final_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break
        cv2.destroyAllWindows()

    def get_gray_mask(self):
        if len(self.final_mask.shape) == 2:
            return self.final_mask
        return cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)

