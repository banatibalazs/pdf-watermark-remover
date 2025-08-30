# mask_manipulator.py
import cv2
import numpy as np
from tkinter import filedialog

from modules.model.base_model import BaseModel


class MaskManipulator:
    def __init__(self, model):
        self.model: BaseModel = model

    def reset_mask(self) -> None:
        self.model.reset_mask()

    def reset_temp_mask(self) -> None:
        # Set temp_mask to all zeros
        self.model.mask_data.temp_mask = np.zeros_like(self.model.mask_data.final_mask)

    def erode_mask(self) -> None:
        self.model.mask_data.final_mask = cv2.erode(self.model.mask_data.final_mask, np.ones((3, 3), np.uint8), iterations=1)

    def dilate_mask(self) -> None:
        self.model.mask_data.final_mask = cv2.dilate(self.model.mask_data.final_mask, np.ones((3, 3), np.uint8), iterations=1)

    def apply_thresholds(self) -> None:
        filtered_median_image = cv2.inRange(self.model.image_data.median_image,
                                            np.array(self.model.get_threshold_min(), dtype=np.uint8),
                                            np.array(self.model.get_threshold_max(), dtype=np.uint8))
        self.model.mask_data.final_mask = cv2.bitwise_and(self.model.mask_data.temp_mask, cv2.inRange(filtered_median_image, 1, 255))
        # cv2.imshow("Median Image", filtered_median_image)
        # cv2.imshow("Temp Mask", self.model.mask_data.temp_mask)
        # cv2.imshow("Final Mask", self.model.mask_data.final_mask)


    def load_mask(self) -> None:
        path = filedialog.askopenfilename(
            title="Load mask",
            filetypes=[("All files", "*.*")]
        )
        if path:
            self.model.load_mask(path)

    def save_mask(self) -> None:
        path = filedialog.asksaveasfile(
            title="Save mask",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="mask.png"
        ).name
        self.model.save_mask(path)

    def get_gray_mask(self):
        return self.model.get_gray_mask() if self.model else None

    def get_bgr_mask(self):
        return self.model.get_bgr_mask() if self.model else None