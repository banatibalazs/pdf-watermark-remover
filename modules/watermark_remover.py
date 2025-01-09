import cv2
import numpy as np
from tqdm import tqdm
import img2pdf
from modules.utils import filter_color, sharpen_image, fill_masked_area



class WatermarkRemover:
    def __init__(self, images, bgr_mask, parameters):
        self.images = images
        self.mask = cv2.resize(bgr_mask, (images[0].shape[1], images[0].shape[0]), interpolation=cv2.INTER_AREA)
        self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w = parameters
        self.processed_images = []

    def remove_watermark(self):
        lower = np.array([self.b_min, self.g_min, self.r_min])
        upper = np.array([self.b_max, self.g_max, self.r_max])

        index = 0
        for img in tqdm(self.images, desc="Removing watermark..."):
            index += 1

            masked_image_part = cv2.bitwise_and(img, self.mask)
            shape = filter_color(masked_image_part, lower, upper)
            image = fill_masked_area(img, shape)
            image = sharpen_image(image, self.w)

            # Convert the image to bytes and append it to the list
            is_success, im_buf_arr = cv2.imencode(".jpg", image)
            byte_im = im_buf_arr.tobytes()
            self.processed_images.append(byte_im)

    def save_pdf(self, save_path):
        with open(save_path, "wb") as f:
            f.write(img2pdf.convert(self.processed_images))