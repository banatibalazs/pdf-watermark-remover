import cv2
import numpy as np
from modules.utils import sharpen_image, fill_masked_area, inpaint_image
from modules.utils import AdjusterParameters


class ParameterAdjusterModel:
    def __init__(self, images, mask):
        self.images = images
        self.mask = mask
        self.current_index = 0
        self.parameters = [AdjusterParameters() for _ in images]
        self.current_parameters = self.parameters[self.current_index]
        self.apply_same_parameters = True


    def get_processed_current_image(self):
        current_image = self.images[self.current_index]
        lower = np.array([self.current_parameters.b_min, self.current_parameters.g_min, self.current_parameters.r_min])
        upper = np.array([self.current_parameters.b_max, self.current_parameters.g_max, self.current_parameters.r_max])
        mask = cv2.bitwise_and(current_image, self.mask)
        gray_mask = cv2.inRange(mask, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY))
        if self.current_parameters.mode:
            processed_current_image = fill_masked_area(current_image, gray_mask)
        else:
            processed_current_image = inpaint_image(current_image, gray_mask)
        processed_current_image = sharpen_image(processed_current_image, self.current_parameters.w)
        return processed_current_image

    def set_all_parameters_the_same_as_current(self):
        params = self.current_parameters.get_parameters()
        for i in range(len(self.parameters)):
            self.parameters[i].set_parameters(params)

    def get_parameters(self):
        return self.parameters

