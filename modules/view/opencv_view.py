import cv2
from modules.utils import add_texts_to_image
from modules.interfaces.interfaces import DisplayInterface

class OpencvView(DisplayInterface):
    def __init__(self, texts, text_color, title):
        self.texts = texts
        self.text_color = text_color
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.title = title

    def setup_window(self, params=None):
        cv2.namedWindow(self.title)
        if params is None:
            return
        if 'trackbars' in params:
            for name, value in params['trackbars'].items():
                if name == 'mode':
                    cv2.createTrackbar(name, self.title, int(value['value']), 1, value['callback'])
                elif name == 'w':
                    cv2.createTrackbar(name, self.title, int(value['value']), 25, value['callback'])
                else:
                    cv2.createTrackbar(name, self.title, int(value['value']), 255, value['callback'])
        if 'mouse' in params:
            cv2.setMouseCallback(self.title, params['mouse'])


    def display_image(self, image):
        displayed_image = image.copy()
        if self.is_text_shown:
            displayed_image = add_texts_to_image(displayed_image, self.texts, self.text_pos,
                                                 self.text_color)
        cv2.imshow(self.title, displayed_image)

    def close_window(self):
        cv2.destroyAllWindows()


    def update_trackbars(self, params):
        for i in range(len(params['names'])):
            cv2.setTrackbarPos(params['names'][i], self.title, int(params['values'][i]))


    def toggle_text(self):
        self.is_text_shown = not self.is_text_shown