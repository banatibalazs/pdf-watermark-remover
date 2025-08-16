from abc import ABC, abstractmethod
import cv2
import numpy as np
from typing import List, Optional


class BaseModel(ABC):
    def __init__(self):
        self.current_image: Optional[np.ndarray] = None
        self.input_mask: Optional[np.ndarray] = None
        self.final_mask: Optional[np.ndarray] = None
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


    def reset_mask(self):
        self.final_mask = self.input_mask.copy()
        self.update_mask()
        print("Mask reset to initial state.")