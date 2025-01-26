import cv2
from modules.model.color_adjuster_model import ColorAdjusterModel
from modules.view.color_adjuster_view import ColorAdjusterView
from modules.interfaces.gui_interfaces import KeyHandlerInterface



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
        self.view.display_image()

    def on_r_max_changed(self, val):
        self.model.current_parameters.r_max = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].r_max = val
        self.view.display_image()

    def on_g_min_changed(self, val):
        self.model.current_parameters.g_min = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].g_min = val
        self.view.display_image()

    def on_g_max_changed(self, val):
        self.model.current_parameters.g_max = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].g_max = val
        self.view.display_image()

    def on_b_min_changed(self, val):
        self.model.current_parameters.b_min = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].b_min = val
        self.view.display_image()

    def on_b_max_changed(self, val):
        self.model.current_parameters.b_max = val
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].b_max = val
        self.view.display_image()

    def on_w_changed(self, pos):
        self.model.current_parameters.w = pos / 10
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].w = pos / 10
        self.view.display_image()

    def on_mode_changed(self, pos):
        self.model.current_parameters.mode = bool(pos)
        if self.model.apply_same_parameters:
            for i in range(len(self.model.parameters)):
                self.model.parameters[i].mode = bool(pos)
        self.view.display_image()


    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_index = max(0, self.model.current_index - 1)
            self.model.current_parameters = self.model.parameters[self.model.current_index]
            self.view.display_image()
            self.view.update_trackbars()
        elif key == ord('d'):
            self.model.current_index = min(len(self.model.images) - 1, self.model.current_index + 1)
            self.model.current_parameters = self.model.parameters[self.model.current_index]
            self.view.display_image()
            self.view.update_trackbars()
        elif key == ord('c'):
            self.view.toggle_text()
            self.view.display_image()
        elif key == ord('t'):
            self.model.apply_same_parameters = not self.model.apply_same_parameters
            if self.model.apply_same_parameters:
                self.model.set_all_parameters_the_same_as_current()
        if key == 32:
            return False
        return True

    def run(self):
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