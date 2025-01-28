from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image
import cv2

from modules.view.base_view import BaseView


class MaskErosionDilationView(BaseView):
    TEXTS = ["Press 'D' to dilate the mask.",
             "Press 'E' to erode the mask.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    def __init__(self):
        super().__init__(MaskErosionDilationView.TEXTS,
                         MaskErosionDilationView.TEXT_COLOR,
                         MaskErosionDilationView.TITLE)



