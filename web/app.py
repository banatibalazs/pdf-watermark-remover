from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from pdf2image import convert_from_path
from utils import sharpen_image, convert_images, save_image_to_io, fill_masked_area, resize_image, get_masked_median_image
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import base64

app = Flask(__name__)

IMAGES = []
IMAGES_FOR_MASK_MAKING = []  # Reduced size images to speed up the process
MEDIAN_IMAGE = None
IM_WIDTH, IM_HEIGHT = 0, 0

MASK = None
THRESHOLD_MASK = None
DILATE_ERODE_MASK = None

TH_MIN, TH_MAX = 100, 195
GL_PAGE_NUM = 0
R_MIN, G_MIN, B_MIN = 0, 0, 0
R_MAX, G_MAX, B_MAX = 255, 255, 255
W = 0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global IMAGES, MASK, IM_HEIGHT, IM_WIDTH, MEDIAN_IMAGE, IMAGES_FOR_MASK_MAKING
    file = request.files['file']
    if file:
        file.save('uploaded.pdf')
        # Returns a list of PIL images -> image.size = (width, height)
        IMAGES = convert_from_path('uploaded.pdf')
        # Convert the PIL images to numpy arrays and convert the color space from RGB to BGR
        # -> image.shape = (height, width, 3)
        IMAGES = convert_images(IMAGES)
        IM_HEIGHT, IM_WIDTH = IMAGES[0].shape[:2]
        # Reduce the size of the images to speed up the mask making process
        IMAGES_FOR_MASK_MAKING = [resize_image(image) for image in IMAGES]

        MASK = np.zeros((IMAGES_FOR_MASK_MAKING[0].shape[:2]), np.uint8)
        MASK = cv2.cvtColor(MASK, cv2.COLOR_GRAY2BGR)
        return render_template('mask_selection.html', page_num=0, total_pages=len(IMAGES))
    return 'No file uploaded', 400

@app.route('/page/<int:page_num>')
def page(page_num):
    global IMAGES_FOR_MASK_MAKING, MASK, GL_PAGE_NUM

    GL_PAGE_NUM = page_num
    if page_num < 0 or page_num >= len(IMAGES):
        return 'Page not found', 404

    resized_mask = cv2.resize(MASK, (IMAGES_FOR_MASK_MAKING[page_num].shape[1], IMAGES_FOR_MASK_MAKING[page_num].shape[0]))
    if len(resized_mask.shape) == 2:  # Check if the image is single-channel (grayscale)
        resized_mask = cv2.cvtColor(resized_mask, cv2.COLOR_GRAY2BGR)
    blended_image = cv2.addWeighted(IMAGES_FOR_MASK_MAKING[page_num], 0.7, resized_mask, 0.3, 0)

    img = cv2.cvtColor(blended_image, cv2.COLOR_BGR2RGB)
    img_io = save_image_to_io(img)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/save_polygon', methods=['POST'])
def save_polygon():
    global MASK, GL_PAGE_NUM

    data = request.get_json()
    polygon = data.get('polygon')
    canvas_width = data.get('canvasWidth')
    canvas_height = data.get('canvasHeight')

    MASK = cv2.resize(MASK, (canvas_width, canvas_height))
    cv2.fillPoly(MASK, [np.array(polygon, dtype=np.int32)], (255, 255, 255))

    return jsonify({'status': 'success'})

@app.route('/reset_mask', methods=['POST'])
def reset_mask():
    global MASK, IM_HEIGHT, IM_WIDTH
    MASK.fill(0)
    return jsonify({'status': 'mask reset'})

@app.route('/mask_thresholding')
def thresholding():
    global MEDIAN_IMAGE, MASK, DILATE_ERODE_MASK, THRESHOLD_MASK, IMAGES_FOR_MASK_MAKING

    if len(MASK.shape) == 3:
        MASK = cv2.cvtColor(MASK, cv2.COLOR_BGR2GRAY)

    MASK = cv2.resize(MASK, (IMAGES_FOR_MASK_MAKING[0].shape[1], IMAGES_FOR_MASK_MAKING[0].shape[0]))
    MEDIAN_IMAGE = get_masked_median_image(IMAGES_FOR_MASK_MAKING, MASK)


    return render_template('mask_thresholding.html')


@app.route('/update_thresholds', methods=['POST'])
def update_thresholds():
    global THRESHOLD_MASK, MEDIAN_IMAGE, MASK, DILATE_ERODE_MASK

    data = request.get_json()
    th_min = float(data.get('th_min'))
    th_max = float(data.get('th_max'))

    if MEDIAN_IMAGE is None:
        MEDIAN_IMAGE = get_masked_median_image(IMAGES_FOR_MASK_MAKING, MASK)

    THRESHOLD_MASK = cv2.inRange(MEDIAN_IMAGE, th_min, th_max)
    THRESHOLD_MASK = cv2.bitwise_and(THRESHOLD_MASK, MASK)

    DILATE_ERODE_MASK = THRESHOLD_MASK.copy()

    img_io = save_image_to_io(THRESHOLD_MASK)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/erode_mask', methods=['POST'])
def erode_mask():
    global DILATE_ERODE_MASK

    kernel = np.ones((3, 3), np.uint8)
    DILATE_ERODE_MASK = cv2.erode(DILATE_ERODE_MASK, kernel, iterations=1)

    return jsonify({'status': 'success'})

@app.route('/dilate_mask', methods=['POST'])
def dilate_mask():
    global DILATE_ERODE_MASK

    kernel = np.ones((3, 3), np.uint8)
    DILATE_ERODE_MASK = cv2.dilate(DILATE_ERODE_MASK, kernel, iterations=1)

    return jsonify({'status': 'success'})

@app.route('/get_dilate_erode_mask/')
def get_dilate_erode_mask():
    global DILATE_ERODE_MASK

    img_io = save_image_to_io(DILATE_ERODE_MASK)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/reset_dilate_erode_mask', methods=['POST'])
def reset_dilate_erode_mask():
    global THRESHOLD_MASK, DILATE_ERODE_MASK
    DILATE_ERODE_MASK = THRESHOLD_MASK.copy()
    return jsonify({'status': 'success'})

@app.route('/update_color_filters', methods=['POST'])
def update_color_filters():
    global R_MIN, R_MAX, G_MIN, G_MAX, B_MIN, B_MAX, W, DILATE_ERODE_MASK, GL_PAGE_NUM, IMAGES_FOR_MASK_MAKING

    data = request.get_json()
    R_MIN, R_MAX = int(data.get('r_min')), int(data.get('r_max'))
    G_MIN, G_MAX = int(data.get('g_min')), int(data.get('g_max'))
    B_MIN, B_MAX = int(data.get('b_min')), int(data.get('b_max'))
    W = int(data.get('sharpen'))
    mode = int(data.get('mode'))

    # BGR Image
    current_image = IMAGES_FOR_MASK_MAKING[GL_PAGE_NUM]
    lower = np.array([B_MIN, G_MIN, R_MIN])
    upper = np.array([B_MAX, G_MAX, R_MAX])

    _mask = cv2.resize(DILATE_ERODE_MASK, (current_image.shape[1], current_image.shape[0]))
    _mask = cv2.cvtColor(_mask, cv2.COLOR_GRAY2BGR)

    masked_image = cv2.bitwise_and(current_image, _mask)
    gray_mask = cv2.inRange(masked_image, lower, upper)
    gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(_mask, cv2.COLOR_BGR2GRAY))

    if mode == 0:
        im_to_show = fill_masked_area(current_image, gray_mask)
    else:
        im_to_show = cv2.inpaint(current_image, gray_mask, 2, cv2.INPAINT_TELEA)

    im_to_show = sharpen_image(im_to_show, W)
    im_to_show = cv2.cvtColor(im_to_show, cv2.COLOR_BGR2RGB)
    img_io = save_image_to_io(im_to_show)

    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True)