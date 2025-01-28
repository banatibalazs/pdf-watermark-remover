import cv2
from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image


class MaskSelectorView(DisplayInterface):
    TEXTS = ["Draw a circle around the object you want to remove.",
             "Press 'A'/'D' to go to the previous/next page.",
             "Press 'U'/'Y' to undo/redo.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]

    TEXT_COLOR = (255, 255, 255)
    def __init__(self):
        self.texts = MaskSelectorView.TEXTS
        self.text_color = MaskSelectorView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.title = "Mask selector"

    def setup_window(self, handle_mouse):
        cv2.namedWindow(self.title)
        cv2.setMouseCallback(self.title, handle_mouse)

    def display_image(self, mask, image):
        displayed_image = image.copy()
        mask = mask.copy()
        if self.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow(self.title, cv2.addWeighted(displayed_image, 0.7, mask, 0.3, 0))

    def close_window(self):
        cv2.destroyAllWindows()