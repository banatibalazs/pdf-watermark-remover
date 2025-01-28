import cv2
from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image
from modules.view.base_view import BaseView


class ParameterAdjusterView(BaseView):
    TEXTS = ["Set the color range with trackbars.",
             "Press 'A'/'D' to go to the previous/next page.",
             "Press 'T' to set different parameters for each image.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)
    TITLE = "Parameter adjuster"

    def __init__(self):
        super().__init__(ParameterAdjusterView.TEXTS,
                         ParameterAdjusterView.TEXT_COLOR,
                         ParameterAdjusterView.TITLE)
