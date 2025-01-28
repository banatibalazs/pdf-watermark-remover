import cv2

from modules.utils import calc_median_image


class MaskThresholdingModel:
    def __init__(self, images, mask):
        gray_image = cv2.cvtColor(calc_median_image(images), cv2.COLOR_BGR2GRAY)
        self.input_mask = cv2.bitwise_and(gray_image, mask)
        self.final_mask = self.input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195

    def update_mask(self):
        self.final_mask = cv2.inRange(self.input_mask, self.threshold_min, self.threshold_max)
        self.final_mask = cv2.bitwise_and(self.final_mask, cv2.inRange(self.input_mask, 1, 255))

    def set_threshold_min(self, value):
        self.threshold_min = value
        self.update_mask()

    def set_threshold_max(self, value):
        self.threshold_max = value
        self.update_mask()

    def get_final_mask(self):
        return self.final_mask

    def get_gray_mask(self):
        return self.final_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)