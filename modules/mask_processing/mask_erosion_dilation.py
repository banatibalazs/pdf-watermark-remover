import cv2
import numpy as np
from modules.mask_processing.mask_processing import MaskProcessing


class MaskErosionDilation(MaskProcessing):
    TEXTS = ["Press 'D' to dilate the mask.",
             "Press 'E' to erode the mask.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, input_mask):
        super().__init__(input_mask, MaskErosionDilation.TEXTS, MaskErosionDilation.TEXT_COLOR)

    def process_mask(self):
        kernel = np.ones((3, 3), np.uint8)
        self.show_mask()
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('d'):
                self.final_mask = cv2.dilate(self.final_mask, kernel, iterations=1)
                self.show_mask()
            elif key == ord('e'):
                self.final_mask = cv2.erode(self.final_mask, kernel, iterations=1)
                self.show_mask()
            elif key == ord('r'):
                self.final_mask = self.input_mask.copy()
                self.show_mask()
            if key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.show_mask()
            if key == 32:
                break
        cv2.destroyAllWindows()
