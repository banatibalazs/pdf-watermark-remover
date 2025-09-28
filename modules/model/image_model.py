import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import calc_median_image, resize_images, load_pdf


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

    def get_number_of_pages(self) -> int:
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