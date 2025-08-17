import numpy as np

from modules.controller.base_controller import BaseController
from modules.controller.gui_config import MaskErosionDilationGUIConfig
from modules.model.base_model import BaseModel
import cv2


class MaskErosionDilation(BaseController):
    def __init__(self, input_mask, view):
        super().__init__()
        self.model = BaseModel(input_mask)
        self.view = view
        self.view.set_texts(MaskErosionDilationGUIConfig.TEXTS,
                            MaskErosionDilationGUIConfig.TEXT_COLOR,
                            MaskErosionDilationGUIConfig.WINDOW_TITLE)

    def handle_key(self, key):
        if key == ord('d'):
            self.model.final_mask = cv2.dilate(self.model.final_mask, np.ones((3, 3), np.uint8), iterations=1)
        elif key == ord('e'):
            self.model.final_mask = cv2.erode(self.model.final_mask, np.ones((3, 3), np.uint8), iterations=1)
        elif key == ord('r'):
            self.reset_mask()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == 32:
            return False
        if key in [ord('d'), ord('e'), ord('r'), ord('c')]:
            self.view.display_image(self.model.get_image_shown())
        return True

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()

        params = {
            'key': on_key,
            'buttons': MaskErosionDilationGUIConfig.get_base_buttons(self)
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.get_image_shown())
        self.view.root.mainloop()

