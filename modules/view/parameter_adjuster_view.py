import cv2
from modules.interfaces.gui_interfaces import DisplayInterface
from modules.utils import add_texts_to_image



class ParameterAdjusterView(DisplayInterface):
    TEXTS = ["Set the color range with trackbars.",
             "Press 'A'/'D' to go to the previous/next page.",
             "Press 'T' to set different parameters for each image.",
             "Press 'C' to hide/show this text.",
             "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)

    def __init__(self):
        self.texts = ParameterAdjusterView.TEXTS
        self.text_color = ParameterAdjusterView.TEXT_COLOR
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.title = 'watermark remover'

    def display_image(self, processed_image):
        image = processed_image.copy()
        if self.is_text_shown:
            image = add_texts_to_image(image, self.texts, self.text_pos, self.text_color)
        cv2.imshow(self.title, image)

    def setup_window(self, params, *args):
        cv2.namedWindow(self.title)
        cv2.createTrackbar('R min', self.title, params.r_min, 255,args[0])
        cv2.createTrackbar('R max', self.title, params.r_max, 255,args[1])
        cv2.createTrackbar('G min', self.title, params.g_min, 255,args[2])
        cv2.createTrackbar('G max', self.title, params.g_max, 255,args[3])
        cv2.createTrackbar('B min', self.title, params.b_min, 255,args[4])
        cv2.createTrackbar('B max', self.title, params.b_max, 255,args[5])
        cv2.createTrackbar('Sharpen', self.title, int(params.w * 10), 100,args[6])
        cv2.createTrackbar('Mode', self.title, int(params.mode), 1,args[7])

    def close_window(self):
        cv2.destroyAllWindows()

    def toggle_text(self):
        self.is_text_shown = not self.is_text_shown


    def update_trackbars(self, params):
        cv2.setTrackbarPos('R min', self.title, params.r_min)
        cv2.setTrackbarPos('R max', self.title, params.r_max)
        cv2.setTrackbarPos('G min', self.title, params.g_min)
        cv2.setTrackbarPos('G max', self.title, params.g_max)
        cv2.setTrackbarPos('B min', self.title, params.b_min)
        cv2.setTrackbarPos('B max', self.title, params.b_max)
        cv2.setTrackbarPos('Sharpen', self.title, int(params.w * 10))
        cv2.setTrackbarPos('Mode', self.title, int(params.mode))
