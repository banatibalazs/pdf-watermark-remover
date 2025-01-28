import cv2
import numpy as np
from modules.interfaces.gui_interfaces import DisplayInterface, MouseHandlerInterface, KeyHandlerInterface
from modules.interfaces.redo_undo_interface import RedoUndoInterface
from modules.model.mask_selector_model import MaskSelectorModel
from modules.view.mask_selector_view import MaskSelectorView



class MaskSelector(KeyHandlerInterface, MouseHandlerInterface, RedoUndoInterface):
    def __init__(self, images):
        self.model = MaskSelectorModel(images)
        self.view: DisplayInterface = MaskSelectorView()

    def undo(self) -> None:
        if not self.model.undo_stack:
            return
        self.model.redo_stack.append(self.model.mask.copy())
        self.model.mask = self.model.undo_stack.pop()
        self.view.display_image(self.model.get_weighted_image())

    def redo(self) -> None:
        if not self.model.redo_stack:
            return
        self.model.undo_stack.append(self.model.mask.copy())
        self.model.mask = self.model.redo_stack.pop()
        self.view.display_image(self.model.get_weighted_image())

    def save_state(self) -> None:
        self.model.undo_stack.append(self.model.mask.copy())
        self.model.redo_stack.clear()

    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_page_index = max(0, self.model.current_page_index - 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('d'):
            self.model.current_page_index = min(len(self.model.images) - 1, self.model.current_page_index + 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('r'):
            self.model.reset_mask()
            self.model.undo_stack.clear()
            self.model.redo_stack.clear()
        elif key == ord('c'):
            self.view.is_text_shown = not self.view.is_text_shown
        elif key == ord('u'):
            self.undo()
        elif key == ord('y'):
            self.redo()
        elif key == 32:
            return False
        if key in [ord('a'), ord('d'), ord('r'), ord('c')]:
            self.view.display_image(self.model.get_weighted_image())
        return True

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.save_state()

        if event == cv2.EVENT_LBUTTONDOWN:
            self.model.drawing = True
            self.model.ix, self.model.iy = x, y
            self.model.points.append((x, y))
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.model.drawing:
                cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
                self.model.ix, self.model.iy = x, y
                self.model.points.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            self.model.drawing = False
            cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
            self.model.points.append((x, y))
            cv2.fillPoly(self.model.mask, [np.array(self.model.points)], (255, 255, 255))
            self.model.points.clear()
        self.view.display_image(self.model.get_weighted_image())

    def run(self):
        params = {
            'mouse': self.handle_mouse
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.get_weighted_image())

        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_gray_mask(self):
        return self.model.get_gray_mask()