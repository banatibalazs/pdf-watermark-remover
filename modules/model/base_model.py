import cv2
import numpy as np
from typing import List, Optional

from modules.utils import calc_median_image


class BaseModel:
    def __init__(self, mask=None, images=None):

        self.median_image = cv2.cvtColor(calc_median_image(images, 1), cv2.COLOR_BGR2GRAY)
        self.temp_mask = mask
        self.mask = mask
        self.images = images
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        self.input_mask = cv2.bitwise_and(self.median_image, mask)
        self.final_mask = self.input_mask.copy()

        self.threshold_min = 0
        self.threshold_max = 195
        self.undo_stack: List[np.ndarray] = []
        self.redo_stack: List[np.ndarray] = []
        self.cursor_size = 10
        self.cursor_pos = (0, 0)
        self.cursor_thickness = 1
        self.ix, self.iy = -1, -1
        self.points = []
        self.weight = 0.7


    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask' + '.png'
        cv2.imwrite(path, self.final_mask)
        print("Mask saved as " + path)
        print("Mask size:", self.final_mask.shape)

    def get_gray_mask(self):
        """Check the channels of the mask and convert to grayscale if necessary."""
        if len(self.final_mask.shape) == 2:
            # Mask is already grayscale
            return self.final_mask
        elif len(self.final_mask.shape) == 3 and self.final_mask.shape[2] == 3:
            # Mask is in color, convert to grayscale
            return cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Mask has an unexpected shape: " + str(self.final_mask.shape))

    def get_bgr_mask(self):
        """Check the channels of the mask and convert to BGR if necessary."""
        if len(self.final_mask.shape) == 2:
            # Mask is grayscale, convert to BGR
            return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)
        elif len(self.final_mask.shape) == 3 and self.final_mask.shape[2] == 3:
            # Mask is already in BGR
            return self.final_mask
        else:
            raise ValueError("Mask has an unexpected shape: " + str(self.final_mask.shape))


    def load_mask(self, path=None):
        if path is None:
            return
        try:
            self.final_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if self.final_mask is None:
                print("No saved mask found. Using default mask.")
                self.reset_mask()
            elif len(self.final_mask.shape) == 2:
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)
        except:
            print(f"Error loading mask from {path}. Using default mask.")
            self.reset_mask()

    def get_image_shown(self):
        """Return the image to be displayed, which is the final mask."""
        if self.final_mask is None:
            raise ValueError("Final mask is not set.")
        return self.final_mask.copy()

    def reset_mask(self):
        self.final_mask = self.input_mask.copy()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.points = []
        print("Mask reset to initial state.")

    def set_cursor_size(self, size: int):
        """Set the size of the cursor."""
        self.cursor_size = size

    def set_cursor_pos(self, pos: tuple):
        """Set the position of the cursor."""
        self.cursor_pos = pos

    def get_weighted_image(self):
        """Return the current image with the mask applied."""
        if self.current_image is None or self.final_mask is None:
            raise ValueError("Current image or final mask is not set.")
        return cv2.addWeighted(self.current_image, self.weight, self.get_bgr_mask(), 0.8, 0)
