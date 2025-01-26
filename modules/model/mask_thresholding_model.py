import cv2


class MaskThresholdingModel:
    def __init__(self, input_mask):
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195
        self.title = "Mask processing"

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