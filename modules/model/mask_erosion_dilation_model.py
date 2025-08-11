import cv2
import numpy as np


class MaskErosionDilationModel:
    def __init__(self, input_mask):
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.kernel = np.ones((3, 3), np.uint8)

    def dilate(self):
        self.final_mask = cv2.dilate(self.final_mask, self.kernel, iterations=1)

    def erode(self):
        self.final_mask = cv2.erode(self.final_mask, self.kernel, iterations=1)

    def reset(self):
        self.final_mask = self.input_mask.copy()

    def get_gray_mask(self):
        return self.final_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)

    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask.png'
        cv2.imwrite(path, self.final_mask)
        print("Mask saved as " + path)
        print("Mask size:", self.final_mask.shape)

    def load_mask(self, path=None):
        if path is None:
            return
        try:
            self.final_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if self.final_mask is None:
                print("No saved mask found. Using default mask.")
                self.reset()
            else:
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_BGR2GRAY)
                self.final_mask = cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)
        except Exception as e:
            print(f"Error loading mask from {path}: {e}")
            self.reset()