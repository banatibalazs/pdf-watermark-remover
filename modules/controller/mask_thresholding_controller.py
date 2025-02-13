import cv2
from modules.interfaces.gui_interfaces import KeyHandlerInterface
from modules.model.mask_thresholding_model import MaskThresholdingModel
from modules.view.mask_thresholding_view import MaskThresholdingView



class MaskThresholding(KeyHandlerInterface):
    def __init__(self, images, input_mask):
        self.model = MaskThresholdingModel(images, input_mask)
        self.view = MaskThresholdingView()

    def on_threshold_trackbar_min(self, pos):
        self.model.set_threshold_min(pos)
        self.view.display_image(self.model.final_mask)

    def on_threshold_trackbar_max(self, pos):
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
        params = {
            'trackbars': {
                'th_min': {'value': self.model.threshold_min, 'callback': self.on_threshold_trackbar_min},
                'th_max': {'value': self.model.threshold_max, 'callback': self.on_threshold_trackbar_max},

            }
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.final_mask)
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break
        self.view.close_window()

    def get_gray_mask(self):
        return self.model.get_gray_mask()

    def get_bgr_mask(self):
        return self.model.get_bgr_mask()
