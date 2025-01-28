import cv2
from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image
from modules.view.base_view import BaseView


class MaskSelectorView(BaseView):
    TEXTS = ["Draw a circle around the object you want to remove.",
             "Press 'A'/'D' to go to the previous/next page.",
             "Press 'U'/'Y' to undo/redo.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)
    TITLE = "Mask selector"

    def __init__(self):
        super().__init__(MaskSelectorView.TEXTS, MaskSelectorView.TEXT_COLOR, MaskSelectorView.TITLE)

