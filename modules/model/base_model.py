from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import cv2
import numpy as np

from modules.controller.constants import MaskMode, CursorType
from modules.interfaces.interfaces import RedoUndoInterface
from modules.model.config_model import ConfigModel
from modules.model.cursor_model import CursorModel
from modules.model.image_model import ImageModel
from modules.model.mask_model import MaskModel
from modules.utils import fill_masked_area, inpaint_image, sharpen_image


@dataclass
class ParamsForRemoval:
    r_min: int = 90
    r_max: int = 240
    g_min: int = 90
    g_max: int = 240
    b_min: int = 90
    b_max: int = 240
    w: float = 0
    mode: bool = True

    def get_parameters(self):
        return [self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode]

    def set_parameters(self, args):
        self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode = args

    @staticmethod
    def get_parameter_names():
        return ['r_min', 'r_max', 'g_min', 'g_max', 'b_min', 'b_max', 'w', 'mode']

    def get_params_as_dict(self):
        return {'names': self.get_parameter_names(),
                'values': self.get_parameters()}


class ParameterModel:
    def __init__(self, image_model: ImageModel):
        self.image_model = image_model
        self.parameters: List[ParamsForRemoval] = []
        self.current_parameters: Optional[ParamsForRemoval] = None
        self.apply_same_parameters = True
        self.initialize_parameters()

    def initialize_parameters(self) -> None:
        total_images = self.image_model.get_number_of_pages()
        self.parameters = [ParamsForRemoval() for _ in range(total_images)]
        self.current_parameters = self.parameters[self.image_model.get_current_page_index()]

    def update_current_parameters(self) -> None:
        self.current_parameters = self.parameters[self.image_model.get_current_page_index()]

    def get_current_parameters(self) -> Dict[str, Any]:
        return self.current_parameters.get_params_as_dict()

    def set_all_parameters_the_same_as_current(self) -> None:
        params = self.current_parameters.get_parameters()
        for param in self.parameters:
            param.set_parameters(params)

    def get_parameters(self) -> List[ParamsForRemoval]:
        return self.parameters

    def toggle_apply_same_parameters(self) -> bool:
        self.apply_same_parameters = not self.apply_same_parameters
        return self.apply_same_parameters

    def get_apply_same_parameters(self) -> bool:
        return self.apply_same_parameters

    def set_current_parameter(self, attr: str, val: Any) -> None:
        if hasattr(self.current_parameters, attr):
            setattr(self.current_parameters, attr, val)
            print(f"Set {attr} to {val} for current parameters.")
            # If apply_same_parameters is enabled, update all parameters
            if self.apply_same_parameters:
                print(f"Set {attr} to {val} for all parameters.")
                for param in self.parameters:
                    setattr(param, attr, val)
        else:
            raise AttributeError(f"ParamsForRemoval has no attribute '{attr}'")


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
        self.parameter_model.initialize_parameters()

        if self.config_model.get_apply_same_parameters():
            self.parameter_model.set_all_parameters_the_same_as_current()

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
        lower = np.array([self.parameter_model.current_parameters.b_min,
                          self.parameter_model.current_parameters.g_min,
                          self.parameter_model.current_parameters.r_min], dtype=np.uint8)
        upper = np.array([self.parameter_model.current_parameters.b_max,
                          self.parameter_model.current_parameters.g_max,
                          self.parameter_model.current_parameters.r_max], dtype=np.uint8)

        bgr_mask = self.get_bgr_mask()
        mask = cv2.bitwise_and(current_image, bgr_mask)
        gray_mask = cv2.inRange(mask, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(bgr_mask, cv2.COLOR_BGR2GRAY))

        if self.parameter_model.current_parameters.mode:
            processed_image = fill_masked_area(current_image, gray_mask)
        else:
            processed_image = inpaint_image(current_image, gray_mask)

        processed_image = sharpen_image(processed_image, self.parameter_model.current_parameters.w / 10)
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
            self.parameter_model.update_current_parameters()
            return True
        return False

    def next_image(self):
        if self.image_model.next_image():
            self.parameter_model.update_current_parameters()
            return True
        return False


