import cv2
import numpy as np


class MaskSelectorModel:
    def __init__(self, images):
        self.images = images
        self.width, self.height = images[0].shape[:2]
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        mask = np.zeros((self.width, self.height), np.uint8)
        self.mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.points = []
        self.redo_stack = []
        self.undo_stack = []

    def reset_mask(self):
        self.mask = cv2.cvtColor(np.zeros((self.width, self.height), np.uint8), cv2.COLOR_GRAY2BGR)

    def get_gray_mask(self):
        return cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)