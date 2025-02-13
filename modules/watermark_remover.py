import cv2
import numpy as np
import img2pdf
from modules.utils import sharpen_image, fill_masked_area, add_texts_to_image, inpaint_image


def draw_progress_bar(image, progress, bar_color=(255, 255, 255), bar_thickness=20):
    height, width = image.shape[:2]
    bar_length = int(width * progress)
    cv2.rectangle(image, (0, height - bar_thickness), (bar_length, height), bar_color, -1)
    return image


class WatermarkRemover:
    def __init__(self, images, bgr_mask, parameters):
        self.images = images
        self.mask = cv2.resize(bgr_mask, (images[0].shape[1], images[0].shape[0]), interpolation=cv2.INTER_AREA)
        self.parameters = parameters
        self.processed_images = []

    def remove_watermark(self):

        total_images = len(self.images)
        progressbar_bg_image = np.zeros((75, 800, 3), np.uint8)
        for i, img in enumerate(self.images):

            # Calculate progress
            progress = (i + 1) / total_images

            # Draw progress bar on the blank image
            image_with_progress = draw_progress_bar(progressbar_bg_image, progress)
            image_with_progress = add_texts_to_image(image_with_progress, [f"Progress: {progress * 100:.2f}%"], (10, 30), (255, 255, 255))

            # Show the image with progress bar
            cv2.imshow('Removing watermark...', image_with_progress)
            cv2.waitKey(1)

            lower = np.array([self.parameters[i].b_min, self.parameters[i].g_min, self.parameters[i].r_min])
            upper = np.array([self.parameters[i].b_max, self.parameters[i].g_max, self.parameters[i].r_max])

            masked_image_part = cv2.bitwise_and(img, self.mask)
            gray_mask = cv2.inRange(masked_image_part, lower, upper)
            gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY))

            if self.parameters[i].mode:
                image = fill_masked_area(img, gray_mask)
            else:
                image = inpaint_image(img, gray_mask)
            image = sharpen_image(image, self.parameters[i].w / 10)

            # Convert the image to bytes and append it to the list
            is_success, im_buf_arr = cv2.imencode(".jpg", image)
            byte_im = im_buf_arr.tobytes()
            self.processed_images.append(byte_im)

    def save_pdf(self, save_path):
        try:
            with open(save_path, "wb") as f:
                f.write(img2pdf.convert(self.processed_images))
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again with a different path.")
            return
