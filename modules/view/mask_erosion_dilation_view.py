from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image
import cv2


class MaskErosionDilationView(DisplayInterface):
    TEXTS = ["Press 'D' to dilate the mask.",
             "Press 'E' to erode the mask.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self):
        self.texts = MaskErosionDilationView.TEXTS
        self.text_color = MaskErosionDilationView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.title = "Mask processing"

    def setup_window(self):
        cv2.namedWindow(self.title)

    def display_image(self, mask):
        displayed_image = mask.copy()
        if self.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image,
                                                 self.texts,
                                                 self.text_pos,
                                                 self.text_color)
        cv2.imshow(self.title, displayed_image)

    def toggle_text(self):
        self.is_text_shown = not self.is_text_shown

    def close_window(self):
        cv2.destroyAllWindows()