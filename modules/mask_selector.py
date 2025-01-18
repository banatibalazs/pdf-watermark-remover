import cv2
import numpy as np
from modules.utils import add_texts_to_image


TEXTS = ["Draw a circle around the object",
         "you want to remove.",
        "Press 'A' to go to the previous page.",
        "Press 'D' to go to the next page.",
        "Press 'R' to reset the mask.",
        "Press 'C' to hide/show this text.",
        "Press 'space' to finish."]
TEXT_COLOR = (255, 255, 255)

class MaskSelector:
    def __init__(self, images):
        self.images = images
        self.width, self.height = images[0].shape[:2]
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        mask = np.zeros((self.width, self.height), np.uint8)
        self.mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        self.current_image = None
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.points = []
        self.texts = TEXTS
        self.text_color = TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True

    def draw_free(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
            self.points.append((x, y))
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.line(self.current_image, (self.ix, self.iy), (x, y), (0, 0, 0), 2)
                self.ix, self.iy = x, y
                self.points.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.current_image, (self.ix, self.iy), (x, y), (0, 0, 0), 2)
            self.points.append((x, y))
            cv2.fillPoly(self.mask, [np.array(self.points)], (255, 255, 255))
            self.points.clear()

    def draw_mask(self):
        cv2.namedWindow('watermark remover')
        cv2.setMouseCallback('watermark remover', self.draw_free)

        self.current_image = add_texts_to_image(self.images[self.current_page_index], self.texts, self.text_pos, self.text_color)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('a'):
                self.current_page_index = max(0, self.current_page_index - 1)
            elif key == ord('d'):
                self.current_page_index = min(len(self.images) - 1, self.current_page_index + 1)
            elif key == ord('r'):
                self.mask = cv2.cvtColor(np.zeros((self.width, self.height), np.uint8), cv2.COLOR_GRAY2BGR)
            elif key == ord('c'):
                self.is_text_shown = not self.is_text_shown
            elif key == 32:
                break

            if key in [ord('a'), ord('d'), ord('r'), ord('c')]:
                if self.is_text_shown:
                    self.current_image = add_texts_to_image(self.images[self.current_page_index], self.texts, self.text_pos, self.text_color)
                else:
                    self.current_image = self.images[self.current_page_index].copy()

            cv2.imshow('watermark remover', cv2.addWeighted(self.current_image, 0.7, self.mask, 0.3, 0))

        # cv2.destroyAllWindows()

    def get_gray_mask(self):
        return cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)