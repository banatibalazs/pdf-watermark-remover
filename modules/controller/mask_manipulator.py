# mask_manipulator.py
import cv2
import numpy as np
from tkinter import filedialog


class MaskManipulator:
    def __init__(self, model):
        self.model = model

    def reset_mask(self) -> None:
        self.model.reset_mask()

    def erode_mask(self) -> None:
        self.model.final_mask = cv2.erode(self.model.final_mask, np.ones((3, 3), np.uint8), iterations=1)

    def dilate_mask(self) -> None:
        self.model.final_mask = cv2.dilate(self.model.final_mask, np.ones((3, 3), np.uint8), iterations=1)

    def apply_thresholds(self) -> None:
        median_image = cv2.inRange(self.model.median_image, np.array(self.model.threshold_min, dtype=np.uint8),
                                   np.array(self.model.threshold_max, dtype=np.uint8))
        self.model.final_mask = cv2.bitwise_and(self.model.temp_mask, cv2.inRange(median_image, 1, 255))

    def load_mask(self) -> None:
        path = filedialog.askopenfilename(
            title="Load mask",
            filetypes=[("All files", "*.*")]
        )
        if path:
            self.model.load_mask(path)

    def save_mask(self, path: str = 'saved_mask.png') -> None:
        self.model.save_mask(path)

    def get_gray_mask(self):
        return self.model.get_gray_mask() if self.model else None

    def get_bgr_mask(self):
        return self.model.get_bgr_mask() if self.model else None