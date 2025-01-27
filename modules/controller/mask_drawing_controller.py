from modules.interfaces.gui_interfaces import MouseHandlerInterface, KeyHandlerInterface, DisplayInterface
from modules.model.mask_drawing_model import MaskDrawingModel
from modules.view.mask_drawing_view import MaskDrawingView
import cv2



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

    def run(self):
        self.view.setup_window(self.handle_mouse)
        self.view.display_image()
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_gray_mask(self):
        return self.model.get_gray_mask()

