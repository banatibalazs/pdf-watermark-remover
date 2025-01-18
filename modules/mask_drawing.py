import cv2
import numpy as np
from modules.utils import add_texts_to_image

TEXTS = ["Draw on the mask.",
        "Mouse wheel: change cursor size",
        "Left mouse button: erase",
        "Right mouse button: draw",
        "Press 'R' to reset the mask.",
        "Press 'C' to hide/show this text.",
        "Press 'space' to finish."]

TEXT_COLOR = (255, 255, 255)

class MaskDrawing:
    def __init__(self, thresholded_mask):
        self.thresholded_mask = thresholded_mask
        self.drawn_mask = self.thresholded_mask.copy()
        self.cursor_size = 5
        self.texts = TEXTS
        self.text_color = TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True


    def draw_on_mask(self):
        def draw_circle(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON):
                cv2.circle(self.drawn_mask, (x, y), self.cursor_size, (0), -1)
            elif event == cv2.EVENT_RBUTTONDOWN or (event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON):
                cv2.circle(self.drawn_mask, (x, y), self.cursor_size, (255), -1)
            elif event == cv2.EVENT_MOUSEWHEEL:
                if flags > 0:
                    self.cursor_size = min(self.cursor_size + 1, 50)
                else:
                    self.cursor_size = max(self.cursor_size - 1, 1)
                print(f"Cursor size: {self.cursor_size}")

            # Draw the cursor perimeter as a white line
            temp_image = self.drawn_mask.copy()
            cv2.circle(temp_image, (x, y), self.cursor_size, (255), 1)
            if self.is_text_shown:
                temp_image = add_texts_to_image(temp_image, self.texts, self.text_pos, self.text_color)
            cv2.imshow('Drawing on the mask', temp_image)

        cv2.namedWindow('Drawing on the mask')
        cv2.setMouseCallback('Drawing on the mask', draw_circle)
        cv2.imshow('Drawing on the mask', self.drawn_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 32:
                break
            elif key == ord('r'):
                self.drawn_mask = self.thresholded_mask.copy()
                cv2.imshow('Drawing on the mask', self.drawn_mask)
            if key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                if self.is_text_shown:
                    texted_mask = add_texts_to_image(self.drawn_mask, self.texts, self.text_pos, self.text_color)
                    cv2.imshow('Drawing on the mask', texted_mask)
                else:
                    cv2.imshow('Drawing on the mask', self.drawn_mask)

        cv2.destroyAllWindows()

    def get_gray_mask(self):
        return self.drawn_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.drawn_mask, cv2.COLOR_GRAY2BGR)
