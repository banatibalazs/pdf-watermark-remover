from modules.interfaces.gui_interfaces import MouseHandlerInterface, KeyHandlerInterface, DisplayInterface
from modules.model.mask_drawing_model import MaskDrawingModel
from modules.view.mask_drawing_view import MaskDrawingView
import cv2



class MaskDrawing(MouseHandlerInterface, KeyHandlerInterface):
    def __init__(self, input_mask):
        self.model = MaskDrawingModel(input_mask)
        self.view: DisplayInterface = MaskDrawingView()

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            self.model.save_state()

        if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
            self.model.draw_circle(x, y, erase=True, fill=True)
        elif event == cv2.EVENT_RBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON):
            self.model.draw_circle(x, y, erase=False, fill=True)
        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.model.adjust_cursor_size(increase=True)
            else:
                self.model.adjust_cursor_size(increase=False)
        self.model.cursor_pos = (x, y)
        self.view.display_image(self.model)

    def handle_key(self, key):
        if key == ord('r'):
            self.model.final_mask = self.model.input_mask.copy()
            self.model.undo_stack.clear()
            self.model.redo_stack.clear()
        elif key == ord('c'):
            self.model.is_text_shown = not self.model.is_text_shown
        elif key == ord('u'):
            self.model.undo()
        elif key == ord('y'):
            self.model.redo()
        elif key == 32:
            return False
        if key in [ord('r'), ord('c'), ord('u'), ord('y')]:
            self.view.display_image(self.model)
        return True

    def run(self):
        params = {
            'mouse': self.handle_mouse
        }
        self.view.setup_window(params)
        self.view.display_image(self.model)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_gray_mask(self):
        return self.model.get_gray_mask()

