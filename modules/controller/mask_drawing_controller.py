from modules.interfaces.gui_interfaces import MouseHandlerInterface, KeyHandlerInterface, DisplayInterface
from modules.interfaces.redo_undo_interface import RedoUndoInterface
from modules.model.mask_drawing_model import MaskDrawingModel
from modules.view.opencv_view import OpencvView
import cv2



class MaskDrawing(MouseHandlerInterface, KeyHandlerInterface, RedoUndoInterface):
    TEXTS = ["Draw on the mask.",
             "LMouse/RMouse: erase/draw",
             "Mouse wheel: cursor size",
             "Press 'U'/'Y' to undo/redo.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    def __init__(self, input_mask):
        self.model = MaskDrawingModel(input_mask)
        self.view: OpencvView = OpencvView(MaskDrawing.TEXTS,
                                           MaskDrawing.TEXT_COLOR,
                                           MaskDrawing.TITLE)

    def undo(self) -> None:
        if not self.model.undo_stack:
            return
        self.model.redo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.undo_stack.pop()
        self.view.display_image(self.model.final_mask)

    def redo(self) -> None:
        if not self.model.redo_stack:
            return
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.redo_stack.pop()
        self.view.display_image(self.model.final_mask)

    def save_state(self) -> None:
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.redo_stack.clear()

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            self.save_state()

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
        mask = self.model.final_mask.copy()
        cv2.circle(mask, self.model.cursor_pos,
                   self.model.cursor_size, [128],
                   self.model.cursor_thickness)
        self.view.display_image(mask)

    def handle_key(self, key):
        if key == ord('r'):
            self.model.final_mask = self.model.input_mask.copy()
            self.model.undo_stack.clear()
            self.model.redo_stack.clear()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == ord('u'):
            self.undo()
        elif key == ord('y'):
            self.redo()
        elif key == 32:
            return False
        if key in [ord('r'), ord('c'), ord('u'), ord('y')]:
            self.view.display_image(self.model.final_mask)
        return True

    def run(self):
        params = {
            'mouse': self.handle_mouse
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.final_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_gray_mask(self):
        return self.model.get_gray_mask()

