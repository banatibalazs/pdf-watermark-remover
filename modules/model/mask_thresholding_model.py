import cv2
import numpy as np
from modules.utils import calc_median_image


class MaskThresholdingModel:
    def __init__(self, images, mask):
        gray_image = cv2.cvtColor(calc_median_image(images), cv2.COLOR_BGR2GRAY)
        self.input_mask = cv2.bitwise_and(gray_image, mask)
        self.final_mask = self.input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195

    def update_mask(self):
        self.final_mask = cv2.inRange(self.input_mask, np.array(self.threshold_min, dtype=np.uint8),
                                      np.array(self.threshold_max, dtype=np.uint8))
        self.final_mask = cv2.bitwise_and(self.final_mask, cv2.inRange(self.input_mask, 1, 255))

    def set_threshold_min(self, value):
        self.threshold_min = value
        self.update_mask()

    def set_threshold_max(self, value):
        value = np.array(value, dtype=np.uint8)
        self.threshold_max = value
        self.update_mask()

    def get_final_mask(self):
        return self.final_mask

    def get_gray_mask(self):
        return self.final_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)

    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask.png'
        cv2.imwrite(path, self.final_mask)
        print("Mask saved as 'png'")
        print("Mask size:", self.final_mask.shape)

    def reset_mask(self):
        self.final_mask = self.input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195
        self.update_mask()
        print("Mask reset to initial state.")

    def load_mask(self, path=None):
        if path is None:
            return
        try:
            self.final_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if self.final_mask is None:
                print("No saved mask found. Using default mask.")
                self.reset_mask()
            else:
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)
        except Exception as e:
            print(f"Error loading mask from {path}: {e}")
            self.reset_mask()