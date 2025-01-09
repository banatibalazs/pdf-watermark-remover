import cv2
import numpy as np


def convert_images(images):
    converted_images = [np.array(image) for image in images]
    converted_images = [cv2.cvtColor(image, cv2.COLOR_RGB2BGR) for image in converted_images]
    return converted_images

def filter_color(img, lower, upper):
    color_mask = cv2.inRange(img, lower, upper)
    color_mask_bgr = cv2.cvtColor(color_mask, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_or(img, color_mask_bgr)
    return img

def sharpen_image(img, w):
    im_blur = cv2.GaussianBlur(img, (3, 3), 2.0)
    im_diff = cv2.subtract(img, im_blur, dtype=cv2.CV_16S)
    img = cv2.add(img, w * im_diff, dtype=cv2.CV_8UC1)
    return img

def get_most_frequent_color(image):
    b, g, r = cv2.split(image)
    b_most_frequent = np.bincount(b.flatten()).argmax()
    g_most_frequent = np.bincount(g.flatten()).argmax()
    r_most_frequent = np.bincount(r.flatten()).argmax()
    return np.array([b_most_frequent, g_most_frequent, r_most_frequent])

def fill_masked_area(image, mask):
    bool_mask = mask[:, :, 0] == 255
    new_color = get_most_frequent_color(image)
    img = image.copy()
    img[bool_mask] = new_color
    return img

def add_texts_to_image(image, texts, start_pos, color, background_color=(0, 0, 0)):
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 1
    texted_image = image.copy()
    x, y = start_pos
    for text in texts:
        (text_w, text_h), _ = cv2.getTextSize(text, font_face, font_scale, thickness)
        texted_image = cv2.rectangle(texted_image, (x, y + 10), (x + text_w, y - text_h - 5), background_color, -1)
        texted_image = cv2.putText(texted_image, text, (x, y), font_face, font_scale, color, thickness, cv2.LINE_AA)
        y += 30
    return texted_image