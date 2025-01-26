# modules/mask_selector_model.py
import cv2
import numpy as np
from modules.interfaces.gui_interfaces import DisplayInterface, MouseHandlerInterface, KeyHandlerInterface
from modules.utils import add_texts_to_image



class MaskSelectorModel:
    def __init__(self, images):
        self.images = images
        self.width, self.height = images[0].shape[:2]
        self.current_page_index = 0
        self.current_image = self.images[self.current_page_index].copy()
        mask = np.zeros((self.width, self.height), np.uint8)
        self.mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.points = []

    def reset_mask(self):
        self.mask = cv2.cvtColor(np.zeros((self.width, self.height), np.uint8), cv2.COLOR_GRAY2BGR)

    def get_gray_mask(self):
        return cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)



class MaskSelectorView(DisplayInterface):
    TEXTS = ["Draw a circle around the object",
             "you want to remove.",
             "Press 'A' to go to the previous page.",
             "Press 'D' to go to the next page.",
             "Press 'R' to reset the mask.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, model=None):
        self.texts = MaskSelectorView.TEXTS
        self.text_color = MaskSelectorView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.model = model

    def display_image(self):
        displayed_image = self.model.current_image.copy()
        mask = self.model.mask.copy()
        if self.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos, self.text_color)
        cv2.imshow('watermark remover', cv2.addWeighted(displayed_image, 0.7, mask, 0.3, 0))

    def close_window(self):
        cv2.destroyAllWindows()



class MaskSelector(KeyHandlerInterface, MouseHandlerInterface):
    def __init__(self, images):
        self.model = MaskSelectorModel(images)
        self.view: DisplayInterface = MaskSelectorView(self.model)

    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_page_index = max(0, self.model.current_page_index - 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('d'):
            self.model.current_page_index = min(len(self.model.images) - 1, self.model.current_page_index + 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('r'):
            self.model.reset_mask()
        elif key == ord('c'):
            self.view.is_text_shown = not self.view.is_text_shown
        elif key == 32:
            return False
        if key in [ord('a'), ord('d'), ord('r'), ord('c')]:
            self.view.display_image()
        return True

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.model.drawing = True
            self.model.ix, self.model.iy = x, y
            self.model.points.append((x, y))
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.model.drawing:
                cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
                self.model.ix, self.model.iy = x, y
                self.model.points.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            self.model.drawing = False
            cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
            self.model.points.append((x, y))
            cv2.fillPoly(self.model.mask, [np.array(self.model.points)], (255, 255, 255))
            self.model.points.clear()
        self.view.display_image()

    def draw_mask(self):
        cv2.namedWindow('watermark remover')
        cv2.setMouseCallback('watermark remover', self.handle_mouse)

        self.view.display_image()

        while True:
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_key(key):
                break

        self.view.close_window()

    def get_gray_mask(self):
        return self.model.get_gray_mask()