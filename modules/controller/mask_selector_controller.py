import tkinter
from tkinter import filedialog
import cv2
import numpy as np
from modules.interfaces.gui_interfaces import DisplayInterface, MouseHandlerInterface, KeyHandlerInterface
from modules.interfaces.redo_undo_interface import RedoUndoInterface
from modules.model.mask_selector_model import MaskSelectorModel
from modules.view.opencv_view import OpencvView
from modules.view.tkinter_view import TkinterView


class MaskSelector(KeyHandlerInterface, MouseHandlerInterface, RedoUndoInterface):
    TEXTS = [
        "Draw a circle around the object you want to remove.",
        "Press 'A'/'D' to go to the previous/next page.",
        "Press 'U'/'Y' to undo/redo.",
        "Press 'R' to reset the mask.",
        "Press 'space' to finish."
    ]
    TEXT_COLOR = (255, 255, 255)
    TITLE = "Mask selector"

    def __init__(self, images):
        self.model = MaskSelectorModel(images)
        self.view = TkinterView(MaskSelector.TEXTS,
                                           MaskSelector.TEXT_COLOR,
                                           MaskSelector.TITLE)

    def undo(self) -> None:
        if not self.model.undo_stack:
            return
        self.model.redo_stack.append(self.model.mask.copy())
        self.model.mask = self.model.undo_stack.pop()

        self.view.display_image(self.model.get_weighted_image())

    def redo(self) -> None:
        if not self.model.redo_stack:
            return
        self.model.undo_stack.append(self.model.mask.copy())
        self.model.mask = self.model.redo_stack.pop()
        self.view.display_image(self.model.get_weighted_image())

    def save_state(self) -> None:
        self.model.undo_stack.append(self.model.mask.copy())
        self.model.redo_stack.clear()

    def handle_key(self, key):
        if key != 255:
            print("Key pressed:", key)
        if key == ord('a'):
            self.model.current_page_index = max(0, self.model.current_page_index - 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('d'):
            self.model.current_page_index = min(len(self.model.images) - 1, self.model.current_page_index + 1)
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
        elif key == ord('r'):
            self.reset_mask()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == ord('u'):
            self.undo()
        elif key == ord('y'):
            self.redo()
        elif key == 32:
            return False
        if key in [ord('a'), ord('d'), ord('r'), ord('c')]:
            self.view.display_image(self.model.get_weighted_image())
        return True

    def handle_mouse(self, event):
        print("Mouse event:", event.type, "at", event.x, event.y, "with state", event.state)
        # get the type of tkinter event
        type = event.type
        x,y = event.x, event.y
        if type == tkinter.EventType.ButtonPress:
            self.save_state()


        if type == tkinter.EventType.ButtonPress and event.num == 1:
            self.model.drawing = True
            self.model.ix, self.model.iy = x, y
            self.model.points.append((x, y))
        elif type == tkinter.EventType.Motion:
            if self.model.drawing:
                cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
                self.model.ix, self.model.iy = x, y
                self.model.points.append((x, y))
        elif type == tkinter.EventType.ButtonRelease:
            self.model.drawing = False
            cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
            self.model.points.append((x, y))
            cv2.fillPoly(self.model.mask, [np.array(self.model.points)], (255, 255, 255))
            self.model.points.clear()
        self.view.display_image(self.model.get_weighted_image())

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()

        params = {
            'mouse': self.handle_mouse,
            'key': on_key,
            'buttons': {
                'undo': {'text': 'Undo', 'callback': self.undo},
                'redo': {'text': 'Redo', 'callback': self.redo},
                'save_mask': {
                    'text': 'Save mask', 'callback': self.model.save_mask},
                'reset_mask': {'text': 'Reset mask', 'callback': self.model.reset_mask},
                'load_mask': {
                    'text': 'Load mask', 'callback': self.load_mask},
            }
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.get_weighted_image())
        self.view.root.mainloop()

    def load_mask(self):
        path = filedialog.askopenfilename(
            title="Select mask file",
            filetypes=[("All files", "*.*")]
        )
        self.model.load_mask(path)
        self.view.display_image(self.model.get_weighted_image())

    def reset_mask(self):
        self.model.reset_mask()
        self.view.display_image(self.model.get_weighted_image())

    def save_mask(self):
        self.model.save_mask()

    def get_gray_mask(self):
        return self.model.get_gray_mask()