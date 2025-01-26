import cv2

from modules.interfaces.gui_interfaces import KeyHandlerInterface, DisplayInterface
from modules.mask_processing.abstract_mask_processing import MaskProcessing
from modules.utils import add_texts_to_image








class MaskThresholding(KeyHandlerInterface):
    def __init__(self, input_mask):
        self.model = MaskThresholdingModel(input_mask)
        self.view = MaskThresholdingView(self.model)

    def on_threshold_trackbar_min(self, pos):
        self.model.set_threshold_min(pos)
        self.view.display_image()

    def on_threshold_trackbar_max(self, pos):
        self.model.set_threshold_max(pos)
        self.view.display_image()

    def handle_key(self, key):
        if key == 32:
            return False
        elif key == ord('c'):
            self.view.toggle_text()
            self.view.display_image()

    def process_mask(self):
        self.view.setup_window(self.on_threshold_trackbar_min, self.on_threshold_trackbar_max,
                               self.model.threshold_min, self.model.threshold_max)
        self.view.display_image()
        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break
        self.view.close_window()


