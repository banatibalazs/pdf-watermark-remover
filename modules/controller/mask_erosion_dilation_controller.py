from modules.model.mask_erosion_dilation_model import MaskErosionDilationModel
from modules.view.mask_erosion_dilation_view import MaskErosionDilationView
import cv2

from modules.interfaces.gui_interfaces import KeyHandlerInterface


class MaskErosionDilation(KeyHandlerInterface):
    def __init__(self, input_mask):
        self.model = MaskErosionDilationModel(input_mask)
        self.view = MaskErosionDilationView()

    def handle_key(self, key):
        if key == ord('d'):
            self.model.dilate()
        elif key == ord('e'):
            self.model.erode()
        elif key == ord('r'):
            self.model.reset()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == 32:
            return False
        if key in [ord('d'), ord('e'), ord('r'), ord('c')]:
            self.view.display_image(self.model.final_mask)
        return True

    def run(self):
        self.view.setup_window()
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