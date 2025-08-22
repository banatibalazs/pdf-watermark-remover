# view_updater.py
import cv2
from modules.controller.constants import MaskMode

class ViewUpdater:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def update_view(self):
        if self.model.mode == MaskMode.DRAW:
            image = self.model.get_weighted_image()
            cv2.circle(image, self.model.cursor_pos, self.model.cursor_size, (0, 0, 0), self.model.cursor_thickness)
            self.view.display_image(image)
        else:
            self.view.display_image(self.model.get_weighted_image())