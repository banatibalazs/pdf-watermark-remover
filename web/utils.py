import cv2
import img2pdf
import numpy as np
from io import BytesIO
from PIL import Image
from flask import send_file


def sharpen_image(img, _w):
    im_blur = cv2.GaussianBlur(img, (3, 3), 2.0)
    im_diff = cv2.subtract(img, im_blur, dtype=cv2.CV_16S)
    img = cv2.add(img, _w * im_diff, dtype=cv2.CV_8UC1)
    return img

def convert_images(images):
    converted_images = [np.array(image) for image in images]
    converted_images = [cv2.cvtColor(image, cv2.COLOR_RGB2BGR) for image in converted_images]
    return converted_images

def save_image_to_io(image):
    img_io = BytesIO()
    pil_img = Image.fromarray(image)
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def get_most_frequent_color(image):
    b, g, r = cv2.split(image)
    b_most_frequent = np.bincount(b.flatten()).argmax()
    g_most_frequent = np.bincount(g.flatten()).argmax()
    r_most_frequent = np.bincount(r.flatten()).argmax()
    return np.array([b_most_frequent, g_most_frequent, r_most_frequent])

def fill_masked_area(image, gray_mask):
    new_color = get_most_frequent_color(image)
    img = image.copy()
    img[gray_mask == 255] = new_color
    return img

def resize_image(img, max_width=600, max_height=800):
    original_height, original_width = img.shape[:2]
    width_ratio = max_width / float(original_width)
    height_ratio = max_height / float(original_height)
    ratio = min(width_ratio, height_ratio)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

def get_masked_median_image(images, mask, length=40):
    length = min(length, len(images))
    # Convert the images to numpy arrays and stack them along a new dimension
    stacked_images = np.stack([np.array(image) for image in images[:length]], axis=-1)
    # Get the median along the new dimension
    median_image = np.median(stacked_images, axis=-1)
    # The median image is float, convert it back to uint8
    median_image = np.uint8(median_image)
    median_image_gray = cv2.cvtColor(median_image, cv2.COLOR_BGR2GRAY)
    print('mask shape:', mask.shape, 'median image shape:', median_image_gray.shape)
    median_image_gray = cv2.bitwise_and(median_image_gray, mask)
    return median_image_gray

def save_image_response(image):
    img_io = save_image_to_io(image)
    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def remove_watermark(img, lower, upper, mask, mode, w):
    masked_image_part = cv2.bitwise_and(img, mask)
    gray_mask = cv2.inRange(masked_image_part, lower, upper)
    gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))

    if mode == 0:
        image = fill_masked_area(img, gray_mask)
    else:
        image = cv2.inpaint(img, gray_mask, 2, cv2.INPAINT_TELEA)
    image = sharpen_image(image, w)

    return image

def save_pdf(images, save_path):
    try:
        with open(save_path, "wb") as f:
            f.write(img2pdf.convert(images))
    except Exception as e:
        print(f"Error: {e}")
        print("Please try again with a different path.")
        return
