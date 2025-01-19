import cv2
from modules.mask_processing import MaskProcessing
from modules.utils import add_texts_to_image


class MaskDrawing(MaskProcessing):
    TEXTS = ["Draw on the mask.",
             "Mouse wheel: change cursor size",
             "Left mouse button: erase",
             "Right mouse button: draw",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, input_mask):
        super().__init__(input_mask, MaskDrawing.TEXTS, MaskDrawing.TEXT_COLOR)
        self.cursor_size = 5

    def process_mask(self):
        def draw_circle(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
                cv2.circle(self.final_mask, (x, y), self.cursor_size, (0), -1)
            elif event == cv2.EVENT_RBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON):
                cv2.circle(self.final_mask, (x, y), self.cursor_size, (255), -1)
            elif event == cv2.EVENT_MOUSEWHEEL:
                if flags > 0:
                    self.cursor_size = min(self.cursor_size + 1, 50)
                else:
                    self.cursor_size = max(self.cursor_size - 1, 1)

            # Draw the cursor perimeter as a white line
            temp_image = self.final_mask.copy()
            cv2.circle(temp_image, (x, y), self.cursor_size, (255), 1)
            if self.is_text_shown:
                temp_image = add_texts_to_image(temp_image, self.texts, self.text_pos, self.text_color)
            cv2.imshow('Drawing on the mask', temp_image)

        cv2.namedWindow('Drawing on the mask')
        cv2.setMouseCallback('Drawing on the mask', draw_circle)
        cv2.imshow('Drawing on the mask', self.final_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 32:
                break
            elif key == ord('r'):
                self.final_mask = self.input_mask.copy()
                cv2.imshow('Drawing on the mask', self.final_mask)
            if key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                if self.is_text_shown:
                    texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
                    cv2.imshow('Drawing on the mask', texted_mask)
                else:
                    cv2.imshow('Drawing on the mask', self.final_mask)

        cv2.destroyAllWindows()
