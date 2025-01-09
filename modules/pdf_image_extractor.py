import cv2
import numpy as np
from pdf2image import convert_from_path
from modules.utils import convert_images


class PDFImageExtractor:
    def __init__(self, pdf_path, dpi=300, max_width=1920, max_height=1080):
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.max_width = max_width
        self.max_height = max_height
        self.images = convert_from_path(self.pdf_path, dpi=self.dpi)
        self.original_width, self.original_height = self.images[0].size[:2]
        self.images_for_watermark_removal = convert_images(self.images)
        self.images_for_mask_making = [self.resize_image(image) for image in self.images_for_watermark_removal]

    def resize_image(self, img):
        width_ratio = self.max_width / float(self.original_width)
        height_ratio = self.max_height / float(self.original_height)
        ratio = min(width_ratio, height_ratio)
        new_width = int(self.original_width * ratio)
        new_height = int(self.original_height * ratio)
        return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def get_images_for_mask_making(self):
        return self.images_for_mask_making

    def get_images_for_watermark_removal(self):
        return self.images_for_watermark_removal

    def get_original_size(self):
        return self.original_width, self.original_height