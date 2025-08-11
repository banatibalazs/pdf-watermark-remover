import cv2
from modules.interfaces.gui_interfaces import KeyHandlerInterface
from modules.model.mask_thresholding_model import MaskThresholdingModel

from modules.view.opencv_view import OpencvView
from modules.view.tkinter_view import TkinterView


class MaskThresholding(KeyHandlerInterface):
    TEXTS = ["Use the trackbars to",
             "adjust the thresholding.",
             "Press 'space' to finish.",
             ]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    def __init__(self, images, input_mask):
        self.model = MaskThresholdingModel(images, input_mask)
        self.view = TkinterView(MaskThresholding.TEXTS,
                                           MaskThresholding.TEXT_COLOR,
                                           MaskThresholding.TITLE)

    def on_threshold_trackbar_min(self, pos):
        print("Threshold min changed to:", pos)
        self.model.set_threshold_min(pos)
        self.view.display_image(self.model.final_mask)

    def on_threshold_trackbar_max(self, pos):
        print("Threshold max changed to:", pos)
        self.model.set_threshold_max(pos)
        self.view.display_image(self.model.final_mask)

    def handle_key(self, key):
        if key == 32:
            return False
        elif key == ord('c'):
            self.view.toggle_text()
            self.view.display_image(self.model.final_mask)
        return True

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()
        params = {
            'trackbars': {
                'th_min': {'value': self.model.threshold_min, 'callback': self.on_threshold_trackbar_min},
                'th_max': {'value': self.model.threshold_max, 'callback': self.on_threshold_trackbar_max},

            },
            'key': on_key
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.final_mask)
        self.view.root.mainloop()

    def get_gray_mask(self):
        return self.model.get_gray_mask()

    def get_bgr_mask(self):
        return self.model.get_bgr_mask()
