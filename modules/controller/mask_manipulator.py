# mask_manipulator.py
import cv2
import numpy as np
from tkinter import filedialog

from modules.controller.constants import CursorType
from modules.model.base_model import BaseModel


class MaskManipulator:
    def __init__(self, model):
        self.model: BaseModel = model

    def reset_mask(self) -> None:
        self.model.reset_mask()

    def reset_temp_mask(self) -> None:
        # Set temp mask to all zeros with shape like the final mask
        self.model.mask_data.temp_mask = np.zeros_like(self.model.mask_data.final_mask)

    def erode_mask(self) -> None:
        self.model.mask_data.final_mask = cv2.erode(self.model.mask_data.final_mask, np.ones((3, 3), np.uint8), iterations=1)

    def dilate_mask(self) -> None:
        self.model.mask_data.final_mask = cv2.dilate(self.model.mask_data.final_mask, np.ones((3, 3), np.uint8), iterations=1)

    def _draw_on_mask(self, color):
        if self.model.cursor_data.type == CursorType.CIRCLE:
            cv2.circle(
                self.model.mask_data.final_mask,
                self.model.cursor_data.pos,
                self.model.cursor_data.size,
                [color],
                -1
            )
        elif self.model.cursor_data.type == CursorType.SQUARE:
            x, y = self.model.cursor_data.pos
            size = self.model.cursor_data.size
            cv2.rectangle(self.model.mask_data.final_mask,
                          (x - size, y - size),
                          (x + size, y + size),
                          [color],
                          -1)

    def draw_white(self):
        self._draw_on_mask(255)

    def draw_black(self):
        self._draw_on_mask(0)

    def apply_thresholds(self) -> None:
        filtered_median_image = cv2.inRange(self.model.get_current_image_gray(),
                                            np.array(self.model.get_threshold_min(), dtype=np.uint8),
                                            np.array(self.model.get_threshold_max(), dtype=np.uint8))

        self.model.mask_data.temp_mask_after_threshold = cv2.bitwise_and(filtered_median_image, self.model.mask_data.temp_mask)

    def add_temp_mask_to_final_mask(self):
        self.model.mask_data.final_mask = cv2.bitwise_or(self.model.mask_data.final_mask, self.model.mask_data.temp_mask_after_threshold)

    def get_gray_mask(self):
        return self.model.get_gray_mask() if self.model else None

    def get_bgr_mask(self):
        return self.model.get_bgr_mask() if self.model else None