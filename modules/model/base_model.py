import cv2
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field

from modules.controller.constants import MaskMode, CursorType
from modules.interfaces.interfaces import RedoUndoInterface
from modules.utils import calc_median_image, fill_masked_area, inpaint_image, sharpen_image, \
    resize_images, resize_mask, load_pdf


class State:
    def __init__(self, final_mask, temp_mask):
        self.temp_mask = temp_mask.copy()
        self.final_mask = final_mask.copy()

    def get_state(self):
        return self.final_mask, self.temp_mask


@dataclass
class ImageData:
    images: List[np.ndarray] = field(default_factory=list)
    original_sized_images: Optional[List[np.ndarray]] = None
    current_image: Optional[np.ndarray] = None
    median_image_bgr: Optional[np.ndarray] = None
    median_image_gray: Optional[np.ndarray] = None
    current_page_index: int = 0
    median_trackbar_pos: int = 1
    median_image_cache: dict = field(default_factory=dict)
    max_width: int = 1920
    max_height: int = 1080
    dpi: int = 200


@dataclass
class MaskData:
    mask: Optional[np.ndarray] = None
    final_mask: Optional[np.ndarray] = None
    temp_mask: Optional[np.ndarray] = None
    temp_mask_after_threshold: Optional[np.ndarray] = None
    undo_stack: List[State] = field(default_factory=list)
    redo_stack: List[State] = field(default_factory=list)
    points: List = field(default_factory=list)


@dataclass
class CursorData:
    type: CursorType = CursorType.CIRCLE
    size: int = 10
    pos: Tuple[int, int] = (0, 0)
    thickness: int = 2
    ix: int = -1
    iy: int = -1


@dataclass
class ConfigData:
    mode: MaskMode = MaskMode.SELECT
    threshold_min: int = 1
    threshold_max: int = 225
    weight: float = 0.45
    apply_same_parameters: bool = True


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


class ConfigModel:
    def __init__(self):
        self.config_data = ConfigData()

    def get_mode(self) -> MaskMode:
        return self.config_data.mode

    def set_mode(self, mode: MaskMode):
        self.config_data.mode = mode

    def get_weight(self) -> float:
        return self.config_data.weight

    def set_weight(self, weight: float):
        self.config_data.weight = weight

    def get_threshold_min(self) -> int:
        return self.config_data.threshold_min

    def set_threshold_min(self, value: int):
        self.config_data.threshold_min = int(value)

    def get_threshold_max(self) -> int:
        return self.config_data.threshold_max

    def set_threshold_max(self, value: int):
        self.config_data.threshold_max = int(value)

    def toggle_apply_same_parameters(self) -> bool:
        self.config_data.apply_same_parameters = not self.config_data.apply_same_parameters
        return self.config_data.apply_same_parameters

    def get_apply_same_parameters(self) -> bool:
        return self.config_data.apply_same_parameters


class ImageModel:
    def __init__(self, path, max_width=1920, max_height=1080, dpi=200):
        self.image_data = ImageData(max_width=max_width, max_height=max_height, dpi=dpi)
        self.load_images(path)

    def update_data(self, images: List[np.ndarray]) -> None:
        self.image_data.original_sized_images = images
        self.image_data.images = resize_images(images, self.image_data.max_width, self.image_data.max_height)
        self.image_data.median_image_cache = {}

        self.image_data.median_image_bgr = calc_median_image(self.image_data.images, self.get_median_trackbar_pos())
        self.image_data.median_image_gray = cv2.cvtColor(self.image_data.median_image_bgr, cv2.COLOR_BGR2GRAY)
        self.update_current_image()

    def update_current_image(self):
        if self.image_data.median_trackbar_pos == 1:
            self.image_data.current_image = self.image_data.images[self.image_data.current_page_index].copy()
        else:
            self.image_data.current_image = self.image_data.median_image_bgr.copy()

    def load_images(self, path: str) -> None:
        try:
            images = load_pdf(path, self.image_data.dpi)
            self.update_data(images)
            return True
        except Exception as e:
            print(f"Error loading images: {e}")
            return False

    def get_current_image(self) -> np.ndarray:
        if self.image_data.median_trackbar_pos == 1:
            image = self.image_data.images[self.image_data.current_page_index]
        else:
            image = self.image_data.median_image_bgr
        return image

    def get_current_image_gray(self) -> np.ndarray:
        if self.image_data.current_image is not None:
            return cv2.cvtColor(self.image_data.current_image, cv2.COLOR_BGR2GRAY)
        return None

    def get_image_size(self) -> Optional[Tuple[int, int]]:
        if self.image_data.current_image is not None:
            return self.image_data.current_image.shape[1], self.image_data.current_image.shape[0]
        return None

    def prev_image(self) -> bool:
        if self.image_data.current_page_index > 0:
            self.image_data.current_page_index -= 1
            self.update_current_image()
            return True
        return False

    def next_image(self) -> bool:
        if self.image_data.current_page_index < len(self.image_data.images) - 1:
            self.image_data.current_page_index += 1
            self.update_current_image()
            return True
        return False

    def set_median_trackbar_pos(self, tb_pos: int) -> None:
        self.image_data.median_trackbar_pos = int(tb_pos)
        self.update_median_image()

    def get_median_trackbar_pos(self) -> int:
        return self.image_data.median_trackbar_pos

    def update_median_image(self) -> None:
        tb_pos = self.get_median_trackbar_pos()
        if tb_pos > 10:
            if tb_pos % 10 < 5:
                tb_pos = (tb_pos // 10) * 10 + 5
            else:
                tb_pos = ((tb_pos + 5) // 10) * 10

        if tb_pos in self.image_data.median_image_cache:
            self.image_data.median_image_bgr = self.image_data.median_image_cache[tb_pos]
        else:
            median_img = calc_median_image(self.image_data.images, tb_pos)
            self.image_data.median_image_cache[tb_pos] = median_img
            self.image_data.median_image_bgr = median_img
        self.image_data.median_image_gray = cv2.cvtColor(self.image_data.median_image_bgr, cv2.COLOR_BGR2GRAY)
        self.update_current_image()

    def get_current_page_index(self) -> int:
        return self.image_data.current_page_index

    def get_total_images(self) -> int:
        return len(self.image_data.images)

    def get_original_sized_images(self) -> List[np.ndarray]:
        return self.image_data.original_sized_images

    def get_resized_images(self) -> List[np.ndarray]:
        return self.image_data.images

    def set_current_image(self, image: np.ndarray) -> None:
        self.image_data.current_image = image

    def get_image_shape(self) -> Optional[Tuple[int, int, int]]:
        if self.image_data.current_image is not None:
            return self.image_data.current_image.shape
        return None


class MaskModel(RedoUndoInterface):
    def __init__(self, image_shape):
        self.mask_data = MaskData(image_shape)
        self.img_shape = image_shape
        self.initialize_mask()

    def initialize_mask(self) -> None:
        self.mask_data.mask = np.zeros((self.img_shape[0], self.img_shape[1]), np.uint8)
        self.mask_data.final_mask = self.mask_data.mask.copy()
        self.mask_data.temp_mask = self.mask_data.final_mask.copy()
        self.mask_data.temp_mask_after_threshold = self.mask_data.final_mask.copy()
        self.mask_data.undo_stack.clear()
        self.mask_data.redo_stack.clear()
        self.mask_data.points = []

    def get_gray_mask(self) -> np.ndarray:
        if len(self.mask_data.final_mask.shape) == 2:
            return self.mask_data.final_mask
        elif len(self.mask_data.final_mask.shape) == 3 and self.mask_data.final_mask.shape[2] == 3:
            return cv2.cvtColor(self.mask_data.final_mask, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Mask has an unexpected shape: " + str(self.mask_data.final_mask.shape))

    def get_bgr_mask(self, mode) -> np.ndarray:
        if mode == MaskMode.THRESHOLD:
            mask = self.mask_data.temp_mask_after_threshold
        else:
            mask = self.mask_data.temp_mask
        if len(mask.shape) == 2:
            return cv2.cvtColor(cv2.bitwise_or(mask, self.mask_data.final_mask), cv2.COLOR_GRAY2BGR)
        elif len(mask.shape) == 3 and mask.shape[2] == 3:
            return cv2.bitwise_or(mask, self.mask_data.final_mask)
        else:
            raise ValueError("Mask has an unexpected shape: " + str(self.mask_data.final_mask.shape))

    def save_mask(self, path=None) -> None:
        if path is None:
            path = 'saved_mask.png'
        cv2.imwrite(path, cv2.bitwise_or(self.mask_data.final_mask, self.mask_data.temp_mask))
        print("Mask saved as " + path)

    def load_mask(self, path=None) -> bool:
        try:
            loaded_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if len(loaded_mask.shape) == 3 and loaded_mask.shape[2] == 3:
                loaded_mask = cv2.cvtColor(loaded_mask, cv2.COLOR_BGR2GRAY)

            if loaded_mask.shape != self.img_shape[:2]:
                loaded_mask = resize_mask(loaded_mask, self.img_shape[1], self.img_shape[0])
                print(f"Resized loaded mask to match image size: {loaded_mask.shape}")
                print(f"Image size: {self.img_shape}")
            self.mask_data.final_mask = loaded_mask
            self.reset_temp_mask()
            return True
        except Exception as e:
            print(f"Error loading mask from {path}. Using default mask. Error: {e}")
            return False

    def reset_temp_mask(self) -> None:
        self.mask_data.temp_mask = self.mask_data.mask.copy()
        self.mask_data.temp_mask_after_threshold = self.mask_data.mask.copy()

    def reset_mask(self) -> None:
        self.mask_data.final_mask = self.mask_data.mask.copy()
        self.reset_temp_mask()
        self.mask_data.undo_stack.clear()
        self.mask_data.redo_stack.clear()
        self.mask_data.points = []

    # RedoUndoInterface implementation
    def undo(self) -> None:
        if not self.mask_data.undo_stack:
            return

        current_state = State(self.get_final_mask(), self.get_temp_mask())
        self.mask_data.redo_stack.append(current_state)

        previous_state = self.mask_data.undo_stack.pop()
        self.restore_state(previous_state)

    def redo(self) -> None:
        if not self.mask_data.redo_stack:
            return

        current_state = State(self.get_final_mask(), self.get_temp_mask())
        self.mask_data.undo_stack.append(current_state)

        next_state = self.mask_data.redo_stack.pop()
        self.restore_state(next_state)

    def restore_state(self, state: State) -> None:
        self.mask_data.final_mask, self.mask_data.temp_mask = state.get_state()
        self.mask_data.temp_mask_after_threshold = self.mask_data.temp_mask.copy()

    def save_state(self) -> None:
        current_state = State(self.get_final_mask(), self.get_temp_mask())
        self.mask_data.undo_stack.append(current_state)
        self.mask_data.redo_stack.clear()

    def get_temp_mask(self) -> np.ndarray:
        return self.mask_data.temp_mask

    def set_temp_mask(self, value: np.ndarray) -> None:
        self.mask_data.temp_mask = value

    def get_temp_mask_after_threshold(self) -> np.ndarray:
        return self.mask_data.temp_mask_after_threshold

    def set_temp_mask_after_threshold(self, value: np.ndarray) -> None:
        self.mask_data.temp_mask_after_threshold = value

    def get_final_mask(self) -> np.ndarray:
        return self.mask_data.final_mask

    def set_final_mask(self, value: np.ndarray) -> None:
        self.mask_data.final_mask = value


class CursorModel:
    def __init__(self):
        self.cursor_data = CursorData()

    def toggle_cursor_type(self) -> None:
        if self.cursor_data.type == CursorType.CIRCLE:
            self.cursor_data.type = CursorType.SQUARE
        else:
            self.cursor_data.type = CursorType.CIRCLE
        print("Cursor type changed to:", self.cursor_data.type)

    def set_cursor_size(self, size: int) -> None:
        self.cursor_data.size = size

    def set_cursor_pos(self, pos: tuple) -> None:
        self.cursor_data.pos = pos

    def get_cursor_type(self) -> CursorType:
        return self.cursor_data.type

    def get_cursor_size(self) -> int:
        return self.cursor_data.size

    def get_cursor_pos(self) -> Tuple[int, int]:
        return self.cursor_data.pos


class ParameterModel:
    def __init__(self, image_model: ImageModel):
        self.image_model = image_model
        self.parameters: List[ParamsForRemoval] = []
        self.current_parameters: Optional[ParamsForRemoval] = None
        self.initialize_parameters()

    def initialize_parameters(self) -> None:
        total_images = self.image_model.get_total_images()
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


class BaseModel(RedoUndoInterface):
    def __init__(self, path=None, dpi=200, max_width=1920, max_height=1080):
        self.config_model = ConfigModel()
        self.image_model = ImageModel(path, max_width, max_height, dpi)
        self.mask_model = MaskModel(self.image_model.get_image_shape())
        self.cursor_model = CursorModel()
        self.parameter_model = ParameterModel(self.image_model)

    def update_data(self, images):
        self.image_model.update_data(images)
        self.mask_model.initialize_mask()
        self.parameter_model.initialize_parameters()

        if self.config_model.get_apply_same_parameters():
            self.parameter_model.set_all_parameters_the_same_as_current()

    def load_mask(self, path):
        if self.mask_model.load_mask(path):
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

        blended_image = ((1 - self.config_model.get_weight()) * current_image.astype(np.float32) + \
                        self.config_model.get_weight() *
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

    def toggle_apply_same_parameters(self):
        apply_same = self.config_model.toggle_apply_same_parameters()
        print("Apply same parameters to all images:", apply_same)
        if apply_same:
            self.parameter_model.set_all_parameters_the_same_as_current()
        return apply_same


