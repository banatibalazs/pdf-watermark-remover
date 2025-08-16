import cv2
import numpy as np

from modules.model.base_model import BaseModel
from modules.utils import calc_median_image


class MaskThresholdingModel(BaseModel):
    def __init__(self, images, mask):
        gray_image = cv2.cvtColor(calc_median_image(images), cv2.COLOR_BGR2GRAY)
        self.input_mask = cv2.bitwise_and(gray_image, mask)
        self.final_mask = self.input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195
        self.redo_stack = []
        self.undo_stack = []

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

    def reset_mask(self):
        self.final_mask = self.input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195
        self.update_mask()
        print("Mask reset to initial state.")

    def get_image_shown(self):
        return self.final_mask