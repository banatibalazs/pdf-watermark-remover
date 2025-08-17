from modules.controller.base_controller import BaseController
from modules.controller.gui_config import MaskThresholdingGUIConfig
from modules.model.mask_thresholding_model import MaskThresholdingModel
import cv2
import numpy as np


class MaskThresholding(BaseController):
    def __init__(self, images, input_mask, view):
        super().__init__()
        self.model = MaskThresholdingModel(images, input_mask)
        self.view = view
        self.view.set_texts(MaskThresholdingGUIConfig.TEXTS,
                             MaskThresholdingGUIConfig.TEXT_COLOR,
                             MaskThresholdingGUIConfig.WINDOW_TITLE)

    def on_threshold_trackbar_min(self, pos):
        print("Threshold min changed to:", pos)
        self.model.threshold_min = pos
        self.update_thresholds()

    def on_threshold_trackbar_max(self, pos):
        print("Threshold max changed to:", pos)
        self.model.threshold_max = pos
        self.update_thresholds()

    def update_thresholds(self):
        self.model.final_mask = cv2.inRange(self.model.input_mask, np.array(self.model.threshold_min, dtype=np.uint8),
                                            np.array(self.model.threshold_max, dtype=np.uint8))
        self.model.final_mask = cv2.bitwise_and(self.model.final_mask, cv2.inRange(self.model.input_mask, 1, 255))
        self.view.display_image(self.model.get_image_shown())

    def on_median_img_number_changed(self, pos):
        '''It sets the number of images used to calculate the median image.'''
        self.model.set_median_img_number(pos)
        self.model.calc_median_image()
        self.update_thresholds()
        self.view.display_image(self.model.get_image_shown())

    def handle_key(self, key):
        if key == 32:
            return False
        elif key == ord('c'):
            self.view.toggle_text()
            self.view.display_image(self.model.get_image_shown())
        return True

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()
        params = {
            'mouse': self.handle_mouse,
            'trackbars': {
                'th_min': {'value': self.model.threshold_min, 'callback': self.on_threshold_trackbar_min},
                'th_max': {'value': self.model.threshold_max, 'callback': self.on_threshold_trackbar_max},
                'median_img_number': {
                    'value': self.model.median_img_number, 'callback': self.on_median_img_number_changed}

            },
            'key': on_key,
            'buttons': MaskThresholdingGUIConfig.get_base_buttons(self)
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.get_image_shown())
        self.view.root.mainloop()

