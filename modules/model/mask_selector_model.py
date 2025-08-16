import cv2
import numpy as np
from modules.model.base_model import BaseModel



class MaskSelectorModel(BaseModel):
    def __init__(self, images):
        self.images = images
        self.width, self.height = images[0].shape[:2]
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        mask = np.zeros((self.width, self.height), np.uint8)
        self.final_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.points = []
        self.redo_stack = []
        self.undo_stack = []

    def reset_mask(self):
        self.final_mask = cv2.cvtColor(np.zeros((self.width, self.height), np.uint8), cv2.COLOR_GRAY2BGR)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_image = self.images[self.current_page_index].copy()
        self.points.clear()
        print("Mask reset to initial state.")

    def get_image_shown(self):
        return cv2.addWeighted(self.current_image, 0.7, self.final_mask, 0.3, 0)

