# mask_manipulator.py
import cv2
import numpy as np
from tkinter import filedialog
from modules.controller.constants import MaskMode

from modules.controller.constants import CursorType
from modules.model.base_model import BaseModel


class MaskManipulator:
    def __init__(self, model):
        self.model: BaseModel = model

    def reset_mask(self) -> None:
        self.model.mask_model.reset_mask()

    def reset_temp_mask(self) -> None:
        # Set temp mask to all zeros with shape like the final mask
        self.model.mask_model.set_temp_mask(np.zeros_like(self.model.mask_model.get_final_mask()))

    def erode_mask(self) -> None:
        if self.model.config_model.get_mode() == MaskMode.THRESHOLD:
            self.model.mask_model.set_temp_mask_after_threshold(cv2.erode(self.model.mask_model.get_temp_mask_after_threshold(),
                                                               np.ones((3, 3), np.uint8), iterations=1))
        else:
            self.model.mask_model.set_temp_mask(cv2.erode(self.model.mask_model.get_temp_mask(), np.ones((3, 3),
                                                                                   np.uint8), iterations=1))
            self.model.mask_model.set_final_mask(cv2.erode(self.model.mask_model.get_final_mask(), np.ones((3, 3),
                                                                                     np.uint8), iterations=1))

    def dilate_mask(self) -> None:
        if self.model.config_model.get_mode() == MaskMode.THRESHOLD:
            self.model.mask_model.set_temp_mask_after_threshold(cv2.dilate(self.model.mask_model.get_temp_mask_after_threshold(),
                                                                np.ones((3, 3), np.uint8), iterations=1))
        else:
            self.model.mask_model.set_final_mask(cv2.dilate(self.model.mask_model.get_final_mask(), np.ones((3, 3),
                                                                                      np.uint8), iterations=1))
            self.model.mask_model.set_temp_mask(cv2.dilate(self.model.mask_model.get_temp_mask(), np.ones((3, 3),
                                                                                      np.uint8), iterations=1))

    def _draw_on_mask(self, color, mask):
        if self.model.cursor_model.get_cursor_type() == CursorType.CIRCLE:
            cv2.circle(
                mask,
                self.model.cursor_model.get_cursor_pos(),
                self.model.cursor_model.get_cursor_size(),
                [color],
                -1
            )
        elif self.model.cursor_model.get_cursor_type() == CursorType.SQUARE:
            x, y = self.model.cursor_model.get_cursor_pos()
            size = self.model.cursor_model.get_cursor_size()
            cv2.rectangle(mask,
                          (x - size, y - size),
                          (x + size, y + size),
                          [color],
                          -1)

    def draw(self):
        self._draw_on_mask(255, self.model.mask_model.get_temp_mask())

    def erase(self):
        self._draw_on_mask(0, self.model.mask_model.get_final_mask())
        self._draw_on_mask(0, self.model.mask_model.get_temp_mask())

    def apply_thresholds(self) -> None:
        filtered_image = cv2.inRange(self.model.image_model.get_current_image_gray(),
                                            np.array(self.model.mask_model.get_threshold_min(), dtype=np.uint8),
                                            np.array(self.model.mask_model.get_threshold_max(), dtype=np.uint8))

        self.model.mask_model.set_temp_mask_after_threshold(cv2.bitwise_and(filtered_image, self.model.mask_model.mask_data.temp_mask))

    def add_temp_mask_to_final_mask(self):
        self.model.mask_model.set_final_mask(cv2.bitwise_or(self.model.mask_model.get_final_mask(),
                                                            self.model.mask_model.get_temp_mask_after_threshold()))
        self.model.mask_model.reset_temp_mask()

    def save_state(self):
        self.model.save_state()

    def redo(self):
        self.model.redo()

    def undo(self):
        self.model.undo()

