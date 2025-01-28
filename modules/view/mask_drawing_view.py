from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image
import cv2

from modules.view.base_view import BaseView


class MaskDrawingView(BaseView):
    TEXTS = ["Draw on the mask.",
             "LMouse/RMouse: erase/draw",
             "Mouse wheel: cursor size",
             "Press 'U'/'Y' to undo/redo.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    def __init__(self):
        super().__init__(MaskDrawingView.TEXTS, MaskDrawingView.TEXT_COLOR, MaskDrawingView.TITLE)

    def display_image(self, model):
        displayed_image = model.final_mask.copy()
        cv2.circle(displayed_image, model.cursor_pos,
                   model.cursor_size, [128],
                   model.cursor_thickness)
        if self.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow(self.title, displayed_image)

