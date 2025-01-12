import cv2
import numpy as np
from modules.utils import filter_color, sharpen_image, add_texts_to_image, fill_masked_area, inpaint_image


TEXTS = ["Set the color range with trackbars.",
        "Press 'A' to go to the previous page.",
        "Press 'D' to go to the next page.",
        "Press 'C' to hide/show this text.",
        "Press 'M' to change the mode.",
        "(Most common color vs Inpainting)",
        "Press 'space' to finish."]
TEXT_COLOR = (255, 255, 255)

class ColorAdjuster:
    def __init__(self, images, mask):
        self.images = images
        self.mask = mask
        self.r_min = self.g_min = self.b_min = 145
        self.r_max = self.g_max = self.b_max = 200
        self.w = 0
        self.mode = True
        self.current_index = 0
        self.texts = TEXTS
        self.text_color = TEXT_COLOR
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
        current_image = self.images[self.current_index]
        lower = np.array([self.b_min, self.g_min, self.r_min])
        upper = np.array([self.b_max, self.g_max, self.r_max])
        mask = cv2.bitwise_and(current_image, self.mask)
        gray_mask = filter_color(mask, lower, upper)
        # This next line fixes a bug: If all the min color ranges was set to 0,
        # then the unmasked area (represented by 0 values) would also get selected by the cv2.inRange function.
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY))
        if self.mode:
            im_to_show = fill_masked_area(current_image, gray_mask)
        else:
            im_to_show = inpaint_image(current_image, gray_mask)
        im_to_show = sharpen_image(im_to_show, self.w)
        if self.is_text_shown:
            im_to_show = add_texts_to_image(im_to_show, self.texts, self.text_pos, self.text_color)
        cv2.imshow('watermark remover', im_to_show)

    def adjust_color_filter(self):
        cv2.imshow('watermark remover', add_texts_to_image(self.images[self.current_index], self.texts, self.text_pos, self.text_color))
        cv2.createTrackbar('R min', 'watermark remover', self.r_min, 255, self.on_r_min_changed)
        cv2.createTrackbar('R max', 'watermark remover', self.r_max, 255, self.on_r_max_changed)
        cv2.createTrackbar('G min', 'watermark remover', self.g_min, 255, self.on_g_min_changed)
        cv2.createTrackbar('G max', 'watermark remover', self.g_max, 255, self.on_g_max_changed)
        cv2.createTrackbar('B min', 'watermark remover', self.b_min, 255, self.on_b_min_changed)
        cv2.createTrackbar('B max', 'watermark remover', self.b_max, 255, self.on_b_max_changed)
        cv2.createTrackbar('Sharpen', 'watermark remover', 0, 100, self.on_w_changed)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('a'):
                self.current_index = max(0, self.current_index - 1)
                self.update_image()
            elif key == ord('d'):
                self.current_index = min(len(self.images) - 1, self.current_index + 1)
                self.update_image()
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.update_image()
            elif key == ord('m'):
                self.mode = not self.mode
                self.update_image()
            if key == 32:
                break
        cv2.destroyAllWindows()

    def get_parameters(self):
        return self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode


