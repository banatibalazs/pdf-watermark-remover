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

    # def setup_window(self, on_threshold_trackbar_min, on_threshold_trackbar_max, threshold_min, threshold_max):
    #     cv2.namedWindow(self.title)
    #     cv2.createTrackbar('th_min', self.title, threshold_min, 255, on_threshold_trackbar_min)
    #     cv2.createTrackbar('th_max', self.title, threshold_max, 255, on_threshold_trackbar_max)

