import cv2
import numpy as np

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
        self.redo_stack = []
        self.undo_stack = []

    def reset_mask(self):
        self.mask = cv2.cvtColor(np.zeros((self.width, self.height), np.uint8), cv2.COLOR_GRAY2BGR)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_image = self.images[self.current_page_index].copy()
        self.points.clear()
        print("Mask reset to initial state.")

    def save_mask(self, path=None):
        if path is None:
            path = 'saved_mask' + '.png'
        cv2.imwrite(path, self.mask)
        print("Mask saved as " + path)
        print("Mask size:", self.mask.shape)

    def get_gray_mask(self):
        return cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)

    def get_weighted_image(self):
        return cv2.addWeighted(self.current_image, 0.7, self.mask, 0.3, 0)

    def load_mask(self, path=None):
        if path is None:
            return
        try:
            self.mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if self.mask is None:
                print("No saved mask found. Using default mask.")
                self.reset_mask()
            elif len(self.mask.shape) == 2:
                self.mask = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)
                print("Mask loaded from " + path)

        except Exception as e:
            print(f"Error loading mask from {path}: {e}")
            self.reset_mask()