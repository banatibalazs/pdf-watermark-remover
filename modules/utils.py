import cv2
import numpy as np
import fitz  # PyMuPDF


def calc_median_image(images, length=40):
    print("image type:", type(images))

    length = min(length, len(images))
    stacked_images = np.stack([np.array(image) for image in images[:length]], axis=-1)
    # if length > 1:
    #     stacked_images_2 = np.stack([np.array(image) for image in images[:(length-1)]], axis=-1)
    #     stacked_images_3 = np.stack([np.array(image) for image in images[:(length-2)]], axis=-1)
    #     median_image_1 = np.median(stacked_images, axis=-1)
    #     median_image_2 = np.median(stacked_images_2, axis=-1)
    #     median_image_3 = np.median(stacked_images_3, axis=-1)
    #     set null the pixels that are different on the two median images
    #     median_image = np.where(median_image_1 == median_image_2, median_image_1, 0)
    #     median_image = np.where(median_image == median_image_3, median_image, 0)
    #     print("Median image calculated with length:", length)
    # else:
    median_image = np.median(stacked_images, axis=-1)
    median_image = np.uint8(median_image)
    return median_image


def convert_images(images):
    return [cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) for image in images]


def sharpen_image(img, w):
    im_blur = cv2.GaussianBlur(img, (3, 3), 2.0)
    im_diff = cv2.subtract(img, im_blur, dtype=cv2.CV_16S)
    img = cv2.add(img, w * im_diff, dtype=cv2.CV_8UC1)
    return img

def get_most_frequent_color(image):
    # Split the image into its channels and get the most frequent color in each channel
    channels = cv2.split(image)
    most_frequent_colors = [np.bincount(channel.flatten()).argmax() for channel in channels]
    return np.array(most_frequent_colors)

def fill_masked_area(image, gray_mask):
    new_color = get_most_frequent_color(image)
    img = image.copy()
    img[gray_mask == 255] = new_color
    return img

def inpaint_image(image, mask):
     return cv2.inpaint(image, mask, 2, cv2.INPAINT_TELEA)
    # return cv2.inpaint(image, mask, 3, cv2.INPAINT_NS)

def add_texts_to_image(image, texts, start_pos, color, background_color=(0, 0, 0)):
    if color == (0, 0, 0):
        background_color = (255, 255, 255)
    elif color == (255, 255, 255):
        background_color = (0, 0, 0)
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 1
    texted_image = image.copy()
    x, y = start_pos
    for text in texts:
        (text_w, text_h), _ = cv2.getTextSize(text, font_face, font_scale, thickness)
        texted_image = cv2.rectangle(texted_image, (x, y + 10), (x + text_w, y - text_h - 5), background_color, -1)
        texted_image = cv2.putText(texted_image, text, (x, y), font_face, font_scale, color, thickness, cv2.LINE_AA)
        y += 30
    return texted_image


class AdjusterParameters:
    def __init__(self, r_min=145, r_max=200, g_min=145, g_max=200, b_min=145, b_max=200, w=0, mode=True):
        self.r_min = r_min
        self.r_max = r_max
        self.g_min = g_min
        self.g_max = g_max
        self.b_min = b_min
        self.b_max = b_max
        self.w = w
        self.mode = mode

    def get_parameters(self):
        return self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode

    def set_parameters(self, args):
        self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode = args

    def get_parameter_names(self):
        return ['r_min', 'r_max', 'g_min', 'g_max', 'b_min', 'b_max', 'w', 'mode']


def draw_progress_bar(image, progress, bar_color=(255, 255, 255), bar_thickness=20):
    height, width = image.shape[:2]
    bar_length = int(width * progress)
    cv2.rectangle(image, (0, height - bar_thickness), (bar_length, height), bar_color, -1)
    return image


def remove_watermark(images, mask, parameters):
    # check if image and mask sizes are the same
    if images[0].shape[:2] != mask.shape[:2]:
        # raise ValueError(f"Image and mask sizes do not match. Image size: {images[0].shape[:2]}, Mask size:{mask.shape[:2]}")
        mask = cv2.resize(mask, (images[0].shape[1], images[0].shape[0]), interpolation=cv2.INTER_AREA)
        print(f"Resized mask to match image size. New mask size: {mask.shape[:]}")

    total_images = len(images)
    progressbar_bg_image = np.zeros((75, 800, 3), np.uint8)
    processed_images = []
    for i, img in enumerate(images):

        # Calculate progress
        progress = (i + 1) / total_images

        # Draw progress bar on the blank image
        image_with_progress = draw_progress_bar(progressbar_bg_image, progress)
        image_with_progress = add_texts_to_image(image_with_progress, [f"Progress: {progress * 100:.2f}%"], (10, 30),
                                                 (255, 255, 255))

        # Show the image with progress bar
        cv2.imshow('Removing watermark...', image_with_progress)
        cv2.waitKey(1)

        lower = np.array([parameters[i].b_min, parameters[i].g_min, parameters[i].r_min], dtype=np.uint8)
        upper = np.array([parameters[i].b_max, parameters[i].g_max, parameters[i].r_max], dtype=np.uint8)

        masked_image_part = cv2.bitwise_and(img, mask)
        gray_mask = cv2.inRange(masked_image_part, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))

        if parameters[i].mode:
            image = fill_masked_area(img, gray_mask)
        else:
            image = inpaint_image(img, gray_mask)
        image = sharpen_image(image, parameters[i].w / 10)

        processed_images.append(image)

    cv2.destroyWindow('Removing watermark...')
    return processed_images


def read_pdf(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes('png')
        img_array = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB, img_array)
        images.append(img_array)
    return images

def resize_images(images, max_width=None, max_height=None):
    img_width, img_height = images[0].shape[:2]
    width_ratio = max_width / float(img_width)
    height_ratio = max_height / float(img_height)
    ratio = min(width_ratio, height_ratio)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    return [cv2.resize(img, (new_height, new_width), interpolation=cv2.INTER_AREA) for img in images]


def load_pdf(pdf_path, dpi=200):
    images = read_pdf(pdf_path, dpi)
    images = convert_images(images)
    return images
