import cv2
import numpy as np
from modules.utils import add_texts_to_image

TEXTS = ["Press 'D' to dilate the mask.",
        "Press 'E' to erode the mask.",
        "Press 'R' to reset the mask.",
        "Press 'C' to hide/show this text.",
        "Press 'space' to finish."]

TEXT_COLOR = (255, 255, 255)


class MaskRefiner:
    def __init__(self, bgr_images, gray_mask):
        self.images = bgr_images
        self.mask = gray_mask
        self.final_mask = None
        self.median_image = self.calc_median_image()
        self.threshold_min = 0
        self.threshold_max = 195
        self.thresholded_mask = None
        self.texts = TEXTS
        self.text_color = TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def calc_median_image(self, length=40):
        length = min(length, len(self.images))
        # Convert the images to numpy arrays and stack them along a new dimension
        stacked_images = np.stack([np.array(image) for image in self.images[:length]], axis=-1)
        # Get the median along the new dimension
        median_image = np.median(stacked_images, axis=-1)
        # The median image is float, convert it back to uint8
        median_image = np.uint8(median_image)
        median_image_gray = cv2.cvtColor(median_image, cv2.COLOR_BGR2GRAY)
        median_image_gray = cv2.bitwise_and(median_image_gray, self.mask)
        return median_image_gray

    def threshold_mask(self):
        cv2.imshow('watermark remover', self.median_image)
        cv2.createTrackbar('th_min', 'watermark remover', self.threshold_min, 255, self.on_threshold_trackbar_min)
        cv2.createTrackbar('th_max', 'watermark remover', self.threshold_max, 255, self.on_threshold_trackbar_max)
        cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def on_threshold_trackbar_min(self, pos):
        self.threshold_min = pos
        self.update_median()

    def on_threshold_trackbar_max(self, pos):
        self.threshold_max = pos
        self.update_median()

    def update_median(self):
        self.thresholded_mask = cv2.inRange(self.median_image, self.threshold_min, self.threshold_max)
        self.thresholded_mask = cv2.bitwise_and(self.thresholded_mask, self.mask)
        cv2.imshow('watermark remover', self.thresholded_mask)

    def erode_dilate_mask(self):

        self.final_mask = self.thresholded_mask.copy()
        # In the main part of your code

        kernel = np.ones((3, 3), np.uint8)
        texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
        cv2.imshow('watermark remover', texted_mask)
        while True:
            # Listen for keypress events
            key = cv2.waitKey(1) & 0xFF

            # If 'd' is pressed, dilate the mask
            if key == ord('d'):
                self.final_mask = cv2.dilate(self.final_mask, kernel, iterations=1)

            # If 'e' is pressed, erode the mask
            elif key == ord('e'):
                self.final_mask = cv2.erode(self.final_mask, kernel, iterations=1)

            elif key == ord('r'):
                self.final_mask = self.thresholded_mask.copy()

            if self.is_text_shown:
                texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
                cv2.imshow('watermark remover', texted_mask)
            else:
                cv2.imshow('watermark remover', self.final_mask)

            if key == ord('c'):
                self.is_text_shown = not self.is_text_shown

            # If 'space' is pressed, break the loop
            if key == 32:
                break

        cv2.destroyAllWindows()

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)

