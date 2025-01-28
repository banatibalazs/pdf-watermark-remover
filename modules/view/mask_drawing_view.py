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
        super().__init__(MaskDrawingView.TEXTS,
                         MaskDrawingView.TEXT_COLOR,
                         MaskDrawingView.TITLE)

