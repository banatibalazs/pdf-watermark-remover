


class ParameterAdjuster:

    def __init__(self, images, mask, view):
        self.model = ParameterAdjusterModel(images, mask)

    def update_parameter(self, attr, val):
        val = int(val)
        setattr(self.model.current_parameters, attr, val)
        if self.model.apply_same_parameters:
            for param in self.model.parameters:
                setattr(param, attr, val)
        self.view.display_image(self.model.get_processed_current_image())

    def on_parameter_changed(self, attr, val):
        self.update_parameter(attr, val)

    def on_mode_changed(self, pos):
        print("Mode changed to:", pos)
        self.update_parameter('mode', pos)

    def get_parameters(self):
        return self.model.get_parameters()