import numpy as np
import cv2


def calc_median_image(images, length=40):
    length = min(length, len(images))
    stacked_images = np.stack([np.array(image) for image in images[:length]], axis=-1)
    median_image = np.median(stacked_images, axis=-1)
    median_image = np.uint8(median_image)
    return median_image


class MedianMaskMaking:
    def __init__(self, bgr_images, gray_mask):
        self.mask = gray_mask
        self.median_image = calc_median_image(bgr_images)

    def get_gray_mask(self):
        median_image_gray = cv2.cvtColor(self.median_image, cv2.COLOR_BGR2GRAY)
        return cv2.bitwise_and(median_image_gray, self.mask)

