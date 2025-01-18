import cv2
import numpy as np
from modules.utils import add_texts_to_image

TEXTS = ["Use the trackbars to",
         "adjust the thresholding.",
        "Press 'space' to finish.",
        "Press 'C' to hide/show this text."]

TEXT_COLOR = (255, 255, 255)

class MaskThresholding:
    def __init__(self, masked_image):
        self.masked_image = masked_image
        self.mask = cv2.inRange(masked_image, 1, 255)
        self.threshold_min = 0
        self.threshold_max = 195
        self.thresholded_mask = None
        self.texts = TEXTS
        self.text_color = TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def threshold_mask(self):
        cv2.imshow('watermark remover', self.masked_image)
        cv2.createTrackbar('th_min', 'watermark remover', self.threshold_min, 255, self.on_threshold_trackbar_min)
        cv2.createTrackbar('th_max', 'watermark remover', self.threshold_max, 255, self.on_threshold_trackbar_max)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Space key
                break
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.update_mask()

        cv2.destroyAllWindows()

    def on_threshold_trackbar_min(self, pos):
        self.threshold_min = pos
        self.update_mask()

    def on_threshold_trackbar_max(self, pos):
        self.threshold_max = pos
        self.update_mask()

    def update_mask(self):
        self.thresholded_mask = cv2.inRange(self.masked_image, self.threshold_min, self.threshold_max)
        self.thresholded_mask = cv2.bitwise_and(self.thresholded_mask, self.mask)
        display_image = self.thresholded_mask.copy()
        if self.is_text_shown:
            display_image = add_texts_to_image(display_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow('watermark remover', display_image)

    def get_gray_mask(self):
        return self.thresholded_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.thresholded_mask, cv2.COLOR_GRAY2BGR)