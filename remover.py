from pdf2image import convert_from_path
import img2pdf
import numpy as np
import cv2
from tqdm import tqdm
import argparse
from scipy import stats

# Global variables
PDF_PATH = 'input.pdf'
SAVE_PATH = 'output.pdf'

# Set the maximum width and height for the images during the masking process
# The final PDF will have the same dimensions as the original PDF
MAX_WIDTH = 1920
MAX_HEIGHT = 1080

# Set the DPI for the images, this affects the quality of the final PDF
DPI = 100


def add_text_to_image(img, text, org, color=(255, 0, 0), thickness=2, fontScale=0.8):
    overlay = img.copy()
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    # Use cv2.putText() method to draw the text on the overlay
    overlay = cv2.putText(overlay, text, org, fontFace, fontScale, color, thickness, cv2.LINE_AA)
    # Define the transparency factor (alpha)
    alpha = 0.4
    # Blend the original image with the overlay
    texted_image = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    return texted_image


def add_texts_to_image(image, texts, start_pos, color):
    pos = list(start_pos)
    for text in texts:
        image = add_text_to_image(image, text, tuple(pos), color)
        pos[1] += 30  # Move position for next text
    return image


def sharpen_image(img, w):
    im_blur = cv2.GaussianBlur(img, (3, 3), 2.0)
    im_diff = cv2.subtract(img, im_blur, dtype=cv2.CV_16S)
    img = cv2.add(img, w * im_diff, dtype=cv2.CV_8UC1)
    return img


def get_most_frequent_color(image):
    # Split the image into B, G, R channels
    b, g, r = cv2.split(image)

    # Find the most frequent value in each channel
    b_most_frequent = np.bincount(b.flatten()).argmax()
    g_most_frequent = np.bincount(g.flatten()).argmax()
    r_most_frequent = np.bincount(r.flatten()).argmax()

    return np.array([b_most_frequent, g_most_frequent, r_most_frequent])


def fill_masked_area(image, mask):
    # Create a boolean mask where the mask is 255
    bool_mask = mask[:, :, 0] == 255
    # Create a color array for the new color
    new_color = get_most_frequent_color(image)
    # Use the boolean mask to assign the new color to the masked area in the image
    img = image.copy()
    img[bool_mask] = new_color

    return img


def average_adjacent_pixels(image):
    # Create a 3x3 kernel with all elements equal to 1/9
    kernel = np.ones((3, 3), np.float32) / 9
    # Use the filter2D function to convolve the kernel with the image
    averaged_image = cv2.filter2D(image, -1, kernel)
    return averaged_image


def filter_color(img, lower, upper):

    # Create a color mask
    color_mask = cv2.inRange(img, lower, upper)
    # Convert the color mask to BGR (3 channels)
    color_mask_bgr = cv2.cvtColor(color_mask, cv2.COLOR_GRAY2BGR)
    # Apply the color mask to the shape
    img = cv2.bitwise_or(img, color_mask_bgr)

    return img


def convert_images(images):
    converted_images = [np.array(image) for image in images]
    converted_images = [cv2.cvtColor(image, cv2.COLOR_RGB2BGR) for image in converted_images]
    return converted_images


class PDFProcessor:
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
        # Calculate the ratios of the new width and height to the old width and height
        width_ratio = self.max_width / float(self.original_width)
        height_ratio = self.max_height / float(self.original_height)
        # Choose the smallest ratio
        ratio = min(width_ratio, height_ratio)
        # Calculate the new dimensions
        new_width = int(self.original_width * ratio)
        new_height = int(self.original_height * ratio)
        # Resize the image
        return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def get_images_for_mask_making(self):
        return self.images_for_mask_making

    def get_images_for_watermark_removal(self):
        return self.images_for_watermark_removal

    def get_original_size(self):
        return self.original_width, self.original_height


class MaskDrawer:
    def __init__(self, images):
        self.images = images
        self.width, self.height = images[0].shape[:2]
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        mask = np.zeros((self.width, self.height), np.uint8)
        self.mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        self.current_image = None
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.points = []
        self.texts = ["Draw a circle around the object you want to remove.",
                      "Press 'A' to go to the previous page.",
                      "Press 'D' to go to the next page.",
                      "Press 'R' to reset the mask.",
                      "Press 'C' to remove this text.",
                      "Press 'space' to finish."]
        self.text_color = (255, 0, 0)
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def draw_free(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
            self.points.append((x, y))
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.line(self.current_image, (self.ix, self.iy), (x, y), (0, 0, 0), 2)
                self.ix, self.iy = x, y
                self.points.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.current_image, (self.ix, self.iy), (x, y), (0, 0, 0), 2)
            self.points.append((x, y))
            cv2.fillPoly(self.mask, [np.array(self.points)], (255, 255, 255))
            self.points.clear()

    def draw_mask(self):
        cv2.namedWindow('mask')
        cv2.setMouseCallback('mask', self.draw_free)

        self.current_image = add_texts_to_image(self.images[self.current_page_index], self.texts, self.text_pos, self.text_color)

        while True:
            # Listen for keypress events
            key = cv2.waitKey(1) & 0xFF

            # If 'a' is pressed, go to the previous page
            if key == ord('a'):
                self.current_page_index = max(0, self.current_page_index - 1)

            # If 'd' is pressed, go to the next page
            elif key == ord('d'):
                self.current_page_index = min(len(self.images) - 1, self.current_page_index + 1)

            # If 'r' is pressed, reset the mask and current_image
            elif key == ord('r'):
                self.mask = cv2.cvtColor(np.zeros((self.width, self.height), np.uint8), cv2.COLOR_GRAY2BGR)

            # if 'c' is pressed, remove the texts
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown

            elif key == 32:  # If 'space' is pressed, break the loop
                break

            if key in [ord('a'), ord('d'), ord('r'), ord('c')]:
                if self.is_text_shown:
                    self.current_image = add_texts_to_image(self.images[self.current_page_index], self.texts, self.text_pos,
                                                            self.text_color)
                else:
                    self.current_image = self.images[self.current_page_index].copy()

            cv2.imshow('mask', cv2.addWeighted(self.current_image, 0.7, self.mask, 0.3, 0))

        cv2.destroyAllWindows()

    def get_gray_mask(self):
        return cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)


class MaskProcessor:
    def __init__(self, bgr_images, gray_mask):
        self.images = bgr_images
        self.mask = gray_mask
        self.final_mask = None
        self.median_image = self.calc_median_image()
        self.threshold = 175
        self.thresholded_mask = None
        self.texts = ["Press 'D' to dilate the mask.",
                      "Press 'E' to erode the mask.",
                      "Press 'R' to reset the mask.",
                      "Press 'C' to remove this text.",
                      "Press 'space' to finish."]
        self.text_color = (255, 255, 255)
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def calc_median_image(self, length=40):
        length = min(length, len(self.images))
        # Convert the images to numpy arrays and stack them along a new dimension
        stacked_images = np.stack([np.array(image) for image in self.images[:length]], axis=-1)
        # Get the median along the new dimension
        median_image = np.median(stacked_images, axis=-1)
        # The median image is float, convert it back to uint8
        median_image = np.uint8(median_image)
        median_image_gray = cv2.cvtColor(median_image, cv2.COLOR_BGR2GRAY)
        median_image_gray = cv2.bitwise_and(median_image_gray, self.mask)
        return median_image_gray

    def threshold_mask(self):
        cv2.imshow('mask', self.median_image)
        cv2.createTrackbar('threshold', 'mask', self.threshold, 255, self.on_threshold_trackbar)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def on_threshold_trackbar(self, pos):
        self.threshold = pos
        self.update_median()

    def update_median(self):
        _, self.thresholded_mask = cv2.threshold(self.median_image, self.threshold, 255, cv2.THRESH_BINARY)
        self.thresholded_mask = cv2.bitwise_not(self.thresholded_mask)
        self.thresholded_mask = cv2.bitwise_and(self.thresholded_mask, self.mask)
        cv2.imshow('mask', self.thresholded_mask)

    def erode_dilate_mask(self):

        self.final_mask = self.thresholded_mask.copy()
        # In the main part of your code

        kernel = np.ones((3, 3), np.uint8)
        texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
        cv2.imshow('mask', texted_mask)
        while True:
            # Listen for keypress events
            key = cv2.waitKey(1) & 0xFF

            # If 'd' is pressed, dilate the mask
            if key == ord('d'):
                self.final_mask = cv2.dilate(self.final_mask, kernel, iterations=1)

            # If 'e' is pressed, erode the mask
            elif key == ord('e'):
                self.final_mask = cv2.erode(self.final_mask, kernel, iterations=1)

            elif key == ord('r'):
                self.final_mask = self.thresholded_mask.copy()

            if self.is_text_shown:
                texted_mask = add_texts_to_image(self.final_mask, self.texts, self.text_pos, self.text_color)
                cv2.imshow('mask', texted_mask)
            else:
                cv2.imshow('mask', self.final_mask)

            if key == ord('c'):
                self.is_text_shown = not self.is_text_shown

            # If 'space' is pressed, break the loop
            if key == 32:
                break

        cv2.destroyAllWindows()

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)

    def show_mask(self):
        cv2.imshow('mask', self.final_mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class ColorFilter:
    def __init__(self, images, mask):
        self.images = images
        self.mask = mask
        self.r_min = self.g_min = self.b_min = 145
        self.r_max = self.g_max = self.b_max = 200
        self.w = 0
        self.current_index = 0
        self.texts = ["Set the color range with trackbars.",
                      "Press 'A' to go to the previous page.",
                      "Press 'D' to go to the next page.",
                      "Press 'C' to remove this text.",
                      "Press 'space' to finish."]
        self.text_color = (255, 0, 0)
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def on_r_min_changed(self, val):
        self.r_min = val
        self.update_image()

    def on_r_max_changed(self, val):
        self.r_max = val
        self.update_image()

    def on_g_min_changed(self, val):
        self.g_min = val
        self.update_image()

    def on_g_max_changed(self, val):
        self.g_max = val
        self.update_image()

    def on_b_min_changed(self, val):
        self.b_min = val
        self.update_image()

    def on_b_max_changed(self, val):
        self.b_max = val
        self.update_image()

    def on_w_changed(self, pos):
        self.w = pos / 10
        self.update_image()

    def update_image(self):
        # Update the color filter range
        lower = np.array([self.b_min, self.g_min, self.r_min])
        upper = np.array([self.b_max, self.g_max, self.r_max])
        # Crop the shape from the image
        mask = cv2.bitwise_and(self.images[self.current_index], self.mask)
        # Sharpen the cropped shape
        # mask = sharpen_image(mask, self.w)
        # Apply the color filter
        mask = filter_color(mask, lower, upper)

        # im_to_show = cv2.bitwise_or(self.images[self.current_index], mask)
        im_to_show = fill_masked_area(self.images[self.current_index], mask)
        im_to_show = sharpen_image(im_to_show, self.w)

        if self.is_text_shown:
            im_to_show = add_texts_to_image(im_to_show, self.texts, self.text_pos, self.text_color)

        cv2.imshow('image', im_to_show)



    def adjust_color_filter(self):

        cv2.imshow('image', add_texts_to_image(self.images[self.current_index], self.texts, self.text_pos, self.text_color))
        cv2.createTrackbar('R min', 'image', self.r_min, 255, self.on_r_min_changed)
        cv2.createTrackbar('R max', 'image', self.r_max, 255, self.on_r_max_changed)
        cv2.createTrackbar('G min', 'image', self.g_min, 255, self.on_g_min_changed)
        cv2.createTrackbar('G max', 'image', self.g_max, 255, self.on_g_max_changed)
        cv2.createTrackbar('B min', 'image', self.b_min, 255, self.on_b_min_changed)
        cv2.createTrackbar('B max', 'image', self.b_max, 255, self.on_b_max_changed)
        cv2.createTrackbar('Sharpen', 'image', 0, 100, self.on_w_changed)

        while True:
            # Listen for keypress events
            key = cv2.waitKey(1) & 0xFF

            # If 'a' is pressed, go to the previous page
            if key == ord('a'):
                self.current_index = max(0, self.current_index - 1)
                self.update_image()

            # If 'd' is pressed, go to the next page
            elif key == ord('d'):
                self.current_index = min(len(self.images) - 1, self.current_index + 1)
                self.update_image()

            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.update_image()

            # If 'space' is pressed, break the loop
            if key == 32:
                break

        cv2.destroyAllWindows()

    def get_parameters(self):
        return (self.r_min, self.r_max,
                self.g_min, self.g_max,
                self.b_min, self.b_max,
                self.w)


class Remover:
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

    def save_pdf(self, save_path=SAVE_PATH):
        with open(save_path, "wb") as f:
            f.write(img2pdf.convert(self.processed_images))


def parse_args():
    parser = argparse.ArgumentParser(description='Remove watermark from PDF.')
    parser.add_argument('pdf_path', type=str, nargs='?', default=PDF_PATH, help='Path to the input PDF file.')
    parser.add_argument('save_path', type=str, nargs='?', default=SAVE_PATH, help='Path to save the output PDF file.')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for the images. Default is 300.')
    parser.add_argument('--max_width', type=int, default=1920, help='Maximum width for the images. Default is 1920.')
    parser.add_argument('--max_height', type=int, default=1080, help='Maximum height for the images. Default is 1080.')
    return parser.parse_args()


def main():
    args = parse_args()

    pdf_processor = PDFProcessor(args.pdf_path, args.dpi, args.max_width, args.max_height)
    images_for_mask_making = pdf_processor.get_images_for_mask_making()
    images_for_watermark_removal = pdf_processor.get_images_for_watermark_removal()

    drawer = MaskDrawer(images_for_mask_making)
    drawer.draw_mask()
    drawn_mask = drawer.get_gray_mask()

    processor = MaskProcessor(images_for_mask_making, drawn_mask)
    processor.threshold_mask()
    processor.erode_dilate_mask()
    mask = processor.get_bgr_mask()

    color_filter = ColorFilter(images_for_mask_making, mask)
    color_filter.adjust_color_filter()
    parameters = color_filter.get_parameters()

    remover = Remover(images_for_watermark_removal, mask, parameters)
    remover.remove_watermark()
    remover.save_pdf(args.save_path)

if __name__ == "__main__":
    main()





