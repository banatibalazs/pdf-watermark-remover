import cv2
from modules.model.parameter_adjuster_model import ParameterAdjusterModel
from modules.view.parameter_adjuster_view import ParameterAdjusterView
from modules.interfaces.gui_interfaces import KeyHandlerInterface



class ParameterAdjuster(KeyHandlerInterface):
    def __init__(self, images, mask):
        self.model = ParameterAdjusterModel(images, mask)
        self.view = ParameterAdjusterView()
        self.window_name = 'watermark remover'

    def update_parameter(self, attr, val):
        setattr(self.model.current_parameters, attr, val)
        if self.model.apply_same_parameters:
            for param in self.model.parameters:
                setattr(param, attr, val)
        self.view.display_image(self.model.get_processed_current_image())

    def on_r_min_changed(self, val):
        self.update_parameter('r_min', val)

    def on_r_max_changed(self, val):
        self.update_parameter('r_max', val)

    def on_g_min_changed(self, val):
        self.update_parameter('g_min', val)

    def on_g_max_changed(self, val):
        self.update_parameter('g_max', val)

    def on_b_min_changed(self, val):
        self.update_parameter('b_min', val)

    def on_b_max_changed(self, val):
        self.update_parameter('b_max', val)

    def on_w_changed(self, pos):
        self.update_parameter('w', pos / 10)

    def on_mode_changed(self, pos):
        self.update_parameter('mode', bool(pos))

    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_index = max(0, self.model.current_index - 1)
        elif key == ord('d'):
            self.model.current_index = min(len(self.model.images) - 1, self.model.current_index + 1)
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == ord('t'):
            self.model.apply_same_parameters = not self.model.apply_same_parameters
            if self.model.apply_same_parameters:
                self.model.set_all_parameters_the_same_as_current()
        elif key == 32:
            return False
        self.model.current_parameters = self.model.parameters[self.model.current_index]
        self.view.display_image(self.model.get_processed_current_image())
        self.view.update_trackbars(self.model.current_parameters)
        return True

    def run(self):
        self.view.setup_window(self.model.current_parameters, self.on_r_min_changed, self.on_r_max_changed, self.on_g_min_changed,
                               self.on_g_max_changed, self.on_b_min_changed, self.on_b_max_changed, self.on_w_changed,
                               self.on_mode_changed)
        self.view.display_image(self.model.get_processed_current_image())

        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_parameters(self):
        return self.model.get_parameters()