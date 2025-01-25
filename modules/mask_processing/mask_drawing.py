import cv2
from modules.mask_processing.abstract_mask_processing import MaskProcessing
from modules.utils import add_texts_to_image

class MaskDrawing(MaskProcessing):
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

    def __init__(self, input_mask):
        super().__init__(input_mask, MaskDrawing.TEXTS, MaskDrawing.TEXT_COLOR)
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
            self.show_mask()
        else:
            self.final_mask = self.input_mask.copy()
            self.show_mask()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.final_mask.copy())
            self.final_mask = self.redo_stack.pop()
            self.show_mask()

    def process_mask(self):
        def draw_circle(event, x, y, flags, param):
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

            display_image = self.final_mask.copy()
            cv2.circle(display_image, (x, y), self.cursor_size, (255), 1)
            if self.is_text_shown:
                display_image = add_texts_to_image(display_image, self.texts, self.text_pos, self.text_color)
            cv2.imshow('Mask processing', display_image)

        cv2.namedWindow('Mask processing')
        cv2.setMouseCallback('Mask processing', draw_circle)
        cv2.imshow('Mask processing', self.final_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 32:
                break
            elif key == ord('r'):
                self.final_mask = self.input_mask.copy()
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.show_mask()
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.show_mask()
            elif key == ord('u'):
                self.undo()
            elif key == ord('y'):
                self.redo()

        cv2.destroyAllWindows()