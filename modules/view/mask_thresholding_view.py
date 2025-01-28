import cv2
from modules.utils import add_texts_to_image
from modules.interfaces.gui_interfaces import DisplayInterface
from modules.view.base_view import BaseView


class MaskThresholdingView(BaseView):
    TEXTS = ["Use the trackbars to",
             "adjust the thresholding.",
             "Press 'space' to finish.",
             "Press 'C' to hide/show this text."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    def __init__(self):
        super().__init__(MaskThresholdingView.TEXTS,
                         MaskThresholdingView.TEXT_COLOR,
                         MaskThresholdingView.TITLE)

