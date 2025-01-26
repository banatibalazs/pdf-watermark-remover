import cv2

from modules.interfaces.gui_interfaces import MouseHandlerInterface, KeyHandlerInterface, DisplayInterface
from modules.interfaces.redo_undo_interface import RedoUndoInterface
from modules.utils import add_texts_to_image



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

    def __init__(self, model=None):
        self.texts = MaskDrawingView.TEXTS
        self.text_color = MaskDrawingView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.model = model

    def display_image(self):
        displayed_image = self.model.final_mask.copy()
        cv2.circle(displayed_image,self.model.cursor_pos,
                   self.model.cursor_size, (255),
                   self.model.cursor_thickness)
        if self.model.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow('Mask processing', displayed_image)

    def close_window(self):
        cv2.destroyAllWindows()



class MaskDrawing(MouseHandlerInterface, KeyHandlerInterface):
    def __init__(self, input_mask):
        self.model = MaskDrawingModel(input_mask)
        self.view: DisplayInterface = MaskDrawingView(self.model)

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            self.model.save_state()

        if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
            self.model.draw_circle(x, y, erase=True)
        elif event == cv2.EVENT_RBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON):
            self.model.draw_circle(x, y, erase=False)
        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.model.adjust_cursor_size(increase=True)
            else:
                self.model.adjust_cursor_size(increase=False)
        self.model.cursor_pos = (x, y)
        self.view.display_image()

    def handle_key(self, key):
        if key == ord('r'):
            self.model.final_mask = self.model.input_mask.copy()
            self.model.undo_stack.clear()
            self.model.redo_stack.clear()
            self.view.display_image()
        elif key == ord('c'):
            self.model.is_text_shown = not self.model.is_text_shown
            self.view.display_image()
        elif key == ord('u'):
            self.model.undo()
            self.view.display_image()
        elif key == ord('y'):
            self.model.redo()
            self.view.display_image()
        elif key == 32:
            return False
        return True

    def process_mask(self):

        cv2.namedWindow('Mask processing')
        cv2.setMouseCallback('Mask processing', self.handle_mouse)
        self.view.display_image()
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        cv2.destroyAllWindows()

    def get_gray_mask(self):
        return self.model.get_gray_mask()

