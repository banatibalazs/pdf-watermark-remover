import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from modules.controller.constants import MaskMode, CursorType
from modules.utils import calc_median_image, fill_masked_area, inpaint_image, sharpen_image, \
    resize_images, resize_mask, load_pdf


@dataclass
class ImageData:
    images: List[np.ndarray] = field(default_factory=list)
    original_sized_images: Optional[List[np.ndarray]] = None
    current_image: Optional[np.ndarray] = None
    median_image_bgr: Optional[np.ndarray] = None
    median_image_gray: Optional[np.ndarray] = None
    current_page_index: int = 0
    median_trackbar_pos: int = 1


@dataclass
class MaskData:
    mask: Optional[np.ndarray] = None
    final_mask: Optional[np.ndarray] = None
    temp_mask: Optional[np.ndarray] = None
    temp_mask_after_threshold: Optional[np.ndarray] = None
    undo_stack: List[np.ndarray] = field(default_factory=list)
    redo_stack: List[np.ndarray] = field(default_factory=list)
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
    max_width: int = 1920
    max_height: int = 1080
    dpi: int = 200
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

    def get_parameter_names(self):
        return ['r_min', 'r_max', 'g_min', 'g_max', 'b_min', 'b_max', 'w', 'mode']

    def get_params_as_dict(self):
        return { 'names': self.get_parameter_names(),
                 'values': self.get_parameters() }


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

        self.image_data.median_image_bgr = calc_median_image(self.image_data.images, self.get_median_trackbar_pos())
        self.image_data.median_image_gray = cv2.cvtColor(self.image_data.median_image_bgr, cv2.COLOR_BGR2GRAY)
        self.update_current_image()

        self.mask_data.final_mask = self.mask_data.mask.copy()
        self.mask_data.temp_mask = self.mask_data.final_mask.copy()
        self.mask_data.temp_mask_after_threshold = self.mask_data.final_mask.copy()
        self.mask_data.undo_stack.clear()
        self.mask_data.redo_stack.clear()
        self.mask_data.points = []

        self.parameters = [ParamsForRemoval() for _ in images]
        self.current_parameters = self.parameters[self.image_data.current_page_index]

        if self.config_data.apply_same_parameters:
            self.set_all_parameters_the_same_as_current()

    def toggle_apply_same_parameters(self):
        self.config_data.apply_same_parameters = not self.config_data.apply_same_parameters
        if self.config_data.apply_same_parameters:
            self.set_all_parameters_the_same_as_current()

    def set_current_image(self, image: np.ndarray):
        self.image_data.current_image = image

    def get_current_parameters(self):
        return self.current_parameters.get_params_as_dict()

    def get_image_size(self):
        if self.image_data.current_image is not None:
            return self.image_data.current_image.shape[1], self.image_data.current_image.shape[0]
        return None

    def prev_image(self):
        if self.image_data.current_page_index > 0:
            self.image_data.current_page_index -= 1
            self.update_current_image()
            self.update_current_parameters()

    def next_image(self):
        if self.image_data.current_page_index < len(self.image_data.images) - 1:
            self.image_data.current_page_index += 1
            self.update_current_image()
            self.update_current_parameters()

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
        if self.config_data.mode == MaskMode.THRESHOLD:
            mask = self.mask_data.temp_mask_after_threshold
        else:
            mask = self.mask_data.temp_mask
        if len(mask.shape) == 2:
            return cv2.cvtColor(cv2.bitwise_or(mask, self.mask_data.final_mask), cv2.COLOR_GRAY2BGR)
        elif len(mask.shape) == 3 and mask.shape[2] == 3:
            return cv2.bitwise_or(mask, self.mask_data.final_mask)
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
                self.reset_mask()

            # if mask has 3 channels, convert to grayscale
            elif len(loaded_mask.shape) == 3 and loaded_mask.shape[2] == 3:
                loaded_mask = cv2.cvtColor(loaded_mask, cv2.COLOR_BGR2GRAY)

            if loaded_mask.shape != self.image_data.current_image.shape:
                loaded_mask = resize_mask(loaded_mask,
                                          self.image_data.current_image.shape[1],
                                          self.image_data.current_image.shape[0])
                print(f"Resized loaded mask to match image size: {loaded_mask.shape}")
                print(f"Image size: {self.image_data.current_image.shape}")
            self.mask_data.final_mask = loaded_mask
        except:
            print(f"Error loading mask from {path}. Using default mask.")
            # print("Mask size:", self.final_mask.shape)
            self.reset_mask()

    def reset_temp_mask(self):
        self.mask_data.temp_mask = self.mask_data.mask.copy()
        self.mask_data.temp_mask_after_threshold = self.mask_data.mask.copy()

    def reset_mask(self):
        self.mask_data.final_mask = self.mask_data.mask.copy()
        self.reset_temp_mask()
        self.mask_data.undo_stack.clear()
        self.mask_data.redo_stack.clear()
        self.mask_data.points = []

    def set_cursor_size(self, size: int):
        """Set the size of the cursor."""
        self.cursor_data.cursor_size = size

    def set_cursor_pos(self, pos: tuple):
        """Set the position of the cursor."""
        self.cursor_data.cursor_pos = pos

    def get_image_to_show(self):
        if self.config_data.mode == MaskMode.ADJUST:
            return self.get_processed_current_image()
        else:
            return self.get_weighted_image()

    def get_weighted_image(self):
        """Return the current image with the mask applied based on the weight."""
        if self.get_current_image() is None or self.mask_data.final_mask is None:
            raise ValueError("Current image or final mask is not set.")
        # Perform blending using NumPy
        blended_image = (1 - self.config_data.weight) * self.get_current_image().astype(np.float32) + \
                        self.config_data.weight * self.get_bgr_mask().astype(np.float32)
        # Clip values to valid range and convert back to uint8
        blended_image = np.clip(blended_image, 0, 255).astype(np.uint8)
        if self.config_data.mode == MaskMode.DRAW:
            blended_image = self.draw_cursor(blended_image)
        return blended_image

    def draw_cursor(self, image):
        if self.cursor_data.type == CursorType.CIRCLE:
            cv2.circle(image,
                       self.cursor_data.pos,
                       self.cursor_data.size,
                       (0, 0, 0),
                       self.cursor_data.thickness)
        elif self.cursor_data.type == CursorType.SQUARE:
            size = self.cursor_data.size
            top_left = (self.cursor_data.pos[0] - size, self.cursor_data.pos[1] - size)
            bottom_right = (self.cursor_data.pos[0] + size, self.cursor_data.pos[1] + size)
            cv2.rectangle(image,
                          top_left,
                          bottom_right,
                          (0, 0, 0),
                          self.cursor_data.thickness)
        return image


    def toggle_cursor_type(self):
        if self.cursor_data.type == CursorType.CIRCLE:
            self.cursor_data.type = CursorType.SQUARE
        else:
            self.cursor_data.type = CursorType.CIRCLE

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

    def get_temp_mask(self):
        return self.mask_data.temp_mask

    def set_temp_mask(self, value):
        self.mask_data.temp_mask = value

    def get_temp_mask_after_threshold(self):
        return self.mask_data.temp_mask_after_threshold

    def set_temp_mask_after_threshold(self, value):
        self.mask_data.temp_mask_after_threshold = value

    def get_cursor_type(self):
        return self.cursor_data.type

    def get_cursor_size(self):
        return self.cursor_data.size

    def get_cursor_pos(self):
        return self.cursor_data.pos

    def get_final_mask(self):
        return self.mask_data.final_mask

    def set_final_mask(self, value):
        self.mask_data.final_mask = value

    def set_threshold_max(self, value):
        self.config_data.threshold_max = int(value)

    def get_current_image(self):
        if self.image_data.median_trackbar_pos == 1:
            image = self.image_data.images[self.image_data.current_page_index]
        else:
            image = self.image_data.median_image_bgr
        return image

    def get_current_image_gray(self):
        if self.image_data.current_image is not None:
            return cv2.cvtColor(self.image_data.current_image, cv2.COLOR_BGR2GRAY)
        return None

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

    def get_median_trackbar_pos(self):
        return self.image_data.median_trackbar_pos

    def get_total_images(self):
        return len(self.image_data.images)

    def get_experimental_image(self):
        # Get the current image
        img = self.image_data.current_image

        # Convert to grayscale if needed
        if img.ndim == 3:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img
        # Convert to float32
        img_float = np.float32(img_gray)
        # Compute DFT
        dft = cv2.dft(img_float, flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        # Compute magnitude spectrum
        magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
        magnitude_spectrum = np.log(magnitude + 1)
        # Normalize for display
        cv2.normalize(magnitude_spectrum, magnitude_spectrum, 0, 255, cv2.NORM_MINMAX)

        # # filter out the high frequencies
        # rows, cols = img_gray.shape
        # crow, ccol = rows // 2, cols // 2
        # mask = np.zeros((rows, cols, 2), np.uint8)
        # r = 70  # radius of the low-pass filter
        # center = (crow, ccol)
        # x, y = np.ogrid[:rows, :cols]
        # mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r * r
        # mask[mask_area] = 1
        # dft_shift = dft_shift * mask

        # filter out the low frequencies
        rows, cols = img_gray.shape
        crow, ccol = rows // 2, cols // 2
        mask = np.ones((rows, cols, 2), np.uint8)
        r = 30  # radius of the high-pass filter
        center = (crow, ccol)
        x, y = np.ogrid[:rows, :cols]
        mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r * r
        mask[mask_area] = 0
        dft_shift = dft_shift * mask


        # Inverse DFT to reconstruct the image
        dft_ishift = np.fft.ifftshift(dft_shift)
        img_back = cv2.idft(dft_ishift)
        img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
        cv2.normalize(img_back, img_back, 0, 255, cv2.NORM_MINMAX)
        img_back = img_back.astype(np.uint8)
        # subtract the img_back from the original image
        img_back = cv2.subtract(img_gray, img_back)
        print(img_back)
        return img_back


    def set_median_image_number(self, tb_pos: int):
        self.image_data.median_trackbar_pos = tb_pos
        self.update_median_image()

    def update_median_image(self):
        self.image_data.median_image_bgr = calc_median_image(self.image_data.images, self.get_median_trackbar_pos())
        self.image_data.median_image_gray = cv2.cvtColor(self.image_data.median_image_bgr, cv2.COLOR_BGR2GRAY)
        self.update_current_image()

    def update_current_image(self):
         # Reset current_image based on aggregate_image_number
        if self.image_data.median_trackbar_pos == 1:
            self.image_data.current_image = self.image_data.images[self.image_data.current_page_index].copy()
        else:
            self.image_data.current_image = self.image_data.median_image_bgr.copy()

    def update_current_parameters(self):
        self.current_parameters = self.parameters[self.image_data.current_page_index]





