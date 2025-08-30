import cv2
from modules.utils import convert_images, read_pdf


class PDFImageExtractor:
    def __init__(self, pdf_path, dpi=300, max_width=1920, max_height=1080):
        self.original_width = None
        self.original_height = None
        self.images_for_mask_making = None
        self.images_for_watermark_removal = None
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.max_width = max_width
        self.max_height = max_height
        self.images = []
        self.load_pdf(pdf_path)

    def load_pdf(self, pdf_path):
        self.pdf_path = pdf_path
        self.images = read_pdf(pdf_path, self.dpi)
        (self.original_height, self.original_width) = self.images[0].shape[:2]
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

    def resize_images_for_mask_making(self, images):
        return [self.resize_image(image) for image in images]

    def get_original_size(self):
        return self.original_width, self.original_height