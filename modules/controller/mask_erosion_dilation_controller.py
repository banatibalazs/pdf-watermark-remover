from modules.controller.base_controller import BaseController
from modules.model.mask_erosion_dilation_model import MaskErosionDilationModel



class MaskErosionDilation(BaseController):
    TEXTS = ["Press 'D' to dilate the mask.",
             "Press 'E' to erode the mask.",
             "Press 'R' to reset the mask.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    def __init__(self, input_mask, view):
        super().__init__()
        self.model = MaskErosionDilationModel(input_mask)
        self.view = view
        self.view.set_texts(MaskErosionDilation.TEXTS, MaskErosionDilation.TEXT_COLOR, MaskErosionDilation.TITLE)

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
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()

        params = {
            'key': on_key
            , 'buttons': {
                'save_mask': {
                    'text': 'Save mask', 'callback': self.save_mask},
                'reset_mask': {'text': 'Reset mask', 'callback': self.reset_mask},
                'load_mask': {'text': 'Load mask', 'callback': self.load_mask}
            }
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.final_mask)
        self.view.root.mainloop()

