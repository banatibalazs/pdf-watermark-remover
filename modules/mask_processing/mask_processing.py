from abc import ABC, abstractmethod
import cv2

class MaskProcessing(ABC):
    def __init__(self, input_mask, texts=None, text_color=(0, 0, 0)):
        if texts is None:
            texts = []
        self.input_mask = input_mask
        self.final_mask = input_mask.copy()
        self.texts = texts
        self.text_color = text_color
        self.text_pos = (10, 40)
        self.is_text_shown = True

    @abstractmethod
    def process_mask(self):
        pass

    def get_gray_mask(self):
        return self.final_mask

    def get_bgr_mask(self):
        return cv2.cvtColor(self.final_mask, cv2.COLOR_GRAY2BGR)