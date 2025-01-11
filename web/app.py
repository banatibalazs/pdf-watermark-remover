from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from pdf2image import convert_from_path
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import base64

app = Flask(__name__)
images = []
median_image = None
im_width, im_height = 0, 0
mask = None
threshold_mask = None
dilate_erode_mask = None
th_min, th_max = 100, 195
gl_page_num = 0
r_min = 0
r_max = 255
g_min = 0
g_max = 255
b_min = 0
b_max = 255
w = 0


def convert_images(images):
    converted_images = [np.array(image) for image in images]
    converted_images = [cv2.cvtColor(image, cv2.COLOR_RGB2BGR) for image in converted_images]
    return converted_images


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    global images, mask, im_height, im_width, median_image
    file = request.files['file']
    if file:
        file.save('uploaded.pdf')
        images = convert_from_path('uploaded.pdf')

        images = convert_images(images)
        im_width, im_height = images[0].shape[:2]
        mask = np.zeros((im_height, im_width), np.uint8)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        length = min(40, len(images))
        # Convert the images to numpy arrays and stack them along a new dimension
        stacked_images = np.stack([np.array(image) for image in images[:length]], axis=-1)
        # Get the median along the new dimension
        median_image = np.median(stacked_images, axis=-1)
        # The median image is float, convert it back to uint8
        median_image = np.uint8(median_image)
        median_image = cv2.cvtColor(median_image, cv2.COLOR_BGR2GRAY)

        return render_template('mask_selection.html', page_num=0, total_pages=len(images))
    return 'No file uploaded', 400


@app.route('/page/<int:page_num>')
def page(page_num):
    global images, mask, gl_page_num

    gl_page_num = page_num
    if page_num < 0 or page_num >= len(images):
        return 'Page not found', 404

    # Resize the mask to match the image dimensions
    resized_mask = cv2.resize(mask, (images[page_num].shape[1], images[page_num].shape[0]))

    # Blend the image with the resized mask
    blended_image = cv2.addWeighted(images[page_num], 0.7, resized_mask, 0.3, 0)
    img = cv2.cvtColor(blended_image, cv2.COLOR_BGR2RGB)

    img_io = BytesIO()
    pil_img = Image.fromarray(img)
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/save_polygon', methods=['POST'])
def save_polygon():
    global mask, gl_page_num
    data = request.get_json()
    polygon = data.get('polygon')
    canvas_width = data.get('canvasWidth')
    canvas_height = data.get('canvasHeight')

    # Convert the polygon to a numpy array
    polygon_np = np.array(polygon, dtype=np.int32)

    mask = cv2.resize(mask, (canvas_width, canvas_height))
    cv2.fillPoly(mask, [polygon_np], (255, 255, 255))

    return jsonify({'status': 'success'})


@app.route('/reset_mask', methods=['POST'])
def reset_mask():
    global mask, im_height, im_width
    mask = np.zeros((im_height, im_width), np.uint8)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    return jsonify({'status': 'mask reset'})


@app.route('/mask_thresholding')
def thresholding():
    return render_template('mask_thresholding.html')


@app.route('/get_threshold_mask/')
def get_threshold_mask():
    global threshold_mask, th_min, th_max

    median_image_mask_gray, mask_gray = calc_median_image()

    _, threshold_mask_min = cv2.threshold(median_image_mask_gray, th_min, 255, cv2.THRESH_BINARY)
    _, threshold_mask_max = cv2.threshold(median_image_mask_gray, th_max, 255, cv2.THRESH_BINARY_INV)

    threshold_mask = cv2.bitwise_and(threshold_mask_min, threshold_mask_max)
    threshold_mask = cv2.bitwise_and(threshold_mask, mask_gray)

    img_io = BytesIO()
    pil_img = Image.fromarray(threshold_mask)
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/update_thresholds', methods=['POST'])
def update_thresholds():
    global threshold_mask, th_min, th_max

    data = request.get_json()
    th_min_p = float(data.get('th_min'))
    th_max_p = float(data.get('th_max'))

    th_min, th_max = th_min_p, th_max_p

    return jsonify({'status': 'mask reset'})


def calc_median_image(length=40):
    global images, mask, median_image

    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask_gray = cv2.resize(mask_gray, (median_image.shape[1], median_image.shape[0]))

    median_image_gray = cv2.bitwise_and(median_image, mask_gray)
    return median_image_gray, mask_gray


@app.route('/erode_mask', methods=['POST'])
def erode_mask():
    global threshold_mask, dilate_erode_mask

    if dilate_erode_mask is None:
        dilate_erode_mask = threshold_mask.copy()

    kernel = np.ones((3, 3), np.uint8)
    dilate_erode_mask = cv2.erode(dilate_erode_mask, kernel, iterations=1)

    return jsonify({'status': 'success'})


@app.route('/dilate_mask', methods=['POST'])
def dilate_mask():
    global threshold_mask, dilate_erode_mask

    if dilate_erode_mask is None:
        dilate_erode_mask = threshold_mask.copy()

    kernel = np.ones((3, 3), np.uint8)
    dilate_erode_mask = cv2.dilate(dilate_erode_mask, kernel, iterations=1)

    return jsonify({'status': 'success'})


@app.route('/get_dilate_erode_mask/')
def get_dilate_erode_mask():
    global dilate_erode_mask

    img_io = BytesIO()
    pil_img = Image.fromarray(dilate_erode_mask)
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/mask_reset', methods=['POST'])
def mask_reset():
    global threshold_mask, dilate_erode_mask

    dilate_erode_mask = threshold_mask.copy()

    return jsonify({'status': 'success'})


def get_most_frequent_color(image):
    b, g, r = cv2.split(image)
    b_most_frequent = np.bincount(b.flatten()).argmax()
    g_most_frequent = np.bincount(g.flatten()).argmax()
    r_most_frequent = np.bincount(r.flatten()).argmax()
    return np.array([b_most_frequent, g_most_frequent, r_most_frequent])


@app.route('/update_color_filters', methods=['POST'])
def update_color_filters():
    global r_min, r_max, g_min, g_max, b_min, b_max, w, mask, gl_page_num, images

    data = request.get_json()
    r_min = int(data.get('r_min'))
    r_max = int(data.get('r_max'))
    g_min = int(data.get('g_min'))
    g_max = int(data.get('g_max'))
    b_min = int(data.get('b_min'))
    b_max = int(data.get('b_max'))
    w = int(data.get('sharpen'))

    current_image = images[gl_page_num]
    _mask = cv2.resize(mask, (current_image.shape[1], current_image.shape[0]))

    lower = np.array([b_min, g_min, r_min])
    upper = np.array([b_max, g_max, r_max])
    _mask = cv2.bitwise_and(current_image, _mask)
    _mask = cv2.inRange(_mask, lower, upper)
    if True:
        new_color = get_most_frequent_color(current_image)
        img = current_image.copy()
        img[_mask == 255] = new_color
        im_to_show = img
    else:
        im_to_show = cv2.inpaint(current_image, _mask, 2, cv2.INPAINT_TELEA)

    # im_to_show = sharpen_image(im_to_show, self.w)

    # Convert the image to base64
    pil_img = Image.fromarray(cv2.cvtColor(im_to_show, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    pil_img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return jsonify({'status': 'success', 'image': img_str})


if __name__ == '__main__':
    app.run(debug=True)