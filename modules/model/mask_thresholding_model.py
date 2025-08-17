import cv2
import numpy as np

from modules.model.base_model import BaseModel
from modules.utils import calc_median_image


class MaskThresholdingModel(BaseModel):
    def __init__(self, images, mask):
        super().__init__()
        gray_image = cv2.cvtColor(calc_median_image(images), cv2.COLOR_BGR2GRAY)
        self.mask = mask
        self.images = images
        self.input_mask = cv2.bitwise_and(gray_image, mask)
        self.final_mask = self.input_mask.copy()
        self.threshold_min = 0
        self.threshold_max = 195
        self.median_img_number = 5

    def set_median_img_number(self, number):
        """Set the number of images used to calculate the median image."""
        number = int(number)
        self.median_img_number = number
        print(f"Median image number set to: {self.median_img_number}")
        if self.median_img_number < 1:
            self.median_img_number = 1
        elif self.median_img_number > len(self.images):
            self.median_img_number = len(self.images)

    def calc_median_image(self):
        gray_image = cv2.cvtColor(calc_median_image(self.images, int(self.median_img_number)), cv2.COLOR_BGR2GRAY)
        self.input_mask = cv2.bitwise_and(gray_image, self.mask)

