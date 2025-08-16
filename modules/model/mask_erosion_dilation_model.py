import cv2
import numpy as np

from modules.model.base_model import BaseModel


class MaskErosionDilationModel(BaseModel):
    def __init__(self, input_mask):
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.kernel = np.ones((3, 3), np.uint8)
        self.redo_stack = []
        self.undo_stack = []

    def dilate(self):
        self.final_mask = cv2.dilate(self.final_mask, self.kernel, iterations=1)

    def erode(self):
        self.final_mask = cv2.erode(self.final_mask, self.kernel, iterations=1)

    def reset(self):
        self.final_mask = self.input_mask.copy()

    def get_image_shown(self):
        return self.final_mask

    def reset_mask(self):
        self.final_mask = self.input_mask.copy()
        self.undo_stack.clear()
        self.redo_stack.clear()
        print("Mask reset to initial state.")

