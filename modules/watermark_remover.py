import cv2
import numpy as np
from tqdm import tqdm
import img2pdf
from modules.utils import filter_color, sharpen_image, fill_masked_area


def draw_progress_bar(image, progress, bar_color=(0, 255, 0), bar_thickness=20):
    height, width = image.shape[:2]
    bar_length = int(width * progress)
    cv2.rectangle(image, (0, height - bar_thickness), (bar_length, height), bar_color, -1)
    return image


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
        total_images = len(self.images)
        blank_image = np.zeros((25, 800, 3), np.uint8)
        for img in tqdm(self.images, desc="Removing watermark..."):
            index += 1

            # Calculate progress
            progress = (index + 1) / total_images

            # Draw progress bar on the blank image
            image_with_progress = draw_progress_bar(blank_image, progress)

            # Show the image with progress bar
            cv2.imshow('Removing watermark...', image_with_progress)
            cv2.waitKey(1)

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