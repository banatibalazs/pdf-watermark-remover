from abc import ABC, abstractmethod
import tkinter
from tkinter import filedialog
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np

from modules.controller.constants import MaskMode
from modules.controller.gui_config import MaskSelectorGUIConfig
from modules.model.base_model import BaseModel
from modules.utils import calc_median_image


class BaseController:
    def __init__(self,  images, view):
        self.view = view
        self.width, self.height = images[0].shape[:2]
        self.input_mask = np.zeros((self.width, self.height), np.uint8)
        self.final_mask = self.input_mask.copy()
        self.model = BaseModel(self.final_mask, images)
        self.mode = MaskMode.SELECT
        self.drawing = False
        self.left_button_pressed = False
        self.right_button_pressed = False
        self.ix = 0
        self.iy = 0
        self.points: List[Tuple[int, int]] = []
        self.points.clear()

    def on_weight_trackbar(self, pos):
        pos = int(pos) / 100.0
        self.model.weight = pos
        self.update_view()

    def on_key(self, event):
        key = ord(event.char) if event.char else 255
        if not self.handle_key(key):
            self.view.close_window()

    def on_button_click(self, button_name):
        if button_name == 'selection':
            self.mode = MaskMode.SELECT
        elif button_name == 'drawing':
            self.mode = MaskMode.DRAW

    def handle_mouse(self, event):
        type = event.type
        x, y = event.x, event.y

        if self.mode == MaskMode.DRAW:
            print(f"Mouse event: {type}, Position: ({x}, {y}), State: {event.state}"
                  f", Button: {event.num}"
                    f", event: {event}"
                  )
            if type == tkinter.EventType.ButtonPress:
                self.save_state()
                # if left mouse button is pressed, set the left_button_pressed flag
                if event.num == 1:
                    self.left_button_pressed = True
                # if right mouse button is pressed, set the right_button_pressed flag
                elif event.num == 3:
                    self.right_button_pressed = True

            elif type == tkinter.EventType.ButtonRelease:
                self.left_button_pressed = False
                self.right_button_pressed = False
                self.apply_thresholds()

            # On left mouse button press, draw a black filled circle
            if type == tkinter.EventType.Motion and self.left_button_pressed:
                cv2.circle(self.model.final_mask, (x, y), self.model.cursor_size, [0], -1)
            #  On right mouse button press, draw a white filled circle
            elif type == tkinter.EventType.Motion and self.right_button_pressed:
                cv2.circle(self.model.final_mask, (x, y), self.model.cursor_size, [255], -1)

            # When scrolling the mouse wheel up increase the cursor size
            if getattr(event, 'num', None) == 4 or getattr(event, 'delta', 0) > 0:
                self.model.cursor_size = min(self.model.cursor_size + 1, 50)
            # When scrolling the mouse wheel down decrease the cursor size
            elif getattr(event, 'num', None) == 5 or getattr(event, 'delta', 0) < 0:
                self.model.cursor_size = max(self.model.cursor_size - 1, 1)

            self.model.cursor_pos = (x, y)
            self.update_view()

        elif self.mode == MaskMode.SELECT:
            if type == tkinter.EventType.ButtonPress:
                self.save_state()

            if type == tkinter.EventType.ButtonPress and event.num == 1:
                self.left_button_pressed = True
                self.model.ix, self.model.iy = x, y
                self.model.points.append((x, y))
            elif type == tkinter.EventType.Motion:
                if self.left_button_pressed:
                    # Draw a line from the last point to the current point on the current image to indicate the selection
                    cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
                    self.model.ix, self.model.iy = x, y
                    self.model.points.append((x, y))
            elif type == tkinter.EventType.ButtonRelease:
                self.left_button_pressed = False
                # Reset the current image in order to remove the drawn line
                self.reset_current_image()
                self.model.points.append((x, y))
                cv2.fillPoly(self.model.final_mask, [np.array(self.model.points)], (255, 255, 255))
                self.model.points.clear()
                self.apply_thresholds()
            self.update_view()

    def reset_current_image(self):
        """Reset the current image to the original image."""
        self.model.current_image = self.model.images[self.model.current_page_index].copy()
        self.update_view()

    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_page_index = max(0, self.model.current_page_index - 1)
            self.reset_current_image()
        elif key == ord('d'):
            self.model.current_page_index = min(len(self.model.images) - 1, self.model.current_page_index + 1)
            self.reset_current_image()
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

        self.update_view()
        return True

    def erode_mask(self):
        """Erode the mask to remove small noise."""
        self.model.final_mask = cv2.erode(self.model.final_mask, np.ones((3, 3), np.uint8), iterations=1)
        self.save_state()
        self.update_view()

    def dilate_mask(self):
        """Dilate the mask to fill small holes."""
        self.model.final_mask = cv2.dilate(self.model.final_mask, np.ones((3, 3), np.uint8), iterations=1)
        self.save_state()
        self.update_view()

    def run(self):
        self.view.setup_window()
        self.view.set_texts(MaskSelectorGUIConfig.TEXTS, MaskSelectorGUIConfig.TEXT_COLOR, MaskSelectorGUIConfig.WINDOW_TITLE)
        self.view.change_window_setup(MaskSelectorGUIConfig.get_params(self))
        self.update_view()

        self.view.root.mainloop()

    def on_threshold_trackbar_min(self, pos):
        self.model.threshold_min = pos
        self.apply_thresholds()

    def on_threshold_trackbar_max(self, pos):
        """ Set the maximum threshold for the mask."""
        self.model.threshold_max = pos
        self.apply_thresholds()

    def apply_thresholds(self):
        """Filter the pixels by thresholds and update the final mask."""
        median_image = cv2.inRange(self.model.median_image, np.array(self.model.threshold_min, dtype=np.uint8),
                                            np.array(self.model.threshold_max, dtype=np.uint8))
        self.model.final_mask = cv2.bitwise_and(self.model.temp_mask, cv2.inRange(median_image, 1, 255))

        self.view.display_image(self.model.get_weighted_image())


    def undo(self) -> None:
        if not self.model.undo_stack:
            return
        self.model.redo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.undo_stack.pop()
        self.update_view()

    def redo(self) -> None:
        if not self.model.redo_stack:
            return
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.redo_stack.pop()
        self.update_view()

    def save_state(self) -> None:
        self.model.temp_mask = self.model.final_mask
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.redo_stack.clear()


    def get_gray_mask(self) -> Optional[Any]:
        """Get the gray mask from the model"""
        return self.model.get_gray_mask() if self.model else None

    def get_bgr_mask(self) -> Optional[Any]:
        """Get the BGR mask from the model"""
        return self.model.get_bgr_mask() if self.model else None

    def load_mask(self) -> None:
        """Load a mask from the specified path"""
        path = filedialog.askopenfilename(
            title="Load mask",
            filetypes=[("All files", "*.*")]
        )
        if self.model:
            self.model.load_mask(path)
            self.update_view()

    def reset_mask(self) -> None:
        """Reset the mask to its initial state"""
        if self.model:
            self.model.reset_mask()
            self.model.current_image = self.model.images[self.model.current_page_index].copy()
            self.update_view()

    def save_mask(self, path: str = 'saved_mask.png') -> None:
        """Save the current mask to the specified path"""
        if self.model:
            self.model.save_mask(path)


    def update_view(self):
        if self.mode == MaskMode.DRAW:
            image = self.model.get_weighted_image()
            cv2.circle(image, self.model.cursor_pos, self.model.cursor_size, (0,0,0), self.model.cursor_thickness)
            self.view.display_image(image)
        else:
            self.view.display_image(self.model.get_weighted_image())

