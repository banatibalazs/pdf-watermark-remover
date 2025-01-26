import cv2
import numpy as np


class MaskErosionDilationModel:
    def __init__(self, input_mask):
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.kernel = np.ones((3, 3), np.uint8)

    def dilate(self):
        self.final_mask = cv2.dilate(self.final_mask, self.kernel, iterations=1)

    def erode(self):
        self.final_mask = cv2.erode(self.final_mask, self.kernel, iterations=1)

    def reset(self):
        self.final_mask = self.input_mask.copy()

    def get_gray_mask(self):
        return self.final_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)

    def save_mask(self, path):
        cv2.imwrite(path, self.final_mask)