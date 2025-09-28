import cv2
import numpy as np

from modules.controller.constants import MaskMode, CursorType
from modules.interfaces.interfaces import RedoUndoInterface
from modules.model.config_model import ConfigModel
from modules.model.cursor_model import CursorModel
from modules.model.image_model import ImageModel
from modules.model.mask_model import MaskModel
from modules.model.parameter_model import ParameterModel
from modules.utils import fill_masked_area, inpaint_image, sharpen_image


class BaseModel(RedoUndoInterface):
    def __init__(self, path=None, dpi=200, max_width=1920, max_height=1080):
        self.config_model = ConfigModel()
        self.image_model = ImageModel(path, max_width, max_height, dpi)
        self.mask_model = MaskModel(self.image_model.get_image_shape())
        self.cursor_model = CursorModel()
        self.parameter_model = ParameterModel(self.image_model)

    def update_data(self, images):
        self.image_model.update_data(images)
        self.mask_model.update_mask(self.image_model.get_image_shape())


    def load_mask(self, path):
        if self.mask_model.load_mask(path, self.image_model.get_image_shape()):
            self.mask_model.save_state()

    def get_image_to_show(self):
        if self.config_model.get_mode() == MaskMode.ADJUST:
            return self.get_processed_current_image()
        else:
            return self.get_weighted_image()

    def get_weighted_image(self) -> np.ndarray:
        current_image = self.image_model.get_current_image()
        if current_image is None or self.mask_model.mask_data.final_mask is None:
            raise ValueError("Current image or final mask is not set.")

        weight = self.config_model.get_weight()
        blended_image = ((1 - weight) * current_image.astype(np.float32) + \
                        weight *
                         self.get_bgr_mask().astype(np.float32))
        blended_image = np.clip(blended_image, 0, 255).astype(np.uint8)

        if self.config_model.get_mode() == MaskMode.DRAW:
            blended_image = self.draw_cursor(blended_image)
        return blended_image

    def draw_cursor(self, image: np.ndarray) -> np.ndarray:
        if self.cursor_model.cursor_data.type == CursorType.CIRCLE:
            cv2.circle(image,
                       self.cursor_model.cursor_data.pos,
                       self.cursor_model.cursor_data.size,
                       (0, 0, 0),
                       self.cursor_model.cursor_data.thickness)
        elif self.cursor_model.cursor_data.type == CursorType.SQUARE:
            size = self.cursor_model.cursor_data.size
            top_left = (self.cursor_model.cursor_data.pos[0] - size, self.cursor_model.cursor_data.pos[1] - size)
            bottom_right = (self.cursor_model.cursor_data.pos[0] + size, self.cursor_model.cursor_data.pos[1] + size)
            cv2.rectangle(image,
                          top_left,
                          bottom_right,
                          (0, 0, 0),
                          self.cursor_model.cursor_data.thickness)
        return image

    def get_bgr_mask(self) -> np.ndarray:
        return self.mask_model.get_bgr_mask(self.config_model.get_mode())

    def get_processed_current_image(self) -> np.ndarray:
        current_image = self.image_model.get_current_image()
        lower = np.array([self.parameter_model.get_current_parameters().b_min,
                          self.parameter_model.get_current_parameters().g_min,
                          self.parameter_model.get_current_parameters().r_min], dtype=np.uint8)
        upper = np.array([self.parameter_model.get_current_parameters().b_max,
                          self.parameter_model.get_current_parameters().g_max,
                          self.parameter_model.get_current_parameters().r_max], dtype=np.uint8)

        bgr_mask = self.get_bgr_mask()
        mask = cv2.bitwise_and(current_image, bgr_mask)
        gray_mask = cv2.inRange(mask, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(bgr_mask, cv2.COLOR_BGR2GRAY))

        if self.parameter_model.get_current_parameters().mode:
            processed_image = fill_masked_area(current_image, gray_mask)
        else:
            processed_image = inpaint_image(current_image, gray_mask)

        processed_image = sharpen_image(processed_image, self.parameter_model.get_current_parameters().w / 10)
        return processed_image

    # RedoUndoInterface delegation
    def undo(self) -> None:
        self.mask_model.undo()

    def redo(self) -> None:
        self.mask_model.redo()

    def save_state(self) -> None:
        self.mask_model.save_state()

    # Navigation methods that need coordination
    def prev_image(self):
        if self.image_model.prev_image():
            return True
        return False

    def next_image(self):
        if self.image_model.next_image():
            return True
        return False


