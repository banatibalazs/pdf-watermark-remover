# view_updater.py
import cv2
from modules.controller.constants import MaskMode
from modules.controller.gui_config import ParameterAdjusterGUIConfig, BaseGUIConfig


class ViewUpdater:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def update_view(self):
        image = self.model.get_weighted_image()

        if self.model.mode == MaskMode.DRAW:
            cv2.circle(image, self.model.cursor_pos, self.model.cursor_size, (0, 0, 0), self.model.cursor_thickness)
            self.view.display_image(image)
        else:
            self.view.display_image(image)

    def change_window_setup(self, parameters):
        self.view.change_window_setup(parameters)
