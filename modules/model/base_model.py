import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from modules.controller.constants import MaskMode
from modules.utils import calc_median_image, AdjusterParameters, fill_masked_area, inpaint_image, sharpen_image, \
    resize_images, load_pdf
from web.utils import resize_image


@dataclass
class ImageData:
    images: List[np.ndarray] = field(default_factory=list)
    original_sized_images: Optional[List[np.ndarray]] = None
    current_image: Optional[np.ndarray] = None
    median_image: Optional[np.ndarray] = None
    current_page_index: int = 0


@dataclass
class MaskData:
    mask: Optional[np.ndarray] = None
    input_mask: Optional[np.ndarray] = None
    final_mask: Optional[np.ndarray] = None
    temp_mask: Optional[np.ndarray] = None
    undo_stack: List[np.ndarray] = field(default_factory=list)
    redo_stack: List[np.ndarray] = field(default_factory=list)
    points: List = field(default_factory=list)


@dataclass
class CursorData:
    size: int = 10
    pos: Tuple[int, int] = (0, 0)
    thickness: int = 2
    ix: int = -1
    iy: int = -1


@dataclass
class ConfigData:
    max_width: int = 1920
    max_height: int = 1080
    dpi: int = 200
    mode: MaskMode = MaskMode.SELECT
    threshold_min: int = 1
    threshold_max: int = 225
    weight: float = 0.45
    apply_same_parameters: bool = True


class BaseModel:
    def __init__(self, images=None, dpi=200, max_width=1920, max_height=1080):

        self.config_data = ConfigData(max_width=max_width, max_height=max_height, dpi=dpi)
        self.image_data = ImageData()
        self.mask_data = MaskData()
        self.cursor_data = CursorData()

        self.parameters = []
        self.current_parameters = None

        self.update_data(images)

    def update_data(self, images):
        self.image_data.original_sized_images = images
        self.image_data.images = resize_images(images, self.config_data.max_width, self.config_data.max_height)
        self.mask_data.mask = np.zeros((self.image_data.images[0].shape[0], self.image_data.images[0].shape[1]), np.uint8)

        self.image_data.median_image = cv2.cvtColor(calc_median_image(self.image_data.images, 10), cv2.COLOR_BGR2GRAY)
        self.image_data.current_page_index = 0
        self.image_data.current_image = self.image_data.images[self.image_data.current_page_index].copy()

        self.mask_data.input_mask = cv2.bitwise_and(self.image_data.median_image, self.mask_data.mask)
        self.mask_data.final_mask = self.mask_data.input_mask.copy()
        self.mask_data.temp_mask = self.mask_data.final_mask.copy()
        self.mask_data.undo_stack.clear()
        self.mask_data.redo_stack.clear()
        self.mask_data.points = []

        self.parameters = [AdjusterParameters() for _ in images]
        self.current_parameters = self.parameters[self.image_data.current_page_index]

        if self.config_data.apply_same_parameters:
            self.set_all_parameters_the_same_as_current()


    def get_image_size(self):
        if self.image_data.current_image is not None:
            return self.image_data.current_image.shape[1], self.image_data.current_image.shape[0]
        return None

    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask.png'
        cv2.imwrite(path, self.mask_data.final_mask)
        print("Mask saved as " + path)

    def get_gray_mask(self):
        if len(self.mask_data.final_mask.shape) == 2:
            return self.mask_data.final_mask
        elif len(self.mask_data.final_mask.shape) == 3 and self.mask_data.final_mask.shape[2] == 3:
            return cv2.cvtColor(self.mask_data.final_mask, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Mask has an unexpected shape: " + str(self.mask_data.final_mask.shape))

    def get_bgr_mask(self):
        if len(self.mask_data.final_mask.shape) == 2:
            return cv2.cvtColor(self.mask_data.final_mask, cv2.COLOR_GRAY2BGR)
        elif len(self.mask_data.final_mask.shape) == 3 and self.mask_data.final_mask.shape[2] == 3:
            return self.mask_data.final_mask
        else:
            raise ValueError("Mask has an unexpected shape: " + str(self.mask_data.final_mask.shape))

    def load_images(self, path):
        try:
            images = load_pdf(path, self.config_data.dpi)
            self.update_data(images)
        except Exception as e:
            print(f"Error loading images: {e}")

    def load_mask(self, path=None):
        if path is None:
            return
        try:
            loaded_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if loaded_mask is None:
                # print("No saved mask found. Using default mask.")
                self.reset_mask()

            elif len(loaded_mask.shape) == 2:
                loaded_mask = cv2.cvtColor(loaded_mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)

            if loaded_mask.shape != self.image_data.current_image.shape:
                loaded_mask = resize_image(loaded_mask,
                                           self.image_data.current_image.shape[1],
                                           self.image_data.current_image.shape[0])
            self.mask_data.final_mask = loaded_mask
        except:
            print(f"Error loading mask from {path}. Using default mask.")
            # print("Mask size:", self.final_mask.shape)
            self.reset_mask()

    def reset_mask(self):
        self.mask_data.final_mask = self.mask_data.input_mask.copy()
        self.mask_data.undo_stack.clear()
        self.mask_data.redo_stack.clear()
        self.mask_data.points = []
        print("Mask reset to initial state.")

    def set_cursor_size(self, size: int):
        """Set the size of the cursor."""
        self.cursor_data.cursor_size = size

    def set_cursor_pos(self, pos: tuple):
        """Set the position of the cursor."""
        self.cursor_data.cursor_pos = pos

    def get_weighted_image(self):
        """Return the current image with the mask applied based on the weight."""
        if self.image_data.current_image is None or self.mask_data.final_mask is None:
            raise ValueError("Current image or final mask is not set.")
        # Perform blending using NumPy
        blended_image = (1 - self.config_data.weight) * self.image_data.current_image.astype(np.float32) + \
                        self.config_data.weight * self.get_bgr_mask().astype(np.float32)
        # Clip values to valid range and convert back to uint8
        blended_image = np.clip(blended_image, 0, 255).astype(np.uint8)
        if self.config_data.mode == MaskMode.DRAW:
            cv2.circle(blended_image,
                       self.cursor_data.pos,
                       self.cursor_data.size,
                       (0, 0, 0),
                       self.cursor_data.thickness)
        return blended_image

    def get_processed_current_image(self):
        current_image = self.image_data.images[self.image_data.current_page_index]
        lower = np.array([self.current_parameters.b_min, self.current_parameters.g_min, self.current_parameters.r_min], dtype=np.uint8)
        upper = np.array([self.current_parameters.b_max, self.current_parameters.g_max, self.current_parameters.r_max], dtype=np.uint8)
        mask = cv2.bitwise_and(current_image, self.get_bgr_mask())
        gray_mask = cv2.inRange(mask, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(self.get_bgr_mask(), cv2.COLOR_BGR2GRAY))
        if self.current_parameters.mode:
            processed_current_image = fill_masked_area(current_image, gray_mask)
        else:
            processed_current_image = inpaint_image(current_image, gray_mask)

        processed_current_image = sharpen_image(processed_current_image, self.current_parameters.w / 10 )
        return processed_current_image

    def set_all_parameters_the_same_as_current(self):
        params = self.current_parameters.get_parameters()
        for i in range(len(self.parameters)):
            self.parameters[i].set_parameters(params)

    def get_parameters(self):
        return self.parameters

    def get_threshold_min(self):
        return self.config_data.threshold_min

    def set_threshold_min(self, value):
        self.config_data.threshold_min = int(value)

    def get_threshold_max(self):
        return self.config_data.threshold_max

    def set_threshold_max(self, value):
        self.config_data.threshold_max = int(value)

    def get_current_image(self):
        return self.image_data.images[self.image_data.current_page_index]

    def get_original_sized_images(self):
        return self.image_data.original_sized_images

    def get_resized_images(self):
        return self.image_data.images

    def get_mode(self):
        return self.config_data.mode

    def set_mode(self, mode: MaskMode):
        self.config_data.mode = mode

    def get_weight(self):
        return self.config_data.weight

    def set_weight(self, weight: float):
        self.config_data.weight = weight

    def get_final_mask(self):
        return self.mask_data.final_mask

    def get_current_page_index(self):
        return self.image_data.current_page_index

    def set_current_page_index(self, page_index: int):
        self.image_data.current_page_index = page_index
        self.image_data.current_image = self.image_data.images[page_index]
        self.current_parameters = self.parameters[page_index]




