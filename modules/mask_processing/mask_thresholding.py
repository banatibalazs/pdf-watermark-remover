import cv2
from modules.mask_processing.mask_processing import MaskProcessing


class MaskThresholding(MaskProcessing):
    TEXTS = ["Use the trackbars to",
             "adjust the thresholding.",
             "Press 'space' to finish.",
             "Press 'C' to hide/show this text."]
    TEXT_COLOR = (0, 0, 0)

    def __init__(self, input_mask):
        super().__init__(input_mask, MaskThresholding.TEXTS, MaskThresholding.TEXT_COLOR)
        self.threshold_min = 0
        self.threshold_max = 195

    def process_mask(self):
        cv2.imshow('Mask processing', self.input_mask)
        cv2.createTrackbar('th_min', 'Mask processing', self.threshold_min, 255, self.on_threshold_trackbar_min)
        cv2.createTrackbar('th_max', 'Mask processing', self.threshold_max, 255, self.on_threshold_trackbar_max)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Space key
                break
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
                self.update_mask()

        cv2.destroyAllWindows()

    def on_threshold_trackbar_min(self, pos):
        self.threshold_min = pos
        self.update_mask()

    def on_threshold_trackbar_max(self, pos):
        self.threshold_max = pos
        self.update_mask()

    def update_mask(self):
        self.final_mask = cv2.inRange(self.input_mask, self.threshold_min, self.threshold_max)
        self.final_mask = cv2.bitwise_and(self.final_mask, cv2.inRange(self.input_mask, 1, 255))
        self.show_mask()
