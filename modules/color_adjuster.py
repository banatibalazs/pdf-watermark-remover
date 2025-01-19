import cv2
import numpy as np
from modules.utils import sharpen_image, add_texts_to_image, fill_masked_area, inpaint_image

class ColorAdjusterParameters:
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


class ColorAdjuster:
    TEXTS = ["Set the color range with trackbars.",
             "Press 'A'/'D' to go to the previous/next page.",
             "Press 'T' to set different parameters for each image.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, images, mask):
        self.images = images
        self.mask = mask
        self.current_index = 0
        self.texts = ColorAdjuster.TEXTS
        self.text_color = ColorAdjuster.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.parameters = [ColorAdjusterParameters() for _ in images]
        self.current_parameters = self.parameters[self.current_index]
        self.apply_same_parameters = True


    def on_r_min_changed(self, val):
        self.current_parameters.r_min = val
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].r_min = val
        self.update_image()

    def on_r_max_changed(self, val):
        self.current_parameters.r_max = val
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].r_max = val
        self.update_image()

    def on_g_min_changed(self, val):
        self.current_parameters.g_min = val
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].g_min = val
        self.update_image()

    def on_g_max_changed(self, val):
        self.current_parameters.g_max = val
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].g_max = val
        self.update_image()

    def on_b_min_changed(self, val):
        self.current_parameters.b_min = val
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].b_min = val
        self.update_image()

    def on_b_max_changed(self, val):
        self.current_parameters.b_max = val
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].b_max = val
        self.update_image()

    def on_w_changed(self, pos):
        self.current_parameters.w = pos / 10
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].w = pos / 10
        self.update_image()

    def on_mode_changed(self, pos):
        self.current_parameters.mode = bool(pos)
        if self.apply_same_parameters:
            for i in range(len(self.parameters)):
                self.parameters[i].mode = bool(pos)
        self.update_image()

    def update_image(self):
        current_image = self.images[self.current_index]
        lower = np.array(
            [self.current_parameters.b_min, self.current_parameters.g_min, self.current_parameters.r_min])
        upper = np.array(
            [self.current_parameters.b_max, self.current_parameters.g_max, self.current_parameters.r_max])
        mask = cv2.bitwise_and(current_image, self.mask)
        gray_mask = cv2.inRange(mask, lower, upper)
        gray_mask = cv2.bitwise_and(gray_mask, cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY))
        if self.current_parameters.mode:
            im_to_show = fill_masked_area(current_image, gray_mask)
        else:
            im_to_show = inpaint_image(current_image, gray_mask)
        im_to_show = sharpen_image(im_to_show, self.current_parameters.w)
        if self.is_text_shown:
            im_to_show = add_texts_to_image(im_to_show, self.texts, self.text_pos, self.text_color)
        cv2.imshow('watermark remover', im_to_show)

    def set_all_parameters_the_same_as_current(self):
        params = self.current_parameters.get_parameters()
        for i in range(len(self.parameters)):
            self.parameters[i].set_parameters(params)

    def update_trackbars(self):
        cv2.setTrackbarPos('R min', 'watermark remover', self.current_parameters.r_min)
        cv2.setTrackbarPos('R max', 'watermark remover', self.current_parameters.r_max)
        cv2.setTrackbarPos('G min', 'watermark remover', self.current_parameters.g_min)
        cv2.setTrackbarPos('G max', 'watermark remover', self.current_parameters.g_max)
        cv2.setTrackbarPos('B min', 'watermark remover', self.current_parameters.b_min)
        cv2.setTrackbarPos('B max', 'watermark remover', self.current_parameters.b_max)
        cv2.setTrackbarPos('Sharpen', 'watermark remover', int(self.current_parameters.w * 10))
        cv2.setTrackbarPos('Mode', 'watermark remover', int(self.current_parameters.mode))

    def toggle_apply_same_parameters(self):
        self.apply_same_parameters = not self.apply_same_parameters
        if self.apply_same_parameters:
            self.set_all_parameters_the_same_as_current()


    def adjust_parameters(self):
        cv2.imshow('watermark remover',
                   add_texts_to_image(self.images[self.current_index], self.texts, self.text_pos, self.text_color))
        cv2.createTrackbar('R min', 'watermark remover', self.current_parameters.r_min, 255, self.on_r_min_changed)
        cv2.createTrackbar('R max', 'watermark remover', self.current_parameters.r_max, 255, self.on_r_max_changed)
        cv2.createTrackbar('G min', 'watermark remover', self.current_parameters.g_min, 255, self.on_g_min_changed)
        cv2.createTrackbar('G max', 'watermark remover', self.current_parameters.g_max, 255, self.on_g_max_changed)
        cv2.createTrackbar('B min', 'watermark remover', self.current_parameters.b_min, 255, self.on_b_min_changed)
        cv2.createTrackbar('B max', 'watermark remover', self.current_parameters.b_max, 255, self.on_b_max_changed)
        cv2.createTrackbar('Sharpen', 'watermark remover', int(self.current_parameters.w * 10), 100,
                           self.on_w_changed)
        cv2.createTrackbar('Mode', 'watermark remover', int(self.current_parameters.mode), 1, self.on_mode_changed)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('a'):
                self.current_index = max(0, self.current_index - 1)
                self.current_parameters = self.parameters[self.current_index]
                self.update_image()
                self.update_trackbars()
            elif key == ord('d'):
                self.current_index = min(len(self.images) - 1, self.current_index + 1)
                self.current_parameters = self.parameters[self.current_index]
                self.update_image()
                self.update_trackbars()
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.update_image()
            elif key == ord('t'):
                self.toggle_apply_same_parameters()
            if key == 32:
                break
        cv2.destroyAllWindows()

    def get_parameters(self):
        return self.parameters