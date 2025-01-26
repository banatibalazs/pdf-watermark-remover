import cv2
import numpy as np

from modules.interfaces.gui_interfaces import KeyHandlerInterface, DisplayInterface
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




class ColorAdjuster(KeyHandlerInterface):
    def __init__(self, images, mask):
        self.model = ColorAdjusterModel(images, mask)
        self.view = ColorAdjusterView(self.model)
        self.window_name = 'watermark remover'

    def on_r_min_changed(self, val):
        self.model.current_parameters.r_min = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].r_min = val
        self.update_image()

    def on_r_max_changed(self, val):
        self.model.current_parameters.r_max = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].r_max = val
        self.update_image()

    def on_g_min_changed(self, val):
        self.model.current_parameters.g_min = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].g_min = val
        self.update_image()

    def on_g_max_changed(self, val):
        self.model.current_parameters.g_max = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].g_max = val
        self.update_image()

    def on_b_min_changed(self, val):
        self.model.current_parameters.b_min = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].b_min = val
        self.update_image()

    def on_b_max_changed(self, val):
        self.model.current_parameters.b_max = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].b_max = val
        self.update_image()

    def on_w_changed(self, pos):
        self.model.current_parameters.w = pos / 10
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].w = pos / 10
        self.update_image()

    def on_mode_changed(self, pos):
        self.model.current_parameters.mode = bool(pos)
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].mode = bool(pos)
        self.update_image()

    def update_image(self):
        self.view.display_image()

    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_index = max(0, self.model.current_index - 1)
            self.model.current_parameters = self.model.parameters[self.model.current_index]
            self.update_image()
            self.view.update_trackbars()
        elif key == ord('d'):
            self.model.current_index = min(len(self.model.images) - 1, self.model.current_index + 1)
            self.model.current_parameters = self.model.parameters[self.model.current_index]
            self.update_image()
            self.view.update_trackbars()
        elif key == ord('c'):
            self.view.toggle_text()
            self.update_image()
        elif key == ord('t'):
            self.model.apply_same_parameters = not self.model.apply_same_parameters
            if self.model.apply_same_parameters:
                self.model.set_all_parameters_the_same_as_current()
        if key == 32:
            return False
        return True

    def adjust_parameters(self):
        self.view.setup_window(self.on_r_min_changed, self.on_r_max_changed, self.on_g_min_changed,
                               self.on_g_max_changed, self.on_b_min_changed, self.on_b_max_changed, self.on_w_changed,
                               self.on_mode_changed)
        self.view.display_image()

        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_parameters(self):
        return self.model.get_parameters()