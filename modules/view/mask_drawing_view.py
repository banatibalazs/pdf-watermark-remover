from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image
import cv2


class MaskDrawingView(DisplayInterface):
    TEXTS = ["Draw on the mask.",
             "L mouse: erase",
             "R mouse: draw",
             "Mouse wheel: cursor size",
             "Press 'R' to reset the mask.",
             "Press 'U' to undo.",
             "Press 'Y' to redo.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, model=None):
        self.texts = MaskDrawingView.TEXTS
        self.text_color = MaskDrawingView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.model = model

    def setup_window(self, *args, **kwargs):
        cv2.namedWindow('Mask processing')
        cv2.setMouseCallback('Mask processing', *args, **kwargs)

    def display_image(self):
        displayed_image = self.model.final_mask.copy()
        cv2.circle(displayed_image,self.model.cursor_pos,
                   self.model.cursor_size, (255),
                   self.model.cursor_thickness)
        if self.model.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow('Mask processing', displayed_image)

    def close_window(self):
        cv2.destroyAllWindows()