from modules.model.parameter_adjuster_model import ParameterAdjusterModel
from modules.interfaces.gui_interfaces import KeyHandlerInterface


class ParameterAdjuster(KeyHandlerInterface):
    TEXTS = ["Set the color range with trackbars.",
            "Press 'A'/'D' to go to the previous/next page.",
            "Press 'T' to set different parameters for each image.",
            "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)
    TITLE = "Parameter adjuster"

    def __init__(self, images, mask, view):
        self.model = ParameterAdjusterModel(images, mask)
        self.view = view
        self.view.set_texts(ParameterAdjuster.TEXTS, ParameterAdjuster.TEXT_COLOR, ParameterAdjuster.TITLE)


    def update_parameter(self, attr, val):
        val = int(val)
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
        self.update_parameter('w', pos)

    def on_mode_changed(self, pos):
        print("Mode changed to:", pos)
        self.update_parameter('mode', pos)

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
        self.view.update_trackbars({
            'values': self.model.current_parameters.get_parameters(),
            'names': self.model.current_parameters.get_parameter_names()
        })
        return True

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()
        params = {
            'trackbars': {
                'r_min': {'value': 0, 'callback': self.on_r_min_changed},
                'r_max': {'value': 255, 'callback': self.on_r_max_changed},
                'g_min': {'value': 0, 'callback': self.on_g_min_changed},
                'g_max': {'value': 255, 'callback': self.on_g_max_changed},
                'b_min': {'value': 0, 'callback': self.on_b_min_changed},
                'b_max': {'value': 255, 'callback': self.on_b_max_changed},
                'w': {'value': 0, 'callback': self.on_w_changed},
                'mode': {'value': 1, 'callback': self.on_mode_changed}
            },
            'key': on_key
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.get_processed_current_image())

        self.view.root.mainloop()

    def get_parameters(self):
        return self.model.get_parameters()