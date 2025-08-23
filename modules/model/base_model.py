import cv2
import numpy as np
from typing import List, Optional

from modules.controller.constants import MaskMode
from modules.utils import calc_median_image, AdjusterParameters, fill_masked_area, inpaint_image, sharpen_image
from web.utils import resize_image


class BaseModel:
    def __init__(self, mask=None, images=None):

        self.median_image = cv2.cvtColor(calc_median_image(images, 1), cv2.COLOR_BGR2GRAY)
        self.mask = mask
        self.images = images
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        self.input_mask = cv2.bitwise_and(self.median_image, mask)
        self.final_mask = self.input_mask.copy()
        self.temp_mask = self.final_mask.copy()
        self.mode = MaskMode.SELECT

        self.threshold_min = 1
        self.threshold_max = 225
        self.undo_stack: List[np.ndarray] = []
        self.redo_stack: List[np.ndarray] = []
        self.cursor_size = 10
        self.cursor_pos = (0, 0)
        self.cursor_thickness = 1
        self.ix, self.iy = -1, -1
        self.points = []
        self.weight = 0.45

        self.parameters = [AdjusterParameters() for _ in images]
        self.current_parameters = self.parameters[self.current_page_index]
        self.apply_same_parameters = True


    def get_image_size(self):
        if self.current_image is not None:
            return self.current_image.shape[1], self.current_image.shape[0]
        else:
            return None

    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask' + '.png'
        cv2.imwrite(path, self.final_mask)
        print("Mask saved as " + path)

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
            loaded_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if loaded_mask is None:
                # print("No saved mask found. Using default mask.")
                self.reset_mask()

            elif len(loaded_mask.shape) == 2:
                loaded_mask = cv2.cvtColor(loaded_mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)

            if loaded_mask.shape != self.current_image.shape:
                loaded_mask = resize_image(loaded_mask, self.current_image.shape[1], self.current_image.shape[0])
                # print(f"Resized loaded mask from {path} to match current image size.")
            self.final_mask = loaded_mask
        except:
            print(f"Error loading mask from {path}. Using default mask.")
            # print("Mask size:", self.final_mask.shape)
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
        """Return the current image with the mask applied based on the weight."""
        if self.current_image is None or self.final_mask is None:
            raise ValueError("Current image or final mask is not set.")
        # Perform blending using NumPy
        blended_image = (1 - self.weight) * self.current_image.astype(np.float32) + \
                        self.weight * self.get_bgr_mask().astype(np.float32)
        # Clip values to valid range and convert back to uint8
        return np.clip(blended_image, 0, 255).astype(np.uint8)


    def get_processed_current_image(self):
        current_image = self.images[self.current_page_index]
        lower = np.array([self.current_parameters.b_min, self.current_parameters.g_min, self.current_parameters.r_min], dtype=np.uint8)
        upper = np.array([self.current_parameters.b_max, self.current_parameters.g_max, self.current_parameters.r_max], dtype=np.uint8)
        mask = cv2.bitwise_and(current_image, self.get_bgr_mask())
        gray_mask = cv2.inRange(mask, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(self.get_bgr_mask(), cv2.COLOR_BGR2GRAY))
        if self.current_parameters.mode:
            processed_current_image = fill_masked_area(current_image, gray_mask)
        else:
            processed_current_image = inpaint_image(current_image, gray_mask)

        processed_current_image = sharpen_image(processed_current_image, self.current_parameters.w / 10 )
        return processed_current_image

    def set_all_parameters_the_same_as_current(self):
        params = self.current_parameters.get_parameters()
        for i in range(len(self.parameters)):
            self.parameters[i].set_parameters(params)

    def get_parameters(self):
        return self.parameters


