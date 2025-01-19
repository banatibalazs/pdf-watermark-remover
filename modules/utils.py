import cv2
import numpy as np


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