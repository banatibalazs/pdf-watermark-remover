from abc import ABC, abstractmethod
import cv2
import numpy as np
from typing import List, Optional


class BaseModel(ABC):
    def __init__(self, mask=None):
        self.input_mask: Optional[np.ndarray] = mask
        self.final_mask: Optional[np.ndarray] = mask.copy() if mask is not None else None
        self.undo_stack: List[np.ndarray] = []
        self.redo_stack: List[np.ndarray] = []


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
        print("Mask reset to initial state.")


class ModelWithDrawing(BaseModel):
    def __init__(self, input_mask=None):
        super().__init__(input_mask)
        self.cursor_size = 10
        self.cursor_pos = (0, 0)
        self.cursor_thickness = 1
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.points = []

    def set_cursor_size(self, size: int):
        """Set the size of the cursor."""
        self.cursor_size = size

    def set_cursor_pos(self, pos: tuple):
        """Set the position of the cursor."""
        self.cursor_pos = pos
