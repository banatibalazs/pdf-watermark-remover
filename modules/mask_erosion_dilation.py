import cv2
import numpy as np
from modules.utils import add_texts_to_image

TEXTS = ["Press 'D' to dilate the mask.",
        "Press 'E' to erode the mask.",
        "Press 'R' to reset the mask.",
        "Press 'C' to hide/show this text.",
        "Press 'space' to finish."]
TEXT_COLOR = (0, 0, 0)

class MaskErosionDilation:
    def __init__(self, drawn_mask):
        self.drawn_mask = drawn_mask
        self.final_mask = drawn_mask.copy()
        self.texts = TEXTS
        self.text_color = TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def erode_dilate_mask(self):
        kernel = np.ones((3, 3), np.uint8)
        texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
        cv2.imshow('watermark remover', texted_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('d'):
                self.final_mask = cv2.dilate(self.final_mask, kernel, iterations=1)
            elif key == ord('e'):
                self.final_mask = cv2.erode(self.final_mask, kernel, iterations=1)
            elif key == ord('r'):
                self.final_mask = self.drawn_mask.copy()
            if self.is_text_shown:
                texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
                cv2.imshow('watermark remover', texted_mask)
            else:
                cv2.imshow('watermark remover', self.final_mask)
            if key == ord('c'):
                self.is_text_shown = not self.is_text_shown
            if key == 32:
                break
        cv2.destroyAllWindows()

    def get_gray_mask(self):
        return self.final_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)