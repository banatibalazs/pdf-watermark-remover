import tkinter
from typing import List, Tuple

from modules.controller.base_controller import BaseController
import cv2
import numpy as np

from modules.model.mask_selector_model import MaskSelectorModel
from modules.controller.gui_config import MaskSelectorGUIConfig, MaskErosionDilationGUIConfig


class MaskSelector(BaseController):
    def __init__(self, images, view_instance):
        super().__init__()
        self.model = MaskSelectorModel(images)
        self.view = view_instance
        self.view.set_texts(MaskSelectorGUIConfig.TEXTS,
                            MaskSelectorGUIConfig.TEXT_COLOR,
                            MaskSelectorGUIConfig.WINDOW_TITLE)


    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_page_index = max(0, self.model.current_page_index - 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('d'):
            self.model.current_page_index = min(len(self.model.images) - 1, self.model.current_page_index + 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('r'):
            self.reset_mask()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == ord('u'):
            self.undo()
        elif key == ord('y'):
            self.redo()
        elif key == 32:
            return False
        if key in [ord('a'), ord('d'), ord('r'), ord('c')]:
            self.update_view()
        return True

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()

        params = {
            'mouse': self.handle_mouse,
            'key': on_key,
            'buttons': MaskSelectorGUIConfig.get_base_buttons(self)
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.get_image_shown())
        self.view.root.mainloop()

