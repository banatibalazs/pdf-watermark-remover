from abc import ABC, abstractmethod
import tkinter
from tkinter import filedialog
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np

class BaseController(ABC):
    def __init__(self):
        self.model = None
        self.view = None
        self.mode = 0
        self.drawing = False
        self.ix = 0
        self.iy = 0
        self.points: List[Tuple[int, int]] = []
        self.points.clear()



    def on_button_click(self, button_name):
        if button_name == 'selection':
            self.mode = 0
        elif button_name == 'drawing':
            self.mode = 1
        elif button_name == 'other':
            self.mode = 2

        print(f"Button clicked: {button_name}, mode set to {self.mode}")


    def handle_mouse(self, event):
        type = event.type
        x, y = event.x, event.y

        if self.mode == 1:

            if type == tkinter.EventType.ButtonPress:
                self.save_state()

            # On left mouse button press, draw a black filled circle
            if event.state == 8464:
                cv2.circle(self.model.final_mask, (x, y), self.model.cursor_size, (0,0,0), -1)
            #  On right mouse button press, draw a white filled circle
            elif event.state == 9232:
                cv2.circle(self.model.final_mask, (x, y), self.model.cursor_size, (255,255,255), -1)
            # When scrolling the mouse wheel up increase the cursor size
            elif event.num == 4:
                self.model.cursor_size = min(self.model.cursor_size + 1, 50)
            # When scrolling the mouse wheel down decrease the cursor size
            elif event.num == 5:
                self.model.cursor_size = max(self.model.cursor_size - 1, 1)

            self.model.cursor_pos = (x, y)
            mask = self.model.get_image_shown()
            cv2.circle(mask, self.model.cursor_pos,
                       self.model.cursor_size, [128],
                       self.model.cursor_thickness)
            self.view.display_image(mask)
        elif self.mode == 0:
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
                cv2.fillPoly(self.model.final_mask, [np.array(self.model.points)], (255, 255, 255))
                self.model.points.clear()
            self.view.display_image(self.model.get_image_shown())


    def on_threshold_trackbar_min(self, pos):
        print("Threshold min changed to:", pos)
        self.model.threshold_min = pos
        self.update_thresholds()

    def on_threshold_trackbar_max(self, pos):
        print("Threshold max changed to:", pos)
        self.model.threshold_max = pos
        self.update_thresholds()

    def update_thresholds(self):
        self.model.final_mask = cv2.inRange(self.model.input_mask, np.array(self.model.threshold_min, dtype=np.uint8),
                                            np.array(self.model.threshold_max, dtype=np.uint8))
        self.model.final_mask = cv2.bitwise_and(self.model.final_mask, cv2.inRange(self.model.input_mask, 1, 255))
        self.view.display_image(self.model.get_image_shown())


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
            self.update_view()

    def save_mask(self, path: str = 'saved_mask.png') -> None:
        """Save the current mask to the specified path"""
        if self.model:
            self.model.save_mask(path)


    def update_view(self):
        self.view.display_image(self.model.get_image_shown())

