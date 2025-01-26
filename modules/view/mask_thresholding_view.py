import cv2
from modules.utils import add_texts_to_image
from modules.interfaces.gui_interfaces import DisplayInterface


class MaskThresholdingView(DisplayInterface):
    TEXTS = ["Use the trackbars to",
             "adjust the thresholding.",
             "Press 'space' to finish.",
             "Press 'C' to hide/show this text."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, model):
        self.texts = MaskThresholdingView.TEXTS
        self.text_color = MaskThresholdingView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.model = model

    def display_image(self):
        display_image = self.model.final_mask.copy()
        if self.is_text_shown:
            display_image = add_texts_to_image(display_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow(self.model.title, display_image)

    def toggle_text(self):
        self.is_text_shown = not self.is_text_shown

    def setup_window(self, on_threshold_trackbar_min, on_threshold_trackbar_max, threshold_min, threshold_max):
        cv2.namedWindow(self.model.title)
        cv2.createTrackbar('th_min', self.model.title, threshold_min, 255, on_threshold_trackbar_min)
        cv2.createTrackbar('th_max', self.model.title, threshold_max, 255, on_threshold_trackbar_max)

    def close_window(self):
        cv2.destroyAllWindows()