from dataclasses import dataclass, field
from typing import List, Optional

import cv2
import numpy as np

from modules.controller.constants import MaskMode
from modules.interfaces.interfaces import RedoUndoInterface
from modules.utils import resize_mask


class State:
    def __init__(self, final_mask, temp_mask):
        self.temp_mask = temp_mask.copy()
        self.final_mask = final_mask.copy()

    def get_state(self):
        return self.final_mask, self.temp_mask



@dataclass
class MaskData:
    mask: Optional[np.ndarray] = None
    final_mask: Optional[np.ndarray] = None
    temp_mask: Optional[np.ndarray] = None
    temp_mask_after_threshold: Optional[np.ndarray] = None
    undo_stack: List[State] = field(default_factory=list)
    redo_stack: List[State] = field(default_factory=list)
    points: List = field(default_factory=list)
    threshold_min: int = 1
    threshold_max: int = 255


class MaskModel(RedoUndoInterface):
    def __init__(self, image_shape):
        self.mask_data = MaskData(image_shape)
        self.update_mask(image_shape)

    def update_mask(self, shape) -> None:
        self.mask_data.mask = np.zeros((shape[0], shape[1]), np.uint8)
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

    def load_mask(self, path, shape) -> bool:
        try:
            loaded_mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if len(loaded_mask.shape) == 3 and loaded_mask.shape[2] == 3:
                loaded_mask = cv2.cvtColor(loaded_mask, cv2.COLOR_BGR2GRAY)

            if loaded_mask.shape != shape[:2]:
                loaded_mask = resize_mask(loaded_mask, shape[1], shape[0])
                print(f"Resized loaded mask to match image size: {loaded_mask.shape}")
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

    def get_threshold_min(self) -> int:
        return self.mask_data.threshold_min

    def set_threshold_min(self, value: int):
        self.mask_data.threshold_min = int(value)

    def get_threshold_max(self) -> int:
        return self.mask_data.threshold_max

    def set_threshold_max(self, value: int):
        self.mask_data.threshold_max = int(value)